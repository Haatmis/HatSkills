#!/usr/bin/env python3
"""Journal d'apprentissage du plugin roblox.

Accumule les leçons tirées de l'usage réel des skills, pour qu'elles soient
consolidées plus tard dans les SKILL.md par /roblox:atelier.

Le journal vit dans ${CLAUDE_PLUGIN_DATA}, qui survit aux mises à jour du
plugin et est partagé entre tous tes projets.

    journal.py add --skill code --type correction --lesson "..." [--context "..."]
    journal.py status                 # combien de leçons en attente
    journal.py list [--skill code] [--all]
    journal.py resolve --ids 3,7 [--note "promu dans le Contexte figé"]

Stdlib uniquement. Les entrées identiques sont fusionnées : leur compteur
`occurrences` monte au lieu de créer un doublon — c'est ce compteur qui dit
ce qui mérite vraiment d'entrer dans un skill.
"""

import argparse
import json
import os
import re
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows : la console est en cp1252 par défaut, et les flèches ou accents de
# ce script la font lever UnicodeEncodeError — donc planter APRÈS avoir fait
# son travail. Un script qui échoue une fois qu'il a réussi apprend à ignorer
# son verdict, ce qui est pire que pas de script du tout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SEUIL = 8          # au-delà, on signale qu'il y a de la matière à consolider
TYPES = {
    "correction":   "l'utilisateur m'a corrigé",
    "studio-error": "Studio a révélé une erreur que j'avais commise",
    "re-precision": "l'utilisateur a dû re-préciser un contexte",
}


def data_dir(explicite=None):
    """Où vit le journal, par ordre de priorité.

    HATSKILLS_JOURNAL_DIR passe avant CLAUDE_PLUGIN_DATA : c'est ce qui permet
    de pointer un dossier synchronisé (le repo, un cloud) pour que les leçons
    d'une machine rejoignent celles des autres. CLAUDE_PLUGIN_DATA reste le
    défaut sain — par plugin, persistant, mais local à la machine, et perdu
    dans une session cloud éphémère.
    """
    for candidat in (explicite,
                     os.environ.get("HATSKILLS_JOURNAL_DIR"),
                     os.environ.get("CLAUDE_PLUGIN_DATA")):
        if candidat and candidat.strip() and "${" not in candidat:
            return Path(candidat).expanduser()
    return Path.home() / ".claude" / "plugins" / "data" / "roblox-hatskills"


def chemin(args):
    d = data_dir(getattr(args, "data_dir", None))
    d.mkdir(parents=True, exist_ok=True)
    return d / "journal.jsonl"


def lire(p):
    if not p.exists():
        return []
    entrees = []
    for ligne in p.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne:
            try:
                entrees.append(json.loads(ligne))
            except json.JSONDecodeError:
                pass  # une ligne corrompue ne doit pas faire perdre le reste
    return entrees


def ecrire(p, entrees):
    tmp = p.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n"
                           for e in entrees), encoding="utf-8")
    tmp.replace(p)


def cle(texte):
    """Normalise une leçon pour reconnaître les redites."""
    return re.sub(r"[^a-z0-9]+", " ", texte.lower()).strip()


def cmd_add(args):
    p = chemin(args)
    entrees = lire(p)
    k = cle(args.lesson)

    for e in entrees:
        if e.get("statut") == "en-attente" and cle(e["lesson"]) == k \
                and e["skill"] == args.skill:
            e["occurrences"] = e.get("occurrences", 1) + 1
            e["vu_le"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            ecrire(p, entrees)
            print(f"Leçon déjà connue → occurrences = {e['occurrences']} "
                  f"(id {e['id']})")
            return rappel(entrees)

    entree = {
        "id": max((e.get("id", 0) for e in entrees), default=0) + 1,
        "cree_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skill": args.skill,
        "type": args.type,
        "lesson": args.lesson.strip(),
        "context": (args.context or "").strip(),
        "occurrences": 1,
        "machine": socket.gethostname(),
        "statut": "en-attente",
    }
    entrees.append(entree)
    ecrire(p, entrees)
    print(f"Leçon enregistrée (id {entree['id']}) → {p}")
    return rappel(entrees)


def rappel(entrees):
    n = sum(1 for e in entrees if e.get("statut") == "en-attente")
    if n >= SEUIL:
        print(f"\n>>> {n} leçons en attente (seuil {SEUIL}). "
              "Signale à l'utilisateur qu'il peut lancer /roblox:atelier.")
    return 0


def cmd_status(args):
    entrees = [e for e in lire(chemin(args)) if e.get("statut") == "en-attente"]
    if not entrees:
        print("Journal vide : rien à consolider.")
        return 0
    par_skill = {}
    for e in entrees:
        par_skill.setdefault(e["skill"], []).append(e)
    print(f"{len(entrees)} leçon(s) en attente (seuil {SEUIL}) :")
    for skill, lst in sorted(par_skill.items()):
        recurrentes = sum(1 for e in lst if e.get("occurrences", 1) > 1)
        suffixe = f", dont {recurrentes} récurrente(s)" if recurrentes else ""
        print(f"  {skill:16} {len(lst)}{suffixe}")
    if len(entrees) >= SEUIL:
        print("\n>>> Seuil atteint : propose /roblox:atelier à l'utilisateur.")
    return 0


def cmd_list(args):
    entrees = lire(chemin(args))
    if not args.all:
        entrees = [e for e in entrees if e.get("statut") == "en-attente"]
    if args.skill:
        entrees = [e for e in entrees if e["skill"] == args.skill]
    if not entrees:
        print("Aucune entrée.")
        return 0
    # Le plus récurrent d'abord : c'est ce qui mérite d'entrer dans un skill.
    entrees.sort(key=lambda e: (-e.get("occurrences", 1), e.get("id", 0)))
    for e in entrees:
        n = e.get("occurrences", 1)
        marque = f" ×{n}" if n > 1 else ""
        etat = "" if e.get("statut") == "en-attente" else f" [{e['statut']}]"
        machines = {x.get("machine") for x in entrees if x.get("machine")}
        prov = f" @{e['machine']}" if len(machines) > 1 and e.get("machine") else ""
        print(f"\n[{e['id']}] {e['skill']} / {e['type']}{marque}{etat}{prov}")
        print(f"    {e['lesson']}")
        if e.get("context"):
            print(f"    contexte : {e['context']}")
    return 0


def cmd_resolve(args):
    p = chemin(args)
    entrees = lire(p)
    ids = {int(x) for x in args.ids.split(",") if x.strip()}
    touches = 0
    for e in entrees:
        if e.get("id") in ids and e.get("statut") == "en-attente":
            e["statut"] = "consolide"
            e["consolide_le"] = datetime.now(timezone.utc).isoformat(
                timespec="seconds")
            if args.note:
                e["note"] = args.note
            touches += 1
    ecrire(p, entrees)
    manquants = ids - {e["id"] for e in entrees}
    print(f"{touches} entrée(s) marquée(s) consolidée(s).")
    if manquants:
        print(f"Ignorés (inconnus) : {sorted(manquants)}")

    # Journal partagé : deux machines ont pu attribuer le même id.
    for i in sorted(ids):
        homonymes = [e for e in entrees if e.get("id") == i]
        if len(homonymes) > 1:
            machines = ", ".join(sorted({e.get("machine", "?") for e in homonymes}))
            print(f"  ⚠ id {i} portée par {len(homonymes)} entrées ({machines}) "
                  "— toutes marquées. Vérifie que c'était voulu.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", help="normalement ${CLAUDE_PLUGIN_DATA}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="enregistrer une leçon")
    a.add_argument("--skill", required=True)
    a.add_argument("--type", required=True, choices=sorted(TYPES))
    a.add_argument("--lesson", required=True,
                   help="la règle à retenir, formulée à l'impératif")
    a.add_argument("--context", help="ce qui se passait, en une ligne")
    a.set_defaults(func=cmd_add)

    s = sub.add_parser("status", help="compter les leçons en attente")
    s.set_defaults(func=cmd_status)

    l = sub.add_parser("list", help="afficher les leçons")
    l.add_argument("--skill")
    l.add_argument("--all", action="store_true", help="y compris consolidées")
    l.set_defaults(func=cmd_list)

    r = sub.add_parser("resolve", help="marquer des leçons comme consolidées")
    r.add_argument("--ids", required=True, help="ex. 3,7,12")
    r.add_argument("--note")
    r.set_defaults(func=cmd_resolve)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
