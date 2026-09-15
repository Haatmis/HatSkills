#!/usr/bin/env python3
"""Refuse une modification du plugin sans changement de version.

Un plugin installé ne reçoit de mise à jour que si `version` change dans
plugin.json. Oublier de la bumper ne casse rien visiblement : ça rend
simplement tout le travail invisible pour ceux qui l'ont déjà installé. Le
défaut est donc silencieux, et c'est exactement ce qu'une vérification
automatique doit attraper.

    python3 scripts/check_version.py [base]     # base par défaut : origin/main
"""

import json
import pathlib
import subprocess
import sys

# Windows : la console est en cp1252 par défaut, et les flèches ou accents de
# ce script la font lever UnicodeEncodeError — donc planter APRÈS avoir fait
# son travail. Un script qui échoue une fois qu'il a réussi apprend à ignorer
# son verdict, ce qui est pire que pas de script du tout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


MANIFESTE = "plugins/roblox/.claude-plugin/plugin.json"
SURVEILLE = "plugins/"
# Une version mineure ou majeure, c'est une « grosse maj » : elle doit arriver
# avec de quoi la comprendre, sinon personne ne sait ce qui a changé — l'auteur
# le premier, six mois plus tard.
AVEC_LA_MAJ = ("plugins/roblox/GUIDE.md", "CHANGELOG.md")


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def version_a(ref):
    """Version du manifeste à une référence git. `None` s'il n'existe pas."""
    brut = git("show", f"{ref}:{MANIFESTE}")
    if brut is None:
        return None
    try:
        return json.loads(brut).get("version")
    except json.JSONDecodeError:
        return None


def version_actuelle():
    """Version sur le disque, pas dans HEAD : le script doit servir AVANT le
    commit, sinon il ne prévient qu'une fois le défaut déjà poussé."""
    try:
        return json.loads(pathlib.Path(MANIFESTE).read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError):
        return None


def triplet(v):
    """'0.2.0' -> (0, 2, 0). None si ce n'est pas du semver lisible."""
    try:
        parts = [int(x) for x in str(v).split(".")[:3]]
        return tuple(parts + [0] * (3 - len(parts)))
    except (ValueError, AttributeError):
        return None


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    fourche = git("merge-base", "HEAD", base)
    if not fourche:
        print(f"Base '{base}' introuvable — vérification ignorée "
              "(historique tronqué ? il faut fetch-depth: 0).")
        return 0

    # Commits + index + copie de travail : le défaut doit se voir avant d'être
    # poussé, pas après.
    changes = set()
    for args in (("diff", "--name-only", fourche, "HEAD"),
                 ("diff", "--name-only", "--cached"),
                 ("diff", "--name-only"),
                 # git diff ignore les fichiers non suivis : sans cette ligne,
                 # un GUIDE.md tout neuf est invisible au garde-fou.
                 ("ls-files", "--others", "--exclude-standard")):
        changes.update((git(*args) or "").splitlines())
    touches = sorted(f for f in changes if f.startswith(SURVEILLE))
    if not touches:
        print("Aucun fichier du plugin modifié — rien à vérifier.")
        return 0

    apres = version_actuelle()
    # Deux références, pas une. La base de fusion dit d'où part cette branche ;
    # la pointe de la base dit ce qui est DÉJÀ publié. Ne regarder que la
    # première laisse passer une version qui n'avance pas sur le publié : deux
    # sessions partent de 0.7.0, l'une publie 0.8.0, l'autre livre 0.7.1 — la
    # comparaison à la fourche dit « ça monte », et pourtant personne ne reçoit
    # rien, parce que 0.7.1 est derrière la version déjà installée.
    avant = version_a(fourche)
    publie = version_a(base)
    if avant is None and publie is None:
        print(f"Pas de version à la base : nouveau manifeste, version {apres}.")
        return 0

    candidats = [(triplet(v), v) for v in (avant, publie) if triplet(v)]
    reference = max(candidats)[1] if candidats else avant
    ta, tb = triplet(reference), triplet(apres)

    if ta and tb and tb <= ta:
        cause = ("inchangée" if tb == ta else "en recul")
        print(f"ERREUR : {len(touches)} fichier(s) du plugin modifié(s), "
              f"mais version {cause} ({reference} → {apres}).")
        if reference == publie and publie != avant:
            print(f"  La version {publie} est déjà publiée sur {base} — "
                  "il faut passer devant, pas à côté.")
        for f in touches[:8]:
            print(f"  {f}")
        if len(touches) > 8:
            print(f"  … et {len(touches) - 8} autre(s)")
        print(f"\nBumpe 'version' dans {MANIFESTE}.")
        print("Sans ça, personne ne recevra cette mise à jour : le plugin "
              "installé restera sur l'ancienne version, en silence.")
        return 1

    avant = reference

    # Grosse mise à jour : le guide et le journal des versions suivent.
    a, b = triplet(avant), triplet(apres)
    if a and b and (a[0], a[1]) != (b[0], b[1]):
        oublis = [f for f in AVEC_LA_MAJ if f not in changes]
        if oublis:
            accord = "n'a pas été mis à jour" if len(oublis) == 1 \
                else "n'ont pas été mis à jour"
            print(f"ERREUR : version mineure {avant} → {apres}, mais "
                  f"{' et '.join(oublis)} {accord}.")
            print("\nUne grosse mise à jour arrive avec de quoi la comprendre. "
                  "Voir la règle permanente dans CLAUDE.md.")
            return 1
        print(f"Version {avant} → {apres} (mineure) — guide et changelog à jour. OK.")
        return 0

    print(f"Version {avant} → {apres} pour {len(touches)} fichier(s) modifié(s). OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
