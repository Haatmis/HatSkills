#!/usr/bin/env python3
"""Tests des scripts du repo. Stdlib, sans réseau.

`validate.py` police les skills ; jusqu'ici rien ne policait `validate.py`. Et
des bugs réels y sont passés : un plantage d'encodage APRÈS avoir affiché
« OK », une déduplication de journal cassée par les accents, un vérificateur
Luau qui hurlait sur du code correct. Chacun de ces trois-là a son test ici —
un test écrit après coup ne prouve rien sur le passé, mais il empêche le
retour.

    python3 scripts/test_scripts.py          # tout
    python3 -m unittest scripts.test_scripts -v
"""

import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

RACINE = pathlib.Path(__file__).resolve().parent.parent


def charger(chemin, nom):
    """Importe un script par son chemin : ils ne forment pas un paquet."""
    spec = importlib.util.spec_from_file_location(nom, RACINE / chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


validate = charger("scripts/validate.py", "v_validate")
check_version = charger("scripts/check_version.py", "v_checkver")
journal = charger("plugins/roblox/scripts/journal.py", "v_journal")
luau = charger("plugins/roblox/scripts/luau_check.py", "v_luau")
toolbox = charger("plugins/roblox/scripts/toolbox.py", "v_toolbox")
build_help = charger("plugins/roblox/scripts/build_help.py", "v_help")


class Frontmatter(unittest.TestCase):
    def test_bloc_plie(self):
        fm, corps = validate.parse_frontmatter(
            "---\nname: x\ndescription: >\n  une ligne\n  et sa suite\n---\ncorps\n")
        self.assertEqual(fm["name"], "x")
        self.assertIn("et sa suite", fm["description"])
        self.assertIn("corps", corps)

    def test_sans_frontmatter(self):
        fm, corps = validate.parse_frontmatter("# rien\n")
        self.assertIsNone(fm)


class Journal(unittest.TestCase):
    def test_accents_dedupliques(self):
        """Le bug de la 0.9.0 : « déplace » et « deplace » ne se reconnaissaient
        pas, donc une leçon récurrente restait à ×1 et ne montait jamais."""
        self.assertEqual(journal.cle("Déplace le personnage"),
                         journal.cle("Deplace le personnage"))

    def test_ponctuation_ignoree(self):
        self.assertEqual(journal.cle("Fais X, toujours."), journal.cle("fais x toujours"))

    def test_skills_connus_non_vide(self):
        self.assertIn("code", journal.skills_connus())


class Versions(unittest.TestCase):
    def test_triplet(self):
        self.assertEqual(check_version.triplet("0.9.1"), (0, 9, 1))
        self.assertEqual(check_version.triplet("1.2"), (1, 2, 0))
        self.assertIsNone(check_version.triplet("pas-une-version"))

    def test_ordre(self):
        self.assertLess(check_version.triplet("0.9.0"), check_version.triplet("0.10.0"))


class Luau(unittest.TestCase):
    def setUp(self):
        self.regles = luau.regles()

    def test_table_lue(self):
        self.assertGreater(len(self.regles), 30)

    def test_attrape_les_depreciees(self):
        code = 'wait(1)\nspawn(f)\nlocal b = Instance.new("BodyVelocity")\nx:connect(g)\n'
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "a.luau"
            f.write_text(code, encoding="utf-8")
            jetons = {t[2] for t in luau.balayer(pathlib.Path(d), self.regles)}
        for attendu in ("wait(n)", "spawn(f)", "BodyVelocity", ":connect()"):
            self.assertIn(attendu, jetons)

    def test_aucun_faux_positif(self):
        """Le remplaçant ne doit jamais être signalé, et `Instance.new` seul est
        parfaitement correct — c'est son second argument qui ne l'est pas."""
        code = ('task.wait(1)\ntask.spawn(f)\nlocal p = Instance.new("Part")\n'
                'p.Parent = workspace\nx:Connect(g)\np:Destroy()\n'
                'print(os.clock())\n')
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "b.luau"
            f.write_text(code, encoding="utf-8")
            trouves = luau.balayer(pathlib.Path(d), self.regles)
        self.assertEqual(trouves, [], f"faux positif : {trouves}")

    def test_commentaire_ignore(self):
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "c.luau"
            f.write_text("-- wait(1) est déprécié\nlocal x = 1\n", encoding="utf-8")
            self.assertEqual(luau.balayer(pathlib.Path(d), self.regles), [])


class Toolbox(unittest.TestCase):
    def test_modele_script_ecarte(self):
        a = {"type_id": 10, "scripts": True, "gratuit": True, "dispo": True}
        ok, raison = toolbox.utilisable(a, avec_scripts=False)
        self.assertFalse(ok)
        self.assertIn("scripts", raison)

    def test_modele_script_sur_demande(self):
        a = {"type_id": 10, "scripts": True, "gratuit": True, "dispo": True}
        self.assertTrue(toolbox.utilisable(a, avec_scripts=True)[0])

    def test_son_script_sans_objet(self):
        a = {"type_id": 3, "scripts": None, "gratuit": True, "dispo": True}
        self.assertTrue(toolbox.utilisable(a, avec_scripts=False)[0])

    def test_payant_ecarte(self):
        a = {"type_id": 3, "gratuit": False, "dispo": True}
        self.assertFalse(toolbox.utilisable(a, avec_scripts=False)[0])

    def test_normalisation_economie(self):
        a = toolbox._normalise_economie({
            "AssetId": 7, "Name": "n", "AssetTypeId": 24, "IsPublicDomain": True,
            "Creator": {"Name": "Moi", "CreatorTargetId": 1}})
        self.assertEqual((a["id"], a["createur"], a["type_id"]), (7, "Moi", 24))
        self.assertIsNone(a["scripts"], "cette route ne sait pas : ne pas inventer")

    def test_animation_liee_au_createur(self):
        self.assertIn(toolbox.TYPES["animation"], toolbox.LIEE_AU_CREATEUR)
        self.assertNotIn(toolbox.TYPES["son"], toolbox.LIEE_AU_CREATEUR)


class Aide(unittest.TestCase):
    def test_conversion(self):
        html, toc = build_help.convertir(
            "# Titre\n\n## Une section\n\nDu texte avec `du code`.\n\n"
            "| a | b |\n|---|---|\n| 1 | 2 |\n")
        self.assertIn("<h1", html)
        self.assertIn("<table>", html)
        self.assertIn("<code>du code</code>", html)
        self.assertEqual([t for _, t in toc], ["Une section"])

    def test_code_protege_du_gras(self):
        self.assertIn("<code>**pas du gras**</code>",
                      build_help.enligne("`**pas du gras**`"))


class Encodage(unittest.TestCase):
    def test_pas_de_plantage_en_cp1252(self):
        """Le bug de la 0.6 : le script faisait son travail, affichait « OK »,
        puis sortait en 1 parce que la console Windows ne savait pas encoder
        une flèche. Un script qui échoue après avoir réussi apprend à ignorer
        son verdict."""
        import os
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        for script in ("scripts/validate.py",
                       "plugins/roblox/scripts/luau_check.py"):
            with self.subTest(script=script):
                r = subprocess.run([sys.executable, script, "--help"],
                                   cwd=RACINE, env=env,
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr[-400:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
