#!/usr/bin/env python3
"""Vérifie les SKILL.md du repo : frontmatter, déclenchement, chevauchement.

Usage:
    python3 scripts/validate.py [chemin...]

Sans argument, scanne tout le repo. Sort en code 1 s'il reste des ERREURs.
Stdlib uniquement — pas de dépendance à installer.
"""

import re
import sys
from pathlib import Path

# Windows : la console est en cp1252 par défaut, et les flèches ou accents de
# ce script la font lever UnicodeEncodeError — donc planter APRÈS avoir fait
# son travail. Un script qui échoue une fois qu'il a réussi apprend à ignorer
# son verdict, ce qui est pire que pas de script du tout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Champs reconnus par Claude Code dans le frontmatter d'un SKILL.md.
KNOWN_KEYS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools",
    "disallowed-tools", "model", "effort", "context", "agent", "background",
    "hooks", "paths", "shell", "metadata", "license", "compatibility",
}

DESC_CHAR_CAP = 1536   # description + when_to_use
BODY_LINE_CAP = 500    # au-delà : passer en references/
REF_TOC_LINES = 300    # au-delà : table des matières attendue
OVERLAP_WARN = 0.35    # similarité de vocabulaire entre deux descriptions

# Mots vides FR/EN, pour que la comparaison porte sur le vocabulaire utile.
STOP = set("""
a ai au aux avec ce ces dans de des du elle en et eux il je la le les leur lui
ma mais me meme mes moi mon ne nos notre nous on ou par pas pour qu que qui sa
se ses son sur ta te tes toi ton tu un une vos votre vous c d j l m n s t y ete
etee etees etes etant suis es est sommes etes sont sera serai seras aura avoir
etre fait faire cette quand utilise utiliser skill claude the of to and in for
when use user this that with or it is be as an
""".split())


def parse_frontmatter(text):
    """Retourne (dict des clés de premier niveau, corps). Parseur volontairement
    simple : on ne lit que des clés de premier niveau, ce qui suffit ici."""
    if not text.startswith("---"):
        return None, text
    end = re.search(r"^---\s*$", text[3:], re.M)
    if not end:
        return None, text
    raw = text[3:3 + end.start()]
    body = text[3 + end.end():]

    fm, key, buf = {}, None, []
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m and not line[0].isspace():
            if key:
                fm[key] = "\n".join(buf).strip() if buf else fm.get(key, "")
            key, val = m.group(1), m.group(2).strip()
            if val in (">", "|", ">-", "|-", ">+", "|+"):
                fm[key], buf = "", []
            else:
                fm[key], buf, key = val, [], None
        elif key is not None:
            buf.append(line.strip())
    if key:
        fm[key] = "\n".join(buf).strip()
    return fm, body


def words(text):
    return {w for w in re.findall(r"[a-zà-ÿ]{3,}", text.lower()) if w not in STOP}


ROOT = Path(__file__).resolve().parent.parent


def check(path, report):
    err = lambda m: report.append(("ERREUR", path, m))
    warn = lambda m: report.append(("ALERTE", path, m))

    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        err("pas de frontmatter YAML délimité par ---")
        return None

    for k in set(fm) - KNOWN_KEYS:
        warn(f"champ inconnu dans le frontmatter : '{k}' (faute de frappe ?)")

    name = fm.get("name", "").strip()
    folder = path.parent.name
    if name and name != folder:
        err(f"name '{name}' ≠ nom du dossier '{folder}'")

    desc = fm.get("description", "").strip()
    combined = desc + " " + fm.get("when_to_use", "")
    if not desc:
        err("pas de description — le skill ne se déclenchera quasiment jamais")
    else:
        if len(combined) > DESC_CHAR_CAP:
            err(f"description + when_to_use = {len(combined)} car. "
                f"(plafond {DESC_CHAR_CAP})")
        if len(desc) < 60:
            warn(f"description très courte ({len(desc)} car.) : dit-elle QUAND "
                 "s'en servir, avec des phrases réelles ?")
        low = combined.lower()
        # Un skill en invocation manuelle seule n'est jamais choisi sur sa
        # description : lui réclamer un vocabulaire de déclenchement et des
        # exclusions croisées n'a pas de sens.
        manuel = str(fm.get("disable-model-invocation", "")).lower() == "true"
        if manuel:
            pass
        elif not any(t in low for t in ("quand", "dès que", "when", "use this",
                                      "utilise ce", "lorsque", "utiliser pour",
                                      "à utiliser", "use for", "trigger")):
            warn("la description ne dit pas QUAND déclencher "
                 "(« Utilise ce skill quand… »)")
        if not manuel and not any(t in low for t in ("n'utilise pas",
                                      "ne pas utiliser", "do not use",
                                      "plutôt", "voir ")):
            warn("la description ne dit pas quand NE PAS s'en servir — "
                 "source n°1 de chevauchement entre skills")

    # `python3` n'existe pas sur une machine Windows par défaut : c'est un alias
    # vers le Microsoft Store, qui ouvre une boutique et n'exécute rien. Le skill
    # ne voit pas d'erreur, l'utilisateur non plus — la commande est simplement
    # sans effet. Ça a muté la capture du journal pendant toute sa première vie.
    # Un skill qui appelle python3 doit donc dire quoi faire à la place, et son
    # allowed-tools doit permettre de le faire.
    if "python3" in body:
        if "`py`" not in body:
            err("appelle `python3` sans donner le repli `py` — sous Windows "
                "python3 est un alias Microsoft Store : la commande n'exécute "
                "rien, en silence")
        outils = fm.get("allowed-tools", "")
        if "python3" in outils and "py " not in outils.replace("python3 ", ""):
            err("allowed-tools autorise `python3` mais pas `py` : sous Windows "
                "le repli est interdit avant d'être tenté")

    nlines = len(body.strip().splitlines())
    if nlines > BODY_LINE_CAP:
        warn(f"corps de {nlines} lignes (> {BODY_LINE_CAP}) : "
             "déplace le détail dans references/")

    low_body = body.lower()
    if "## format" not in low_body and "format de sortie" not in low_body:
        warn("pas de section « Format de sortie » : principale cause de dérive")
    if "exemple" not in low_body and "example" not in low_body:
        warn("aucun exemple entrée → sortie")

    # Renvois vers des fichiers absents. Un chemin peut être relatif au skill
    # (references/), au plugin (${CLAUDE_PLUGIN_ROOT}/scripts/) ou au repo.
    bases = [path.parent, ROOT]
    for parent in path.parents:
        if (parent / ".claude-plugin").is_dir():
            bases.append(parent)
            break
    # Le motif prend le chemin entier (pas juste sa fin) pour ne pas confondre
    # « references/x.md » avec « skills/code/references/x.md ».
    motif = (r"(?<![\w/])(?:\$\{[A-Z_]+\}/)?(?:[\w.-]+/)*"
             r"(?:references|scripts|assets)/[\w./-]+")
    for ref in sorted(set(re.findall(motif, body))):
        rel = re.sub(r"^\$\{[A-Z_]+\}/", "", ref)
        if not any((base / rel).exists() for base in bases):
            err(f"renvoi vers un fichier absent : {ref}")

    for ref in (path.parent / "references").glob("*.md"):
        rl = ref.read_text(encoding="utf-8").splitlines()
        if len(rl) > REF_TOC_LINES and not any(
            h in "\n".join(rl[:40]).lower()
            for h in ("## sommaire", "## table", "## contents")
        ):
            warn(f"{ref.name} fait {len(rl)} lignes sans table des matières")

    return (folder, words(combined)) if desc else None


def evals_documentes(report):
    """Chaque cas d'éval présent sur le disque doit figurer dans son README.

    Un README qui annonce sept cas quand il y en a dix ne casse rien — il
    désinforme, ce qui est pire : on croit mesurer plus qu'on ne mesure.
    """
    for readme in ROOT.glob("plugins/*/evals/README.md"):
        texte = readme.read_text(encoding="utf-8")
        # Le README porte aussi le protocole manuel, qui est la seule façon de
        # mesurer tant que `claude plugin eval` est en accès anticipé. Sa table
        # avait déjà pris un cas de retard, en silence : un protocole qui
        # annonce couvrir la suite et en oublie un tiers ne mesure pas ce qu'on
        # croit. Le prompt doit y figurer tel quel — reformulé, il teste autre
        # chose que le cas.
        aplati = " ".join(texte.split())
        for cas in sorted(d for d in readme.parent.iterdir() if d.is_dir()):
            if f"`{cas.name}`" not in texte:
                report.append(("ERREUR", readme,
                               f"le cas d'éval « {cas.name} » n'est documenté nulle part"))
            prompt = cas / "prompt.md"
            if not prompt.exists():
                report.append(("ERREUR", cas, "cas d'éval sans prompt.md"))
                continue
            brut = prompt.read_text(encoding="utf-8")
            corps = re.split(r"^---\s*$", brut, maxsplit=2, flags=re.M)[-1]
            phrase = " ".join(corps.split())
            if phrase and phrase not in aplati:
                report.append(("ERREUR", readme,
                               f"le prompt du cas « {cas.name} » ne figure pas dans le "
                               "protocole manuel"))


NOMBRES = {"un": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6,
           "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12,
           "treize": 13, "quatorze": 14, "quinze": 15, "seize": 16, "vingt": 20}


def _nombre(mot):
    return int(mot) if mot.isdigit() else NOMBRES.get(mot.lower())


def routage_mesure(report):
    """Depuis quand le routage n'a-t-il pas été remesuré ?

    Emprunté à la bannière de péremption de `codegraph` : quand l'index peut
    être en retard, la réponse le dit en tête plutôt que de servir de vieilles
    données avec aplomb. Ici l'« index », c'est la mesure du déclenchement. Sans
    cette trace, « le routage n'est pas mesuré » dépendait de la mémoire de
    celui qui parle.

    Alerte, pas erreur : un correctif ponctuel ne justifie pas de rejouer
    trente-trois prompts. C'est un rappel, pas un barrage.
    """
    for resultats in ROOT.glob("plugins/*/evals/RESULTATS.md"):
        manifeste = resultats.parent.parent / ".claude-plugin" / "plugin.json"
        if not manifeste.exists():
            continue
        import json
        try:
            courante = json.loads(manifeste.read_text(encoding="utf-8")).get("version")
        except json.JSONDecodeError:
            continue
        texte = resultats.read_text(encoding="utf-8")
        # Seule la table d'en-tête compte : tout ce qui suit le premier titre de
        # section est du mode d'emploi, exemples compris. Les lire comme des
        # campagnes ferait passer un exemple pour une mesure.
        entete = texte.split("\n## ", 1)[0]
        versions = [v for v in re.findall(r"^\|\s*(\d+\.\d+\.\d+)\s*\|", entete, re.M)]
        if not versions:
            report.append(("ALERTE", resultats,
                           "le routage n'a jamais été mesuré entièrement — "
                           "protocole dans evals/README.md"))
            continue
        derniere = max(versions, key=lambda v: [int(x) for x in v.split(".")])
        a = [int(x) for x in derniere.split(".")]
        b = [int(x) for x in str(courante).split(".")[:3]]
        if a[:2] != b[:2]:
            report.append(("ALERTE", resultats,
                           f"routage mesuré pour la dernière fois en {derniere}, "
                           f"le plugin est en {courante}"))


def comptes_annonces(report):
    """Le README racine annonce des nombres d'évals. Ils vieillissent seuls.

    Il annonçait sept évals pour onze, et quatre cas de frontière pour cinq —
    les deux chiffres dataient d'avant la moitié de la suite. Un README qui
    sous-annonce ce qui est mesuré fait croire à une couverture plus faible
    qu'elle n'est, et personne ne relit un chiffre en passant.
    """
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    texte = readme.read_text(encoding="utf-8")
    cas = sorted(d for d in (ROOT / "plugins/roblox/evals").glob("*") if d.is_dir())
    reels = {
        r"([\wéè]+) évals": len(cas),
        r"([\wéè]+) cas de frontière": sum(
            1 for d in cas if list((d / "graders").glob("pas-*.md"))),
    }
    for motif, reel in reels.items():
        for mot in set(re.findall(motif, texte)):
            n = _nombre(mot)
            if n is not None and n != reel:
                report.append(("ERREUR", readme,
                               f"annonce « {mot} » là où il y en a {reel} "
                               f"({motif.split(' ', 1)[1]})"))


def guide_a_jour(report):
    """Le guide annonce une version et un nombre de skills. Les deux dérivent.

    CLAUDE.md exige que le numéro en tête du guide corresponde à plugin.json.
    Rien ne le vérifiait, et il avait déjà décroché. Un guide qui annonce la
    mauvaise version n'est pas une coquille : c'est la seule page que
    l'utilisateur lit pour savoir ce qu'il a reçu.
    """
    import json
    for manifeste in ROOT.glob("plugins/*/.claude-plugin/plugin.json"):
        racine = manifeste.parent.parent
        guide = racine / "GUIDE.md"
        if not guide.exists():
            continue
        try:
            version = json.loads(manifeste.read_text(encoding="utf-8")).get("version")
        except json.JSONDecodeError:
            report.append(("ERREUR", manifeste, "JSON illisible"))
            continue
        texte = guide.read_text(encoding="utf-8")
        entete = "\n".join(texte.splitlines()[:10])
        if version and version not in entete:
            report.append(("ERREUR", guide,
                           f"l'en-tête n'annonce pas la version {version} du manifeste "
                           "— voir la règle permanente dans CLAUDE.md"))
        reel = len(list((racine / "skills").glob("*/SKILL.md")))
        for annonce in set(re.findall(r"(\d+)\s+skills", texte)):
            if int(annonce) != reel:
                report.append(("ERREUR", guide,
                               f"le guide annonce {annonce} skills, il y en a {reel}"))


def main():
    targets = [Path(a) for a in sys.argv[1:]] or [ROOT]
    files = sorted({
        p for t in targets
        for p in ([t] if t.name == "SKILL.md" else t.rglob("SKILL.md"))
        if ".git" not in p.parts and "templates" not in p.parts
    })

    if not files:
        print("Aucun SKILL.md trouvé. Rien à valider.")
        return 0

    report, descs = [], []
    evals_documentes(report)
    guide_a_jour(report)
    comptes_annonces(report)
    routage_mesure(report)
    for f in files:
        got = check(f, report)
        if got:
            descs.append((got[0], got[1], f))

    # Chevauchement : similarité de Jaccard entre vocabulaires de déclenchement.
    for i in range(len(descs)):
        for j in range(i + 1, len(descs)):
            (na, wa, fa), (nb, wb, _) = descs[i], descs[j]
            if not wa or not wb:
                continue
            score = len(wa & wb) / len(wa | wb)
            if score >= OVERLAP_WARN:
                shared = ", ".join(sorted(wa & wb)[:8])
                report.append(("ALERTE", fa,
                               f"description proche de '{nb}' "
                               f"({score:.0%} de vocabulaire commun : {shared}) "
                               "— ajoute une exclusion croisée"))

    cwd = Path.cwd()
    for level, path, msg in report:
        try:
            shown = path.relative_to(cwd)
        except ValueError:
            shown = path
        print(f"{level:7} {shown}: {msg}")

    errors = sum(1 for l, _, _ in report if l == "ERREUR")
    warns = len(report) - errors
    print(f"\n{len(files)} skill(s) — {errors} erreur(s), {warns} alerte(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
