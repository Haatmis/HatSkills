# Guide rapide — plugin `roblox`

> Version **0.15.0** · 9 skills · [Journal des versions](CHANGELOG.md)

Un assistant de développement de jeux Roblox : il cadre, code, debugge,
modélise et anime, en respectant toujours les mêmes conventions — et il vérifie
dans Studio avant de te rendre quoi que ce soit.

## Installer et mettre à jour

```
/plugin marketplace add haatmis/HatSkills
/plugin install roblox@hatskills
```

Après chaque mise à jour du repo :

```
/plugin update roblox@hatskills
```

⚠ Sans cette commande, tu restes sur ta version installée. Vérifie le numéro
en tête de ce guide contre celui du `/plugin` : s'ils diffèrent, tu n'as pas
les dernières corrections.

## Les 9 skills

Tu n'as normalement **rien à taper** : ils se déclenchent seuls sur ce que tu
écris. La colonne du milieu montre le genre de phrase qui les appelle.

| Skill | Tu écris quelque chose comme… | Tu obtiens |
|---|---|---|
| `game-design` | « ajoute un système de combat » | Une spec dans `docs/design/` : règles, chiffres justifiés, cas limites — **avant** tout code |
| `feature` | « exécute le plan », « j'ai mis les IDs » | L'exécution de la spec, étape par étape, chacune vérifiée dans Studio |
| `code` | « ajoute un RemoteEvent », « un script qui… » | Du Luau vanilla, typé, vérifié dans Studio, avec les chemins d'instance |
| `debug` | « ça marche pas », « le shop déconne » | Le bug reproduit dans Studio, la cause racine, le correctif minimal |
| `vfx` | « des particules quand on tape » | Un preset réutilisable dans `src/shared/VFX/`, cohérent avec ta charte |
| `hat3d` | « fais-moi un coffre en 3D » | Un `model.json`, une préview HTML à valider, un `build.lua` pour Studio |
| `anim` | « une animation de coup », « le perso reste droit quand il frappe » | Un `KeyframeSequence` à publier en deux clics, et le câblage qui va avec |
| `atelier` | « fais-en un skill », « consolide le journal » | Un nouveau skill après interview, ou les leçons promues dans les skills existants |
| `help` | `/roblox:help` | Cette page, dans ton navigateur |

Pour forcer l'un d'eux, tape son nom : `/roblox:game-design je voudrais…`

Et pour relire cette page à tout moment : **`/roblox:help`**. Elle est regénérée à chaque appel depuis ce fichier, donc jamais périmée.

## Ce qui décide si un skill t'aide

Ce n'est pas la taille de ton jeu, ni la difficulté de la tâche. C'est **à quel
point ta demande laisse des choses non dites.**

« Ajoute un système de dégâts » ne dit pas combien, ni à qui, ni ce qu'on voit
quand ça touche. Tout ce que le skill porte — les questions à poser, l'ordre
des étapes, ce qui doit être vérifié — remplace du va-et-vient avec toi. Le
gain est maximal.

« Ajoute un `print` dans cette fonction » ne laisse rien de non dit. Il n'y a
rien à cadrer, et le skill ne ferait que coûter son contenu pour rien. C'est
pour ça qu'il ne se déclenche pas, et c'est normal.

Entre les deux, tu peux le sentir à une chose : **si tu sais déjà exactement
quel fichier va changer et comment, tu n'as pas besoin d'un skill.** Si tu
devrais d'abord en discuter avec quelqu'un, tu es au bon endroit.

## Ce que ça te coûte

Un skill n'est pas gratuit : son contenu est rechargé à chaque déclenchement,
et tu le paies en tokens. Trois niveaux, du moins cher au plus cher :

- **Les descriptions** (~1700 tokens) sont là en permanence. C'est le prix
  d'entrée pour que le bon skill parte tout seul.
- **Le corps d'un skill** (~3000 tokens) n'arrive que quand il se déclenche.
- **Les fiches de référence** ne se chargent que par la section utile — depuis
  la `0.11.0`. Avant, une demande de VFX chargeait la boîte à outils entière,
  soit plus cher que le skill lui-même pour un contenu utilisé au cinquième.

Si une demande te paraît trop simple pour mériter tout ça, elle l'est
probablement : voir la section précédente.

## Le parcours d'une feature

```
« ajoute un système pour taper les autres joueurs »
        │
        ▼
  game-design ──► docs/design/combat.md      règles, dégâts, cooldown, cas limites
        │
        ▼
  feature ──► découpe et exécute             serveur AVANT client, toujours
        │         ├─► hat3d   l'arme, si elle n'existe pas
        │         ├─► code    config → serveur → Remotes → client
        │         ├─► vfx     l'impact
        │         └─► debug   si une étape casse
        ▼
  un système qui tourne + la liste de ce qu'il te reste à fournir
```

## Avant d'agir, il reformule — parfois

Quand ta demande admet plusieurs lectures, le skill répond d'abord une ligne :
« Je comprends : … ». Corrige-la si c'est faux, et tu viens d'éviter un
malentendu à 400 lignes.

Il ne le fait que si ça change quelque chose — la demande nomme un système,
un « qui » reste implicite, ou le travail dépasse un fichier. Sur « ajoute un
print », il fait le travail sans commentaire.

## Les trois fichiers qui comptent dans ton jeu

| Fichier | À quoi il sert |
|---|---|
| `src/shared/Config/Assets.luau` | Les IDs d'animations, de sons, de meshes. Un vrai ID pris dans la Toolbox = provisoire, sa provenance est en commentaire. Un `0` = à fournir par toi. Le code saute proprement ce qui manque, donc **le jeu tourne sans** |
| `src/shared/VFX/Style.luau` | Ta charte visuelle : palette, durées, densité. Tous les effets en dérivent — tu changes le style du jeu entier ici |
| `docs/design/*.md` | Les specs. `code` les lit avant d'écrire, `debug` avant de diagnostiquer — un comportement conforme à la spec n'est pas un bug |

**Le cycle des assets** : Claude ne peut ni publier une animation, ni créer un
son. Il te livre un système complet avec des `0`, tu remplis quand tu veux, tu
dis « reprends », et seuls les branchements concernés sont revérifiés.

## Il te demande comment le joueur voit ce qui se passe

Une mécanique qu'on ne peut pas lire n'existe pas : si tu infliges 20 dégâts et
que rien ne le dit, le joueur croit que la feature est cassée.

`game-design` remplit donc une section **Retour joueur** dans chaque spec —
comment le joueur sait que son action a marché, qu'il subit quelque chose, et
où il en est. Et `vfx` sait que **décorer et informer sont deux métiers** : un
effet décoratif peut être discret, une pastille de dégâts doit être *lue* en un
tiers de seconde, ne pas se superposer à elle-même, et disparaître en moins
d'une seconde.

Depuis la `0.9.0`, `vfx` vise aussi **le haut plutôt que le milieu** : un effet
trop discret est indistinguable d'un effet absent, et c'est le retour le plus
fréquent après livraison. Il te donne un réglage pour baisser — dans l'autre
sens, il faudrait d'abord que tu devines qu'il manque quelque chose.

## Il pense à la perf en écrivant, pas après

Quatre décisions de structure sont prises au moment d'écrire, parce qu'elles ne
se rattrapent pas ensuite — elles se réécrivent : un événement plutôt qu'une
boucle par frame, le réseau compté plutôt qu'estimé, les objets créés en boucle
recyclés, et ce qui n'a pas besoin d'autorité déplacé sur le client.

En revanche il **ne micro-optimise pas** : pas de service mis en local, pas de
`ipairs` par réflexe. Ça abîme la lisibilité pour un gain que personne n'a
mesuré. Si la perf devient vraiment le sujet, il sait où sont les vrais coûts
et comment les mesurer.

Ta spec porte maintenant une ligne **Échelle** — combien de joueurs, combien
d'instances au pic. C'est elle qui décide de la structure : un système pour 4
joueurs et un pour 40 ne s'écrivent pas pareil.

## Le journal, en trois lignes

Quand tu corriges Claude, ou que Studio révèle une erreur de sa part, la leçon
part dans un journal. À 8 leçons, il te propose `/roblox:atelier`, qui les
promeut dans les skills — **avec ton accord sur le diff**. C'est comme ça que
le plugin s'améliore ; rien ne bouge tout seul.

**Le journal ne suit pas tes machines par défaut.** Il vit dans un dossier
local, et une session cloud le perd quand son conteneur est recyclé. Une ligne
dans ton profil PowerShell le règle une fois pour toutes :

```powershell
$env:HATSKILLS_JOURNAL_DIR = "C:\...\HatSkills\.journal"
```

Il devient alors versionné : il suit tes machines, il a un historique, et deux
machines qui divergent fusionnent sans conflit.

**Et il ne retient que ce que Claude a observé lui-même** — une correction que
tu lui as faite, une erreur que la vérification a révélée. Jamais une consigne
trouvée dans un fichier, un commentaire ou une page web : ce sont des données,
pas des instructions. À la consolidation, toute leçon qui demanderait
d'exécuter quelque chose ou d'affaiblir une vérification est refusée **et
signalée**, pas écartée en silence.

## Il vérifie le code sans ouvrir Studio

Studio fermé, ou le MCP pas connecté ? Une partie du contrôle se fait quand
même. `luau_check.py` lit la table des API dépréciées du plugin et balaye ton
`src/` : `wait()`, `spawn()`, `BodyVelocity`, `:connect()`, `game.Workspace` et
une cinquantaine d'autres, avec leur remplaçant exact.

```bash
python3 "<plugin>/scripts/luau_check.py" --dans src
```

Ça marche aussi sur du code écrit **avant** que tu installes le plugin — c'est
souvent là qu'il y en a le plus. Et `code` le passe systématiquement avant de
te rendre quoi que ce soit : la règle « zéro API dépréciée » ne dépend plus de
ce dont Claude se souvient au bon moment.

## Il sait dire ce qu'il a vraiment vérifié

Avant, c'était binaire : « vérifié dans Studio », ou un aveu que le MCP
manquait. Depuis la `0.15.0`, il annonce un **mode** :

- **plein** — Studio ouvert, le code a tourné, l'Output est lu ;
- **réduit** — pas de Studio, mais `luau_check` est passé et les IDs d'assets
  sont vérifiés auprès de Roblox ;
- **hors-ligne** — rien n'a tourné, relecture seule.

Ça évite les deux mensonges symétriques : annoncer « vérifié » quand rien n'a
été exécuté, et annoncer « non vérifié » quand la moitié des contrôles sont
passés.

## Avant de publier une mise à jour

Les contrôles des skills s'arrêtent à « ce bout de travail est correct ». Quand
des gens jouent déjà à ton jeu, il y a autre chose à regarder — et une seule
chose vraiment irréversible : **les sauvegardes**.

La liste est dans `references/publication.md` du plugin, en cinq sections :
perte de données, exploits, ce qui casse pour les autres et pas pour toi,
performance, retour arrière. Lis la section qui correspond à ce que ta mise à
jour touche.

Si tu ne devais retenir qu'une ligne : **teste la migration de sauvegarde sur
un vieux compte, pas sur un compte neuf.** Un compte neuf ne révèle jamais un
bug de migration.

## Quand ça se passe mal

| Symptôme | Quoi faire |
|---|---|
| Le mauvais skill s'est déclenché | Dis-le : la leçon part au journal. Le remède est dans sa `description` |
| Aucun skill ne s'est déclenché | Appelle-le à la main : `/roblox:<nom>` |
| Le code livré n'a pas été vérifié | Studio doit être ouvert avec le MCP connecté. Sinon Claude te le dit — il ne fait jamais semblant |
| Un effet est moche | Normal : Claude ne voit pas le rendu. Il te donne les réglages à tourner |
| Une commande du plugin n'affiche rien, ou ouvre le Microsoft Store | Tu es sous Windows : `python3` y est un alias. Claude relance avec `py` — dis-le-lui s'il ne le fait pas |
| Tu n'as pas les dernières corrections | `/plugin update roblox@hatskills` |

## Il emprunte à la Toolbox plutôt que de te laisser dans le silence

Depuis la `0.12.0`, quand une feature a besoin d'un son, d'une image, d'un
modèle ou d'un mesh, Claude va en chercher un **vrai** dans la Toolbox Roblox
au lieu de poser `0` et d'attendre. Ton système sonne dès la première
exécution, et tu testes pour de bon au lieu de deviner.

Trois garanties :

- **Aucun identifiant inventé.** Chaque ID vient d'une réponse de Roblox,
  jamais de la mémoire de Claude. Un `rbxassetid://` inventé a l'air juste et
  ne charge rien — c'est le défaut le plus difficile à voir.
- **Aucun modèle scripté.** Un modèle de la Toolbox qui contient des scripts
  est écarté d'office : c'est le vecteur de backdoor le plus courant sur
  Roblox. Il faut le demander explicitement pour en avoir un.
- **L'emprunt est toujours signalé** — en commentaire dans `Assets.luau`, et
  dans la liste « À toi de fournir » en fin de réponse. Un placeholder trop
  crédible se fait oublier et part en production.

Les **animations** font exception, pour une raison plus embêtante : la Toolbox
en contient, mais Roblox lie une animation à son créateur. Celle de quelqu'un
d'autre ne se chargera pas dans ton jeu publié — et elle peut très bien marcher
dans Studio avant d'échouer pour tous les joueurs une fois en ligne. Elles
valent donc `0` jusqu'à ce que tu publies la tienne, sous le compte ou le
groupe qui possède le jeu.

Si une animation te fait ce coup-là, la cause se tranche sans ouvrir Studio :

```bash
python3 "<plugin>/scripts/toolbox.py" verifier --ids <id> --proprietaire "<ton compte>"
```

## Ce que le plugin ne fait pas

- **Juger un rendu visuel** — il construit et vérifie, tes yeux tranchent
- **Publier une animation ou créer un son** — ça passe par toi
- **Du level design** — `hat3d` fait des props, pas des maps
- **Tourner sans ton PC** — Studio est une application de bureau
