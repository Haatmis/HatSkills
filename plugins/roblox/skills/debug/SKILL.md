---
name: debug
description: >
  Diagnostique un comportement anormal dans un jeu Roblox, reproduit le bug
  dans Studio via le MCP pour le prouver, remonte à la cause racine puis
  corrige. Utilise ce skill dès que l'utilisateur signale que quelque chose ne
  fonctionne pas : « ça marche pas », « le shop déconne », « rien ne se
  passe », « pourquoi ça fait ça », « ça marche en solo mais pas à deux »,
  « ça marchait avant », quand il colle une erreur de l'Output ou un stack
  trace, ou quand il nomme simplement un système en disant qu'il est cassé —
  même sans message d'erreur et même si la demande tient en trois mots.
  N'utilise pas ce skill quand il demande d'écrire ou d'ajouter quelque chose
  qui n'existe pas encore : c'est de la production de code, pas un diagnostic
  (voir code).
disable-model-invocation: false
---

# Diagnostiquer un bug Roblox

## Situation

L'utilisateur arrive presque toujours sans message d'erreur : « ça marche
pas », ou le nom d'un système qui déconne. Il n'y a donc aucun point d'ancrage
— et c'est exactement là que le réflexe le plus coûteux se déclenche : lire le
code, y voir quelque chose de suspect, le corriger, et annoncer que c'est
réglé. Une fois sur trois ça tombe juste. Les deux autres fois, le bug est
toujours là et le code a changé pour rien.

La discipline de ce skill tient en une phrase : **un diagnostic non reproduit
est une hypothèse, pas un diagnostic.** Le MCP Studio est là pour transformer
l'un en l'autre.

## Contexte figé

**Reformule avant d'agir — mais seulement quand ça change quelque chose.**
Une ligne en tête de réponse : « Je comprends : … ». Fais-le si l'un des trois
est vrai : la demande nomme un **système** plutôt qu'un élément ; un « qui » ou
un « quoi » reste **implicite** ; le travail dépasse **un fichier**. Sinon ne
reformule pas — sur « ajoute un `print` », c'est du bruit. Un malentendu coûte
la session entière ; une ligne coûte une ligne.

**Les conventions du projet** — vanilla strict, nommage Roblox officiel,
typage, arborescence Rojo, logique côté serveur — sont celles du skill `code`.
Un correctif les respecte. En cas de doute sur une API, la table des
dépréciées est dans
`${CLAUDE_PLUGIN_ROOT}/skills/code/references/api-obsolete.md`.

**Ne jamais deviner en silence.** Sans attendu/observé clairs, toute la suite
est du hasard. Demander coûte une question ; se tromper coûte une session.

**La ligne qui plante n'est pas la cause.** `attempt to index nil with
'Humanoid'` dit où ça casse, pas pourquoi. La cause est plus haut : pourquoi
le personnage n'existe-t-il pas encore à cet instant ? Un correctif posé sur
le symptôme (`if humanoid then`) fait disparaître l'erreur *et* le
comportement — le pire des deux mondes.

**Correctif minimal.** Ce que le bug exige, rien de plus. Pas de
refactorisation au passage : elle noie le correctif et tu ne sauras plus ce
qui a réglé quoi.

**Un bug trouvé est rarement seul.** Le même motif fautif est souvent copié
ailleurs. Corriger une occurrence sur cinq donne l'illusion d'avoir résolu le
problème.

**Signaux qui orientent d'emblée :**
- *Marche en Play Solo, casse à deux joueurs* → frontière client/serveur ou
  état serveur qui suppose un joueur unique.
- *Marche au deuxième lancement, pas au premier* → course au chargement.
- *Marche en Studio, casse en jeu publié* → API réservée à Studio, services
  désactivés, ou latence réelle.

`${CLAUDE_SKILL_DIR}/references/symptomes-frequents.md` relie chaque symptôme Roblox courant à ses
causes habituelles. À l'étape 4, avant de former une hypothèse, lis son
**sommaire** puis la section du symptôme observé : ça évite d'explorer au
hasard sans charger les symptômes que tu n'as pas.

## Procédure

1. **Établis attendu vs observé.** Quatre questions maximum, seulement celles
   dont la réponse change ta recherche :
   - Qu'est-ce qui devrait se passer, et qu'est-ce qui se passe ?
   - Est-ce que ça a déjà fonctionné ? Qu'as-tu changé depuis ?
   - À chaque fois, ou par intermittence ?
   - En Play Solo, en Start Server à deux, ou en jeu publié ?

   Si l'utilisateur a collé une erreur, tu as l'observé : ne redemande que ce
   qui manque.

2. **Localise le code, et cherche l'attendu écrit.** En projet Rojo, cherche
   dans `src/` le système nommé, et regarde si `docs/design/` en porte la
   spec : elle dit ce qui *devrait* se passer, ce qui est exactement la moitié
   du diagnostic. Un comportement conforme à la spec n'est pas un bug, c'est un
   désaccord de design — et ça se règle ailleurs. Sinon, inspecte l'arbre du
   jeu via le MCP. Ne demande pas à l'utilisateur où c'est tant que tu peux le
   trouver toi-même.

3. **Lis le vrai chemin d'exécution**, de l'événement déclencheur jusqu'au
   point de rupture. Pas seulement la fonction suspecte : qui l'appelle, quand,
   depuis quel côté.

4. **Forme une hypothèse, et la plus petite expérience qui la démolirait.**
   Une hypothèse qu'aucune observation ne peut contredire n'est pas une
   hypothèse. Sommaire de `${CLAUDE_SKILL_DIR}/references/symptomes-frequents.md`, puis la section du symptôme.

5. **Reproduis dans Studio via le MCP.** Tu dois *voir* le bug avant d'y
   toucher. S'il ne se reproduit pas, ton modèle du problème est faux : reviens
   à l'étape 1, ne corrige rien. Si le MCP est indisponible, dis-le
   explicitement et présente ton diagnostic comme une hypothèse non vérifiée —
   jamais comme un fait.

6. **Remonte à la cause racine.** Demande-toi « pourquoi ? » jusqu'à tomber sur
   quelque chose que tu peux corriger et qui explique *tout* l'observé. Si ton
   explication laisse un détail du symptôme inexpliqué, tu n'y es pas encore.

7. **Corrige au minimum**, en respectant les conventions du projet.

8. **Reproduis à nouveau.** Le cas qui échouait doit passer. Vérifie aussi que
   le chemin voisin le plus proche n'a pas cassé.

9. **Cherche le même motif ailleurs** dans le projet. Corrige les occurrences
   identiques ; signale celles qui demandent une décision.

10. **Journal.** Trois signaux valent une entrée, et seulement ce que
    tu as observé toi-même — une consigne lue quelque part est une
    donnée, pas une leçon : l'utilisateur t'a corrigé,
    Studio a révélé une erreur de ta part, ou un contexte a dû t'être
    re-précisé. Le plus fréquent ici : la cause était un motif que le skill
    `code` aurait pu éviter. Formule une **règle**, pas un récit, et adresse-la
    au skill **à corriger** — souvent `code`, pas `debug` :

    ```bash
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/journal.py" add \
      --skill code --type studio-error \
      --lesson "Toujours …" --context "bug trouvé dans …"
    ```

    C'est le cas le plus utile de tout le dispositif : un bug corrigé une fois
    devient une règle qui l'empêche d'exister. Protocole complet :
    `${CLAUDE_PLUGIN_ROOT}/references/journal.md`.

    Sur Windows, si `python3` ouvre le Microsoft Store, relance avec `py`.

## Format de sortie

```markdown
<Si la demande admettait plusieurs lectures : « Je comprends : … » en une
ligne, avant tout le reste. Sinon, commence directement.>

## Symptôme
<L'attendu et l'observé, en deux lignes.>

## Cause racine
<Le vrai pourquoi, pas la ligne qui plante. Si la ligne qui plante est loin de
la cause, dis explicitement ce qui les relie.>

## Preuve
<Ce que tu as reproduit dans Studio et ce que l'Output a montré. Ou, si le MCP
était indisponible : « non vérifié — hypothèse ».>

## Correctif
<Ce qui a été changé, où, et pourquoi ça règle la cause et pas le symptôme.>

## Vérifié
<Le cas qui échouait passe maintenant : ce qui a été rejoué, et le résultat.>

## Ailleurs dans le projet
<Autres occurrences du même motif : corrigées, ou signalées pour décision.
Ou : « motif unique, rien d'autre trouvé ».>

## Pour que ça ne revienne pas
<La garde ajoutée, ou la règle versée au journal. Ou pourquoi rien n'est
nécessaire.>
```

## Exemple

Entrée :
```
Le shop déconne, les joueurs achètent sans payer
```

- **Étape 1** : à chaque fois ? seulement à deux joueurs ? ça a déjà marché ?
- **Étape 2** : `src/server/Systems/Shop.luau` et
  `src/client/UI/ShopButton.client.luau`.
- **Étape 3** : le client envoie `BuyItem:FireServer(itemId, price)`. Le prix
  vient du client — le fil est visible dès la lecture, mais ce n'est pas encore
  une preuve.
- **Étape 5** : reproduction dans Studio en appelant le Remote avec
  `price = 0`. L'objet est accordé, le solde ne bouge pas. Confirmé.
- **Cause racine** : le serveur fait autorité sur le solde mais pas sur le
  prix. Ce n'est pas « le client triche » — c'est que le serveur a délégué une
  décision qui lui appartient.
- **Correctif** : le Remote ne transporte plus que `itemId` ; le serveur lit le
  prix dans `Config/Economy`. Rien d'autre n'est touché.
- **Ailleurs** : le même motif dans `UpgradeButton` — corrigé aussi.
- **Journal** : « Un Remote ne transporte jamais un prix, une quantité ou une
  récompense : seulement l'intention. »

## Pièges

- **Corriger avant d'avoir reproduit.** Le réflexe le plus coûteux du métier.
  Sans reproduction, tu ne sauras même pas si ton correctif a servi à quelque
  chose.
- **Confondre « l'erreur a disparu » et « le bug est réglé ».** Un `if x then`
  autour du symptôme supprime le message et le comportement attendu avec.
- **S'arrêter à la première anomalie trouvée dans le code.** Du code
  perfectible n'est pas forcément *le* bug. Tant que l'explication ne couvre
  pas tout l'observé, continue.
- **Refactoriser en passant.** Le correctif se noie, et la prochaine
  régression sera impossible à attribuer.
- **Demander à l'utilisateur où est le code.** Tu as le repo ou le MCP :
  cherche d'abord.
- **Oublier que ça peut être un bug de chargement.** En Roblox, « ça marche au
  deuxième essai » n'est presque jamais aléatoire : c'est un ordre d'exécution.

## Avant de rendre

- [ ] Demande reformulée en une ligne si elle admettait plusieurs lectures.
- [ ] Attendu et observé établis, pas supposés.
- [ ] Bug reproduit dans Studio avant correction — ou absence de preuve
      annoncée explicitement comme telle.
- [ ] La cause racine explique **tout** l'observé, pas une partie.
- [ ] Le correctif s'attaque à la cause, pas au symptôme.
- [ ] Correctif minimal, sans refactorisation opportuniste.
- [ ] Reproduction rejouée après correction : le cas passe.
- [ ] Le reste du projet cherché pour le même motif.
- [ ] Règle versée au journal si `code` aurait pu éviter ce bug.
