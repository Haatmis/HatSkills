---
name: atelier
description: >
  Entretient les skills du plugin : en crée un nouveau après interview, ou
  consolide le journal d'apprentissage dans les skills existants. Utilise ce
  skill quand l'utilisateur veut créer ou ajouter un skill, dit « transforme
  ça en skill », « fais-en un skill », « j'en ai marre de retaper ça », ou
  décrit un geste qu'il répète — et aussi quand il dit « affine »,
  « consolide », « mets à jour les skills », « applique ce que tu as appris »,
  « vide le journal », ou donne suite au signalement « N leçons en attente ».
  N'utilise pas ce skill pour le travail sur le jeu lui-même : écrire du code
  (voir code), cadrer une feature (voir game-design), diagnostiquer (voir
  debug). L'atelier ne touche qu'aux skills, jamais au jeu.
---

# Atelier des skills

## Situation

Deux gestes rares mais structurants : fabriquer un skill, et affûter ceux qui
existent. Ils partagent la même matière et les mêmes garde-fous, d'où un seul
skill — mais **deux livrables distincts**, donc deux gabarits de sortie.

Le mode se lit dans la demande. Il n'y a pas d'ambiguïté possible : on ne
consolide pas ce qui n'existe pas, on ne crée pas ce qui est déjà là.

| Le signal | Le mode |
|---|---|
| « fais-en un skill », « j'en ai marre de retaper », un geste répété décrit | **Créer** |
| « affine », « consolide », « applique ce que tu as appris », « N leçons » | **Consolider** |

## Contexte figé

**On travaille dans le repo HatSkills, jamais dans le plugin installé** — une
mise à jour du plugin écraserait les changements. Si le repo n'est pas ouvert,
produis le diff proposé et dis-le, au lieu d'écrire dans l'installation.

**Langue** : français, y compris dans le frontmatter. Nom du skill en
kebab-case, identique au nom du dossier.

**Un skill = un livrable.** Si nommer la sortie demande deux mots, le
périmètre est trop large : découpe. *(Cet atelier est la seule exception
assumée : deux modes, deux gabarits, parce que les deux gestes sont rares et
que le mode se lit sans hésitation.)*

**Améliorer ≠ grossir.** Tout ce qui entre dans un `SKILL.md` est rechargé à
**chaque** déclenchement. Un skill qui grossit à chaque passage se dilue et
rend de moins bons résultats — l'inverse du but.

**Un problème de déclenchement se règle dans la `description`, jamais dans le
corps.** Si le skill ne s'est pas déclenché, son corps n'a jamais été lu.

**`python3 scripts/validate.py` doit passer sans erreur ni alerte** avant tout
commit.

---

## Mode CRÉER

### Procédure

1. **Vérifie que c'est bien un skill.** Ça s'applique tout le temps → le
   `CLAUDE.md` du projet. Le déclenchement doit être garanti → un hook. C'est
   un cas unique → un bon prompt suffit. Dis-le franchement plutôt que de
   produire un skill inutile.
2. **Interviewe.** Quatre questions, pas plus :
   - Quel est le livrable, en un mot ?
   - Quelles phrases tapes-tu réellement quand tu veux ça ?
   - Qu'est-ce que tu te retrouves à re-préciser à chaque fois ?
   - À quoi ressemble une bonne sortie ? (demande un exemple réel)
3. **Cherche les voisins** dans `plugins/roblox/skills/` et repère ceux dont le
   vocabulaire de déclenchement recoupe le nouveau.
4. **Écris la description** : ce que ça produit → quand s'en servir, avec les
   phrases réelles et un ton un peu insistant → quand ne pas s'en servir, en
   nommant le skill voisin.
5. **Écris le corps** d'après `templates/SKILL.template.md`. Les réponses à la
   question 3 de l'interview vont dans `Contexte figé`. Recopie la section
   `Apprendre de la session` en remplaçant `--skill` par le nouveau nom : sans
   elle, le skill ne remontera jamais rien.
6. **Pose l'exclusion croisée dans les deux sens** — chez le voisin aussi.
7. **Valide** jusqu'à zéro erreur, puis **ajoute un cas d'éval** dans
   `plugins/roblox/evals/` : un positif, et un de frontière avec le voisin.
8. **Propose 2-3 prompts de test**, dont un piège qui doit partir ailleurs, et
   demande s'ils sont réalistes avant de les jouer.

### Format de sortie

Crée `plugins/roblox/skills/<nom>/SKILL.md` au gabarit de
`templates/SKILL.template.md`, puis rends :

```markdown
## <nom> créé
`plugins/roblox/skills/<nom>/SKILL.md`

**Description** (le texte intégral, c'est lui qui décide du déclenchement)
> …

## Frontières
| Voisin | Exclusion posée chez lui |
|---|---|

## Éval ajoutée
<le cas, et ce qu'il vérifie>

## Validation
<sortie de validate.py>

## À tester
1. <prompt réaliste>
2. <le piège : doit partir sur un autre skill>
```

---

## Mode CONSOLIDER

### Procédure

1. **Lis le journal** :
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" list`
   Les entrées sortent par récurrence décroissante.
2. **Trie en trois tas :**
   - **À promouvoir** — `occurrences ≥ 2`, ou une seule fois mais règle
     générale et vérifiable. Destination : le `Contexte figé` du skill visé, ou
     ses `Pièges` si la leçon s'explique mieux par un contre-exemple.
   - **À classer ailleurs** — une API dépréciée va dans la table du skill
     concerné, pas dans son corps. Une convention propre à un projet va dans le
     `CLAUDE.md` de ce projet : un skill est transversal.
   - **À écarter** — incident isolé, redite, préférence ponctuelle. Dis
     pourquoi ; ne le tais pas.
3. **Cherche ce qui peut sortir.** Relis chaque skill touché en entier :
   règles que plus rien ne justifie, doublons, exemples redondants. Une
   consolidation sans aucun retrait sur un skill mûr est suspecte — signale-le.
4. **Traite les leçons de déclenchement dans les descriptions**, et renforce
   les exclusions croisées **dans les deux sens**.
5. **Propose le diff.** Attends l'accord. Rien n'est écrit avant.
6. **Applique**, puis valide jusqu'à zéro erreur.
7. **Marque les entrées traitées** — promues **et** écartées, sinon elles
   reviendront :
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" resolve --ids 3,7 --note "…"`
8. **Bumpe la version** du plugin : sans ça personne ne recevra la mise à jour.

### Format de sortie

```markdown
## Journal : N leçons en attente

### À promouvoir
| # | Skill | Leçon | Vue | Où ça va |
|---|---|---|---|---|

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
<fichier par fichier>

### Bilan
<Ce que les skills sauront faire de mieux, en 2 lignes. Et le solde :
+X lignes / −Y lignes.>
```

---

## Exemple

**Créer.** « J'en ai marre de reformater mes notes de réunion » → après
interview, un skill `compte-rendu` dont la description contient les phrases
réelles de l'utilisateur (« CR », « débrief », « mets ça au propre ») et dont
le `Contexte figé` porte ce qu'il a dit re-préciser : le client nommé en toutes
lettres, les dates en JJ/MM, aucune action sans porteur.

**Consolider.** 11 leçons, dont 4 fois « le dash utilisait BodyVelocity » et
3 fois « tu as oublié de dire dans quel service coller ». La première monte
dans la table des API dépréciées — elle existe déjà, c'est sa place, pas le
corps du skill. La seconde révèle que la section `Fichiers / instances` du
gabarit est sautée : le remède n'est pas une règle de plus, c'est une ligne
dans `Avant de rendre` qui la rend vérifiable. Et un retrait : `code` disait
deux fois de poser `.Parent` en dernier — on garde la version qui explique
pourquoi.

## Pièges

- **Empiler sans jamais retirer.** Chaque ligne est rechargée à chaque
  déclenchement.
- **Promouvoir un incident isolé.** Une fois n'est pas une règle : c'est comme
  ça qu'un skill se remplit de cas particuliers qui ne reviendront jamais.
- **Écrire le corps avant la description.** La description décide du
  déclenchement ; un corps parfait derrière une description vague ne sert
  jamais.
- **Mettre « quand utiliser » dans le corps.** Il n'est lu qu'une fois la
  décision prise — trop tard.
- **Décrire la sortie en prose.** La prose laisse place à l'improvisation, le
  gabarit non.
- **Oublier l'exclusion croisée.** « Pas pour B » sans que B dise « pas pour
  A » laisse la collision intacte dans un sens sur deux.
- **Modifier le plugin installé.** La prochaine mise à jour écrase tout.
- **Oublier `resolve`.** Les entrées non marquées reviennent, et tu reproposes
  ce que l'utilisateur a déjà écarté.
- **Oublier de bumper la version.** La consolidation ne sert à rien si
  personne ne la reçoit.

## Apprendre de la session

**En mode créer uniquement** — consolider, c'est déjà vider le journal.

Trois signaux valent une entrée, et trois seulement : l'utilisateur t'a
corrigé, la vérification a révélé une erreur de ta part, ou un contexte a dû
t'être re-précisé. Formule une **règle**, pas un récit :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" add \
  --skill atelier --type correction \
  --lesson "Toujours …" --context "ce qui se passait, une ligne"
```

Protocole complet : `${CLAUDE_PLUGIN_ROOT}/references/journal.md`.

## Avant de rendre

**Créer**
- [ ] `name` == nom du dossier, kebab-case.
- [ ] La description dit ce que ça produit, quand, et quand **pas**.
- [ ] Les phrases de déclenchement sont celles de l'utilisateur.
- [ ] `Contexte figé` porte tout ce qu'il a dit re-préciser.
- [ ] Gabarit de sortie exact + exemple entrée → sortie réel.
- [ ] Section `Apprendre de la session` présente, avec le bon `--skill`.
- [ ] Exclusion croisée posée **dans les deux sens**.
- [ ] Un cas d'éval ajouté : positif + frontière.

**Consolider**
- [ ] Chaque leçon est dans un des trois tas, aucune oubliée.
- [ ] Rien de promu qui n'ait été vu deux fois, sauf règle générale justifiée.
- [ ] J'ai cherché ce qui peut sortir — et dit ce que j'ai trouvé, ou pourquoi
      rien ne sort.
- [ ] Les problèmes de déclenchement traités dans les descriptions.
- [ ] Rien écrit avant l'accord de l'utilisateur.
- [ ] `journal.py resolve` appelé sur les promues **et** les écartées.
- [ ] Version du plugin bumpée.

**Les deux**
- [ ] `python3 scripts/validate.py` : zéro erreur, zéro alerte.
