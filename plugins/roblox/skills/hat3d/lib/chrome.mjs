// lib/chrome.mjs — détection d'un Chromium headless (Chrome ou Edge), partagée
// par les scripts qui pilotent un navigateur (shots.mjs, palette.mjs).
//
// N'importe quel Chromium fait l'affaire en mode headless (même moteur de
// rendu, mêmes flags) : Chrome d'abord par préférence, Edge en repli — sur
// beaucoup de machines Windows c'est le seul des deux présent de base.
import { existsSync } from "node:fs";

export function findChrome() {
  if (process.env.HAT3D_CHROME_PATH && existsSync(process.env.HAT3D_CHROME_PATH)) {
    return process.env.HAT3D_CHROME_PATH;
  }
  return [
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/microsoft-edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  ].find(existsSync);
}
