# 1. Choisir le bon outil

Avant d'écrire un skill, vérifie que c'est bien un skill qu'il te faut. Six
mécanismes différents, six usages. Les confondre est la première cause de
« j'ai écrit un truc et ça ne change rien ».

| Mécanisme | Ce que ça donne | Chargé quand | Pour quoi |
|---|---|---|---|
| **CLAUDE.md** | Contexte permanent, toujours visible | À chaque tour, tout le temps | Conventions du repo, commandes de build, ton par défaut |
| **Skill** | Un savoir-faire tâche-par-tâche, chargé à la demande | Quand la `description` matche, ou via `/nom` | Un workflow répétable avec un format de sortie précis |
| **Plugin** | L'emballage : skills + agents + hooks + MCP, versionné | Une fois installé, partout | Partager, versionner, retrouver tes skills sur toutes tes machines |
| **Subagent** (`agents/`) | Un contexte isolé, son propre prompt système et ses outils | Quand tu délègues une tâche | Explorations larges, tâches longues qui pollueraient le contexte |
| **Hook** | Du code exécuté par le harness, pas par le modèle | Sur un événement (avant/après un outil) | « À chaque fois que X, fais Y » — déterministe, non négociable |
| **MCP** | Des outils externes (API, bases, SaaS) | Serveur connecté | Accéder à des données ou des systèmes hors du repo |

## La distinction qui compte : skill vs plugin

Ce n'est **pas** un choix exclusif.

- Un **skill** est le contenu : un dossier avec un `SKILL.md` qui dit à Claude
  comment faire une chose précise.
- Un **plugin** est le contenant : un dossier avec un manifeste
  `.claude-plugin/plugin.json` qui regroupe un ou plusieurs skills (plus
  éventuellement des agents, des hooks, un serveur MCP, des réglages) et qui
  s'installe, se versionne et se partage d'un bloc.

Tu écris toujours des skills. La question est seulement : où les poser ?

| Emplacement | Portée | Limite |
|---|---|---|
| `~/.claude/skills/<nom>/SKILL.md` | Toi, sur **cette machine** | Ne suit pas dans les sessions cloud / Cowork |
| `.claude/skills/<nom>/SKILL.md` dans un repo | Tous ceux qui clonent ce repo | Ne sert que dans ce repo |
| `plugins/<plugin>/skills/<nom>/SKILL.md` | Partout où le plugin est installé | Demande un manifeste + un marketplace |

**Pour ce repo, on prend la voie plugin.** Raison : tes skills sont
transversaux (ils ne concernent pas un projet en particulier), tu veux les
retrouver sur toutes tes machines et dans les sessions web, et tu veux pouvoir
les faire évoluer sans copier-coller des dossiers. Le prix à payer est un
fichier de manifeste. C'est tout.

Effet de bord à connaître : les skills d'un plugin sont **namespacés**. Un skill
`note-client` dans le plugin `hat` s'invoque `/hat:note-client`. C'est ce qui
évite les collisions de noms — et c'est aussi ta première ligne de défense
contre les skills qui se marchent dessus.

## Le test en trois questions

1. **Est-ce que ça doit s'appliquer *tout le temps*, sans que je le demande ?**
   → CLAUDE.md (dans un repo) ou mémoire. Pas un skill.
2. **Est-ce que ça doit se déclencher *tout seul*, de façon garantie, même si
   le modèle « n'y pense pas » ?**
   → Hook. Un skill peut toujours ne pas se déclencher ; un hook, non.
3. **Est-ce que c'est une tâche que je refais régulièrement, avec un résultat
   qui a une forme reconnaissable ?**
   → Skill. C'est le cœur de cible.

Si tu réponds « c'est une tâche, mais elle est unique », ne fais pas de skill :
écris un bon prompt. Un skill ne se rentabilise qu'à partir de la troisième ou
quatrième répétition.

---

Suite : [02-guide-ecriture.md](02-guide-ecriture.md) — écrire un skill qui se déclenche au bon moment et ne dérive pas
