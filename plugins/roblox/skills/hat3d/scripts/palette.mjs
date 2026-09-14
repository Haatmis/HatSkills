#!/usr/bin/env node
// palette.mjs — extrait les couleurs dominantes d'une image de référence, pour
// éviter de deviner les `color` d'un générateur à l'œil.
//
//   node .claude/skills/hat3d/scripts/palette.mjs hat3d/coffre/reference.png
//   node .claude/skills/hat3d/scripts/palette.mjs reference.png --n 8
//
// Aucun décodeur d'image maison : on fait décoder l'image par le Chromium
// headless déjà requis par shots.mjs (via <canvas>, qui gère PNG/JPEG/WebP
// nativement), on y fait tourner un k-means sur les pixels, et on récupère
// le résultat en dumpant le DOM après calcul — même famille de solution que
// shots.mjs, pour ne pas ajouter de dépendance npm à un skill qui n'en a
// aucune.
import { existsSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { join, resolve, basename } from "node:path";
import { tmpdir } from "node:os";
import { pathToFileURL } from "node:url";
import { execFileSync } from "node:child_process";
import { findChrome } from "../lib/chrome.mjs";

const argv = process.argv.slice(2);
const imgArg = argv.find((a) => !a.startsWith("--"));
const val = (n, d) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : d; };
if (!imgArg) {
  console.error("Usage : node palette.mjs <image.png|jpg|webp> [--n 6] [--out palette.json] [--taille 96]");
  process.exit(1);
}
const imgPath = resolve(imgArg);
if (!existsSync(imgPath)) { console.error("Introuvable : " + imgPath); process.exit(1); }

const N = parseInt(val("n", "6"), 10);
const TAILLE = parseInt(val("taille", "96"), 10);
// Par défaut dans le dossier courant (pas à côté de la source) : l'image de
// référence peut vivre n'importe où (bibliothèque d'assets d'une app, dossier
// de téléchargements) et n'est pas un dossier qu'un script Hat3D doit écrire.
const outPath = resolve(val("out", "palette.json"));

const CHROME = findChrome();
if (!CHROME) {
  console.error("Chrome/Edge introuvable. Installe l'un des deux, ou fixe HAT3D_CHROME_PATH=<chemin-exe>.");
  process.exit(1);
}

// Page one-shot : décode l'image dans un canvas réduit à TAILLE×TAILLE
// (échantillonnage suffisant pour des teintes dominantes, rapide même sur une
// photo haute résolution), k-means déterministe (centroïdes de départ répartis
// régulièrement dans l'échantillon — pas de Math.random, un même run redonne
// le même résultat), résultat écrit dans #out puis récupéré via --dump-dom.
// L'image est une balise <img> du markup initial (pas un \`new Image()\`
// détaché) : seule une ressource découverte au parsing (ou explicitement
// posée avant l'évènement \`load\`) fait attendre \`--dump-dom\`. Un \`new
// Image()\` créé depuis le script ne bloque jamais \`load\` — piégé une fois,
// la palette sortait vide à chaque coup avant ce correctif.
const html = `<!DOCTYPE html><html><body>
<img id="src" src="${pathToFileURL(imgPath).href}" style="display:none" alt="">
<canvas id="c" width="${TAILLE}" height="${TAILLE}"></canvas>
<pre id="out">en_attente</pre>
<script>
const K = ${N}, TAILLE = ${TAILLE};
const img = document.getElementById("src");
const run = () => {
  const ctx = document.getElementById("c").getContext("2d");
  ctx.drawImage(img, 0, 0, TAILLE, TAILLE);
  const { data } = ctx.getImageData(0, 0, TAILLE, TAILLE);
  const pixels = [];
  for (let i = 0; i < data.length; i += 4) {
    if (data[i + 3] < 16) continue; // pixel quasi transparent : ignoré
    pixels.push([data[i], data[i + 1], data[i + 2]]);
  }
  if (pixels.length < K) { document.getElementById("out").textContent = "ERREUR_TROP_PETIT"; return; }

  // coins moyens = fond probable (convention Hat3D : référence sur fond neutre uni)
  const corners = [0, TAILLE - 1].flatMap((y) => [0, TAILLE - 1].map((x) => {
    const idx = (y * TAILLE + x) * 4;
    return [data[idx], data[idx + 1], data[idx + 2]];
  }));
  const bg = corners.reduce((a, p) => [a[0] + p[0] / 4, a[1] + p[1] / 4, a[2] + p[2] / 4], [0, 0, 0]);

  let centroids = Array.from({ length: K }, (_, i) => pixels[Math.floor((i + 0.5) * pixels.length / K)]);
  const dist2 = (a, b) => (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2;
  let assign = new Array(pixels.length).fill(0);
  for (let iter = 0; iter < 10; iter++) {
    for (let p = 0; p < pixels.length; p++) {
      let best = 0, bd = Infinity;
      for (let k = 0; k < K; k++) {
        const d = dist2(pixels[p], centroids[k]);
        if (d < bd) { bd = d; best = k; }
      }
      assign[p] = best;
    }
    const sums = Array.from({ length: K }, () => [0, 0, 0, 0]);
    for (let p = 0; p < pixels.length; p++) {
      const s = sums[assign[p]], px = pixels[p];
      s[0] += px[0]; s[1] += px[1]; s[2] += px[2]; s[3]++;
    }
    centroids = sums.map((s, k) => (s[3] ? [s[0]/s[3], s[1]/s[3], s[2]/s[3]] : centroids[k]));
  }
  const counts = new Array(K).fill(0);
  for (const a of assign) counts[a]++;
  const toHex = (v) => Math.round(v).toString(16).padStart(2, "0");
  const clusters = centroids
    .map((c, k) => ({
      rgb: c.map(Math.round),
      hex: "#" + c.map(toHex).join(""),
      weight: Math.round((counts[k] / pixels.length) * 1000) / 1000,
      background: Math.sqrt(dist2(c, bg)) < 18,
    }))
    .sort((a, b) => b.weight - a.weight);
  document.getElementById("out").textContent = JSON.stringify(clusters);
};
img.onerror = () => { document.getElementById("out").textContent = "ERREUR_CHARGEMENT"; };
if (img.complete && img.naturalWidth > 0) run(); else img.onload = run;
</script>
</body></html>`;

const tmpDir = mkdtempSync(join(tmpdir(), "hat3d-palette-"));
const tmpHtml = join(tmpDir, "index.html");
writeFileSync(tmpHtml, html);

let dom;
try {
  dom = execFileSync(CHROME, [
    "--headless=new", "--disable-gpu", "--no-first-run",
    "--disable-background-networking", "--disable-sync", "--disable-extensions",
    // Sans ce flag, charger l'image de référence en file:// dans le <canvas>
    // « tainte » le canvas (origine opaque) et getImageData lève une
    // SecurityError — silencieuse en headless, la palette sortait vide à
    // chaque essai tant que ce n'était pas identifié.
    "--allow-file-access-from-files",
    "--user-data-dir=" + join(tmpDir, "profile"),
    "--dump-dom", pathToFileURL(tmpHtml).href,
  ], { encoding: "utf8" });
} catch (e) {
  console.error("Échec du rendu : " + e.message);
  process.exit(1);
} finally {
  try { rmSync(tmpDir, { recursive: true, force: true }); } catch { /* best effort */ }
}

const m = /<pre id="out">([\s\S]*?)<\/pre>/.exec(dom);
const raw = m ? m[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">") : null;
if (!raw || raw === "en_attente") {
  console.error("Échec : la page n'a pas fini de calculer la palette (Chrome trop lent, ou --dump-dom a coupé trop tôt).");
  process.exit(1);
}
if (raw === "ERREUR_CHARGEMENT") { console.error("Chrome n'a pas pu charger l'image : " + imgPath); process.exit(1); }
if (raw === "ERREUR_TROP_PETIT") { console.error("Image trop petite ou trop transparente pour " + N + " couleurs."); process.exit(1); }

let clusters;
try { clusters = JSON.parse(raw); }
catch { console.error("Sortie inattendue de la page de calcul : " + raw.slice(0, 200)); process.exit(1); }

writeFileSync(outPath, JSON.stringify(clusters, null, 2));
console.log("Palette de " + basename(imgPath) + " (" + clusters.length + " couleurs) :\n");
for (const c of clusters) {
  const pct = (c.weight * 100).toFixed(0).padStart(3) + "%";
  console.log("  " + c.hex + "   rgb(" + c.rgb.join(", ") + ")   " + pct + (c.background ? "   ← probablement le fond" : ""));
}
console.log("\n→ " + outPath);
