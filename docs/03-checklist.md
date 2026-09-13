# 3. Checklist de relecture

À passer avant de committer un skill. Une ligne qui coince = une réécriture,
pas une exception.

## Périmètre

- [ ] Je peux nommer le livrable de ce skill **en un mot**.
- [ ] La tâche revient assez souvent pour mériter un skill (≥ 3-4 fois).
- [ ] Ce n'est pas plutôt un hook (déclenchement garanti), du CLAUDE.md
      (contexte permanent) ou un simple bon prompt (cas unique).

## Description — le déclenchement

- [ ] Elle dit **ce que ça produit** ET **quand s'en servir**.
- [ ] Elle contient les **vraies phrases** que je tape, pas des catégories.
- [ ] Elle est un peu insistante (« dès que… même sans demande explicite »).
- [ ] Elle dit **quand ne pas s'en servir**, et nomme le skill voisin.
- [ ] Aucun autre skill ne partage son vocabulaire de déclenchement.
- [ ] `description` + `when_to_use` ≤ **1 536 caractères**.
- [ ] Si le périmètre est délimitable par fichiers → `paths:` est renseigné.
- [ ] Si je veux garder le contrôle du moment → `disable-model-invocation: true`.

## Corps — la stabilité du résultat

- [ ] Tout ce que j'ai précisé à la main **deux fois** est dans `Contexte figé`.
- [ ] Il y a un **gabarit de sortie exact**, pas une description en prose.
- [ ] Il y a **au moins un** couple entrée → sortie réel.
- [ ] La procédure est numérotée et chaque étape est vérifiable.
- [ ] Les pièges sont accompagnés d'un **pourquoi**, pas d'un `MUST`.
- [ ] Il y a une section `Avant de rendre` avec des vérifications concrètes.
- [ ] Aucun « quand utiliser ce skill » n'a atterri dans le corps.

## Économie de contexte

- [ ] Corps < 500 lignes. Sinon → `references/`.
- [ ] Chaque renvoi à un fichier dit **à quelle condition** y aller.
- [ ] Tout ce qui est déterministe et répétitif est dans `scripts/`, pas en prose.
- [ ] Les chemins embarqués passent par `${CLAUDE_SKILL_DIR}`.
- [ ] Tout fichier de référence > 300 lignes a une table des matières.

## Vérification

- [ ] 2-3 prompts de test réalistes écrits.
- [ ] Au moins un **cas piège** qui doit partir sur un autre skill.
- [ ] Essayé avec et sans le skill, pour voir ce qu'il apporte vraiment.
- [ ] `python3 scripts/validate.py` passe.

## Hygiène

- [ ] `name` == nom du dossier.
- [ ] Le skill ne fait rien de surprenant par rapport à ce que sa description
      annonce (pas d'effet de bord caché, pas d'accès non justifié).
- [ ] `allowed-tools` est aussi étroit que possible (`Bash(git status *)` plutôt
      que `Bash`).
