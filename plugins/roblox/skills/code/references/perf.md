# Performance Roblox : ce qui coûte, et quand s'en occuper

À lire **avant** d'écrire quelque chose de chaud — une boucle par frame, un
système qui crée des instances en continu, quelque chose qui tourne pour tous
les joueurs — ou quand la performance est explicitement le sujet.

## Sommaire

1. [Les deux performances](#1-les-deux-performances)
2. [Mesurer avant de toucher](#2-mesurer-avant-de-toucher)
3. [Les coûts réels, par ordre](#3-les-coûts-réels-par-ordre)
4. [Le pooling : quand et comment](#4-le-pooling--quand-et-comment)
5. [Seuils indicatifs](#5-seuils-indicatifs)
6. [Ce qui ne vaut pas le détour](#6-ce-qui-ne-vaut-pas-le-détour)

---

## 1. Les deux performances

| | Structurelle | Micro |
|---|---|---|
| **C'est quoi** | Combien d'appels, combien d'instances, qui fait le travail | Faire la même chose un peu plus vite |
| **Quand** | À l'écriture | Après mesure, jamais avant |
| **Se rattrape** | Non — ça se réécrit | Oui, en dix minutes |
| **Exemple** | Un Remote par frame au lieu d'un par changement | `ipairs` plutôt que `pairs` |

Tout ce document parle de la première. La seconde attend le profileur.

La question à se poser en écrivant n'est jamais « est-ce rapide ? » mais
**« combien de fois ça va tourner, et pour combien de joueurs ? »**. Un code
appelé une fois au démarrage n'a aucun enjeu ; le même appelé par frame et par
joueur en a un énorme.

## 2. Mesurer avant de toucher

| Outil | Ce qu'il montre |
|---|---|
| **Developer Console** (F9 en jeu) | Scripts les plus coûteux, mémoire, réseau, erreurs réelles |
| **MicroProfiler** (Ctrl+F6 en Studio) | Où part chaque frame, image par image |
| `os.clock()` autour d'un bloc | Le coût d'une fonction précise, en secondes |
| **Onglet Network** de la console | Le trafic réel des Remotes |

Le piège classique : optimiser ce qu'on croit lent. Le coût dominant d'un jeu
Roblox est rarement dans le Luau — il est dans le nombre d'instances, la
réplication et le rendu.

## 3. Les coûts réels, par ordre

### Les boucles par frame

`RunService.PreRender` (client) bloque le rendu : ce qui y traîne fait chuter
les images par seconde directement. `PostSimulation` est plus tolérant mais
tourne aussi ~60 fois par seconde.

Avant d'écrire une boucle par frame, cherche l'événement qui ferait le même
travail : `Changed`, `GetPropertyChangedSignal`, `Touched`,
`CollectionService:GetInstanceAddedSignal`. Une surveillance d'état est presque
toujours un signal déguisé.

Si la boucle est vraiment nécessaire, elle n'a pas besoin de tourner à 60 Hz :
un accumulateur qui ne fait le travail que toutes les 0,1 s divise le coût par
six sans que personne ne le voie.

### Le réseau

Chaque appel de Remote a un coût fixe, indépendant de la charge utile. Cent
petits appels coûtent bien plus que un gros.

| À éviter | À faire |
|---|---|
| `FireServer` à chaque frame | Envoyer au changement, ou grouper sur un intervalle |
| `FireAllClients` pour un effet local | `FireClient` aux seuls concernés |
| Envoyer un état complet | Envoyer le delta |
| Un Remote par objet | Un Remote avec une table d'objets |

Et la règle qui sert deux fois : **le client envoie une intention, pas une
donnée.** C'est sécurisant, et c'est plus léger.

### Les instances

Créer et détruire en continu use le ramasse-miettes et fait grimper la mémoire.
Un `Instance.new` par tir de mitrailleuse est un problème ; le même par
ouverture de menu n'en est pas un.

Poser `.Parent` **en dernier**, une fois les propriétés réglées : sinon
l'instance est répliquée puis modifiée, ce qui double le trafic et fait
clignoter l'objet une frame.

### La réplication

Tout ce qui vit dans `Workspace` ou `ReplicatedStorage` est envoyé à chaque
client qui rejoint. Ce qui n'a pas besoin d'être vu va dans `ServerStorage` —
c'est à la fois plus léger et plus sûr.

`StreamingEnabled` fait que des parties du monde n'existent pas encore chez un
client donné. C'est un gain massif sur les grandes cartes, mais le code client
doit alors gérer l'absence : `WaitForChild`, et pas de supposition sur ce qui
est chargé.

### Le rendu

Le coût dominant n'est pas le nombre de parts mais la **surface transparente
empilée** et le nombre de sources de lumière. Détail et leviers dans le skill
`vfx` (`skills/vfx/references/boite-a-outils.md` § Performance).

### La physique

Seules les pièces **non ancrées** sont simulées. Ancrer le décor est le levier
le plus rentable qui existe, et il est gratuit.

`CanCollide`, `CanTouch` et `CanQuery` à `false` sur ce qui n'en a pas besoin
retirent trois calculs par pièce et par frame.

### L'audio

Un `Instance.new("Sound")` créé au moment de jouer démarre avec un retard fixe
— mesuré à 0,36 s, identique sur deux fichiers de durées différentes, donc
imputable au chargement et non au contenu. Ça s'entend comme un fichier mal
découpé, et on cherche le défaut dans l'export.

`ContentProvider:PreloadAsync` au démarrage, et une instance `Sound` réutilisée
plutôt qu'une par déclenchement.

### Les DataStore

Les quotas sont par joueur et par minute. Sauvegarder à chaque changement les
épuise. Sauvegarde périodiquement et aux moments clés, jamais à chaque
variation d'une valeur.

## 4. Le pooling : quand et comment

Réutiliser plutôt que créer vaut le détour quand **le même type d'objet est
créé plus de quelques fois par seconde** : projectiles, impacts, lignes d'une
liste qui défile.

Le principe : une réserve d'objets inactifs, `Parent = nil` ou rangés hors
champ. On en prend un, on le règle, on le rend. Ce qui est rendu est remis
dans son état neutre — sinon le suivant hérite des propriétés du précédent,
et c'est un bug qui se cherche longtemps.

En dessous de ce rythme, le pooling est de la complexité gratuite : un menu
ouvert dix fois par partie n'a aucun besoin d'une réserve.

## 5. Seuils indicatifs

Des ordres de grandeur, pas des lois. À vérifier sur ta machine cible — et la
machine cible d'un jeu Roblox est un téléphone moyen, pas ton PC.

| Repère | Ordre de grandeur |
|---|---|
| Travail dans une boucle par frame | < 1 ms, sinon découper ou espacer |
| Remotes par joueur | quelques-uns par seconde, pas par frame |
| Parts non ancrées simulées | quelques centaines, pas des milliers |
| Instances dans `Workspace` | le moins possible ; surveiller la croissance |
| Connexions d'événements | constante dans le temps — si ça monte, c'est une fuite |

Le dernier est le plus important : une quantité qui **croît** est toujours un
bug, quel que soit son niveau de départ.

## 6. Ce qui ne vaut pas le détour

Sans mesure préalable, ces gestes coûtent en lisibilité pour un gain
invisible :

- Mettre un service dans une variable locale « pour aller plus vite »
- Choisir `ipairs` plutôt que `pairs` par réflexe
- Dérouler une boucle à la main
- Remplacer une fonction claire par une ligne illisible
- Fusionner des modules pour « éviter des `require` »

Si l'un d'eux est vraiment le goulot d'étranglement, le profileur te le dira —
et alors ce ne sera plus une micro-optimisation, ce sera une correction.
