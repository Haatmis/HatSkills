# Journal des versions

Le plugin `roblox`. Une entrée par version publiée — et une version publiée à
chaque changement, sinon personne ne la reçoit.

## 0.4.0

⚠ **`/roblox:nouveau-skill` et `/roblox:affiner` disparaissent** au profit de
**`/roblox:atelier`**, qui fait les deux.

La fusion n'a pas été faite pour économiser des tokens — le gain permanent est
marginal. Deux autres raisons : les deux skills se disputaient le même
vocabulaire (« skill », « améliorer »), et ils se déclenchaient dans des
sessions Roblox alors qu'ils n'ont rien à voir avec faire un jeu. Une paire de
collision en moins, un parasite en moins.

Le skill fusionné fait **925 tokens de moins** que la somme des deux : le
contexte figé, les pièges et les garde-fous étaient largement communs.

C'est la seule entorse assumée à la règle « un skill = un livrable » : deux
modes, deux gabarits de sortie, parce que les deux gestes sont rares et que le
mode se lit sans hésitation dans la demande.

## 0.3.0

- **`/roblox:help`** — ouvre le guide dans le navigateur. La page est
  **générée** depuis `GUIDE.md` à chaque appel plutôt que stockée : une aide
  écrite à la main diverge du guide dès la mise à jour suivante, et une aide
  périmée affirme des choses fausses avec assurance. Ouverture compatible
  Windows, macOS et Linux ; en session distante sans navigateur, le chemin du
  fichier est donné au lieu d'échouer.
- `GUIDE.md` déménage à la racine du plugin : il n'était pas livré avec
  l'installation, donc `/roblox:help` ne l'aurait pas trouvé.
- Le validateur n'exige plus de vocabulaire de déclenchement ni d'exclusion
  croisée sur un skill en invocation manuelle seule — par construction, il
  n'est jamais choisi sur sa description.

## 0.2.0

Première mise à jour réellement distribuée : la `0.1.0` n'ayant jamais été
bumpée, tout ce qui suit était resté invisible pour les installations
existantes.

**Nouveaux skills**

- `game-design` — cadre une feature avant tout code : règles, chiffres
  justifiés, cas limites, ce qu'un exploiteur tentera. Écrit la spec dans
  `docs/design/`.
- `feature` — exécute la spec, étape par étape, en appelant le skill compétent
  à chacune et en vérifiant dans Studio avant de passer à la suivante.
- `debug` — reproduit le bug dans Studio avant d'y toucher, remonte à la cause
  racine, corrige au minimum, cherche le même motif ailleurs.
- `vfx` — presets réutilisables dérivés d'une charte visuelle par projet.
- `hat3d` — image → modèle 3D : `model.json` comme source de vérité, préview
  HTML à valider, `build.lua` pour Studio.
- `affiner` — consolide le journal d'apprentissage dans les skills.

**Boucle d'amélioration**

- Journal d'apprentissage câblé sur les 7 skills de production.
- `HATSKILLS_JOURNAL_DIR` permet de le faire suivre d'une machine à l'autre ;
  fusion sans conflit via `merge=union`.

**Fiabilité**

- 10 évals de routage, dont 4 cas de frontière et 1 cas négatif absolu.
- CI : validation à chaque push, évals en déclenchement manuel.
- `check_version.py` refuse une modification du plugin sans bump de version.
- Renvois morts de `hat3d` qualifiés (`hat3d-blender`, `hatstack`,
  `/hat3d-finition` ne sont pas fournis par ce plugin).

## 0.1.0

Première version : les skills `code` et `nouveau-skill`, la structure du
plugin, le validateur et la méthode d'écriture.
