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
  remonte rien à `/roblox:atelier`.

## Avant de committer

```bash
python3 scripts/validate.py        # 0 erreur, et chaque alerte réglée ou assumée
python3 scripts/check_version.py   # version bumpée si le plugin a changé
```

Zéro erreur, toujours. Les alertes se règlent, sauf une qu'on assume : tant
qu'aucune campagne d'évals n'est enregistrée dans `plugins/roblox/evals/RESULTATS.md`,
le validateur rappelle que le routage n'est pas mesuré. Elle ne se tait qu'en
jouant les onze prompts, trois fois chacun. C'est voulu — une alerte qu'on fait
taire autrement redevient invisible.

## Le journal des versions dit aussi ce qui n'a pas avancé

Une entrée de `CHANGELOG.md` qui ne raconte que des victoires n'est pas un
journal, c'est une affiche. Chaque entrée dit ce qui a reculé, ce qui a grossi
alors qu'il devait maigrir, ou ce qui n'a pas pu être vérifié. C'est ce qui
rend le reste croyable — et c'est ce qui permet de retrouver la dette six mois
plus tard, quand plus personne ne s'en souvient.

## Ce qu'on ne fait pas

- Ajouter une règle à un skill sans en retirer une autre quand il grossit :
  chaque ligne est rechargée à **chaque** déclenchement.
- Promouvoir une leçon vue une seule fois. Un incident n'est pas une règle.
- Corriger un problème de déclenchement dans le corps d'un skill. Si le skill
  ne s'est pas déclenché, son corps n'a jamais été lu.
