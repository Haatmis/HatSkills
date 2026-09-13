# HatSkills

Mes skills pour Claude, packagés en plugin.

## Installation

```shell
/plugin marketplace add haatmis/HatSkills
/plugin install hat@hatskills
```

Les skills s'invoquent alors `/hat:<nom>` — ou se déclenchent tout seuls quand
leur `description` correspond à ce que tu demandes.

Pour développer sans installer :

```bash
claude --plugin-dir ./plugins/hat
# puis /reload-plugins après chaque modification
```

## Organisation

```
HatSkills/
├── .claude-plugin/marketplace.json   # le marketplace « hatskills »
├── plugins/hat/                      # le plugin
│   ├── .claude-plugin/plugin.json
│   └── skills/<nom>/SKILL.md         # ← les skills vivent ici
├── docs/                             # la méthode
├── templates/SKILL.template.md       # le point de départ d'un nouveau skill
└── scripts/validate.py               # la vérification avant commit
```

## Ajouter un skill

```shell
/hat:nouveau-skill
```

Ou à la main : copie `templates/SKILL.template.md` dans
`plugins/hat/skills/<nom>/SKILL.md`, remplis-le, puis

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
| `nouveau-skill` | Crée un skill conforme aux conventions de ce repo, après interview |
