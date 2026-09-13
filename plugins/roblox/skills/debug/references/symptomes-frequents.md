# Symptômes Roblox et leurs causes habituelles

À lire à l'étape 4, avant de former une hypothèse. Chaque symptôme liste ses
causes par ordre de fréquence réelle, et le test qui les départage.

Ces causes sont des pistes, pas des verdicts : elles servent à choisir quoi
reproduire, jamais à conclure sans reproduction.

## Sommaire

1. [Ça marche en Play Solo, pas à deux joueurs](#1-ça-marche-en-play-solo-pas-à-deux-joueurs)
2. [Ça marche au deuxième lancement, pas au premier](#2-ça-marche-au-deuxième-lancement-pas-au-premier)
3. [Rien ne se passe, aucune erreur](#3-rien-ne-se-passe-aucune-erreur)
4. [Valeur nil alors que l'objet existe](#4-valeur-nil-alors-que-lobjet-existe)
5. [Le client voit, le serveur non (ou l'inverse)](#5-le-client-voit-le-serveur-non-ou-linverse)
6. [L'UI ne réagit pas ou disparaît](#6-lui-ne-réagit-pas-ou-disparaît)
7. [Ça se déclenche plusieurs fois](#7-ça-se-déclenche-plusieurs-fois)
8. [Les données ne se sauvent pas](#8-les-données-ne-se-sauvent-pas)
9. [L'animation ne joue pas](#9-lanimation-ne-joue-pas)
10. [Ça marche en Studio, pas en jeu publié](#10-ça-marche-en-studio-pas-en-jeu-publié)
11. [Le joueur traverse ou tombe](#11-le-joueur-traverse-ou-tombe)
12. [Lenteurs, lag, mémoire qui monte](#12-lenteurs-lag-mémoire-qui-monte)

---

## 1. Ça marche en Play Solo, pas à deux joueurs

| Cause | Comment la départager |
|---|---|
| État serveur stocké dans une variable unique au lieu d'une table par joueur | Chercher une variable de module qui n'est pas indexée par `player` ou `UserId` |
| Logique dans un LocalScript : chaque client a son propre état, rien n'est partagé | Le comportement est-il correct pour celui qui agit et faux pour l'autre ? |
| `PlayerAdded` connecté trop tard : en Play Solo le joueur local existe déjà avant le script | Ajouter une boucle sur `Players:GetPlayers()` après la connexion |
| `workspace.CurrentCamera` ou `LocalPlayer` référencés côté serveur | N'existent pas sur le serveur |

Play Solo fait tourner client et serveur dans la même machine avec un seul
joueur : il masque précisément les bugs de frontière et de multiplicité.
**Start Server + 2 Players est le vrai test.**

## 2. Ça marche au deuxième lancement, pas au premier

Presque jamais aléatoire : c'est un ordre d'exécution.

| Cause | Comment la départager |
|---|---|
| `FindFirstChild` sur une instance pas encore répliquée | Remplacer par `WaitForChild` et voir si ça se stabilise |
| Le personnage n'existe pas encore au moment du script client | `player.CharacterAdded` plutôt que `player.Character` direct |
| Un ModuleScript s'initialise avant celui dont il dépend | Rendre la dépendance explicite dans `require` plutôt qu'implicite dans l'ordre |
| Un asset ou une image pas encore chargé | `ContentProvider:PreloadAsync()` |

`player.Character` peut être `nil` à tout moment — à la connexion, entre deux
morts. Le code client qui y touche doit gérer les deux cas.

## 3. Rien ne se passe, aucune erreur

| Cause | Comment la départager |
|---|---|
| `WaitForChild` sans timeout qui n'aboutit jamais : le thread est bloqué, sans erreur | Ajouter un `print` juste après, voir s'il s'affiche |
| Une erreur avalée par un `pcall` dont le résultat n'est pas lu | Lire et journaliser le second retour du `pcall` |
| L'événement n'est jamais connecté (script dans un conteneur qui ne s'exécute pas) | `print` en tête de script : s'affiche-t-il seulement ? |
| Script désactivé, ou placé là où il ne tourne pas (un `Script` dans `ReplicatedStorage`) | Vérifier le conteneur |
| Un `return` précoce sur une condition jamais vraie | Journaliser la condition |

Un `Script` ne s'exécute que dans `ServerScriptService`, `Workspace`,
`ServerStorage` (si déplacé) ; un `LocalScript` dans `StarterPlayerScripts`,
`StarterCharacterScripts`, `StarterGui`, ou le sac du joueur. Ailleurs, il ne
démarre pas — et personne ne prévient.

## 4. Valeur nil alors que l'objet existe

| Cause | Comment la départager |
|---|---|
| Réplication pas terminée : l'objet existe dans Studio mais pas encore chez le client | `WaitForChild` |
| Nom différent de ce qui est écrit (espace final, casse) | `print(obj:GetChildren())` et comparer |
| Objet détruit ailleurs entre-temps | Chercher les `:Destroy()` sur ce chemin |
| Instance créée côté client : elle n'existe pas côté serveur | De quel côté tourne le script ? |
| `:FindFirstChild()` non récursif alors que l'objet est plus profond | Second argument `true` |

## 5. Le client voit, le serveur non (ou l'inverse)

C'est le modèle de réplication, pas un bug.

| Ce qui se réplique | Ce qui ne se réplique pas |
|---|---|
| Serveur → client : instances et propriétés | Client → serveur : **rien**, sauf via un Remote |
| `ReplicatedStorage`, `Workspace` (selon le streaming) | `ServerStorage`, `ServerScriptService` |
| Le personnage du joueur (physique, sous conditions) | Les modifications d'UI locales |

Une instance créée par un LocalScript n'existe que chez ce client. Un
changement de propriété fait côté client n'atteint jamais le serveur.
L'exception : la physique des pièces dont le client a la propriété
(`SetNetworkOwner`) — source classique de désaccords.

## 6. L'UI ne réagit pas ou disparaît

| Cause | Comment la départager |
|---|---|
| `ResetOnSpawn` à `true` : la ScreenGui est recréée à chaque mort | Le bug survient-il après une mort ? |
| `Active` à `false`, ou un élément transparent au-dessus qui capte le clic | Test avec `ZIndex` et `Active` |
| L'UI est modifiée dans `StarterGui` au lieu de `PlayerGui` | `StarterGui` est le modèle, pas l'instance vivante |
| `Visible` d'un parent à `false` | Remonter la chaîne des parents |
| `IgnoreGuiInset`, ancrage, ou `UIListLayout` qui repositionne | Inspecter dans Studio en Play |

## 7. Ça se déclenche plusieurs fois

| Cause | Comment la départager |
|---|---|
| Pas de debounce sur `Touched` | `Touched` se déclenche pour **chaque pièce** du personnage, et plusieurs fois par contact |
| Connexion créée dans une boucle ou un événement : elle s'empile | Compter les connexions ; déconnecter avant de reconnecter |
| Connexions jamais déconnectées à la mort du joueur | Garder les connexions et les `:Disconnect()` au `CharacterRemoving` |
| `ClickDetector` et une autre entrée qui font la même chose | Journaliser la source |

## 8. Les données ne se sauvent pas

| Cause | Comment la départager |
|---|---|
| *Enable Studio Access to API Services* désactivé | Les DataStores ne marchent pas du tout en Studio sans ça |
| Erreur réseau avalée faute de `pcall` lu | Journaliser le message d'erreur du `pcall` |
| Pas de `game:BindToClose()` : l'arrêt du serveur perd la dernière écriture | Le bug survient-il surtout à la fermeture ? |
| `:SetAsync()` qui écrase une écriture concurrente | Passer à `:UpdateAsync()` |
| Quota dépassé (trop d'écritures par joueur et par minute) | Espacer, et journaliser les échecs |
| Clé différente entre l'écriture et la lecture | Comparer les deux littéralement |

## 9. L'animation ne joue pas

| Cause | Comment la départager |
|---|---|
| Chargée sur le `Humanoid` au lieu de l'`Animator` | API dépréciée : voir la table des dépréciées |
| L'animation n'appartient pas au compte ou au groupe propriétaire du jeu | Erreur de permission dans l'Output |
| `AnimationPriority` trop basse : l'animation par défaut passe devant | Monter en `Action` |
| `AnimationTrack` rechargée à chaque appel : la précédente tourne encore | Charger une fois, garder la track |
| `Animator` pas encore créé au moment du chargement | `humanoid:WaitForChild("Animator")` |

## 10. Ça marche en Studio, pas en jeu publié

| Cause | Comment la départager |
|---|---|
| Latence réelle : ce qui était instantané en local prend du temps | Ajouter des `WaitForChild` et tester à distance |
| Requêtes HTTP désactivées dans les paramètres du jeu | Erreur explicite dans l'Output serveur |
| API réservée à Studio, ou branche `RunService:IsStudio()` oubliée | Chercher les `IsStudio` |
| Version publiée plus ancienne que le Studio local | Republier avant de conclure |
| `StreamingEnabled` : des parties du monde n'existent pas encore chez le client | Voir la section suivante |

## 11. Le joueur traverse ou tombe

| Cause | Comment la départager |
|---|---|
| `CanCollide` à `false`, ou remis à `false` par un script | Inspecter la pièce en Play |
| `Anchored` à `false` sur une pièce de décor | Elle tombe au premier contact |
| `StreamingEnabled` : le sol n'est pas encore chargé chez ce client | `player:RequestStreamAmountAsync()`, ou `ModelStreamingMode` |
| Téléportation par `CFrame` sur le `HumanoidRootPart` sans tenir compte de la hauteur | Utiliser `PivotTo` sur le personnage entier |
| `CollisionGroup` mal configuré | Vérifier la matrice dans Studio |

## 12. Lenteurs, lag, mémoire qui monte

| Cause | Comment la départager |
|---|---|
| Connexions jamais déconnectées (fuite classique) | Compter les connexions au fil du temps |
| Boucle par frame qui fait un travail lourd | `RunService` : ce qui peut être événementiel doit l'être |
| Instances créées sans jamais être détruites | Compter les enfants de `Workspace` en jeu |
| `WaitForChild` sans timeout dans une boucle | Chaque appel bloque son thread |
| Remote appelé à chaque frame | Regrouper, ou envoyer seulement au changement |
| Trop de pièces non ancrées simulées | Ancrer le décor |

Le Developer Console (F9 en jeu) et le MicroProfiler montrent ce que la
lecture du code ne montre pas.
