---
name: help
description: >
  Ouvre le guide du plugin dans le navigateur : à quoi sert chaque skill,
  comment se déroule une feature, et quoi faire quand ça rate. La page est
  générée depuis GUIDE.md à chaque appel, donc jamais périmée.
disable-model-invocation: true
allowed-tools: Bash(python3 *) Bash(start *) Bash(open *) Bash(xdg-open *) Read
---

# Guide du plugin

## Situation

L'utilisateur a tapé `/roblox:help`. Il veut voir la page, pas lire un résumé
que tu improviserais. Ouvre-la, dis-lui où elle est, et arrête-toi là.

## Contexte figé

- La page est **générée**, jamais stockée : `GUIDE.md` est la seule source.
  N'écris jamais de HTML d'aide à la main — il divergerait du guide dès la
  mise à jour suivante, et une aide périmée affirme des choses fausses avec
  assurance.
- Le générateur écrit dans le dossier temporaire du système. Rien n'est
  ajouté au projet de l'utilisateur.
- Si l'ouverture échoue — session sans interface, conteneur, machine
  distante — ce n'est pas une erreur : donne le chemin du fichier et
  passe à autre chose.

## Procédure

1. **Génère la page** et récupère le chemin qu'elle affiche :

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_help.py" "${CLAUDE_PLUGIN_ROOT}/GUIDE.md"
   ```

2. **Ouvre-la**, avec la commande de la plateforme :

   | Système | Commande |
   |---|---|
   | Windows | `start "" "<chemin>"` |
   | macOS | `open "<chemin>"` |
   | Linux | `xdg-open "<chemin>"` |

3. **Réponds en deux lignes** : la page est ouverte, et son chemin. Si
   l'utilisateur a passé un argument (`/roblox:help vfx`), ajoute une phrase
   sur ce point précis en le lisant dans `GUIDE.md` — mais ouvre la page
   quand même.

## Format de sortie

```markdown
Guide ouvert : `<chemin>`

<Une ligne seulement si l'utilisateur a demandé un point précis.>
```

Rien de plus. Ne résume pas le guide : il est sous ses yeux.

## Exemple

Entrée :
```
/roblox:help
```

Sortie :
```
Guide ouvert : `C:\Users\hat\AppData\Local\Temp\roblox-aide.html`
```

Entrée :
```
/roblox:help vfx
```

Sortie :
```
Guide ouvert : `/tmp/roblox-aide.html`

Le skill `vfx` produit des presets dans `src/shared/VFX/`, dérivés de la
charte `Style.luau` — section « Les trois fichiers qui comptent ».
```

## Pièges

- **Résumer le guide dans la réponse.** Il vient de l'ouvrir. Le paraphraser
  double la longueur pour zéro information.
- **Écrire du HTML à la main.** La page se génère. Toujours.
- **Traiter un échec d'ouverture comme une panne.** En session distante,
  aucun navigateur n'existe. Le chemin suffit.

## Avant de rendre

- [ ] La page a été générée depuis `GUIDE.md`, pas écrite.
- [ ] La commande d'ouverture correspond au système.
- [ ] Le chemin est donné, même si l'ouverture a échoué.
- [ ] Aucun résumé du guide dans la réponse.
