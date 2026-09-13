# Le journal d'apprentissage

Protocole partagé par tous les skills du plugin. Chaque SKILL.md en porte une
version compacte ; ce fichier est la référence complète.

## Ce qui vaut une entrée — et rien d'autre

| Signal | `--type` |
|---|---|
| L'utilisateur te corrige, ou réécrit ce que tu as produit | `correction` |
| La vérification Studio révèle une erreur que tu avais commise | `studio-error` |
| L'utilisateur re-précise un contexte que le skill aurait dû porter | `re-precision` |

Rien d'autre. Une préférence exprimée une fois, un choix de goût, une
information de contexte projet : ce n'est pas une leçon sur le skill. Un
journal qui se remplit de bruit ne sera jamais dépouillé.

## La commande

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" add \
  --skill <nom-du-skill> --type <type> \
  --lesson "Toujours …" --context "ce qui se passait, une ligne"
```

`--skill` est le skill **à corriger**, pas forcément celui qui tourne. Quand
`debug` trouve un bug qu'un motif de `code` aurait pu éviter, la leçon va à
`code`.

## Formuler la leçon

Une **règle**, pas un récit. Elle doit pouvoir être collée telle quelle dans un
`Contexte figé` sans réécriture.

| Mauvais | Bon |
|---|---|
| « J'ai oublié de valider le prix côté serveur » | « Un Remote ne transporte jamais un prix : seulement l'intention » |
| « L'utilisateur voulait ses systèmes dans Systems/ » | « Les systèmes serveur vont dans `src/server/Systems/` » |
| « L'animation ne marchait pas » | « Charger une animation via `humanoid.Animator`, jamais via `Humanoid` » |

Une leçon qui commence par « j'ai » est presque toujours mal formulée.

## Ce qui se passe ensuite

Les leçons identiques fusionnent et incrémentent `occurrences` — c'est ce
compteur qui distingue une règle d'un incident isolé. Une entrée vue une seule
fois n'entrera pas dans un skill.

À partir de **8 leçons en attente**, la commande le signale dans sa sortie.
Ajoute alors une ligne en fin de réponse pour dire que `/roblox:affiner` est
disponible, puis reprends ce que tu faisais. **N'affine jamais de toi-même** :
modifier un skill est une décision de l'utilisateur.

Consultation :

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" status
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" list --skill code
```

## Pourquoi ce n'est pas automatique

Un skill ne se réécrit pas seul, et c'est tant mieux : chaque ligne ajoutée est
rechargée à **chaque** déclenchement. Une boucle qui ne ferait qu'ajouter
dégraderait les skills au lieu de les améliorer. La consolidation est donc un
acte délibéré, qui retire autant qu'il ajoute — voir le skill `affiner`.
