# Évals de routage

Onze cas qui mesurent **quel skill se déclenche** sur une phrase réelle. C'est
la seule façon de savoir si les descriptions font leur travail : le
recouvrement de vocabulaire que mesure `scripts/validate.py` détecte les
collisions probables, il ne dit pas ce qui se passe vraiment.

## Ce que chaque cas vérifie

### Les frontières — cinq cas

Ce sont les plus informatifs. Chacun vérifie qu'un skill part **et** que son
voisin reste à sa place.

| Cas | Doit déclencher | Ne doit PAS déclencher |
|---|---|---|
| `combat-multi-domaine` | `game-design` | `code` |
| `bug-humanoid-nil` | `debug` | `code` |
| `remote-simple` | `code` | `game-design` |
| `equilibrage-sans-code` | `game-design` | `code` |
| `pastille-degats` | `vfx` | `code` |

### Le routage simple — cinq cas

Chaque skill doit être atteint par la phrase qui lui correspond.

| Cas | Doit déclencher |
|---|---|
| `effet-impact` | `vfx` |
| `modele-3d` | `hat3d` |
| `reprise-assets` | `feature` |
| `creer-un-skill` | `atelier` |
| `consolider-journal` | `atelier` |

### Le cas négatif — `hors-perimetre`

Il ne rentre pas dans les tableaux ci-dessus, parce qu'il n'a **aucun** skill
attendu. Une question sur `git rebase` doit ne rien charger du tout : un seul
grader, `tool_used` avec `min: 0` et `max: 0`.

C'est le seul cas qui mesure le **sur-déclenchement** — et c'est la panne qui
ne se voit pas à l'usage. Un skill muet, tu le remarques tout de suite ; un
skill qui prend le terrain d'un autre te rend une réponse plausible, du mauvais
métier, sans rien signaler. Chacun coûte aussi son corps en contexte pour rien.

Sans ce cas, on ne mesurerait qu'une moitié du problème.

## Lancer

Depuis la racine du plugin (`plugins/roblox/`) :

```bash
claude plugin eval . --ablation none              # toute la suite
claude plugin eval . --ablation none --case bug-humanoid-nil
```

**`--ablation none` n'est pas optionnel ici.** Par défaut, la commande ajoute
un bras « sans plugin » et note l'écart. Or cette suite ne mesure qu'une chose :
quel skill se déclenche. La comparaison avec un Claude sans plugin n'apporte
rien — un plugin absent ne déclenche évidemment aucun skill — et elle double le
coût pour un delta sans information.

⚠ `claude plugin eval` est en **accès anticipé**. Si la commande répond
`plugin eval is currently in early access`, elle n'est pas encore activée sur
le compte. Voir « Mesurer sans la commande » plus bas.

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

## Mesurer sans la commande

Le harnais automatise la mesure ; il ne la conditionne pas. Les onze prompts se
jouent à la main en un quart d'heure, et le résultat est même **plus
représentatif** — l'éval tourne dans un bac à sable qui exclut `CLAUDE.md`, la
mémoire et les autres plugins, alors que ton usage réel les a tous.

**Protocole.** Une session par prompt, ou `/clear` entre chaque — sinon le
contexte de la question précédente fausse le déclenchement. Pour chaque
prompt : le coller, regarder quel skill Claude Code annonce avoir invoqué,
noter, passer au suivant. Ne corrige rien en cours de route.

| # | Prompt à taper | Attendu | Interdit |
|---|---|---|---|
| 1 | Rajoute un système qui permet de taper et d'infliger des dégâts aux autres joueurs | `game-design` | `code` |
| 2 | J'ai une erreur "attempt to index nil with 'Humanoid'" dans mon script de combat | `debug` | `code` |
| 3 | Ajoute un RemoteEvent pour que le client demande l'ouverture d'une porte | `code` | `game-design` |
| 4 | Les combats de mon jeu durent trop longtemps, je mets combien de dégâts par coup ? | `game-design` | `code` |
| 5 | Je veux des particules quand l'épée touche quelqu'un | `vfx` | — |
| 6 | Fais-moi un coffre en 3D pour mon jeu, je te donne une image de référence juste après | `hat3d` | — |
| 7 | J'ai rempli les IDs dans Config/Assets.luau, tu peux reprendre | `feature` | — |
| 8 | J'en ai marre de retaper les mêmes consignes pour mes messages de commit, transforme ça en skill | `atelier` | — |
| 9 | J'ai une dizaine de leçons en attente dans le journal, applique-les aux skills | `atelier` | — |
| 10 | On ne voit pas les dégâts qu'on inflige, ajoute une pastille avec le chiffre qui monte et disparaît | `vfx` | `code` |
| 11 | Explique-moi la différence entre git merge et git rebase | **aucun** | tous |

Les prompts sont ceux des `prompt.md` : si tu les reformules, tu mesures autre
chose. Note pour chaque ligne le skill réellement déclenché, même quand c'est
le bon — un « ✅ » sans détail perd l'information quand deux skills partent
ensemble.