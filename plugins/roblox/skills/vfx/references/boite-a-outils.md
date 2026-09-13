# Boîte à outils VFX Roblox

À lire avant de choisir une instance.

## Sommaire

1. [Quelle instance pour quel effet](#1-quelle-instance-pour-quel-effet)
2. [ParticleEmitter : les propriétés qui comptent](#2-particleemitter--les-propriétés-qui-comptent)
3. [Beam et Trail](#3-beam-et-trail)
4. [Highlight et lumières](#4-highlight-et-lumières)
5. [Recettes de base](#5-recettes-de-base)
6. [Performance](#6-performance)
7. [Pièges qui ne lèvent aucune erreur](#7-pièges-qui-ne-lèvent-aucune-erreur)

---

## 1. Quelle instance pour quel effet

| L'effet | L'instance | Pourquoi |
|---|---|---|
| Impact, éclaboussure, gerbe ponctuelle | `ParticleEmitter` + `:Emit(n)` | Salve nette, cadrée dans le temps |
| Feu, fumée, aura continue | `ParticleEmitter` + `Rate` | Flux permanent tant qu'il est actif |
| Rayon, lien, éclair entre deux points | `Beam` | Suit deux `Attachment`, se courbe |
| Sillage d'épée, traînée de projectile | `Trail` | Suit le mouvement réel de l'objet |
| Mettre un objet en évidence | `Highlight` | Contour et remplissage, traverse les murs si voulu |
| Halo lumineux localisé | `PointLight` / `SpotLight` | Éclaire vraiment la scène autour |
| Flash plein écran | `ScreenGui` + `Frame` | Client uniquement, pas un VFX 3D |

`Sparkles`, `Smoke` et `Fire` existent encore mais sont figés et datés : un
`ParticleEmitter` fait mieux et se règle. `Explosion` est un objet de
*gameplay* — voir la section 7.

## 2. ParticleEmitter : les propriétés qui comptent

Le parent doit être une `BasePart` ou un `Attachment`. Un `Attachment`
temporaire est presque toujours le bon choix : il se place au stud près et se
détruit proprement.

**La forme du temps**

| Propriété | Type | Rôle |
|---|---|---|
| `Lifetime` | `NumberRange` | Durée de vie des particules. Le max gouverne le nettoyage |
| `Rate` | nombre | Particules par seconde. `0` pour un effet en salve |
| `:Emit(n)` | méthode | Envoie `n` particules d'un coup. La base de tout impact |
| `Enabled` | booléen | Coupe l'émission, **sans** détruire les particules vivantes |

**La forme de l'espace**

| Propriété | Rôle |
|---|---|
| `Speed` (`NumberRange`) | Vitesse initiale |
| `SpreadAngle` (`Vector2`) | Ouverture du cône. Large = gerbe, nul = jet |
| `EmissionDirection` | Face d'émission du parent |
| `Acceleration` (`Vector3`) | Gravité locale. Vers le bas, les éclats retombent — c'est ce détail qui distingue un impact de « des particules » |
| `Drag` | Freinage. Monter pour un effet qui s'essouffle |
| `Shape`, `ShapeStyle`, `ShapeInOut` | Volume d'émission : boîte, sphère, cylindre, disque |

**L'apparence**

| Propriété | Rôle |
|---|---|
| `Color` (`ColorSequence`) | Couleur dans le temps |
| `Size` (`NumberSequence`) | Taille dans le temps. Démarrer petit, gonfler, retomber à zéro évite la coupure sèche |
| `Transparency` (`NumberSequence`) | Finir à `1` pour que la particule s'éteigne au lieu de disparaître |
| `LightEmission` (0–1) | Rendu additif : monte pour le feu, l'énergie, la magie |
| `LightInfluence` (0–1) | `0` = ignore la lumière ambiante, la particule garde sa couleur de nuit |
| `Rotation`, `RotSpeed` | Rotation initiale et vitesse de rotation |
| `ZOffset` | Décale le rendu vers ou loin de la caméra, pour régler une superposition |
| `Orientation` | `FacingCamera` par défaut ; `VelocityParallel` pour des éclats étirés dans leur sens de déplacement |
| `Texture` | Vide = texture par défaut. **Jamais d'ID inventé** |

Deux règles de séquence qui changent tout le ressenti :

- `Transparency` doit finir à `1`. Sinon la particule se coupe net.
- `Size` qui part de `0`, gonfle, puis retombe à `0` donne une apparition et
  une extinction douces sans rien coder.

## 3. Beam et Trail

**Les deux exigent deux `Attachment`.** Sans `Attachment0` et `Attachment1`,
ils ne rendent rien — sans erreur ni avertissement. C'est la première chose à
vérifier quand « ça ne s'affiche pas ».

**Beam** relie deux points fixes.

| Propriété | Rôle |
|---|---|
| `Width0`, `Width1` | Largeur à chaque extrémité |
| `CurveSize0`, `CurveSize1` | Courbure. Non nuls = arc au lieu d'une ligne droite |
| `Segments` | Finesse de la courbe. Inutile de monter si la courbure est nulle |
| `TextureSpeed`, `TextureLength`, `TextureMode` | Défilement de la texture, pour un flux qui bouge |
| `FaceCamera` | À activer pour que le faisceau reste visible sous tous les angles |

**Trail** suit le mouvement réel. Les deux `Attachment` définissent sa largeur :
placés aux deux bords de la lame, le sillage a la largeur de la lame.

| Propriété | Rôle |
|---|---|
| `Lifetime` | Longueur apparente de la traînée |
| `MinLength` | Distance minimale avant qu'un segment apparaisse. Monter pour éviter les paquets quand l'objet est presque immobile |
| `WidthScale` (`NumberSequence`) | Profil de largeur sur la longueur. Finir fin donne une pointe |
| `Enabled` | Se coupe pendant l'inactivité : un sillage permanent sur une épée au repos fait sale |

## 4. Highlight et lumières

`Highlight` : `Adornee`, `FillColor`, `FillTransparency`, `OutlineColor`,
`OutlineTransparency`, `DepthMode` (`AlwaysOnTop` pour traverser les murs,
`Occluded` pour être masqué normalement).

**Roblox n'en rend qu'un nombre limité simultanément** (une trentaine). Au-delà,
certains ne s'affichent pas, silencieusement. N'en mets pas un par ennemi dans
une scène chargée : réserve-le à la cible courante ou à l'objet interactif
proche.

Les lumières (`PointLight`, `SpotLight`, `SurfaceLight`) sont aussi limitées en
nombre rendu et coûtent cher avec `Shadows` actif. Une lumière ajoutée à un
effet lui donne beaucoup de présence — une par effet suffit largement.

## 5. Recettes de base

À adapter à la charte du projet, jamais à copier telle quelle.

| Effet | Instance | Ce qui le caractérise |
|---|---|---|
| Impact | `ParticleEmitter`, `:Emit(10–15)` | `SpreadAngle` large, `Acceleration` vers le bas, `Lifetime` 0,3–0,5 s |
| Soin | `ParticleEmitter`, `Rate` bref | `Acceleration` vers le **haut**, vert doux, `LightEmission` haut, montée lente |
| Montée de niveau | Salve + `Beam` vertical | Salve depuis les pieds, `Shape = Cylinder`, `Beam` court en colonne |
| Sillage d'épée | `Trail` | Deux `Attachment` aux bords de la lame, `Enabled` seulement pendant le coup |
| Explosion visuelle | Salve + `PointLight` bref | Grosses particules courtes, lumière 0,1 s. **Pas** l'objet `Explosion` |
| Portail, zone | `ParticleEmitter` continu, côté serveur | `Shape = Cylinder`, `Rate` bas, `Lifetime` long |
| Projectile magique | `ParticleEmitter` attaché + `Trail` | L'emitter suit le projectile, le `Trail` marque la course |

## 6. Performance

Le coût dominant n'est pas le nombre de particules mais **la surface
transparente empilée à l'écran**. Dix grosses particules translucides qui se
recouvrent coûtent plus cher que cent petites bien réparties.

| Levier | Effet |
|---|---|
| Diviser `Rate` ou `:Emit(n)` par deux | Le plus rentable, et souvent invisible à l'œil |
| Réduire `Size` | Moins de surface, donc moins de coût |
| Raccourcir `Lifetime` | Moins de particules simultanées : le total vivant vaut `Rate × Lifetime` |
| Éviter les lumières multiples | Une par effet suffit |
| Couper les effets lointains | Rien ne sert d'émettre à 200 studs du joueur |

Sur téléphone, viser la lisibilité plutôt que la densité : un impact net à
12 particules se lit mieux en mêlée qu'un nuage à 60.

## 7. Pièges qui ne lèvent aucune erreur

| Symptôme | Cause |
|---|---|
| Rien ne s'affiche | `Beam`/`Trail` sans ses deux `Attachment` |
| Rien ne s'affiche | `Texture` pointant sur un ID inexistant |
| Rien ne s'affiche | L'effet est créé côté serveur dans `ServerStorage`, jamais répliqué |
| L'effet se coupe net | L'emitter est détruit avant `Lifetime.Max` |
| L'effet s'accumule | Les `Attachment` ne sont jamais détruits |
| L'effet est invisible de nuit | `LightInfluence` à `1` : passer à `0` |
| L'effet traverse tout | `ZOffset` mal réglé, ou `DepthMode = AlwaysOnTop` |
| Le sillage fait des paquets | `MinLength` trop bas sur un objet lent |
| Les joueurs meurent | `Explosion` utilisée pour du visuel : elle casse les assemblages et blesse. `DestroyJointRadiusPercent = 0` et `BlastPressure = 0` la rendent inoffensive — mais une salve de particules fait mieux et coûte moins |
| Certaines surbrillances manquent | Plus de `Highlight` simultanés que Roblox n'en rend |
