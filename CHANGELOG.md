# Journal des versions

Le plugin `roblox`. Une entrée par version publiée — et une version publiée à
chaque changement, sinon personne ne la reçoit.

## 0.6.0

**Autorité physique.** `code` ne disait rien de la propriété réseau — le sujet
le plus piégeux pour tout ce qui déplace un personnage ou un objet. Il sait
maintenant que `SetNetworkOwner` délègue une autorité falsifiable, qu'elle ne
se donne jamais sur ce qui décide d'une issue de jeu, qu'elle se rend par
`SetNetworkOwnerAuto()`, et qu'elle lève une erreur sur une pièce ancrée.

**Optimisation structurelle, pas micro.** Quatre règles gratuites à l'écriture
et coûteuses à rattraper : événement plutôt que boucle par frame, réseau
compté plutôt qu'estimé, réutilisation plutôt que création en boucle, travail
sans autorité déplacé sur le client. Avec l'anti-règle explicite : ne pas
micro-optimiser sans mesure — ça abîme la lisibilité pour un gain invisible.

`references/perf.md` porte le détail : les coûts réels par ordre, les outils de
mesure, le pooling et quand il ne vaut pas le détour, des seuils indicatifs, et
la liste de ce qui ne mérite pas le détour. Consulté au besoin, pas payé à
chaque déclenchement.

**`game-design` chiffre l'échelle.** La spec porte une section « Échelle » —
joueurs simultanés, instances, appels au pic. C'est l'entrée qui décide de la
structure du code, et elle manquait.

Un retrait au passage : `Instance.new("Part", parent)` sortait dans la table
des dépréciées **et** dans les Pièges, où le pourquoi est expliqué. La table
en garde cinq au lieu de six.

## 0.5.0

**Reformulation conditionnelle.** Les cinq skills de production reformulent la
demande en une ligne avant d'agir — mais seulement quand elle nomme un système
plutôt qu'un élément, laisse un « qui » implicite, ou dépasse un fichier.
Ailleurs, c'est du bruit.

L'alternative envisagée était de déclencher `game-design` sur tout. Rejetée :
une spec complète pour quinze lignes de Luau, c'est un outil qu'on contourne
au bout de deux fois — et qui ne sert alors plus, même là où il comptait.
Comprendre et spécifier sont deux gestes de coût très différent.

**`code` et `debug` lisent `docs/design/`.** Rien ne les y obligeait : une
décision de design prise lundi pouvait être contredite par du code écrit
jeudi, sans que ça se voie à la relecture. Pour `debug` le gain est double —
la spec dit ce qui *devrait* se passer, soit la moitié du diagnostic, et un
comportement conforme à la spec n'est pas un bug mais un désaccord de design.

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
