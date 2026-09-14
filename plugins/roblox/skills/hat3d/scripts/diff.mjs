#!/usr/bin/env node
// diff.mjs — comparaison visuelle de deux captures (avant/après une
// itération sur un générateur), pour repérer un changement non voulu ailleurs
// que sur la pièce qu'on vient de retoucher.
//
//   node .claude/skills/hat3d/scripts/diff.mjs hat3d/coffre-au-tresor
//     → compare shot-3q.png à shot-3q.prev.png (sauvegardé par shots.mjs à
//       chaque nouvelle capture, avant d'écraser l'ancienne)
//   node .claude/skills/hat3d/scripts/diff.mjs hat3d/coffre-au-tresor --vue face
//   node .claude/skills/hat3d/scripts/diff.mjs avant.png apres.png [--out diff.png]
//
// Pas de getImageData ni de décodage pixel : trois <img> affichées, la
// dernière en double avec `mix-blend-mode: difference` en CSS — c'est le
// compositeur du navigateur qui calcule la différence visuelle. Ça évite le
// piège du canvas "tainted" par une image file:// (voir palette.mjs) : on ne
// lit jamais les pixels depuis le script, on affiche seulement.
import { existsSync, readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { pathToFileURL } from "node:url";
import { execFileSync } from "node:child_process";
import { findChrome } from "../lib/chrome.mjs";

const argv = process.argv.slice(2);
const positional = argv.filter((a) => !a.startsWith("--"));
const val = (n, d) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : d; };
const vue = val("vue", "3q");

let avant, apres, defaultOut;
if (positional.length >= 2) {
  [avant, apres] = positional.map(resolve);
  defaultOut = "diff.png";
} else if (positional.length === 1) {
  const d = resolve(positional[0]);
  apres = join(d, `shot-${vue}.png`);
  avant = join(d, `shot-${vue}.prev.png`);
  defaultOut = join(d, `diff-${vue}.png`);
} else {
  console.error("Usage : node diff.mjs <dossier-modele> [--vue 3q|face|profil|dessous] [--out diff.png]\n"
    + "        node diff.mjs <avant.png> <apres.png> [--out diff.png]");
  process.exit(1);
}
for (const [label, p] of [["avant", avant], ["après", apres]]) {
  if (!existsSync(p)) {
    console.error(label + " introuvable : " + p
      + (label === "avant" && positional.length === 1
          ? " — il faut au moins deux passages de shots.mjs sur cette vue (le premier n'a rien à comparer)."
          : ""));
    process.exit(1);
  }
}

function pngSize(path) {
  const buf = readFileSync(path);
  if (buf.length < 24 || buf.readUInt32BE(0) !== 0x89504e47) return null;
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}
const sizeA = pngSize(avant), sizeB = pngSize(apres);
if (!sizeA || !sizeB) { console.error("Les deux fichiers doivent être des PNG (sortie de shots.mjs)."); process.exit(1); }
const W = Math.max(sizeA.width, sizeB.width), H = Math.max(sizeA.height, sizeB.height);

const outPath = resolve(val("out", defaultOut));

const CHROME = findChrome();
if (!CHROME) {
  console.error("Chrome/Edge introuvable. Installe l'un des deux, ou fixe HAT3D_CHROME_PATH=<chemin-exe>.");
  process.exit(1);
}

const urlA = pathToFileURL(avant).href, urlB = pathToFileURL(apres).href;
const PAD = 8, LABEL_H = 22;
const totalW = W * 3 + PAD * 4;
const totalH = H + LABEL_H + PAD * 2;

const panel = (label, inner) => `
  <div style="width:${W}px;">
    <div style="color:#9aa0a6;font:12px system-ui,sans-serif;margin-bottom:4px;">${label}</div>
    ${inner}
  </div>`;
const img = (url, extra = "") => `<img src="${url}" style="width:${W}px;height:${H}px;object-fit:contain;background:#000;display:block;${extra}">`;

const html = `<!DOCTYPE html><html><body style="margin:0;background:#1c1e22;">
<div style="display:flex;gap:${PAD}px;padding:${PAD}px;width:${totalW}px;box-sizing:border-box;">
  ${panel("avant", img(urlA))}
  ${panel("après", img(urlB))}
  ${panel("différence (noir = identique)", `
    <div style="position:relative;width:${W}px;height:${H}px;background:#000;">
      ${img(urlA, "position:absolute;inset:0;")}
      ${img(urlB, "position:absolute;inset:0;mix-blend-mode:difference;")}
    </div>`)}
</div>
</body></html>`;

const tmpDir = mkdtempSync(join(tmpdir(), "hat3d-diff-"));
const tmpHtml = join(tmpDir, "index.html");
writeFileSync(tmpHtml, html);
try {
  execFileSync(CHROME, [
    "--headless=new", "--disable-gpu", "--no-first-run",
    "--disable-background-networking", "--disable-sync", "--disable-extensions",
    "--user-data-dir=" + join(tmpDir, "profile"),
    "--window-size=" + Math.ceil(totalW) + "," + Math.ceil(totalH), "--hide-scrollbars",
    "--screenshot=" + outPath, pathToFileURL(tmpHtml).href,
  ], { stdio: "ignore" });
} catch (e) {
  console.error("Échec du rendu : " + e.message);
  process.exit(1);
} finally {
  try { rmSync(tmpDir, { recursive: true, force: true }); } catch { /* best effort */ }
}
if (!existsSync(outPath)) { console.error("Chrome n'a rien écrit."); process.exit(1); }
console.log("→ " + outPath);
