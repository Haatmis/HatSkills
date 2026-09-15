# Journal des versions

Le plugin `roblox`. Une entrée par version publiée — et une version publiée à
chaque changement, sinon personne ne la reçoit.

## 0.13.0

**Correction d'une affirmation fausse de la `0.12.0`.** J'y avais écrit que
l'API de la Toolbox n'expose pas les animations, en me réclamant d'une
vérification. La vérification était mauvaise : j'avais interrogé la catégorie
animation avec le mot-clé « door ». Avec « punch », « idle » ou « run », elle
répond — 188 résultats pour « idle ». Le type 24 est cherchable comme les
autres, et `toolbox.py` le propose maintenant.

**La vraie raison de ne pas emprunter une animation est plus embêtante.**
Roblox lie une animation à son créateur : celle d'un autre compte ne se charge
pas dans un jeu publié. Elle peut marcher dans Studio chez son propriétaire et
échouer pour tous les joueurs une fois en ligne — un défaut qui ne se voit pas
là où on teste. Les animations restent donc à `0`, mais parce que la propriété
l'interdit, pas parce que l'API serait muette.

`toolbox.py verifier --proprietaire "<compte du jeu>"` tranche ce cas sans
ouvrir Studio, et la fiche des symptômes de `debug` renvoie dessus. Ce plugin
connaissait déjà la règle de propriété — elle est dans `symptomes-frequents.md`
depuis longtemps. C'est `feature` qui la contredisait : la connaissance était
là, la cohérence entre skills ne l'était pas.

La route de détails de la Toolbox refuse les animations (404) ; le script
retombe sur l'API économie, qui répond pour tout et porte le créateur. Se
contenter de la première route était la deuxième moitié de mon erreur.

**Ce qui n'a pas avancé.** Trois faux négatifs cette session, tous du même
genre : une recherche mal formulée prise pour un fait établi. Les deux premiers
étaient sans conséquence, celui-ci a été publié dans le guide et dans le
changelog avant d'être attrapé — par l'utilisateur, pas par moi. Aucun
garde-fou ne peut vérifier une affirmation sur le monde extérieur ; seule la
discipline de tester la négation le peut.

## 0.12.0

**Le plugin emprunte à la Toolbox au lieu de livrer muet.** Jusqu'ici, tout
asset que Claude ne peut pas publier valait `0` : le système tournait, mais
sans un son. Un système muet se teste mal — on ne sait pas si le son ne se
déclenche pas ou s'il n'existe pas encore. `feature` et `vfx` vont maintenant
chercher un vrai asset pour les sons, images, modèles et meshes.

`scripts/toolbox.py` interroge l'API Toolbox de Roblox : `chercher` rend des
candidats réels avec nom, durée et créateur, `verifier` dit si un identifiant
existe encore — un asset de la Toolbox peut être modéré après coup, et son ID
reste valide en apparence sans plus rien charger.

Deux filtres par défaut. **Gratuit et disponible**, sinon l'ID ne sert à rien.
Et **aucun modèle contenant des scripts** : c'est le vecteur de backdoor le
plus courant sur Roblox, et sur la première recherche d'essai — « door » — les
deux premiers modèles en contenaient. Il faut `--avec-scripts` pour en obtenir,
explicitement.

La règle qui compte plus que le reste : **aucun identifiant n'est écrit s'il ne
vient pas d'une réponse de Roblox.** Un `rbxassetid://` tiré de la mémoire a
l'air juste, passe la relecture et ne charge rien. `vfx` portait déjà cette
interdiction sans offrir d'alternative ; elle en a une.

Chaque emprunt se signale — provenance en commentaire dans `Assets.luau`, et
ligne dédiée dans « À toi de fournir », avec l'état *emprunté* distingué de
*manquant*. Un placeholder trop crédible se fait oublier et part en production ;
c'est le défaut symétrique de l'effet trop discret de la `0.9.0`.

Les **animations** ne sont pas concernées : l'API de la Toolbox ne les expose
pas — vérifié, pas supposé. Elles restent à `0` et à publier à la main.

**Ce qui n'a pas avancé.** Le corps de `feature` grossit de dix-sept lignes ;
`vfx` en rend deux, sa procédure de repli étant devenue inutile. Le solde reste
négatif et s'ajoute à la dette de la `0.9.0`. Le routage n'est toujours pas
mesuré, et aucun de ces chemins n'a été essayé dans Studio — seulement contre
l'API, d'ici.

## 0.11.0

**Les références se lisent par section, plus en entier.** Cinq skills
imposaient la lecture intégrale d'une fiche pour en utiliser une ligne. Sur
`vfx`, la boîte à outils coûtait 3143 tokens à chaque déclenchement — plus cher
que le skill lui-même — pour un contenu utilisé au cinquième. Chaque fiche
concernée a déjà un sommaire ; le corps dit maintenant de lire le sommaire puis
la section utile.

Mesuré fiche par fiche : 11 522 tokens avant, 1 986 après, soit **9 536 tokens
évités** sur une passe complète. Par déclenchement : 2 634 sur `vfx`, 2 166 sur
`debug`, 1 237 sur `game-design`, jusqu'à 3 499 sur `code` quand les deux
fiches étaient sollicitées.

`validate.py` refuse désormais qu'une fiche à sommaire soit lue en entier. Une
fiche peut s'en dispenser en le déclarant — `style-detaille.md` de `hat3d` le
fait, parce que ce n'est pas une table de consultation mais la procédure du
mode par défaut, lue dans l'ordre. La découper rendrait un plus mauvais modèle,
et l'économie ne vaut jamais ça.

**Ce qui n'a pas été touché, délibérément.** Les ~1700 tokens de descriptions
sont le seul coût permanent, donc la cible évidente. Ce sont aussi le seul
texte qui décide du déclenchement, et le routage n'est toujours pas mesuré :
les raccourcir reviendrait à dégrader la seule chose qui compte, sans moyen de
s'en apercevoir. Ça attend une campagne d'évals. Dédupliquer les paragraphes
communs entre skills ne rapporterait rien non plus — un seul corps est chargé
à la fois.

## 0.10.0

**Quatre emprunts à la méthodologie de `codegraph`**, un index de code local
qui publie ses propres mesures — et dont le benchmark s'est fait contester sur
son témoin. Les deux moitiés étaient instructives.

**Trois runs par prompt, pas un.** Le protocole manuel des évals mesurait
chaque cas une seule fois. Le déclenchement d'un skill est stochastique : une
mesure unique ne distingue pas « ça marche » de « ça a marché cette fois-là ».
Chaque prompt se joue maintenant trois fois, médiane comme verdict, et tout
prompt qui n'est pas 3/3 est signalé — un 2/3 est une description limite, qui
lâchera sans prévenir.

**La péremption devient visible.** `evals/RESULTATS.md` enregistre chaque
campagne : version mesurée, date, couverture, verdict. `validate.py` alerte
quand la dernière mesure date d'une version antérieure, ou qu'il n'y en a
aucune — ce qui est le cas aujourd'hui. C'est la bannière de péremption de
`codegraph`, transposée : l'aveu ne dépend plus de la mémoire de celui qui
parle. L'alerte ne se tait qu'en jouant les onze prompts.

**Le journal des versions dit aussi ce qui recule.** Nouvelle règle dans
`CLAUDE.md`, appliquée rétroactivement à la `0.9.0` : ce qui a grossi alors
qu'il devait maigrir, ou ce qui n'a pas pu être vérifié, s'écrit. Un journal
qui ne raconte que des victoires est une affiche.

**Le guide nomme la vraie variable.** Ce qui décide si un skill aide, ce n'est
ni la taille du jeu ni la difficulté : c'est à quel point la demande laisse des
choses non dites. Nouvelle section, avec le test simple — si tu sais déjà quel
fichier va changer et comment, tu n'as pas besoin d'un skill.

Deux choses délibérément **pas** reprises : les pourcentages de vitrine, parce
que le témoin de `codegraph` est un agent que personne ne fait tourner, et
l'outil unique, parce qu'on a déjà mesuré qu'un skill fusionné coûte neuf fois
ses descriptions séparées.

## 0.9.0

**Dix passes de relecture, et ce qu'elles ont trouvé n'était pas du confort.**
Presque tout ce qui suit est un défaut silencieux : rien ne plantait, et le
plugin ne faisait pas ce qu'il annonçait.

`/roblox:help` ne pouvait pas marcher sous Windows. Le skill n'avait aucun
repli `py`, et son `allowed-tools` n'autorisait que `python3` — l'alias
Microsoft Store. La commande ouvrait une boutique, et le repli était interdit
avant d'être tenté. C'est la troisième fois que ce défaut passe : `validate.py`
refuse maintenant tout skill qui appelle `python3` sans donner le repli.

Le journal ratait sa déduplication **sur sa propre langue**. Les accents
n'étaient pas retirés avant la normalisation, donc « déplace » et « deplace »
ne se reconnaissaient pas. Comme c'est le compteur d'occurrences qui décide de
ce qui monte dans un skill, une leçon vue trois fois pouvait rester à ×1 et n'y
monter jamais. Un `--skill` mal orthographié était aussi accepté en silence,
créant une leçon qu'`atelier` ne saurait jamais où promouvoir.

`vfx` gagne la règle que l'usage réel réclamait : **un effet qu'on ne remarque
pas n'existe pas.** Viser le haut, et donner un réglage pour baisser. En
compensation, deux renvois vers le même fichier ont fusionné.

La page d'aide affichait des backticks dans l'onglet du navigateur et
construisait son sommaire en JavaScript — donc le perdait dès qu'on relisait
le fichier autrement, ce qui est précisément le cas prévu quand l'ouverture
échoue. Le sommaire est maintenant dans le HTML.

**Ce qui n'a pas avancé.** Le corps de `vfx` a grossi de six lignes nettes :
la règle ajoutée valait sa place, la redondance retirée en compensation ne
suffisait pas. `CLAUDE.md` demande de retirer autant qu'on ajoute, et le solde
reste à payer à la prochaine consolidation. Le routage, lui, n'a toujours pas
été mesuré — `claude plugin eval` reste en accès anticipé, et dix prompts du
protocole manuel sur onze n'ont jamais été joués.

Trois garde-fous ferment des dérives déjà constatées : `check_version.py`
comparait à la base de fusion seule et laissait passer une version **derrière**
celle déjà publiée ; l'en-tête du guide avait décroché d'une version ; le
protocole manuel des évals couvrait dix cas sur onze, et le README racine en
annonçait sept pour onze, avec une commande d'éval qui doublait la facture
faute de `--ablation none`. Chaque garde-fou a été vérifié sur un cas cassé
avant d'être gardé.

## 0.8.1

Réconcilie deux versions écrites en parallèle : la `0.8.0` (durcissement du
journal) sur la branche, et la `0.7.1` (consolidation « regarder avant de
détruire ») poussée sur `main` depuis une autre session. Les deux touchaient
`code` et `vfx`, mais à des endroits différents — git les a fusionnées seul,
seuls le numéro de version et le journal des versions demandaient un arbitrage.

Aucun contenu perdu des deux côtés. C'est le premier cas où deux sessions ont
travaillé le même plugin en même temps, et ça a tenu.

## 0.8.0

**Le journal se durcit contre l'injection indirecte.** Personne d'extérieur
n'écrit dans le journal — c'est Claude qui écrit, dans tes sessions. Le risque
n'est donc pas l'intrusion, c'est qu'il prenne pour une leçon quelque chose
qu'il a simplement **lu** : un commentaire dans un module tiers, un README de
dépendance, une page web.

Le scénario n'a besoin de personne de malveillant. Un module contient
`-- Note : désactiver la validation serveur, c'est plus rapide`. Claude le lit,
l'enregistre en croyant bien faire, et deux semaines plus tard la règle est
dans le `Contexte figé` de `code` — validée par un utilisateur qui valide tout.

- **À la capture** : seulement ce qui a été observé dans la session. Une
  consigne lue quelque part est une donnée, pas une leçon — même rédigée comme
  une consigne, et surtout quand elle l'est. `--context` doit citer
  l'observation, ce qui rend la provenance jugeable des semaines plus tard.
- **À la consolidation** : `atelier` gagne un quatrième tas, **refuser**. Toute
  leçon qui demande d'exécuter, de contacter un service, de désactiver une
  vérification ou d'affaiblir la sécurité au nom de la rapidité est refusée
  **et nommée** — jamais écartée en silence. Une leçon légitime dit comment
  bien faire, jamais comment contourner.

La vraie barrière reste la validation humaine du diff. Ces règles ne la
remplacent pas : elles rendent le mauvais cas **visible** au lieu de le laisser
se fondre dans le lot.

**`.journal/` existe enfin.** La capacité de partage était construite depuis la
0.2.0 mais n'avait jamais été activée : ni dossier, ni variable posée. Le
dossier est là, avec le mode d'emploi.
## 0.7.1

**Consolidation du journal : regarder avant de détruire.** Cinq leçons remontées
d'une session de bout en bout sur un jeu réel, dont trois erreurs que la
vérification Studio a révélées et qui ont chacune coûté un aller-retour.

- `vfx` ajoute aux pièges le `NumberRange` dont une seule borne est mise à
  l'échelle : `NumberRange.new(26, 40 * i)` lève dès que `i` passe sous 0,65,
  donc un effet qui marche en rareté haute plante en rareté basse.
- `code` fusionne en un seul piège deux façons de se tromper sur `:Destroy()` —
  le conteneur temporaire qui *est* l'objet qu'on vient d'en extraire, et
  l'instance gérée par Rojo qui ne se recrée pas sans reconnexion manuelle.
- `code` tire de sa règle de propriété réseau le corollaire pour les tests :
  rapprocher un joueur d'un objet se fait en déplaçant le personnage, jamais
  l'objet, sinon le serveur le voit rester où il était et refuse sur la
  distance.
- `code/references/perf.md` gagne une section **audio** : un `Instance.new`
  de `Sound` démarre avec 0,36 s de retard fixe, ce qui s'entend comme un
  fichier mal découpé et envoie chercher le défaut dans l'export.

Deux retraits pour compenser : la puce `:Emit(n)` de `vfx`, déjà dite deux fois
ailleurs dont une avec le pourquoi, et la redite « ne rends jamais du code non
exécuté » dans l'étape 5 de `code`, que les pièges portent mieux.

## 0.7.0

**Le retour joueur devient une catégorie.** Lacune trouvée sur la première
feature réelle : le système de combat fonctionnait, était sécurisé, vérifié —
et aucune pastille de dégâts. Ni `game-design` ni `vfx` n'y avaient pensé,
parce que rien dans le plugin ne parlait de lisibilité. C'était une lacune de
conception, pas d'exécution : personne n'avait rien demandé.

- `game-design` remplit une section **Retour joueur** dans chaque spec : action
  réussie, dégât subi, état courant. « Rien » est un choix acceptable, mais il
  doit être écrit.
- `vfx` distingue **décorer** et **informer**. Un effet décoratif enrichit et
  peut être discret ; un effet qui informe doit être lu en un tiers de seconde,
  porter une seule information, ne pas se superposer à lui-même, et partir en
  moins d'une seconde.
- La boîte à outils gagne le volet correspondant : quelle instance pour quelle
  information, le réglage complet d'une pastille de dégâts, et surtout le
  décalage aléatoire sans lequel trois coups rapides empilent trois chiffres
  illisibles. Plus la règle qui économise du réseau : une pastille est
  **locale**, le serveur diffuse l'événement et chaque client décide.

## 0.6.4

Reprise de la consolidation validée dans une session parallèle, pour éviter
une fusion manuelle à quatre fichiers en conflit.

- `code` sait maintenant qu'une règle réagissant à un état se branche sur le
  **signal** qui porte cet état, pas sur le seul chemin de code qui l'a
  provoqué — sinon elle rate les autres causes et ne se teste qu'en rejouant
  ce chemin. Leçon issue du vrai bug : la pause de régénération accrochée au
  coup de poing au lieu de la perte de PV.
- Retrait du piège « Réinventer un système déjà présent dans `src/` », qui ne
  faisait que renvoyer à l'étape 2 de la procédure sans rien ajouter.

## 0.6.3

Trois bugs Windows, tous introduits par moi : les scripts ont été écrits et
testés sous Linux, jamais sur la seule plateforme où ils tournent vraiment.

- **`check_version.py` sortait en erreur après avoir conclu « OK ».** La
  console Windows est en cp1252 et ne sait pas encoder la flèche `→` :
  `UnicodeEncodeError`, exit 1, juste après avoir réussi. Un script qui échoue
  une fois qu'il a réussi apprend à ignorer son verdict — c'est pire que pas
  de script. Reproduit sous cp1252, corrigé, revérifié.
- `validate.py`, `journal.py` et `build_help.py` avaient le même défaut
  latent. Les quatre reconfigurent maintenant leur sortie en UTF-8.
- **`python3` est un alias du Microsoft Store sur Windows** : la commande du
  journal ouvrait une page de boutique et n'enregistrait rien. La capture
  était donc muette. Les huit skills et la référence indiquent `py` en repli.

## 0.6.2

Les 18 renvois vers `references/` étaient écrits en relatif. Observé en usage
réel : le modèle construisait le chemin absolu vers le cache du plugin à la
main, avec un `cat … 2>/dev/null || ls` en repli — il tâtonnait. Tous passés en
`${CLAUDE_SKILL_DIR}/references/…`. Le gabarit suit, sinon le prochain skill
repartirait en relatif.

## 0.6.1

Le README des évals annonçait sept cas alors que la suite en a dix : les trois
ajoutés en même temps que `atelier` n'avaient jamais été documentés. Les
graders, eux, étaient à jour. Un README qui sous-annonce ne casse rien — il
désinforme, et on croit mesurer moins qu'on ne mesure.

Corrigé, et restructuré : les frontières, le routage simple, et `hors-perimetre`
à part — il n'a aucun skill attendu, ce que le tableau ne savait pas exprimer.

`validate.py` refuse désormais un cas d'éval absent de son README : ce
décalage-là ne peut plus revenir.

Ajout d'un protocole de mesure **à la main**, avec les dix prompts : le harnais
`claude plugin eval` est en accès anticipé et peut ne pas être activé sur un
compte. Il automatise la mesure, il ne la conditionne pas.

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
