# API Roblox obsolètes et leurs remplaçants

À consulter avant d'écrire du timing, du mouvement, de l'animation, de
l'input, du raycast ou de la sauvegarde.

Deux niveaux, distingués dans les tables :
- **Déprécié** — marqué comme tel par Roblox. Ne pas écrire.
- **Découragé** — fonctionne toujours, mais il existe mieux depuis. Ne pas
  écrire dans du code neuf.

## Sommaire

1. [Timing et threads](#1-timing-et-threads)
2. [Événements et instances](#2-événements-et-instances)
3. [Mouvement : BodyMovers → Constraints](#3-mouvement--bodymovers--constraints)
4. [Animation](#4-animation)
5. [Input](#5-input)
6. [Raycast et géométrie](#6-raycast-et-géométrie)
7. [Modèles et pivots](#7-modèles-et-pivots)
8. [Données et sauvegarde](#8-données-et-sauvegarde)
9. [Divers](#9-divers)

---

## 1. Timing et threads

| À éviter | Remplaçant | Niveau | Ce qui change |
|---|---|---|---|
| `wait(n)` | `task.wait(n)` | Déprécié | Précision bien meilleure et pas de throttling ; `wait()` peut dépasser largement le délai demandé sous charge |
| `spawn(f)` | `task.spawn(f)` | Déprécié | `spawn` ajoutait un délai non documenté avant de démarrer ; `task.spawn` démarre immédiatement |
| `delay(n, f)` | `task.delay(n, f)` | Déprécié | Même problème de dérive |
| `f()` différé d'une frame | `task.defer(f)` | — | Exécute à la fin du cycle courant, sans attendre un tick complet |
| `tick()` | `os.time()`, `os.clock()`, `workspace:GetServerTimeNow()` | Déprécié | `tick()` dépendait du fuseau de la machine. `os.clock()` pour mesurer une durée, `GetServerTimeNow()` pour un temps partagé client/serveur |
| `RunService.Stepped` | `RunService.PreSimulation` | Découragé | Même événement, nom explicite |
| `RunService.Heartbeat` | `RunService.PostSimulation` | Découragé | Idem |
| `RunService.RenderStepped` | `RunService.PreRender` | Découragé | Idem — client uniquement dans les deux cas |

Une boucle `while true do task.wait() end` est presque toujours le signe qu'un
événement ferait mieux l'affaire. Cherche `Changed`, `GetPropertyChangedSignal`,
`Touched`, ou un `RunService` explicite.

## 2. Événements et instances

| À éviter | Remplaçant | Niveau |
|---|---|---|
| `:connect()` | `:Connect()` | Déprécié |
| `:wait()` sur un signal | `:Wait()` | Déprécié |
| `:remove()` | `:Destroy()` | Déprécié |
| `:destroy()`, `:clone()`, `:children()`, `:findFirstChild()` | `:Destroy()`, `:Clone()`, `:GetChildren()`, `:FindFirstChild()` | Déprécié |
| `Instance.new("X", parent)` | `Instance.new("X")`, propriétés, puis `.Parent` en dernier | Découragé |
| `LoadLibrary` | — (supprimé) | Retiré |
| `ypcall` | `pcall` | Déprécié |
| `game.Workspace` | `workspace` ou `game:GetService("Workspace")` | Découragé |
| `game.Players` (indexation directe d'un service) | `game:GetService("Players")` | Découragé |

`Instance.new("X", parent)` fait répliquer l'instance avant qu'elle soit
configurée : coût réseau inutile, et l'objet est visible une frame dans son
état par défaut. Poser `.Parent` en dernier n'est pas du style, c'est une
optimisation.

Indexer un service directement (`game.Players`) casse si le service est
renommé ou pas encore chargé. `GetService` le crée au besoin.

## 3. Mouvement : BodyMovers → Constraints

Les `BodyMover` sont dépréciés en bloc. Les Constraints qui les remplacent
exigent un `Attachment` sur la pièce (ou deux, selon le cas).

| À éviter | Remplaçant | Notes |
|---|---|---|
| `BodyVelocity` | `LinearVelocity` | `VectorVelocity` + `MaxForce` ; choisir `RelativeTo` |
| `BodyPosition` | `AlignPosition` | `Position` + `MaxForce`/`Responsiveness` ; `Mode = OneAttachment` pour viser un point du monde |
| `BodyGyro` | `AlignOrientation` | `CFrame` + `MaxTorque`/`Responsiveness` |
| `BodyAngularVelocity` | `AngularVelocity` | `AngularVelocity` + `MaxTorque` |
| `BodyForce` | `VectorForce` | `Force` ; `RelativeTo` décide du repère |
| `BodyThrust` | `VectorForce` | Avec un `Attachment` décentré pour reproduire le couple |
| `RocketPropulsion` | `LinearVelocity` + `AlignOrientation` | Pas d'équivalent direct, à recomposer |

Pour un déplacement scripté sans physique, `TweenService` ou `PivotTo` valent
souvent mieux qu'une contrainte.

## 4. Animation

| À éviter | Remplaçant | Niveau |
|---|---|---|
| `Humanoid:LoadAnimation(anim)` | `humanoid.Animator:LoadAnimation(anim)` | Déprécié |
| `AnimationController:LoadAnimation()` | `animationController.Animator:LoadAnimation()` | Déprécié |
| `Humanoid.Torso` | `character.HumanoidRootPart` ou `humanoid.RootPart` | Déprécié |

Sur le serveur, l'`Animator` peut ne pas exister encore au moment où le
personnage apparaît : `humanoid:WaitForChild("Animator")`.

Charger la même `Animation` en boucle crée des `AnimationTrack` à chaque
appel. Charge une fois, garde la track, `:Play()` / `:Stop()` ensuite.

## 5. Input

| À éviter | Remplaçant | Niveau |
|---|---|---|
| `Mouse.KeyDown`, `Mouse.Button1Down` | `UserInputService.InputBegan` / `InputEnded` | Déprécié |
| `Player:GetMouse()` | `UserInputService:GetMouseLocation()`, `Camera:ViewportPointToRay()` | Découragé |
| Liaison manuelle de touche pour une action de jeu | `ContextActionService:BindAction()` | Découragé |

`UserInputService` est **client uniquement**. Toujours tester
`gameProcessedEvent` dans `InputBegan` pour ne pas réagir quand le joueur tape
dans un champ de texte.

`ContextActionService` gère gratuitement le bouton mobile et la manette.

## 6. Raycast et géométrie

| À éviter | Remplaçant | Niveau |
|---|---|---|
| `workspace:FindPartOnRay()` | `workspace:Raycast(origin, direction, params)` | Déprécié |
| `workspace:FindPartOnRayWithIgnoreList()` | `RaycastParams` avec `FilterType = Exclude` | Déprécié |
| `workspace:FindPartOnRayWithWhitelist()` | `RaycastParams` avec `FilterType = Include` | Déprécié |
| `Ray.new(origin, direction)` pour caster | `workspace:Raycast()` | Découragé |

Avec `Raycast`, la direction porte la longueur : `direction.Unit * range`. Un
`Vector3` non normalisé donne une portée surprenante.

Réutilise le même objet `RaycastParams` au lieu d'en créer un par frame.

## 7. Modèles et pivots

| À éviter | Remplaçant | Niveau |
|---|---|---|
| `Model:SetPrimaryPartCFrame()` | `Model:PivotTo()` | Déprécié |
| `Model:GetPrimaryPartCFrame()` | `Model:GetPivot()` | Déprécié |
| `Model:MoveTo()` pour un placement précis | `Model:PivotTo()` | Découragé |

`MoveTo` remonte le modèle pour éviter les collisions — utile pour poser un
personnage au sol, trompeur pour placer une porte.

`PivotTo` ne demande pas de `PrimaryPart` : il utilise le pivot du modèle.

## 8. Données et sauvegarde

| À éviter | Remplaçant | Pourquoi |
|---|---|---|
| `:SetAsync()` pour sauver un joueur | `:UpdateAsync()` | `SetAsync` écrase sans lire : deux serveurs, et la progression saute |
| Sauvegarder uniquement sur `PlayerRemoving` | `PlayerRemoving` **et** `game:BindToClose()` | Sans `BindToClose`, l'arrêt d'un serveur perd la dernière sauvegarde de tous les joueurs connectés |
| Un appel DataStore sans `pcall` | `pcall` + retry avec backoff | Les appels réseau échouent ; sans `pcall`, le script meurt et la suite ne s'exécute pas |
| Sauver à chaque changement | Sauvegarde périodique + aux moments clés | Les quotas DataStore sont par joueur et par minute |

`BindToClose` dispose d'un budget de 30 secondes ; il ne sert à rien d'y
lancer un travail plus long.

En Studio, les DataStores ne fonctionnent que si *Enable Studio Access to API
Services* est actif dans les paramètres du jeu.

## 9. Divers

| À éviter | Remplaçant | Niveau |
|---|---|---|
| Chat hérité (`Chat` service, scripts de `ChatModules`) | `TextChatService` | Déprécié |
| `Instance.new("Message")`, `Instance.new("Hint")` | Une `ScreenGui` | Déprécié |
| `math.random()` pour du gameplay | `Random.new()` | Découragé — flux indépendants, pas d'état global partagé |
| `BasePart.BrickColor` | `BasePart.Color` (`Color3`) | Découragé — palette continue |
| `ClickDetector` pour interagir avec un objet du monde | `ProximityPrompt` | Découragé — gère la distance, le clavier, le mobile et la manette |
| `Vector3.new(0, 0, 0)`, `Vector3.new(1, 1, 1)` | `Vector3.zero`, `Vector3.one` | Découragé |
| `:GetChildren()` puis boucle pour trouver un descendant | `:FindFirstChild(name, true)` | Découragé |
