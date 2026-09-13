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
| `code` | Écrit du code Luau vanilla pour un jeu Roblox, et le vérifie dans Studio via le MCP avant de le rendre |
| `affiner` | Consolide le journal d'apprentissage dans les skills, en proposant un diff à valider |
| `nouveau-skill` | Crée un skill conforme aux conventions de ce repo, après interview |

Conventions communes portées par `code` : vanilla strict (aucune lib externe),
nommage Roblox officiel, `--!strict` sur les ModuleScripts, arborescence Rojo
`src/{server,client,shared}`, logique de jeu côté serveur uniquement, et zéro
API dépréciée (table complète dans
[`references/api-obsolete.md`](plugins/roblox/skills/code/references/api-obsolete.md)).

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

**2. Consolidation, quand tu le décides.** À partir de 8 leçons en attente, le
skill actif te signale qu'il y a de la matière. Tu lances `/roblox:affiner`,
qui trie, propose un diff et n'écrit qu'après ton accord.

La contrainte qui gouverne tout : **chaque ligne d'un SKILL.md est rechargée à
chaque déclenchement.** Un skill qui grossit à chaque passage se dilue et rend
de moins bons résultats. C'est pourquoi `affiner` cherche systématiquement ce
qui peut *sortir*, et pourquoi une leçon vue une seule fois n'entre pas.
