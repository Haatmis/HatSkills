# 2. Écrire un skill qui marche dès le premier prompt

## 2.1 Le modèle mental : trois niveaux de chargement

Un skill n'est pas chargé d'un bloc. Comprendre ça explique 90 % des ratés.

| Niveau | Contenu | Quand c'est en contexte | Budget |
|---|---|---|---|
| 1 | `name` + `description` | **Toujours**, pour tous tes skills | ~100 mots |
| 2 | Le corps du `SKILL.md` | Seulement quand le skill se déclenche | < 500 lignes |
| 3 | `references/`, `scripts/`, `assets/` | Seulement quand le corps y renvoie | illimité |

Deux conséquences directes :

- **La `description` est le seul texte que Claude voit avant de décider.** Si le
  skill ne se déclenche pas, le problème est *toujours* là, jamais dans le corps.
- **Chaque ligne du corps est un coût récurrent.** Le contenu reste en contexte
  pour tous les tours suivants. Un corps bavard ne rend pas le skill plus fiable,
  il le rend plus cher et plus dilué.

## 2.2 Le frontmatter

Tous les champs sont optionnels, mais `description` ne l'est pas vraiment.

### Les quatre que tu utiliseras tout le temps

```yaml
---
name: note-client                    # défaut : le nom du dossier
description: ...                     # le déclencheur — voir 2.3
allowed-tools: Bash(git *) Read      # pré-autorise des outils, valable 1 tour
disable-model-invocation: true       # /nom seulement, jamais automatique
---
```

### Les autres, par besoin

| Champ | Effet | Quand t'en servir |
|---|---|---|
| `when_to_use` | Texte ajouté à la description (plafond combiné : **1 536 caractères**) | Quand la description devient longue et que tu veux séparer « ce que ça fait » de « quand » |
| `user-invocable: false` | Claude peut l'invoquer, toi non | Skills de contexte pur (référence, jargon métier) |
| `paths: ["src/**"]` | Ne s'active que sur ces fichiers | Réduit drastiquement les faux déclenchements |
| `argument-hint: [ticket]` | Aide à l'autocomplétion | Skills invoqués à la main avec un argument |
| `arguments: [issue, branch]` | Arguments nommés, utilisables via `$issue` | Skills paramétrés |
| `disallowed-tools` | Retire des outils pendant le skill | Empêcher une dérive connue (ex. bloquer `AskUserQuestion` sur un skill qui doit trancher seul) |
| `context: fork` | Tourne dans un subagent isolé | Tâches longues qui pollueraient le contexte |
| `model`, `effort` | Force un modèle / un niveau d'effort | Rarement. À réserver aux skills coûteux ou triviaux |

### Substitutions utilisables dans le corps

`$ARGUMENTS` (tout), `$0`/`$1`/`$2` (Nième), `$nom` (si `arguments:`),
`${CLAUDE_SKILL_DIR}` (le dossier du skill — indispensable pour pointer un
script embarqué), `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`.

Et l'injection de contexte dynamique :

```markdown
## État actuel
- Diff : !`git diff HEAD`
```

La commande tourne **avant** que Claude voie le skill, et sa sortie est
injectée. Attention : si elle échoue (code de retour non nul), **toute
l'invocation du skill est annulée**. N'y mets que des commandes qui ne peuvent
pas casser.

---

## 2.3 La description — contre le non-déclenchement et le chevauchement

C'est le champ le plus important du fichier. Écris-le en dernier, relis-le en
premier.

### La formule

```
<Ce que ça produit, une phrase à l'impératif>.
Utilise ce skill quand <déclencheurs concrets : phrases réelles, types de
fichiers, situations>.
N'utilise pas ce skill pour <ce qui appartient à un autre skill>.
```

La troisième ligne est celle que tout le monde oublie. C'est elle qui règle le
problème des skills qui se marchent dessus.

### Avant / après

**Avant** — vague, ne se déclenche jamais :
```yaml
description: Aide à rédiger des comptes rendus.
```

**Après** — explicite, et borné :
```yaml
description: >
  Rédige un compte rendu de réunion client au format interne (décisions,
  actions avec porteur et échéance, points en suspens). Utilise ce skill dès
  que l'utilisateur mentionne un compte rendu, un CR, des notes de réunion, un
  débrief client, ou colle une transcription à mettre au propre — même sans
  demander explicitement un « compte rendu ». N'utilise pas ce skill pour une
  note interne d'équipe (voir note-interne) ni pour une proposition
  commerciale (voir proposition).
```

### Les quatre règles

1. **Sois un peu insistant.** Claude a tendance à *sous*-déclencher les skills.
   « Utilise ce skill dès que… même si l'utilisateur ne demande pas
   explicitement X » est une formulation qui marche.
2. **Mets les vraies phrases de l'utilisateur**, pas des catégories abstraites.
   Tu écris « CR », « débrief », « mets ça au propre » ? Mets-les.
3. **Tout le « quand » va dans la description**, jamais dans le corps. Le corps
   n'est lu qu'une fois la décision prise — trop tard.
4. **Nomme les skills voisins.** `N'utilise pas ce skill pour X (voir <autre>)`
   donne à Claude de quoi arbitrer au lieu de deviner.

### Faire respecter les frontières

Trois skills qui se chevauchent, c'est trois skills mal découpés. Le remède :

- **Un skill = un livrable.** Si tu n'arrives pas à nommer la sortie en un mot,
  le périmètre est trop large — découpe.
- **Vocabulaire de déclenchement disjoint.** Deux descriptions ne doivent pas
  partager leurs mots-clés. Si c'est le cas, soit tu fusionnes, soit tu
  spécialises.
- **Exclusions croisées.** Si A dit « pas pour B », B doit dire « pas pour A ».
- **`paths:` quand c'est possible.** Un skill limité à `docs/**` ne se
  déclenchera jamais sur du code. C'est gratuit et infaillible.
- **`disable-model-invocation: true`** pour tout ce dont tu veux garder le
  contrôle du moment. Un skill qu'on appelle toujours à la main ne peut pas
  entrer en collision avec un autre.

---

## 2.4 Le corps — contre la dérive et le « je dois re-préciser »

Un skill qui se déclenche mais dérive a presque toujours le même défaut : il
décrit une intention au lieu de décrire un résultat.

### La structure qui tient

```markdown
# <Nom du skill>

## Situation
<1-2 phrases : où on est, ce qui compte ici.>

## Contexte figé
- Public : ...
- Ton : ...
- Contraintes métier : ...
- Vocabulaire imposé / interdit : ...

## Procédure
1. ...
2. ...
3. ...

## Format de sortie
<Le gabarit exact, copiable tel quel.>

## Exemple
Entrée : ...
Sortie : ...

## Pièges
- <Erreur fréquente> — <pourquoi c'est faux ici>

## Avant de rendre
- [ ] ...
- [ ] ...
```

### Pourquoi chaque section est là

**`Contexte figé`** répond directement à « je dois toujours re-préciser des
choses ». Tout ce que tu te surprends à retaper d'une session à l'autre — le
ton, le public, le fait que le client s'appelle X et pas Y, le format de date,
les mots à bannir — appartient à cette section. Règle pratique : **si tu l'as
précisé deux fois à la main, il doit être ici.**

**`Format de sortie`** est le meilleur anti-dérive qui existe. Un gabarit exact
laisse infiniment moins de place à l'improvisation qu'une description en prose.
Écris-le comme un modèle à remplir, pas comme une consigne.

**`Exemple`** vaut mieux que trois paragraphes d'explication. Un couple
entrée → sortie réel cale le registre, la longueur et le niveau de détail d'un
coup. Un seul exemple bien choisi suffit ; trois exemples proches se
neutralisent.

**`Avant de rendre`** est une relecture forcée. C'est ce qui rattrape les
oublis sur les sorties longues.

### Ton et rédaction

- **Impératif.** « Liste les actions » et non « il faudrait lister les actions ».
- **Explique le pourquoi plutôt que de crier.** Une salve de `MUST` et de
  majuscules se dilue vite ; une raison courte (« sinon le client ne sait pas
  qui porte l'action ») tient mieux, parce qu'elle se généralise aux cas que tu
  n'as pas prévus.
- **Généralise.** Un skill trop collé à un exemple précis échoue sur le cas
  d'à côté.
- **Écris un brouillon, puis relis à froid.** Les deux tiers du gain sont là.

### Divulgation progressive

Dès que le corps dépasse ~500 lignes, sors le détail :

```
mon-skill/
├── SKILL.md              # la procédure, le format, l'exemple
├── references/
│   ├── api.md            # doc détaillée, lue seulement si besoin
│   └── glossaire.md
├── scripts/
│   └── verifier.py       # exécutable — n'entre jamais en contexte
└── assets/
    └── modele.docx       # fichiers utilisés dans la sortie
```

Depuis `SKILL.md`, renvoie explicitement **et dis quand y aller** :

> Pour les cas multi-devises, lis `references/devises.md` avant de calculer.

Un renvoi sans condition de déclenchement ne sert à rien : soit Claude lit tout,
soit il ne lit rien.

Deux réflexes qui font gagner beaucoup :

- **Un script vaut mieux qu'une consigne** dès que la tâche est déterministe et
  répétitive. Le script s'exécute sans consommer de contexte et ne dérive pas.
- **Une table des matières** en tête de tout fichier de référence de plus de
  300 lignes.

---

## 2.5 Vérifier au lieu de supposer

Un skill n'est pas fini quand il est écrit, il est fini quand il se déclenche
au bon moment et produit la bonne forme.

1. **Écris 2-3 prompts de test réalistes** — la phrase que tu taperais
   vraiment, pas une reformulation propre de la description.
2. **Fais tourner avec et sans le skill.** La question n'est pas « est-ce que
   c'est bon ? » mais « qu'est-ce que le skill a apporté ? ». Sans comparaison,
   tu ne sais pas si tu as amélioré le skill ou eu de la chance.
3. **Ajoute un cas piège** : un prompt qui ressemble au déclencheur mais qui
   doit partir sur un autre skill. C'est le seul moyen de mesurer le
   chevauchement.
4. **Outils** : le skill `skill-creator` (`/anthropic-skills:skill-creator`)
   gère la boucle brouillon → évals → réécriture, y compris l'optimisation de
   la description pour le déclenchement. Pour un plugin,
   `claude plugin eval` rejoue un jeu de prompts avec et sans le plugin.
5. **Corrige toujours une seule chose à la fois.** Déclenchement et qualité de
   sortie sont deux problèmes distincts, avec deux remèdes distincts
   (description / corps). Les traiter ensemble empêche de savoir ce qui a marché.

---

Suite : [03-checklist.md](03-checklist.md) — la relecture avant de committer
