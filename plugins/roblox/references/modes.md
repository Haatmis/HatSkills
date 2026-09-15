# Les trois modes de vérification

Un skill de ce plugin ne rend jamais du travail en prétendant l'avoir vérifié.
Mais « vérifié » n'est pas binaire : selon ce qui est branché, le contrôle
possible va de complet à partiel. Ce qui compte, c'est que **le compte rendu
dise lequel** — un travail non vérifié annoncé comme vérifié est pire qu'un
travail non vérifié annoncé comme tel.

## L'échelle

| Mode | Condition | Ce qui est réellement contrôlé |
|---|---|---|
| **Plein** | Studio ouvert, MCP connecté | Le code s'exécute, l'Output est lu, les instances existent, le comportement est observé |
| **Réduit** | Pas de MCP, mais un projet Rojo sur le disque | `luau_check.py` passe, les chemins d'instance sont cohérents avec `src/`, les identifiants d'assets sont vérifiés auprès de Roblox |
| **Hors-ligne** | Ni MCP ni projet | Rien n'est exécuté. Relecture adverse et `luau_check.py` sur ce qui vient d'être écrit, c'est tout |

## Ce qu'on fait dans chaque mode

**Plein.** Le mode nominal. Exécute, lis l'Output, corrige, relance. Ne rends
rien tant qu'une erreur ou un avertissement subsiste.

**Réduit.** Le contrôle statique reste entier, et il attrape une bonne part des
défauts réels :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/luau_check.py" --dans src
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/toolbox.py" verifier --ids <ids> --proprietaire "<compte du jeu>"
```

Sur Windows, `py` si `python3` ouvre la boutique.

Ce qui reste invisible en mode réduit : tout ce qui dépend de l'exécution — une
instance absente au moment où le script tourne, un ordre de chargement, une
course entre deux événements, un `nil` qui n'apparaît qu'avec un vrai joueur.
Dis-le.

**Hors-ligne.** Même contrôle statique sur ce que tu viens d'écrire, plus la
relecture adverse. Aucune affirmation sur le comportement.

## La ligne à écrire dans le compte rendu

Une ligne, jamais plus, et jamais omise :

```markdown
## Vérifié
Mode plein — exécuté dans Studio, Output propre.
```

```markdown
## Vérifié
Mode réduit — MCP non connecté. luau_check passé (0 API dépréciée), chemins
cohérents avec src/. Non vérifié : l'exécution, donc l'ordre de chargement et
le comportement avec un joueur réel.
```

```markdown
## Vérifié
Mode hors-ligne — ni Studio ni projet. Relu en adversaire, luau_check passé.
Rien n'a été exécuté.
```

## Pourquoi c'est une échelle et pas un drapeau

Avant, la règle était « vérifie dans Studio, et si le MCP est absent, dis-le ».
Ça produisait deux états : vérifié, ou un aveu sans contenu. Or l'absence de
Studio n'empêche pas la moitié des contrôles — elle empêche seulement ceux qui
demandent une exécution. Annoncer « non vérifié » quand `luau_check` est passé
sous-vend le travail ; annoncer « vérifié » quand rien n'a tourné le survend.
Le mode dit exactement où on est.

## Ce qui ne change jamais

Le mode ne change pas ce qui est **écrit**, seulement ce qui est **affirmé**.
Aucune règle du skill ne se relâche parce que Studio est fermé : on n'écrit pas
du code plus approximatif sous prétexte que personne ne le lancera aujourd'hui.
