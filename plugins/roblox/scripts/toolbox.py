#!/usr/bin/env python3
"""Cherche un asset réel dans la Toolbox Roblox, et vérifie qu'il existe.

Un `rbxassetid://` inventé de mémoire est le pire des défauts : il a l'air
juste, il passe la relecture, et il donne un son muet ou une texture invisible
que personne ne sait expliquer. Ce script existe pour qu'aucun identifiant
écrit par Claude ne vienne d'ailleurs que d'une réponse de Roblox.

    toolbox.py chercher --type son    --query "impact epee"
    toolbox.py chercher --type modele --query "caisse en bois"
    toolbox.py verifier --ids 140277245983305,9046286664

Types : son, modele, mesh, image, animation.

Une animation trouvée ici ne peut PAS servir de placeholder : Roblox lie une
animation à son créateur, et une animation qui ne t'appartient pas ne se
charge pas dans ton jeu publié. La recherche sert à vérifier une animation que
tu as déjà, pas à en emprunter une.

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
# La route ci-dessus refuse les animations (404). Celle-ci répond pour tout,
# avec moins de champs — mais elle porte le créateur, qui est ce qui décide
# qu'une animation se chargera ou non.
ECONOMIE = "https://economy.roblox.com/v2/assets/{id}/details"

# Vérifiés un par un contre l'API : ce sont les seuls types qui répondent.
TYPES = {
    "son": 3,
    "modele": 10,
    "image": 13,
    "mesh": 40,
    "animation": 24,
}

# Roblox refuse de charger une animation dont le créateur n'est pas le
# propriétaire du jeu. Elle peut marcher dans Studio chez son auteur et échouer
# pour tous les joueurs une fois publié — le défaut le plus pénible à
# diagnostiquer, parce qu'il ne se voit pas là où on teste.
LIEE_AU_CREATEUR = {24}

# Les types où un script peut se cacher. Un son n'en contient pas.
SCRIPTABLES = {10, 40}


def appel(url, params):
    requete = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"Accept": "application/json", "User-Agent": "HatSkills/toolbox"},
    )
    with urllib.request.urlopen(requete, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def _normalise_toolbox(item):
    a = item["asset"]
    argent = item.get("fiatProduct") or {}
    c = item.get("creator") or {}
    return {
        "id": a["id"], "nom": a.get("name", "?"), "type_id": a.get("typeId"),
        "duree": a.get("duration"), "scripts": a.get("hasScripts"),
        "createur": c.get("name", "?"), "createur_id": c.get("id"),
        "verifie": bool(c.get("isVerifiedCreator")),
        "gratuit": argent.get("isFree", True),
        "dispo": argent.get("purchasable", True),
    }


def _normalise_economie(d):
    c = d.get("Creator") or {}
    prix = d.get("PriceInRobux")
    return {
        "id": d.get("AssetId"), "nom": d.get("Name", "?"),
        "type_id": d.get("AssetTypeId"), "duree": None,
        "scripts": None,  # inconnu par cette route : ne pas prétendre le contraire
        "createur": c.get("Name", "?"), "createur_id": c.get("CreatorTargetId"),
        "verifie": bool(c.get("HasVerifiedBadge")),
        "gratuit": bool(d.get("IsPublicDomain")) or prix in (None, 0),
        "dispo": True,
    }


def details(ids):
    """Détails normalisés. Un id absent du retour n'existe plus.

    Deux sources : la route Toolbox, riche (durée, présence de scripts) mais
    muette sur les animations, puis la route économie pour ce qu'elle a laissé
    tomber. Se contenter de la première faisait conclure qu'une animation
    n'existe pas, alors qu'elle n'était simplement pas servie là.
    """
    if not ids:
        return []
    trouves = {}
    try:
        for item in appel(DETAILS, {"assetIds": ",".join(str(i) for i in ids)}).get("data", []):
            n = _normalise_toolbox(item)
            trouves[n["id"]] = n
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        pass  # le repli couvre tout : ce n'est pas une panne

    for i in ids:
        if i in trouves:
            continue
        try:
            trouves[i] = _normalise_economie(appel(ECONOMIE.format(id=i), {}))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            pass  # vraiment introuvable : l'appelant le signalera
    return [trouves[i] for i in ids if i in trouves]


def utilisable(a, avec_scripts):
    """(ok, raison du rejet). La raison sert à expliquer une liste vide."""
    if not a.get("gratuit", True):
        return False, "payant"
    if not a.get("dispo", True):
        return False, "non disponible"
    if a.get("type_id") in SCRIPTABLES and a.get("scripts") and not avec_scripts:
        return False, "contient des scripts"
    return True, ""


def ligne(a):
    verifie = "✔" if a.get("verifie") else " "
    duree = f"{a['duree']:>4} s" if a.get("duree") else "      "
    scripts = "  ⚠ scripts" if a.get("scripts") else ""
    return (f"  {a['id']:<16}{duree}  {a['nom'][:38]:<38} "
            f"{a['createur'][:18]:<18}{verifie}{scripts}")


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
    if TYPES[args.type] in LIEE_AU_CREATEUR:
        print("\n⚠ Une animation est liée à son créateur. Aucun de ces "
              "identifiants ne se chargera\n  dans un jeu qui ne t'appartient "
              "pas — n'en écris aucun dans Config/Assets.luau.\n  Cette "
              "recherche sert à vérifier une animation que tu as déjà.")
        return 0
    print("\nCopie l'identifiant dans Config/Assets.luau en notant sa provenance.")
    return 0


def cmd_verifier(args):
    demandes = [int(x) for x in args.ids.replace(" ", "").split(",") if x]
    try:
        vus = {a["id"]: a for a in details(demandes)}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"ERREUR : Roblox n'a pas répondu ({e}).", file=sys.stderr)
        return 1

    attendu = (args.proprietaire or "").strip().lower()
    perdus = 0
    for i in demandes:
        a = vus.get(i)
        if not a:
            # Un asset de la Toolbox peut être modéré ou retiré après coup.
            # L'identifiant reste valide en apparence et ne charge plus rien.
            print(f"  {i:<16} INTROUVABLE — retiré ou modéré, à remplacer")
            perdus += 1
            continue
        ok, raison = utilisable(a, args.avec_scripts)
        etat = "ok" if ok else f"REJET : {raison}"
        # Le piège des animations : celle-ci existe, elle est gratuite, et elle
        # ne se chargera jamais dans le jeu de quelqu'un d'autre.
        if ok and attendu and a["type_id"] in LIEE_AU_CREATEUR \
                and a["createur"].strip().lower() != attendu:
            etat = f"NE CHARGERA PAS : appartient à {a['createur']}"
            ok = False
        perdus += 0 if ok else 1
        print(f"  {i:<16} {etat:<40} « {a['nom'][:32]} »")

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
    v.add_argument("--proprietaire", help="nom du compte ou groupe qui possède "
                   "le jeu : signale une animation qui ne se chargera pas")
    v.add_argument("--avec-scripts", action="store_true")
    v.set_defaults(func=cmd_verifier)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
