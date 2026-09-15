#!/usr/bin/env python3
"""Cherche un asset réel dans la Toolbox Roblox, et vérifie qu'il existe.

Un `rbxassetid://` inventé de mémoire est le pire des défauts : il a l'air
juste, il passe la relecture, et il donne un son muet ou une texture invisible
que personne ne sait expliquer. Ce script existe pour qu'aucun identifiant
écrit par Claude ne vienne d'ailleurs que d'une réponse de Roblox.

    toolbox.py chercher --type son    --query "impact epee"
    toolbox.py chercher --type modele --query "caisse en bois"
    toolbox.py verifier --ids 140277245983305,9046286664

Types : son, modele, mesh, image. Les animations ne sont pas exposées par
l'API de la Toolbox — elles restent à publier à la main.

Par défaut, seuls les assets gratuits et disponibles sortent, et les modèles
contenant des scripts sont écartés : un modèle scripté de la Toolbox est le
vecteur de backdoor le plus courant sur Roblox. `--avec-scripts` les rétablit,
en le disant.

Stdlib uniquement.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

# Windows : la console est en cp1252 par défaut, et les flèches ou accents de
# ce script la font lever UnicodeEncodeError — donc planter APRÈS avoir fait
# son travail. Un script qui échoue une fois qu'il a réussi apprend à ignorer
# son verdict, ce qui est pire que pas de script du tout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


RECHERCHE = "https://apis.roblox.com/toolbox-service/v1/marketplace/{type_id}"
DETAILS = "https://apis.roblox.com/toolbox-service/v1/items/details"

# Vérifiés un par un contre l'API : ce sont les seuls types qui répondent.
TYPES = {
    "son": 3,
    "modele": 10,
    "image": 13,
    "mesh": 40,
}

# Les types où un script peut se cacher. Un son n'en contient pas.
SCRIPTABLES = {10, 40}


def appel(url, params):
    requete = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"Accept": "application/json", "User-Agent": "HatSkills/toolbox"},
    )
    with urllib.request.urlopen(requete, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def details(ids):
    """Les détails de plusieurs assets. Un id absent du retour n'existe plus."""
    if not ids:
        return []
    return appel(DETAILS, {"assetIds": ",".join(str(i) for i in ids)}).get("data", [])


def utilisable(item, avec_scripts):
    """(ok, raison du rejet). La raison sert à expliquer une liste vide."""
    a = item.get("asset", {})
    argent = item.get("fiatProduct") or {}
    if argent and not argent.get("isFree", True):
        return False, "payant"
    if argent and not argent.get("purchasable", True):
        return False, "non disponible"
    if a.get("typeId") in SCRIPTABLES and a.get("hasScripts") and not avec_scripts:
        return False, "contient des scripts"
    return True, ""


def ligne(item):
    a = item["asset"]
    createur = (item.get("creator") or {}).get("name", "?")
    verifie = "✔" if (item.get("creator") or {}).get("isVerifiedCreator") else " "
    duree = f"{a['duration']:>4} s" if a.get("duration") else "      "
    scripts = "  ⚠ scripts" if a.get("hasScripts") else ""
    return (f"  {a['id']:<16}{duree}  {a['name'][:38]:<38} "
            f"{createur[:18]:<18}{verifie}{scripts}")


def cmd_chercher(args):
    type_id = TYPES[args.type]
    try:
        brut = appel(RECHERCHE.format(type_id=type_id),
                     {"limit": max(args.limite * 3, 10), "keyword": args.query})
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"ERREUR : la Toolbox n'a pas répondu ({e}).", file=sys.stderr)
        print("Sans réponse, ne devine pas d'identifiant : laisse 0 et dis-le.",
              file=sys.stderr)
        return 1

    ids = [x["id"] for x in brut.get("data", [])]
    if not ids:
        print(f"Aucun {args.type} pour « {args.query} ». Reformule la recherche "
              "en anglais : la Toolbox est indexée en anglais.")
        return 1

    gardes, rejets = [], {}
    for item in details(ids):
        ok, raison = utilisable(item, args.avec_scripts)
        if ok:
            gardes.append(item)
        else:
            rejets[raison] = rejets.get(raison, 0) + 1
        if len(gardes) >= args.limite:
            break

    if not gardes:
        detail = ", ".join(f"{n} {r}" for r, n in sorted(rejets.items()))
        print(f"Aucun {args.type} utilisable pour « {args.query} » "
              f"({detail or 'aucun détail disponible'}).")
        return 1

    print(f"{args.type} « {args.query} » — {len(gardes)} candidat(s) vérifié(s) "
          "auprès de Roblox :\n")
    for item in gardes:
        print(ligne(item))
    if rejets:
        detail = ", ".join(f"{n} {r}" for r, n in sorted(rejets.items()))
        print(f"\n({detail} — écarté(s))")
    print("\nCopie l'identifiant dans Config/Assets.luau en notant sa provenance.")
    return 0


def cmd_verifier(args):
    demandes = [int(x) for x in args.ids.replace(" ", "").split(",") if x]
    try:
        trouves = details(demandes)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"ERREUR : la Toolbox n'a pas répondu ({e}).", file=sys.stderr)
        return 1

    vus = {}
    for item in trouves:
        vus[item["asset"]["id"]] = item

    perdus = 0
    for i in demandes:
        item = vus.get(i)
        if not item:
            # Un asset de la Toolbox peut être modéré ou retiré après coup.
            # L'identifiant reste valide en apparence et ne charge plus rien.
            print(f"  {i:<16} INTROUVABLE — retiré ou modéré, à remplacer")
            perdus += 1
            continue
        ok, raison = utilisable(item, args.avec_scripts)
        etat = "ok" if ok else f"REJET : {raison}"
        perdus += 0 if ok else 1
        print(f"  {i:<16} {etat:<24} « {item['asset']['name'][:34]} »")

    print(f"\n{len(demandes) - perdus}/{len(demandes)} utilisable(s).")
    return 1 if perdus else 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("chercher", help="trouver un asset réel")
    c.add_argument("--type", required=True, choices=sorted(TYPES))
    c.add_argument("--query", required=True, help="en anglais : l'index l'est")
    c.add_argument("--limite", type=int, default=5)
    c.add_argument("--avec-scripts", action="store_true",
                   help="autoriser les modèles scriptés (backdoor possible)")
    c.set_defaults(func=cmd_chercher)

    v = sub.add_parser("verifier", help="un identifiant existe-t-il encore ?")
    v.add_argument("--ids", required=True, help="ex. 140277245983305,9046286664")
    v.add_argument("--avec-scripts", action="store_true")
    v.set_defaults(func=cmd_verifier)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
