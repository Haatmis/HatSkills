# HatSkills

Mes skills Claude pour le développement de jeux **Roblox**, packagés en plugin.

## Installation

```shell
/plugin marketplace add haatmis/HatSkills
/plugin install roblox@hatskills
```

Les skills s'invoquent alors `/roblox:<nom>` — ou se déclenchent tout seuls quand
leur `description` correspond à ce que tu demandes.

Pour développer sans installer :

```bash
claude --plugin-dir ./plugins/roblox
# puis /reload-plugins après chaque modification
```

## Organisation

```
HatSkills/
├── .claude-plugin/marketplace.json   # le marketplace « hatskills »
├── plugins/roblox/                      # le plugin
│   ├── .claude-plugin/plugin.json
│   └── skills/<nom>/SKILL.md         # ← les skills vivent ici
├── docs/                             # la méthode
├── templates/SKILL.template.md       # le point de départ d'un nouveau skill
└── scripts/validate.py               # la vérification avant commit
```

## Ajouter un skill

```shell
/roblox:nouveau-skill
```

Ou à la main : copie `templates/SKILL.template.md` dans
`plugins/roblox/skills/<nom>/SKILL.md`, remplis-le, puis

```bash
python3 scripts/validate.py
```

Le validateur vérifie le frontmatter, la qualité de la description (déclenchement
et exclusions), la présence d'un gabarit de sortie et d'un exemple, les renvois
morts, et signale deux skills dont les descriptions se recouvrent trop.

## La méthode

1. [Choisir le bon outil](docs/01-choisir-le-bon-outil.md) — skill, plugin,
   CLAUDE.md, hook, subagent ou MCP : ce que chacun permet.
2. [Écrire un skill qui marche dès le premier prompt](docs/02-guide-ecriture.md) —
   déclenchement, frontières entre skills, structure anti-dérive.
3. [Checklist de relecture](docs/03-checklist.md) — à passer avant de committer.

### Le résumé en trois lignes

- **Ça ne se déclenche pas** → le problème est dans la `description`, jamais
  dans le corps. C'est le seul texte que Claude voit avant de décider.
- **Ça déclenche mais ça dérive** → il manque un **gabarit de sortie exact** et
  un exemple entrée → sortie.
- **Je dois re-préciser à chaque fois** → tout ce qui a été précisé deux fois à
  la main appartient à la section `Contexte figé` du skill.

## Skills disponibles

| Skill | Ce qu'il fait |
|---|---|
| `game-design` | Cadre une feature avant tout code : règles, chiffres jouables, cas limites, risques — et écrit la spec dans `docs/design/` |
| `feature` | Exécute une spec : découpe en étapes, appelle le skill compétent à chacune, vérifie dans Studio, livre avec placeholders |
| `hat3d` | Image → modèle 3D Roblox : `model.json` comme source de vérité, préview HTML à valider, `build.lua` généré pour Studio |
| `vfx` | Crée des effets visuels (particules, faisceaux, traînées) en presets réutilisables, dérivés de la charte du projet |
| `code` | Écrit un morceau de code Luau vanilla délimité, et le vérifie dans Studio via le MCP avant de le rendre |
| `debug` | Diagnostique un comportement anormal, reproduit le bug dans Studio pour le prouver, puis corrige la cause racine |
| `affiner` | Consolide le journal d'apprentissage dans les skills, en proposant un diff à valider |
| `nouveau-skill` | Crée un skill conforme aux conventions de ce repo, après interview |

Conventions communes portées par `code` : vanilla strict (aucune lib externe),
nommage Roblox officiel, `--!strict` sur les ModuleScripts, arborescence Rojo
`src/{server,client,shared}`, logique de jeu côté serveur uniquement, et zéro
API dépréciée (table complète dans
[`references/api-obsolete.md`](plugins/roblox/skills/code/references/api-obsolete.md)).

## La chaîne d'une feature

Une demande comme « ajoute un système qui permet de taper les autres joueurs »
traverse plusieurs métiers : code serveur, code client, animation, VFX, son.
Aucun skill ne couvre tout, et rien ne les coordonne spontanément — d'où une
chaîne explicite, où chaque maillon appelle le suivant par son nom plutôt que
d'espérer un déclenchement automatique.

```
demande floue
     │
     ▼
game-design ──► docs/design/<feature>.md        règles, chiffres, cas limites
     │
     ▼
feature ──────► découpe en étapes ordonnées     serveur avant client, toujours
     │              │
     │              ├─► hat3d   (étape 0 : les props dont la feature a besoin)
     │              ├─► code    (étapes 1-5, vérifiées dans Studio)
     │              ├─► vfx     (étape 6, vérifiée dans Studio)
     │              └─► debug   (si une étape casse)
     ▼
système qui tourne + src/shared/Config/Assets.luau
                          │
                          └─► tu colles tes IDs, tu dis « reprends »
```

**Le point de rendez-vous des assets.** Claude ne peut pas publier une
animation ni créer un son : ces identifiants viennent de toi. Plutôt que de
bloquer, `feature` livre un système complet où chaque ID manquant vaut `0`
dans `src/shared/Config/Assets.luau` — le code teste cette valeur et saute le
son ou l'animation au lieu de planter. Tu remplis le fichier quand tu veux, tu
demandes à reprendre, et seuls les branchements concernés sont revérifiés.

**Deux règles portées par `feature`.** Le serveur avant le client, parce qu'une
feature construite dans l'autre sens est un aimant à exploiteurs et coûte plus
cher à reprendre qu'à écrire correctement. Et une vérification dans Studio
après *chaque* étape : une erreur d'étape 1 trouvée à l'étape 1 coûte une
correction, trouvée à l'étape 8 il faut d'abord démêler ce qui vient de quoi.

## La boucle d'amélioration

Un SKILL.md est un fichier statique : il ne se réécrit pas tout seul. Ce repo
remplace l'auto-amélioration magique par une boucle en deux temps.

**1. Capture, au fil de l'eau.** Chaque skill enregistre une leçon quand l'un
de trois signaux se produit — tu l'as corrigé, la vérification Studio a révélé
une erreur de sa part, ou tu as dû re-préciser un contexte qu'il aurait dû
porter. Rien d'autre ne vaut une entrée.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" status
```

Le journal vit dans `${CLAUDE_PLUGIN_DATA}/journal.jsonl` : il survit aux mises
à jour du plugin et il est partagé entre tous tes projets. Les leçons
identiques fusionnent et incrémentent un compteur — c'est ce compteur qui
distingue une vraie règle d'un incident isolé.

Le protocole complet vit dans
[`plugins/roblox/references/journal.md`](plugins/roblox/references/journal.md) ;
chaque skill en porte une version compacte. Les huit skills sont câblés —
sauf `affiner`, qui vide le journal plutôt que de le remplir.

**2. Consolidation, quand tu le décides.** À partir de 8 leçons en attente, le
skill actif te signale qu'il y a de la matière. Tu lances `/roblox:affiner`,
qui trie, propose un diff et n'écrit qu'après ton accord.

La contrainte qui gouverne tout : **chaque ligne d'un SKILL.md est rechargée à
chaque déclenchement.** Un skill qui grossit à chaque passage se dilue et rend
de moins bons résultats. C'est pourquoi `affiner` cherche systématiquement ce
qui peut *sortir*, et pourquoi une leçon vue une seule fois n'entre pas.

## Mesurer plutôt que supposer

Le validateur détecte les collisions **probables** entre descriptions, par
recouvrement de vocabulaire. Il ne dit pas ce qui se passe vraiment. Pour ça,
une suite de sept évals de routage mesure **quel skill se déclenche** sur une
phrase réelle, et surtout lesquels ne doivent pas :

```bash
cd plugins/roblox && claude plugin eval .
```

Les quatre cas de frontière sont les plus informatifs. Un skill qui ne se
déclenche jamais est un problème visible ; un skill qui prend le terrain d'un
autre ne se voit pas, et rend un résultat plausible mais du mauvais métier.

Détail des cas et lecture des échecs :
[`plugins/roblox/evals/README.md`](plugins/roblox/evals/README.md).

## Intégration continue

| Workflow | Quand | Coût |
|---|---|---|
| `validate.yml` | Chaque push et chaque PR | Gratuit — aucun appel au modèle |
| `evals.yml` | À la main (`workflow_dispatch`) | **Payant** — chaque cas est un vrai appel |

Les évals ne sont volontairement pas branchées sur chaque push : elles
factureraient ton compte à chaque virgule changée. Les graders utilisés sont
tous de type `tool_used`, donc sans modèle juge, et `max_turns: 3` plafonne
le coût — le routage se décide au premier tour.
