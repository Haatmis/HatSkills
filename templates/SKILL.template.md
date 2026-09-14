---
# Le nom du dossier fait foi ; garde les deux identiques.
name: nom-du-skill

# LE champ décisif : c'est le seul texte que Claude voit avant de décider.
# Formule : <ce que ça produit>. Utilise ce skill quand <déclencheurs réels>.
#           N'utilise pas ce skill pour <ce qui appartient à un autre skill>.
# Plafond description + when_to_use : 1 536 caractères.
description: >
  <Ce que ça produit, à l'impératif, en une phrase.> Utilise ce skill quand
  <phrases réelles que tape l'utilisateur, types de fichiers, situations> —
  même si <X> n'est pas demandé explicitement. N'utilise pas ce skill pour
  <cas voisin> (voir <autre-skill>).

# --- Optionnels : supprime les lignes que tu n'utilises pas ---------------
# paths: ["docs/**"]                  # ne s'active que sur ces fichiers
# disable-model-invocation: true      # /nom seulement, jamais automatique
# user-invocable: false               # skill de contexte pur
# allowed-tools: Bash(git status *) Read    # aussi étroit que possible
# disallowed-tools: AskUserQuestion   # couper une dérive connue
# argument-hint: [ticket]
# arguments: [ticket, branche]        # utilisables via $ticket, $branche
# context: fork                       # tâche longue, contexte isolé
---

# <Nom du skill>

## Situation

<1-2 phrases : où on est quand ce skill se déclenche, et ce qui compte ici.
Pas de « quand utiliser ce skill » — ça va dans la description.>

## Contexte figé

<Tout ce que tu te surprends à re-préciser d'une session à l'autre.
Règle : précisé deux fois à la main = doit être ici.>

- Public :
- Ton :
- Contraintes :
- Vocabulaire imposé :
- Vocabulaire interdit :

## Procédure

1. <Étape vérifiable, à l'impératif.>
2. <…>
3. <…>

## Format de sortie

<Le gabarit exact, copiable tel quel. C'est le meilleur anti-dérive.>

```
# [Titre]

## [Section]
- …
```

## Exemple

Entrée :
```
<un vrai bout d'entrée, pas une paraphrase>
```

Sortie :
```
<la sortie attendue, complète>
```

## Pièges

- <Erreur fréquente> — <pourquoi c'est faux ici>. <Le pourquoi vaut mieux
  qu'un MUST : il se généralise aux cas non prévus.>

## Apprendre de la session

<Ne retire pas cette section : c'est elle qui alimente /roblox:atelier.>

Trois signaux valent une entrée au journal, et trois seulement : l'utilisateur
t'a corrigé, la vérification Studio a révélé une erreur de ta part, ou un
contexte a dû t'être re-précisé. Formule une **règle**, pas un récit :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" add \
  --skill <nom-du-skill> --type correction \
  --lesson "Toujours …" --context "ce qui se passait, une ligne"
```

Types : `correction`, `studio-error`, `re-precision`. Rien à signaler : ne
lance rien. Si la commande annonce que le seuil est atteint, signale en une
ligne que `/roblox:atelier` est disponible — n'affine jamais de toi-même.
Protocole complet : `${CLAUDE_PLUGIN_ROOT}/references/journal.md`.

## Avant de rendre

- [ ] <vérification concrète>
- [ ] <vérification concrète>
- [ ] Leçon enregistrée au journal si tu as été corrigé, si Studio a révélé
      une erreur de ta part, ou si un contexte a dû t'être re-précisé.

<!--
Ressources embarquées (à créer seulement si besoin) :
  references/  docs détaillées — renvoie-y AVEC une condition de déclenchement
               (« pour les cas multi-devises, lis references/devises.md »)
  scripts/     code exécutable — ne consomme pas de contexte, ne dérive pas
  assets/      fichiers utilisés dans la sortie (modèles, polices, icônes)
Chemins : ${CLAUDE_SKILL_DIR}/scripts/verifier.py
-->
