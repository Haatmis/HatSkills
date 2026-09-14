# Journal d'apprentissage

Les leçons tirées de l'usage réel des skills, en attente de consolidation par
`/roblox:atelier`. Une ligne JSON par leçon dans `journal.jsonl`.

## Pour que tes leçons atterrissent ici

Sans cette variable, le journal reste dans `${CLAUDE_PLUGIN_DATA}` : local à la
machine, et **perdu** quand une session cloud est recyclée.

```powershell
# À mettre une fois dans ton profil PowerShell ($PROFILE)
$env:HATSKILLS_JOURNAL_DIR = "C:\chemin\vers\HatSkills\.journal"
```

```bash
export HATSKILLS_JOURNAL_DIR="$HOME/HatSkills/.journal"
```

Ici, le journal est versionné : il suit tes machines, il a un historique, et tu
peux relire pourquoi une règle est entrée dans un skill six mois plus tard.

`.gitattributes` déclare `merge=union` sur le fichier : deux machines qui
divergent voient leurs lignes gardées des deux côtés, sans conflit.

## Ce qui est public

Ce dépôt est public. Les leçons le sont donc aussi. Ce ne sont que des règles
de métier — jamais de clé, de chemin personnel ni de contenu de jeu — mais
c'est à savoir avant d'y écrire.
