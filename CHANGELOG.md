# Journal des versions

Le plugin `roblox`. Une entrée par version publiée — et une version publiée à
chaque changement, sinon personne ne la reçoit.

## 0.18.0

**Seize leçons, dont sept qui disaient la même chose : l'instrument ment.**
Une session entière passée à mesurer dans Studio, et la moitié du journal
décrit non pas des bugs du jeu mais des bugs de la *mesure* — un viewport
réduit qui met `PreRender` à zéro et gèle `TweenService` pendant que
`Heartbeat` tourne à 144 ; une sonde qui attend que `Sound.TimePosition`
avance en mode Edit, où il n'avance jamais, et qui tourne jusqu'au délai du
MCP ; `Model:GetPivot()` qui rend un `WorldPivot` figé et rapporte « aucun
mouvement » sur des portes qui bougeaient ; `PlaybackLoudness` indépendant de
`Volume`.

Ces sept-là ne sont pas entrées dans un skill. Elles forment une nouvelle
section de `references/modes.md` — « Le mode plein ment aussi : vérifier
l'instrument » — parce qu'une référence se charge à la demande, quand on va
mesurer, alors qu'un corps de skill est rechargé à chaque déclenchement. Le
pavé « Faire confiance à son propre harnais » de `debug` y renvoie désormais
au lieu de le paraphraser.

**Les neuf autres sont allées dans `code` et `vfx`** : un `TweenService`
serveur ne se réplique pas ; une expérience à deux places ne nomme jamais sa
cible en dur et refuse explicitement la place courante ; `CollectionService`
publie ses tags progressivement, donc on attend que le compte se *stabilise* ;
un `ParticleEmitter` créé en Edit via le MCP n'émet rien en Play ; et la
recherche d'images de la Toolbox rend des Decals que `PreloadAsync` accepte et
qui ne rendent rien — ce que `vfx` recommandait sans réserve.

**Le plus instructif est le tri, encore une fois.** Les trois skills touchés
ont dépassé leur plafond du premier coup, et chercher de quoi payer a mis au
jour trois redites franches : cinq des neuf pièges de `vfx` étaient mot pour
mot dans le § 8 de sa propre fiche de référence ; le détail des pastilles de
dégâts aussi ; le retard de 0,35 s des `Sound` était déjà chiffré dans
`perf.md`, et `code` le répétait. Plus une redite interne dans `code`, qui
posait la validation des Remotes dans son contexte figé puis la reposait dans
ses pièges.

**Aucun plafond n'a été relevé.** Les corps de `code`, `feature` et `vfx`
finissent sous leur budget d'origine ; `vfx` y gagne même de la place alors
qu'il porte deux règles de plus. Une règle de production qui s'était égarée
dans `debug` — rendre la caméra `Scriptable` sur tous les chemins de sortie —
est remontée dans `code` au passage, et une règle de mesure qui traînait dans
`code` est descendue dans `modes.md`.

## 0.17.0

**Vingt leçons vidées du journal.** Deux mois de sessions sur un même jeu, et
le journal qui déborde. Le tri a été plus instructif que le contenu : huit des
vingt entrées décrivaient **le même symptôme sous trois angles**. « La poubelle
n'a ni couvercle ni roues », « Bin.Start ne tourne jamais », « l'écran titre ne
s'ouvre pas » — trois bugs, trois causes, un seul symptôme : *il ne se passe
rien au démarrage client*. Elles sont désormais un piège unique dans `code`, et
c'est ce regroupement, pas les règles prises une à une, qui les rendra
trouvables. Même chose pour trois leçons de physique devenues « régler la
physique à vue » : la vitesse lue dans `Touched` est post-collision, une zone
plus mince que vitesse/60 est traversée, une impulsion estimée à l'œil est
absorbée par le sol. Toutes disent *mesure d'abord*.

**Le serveur valide la surface, pas seulement la distance.** Deux incidents
distincts — une tache posée sur un joueur qui part et la laisse suspendue, un
coup de balai accepté en plein vide — pour la même cause : une position dans
la portée ne prouve pas qu'il y ait quelque chose là. Avec son corollaire, payé
cher le jour même : un contrôle ajouté pour en doubler un autre doit refaire
**la même géométrie** que lui, sinon il refuse ce que l'autre acceptait.

**Deux doublons retirés, pas compressés.** Les pièges `:SetAsync()` et
`game:BindToClose()` de `code` étaient déjà énoncés, avec leur raison, dans la
section `Exemple` du même fichier. Et `debug` renvoyait deux fois à
`symptomes-frequents.md` : une fois dans le `Contexte figé`, une fois à l'étape
4 — seule la seconde arrive au moment où c'est actionnable. Le piège « demander
à l'utilisateur où est le code » redisait l'étape 2. Trois retraits qui ne
coûtent rien.

**Trois plafonds relevés, et c'est le point à discuter.** `code` 3975 → 4615,
`debug` 2666 → 2830, `feature` 3460 → 3600. Les trois étaient saturés à moins
de quinze tokens près : vingt leçons ne rentraient pas gratuitement. L'autre
voie était de raboter des sections qu'aucune leçon n'avait désignées, pour
faire tenir le total — de la compression cosmétique payée par une perte de
précision ailleurs. Le choix assumé est de relever, et de le dire ici plutôt
que de le dissimuler dans un diff de reformulation. À surveiller : `code` est
maintenant le deuxième skill le plus lourd après `hat3d`.

**Ce qui n'a pas été promu.** Une leçon sur les simulations Verlet — corriger
`position` **et** `previous`, sinon chaque contact injecte de l'énergie. Juste,
vérifiée, et écartée : une occurrence, dans un système d'un seul jeu. La mettre
dans `code` la ferait charger à chaque `print` demandé. Elle reste en
commentaire là où elle s'applique.

## 0.16.0

**`hat3d` rentre dans la famille.** Il était le seul skill à ne venir de la
méthode : ni `Situation`, ni `Contexte figé`, ni `Exemple`, un `Workflow` au
lieu d'une `Procédure` et des `Rappels` au lieu de `Pièges`. Ce n'était pas
cosmétique : `atelier` consolide les leçons dans le `Contexte figé`, et `hat3d`
n'en avait pas — une leçon apprise sur la 3D n'avait littéralement aucun
endroit où aller, et serait restée dans le journal pour toujours.

Et **ça n'a rien coûté**. La restructuration plus un exemple entrée → sortie
sont payés par la section « génération d'image IA », descendue en fiche : 441
tokens qui se chargeaient à chaque modèle demandé, y compris pour les
utilisateurs sans clé d'API — c'est-à-dire presque tout le monde.

**Le garde-fou « Exemple » ne gardait rien.** Il cherchait le mot « exemple »
n'importe où dans le corps. Chez `hat3d`, une seule occurrence, dans un chemin
de fichier, le satisfaisait alors qu'aucun exemple n'existait. Il exige
désormais une vraie section. Vérifié en la renommant : l'alerte tombe.

**Deux exclusions vers `anim`.** `vfx` et `hat3d` ne le nommaient pas.
Les deux paires sont fondées sur une phrase réellement prononcée — « quand on
frappe, il ne se passe rien » peut aller chez `vfx` comme chez `anim` ; « anime
la porte » et « anime le perso » ne visent pas le même skill. Coût : **55
tokens permanents**, payés à chaque tour. C'est un pari, et il est étiqueté
comme tel dans `budget.json` : si la campagne d'évals montre un bon routage
sans, ces 55 tokens sont à reprendre.

**La doctrine d'exclusion est réécrite, et elle dit maintenant l'inverse sur un
point.** On tenait que l'exclusion devait aller dans les deux sens. C'est
probablement faux : le modèle voit toutes les descriptions en même temps quand
il route, donc une exclusion à sens unique porte déjà l'information. La
confusion, elle, est souvent à sens unique — celui qui risque de prendre le
travail de l'autre doit le dire, pas l'inverse. Et nommer son voisin importe
son vocabulaire, donc **rapproche** les deux descriptions aux yeux du détecteur
de recouvrement. Les quinze asymétries actuelles restent donc en l'état, sauf
les deux ci-dessus. `CLAUDE.md` porte la doctrine et ses limites.

**Ce qui n'a pas avancé.** La doctrine d'exclusion n'a toujours jamais été
mesurée — ni l'ancienne version, ni la nouvelle. C'est la plus grosse croyance
non vérifiée du plugin, et elle gouverne le seul coût payé à chaque tour. La
campagne d'évals est le seul moyen d'en sortir, et elle n'a toujours pas tourné.

## 0.15.0

Trois emprunts à l'étude des skills Roblox concurrents et de la doc officielle,
et un quatrième refusé faute de pouvoir en constater les dégâts.

**Un neuvième skill : `anim`.** C'était le trou le plus visible du plugin —
aucune occurrence d'anticipation, de pose clé ou de breakdown nulle part. Il
construit un `KeyframeSequence` que l'utilisateur publie en deux clics, ce qui
résout au passage le problème de propriété de la `0.13.0` : l'animation naît
sous le bon compte. Il **lit le rig au lieu de le supposer** — la doc officielle
donne la hiérarchie des parts mais pas les noms des `Motor6D`, et un `Pose` mal
nommé est ignoré en silence, sans la moindre erreur.

La règle qui compte le plus est celle de l'anticipation : un coup sans petit
mouvement inverse n'a pas de poids. C'est probablement une partie de ce qui
manquait au système de combat, avant même les particules.

**L'échelle de modes.** « Vérifié dans Studio » était binaire : vérifié, ou un
aveu que le MCP manquait. Or l'absence de Studio n'empêche que les contrôles qui
demandent une exécution. Trois modes — plein, réduit, hors-ligne — et le compte
rendu dit lequel. Ça ferme les deux mensonges symétriques : annoncer « vérifié »
quand rien n'a tourné, et « non vérifié » quand `luau_check` est passé.
`references/modes.md`. `debug` n'a pas été touché : sa règle « un diagnostic non
reproduit est une hypothèse » disait déjà mieux la même chose.

**Une checklist de publication.** Les contrôles des skills s'arrêtent à « ce
bout de travail est correct ». Quand des gens jouent déjà, il y a autre chose —
et une seule chose irréversible, la sauvegarde. Cinq sections lisibles
séparément, `references/publication.md`.

**Ce qui a été vérifié et n'a pas tenu.** Deux « règles pro » reviennent partout
sur les blogs VFX Roblox : superposer trois à cinq emitters par effet, et
bloquer le mouvement avec une texture blanche avant de s'occuper des textures.
Le tutoriel d'explosion officiel de Roblox utilise **un seul** emitter, le
cursus artiste officiel n'aborde pas la superposition, et son ordre de travail
est couleur → texture → taille → vitesse, l'inverse. Aucune des deux n'entre
dans `vfx`. Le seul détail concret trouvé côté superposition — régler `ZOffset`
pour ordonner feu et fumée — y était déjà.

**Ce qui n'a pas avancé.** `hat3d` devait passer en routeur : c'est le plus gros
skill, 6 136 tokens, et son `## Workflow` en fait 3 435 à lui seul, soit 56 %.
Mesure faite, c'est une procédure séquentielle — cadrer, modéliser, vérifier,
valider, finir, construire. La découper contredirait la raison même pour
laquelle `style-detaille.md` a sa dispense en `0.11.0`, et je ne peux pas juger
un modèle 3D pour constater la dégradation. Reporté, pas abandonné : la décision
revient à quelqu'un qui peut regarder le rendu.

Le budget a servi quatre fois dans cette version. Deux fois il a forcé une
compression (les renvois de modes, écrits à 89 tokens, livrés à 53), une fois il
a fait retirer un doublon réel dans `feature` — un piège qui redisait le
`Contexte figé` à un chiffre près — et une fois il a fallu relever
`total_descriptions` pour le neuvième skill. Aucune de ces quatre fois n'était
prévue en commençant.

## 0.14.0

**La règle qui interdit de grossir devient mécanique.** `CLAUDE.md` dit depuis
toujours qu'on ne rajoute pas une règle à un skill sans en retirer une autre.
Cette règle a été enfreinte deux fois en une seule session, à la main, par
celui-là même qui l'avait écrite — `vfx` +6 lignes, `feature` +17. Une règle
tenue à l'honneur et respectée une fois sur deux n'est pas une règle.
`budget.json` fixe désormais un plafond par skill et par couche, sans marge, et
`validate.py` échoue au dépassement.

Le garde-fou s'est déclenché sur la toute première modification qui a suivi sa
pose. Sur `debug`, trois tokens de trop : retirés ailleurs plutôt que tolérés.
Sur `hat3d` et `code`, les plafonds ont été relevés — chaque hausse est écrite
dans `budget.json` avec ce qu'elle achète. C'est le comportement voulu :
l'arbitrage est forcé, pas interdit.

**`luau_check.py` remplace un espoir par un verdict.** « Zéro API dépréciée »
est la règle la plus répétée du plugin, et elle reposait entièrement sur la
mémoire du modèle au bon moment. Le script lit la table du skill `code` — pas
une copie qui divergerait — et balaye le projet : 52 motifs, le remplaçant
exact, `Studio fermé`. Il attrape aussi le code écrit avant l'installation du
plugin, qui est souvent le plus atteint. `code` le passe avant de rendre.

**Les fiches de `hat3d` se lisent par section.** `animations.md` et
`finition.md` ont un sommaire : 2 432 → 447 et 3 007 → 632 tokens, soit **4 360
évités** sur le chemin le plus cher du plugin. Même levier que la `0.11.0`,
appliqué là où il n'avait pas été fini. `part-schema.md` reste entier : c'est
un schéma, en sauter un morceau produit un fichier invalide.

**Vingt tests, là où rien ne surveillait les surveillants.** `validate.py`
police les skills ; personne ne policait `validate.py`. Trois bugs réels y sont
passés, et chacun a maintenant son test : le plantage d'encodage *après* avoir
affiché « OK », la déduplication du journal cassée par les accents, et le
vérificateur Luau qui hurlait sur `Instance.new("Part")` — ce dernier attrapé
pendant son propre développement, avant publication.

**Une règle déclarée obligatoire et jamais vérifiée.** `CLAUDE.md` exige la
section « Apprendre de la session ». `debug` ne l'avait pas : sa capture était
enfouie dans la `Procédure`, là où `atelier` ne la cherche pas. Elle a sa
section, et `validate.py` refuse désormais un skill qui n'en a pas.

**Ce qui n'a pas avancé.** Les ~1 670 tokens de descriptions restent intacts :
c'est le seul coût payé à chaque tour, donc la cible évidente, et c'est aussi le
seul texte qui décide du déclenchement. Les toucher sans campagne d'évals, ce
serait dégrader la seule chose qui compte sans pouvoir le constater. Rien de
tout ça n'a tourné dans Studio ; `luau_check` a été éprouvé sur des fichiers
fabriqués, pas sur un vrai projet.

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
