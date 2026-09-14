---
name: feature
description: >
  Exécute une feature déjà cadrée : découpe la spec en étapes techniques
  ordonnées, appelle le skill compétent à chaque étape, vérifie dans Studio
  après chacune, et livre un système qui tourne avec des placeholders pour les
  assets manquants. Utilise ce skill quand game-design vient de passer la main
  avec une spec, quand l'utilisateur dit « exécute le plan », « enchaîne »,
  « implémente la spec », « continue la feature », ou quand il revient après
  avoir rempli des identifiants d'assets — « j'ai mis les IDs », « reprends
  avec les assets », « relance ». N'utilise pas ce skill pour cadrer une
  feature qui n'a pas encore de spec (voir game-design), pour écrire un bout
  de code isolé et déjà délimité (voir code), ni pour diagnostiquer un
  comportement cassé (voir debug).
---

# Exécuter une feature de bout en bout

## Situation

Une feature réelle traverse plusieurs métiers : du code serveur, du code
client, de l'animation, des VFX, du son. Aucun skill ne couvre tout, et rien
ne les coordonne tout seul — c'est ce trou que tu remplis.

Deux échecs guettent. Le premier : laisser un skill déborder sur un domaine
qui n'est pas le sien, parce que le bon n'a jamais été appelé. Le second :
produire les morceaux dans le désordre, et découvrir à la fin que l'étape 1
était fausse.

Ton livrable n'est pas du code : c'est **un système qui tourne**, vérifié à
chaque étape, plus la liste courte de ce qui reste à fournir.

## Contexte figé

**Appelle explicitement les autres skills.** N'écris pas de VFX toi-même en
espérant t'en sortir : invoque le skill du domaine. L'appel explicite est
fiable, le déclenchement automatique ne l'est pas.

| Domaine | Skill |
|---|---|
| Code serveur, client, configuration, câblage son | `/roblox:code` |
| Particules, faisceaux, traînées, surbrillances, flashs | `/roblox:vfx` |
| Modèle 3D, prop, objet construit depuis une image | `/roblox:hat3d` |
| Diagnostic quand une étape casse | `/roblox:debug` |
| Cadrage manquant ou spec à trancher | `/roblox:game-design` |

Un domaine sans skill dédié reste chez `/roblox:code`, avec le détail
nécessaire dans la consigne que tu lui passes.

**Serveur avant client, toujours.** Tant que le serveur n'est pas la source de
vérité, le code client n'a pas de sens à écrire. Cet ordre n'est pas du
confort : une feature de jeu construite dans l'autre sens est un aimant à
exploiteurs, et la reprendre après coup coûte plus cher que de l'écrire dans
le bon ordre.

**Vérification dans Studio après chaque étape**, avant de passer à la suivante.
Une erreur d'étape 1 trouvée à l'étape 1 coûte une correction ; trouvée à
l'étape 6, il faut d'abord démêler ce qui vient de quoi. Si une étape ne
passe pas, corrige-la — au besoin via `/roblox:debug` — avant d'avancer.

**Un placeholder ne doit jamais faire planter.** Un identifiant d'asset absent
vaut `0` dans la configuration, et le code teste cette valeur : il saute le son
ou l'animation au lieu de lever une erreur. Le système doit tourner de bout en
bout sans un seul asset.

**Les identifiants d'assets vivent dans un seul fichier :**
`src/shared/Config/Assets.luau`. C'est le point de rendez-vous — l'utilisateur
y colle ses IDs et te redemande de reprendre.

```lua
--!strict
-- 0 = à fournir. Remplace la valeur, puis demande à Claude de reprendre.
return {
    Combat = {
        -- Animation R15. Éditeur d'animation → publier → copier l'ID.
        SwingAnimation = 0,
        -- Son d'impact. Bibliothèque Roblox ou upload.
        HitSound = 0,
    },
}
```

**Exécute sans demander la permission de commencer.** Le plan est annoncé puis
déroulé. Tu ne t'arrêtes que sur un vrai blocage : deux lectures de la spec
possibles et contradictoires, ou une étape qui échoue et que tu ne sais pas
réparer.

## Procédure

1. **Lis la spec.** Le chemin `docs/design/<feature>.md` t'a été passé. Sans
   spec, ne devine pas : invoque `/roblox:game-design` d'abord.
2. **Relève les contraintes techniques** avant de découper : le rig est-il R6
   ou R15 ? quels systèmes existants sont touchés ? l'arborescence est-elle
   Rojo ou faut-il passer par le MCP ? la feature a-t-elle besoin d'un objet
   qui n'existe pas encore — une épée, un coffre, une borne ? Un prop est une
   **entrée** de la feature : il se construit avant le code qui s'en sert,
   sinon les étapes suivantes travaillent sur du vide.
3. **Découpe en étapes**, chacune avec son skill, son livrable et sa
   vérification. L'ordre par défaut, à adapter :

   | # | Étape | Skill |
   |---|---|---|
   | 0 | Prop ou modèle 3D dont la feature a besoin | `hat3d` |
   | 1 | Configuration et types partagés | `code` |
   | 2 | Logique serveur : la source de vérité | `code` |
   | 3 | Remotes : intentions du client, validées serveur | `code` |
   | 4 | Client : entrée, retour immédiat | `code` |
   | 5 | Animation : lecture, priorité, rig | `code` |
   | 6 | VFX | `vfx` |
   | 7 | Son : câblage | `code` |
   | 8 | Vérification d'ensemble à deux joueurs | `code` |

4. **Annonce le plan** en quelques lignes, puis enchaîne sans attendre.
5. **Pour chaque étape** : invoque le skill avec une consigne qui contient le
   morceau de spec concerné, les chiffres, et ce que l'étape précédente a
   produit. Un skill appelé sans contexte réinvente ce qui existe déjà.
6. **Vérifie dans Studio** après l'étape. Échec → corrige avant d'avancer.
7. **Note les assets manquants** dans `src/shared/Config/Assets.luau` au fur et
   à mesure, avec un commentaire disant d'où vient chaque ID.
8. **Vérifie l'ensemble** en conditions réelles : Start Server + 2 joueurs.
9. **Livre** au format ci-dessous.

### Reprise après remplissage des assets

L'utilisateur revient en disant qu'il a mis les IDs. Alors :
relis `src/shared/Config/Assets.luau`, repère les valeurs qui ne sont plus à
`0`, vérifie que chacune est branchée au bon endroit, teste dans Studio que
l'animation joue et que le son sort, et rends un compte rendu court : ce qui
est désormais actif, ce qui reste à `0`. Ne recode pas ce qui marchait déjà.

## Format de sortie

```markdown
## Plan
| # | Étape | Skill | Vérifié |
|---|---|---|---|
| 1 | … | code | ✅ |

## Ce qui tourne maintenant
<Ce que le joueur peut faire, concrètement, en 3 lignes.>

## Fichiers
| Chemin | Type | Rôle |
|---|---|---|

## Client / serveur
- **Serveur** : <ce qu'il décide>
- **Client** : <ce qu'il affiche et envoie>
- **Transite** : <Remote, charge utile, validation serveur>

## Sécurité
<Ce qu'un exploiteur tenterait, et ce qui l'en empêche.>

## À toi de fournir
| Asset | Où le coller | Comment l'obtenir |
|---|---|---|
| Animation de coup | `Config/Assets.luau` → `Combat.SwingAnimation` | Éditeur d'animation → publier → copier l'ID |

Dis-moi quand c'est rempli et je reprends.

## Écarts avec la spec
<Ce qui a été fait différemment et pourquoi. Ou : « conforme ».>
```

## Exemple

Entrée : `docs/design/combat-melee.md`, tout juste écrite par `game-design`.

Le découpage réel : `Config/Combat.luau` avec les chiffres de la spec →
`Systems/Combat.luau` côté serveur, qui détient la hitbox, le cooldown et les
dégâts → le Remote `RequestSwing`, qui ne transporte **rien** d'autre que
l'intention, le serveur décidant de la portée et des dégâts → le tool et son
entrée client → l'animation, avec le rig détecté à l'étape 2 → les VFX
d'impact → le son.

Chaque étape est vérifiée avant la suivante. À la fin, le système tourne :
on tape, les dégâts s'appliquent, le retour visuel est là. Restent deux lignes
dans `Assets.luau` à `0` — l'animation et le son — et le code les saute
proprement en attendant.

## Pièges

- **Écrire soi-même le domaine d'un autre skill.** Des VFX écrits par
  l'orchestrateur sont des VFX écrits sans savoir-faire VFX — et sans la
  charte visuelle du projet, donc incohérents avec le reste du jeu.
- **Client avant serveur.** L'ordre le plus coûteux à rattraper : il faut
  reprendre toute la logique une fois qu'on réalise que le client décidait.
- **Passer un skill sans contexte.** Il réinventera ce que l'étape précédente
  vient de produire, avec d'autres noms.
- **Tout vérifier à la fin.** Une erreur d'étape 1 trouvée à l'étape 8
  contamine tout ce qui est entre les deux.
- **Bloquer sur un asset absent.** Le système doit tourner sans. Un son muet
  n'empêche pas de tester des dégâts.
- **Laisser un placeholder lever une erreur.** Un ID à `0` se teste, il ne se
  charge pas.
- **Dériver au-delà de la spec.** Ce qui n'y est pas n'est pas à faire. Une
  bonne idée en cours de route se propose, elle ne s'implémente pas en douce.

## Apprendre de la session

Trois signaux valent une entrée au journal, et trois seulement : l'utilisateur
t'a corrigé, la vérification Studio a révélé une erreur de ta part, ou un
contexte a dû t'être re-précisé. Formule une **règle**, pas un récit :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" add \
  --skill feature --type correction \
  --lesson "Toujours …" --context "ce qui se passait, une ligne"
```

Types : `correction`, `studio-error`, `re-precision`. Rien à signaler : ne
lance rien. Si la commande annonce que le seuil est atteint, signale en une
ligne que `/roblox:atelier` est disponible — n'affine jamais de toi-même.
Protocole complet : `${CLAUDE_PLUGIN_ROOT}/references/journal.md`.

## Avant de rendre

- [ ] La spec a été lue, et le plan en découle.
- [ ] Rig R6/R15 identifié avant toute étape d'animation.
- [ ] Serveur avant client.
- [ ] Chaque étape a appelé son skill, pas été traitée en interne.
- [ ] Chaque skill a reçu le contexte de ce qui précède.
- [ ] Chaque étape vérifiée dans Studio avant la suivante.
- [ ] Vérification d'ensemble faite à deux joueurs.
- [ ] Aucun placeholder ne peut lever une erreur.
- [ ] `Config/Assets.luau` à jour, chaque entrée disant comment l'obtenir.
- [ ] Écarts avec la spec signalés, ou conformité affirmée.
- [ ] Leçon enregistrée au journal si tu as été corrigé, si Studio a révélé
      une erreur de ta part, ou si un contexte a dû t'être re-précisé.
