---
name: affiner
description: >
  Consolide le journal d'apprentissage dans les skills du plugin roblox :
  lit les leçons accumulées pendant l'usage réel, propose un diff pour chaque
  SKILL.md concerné, et marque les entrées traitées une fois validées.
  Utilise ce skill quand l'utilisateur dit « affine », « consolide »,
  « mets à jour les skills », « applique ce que tu as appris », « vide le
  journal », ou quand il donne suite au signalement « N leçons en attente ».
  N'utilise pas ce skill pour créer un skill qui n'existe pas encore (voir
  nouveau-skill), ni pour enregistrer une leçon au fil de l'eau — ça, c'est
  journal.py add, fait par le skill qui était actif à ce moment-là.
disable-model-invocation: false
---

# Affiner les skills à partir du journal

## Situation

Les skills accumulent des leçons pendant l'usage : corrections de
l'utilisateur, erreurs révélées par Studio, contexte qu'il a dû re-préciser.
Ce skill transforme ce tas en modifications ciblées.

Le piège est l'accumulation. Tout ce qui entre dans un SKILL.md est rechargé à
**chaque** déclenchement : une règle ajoutée coûte pour toujours. Un skill qui
grossit à chaque passage finit par se diluer et par produire de moins bons
résultats — l'inverse exact du but. Affiner, c'est donc autant retirer
qu'ajouter.

## Contexte figé

- **Le journal** : `${CLAUDE_PLUGIN_DATA}/journal.jsonl`, géré par
  `${CLAUDE_PLUGIN_ROOT}/scripts/journal.py`. Ne l'édite jamais à la main.
- **Les skills se modifient dans le repo HatSkills**, jamais dans le plugin
  installé : une mise à jour du plugin écraserait les changements. Si le repo
  n'est pas ouvert, produis le diff proposé et dis-le clairement plutôt que
  d'écrire dans l'installation.
- **Rien n'est écrit sans accord de l'utilisateur.** Tu proposes, il tranche.
- **Une leçon vue une seule fois n'entre pas dans un skill.** Un incident
  isolé n'est pas une règle. Le compteur `occurrences` est là pour ça.
- **Seuil de signalement** : 8 leçons en attente. En dessous, ne propose pas
  spontanément de consolider.

## Procédure

1. **Lis le journal** :
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" list`
   Les entrées sortent par récurrence décroissante.
2. **Trie en trois tas :**
   - **À promouvoir** — `occurrences ≥ 2`, ou une seule occurrence mais qui
     énonce une règle générale et vérifiable. Destination : le `Contexte figé`
     du skill concerné, ou sa section `Pièges` si la leçon s'explique mieux
     par un contre-exemple.
   - **À classer ailleurs** — une API dépréciée va dans la table du skill
     concerné (`skills/code/references/api-obsolete.md`), pas dans le corps. Une convention propre à
     un seul projet va dans le `CLAUDE.md` de ce projet, pas dans le skill :
     un skill est transversal.
   - **À écarter** — incident isolé, redite de ce qui est déjà écrit,
     préférence ponctuelle. Dis pourquoi tu écartes ; ne le tais pas.
3. **Cherche ce qui peut sortir.** Pour chaque skill touché, relis-le en
   entier et repère : les règles que plus rien ne justifie, celles qui sont
   dites deux fois, les exemples redondants, les précisions devenues
   évidentes. Une consolidation sans aucun retrait sur un skill déjà mûr est
   suspecte — signale-le si c'est le cas.
4. **Vérifie le déclenchement.** Si des leçons disent « le skill ne s'est pas
   déclenché » ou « le mauvais skill s'est déclenché », le remède est dans la
   `description`, pas dans le corps. Et si deux skills se disputent le même
   terrain, pose ou renforce l'exclusion croisée **dans les deux sens**.
5. **Propose le diff** au format ci-dessous. Attends l'accord.
6. **Applique** ce qui a été accepté, puis
   `python3 scripts/validate.py` jusqu'à zéro erreur.
7. **Marque les entrées traitées** — celles qui ont été promues **et** celles
   qui ont été écartées, sinon elles reviendront à chaque fois :
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" resolve --ids 3,7,12 --note "..."`
8. **Commit** avec un message qui dit ce que le skill sait faire de plus, pas
   « mise à jour du skill ».

## Format de sortie

```markdown
## Journal : N leçons en attente

### À promouvoir
| # | Skill | Leçon | Vue | Où ça va |
|---|---|---|---|---|
| 3 | code | Toujours … | ×4 | Contexte figé |

### À classer ailleurs
| # | Leçon | Destination | Pourquoi |
|---|---|---|---|

### À écarter
| # | Leçon | Pourquoi |
|---|---|---|

### Ce qui peut sortir
| Skill | Ce que je retire | Pourquoi ça ne sert plus |
|---|---|---|

### Diff proposé
<les modifications exactes, fichier par fichier>

### Bilan
<Ce que le skill saura faire de mieux, en 2 lignes. Et le solde :
+X lignes / −Y lignes.>
```

## Exemple

Entrée : 11 leçons en attente, dont 4 fois « le code de dash utilisait
BodyVelocity » et 3 fois « tu as oublié de me dire dans quel service coller ».

Sortie : la première monte en règle explicite dans la table
`skills/code/references/api-obsolete.md` — elle existe déjà, c'est sa place,
pas le corps du skill. La seconde
révèle que la section `Fichiers / instances` du gabarit de sortie est sautée :
le remède n'est pas une règle de plus, c'est une ligne dans `Avant de rendre`
qui la rend vérifiable.

Et un retrait : le skill dit deux fois de poser `.Parent` en dernier, dans le
contexte figé et dans les pièges. On garde la version « pièges », qui explique
pourquoi.

## Pièges

- **Empiler sans jamais retirer.** Chaque ligne est rechargée à chaque
  déclenchement. Un skill qui double de taille produit de moins bons
  résultats, pas de meilleurs.
- **Promouvoir un incident isolé.** Une fois n'est pas une règle : c'est
  comme ça qu'un skill se remplit de cas particuliers qui ne se reproduiront
  jamais.
- **Traiter un problème de déclenchement dans le corps.** Si le skill ne s'est
  pas déclenché, le corps n'a jamais été lu. Seule la description compte.
- **Modifier le plugin installé.** La prochaine mise à jour écrase tout. Le
  repo est la source.
- **Oublier `resolve`.** Les entrées non marquées reviennent au tour suivant
  et tu reproposes ce que l'utilisateur a déjà écarté.
- **Ajouter une règle là où il faut une vérification.** « Pense à X » dans le
  contexte figé se dilue ; « [ ] X » dans `Avant de rendre` se vérifie.

## Avant de rendre

- [ ] Chaque leçon du journal est dans un des trois tas, aucune oubliée.
- [ ] Rien de promu qui n'ait été vu au moins deux fois, sauf règle générale
      explicitement justifiée.
- [ ] J'ai cherché ce qui peut sortir, et dit ce que j'ai trouvé — ou pourquoi
      rien ne sort.
- [ ] Les problèmes de déclenchement sont traités dans la `description`.
- [ ] Les exclusions croisées touchées le sont dans les deux sens.
- [ ] Rien n'a été écrit avant l'accord de l'utilisateur.
- [ ] `python3 scripts/validate.py` passe.
- [ ] `journal.py resolve` appelé sur les promues **et** les écartées.
