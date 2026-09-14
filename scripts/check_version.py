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

MANIFESTE = "plugins/roblox/.claude-plugin/plugin.json"
SURVEILLE = "plugins/"


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
                 ("diff", "--name-only")):
        changes.update((git(*args) or "").splitlines())
    touches = sorted(f for f in changes if f.startswith(SURVEILLE))
    if not touches:
        print("Aucun fichier du plugin modifié — rien à vérifier.")
        return 0

    avant, apres = version_a(fourche), version_actuelle()
    if avant is None:
        print(f"Pas de version à la base : nouveau manifeste, version {apres}.")
        return 0

    if avant == apres:
        print(f"ERREUR : {len(touches)} fichier(s) du plugin modifié(s), "
              f"mais version inchangée ({avant}).")
        for f in touches[:8]:
            print(f"  {f}")
        if len(touches) > 8:
            print(f"  … et {len(touches) - 8} autre(s)")
        print(f"\nBumpe 'version' dans {MANIFESTE}.")
        print("Sans ça, personne ne recevra cette mise à jour : le plugin "
              "installé restera sur l'ancienne version, en silence.")
        return 1

    print(f"Version {avant} → {apres} pour {len(touches)} fichier(s) modifié(s). OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
