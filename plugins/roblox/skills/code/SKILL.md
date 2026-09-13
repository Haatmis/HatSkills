---
name: code
description: >
  Écrit du code Luau pour un jeu Roblox — feature, module, système, outil ou
  squelette de projet — en vanilla strict, puis le vérifie dans Studio via le
  MCP avant de le rendre. Utilise ce skill dès que l'utilisateur demande du
  code Roblox ou Luau : « fais-moi un système de… », « ajoute un
  RemoteEvent », « comment je fais pour que le joueur… », « crée un
  ModuleScript », « un script qui… », un leaderstats, une sauvegarde
  DataStore, un inventaire, une boucle de jeu, une UI — même s'il ne dit ni
  « Luau » ni « Roblox », et même si la demande ressemble à une simple
  question. N'utilise pas ce skill quand il colle une erreur, un stack trace
  ou du code qui ne marche pas et demande pourquoi : c'est un diagnostic, pas
  de l'écriture (voir debug).
---

# Écrire du code Roblox

## Situation

L'utilisateur veut du code qui tourne dans son jeu. Le piège n'est pas la
syntaxe Luau, c'est que les modèles ont appris sur dix ans de forums Roblox :
ils ressortent des API dépréciées et mettent côté client de la logique qui
n'a rien à y faire. Le code « qui a l'air bon » coûte plus cher que pas de
code du tout, parce qu'il faut le débusquer ensuite.

Deux garde-fous : le contexte figé ci-dessous, et la vérification réelle dans
Studio avant de rendre quoi que ce soit.

## Contexte figé

**Vanilla strict.** Aucune dépendance externe : ni Knit, ni Fusion, ni Roact,
ni ProfileService, ni aucun paquet Wally. Tout à la main avec l'API Roblox. Si
une lib rendrait vraiment service, dis-le en une phrase — ne l'introduis pas.

**Langue.** Code, identifiants et commentaires en anglais. Les explications
autour du code, en français.

**Nommage** (style Roblox officiel, celui de l'API elle-même) :
- `PascalCase` — ModuleScripts, fonctions publiques, méthodes, constantes exportées
- `camelCase` — variables et fonctions locales
- `_prefixe` — membres privés d'un module
- `SCREAMING_SNAKE` — constantes locales de configuration

**Typage.** `--!strict` en tête de tout ModuleScript ; `--!nonstrict` sur les
Scripts et LocalScripts. Raison : les modules sont les frontières réutilisées
partout, c'est là que les types rapportent ; les scripts d'entrée manipulent
beaucoup d'instances dont les types sont mal inférés, et le strict y produit
surtout du bruit. Type les signatures publiques et les tables de données,
jamais par `any` implicite.

**Serveur par défaut.** Toute logique de jeu vit sur le serveur : économie,
statistiques, inventaire, progression, dégâts, validation. Le client affiche
et envoie des intentions, rien de plus. Un client est toujours supposé hostile
— un exploiteur contrôle entièrement ce qui tourne chez lui.

Ce qui découle de cette règle, à appliquer sans y penser :
- Tout `RemoteEvent`/`RemoteFunction` valide ses arguments côté serveur :
  type, bornes, et **droit de faire l'action** (le joueur possède-t-il
  vraiment l'objet ? est-il assez près ? le cooldown est-il écoulé ?).
- Jamais de prix, de quantité ou d'identifiant d'objet envoyé par le client
  comme source de vérité. Le client envoie *quoi* il veut faire, le serveur
  décide *si* et *combien*.
- Un `RemoteFunction` appelé du serveur vers le client peut ne jamais
  répondre : préfère un `RemoteEvent` dans ce sens.
- Les données sensibles ne sont pas dans `ReplicatedStorage`.

**Régime prototype ou production.** Demande-le si ce n'est pas clair, ou
déduis-le. En prototype, signale les manques de sécurité sans bloquer. Dès que
le jeu est publié, tout ce qui touche à l'économie, aux données joueur ou aux
Remotes doit être correct avant livraison — pas « à durcir plus tard ».

**Arborescence** (fixée pour tous les projets) :

```
src/server/    → ServerScriptService/Server
src/client/    → StarterPlayer/StarterPlayerScripts/Client
src/shared/    → ReplicatedStorage/Shared
```

Conventions de fichiers Rojo : `Nom.luau` → ModuleScript, `Nom.server.luau` →
Script, `Nom.client.luau` → LocalScript, `init.luau` → le module d'un dossier.

**API dépréciées — les six qui reviennent tout le temps :**

| Ne jamais écrire | Écrire à la place |
|---|---|
| `wait()`, `spawn()`, `delay()` | `task.wait()`, `task.spawn()`, `task.defer()`, `task.delay()` |
| `:connect()`, `:wait()` (minuscule) | `:Connect()`, `:Wait()` |
| `:remove()` | `:Destroy()` |
| `Instance.new("Part", parent)` | `Instance.new("Part")` puis `.Parent` **en dernier**, une fois les propriétés posées |
| `Humanoid:LoadAnimation()` | `humanoid.Animator:LoadAnimation()` |
| `BodyVelocity`, `BodyPosition`, `BodyGyro` | `LinearVelocity`, `AlignPosition`, `AlignOrientation` |

Avant d'écrire du mouvement, de l'animation, du timing, de l'input ou de
l'accès aux services, lis `references/api-obsolete.md` : la table complète y
est, avec le remplaçant exact et ce qui change dans l'usage.

## Procédure

1. **Repère le mode.** Un `default.project.json` ou un dossier `src/` →
   projet Rojo : tu écris et modifies les fichiers directement. Sinon → mode
   MCP/Studio : tu crées les instances via le MCP et tu donnes les chemins.
2. **Lis avant d'écrire.** En projet Rojo, parcours `src/` pour relever les
   modules existants, le style en place et ce qui est déjà résolu. N'introduis
   pas un deuxième système là où il y en a déjà un. En mode MCP, inspecte
   l'arbre du jeu.
3. **Situe la frontière client/serveur** avant la première ligne : qu'est-ce
   qui tourne où, et qu'est-ce qui transite. Si la réponse n'est pas nette, la
   suite sera fausse.
4. **Écris**, en respectant le contexte figé ci-dessus.
5. **Vérifie dans Studio via le MCP — toujours, avant de rendre.** Exécute le
   code ou le module et lis l'Output. Une erreur, un avertissement, un nom
   d'API qui n'existe pas : tu corriges et tu relances. Ne rends jamais du
   code non exécuté en disant qu'il devrait marcher.
   Si le MCP n'est pas disponible, dis-le explicitement en une ligne au lieu
   de faire comme si la vérification avait eu lieu.
6. **Relis en adversaire** : qu'est-ce qu'un exploiteur peut envoyer dans ce
   Remote ? Que se passe-t-il si le joueur part au milieu ? Si l'instance
   n'existe pas encore ? Si deux appels arrivent en même temps ?
7. **Rends** au format ci-dessous.

## Apprendre de la session

Trois signaux, et rien d'autre, valent une entrée au journal :

| Signal | `--type` |
|---|---|
| L'utilisateur te corrige, ou réécrit ce que tu as produit | `correction` |
| La vérification Studio révèle une erreur que tu avais commise | `studio-error` |
| L'utilisateur re-précise un contexte que ce skill aurait dû porter | `re-precision` |

Enregistre la leçon sur le moment, formulée comme une règle et pas comme un
récit — « Toujours X » plutôt que « j'ai oublié X » :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" add \
  --skill code --type correction \
  --lesson "Toujours …" --context "ce qui se passait, une ligne"
```

Rien à signaler : ne lance pas la commande. Si elle répond que le seuil est
atteint, ajoute une ligne en fin de réponse pour dire que `/roblox:affiner`
est disponible — puis reprends. N'affine jamais de toi-même : modifier un
skill est une décision de l'utilisateur.

## Format de sortie

En mode Rojo, modifie les fichiers puis rends **seulement** le compte rendu.
En mode MCP, crée les instances puis rends le même compte rendu.

```markdown
## Ce que j'ai fait
<2-4 lignes. Ce qui a été ajouté ou modifié, et le choix structurant s'il y
en a un.>

## Fichiers / instances
| Chemin | Type | Rôle |
|---|---|---|
| `src/server/Systems/Inventory.luau` → `ServerScriptService/Server/Systems/Inventory` | ModuleScript | … |

## Client / serveur
- **Serveur** : <ce qu'il détient et décide>
- **Client** : <ce qu'il affiche et envoie>
- **Transite** : <Remote, sa charge utile, et ce que le serveur en valide>

## Sécurité
- <Ce qu'un exploiteur tenterait> → <ce qui l'en empêche>
<Ou : « Rien de sensible ici : aucun Remote, aucune donnée joueur. »>

## Vérifié dans Studio
<Ce qui a été exécuté et ce que l'Output a donné.>

## À tester toi-même
1. <Étape concrète : Play Solo, ou Start Server + 2 joueurs, et ce qu'on doit voir.>
```

N'explique que les points non évidents : un choix qui pourrait surprendre, un
piège évité. Pas de cours sur ce qui se lit dans le code.

## Exemple

Entrée :
```
Fais-moi un système de monnaie, avec sauvegarde
```

Ce que ça donne :

- `src/shared/Config/Economy.luau` (ModuleScript, `--!strict`) — les valeurs de
  configuration, partagées pour que l'UI affiche les mêmes chiffres que le
  serveur applique.
- `src/server/Systems/Currency.luau` (ModuleScript) — détient les soldes,
  expose `Currency.Add(player, amount, reason)` et `Currency.TrySpend(player, amount)`.
  `TrySpend` retourne `false` si le solde est insuffisant plutôt que de laisser
  passer un négatif.
- `src/server/Systems/DataStore.luau` (ModuleScript) — charge au `PlayerAdded`,
  sauve au `PlayerRemoving` **et** au `game:BindToClose()`, avec `:UpdateAsync()`
  plutôt que `:SetAsync()` pour ne pas écraser une écriture concurrente, et un
  retry avec backoff.
- `src/client/UI/CurrencyDisplay.client.luau` (LocalScript) — écoute et affiche.

La section **Sécurité** dira : le client ne reçoit jamais `Currency.Add` ; il
n'existe aucun Remote qui crédite. Le seul Remote va dans l'autre sens
(« je veux acheter l'objet X »), et le serveur décide du prix depuis
`Config/Economy` — pas depuis ce que le client annonce.

## Pièges

- **Rendre du code non exécuté.** Le MCP est là : s'en passer, c'est retomber
  sur du code « plausible ». Une API qui n'existe pas ne se voit pas à la
  relecture, elle se voit dans l'Output.
- **Mettre la logique côté client parce que c'est plus simple.** Ça marche en
  Play Solo et ça se fait vider en production. Si tu es tenté, c'est
  généralement qu'il manque un Remote.
- **Faire confiance aux arguments d'un Remote.** Le type, les bornes *et* le
  droit d'agir. Vérifier le type seul ne protège de rien : un exploiteur
  envoie des nombres parfaitement valides.
- **`:SetAsync()` pour sauvegarder un joueur.** Deux serveurs, une session
  fantôme, et la progression saute. `:UpdateAsync()` lit puis écrit dans la
  même opération.
- **Oublier `game:BindToClose()`.** Sans lui, l'arrêt d'un serveur perd la
  dernière sauvegarde de tous les joueurs encore connectés.
- **Poser `.Parent` avant les propriétés.** L'instance est répliquée puis
  modifiée : coût réseau inutile et clignotement visible.
- **Réinventer un système déjà présent dans `src/`.** L'étape 2 de la
  procédure existe pour ça.

## Avant de rendre

- [ ] Exécuté dans Studio via le MCP, Output lu et propre — ou absence du MCP
      signalée explicitement.
- [ ] Aucune API de la table des dépréciées.
- [ ] `--!strict` sur les ModuleScripts, `--!nonstrict` sur les scripts.
- [ ] Aucune dépendance externe introduite.
- [ ] Chaque Remote valide type, bornes et droit d'agir côté serveur.
- [ ] Aucune logique de jeu, d'économie ou de données sur le client.
- [ ] Chemins d'instance complets donnés pour chaque fichier.
- [ ] Section Sécurité remplie, même quand la réponse est « rien de sensible ».
- [ ] Étapes de test dans Studio concrètes, pas « teste que ça marche ».
- [ ] Leçon enregistrée au journal si tu as été corrigé, si Studio a révélé
      une erreur de ta part, ou si un contexte a dû t'être re-précisé.
