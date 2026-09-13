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
        if not any(t in low for t in ("quand", "dès que", "when", "use this",
                                      "utilise ce", "lorsque")):
            warn("la description ne dit pas QUAND déclencher "
                 "(« Utilise ce skill quand… »)")
        if not any(t in low for t in ("n'utilise pas", "ne pas utiliser",
                                      "do not use", "plutôt", "voir ")):
            warn("la description ne dit pas quand NE PAS s'en servir — "
                 "source n°1 de chevauchement entre skills")

    nlines = len(body.strip().splitlines())
    if nlines > BODY_LINE_CAP:
        warn(f"corps de {nlines} lignes (> {BODY_LINE_CAP}) : "
             "déplace le détail dans references/")

    low_body = body.lower()
    if "## format" not in low_body and "format de sortie" not in low_body:
        warn("pas de section « Format de sortie » : principale cause de dérive")
    if "exemple" not in low_body and "example" not in low_body:
        warn("aucun exemple entrée → sortie")

    # Renvois vers des fichiers absents (résolus depuis le skill ou la racine).
    for ref in sorted(set(re.findall(r"(?:references|scripts|assets)/[\w./-]+",
                                     body))):
        if not any((base / ref).exists() for base in (path.parent, ROOT)):
            err(f"renvoi vers un fichier absent : {ref}")

    for ref in (path.parent / "references").glob("*.md"):
        rl = ref.read_text(encoding="utf-8").splitlines()
        if len(rl) > REF_TOC_LINES and not any(
            h in "\n".join(rl[:40]).lower()
            for h in ("## sommaire", "## table", "## contents")
        ):
            warn(f"{ref.name} fait {len(rl)} lignes sans table des matières")

    return (folder, words(combined)) if desc else None


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
