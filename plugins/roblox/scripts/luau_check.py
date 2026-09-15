#!/usr/bin/env python3
"""Cherche les API Roblox dépréciées dans du Luau, sans ouvrir Studio.

« Zéro API dépréciée » est la règle la plus répétée du plugin, et jusqu'ici
elle reposait entièrement sur le fait que le modèle s'en souvienne au bon
moment. Une règle qu'on espère n'est pas une règle. Ce script lit la table des
remplacements — la même que celle du skill `code`, pas une copie qui
divergerait — et balaye le projet.

    luau_check.py                       # balaye ./src
    luau_check.py --dans chemin/ --format court

Sort en code 1 s'il reste une occurrence. Stdlib uniquement, aucun réseau :
il tourne Studio fermé, et il attrape aussi le code écrit avant le plugin.
"""

import argparse
import pathlib
import re
import sys

# Windows : la console est en cp1252 par défaut, et les flèches ou accents de
# ce script la font lever UnicodeEncodeError — donc planter APRÈS avoir fait
# son travail. Un script qui échoue une fois qu'il a réussi apprend à ignorer
# son verdict, ce qui est pire que pas de script du tout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


TABLE = (pathlib.Path(__file__).resolve().parent.parent
         / "skills" / "code" / "references" / "api-obsolete.md")

# Entrées de la table qui ne décrivent pas un identifiant cherchable : ce sont
# des conseils de forme, pas des noms à remplacer.
INCHERCHABLES = {"f()", "—", "-"}

# Entrées dont la forme naïve produirait un faux positif sur du code correct.
# `Instance.new` est parfaitement valide ; c'est le second argument qui ne
# l'est pas.
SUR_MESURE = {
    'Instance.new("X", parent)': r'Instance\.new\s*\([^)\n]*,',
}


def motif(jeton):
    """Regex cherchant `jeton` dans du Luau, sans attraper son remplaçant.

    Le point d'attention est `wait(` : il ne doit pas se déclencher sur
    `task.wait(`. D'où la garde arrière sur le point et les caractères de mot.
    """
    if jeton in SUR_MESURE:
        return SUR_MESURE[jeton]
    if jeton.startswith(":"):
        return re.escape(jeton.split("(")[0]) + r"\s*\("
    if "(" in jeton:
        nom, _, reste = jeton.partition("(")
        # `Instance.new("Message")` ne vise pas tous les Instance.new : c'est
        # l'argument qui est déprécié, pas l'appel. Couper au « ( » ferait
        # hurler le script sur du code parfaitement correct — et un outil qui
        # produit des faux positifs, on cesse de le lire.
        litteral = re.search(r'["\']([^"\']+)["\']', reste)
        if litteral:
            return (re.escape(nom) + r'\s*\(\s*["\']'
                    + re.escape(litteral.group(1)) + r'["\']')
        return r"(?<![.\w:])" + re.escape(nom) + r"\s*\("
    return r"(?<![.\w])" + re.escape(jeton) + r"(?![\w])"


def regles():
    """(motif compilé, ce qu'il faut écrire à la place, niveau) depuis la table.

    Lire la table du skill plutôt que d'en garder une copie : deux listes de
    dépréciations finissent toujours par diverger, et c'est celle du script
    qu'on oublie de mettre à jour.
    """
    if not TABLE.exists():
        print(f"ERREUR : table introuvable ({TABLE}).", file=sys.stderr)
        return []
    out, vus = [], set()
    for ligne in TABLE.read_text(encoding="utf-8").splitlines():
        if not ligne.startswith("|") or set(ligne) <= set("|-: "):
            continue
        cols = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if len(cols) < 2 or cols[0].startswith("À éviter"):
            continue
        remplacant = re.sub(r"`", "", cols[1]).strip()
        niveau = cols[2] if len(cols) > 2 else ""
        for jeton in re.findall(r"`([^`]+)`", cols[0]):
            if jeton in INCHERCHABLES or jeton in vus or len(jeton) < 3:
                continue
            vus.add(jeton)
            out.append((jeton, re.compile(motif(jeton)), remplacant, niveau))
    return out


def sans_commentaire(ligne):
    """Coupe un commentaire de fin de ligne. Approximatif et assumé : rater un
    `--` dans une chaîne ne produit qu'un faux négatif, jamais un faux positif
    — et un faux positif ferait ignorer le script."""
    i = ligne.find("--")
    return ligne if i < 0 else ligne[:i]


def balayer(racine, regles_):
    trouves = []
    # Accepter un fichier seul autant qu'un dossier : « vérifie ce script-là »
    # est la demande la plus naturelle, et rglob sur un fichier ne rend rien —
    # le script aurait répondu « aucune API dépréciée » sans rien lire.
    cibles = [racine] if racine.is_file() else sorted(racine.rglob("*"))
    for f in cibles:
        if f.suffix not in (".luau", ".lua") or not f.is_file():
            continue
        try:
            lignes = f.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        dans_bloc = False
        for n, brute in enumerate(lignes, 1):
            if "--[[" in brute:
                dans_bloc = True
            if dans_bloc:
                if "]]" in brute:
                    dans_bloc = False
                continue
            ligne = sans_commentaire(brute)
            for jeton, rx, remplacant, niveau in regles_:
                if rx.search(ligne):
                    trouves.append((f, n, jeton, remplacant, niveau, brute.strip()))
    return trouves


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dans", default="src", help="dossier à balayer (défaut : src)")
    ap.add_argument("--format", choices=("long", "court"), default="long")
    a = ap.parse_args()

    racine = pathlib.Path(a.dans)
    if not racine.exists():
        print(f"Rien à balayer : {racine} n'existe pas.")
        return 0

    rg = regles()
    if not rg:
        return 1

    trouves = balayer(racine, rg)
    if not trouves:
        n = (1 if racine.is_file() else
             sum(1 for f in racine.rglob("*") if f.suffix in (".luau", ".lua")))
        print(f"{n} fichier(s) Luau — aucune API dépréciée "
              f"({len(rg)} motifs cherchés).")
        return 0

    for f, n, jeton, remplacant, niveau, brute in trouves:
        print(f"{f}:{n}  {jeton} → {remplacant}"
              + (f"  [{niveau}]" if niveau and a.format == "long" else ""))
        if a.format == "long":
            print(f"    {brute[:100]}")

    fichiers = len({f for f, *_ in trouves})
    print(f"\n{len(trouves)} occurrence(s) dans {fichiers} fichier(s). "
          "Remplacement dans api-obsolete.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
