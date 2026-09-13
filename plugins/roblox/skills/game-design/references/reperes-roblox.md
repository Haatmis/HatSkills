# Repères chiffrés pour le game design Roblox

Deux natures de valeurs ici, à ne pas confondre :

- **Défauts de la plateforme** — ce que Roblox applique si tu ne changes rien.
  Ce sont des faits.
- **Fourchettes usuelles** — ce qu'on observe couramment dans les jeux du
  genre. Ce sont des points de départ à tester en jeu, pas des vérités. Un
  chiffre juste est celui qui fait un bon ressenti dans *ton* jeu.

## Sommaire

1. [Défauts du personnage](#1-défauts-du-personnage)
2. [Échelle et distances](#2-échelle-et-distances)
3. [Combat](#3-combat)
4. [Temporalité et ressenti](#4-temporalité-et-ressenti)
5. [Économie et progression](#5-économie-et-progression)
6. [Monétisation](#6-monétisation)
7. [Rétention](#7-rétention)

---

## 1. Défauts du personnage

| Propriété | Défaut | Note |
|---|---|---|
| `Humanoid.MaxHealth` | 100 | Base de tout calcul de dégâts |
| `Humanoid.WalkSpeed` | 16 | Studs par seconde |
| `Humanoid.JumpPower` | 50 | Quand `UseJumpPower` est vrai |
| `Humanoid.JumpHeight` | 7.2 | Quand `UseJumpPower` est faux |
| `Workspace.Gravity` | 196.2 | Modifier change tout le ressenti du saut |
| Rig | R6 ou R15 | Réglé dans Game Settings → Avatar. **Une animation R15 ne joue pas sur un rig R6** : la spec doit dire lequel |

Toucher à `WalkSpeed` ou à `Gravity` change le ressenti de *tout* le jeu, pas
seulement de la feature en cours. À signaler comme un risque.

## 2. Échelle et distances

| Repère | Valeur approximative |
|---|---|
| Hauteur d'un personnage R15 | ~5 studs |
| Largeur d'épaules | ~2 studs |
| Un pas de course en 1 s | 16 studs |
| Hauteur de saut par défaut | ~7 studs |
| Marche typique d'escalier | 1 à 2 studs |

Utile pour chiffrer une portée : « 10 studs » est concret quand on sait que
c'est deux fois la taille d'un personnage.

## 3. Combat

Fourchettes usuelles, à tester :

| Paramètre | Fourchette | Ce qui la gouverne |
|---|---|---|
| Temps pour tuer (TTK) | 2 à 5 s | Trop court : frustrant, on meurt sans comprendre. Trop long : mou |
| Coups pour tuer | 3 à 6 | À 100 PV, ça donne 17 à 33 dégâts par coup |
| Portée de mêlée | 8 à 14 studs | Plus court paraît injuste avec la latence |
| Cooldown d'attaque | 0,4 à 0,8 s | En dessous, ça devient du matraquage |
| Fenêtre d'invulnérabilité au spawn | 2 à 5 s | Sans ça, le camping de spawn vide le serveur |

La latence est une contrainte de design, pas seulement technique : sur un
serveur réel, un joueur voit sa cible là où elle était il y a 50–150 ms. Une
portée trop juste rend le combat frustrant sans que personne comprenne
pourquoi.

## 4. Temporalité et ressenti

| Repère | Valeur | Note |
|---|---|---|
| Retour visuel après une action | < 100 ms | Au-delà, l'action semble ne pas avoir marché |
| Durée d'animation d'attaque | 0,3 à 0,6 s | Doit finir avant le cooldown, sinon ça coupe |
| Tween d'interface | 0,15 à 0,3 s | Plus long paraît lent |
| Temps avant première action d'un nouveau joueur | < 30 s | Le taux d'abandon monte vite au-delà |

Le retour immédiat peut être client (l'animation part tout de suite) pendant
que le serveur valide. C'est un choix de design assumé : si le serveur refuse,
il faut prévoir ce que voit le joueur.

## 5. Économie et progression

| Repère | Fourchette | Note |
|---|---|---|
| Première récompense | < 1 min de jeu | Prouve au joueur que la boucle existe |
| Premier achat significatif | 5 à 15 min | Trop loin, il part avant d'y goûter |
| Facteur entre deux paliers d'upgrade | ×1,3 à ×2 | Au-delà, le mur devient décourageant |
| Durée de session visée | 10 à 20 min | Sur Roblox, les sessions sont courtes |

Deux pièges d'économie fréquents :

- **La boucle de farm non intentionnelle** : une action répétitive rapporte
  plus que le contenu conçu pour ça. Cherche toujours quel est le meilleur
  taux de gain par minute, et vérifie que c'est celui que tu veux.
- **L'inflation** : une source de monnaie ajoutée sans toucher aux prix dévalue
  toute la progression existante.

## 6. Monétisation

| Repère | Valeur | Note |
|---|---|---|
| Part reversée au développeur | 70 % | Sur les gamepass et dev products |
| Prix d'entrée courant d'un gamepass | 49 à 199 R$ | L'achat d'impulsion |
| Gamepass « premium » | 400 à 999 R$ | Doit apporter un vrai confort durable |
| Dev product consommable | 25 à 100 R$ | Monnaie, boost, relance |

Ce qui monétise sainement : cosmétique, confort (inventaire plus grand, voyage
rapide), accélération d'un contenu **déjà accessible gratuitement**.

Ce qu'il faut signaler à l'utilisateur :

- Un mur de progression dont la seule issue raisonnable est payante.
- Une loot box dont les probabilités ne sont pas affichées.
- Un avantage de combat vendu, dans un jeu PvP — c'est du pay-to-win, et ça
  fait fuir les joueurs non payants, donc aussi les payants.
- Une pression sociale artificielle (compte à rebours, rareté fausse).

Le public est jeune : une mécanique conçue pour exploiter l'impatience pose un
problème qu'il faut nommer, pas contourner.

## 7. Rétention

Les trois moments qui décident si un joueur reste :

| Moment | Enjeu |
|---|---|
| Les 30 premières secondes | A-t-il compris quoi faire, et l'a-t-il fait ? |
| La première session | A-t-il vu la boucle complète au moins une fois ? |
| Le retour du lendemain | Sait-il ce qui l'attend s'il revient ? |

Une feature qui n'agit sur aucun des trois est peut-être sympathique, mais elle
ne fera pas grandir le jeu. Ça vaut d'être dit quand c'est le cas.
