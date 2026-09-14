# Évals de routage

Sept cas qui mesurent **quel skill se déclenche** sur une phrase réelle. C'est
la seule façon de savoir si les descriptions font leur travail : le
recouvrement de vocabulaire que mesure `scripts/validate.py` détecte les
collisions probables, il ne dit pas ce qui se passe vraiment.

## Ce que chaque cas vérifie

| Cas | Doit déclencher | Ne doit PAS déclencher |
|---|---|---|
| `combat-multi-domaine` | `game-design` | `code` |
| `bug-humanoid-nil` | `debug` | `code` |
| `remote-simple` | `code` | `game-design` |
| `equilibrage-sans-code` | `game-design` | `code` |
| `effet-impact` | `vfx` | — |
| `modele-3d` | `hat3d` | — |
| `reprise-assets` | `feature` | — |

Les quatre premiers sont les plus informatifs : ce sont les **frontières**.
Un skill qui ne se déclenche jamais est un problème visible ; un skill qui
prend le terrain d'un autre ne se voit pas, et produit un résultat plausible
mais du mauvais métier.

## Lancer

Depuis la racine du plugin (`plugins/roblox/`) :

```bash
claude plugin eval .                      # toute la suite
claude plugin eval . --case bug-humanoid-nil
```

## Coût

⚠ **Chaque cas est un vrai appel au modèle**, facturé sur ton compte.

Les graders utilisés ici sont tous de type `tool_used` : ils lisent la
transcription et **ne coûtent rien de plus** — pas de modèle juge. Le coût se
limite donc aux tours d'agent, et `max_turns: 3` les plafonne : le routage se
décide au premier tour, inutile de laisser la tâche se dérouler.

C'est pour cette raison que la suite n'est **pas** branchée sur chaque push.
Voir `.github/workflows/evals.yml`, déclenché à la main.

## Lire un échec

| Ce qui échoue | Où est le remède |
|---|---|
| Le bon skill ne s'est pas déclenché | Sa `description` : elle ne contient pas la phrase réelle, ou elle n'est pas assez insistante |
| Le mauvais skill s'est déclenché | L'exclusion croisée entre les deux, **dans les deux sens** |
| Les deux se sont déclenchés | Les vocabulaires de déclenchement se recouvrent : il faut spécialiser, ou fusionner |

Dans les trois cas, le remède est dans la **description**, jamais dans le
corps : quand un skill ne se déclenche pas, son corps n'a jamais été lu.

## Ajouter un cas

Chaque nouveau skill mérite au moins un cas positif, et un cas de frontière
avec son voisin le plus proche. Copier un dossier existant et changer le
`prompt.md` plus l'`input_match` des graders suffit.

Écrire le prompt **comme l'utilisateur le taperait** — pas une reformulation
propre de la description, sinon le test ne mesure que sa propre tautologie.
