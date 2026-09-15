# Génération d'image de référence par IA

Étape **optionnelle**, et sans effet si `config.json` n'existe pas dans le
dossier du skill. Elle vivait dans le corps du skill, où elle coûtait ses
441 tokens à chaque modèle demandé — y compris à ceux qui partent d'une image
que l'utilisateur fournit lui-même, c'est-à-dire la majorité.

## La procédure

Le skill peut générer lui-même l'image de référence depuis un prompt texte, via
une API d'images **compatible OpenAI** (`POST {baseUrl}/images/generations`) :
OpenAI (`gpt-image-1`, `dall-e-3`) ou tout fournisseur compatible (Together,
xAI, fal…) en changeant `baseUrl`.

**Configuration** : copier `config.example.json` vers `config.json` (même
dossier que ce SKILL.md) et renseigner :

```json
{ "imageGen": { "baseUrl": "https://api.openai.com/v1",
                "apiKey": "sk-…", "model": "gpt-image-1", "size": "1024x1024" } }
```

`config.json` contient un secret : ne jamais le committer, ne jamais afficher
la clé en clair dans une réponse.

**Usage** :

```powershell
node "${CLAUDE_PLUGIN_ROOT}/skills/hat3d/scripts/genimage.mjs" hat3d/<slug> "<prompt>" [--name reference.png] [--size 1024x1024]
```

→ sauvegarde `hat3d/<slug>/reference.png`, à lire et valider avec
l'utilisateur avant de modéliser (c'est ensuite une image source normale,
à référencer dans `source_image`).

Conseils de prompt pour une référence modélisable : **un seul objet, vue de
trois quarts ou de profil, fond neutre uni**, style simple et lisible.

Logique de décision :
- L'utilisateur demande explicitement la génération IA → l'utiliser (erreur
  claire s'il manque `config.json`).
- Texte seul et `config.json` présent → proposer les deux options (génération
  ou modélisation directe) ; en cas de doute, modélisation directe.
- Échec API (clé invalide, quota, réseau) → le signaler et retomber sur la
  modélisation directe depuis le texte.
