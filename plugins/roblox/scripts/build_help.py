#!/usr/bin/env python3
"""Génère la page d'aide HTML à partir de GUIDE.md.

Elle est produite à l'invocation, jamais commitée : une page d'aide écrite à
la main diverge du guide dès la première mise à jour, et une page périmée est
pire que pas de page — elle affirme des choses fausses avec assurance.

    python3 build_help.py <GUIDE.md> [-o sortie.html]

Le convertisseur ne gère que ce que GUIDE.md utilise réellement : titres,
tableaux, blocs de code, citations, listes, gras, code inline, liens. Tout le
reste passe en paragraphe — pas de silence, pas de balise cassée.
"""

import argparse
import html
import re
import sys
import tempfile
from pathlib import Path

# Windows : la console est en cp1252 par défaut, et les flèches ou accents de
# ce script la font lever UnicodeEncodeError — donc planter APRÈS avoir fait
# son travail. Un script qui échoue une fois qu'il a réussi apprend à ignorer
# son verdict, ce qui est pire que pas de script du tout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


CSS = """
:root{--bg:#fbfaf8;--fg:#23201d;--mut:#6b645c;--line:#e5e0d8;--card:#fff;
--acc:#b4512a;--code-bg:#f3f0eb}
@media(prefers-color-scheme:dark){:root{--bg:#17161a;--fg:#e8e5e0;--mut:#9a938a;
--line:#2e2b30;--card:#1e1d22;--acc:#e08a5f;--code-bg:#24222a}}
*{box-sizing:border-box}
body{margin:0;padding:0;background:var(--bg);color:var(--fg);
font:16px/1.65 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:860px;margin:0 auto;padding:48px 20px 96px}
h1{font-size:1.9rem;line-height:1.2;margin:0 0 4px;letter-spacing:-.02em}
h2{font-size:1.3rem;margin:2.4em 0 .6em;padding-top:.8em;
border-top:1px solid var(--line);letter-spacing:-.01em}
h3{font-size:1.05rem;margin:1.8em 0 .4em;color:var(--mut)}
p{margin:.8em 0}
a{color:var(--acc)}
code{background:var(--code-bg);padding:.12em .38em;border-radius:4px;
font:.88em/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:14px 16px;overflow-x:auto;margin:1em 0}
pre code{background:none;padding:0;font-size:.85rem;line-height:1.55}
table{border-collapse:collapse;width:100%;margin:1.1em 0;font-size:.93rem;
display:block;overflow-x:auto}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);
vertical-align:top}
th{font-weight:600;font-size:.8rem;text-transform:uppercase;
letter-spacing:.05em;color:var(--mut)}
tr:last-child td{border-bottom:none}
blockquote{margin:1.2em 0;padding:12px 16px;background:var(--card);
border-left:3px solid var(--acc);border-radius:0 8px 8px 0}
blockquote p{margin:.3em 0}
ul{padding-left:1.3em}li{margin:.35em 0}
.sub{color:var(--mut);font-size:.9rem;margin:0 0 8px}
.toc{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:14px 18px;margin:28px 0 8px}
.toc-t{font-size:.75rem;text-transform:uppercase;letter-spacing:.07em;
color:var(--mut);margin-bottom:8px}
.toc a{display:block;padding:3px 0;text-decoration:none}
.toc a:hover{text-decoration:underline}
@media print{body{background:#fff}.toc{display:none}h2{page-break-after:avoid}}
"""


def enligne(t):
    """Gras, code inline et liens. Le code est protégé en premier pour qu'un
    `**` à l'intérieur d'un backtick ne soit pas pris pour du gras."""
    jetons = []

    def garde(m):
        jetons.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(jetons) - 1}\x00"

    t = re.sub(r"`([^`]+)`", garde, t)
    t = html.escape(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: jetons[int(m.group(1))], t)


def ancre(t):
    t = re.sub(r"[`*]", "", t).lower()
    return re.sub(r"[^\w]+", "-", t.strip()).strip("-")


def convertir(md):
    lignes = md.split("\n")
    out, toc, i = [], [], 0

    while i < len(lignes):
        l = lignes[i]

        if l.startswith("```"):                                   # bloc de code
            i += 1
            buf = []
            while i < len(lignes) and not lignes[i].startswith("```"):
                buf.append(lignes[i]); i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")

        elif l.startswith("|"):                                   # tableau
            bloc = []
            while i < len(lignes) and lignes[i].startswith("|"):
                bloc.append(lignes[i]); i += 1
            i -= 1
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            corps = bloc[2:] if len(bloc) > 1 and set(bloc[1]) <= set("|-: ") else bloc[1:]
            out.append("<table><thead><tr>"
                       + "".join(f"<th>{enligne(c)}</th>" for c in cells(bloc[0]))
                       + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{enligne(c)}</td>"
                                                  for c in cells(r)) + "</tr>"
                                 for r in corps)
                       + "</tbody></table>")

        elif m := re.match(r"^(#{1,3}) (.+)$", l):                # titre
            n, txt = len(m.group(1)), m.group(2)
            a = ancre(txt)
            if n == 2:
                toc.append((a, re.sub(r"[`*]", "", txt)))
            out.append(f'<h{n} id="{a}">{enligne(txt)}</h{n}>')

        elif l.startswith(">"):                                   # citation
            buf = []
            while i < len(lignes) and lignes[i].startswith(">"):
                buf.append(lignes[i].lstrip("> ").rstrip()); i += 1
            i -= 1
            out.append("<blockquote><p>" + enligne(" ".join(buf)) + "</p></blockquote>")

        elif re.match(r"^[-*] ", l):                              # liste
            buf = []
            while i < len(lignes) and (re.match(r"^[-*] ", lignes[i])
                                       or (buf and lignes[i].startswith("  "))):
                if re.match(r"^[-*] ", lignes[i]):
                    buf.append(lignes[i][2:])
                else:
                    buf[-1] += " " + lignes[i].strip()
                i += 1
            i -= 1
            out.append("<ul>" + "".join(f"<li>{enligne(x)}</li>" for x in buf) + "</ul>")

        elif l.strip() and not l.startswith("---"):               # paragraphe
            buf = []
            while i < len(lignes) and lignes[i].strip() and not re.match(
                    r"^(\||#{1,3} |```|>|[-*] |---)", lignes[i]):
                buf.append(lignes[i].strip()); i += 1
            i -= 1
            out.append("<p>" + enligne(" ".join(buf)) + "</p>")

        i += 1
    return "\n".join(out), toc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guide")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    src = Path(a.guide)
    if not src.exists():
        print(f"Introuvable : {src}", file=sys.stderr)
        return 1
    md = src.read_text(encoding="utf-8")

    titre = next((l[2:] for l in md.split("\n") if l.startswith("# ")), "Aide")
    version = (re.search(r"[Vv]ersion \*\*([\d.]+)\*\*", md) or [None, "?"])[1]
    corps, toc = convertir(md)
    nav = ("<nav class='toc'><div class='toc-t'>Sommaire</div>"
           + "".join(f"<a href='#{a_}'>{html.escape(t)}</a>" for a_, t in toc)
           + "</nav>")
    corps = corps.replace("</h1>", "</h1>", 1)

    page = (f"<!doctype html><html lang=fr><head><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(titre)}</title><style>{CSS}</style></head>"
            f"<body><div class=wrap>{corps}</div>"
            f"<script>document.querySelector('h1')?.insertAdjacentHTML("
            f"'afterend', {nav!r});</script></body></html>")

    out = Path(a.out) if a.out else Path(tempfile.gettempdir()) / "roblox-aide.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
