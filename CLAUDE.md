# Conventions du repo HatSkills

## Règle permanente : le guide suit les grosses mises à jour

À **chaque changement de version mineure ou majeure** du plugin
(`0.2.x` → `0.3.0`, `0.x` → `1.0`), mettre à jour dans le même commit :

- `plugins/roblox/GUIDE.md` — le guide rapide destiné à l'utilisateur. Il vit **dans** le plugin, pour être livré avec lui et servir de source à `/roblox:help`. Court, scannable,
  sans jargon. Il doit répondre à « c'est quoi, ça fait quoi, comment je m'en
  sers, que faire quand ça rate ». Le numéro de version en tête doit
  correspondre à `plugin.json`.
- `CHANGELOG.md` — ce qui change, et pourquoi c'est utile.

`scripts/check_version.py` le vérifie et fait échouer la CI si l'un des deux
manque. Un correctif ponctuel (`0.2.0` → `0.2.1`) n'est pas concerné.

## Écrire un skill

La méthode est dans `docs/`. En résumé :

- La `description` est le seul texte vu avant le déclenchement. Tout le
  « quand » y va, y compris le **quand ne pas** — avec le nom du skill voisin.
- Un gabarit de sortie exact, pas une description en prose.
- Ce qui a été précisé deux fois à la main appartient au `Contexte figé`.
- Section `Apprendre de la session` obligatoire : sans elle, le skill ne
  remonte rien à `/roblox:affiner`.

## Avant de committer

```bash
python3 scripts/validate.py        # 0 erreur ET 0 alerte
python3 scripts/check_version.py   # version bumpée si le plugin a changé
```

## Ce qu'on ne fait pas

- Ajouter une règle à un skill sans en retirer une autre quand il grossit :
  chaque ligne est rechargée à **chaque** déclenchement.
- Promouvoir une leçon vue une seule fois. Un incident n'est pas une règle.
- Corriger un problème de déclenchement dans le corps d'un skill. Si le skill
  ne s'est pas déclenché, son corps n'a jamais été lu.
