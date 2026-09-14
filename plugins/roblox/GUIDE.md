# Guide rapide — plugin `roblox`

> Version **0.5.0** · 8 skills · [Journal des versions](CHANGELOG.md)

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

## Les 8 skills

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
| `atelier` | « fais-en un skill », « consolide le journal » | Un nouveau skill après interview, ou les leçons promues dans les skills existants |
| `help` | `/roblox:help` | Cette page, dans ton navigateur |

Pour forcer l'un d'eux, tape son nom : `/roblox:game-design je voudrais…`

Et pour relire cette page à tout moment : **`/roblox:help`**. Elle est regénérée à chaque appel depuis ce fichier, donc jamais périmée.

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
| `src/shared/Config/Assets.luau` | Les IDs d'animations, de sons, de meshes. Un `0` = à fournir. Le code saute proprement ce qui manque, donc **le jeu tourne sans** |
| `src/shared/VFX/Style.luau` | Ta charte visuelle : palette, durées, densité. Tous les effets en dérivent — tu changes le style du jeu entier ici |
| `docs/design/*.md` | Les specs. `code` les lit avant d'écrire, `debug` avant de diagnostiquer — un comportement conforme à la spec n'est pas un bug |

**Le cycle des assets** : Claude ne peut ni publier une animation, ni créer un
son. Il te livre un système complet avec des `0`, tu remplis quand tu veux, tu
dis « reprends », et seuls les branchements concernés sont revérifiés.

## Le journal, en trois lignes

Quand tu corriges Claude, ou que Studio révèle une erreur de sa part, la leçon
part dans un journal. À 8 leçons, il te propose `/roblox:atelier`, qui les
promeut dans les skills — **avec ton accord sur le diff**. C'est comme ça que
le plugin s'améliore ; rien ne bouge tout seul.

Pour que le journal suive d'une machine à l'autre :

```powershell
$env:HATSKILLS_JOURNAL_DIR = "C:\...\HatSkills\.journal"
```

## Quand ça se passe mal

| Symptôme | Quoi faire |
|---|---|
| Le mauvais skill s'est déclenché | Dis-le : la leçon part au journal. Le remède est dans sa `description` |
| Aucun skill ne s'est déclenché | Appelle-le à la main : `/roblox:<nom>` |
| Le code livré n'a pas été vérifié | Studio doit être ouvert avec le MCP connecté. Sinon Claude te le dit — il ne fait jamais semblant |
| Un effet est moche | Normal : Claude ne voit pas le rendu. Il te donne les réglages à tourner |
| Tu n'as pas les dernières corrections | `/plugin update roblox@hatskills` |

## Ce que le plugin ne fait pas

- **Juger un rendu visuel** — il construit et vérifie, tes yeux tranchent
- **Publier une animation ou créer un son** — ça passe par toi
- **Du level design** — `hat3d` fait des props, pas des maps
- **Tourner sans ton PC** — Studio est une application de bureau
