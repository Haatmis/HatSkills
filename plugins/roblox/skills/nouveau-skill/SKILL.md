---
name: nouveau-skill
description: >
  Crée un nouveau skill dans le repo HatSkills, complet et conforme aux
  conventions maison (description qui déclenche, contexte figé, gabarit de
  sortie, exemple, auto-vérification). Utilise ce skill dès que l'utilisateur
  veut créer, ajouter, écrire ou scaffolder un skill, dit « transforme ça en
  skill », « j'en ai marre de retaper ça », « fais-en un skill », ou décrit un
  workflow qu'il répète — même sans prononcer le mot « skill ». N'utilise pas
  ce skill pour améliorer un skill qui existe déjà, à partir du journal
  d'apprentissage ou d'une correction (voir affiner), ni pour créer un hook,
  un subagent ou un serveur MCP.
disable-model-invocation: false
---

# Nouveau skill

## Situation

L'utilisateur a un geste qu'il répète et veut le figer. Le piège est d'écrire
trop vite : un skill produit d'après une description vague se déclenche mal et
dérive, et le corriger coûte plus cher que de l'avoir bien cadré. L'interview
compte autant que la rédaction.

## Contexte figé

- **Repo** : `HatSkills`. Les skills vont dans `plugins/roblox/skills/<nom>/SKILL.md`.
- **Langue** : français, y compris dans le frontmatter.
- **Nom** : kebab-case, et `name` du frontmatter identique au nom du dossier.
- **Budget** : corps < 500 lignes ; `description` + `when_to_use` ≤ 1 536 car.
- **Un skill = un livrable.** S'il faut deux mots pour nommer la sortie, le
  périmètre est trop large : découpe.
- **Ne jamais inventer le contexte métier.** Ce qu'on ne sait pas, on le
  demande — un contexte figé deviné est pire qu'absent, parce qu'il sera
  appliqué avec aplomb.

## Procédure

1. **Vérifie que c'est bien un skill.** Si ça doit s'appliquer tout le temps →
   CLAUDE.md. Si le déclenchement doit être garanti et déterministe → hook. Si
   c'est un cas unique → un bon prompt suffit. Dis-le franchement plutôt que de
   produire un skill inutile.
2. **Interviewe.** Quatre questions, pas plus :
   - Quel est le livrable, en un mot ?
   - Quelles phrases tapes-tu réellement quand tu veux ça ?
   - Qu'est-ce que tu te retrouves à re-préciser à chaque fois ?
   - À quoi ressemble une bonne sortie ? (demande un exemple réel)
3. **Cherche les voisins.** Liste les skills déjà présents dans
   `plugins/roblox/skills/` et repère ceux dont le vocabulaire de déclenchement
   recoupe le nouveau. Prévois une exclusion croisée dans les deux sens.
4. **Écris la description** selon la formule : ce que ça produit → quand s'en
   servir (phrases réelles, ton un peu insistant) → quand ne pas s'en servir
   (en nommant le skill voisin).
5. **Écris le corps** au gabarit ci-dessous. Tout ce que l'utilisateur a
   répondu à la question 3 de l'interview va dans `Contexte figé`.
6. **Ajoute l'exclusion croisée** dans la description du ou des skills voisins
   identifiés à l'étape 3.
7. **Lance `python3 scripts/validate.py`** et corrige jusqu'à zéro erreur.
8. **Propose 2-3 prompts de test** dont au moins un cas piège (un prompt qui
   ressemble au déclencheur mais doit partir ailleurs), et demande à
   l'utilisateur s'ils sont réalistes avant de les jouer.

## Format de sortie

Crée `plugins/roblox/skills/<nom>/SKILL.md` exactement sur ce gabarit :

```markdown
---
name: <nom-du-dossier>
description: >
  <Ce que ça produit, une phrase à l'impératif.> Utilise ce skill quand
  <déclencheurs concrets, phrases réelles> — même si <X> n'est pas demandé
  explicitement. N'utilise pas ce skill pour <cas voisin> (voir <autre-skill>).
---

# <Nom>

## Situation
<1-2 phrases : où on est, ce qui compte ici.>

## Contexte figé
- Public :
- Ton :
- Contraintes :
- Vocabulaire imposé / interdit :

## Procédure
1. <étape vérifiable, à l'impératif>

## Format de sortie
<gabarit exact, copiable>

## Exemple
Entrée : <réelle>
Sortie : <complète>

## Pièges
- <erreur fréquente> — <pourquoi c'est faux ici>

## Avant de rendre
- [ ] <vérification concrète>
```

Puis affiche à l'utilisateur : le chemin créé, la description en entier, et le
résultat de `validate.py`.

## Exemple

Entrée :
```
J'en ai marre de reformater mes notes de réunion client à chaque fois.
```

Sortie (après interview) : `plugins/roblox/skills/compte-rendu-client/SKILL.md`,
dont la description est

```
Rédige un compte rendu de réunion client au format interne (décisions, actions
avec porteur et échéance, points en suspens). Utilise ce skill dès que
l'utilisateur mentionne un CR, un débrief, des notes de réunion, ou colle une
transcription à mettre au propre — même sans demander un « compte rendu ».
N'utilise pas ce skill pour une note interne d'équipe (voir note-interne).
```

et dont le `Contexte figé` contient les réponses données pendant l'interview :
le client est nommé en toutes lettres au premier paragraphe, les dates sont au
format JJ/MM, aucune action n'est listée sans porteur.

## Pièges

- **Écrire le corps avant la description.** La description décide du
  déclenchement ; un corps parfait derrière une description vague ne sert
  jamais. Écris-la d'abord, relis-la en dernier.
- **Mettre « quand utiliser ce skill » dans le corps.** Le corps n'est lu
  qu'une fois la décision prise — c'est trop tard pour influencer quoi que ce
  soit.
- **Décrire la sortie en prose au lieu de donner un gabarit.** La prose laisse
  de la place à l'improvisation, le gabarit non. C'est le premier remède
  contre la dérive.
- **Empiler les `MUST` en majuscules.** Ça se dilue. Une raison courte
  (« sinon le client ne sait pas qui porte l'action ») tient mieux, parce
  qu'elle se généralise aux cas non prévus.
- **Oublier l'exclusion croisée.** Un skill qui dit « pas pour B » sans que B
  dise « pas pour A » laisse la collision intacte dans un sens sur deux.

## Avant de rendre

- [ ] `name` == nom du dossier, en kebab-case.
- [ ] La description dit ce que ça produit, quand, et quand **pas**.
- [ ] Les phrases de déclenchement sont celles de l'utilisateur, pas les miennes.
- [ ] `Contexte figé` contient tout ce qu'il a dit re-préciser à chaque fois.
- [ ] Il y a un gabarit de sortie exact et un exemple entrée → sortie réel.
- [ ] L'exclusion croisée est posée **dans les deux sens**.
- [ ] `python3 scripts/validate.py` ne renvoie aucune erreur.
