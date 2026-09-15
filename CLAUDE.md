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

## La doctrine d'exclusion — et ses limites

Une `description` dit quand déclencher **et quand ne pas**. C'est la partie
« quand ne pas » qui empêche deux skills de se disputer une demande.

Mais une exclusion n'est pas gratuite : elle est payée **à chaque tour**, même
quand aucun skill ne part. Et elle a un effet pervers mesurable — nommer son
voisin, c'est importer son vocabulaire, donc **se rapprocher** de lui aux yeux
du détecteur de recouvrement.

### Quand une exclusion se justifie

Une seule condition, et elle est empirique : **une phrase réellement prononcée
par l'utilisateur pourrait raisonnablement partir chez les deux.**

« Quand on frappe, il ne se passe rien » peut aller chez `vfx` comme chez
`anim`. Ça, c'est une exclusion fondée. « Écris un RemoteEvent » ne risque pas
de partir chez `atelier` : l'exclusion serait du rituel.

### La symétrie n'est pas une règle

On a longtemps tenu que l'exclusion devait aller **dans les deux sens**. C'est
probablement faux, et ça n'a jamais été mesuré :

- Le modèle voit **toutes** les descriptions en même temps quand il route. Il
  ne lit pas A, décide, puis lit B. Si A dit « pas moi, plutôt B »,
  l'information est déjà là — que B le dise aussi n'ajoute rien de nouveau.
- La confusion est souvent **à sens unique**. Celui qui risque de prendre le
  travail de l'autre doit le dire ; l'inverse n'a pas de raison d'exister.
- Rendre symétriques les quinze asymétries actuelles coûterait quelques
  centaines de tokens permanents pour un bénéfice que personne n'a constaté.

Donc : **on ajoute une exclusion quand on a vu l'ambiguïté, pas pour équilibrer
un tableau.** Les asymétries restantes sont assumées jusqu'à ce qu'une campagne
d'évals montre qu'elles coûtent un mauvais routage — c'est elle qui tranche,
pas le raisonnement.

## Avant de committer

```bash
python3 scripts/test_scripts.py    # les scripts eux-mêmes
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
  chaque ligne est rechargée à **chaque** déclenchement. Cette règle n'est plus
  tenue à l'honneur — elle a été enfreinte deux fois par celui qui l'avait
  écrite. `budget.json` fixe un plafond par skill et `validate.py` échoue au
  dépassement. Relever un plafond reste permis : ça se voit dans le diff, et ça
  se justifie dans le `CHANGELOG`. C'est tout l'intérêt.
- Promouvoir une leçon vue une seule fois. Un incident n'est pas une règle.
- Corriger un problème de déclenchement dans le corps d'un skill. Si le skill
  ne s'est pas déclenché, son corps n'a jamais été lu.
