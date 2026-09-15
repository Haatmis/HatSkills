# Animation de personnage — recettes et repères

## Sommaire

1. [Durées de départ](#1-durées-de-départ)
2. [Coup et frappe](#2-coup-et-frappe)
3. [Déplacement : marche, course](#3-déplacement--marche-course)
4. [Saut et réception](#4-saut-et-réception)
5. [Idle et attente](#5-idle-et-attente)
6. [Porter, tirer, pousser](#6-porter-tirer-pousser)
7. [Easings : lequel pour quoi](#7-easings--lequel-pour-quoi)
8. [Construire le KeyframeSequence](#8-construire-le-keyframesequence)

Lis la section du geste demandé, pas la fiche entière.

---

## 1. Durées de départ

Des points de départ, à ajuster en regardant. Aucun n'est une vérité.

| Geste | Durée | Boucle | Priority |
|---|---|---|---|
| Coup rapide | 0,3 – 0,5 s | non | `Action` |
| Coup lourd | 0,6 – 1,0 s | non | `Action` |
| Marche | 1,0 s | oui | `Movement` |
| Course | 0,6 – 0,8 s | oui | `Movement` |
| Saut (départ) | 0,2 – 0,3 s | non | `Action` |
| Réception | 0,3 – 0,5 s | non | `Action` |
| Idle | 3 – 6 s | oui | `Idle` |
| Emote | 1 – 3 s | selon | `Action` |

Une durée trop longue est le défaut le plus courant : en jeu, tout paraît plus
lent que dans l'éditeur, parce qu'on attend le résultat de l'action.

---

## 2. Coup et frappe

Trois temps, jamais réguliers :

| Temps | Part de la durée | Ce qui s'y passe |
|---|---|---|
| Anticipation | ~35 % | Recul du membre, vrille du buste dans le sens inverse |
| Impact | ~10 % | L'extrême, le plus court de tous |
| Retour | ~55 % | Reprise du repos, sans repasser exactement par les mêmes poses |

Le rapport impact/anticipation fait tout : un impact aussi long que
l'anticipation donne un geste mou.

**Le buste porte le coup, pas le bras.** Un coup animé uniquement au bras
paraît désarticulé. Fais tourner le torse (la taille) de quelques degrés dans
le sens du geste — c'est ce qui donne l'impression de masse.

**Le retour n'est pas l'anticipation à l'envers.** Reprendre exactement le
chemin inverse donne un effet d'élastique. Décale légèrement.

---

## 3. Déplacement : marche, course

Un cycle est symétrique en structure, pas en détail : quatre poses clés —
contact gauche, passage, contact droit, passage. La boucle doit refermer
exactement sur la première pose, sinon un à-coup apparaît à chaque tour.

**La hauteur du bassin varie.** Un cycle où le personnage reste à hauteur
constante glisse au lieu de marcher. Le point haut est au passage, le point bas
au contact.

**Les bras vont à l'inverse des jambes.** Bras gauche avec jambe droite. C'est
automatique chez un humain, et son absence se remarque immédiatement sans qu'on
sache dire pourquoi.

Pour une course, tout se resserre : amplitude plus grande, buste penché en
avant, durée plus courte.

---

## 4. Saut et réception

Le saut est une anticipation exagérée : accroupissement net, puis extension
complète. Sans l'accroupissement, le personnage paraît aspiré vers le haut.

La réception est l'inverse, et elle est **plus importante que le saut** pour la
sensation de poids : absorption par les genoux, puis retour. Une réception
instantanée donne un personnage en papier.

---

## 5. Idle et attente

Une idle doit être longue et de faible amplitude. Une idle courte devient un
tic visible au bout de vingt secondes, et l'œil l'attrape.

Respiration : légère montée/descente du buste, plus une dérive minuscule des
bras. Si tu peux décrire ce qui bouge en regardant, c'est trop.

La boucle doit être **invisible** : première et dernière pose identiques, et le
milieu pas exactement symétrique, sinon le retour se voit.

---

## 6. Porter, tirer, pousser

Le poids se lit dans le **contre-mouvement**, pas dans l'objet. Un personnage
qui porte quelque chose de lourd se penche en arrière, écarte les appuis,
et ses bras ne sont pas symétriques.

Pousser ou tirer : le buste est incliné dans le sens de l'effort, et les jambes
sont décalées. Un personnage vertical qui pousse ne pousse rien.

Pour un objet porté à deux mains devant soi : l'anticipation est dans le
**démarrage** — une fraction de seconde où l'objet ne bouge pas encore alors
que le corps s'est déjà engagé.

---

## 7. Easings : lequel pour quoi

| Situation | Style | Direction |
|---|---|---|
| Anticipation | `Quad` ou `Cubic` | `Out` |
| Impact, frappe | `Linear` ou `Quad` | `In` |
| Retour au repos | `Quad` | `InOut` |
| Cycle de marche | `Linear` | — |
| Réception, absorption | `Cubic` | `Out` |
| Idle | `Sine` | `InOut` |

Un cycle de marche en `InOut` marque un temps d'arrêt à chaque contact : c'est
le défaut typique d'une marche qui « boite » sans qu'on voie pourquoi.

---

## 8. Construire le KeyframeSequence

La structure exacte : `KeyframeSequence` → `Keyframe` (par `AddKeyframe`) →
`Pose` (par `AddPose`), et les poses s'imbriquent par `AddSubPose` **en suivant
la hiérarchie des parts du rig** — `HumanoidRootPart` à la racine.

Le `Name` d'une `Pose` est le nom exact de la **part**, pas du `Motor6D`. Un nom
qui ne correspond à rien n'émet aucune erreur : la pose est ignorée, et
l'animation paraît partiellement figée.

Propriétés du `KeyframeSequence` : `Loop`, `Priority`, `AuthoredHipHeight`.

Une `Pose` porte `CFrame` (relatif au repos de la jointure), `EasingStyle`,
`EasingDirection` et `Weight`.

**Chaque part animée doit avoir une pose dans chaque keyframe**, sinon
l'interpolation part de la dernière valeur connue et produit des dérives
difficiles à lire.
