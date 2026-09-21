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

## Le mode plein ment aussi : vérifier l'instrument

Studio ouvert et MCP connecté ne suffit pas. L'instrument peut rendre un
chiffre faux **sans lever la moindre erreur**, et c'est le plus coûteux des
échecs : on ne se sait pas trompé, on croit mesurer.

**Le viewport doit rendre.** Vue 3D réduite, et `PreRender`/`RenderStepped`
tombent à **0 par seconde** pendant que `Heartbeat` tourne à 144 —
`TweenService` n'avance plus non plus. Relevé : `ViewportSize` à 1×1. Compte
les deux avant toute mesure qui dépend du rendu. Et pour rétablir : ni
maximiser la fenêtre ni fermer les onglets de l'éditeur de script n'y font
quoi que ce soit, **un clic physique dans la zone 3D, si**.

**Borne une sonde au temps réel** (`os.clock`), jamais à la grandeur qu'elle
mesure. Une boucle qui attendait que `Sound.TimePosition` avance a tourné
jusqu'au délai de 120 s du MCP — en mode Edit, un `Sound` annonce
`IsPlaying = true` et n'avance jamais.

**`Model:GetPivot()` peut mentir** : un modèle porte un `WorldPivot` qui peut
être figé et ne pas suivre ses pièces. Une animation qui marchait s'est
mesurée « aucun mouvement ». Observe la position réelle d'une `BasePart`.

**`PlaybackLoudness` est indépendant de `Volume`** : il rend la forme d'onde du
fichier, pas la sortie. Pour équilibrer un mélange, raisonne sur le produit
sonie × volume — jamais sur la sonie seule.

**Le pointeur synthétique se calibre avant de servir.** La coordonnée envoyée
et celle que `GetMouseLocation` rend au jeu peuvent différer de la hauteur de
l'inset GUI (58 px relevés), et le pointeur ne bouge pas du tout si la fenêtre
Studio n'a pas le premier plan — sans erreur. `user_mouse_input` avec
`instance_path` n'accepte que des `GuiObject` : pour viser une pièce 3D,
passe par `WorldToViewportPoint` moins l'inset. `VirtualInputManager` est
refusé au bac à sable (`lacking capability RobloxScript`).

**Et un relevé s'arme avant le geste qui le déclenche.** Deux appels MCP ne
partent pas ensemble : lance la sonde en `task.spawn`, fais-lui écrire son
résultat dans un attribut, puis déclenche, puis relis l'attribut.

**Pour tester un coup validé serveur, équipe l'outil depuis le serveur.**
`Humanoid:EquipTool` appelé côté client ne réplique pas : le serveur voit
« aucun outil » et refuse chaque coup en silence.

**Pour rapprocher un joueur d'un objet, déplace le personnage, jamais
l'objet.** Le serveur voit l'objet là où il l'a laissé, et refuse sur le
contrôle de distance.

**Une instance créée par le MCP en mode Edit ne marque pas la place comme
modifiée** : Studio ne propose donc jamais de sauvegarder, et elle disparaît à
la fermeture. Dis-le au moment de la créer, ou fais venir le contenu par Rojo.
Ce que crée un *plugin* survit, lui, parce qu'il passe par
`ChangeHistoryService`.

**Quand Rojo n'est pas connecté**, pousse le code par `HttpService` :
`HttpEnabled` à vrai, un serveur HTTP local sur le dossier du projet, et
`script.Source = HttpService:GetAsync(...)`. Studio lit les fichiers lui-même,
le résultat est identique à l'octet, et il n'y a aucune transcription
possible. En contrepartie, ces scripts ne sont plus suivis par Rojo : redis-le
avant de publier.

## Ce qui ne change jamais

Le mode ne change pas ce qui est **écrit**, seulement ce qui est **affirmé**.
Aucune règle du skill ne se relâche parce que Studio est fermé : on n'écrit pas
du code plus approximatif sous prétexte que personne ne le lancera aujourd'hui.
