# Avant de publier une mise à jour

## Sommaire

1. [Ce qui fait perdre des données](#1-ce-qui-fait-perdre-des-données)
2. [Ce qui se fait voler](#2-ce-qui-se-fait-voler)
3. [Ce qui casse pour les autres, pas pour toi](#3-ce-qui-casse-pour-les-autres-pas-pour-toi)
4. [Ce qui rame chez les joueurs](#4-ce-qui-rame-chez-les-joueurs)
5. [Le retour arrière](#5-le-retour-arrière)

Lis la section qui correspond à ce que ta mise à jour touche. Tout lire avant
chaque publication est un bon moyen de ne plus rien lire du tout.

Les contrôles d'un skill s'arrêtent à « ce bout de travail est correct ». Cette
fiche couvre autre chose : **des gens jouent déjà**. Une régression ne se
mesure plus en temps perdu mais en sauvegardes détruites et en joueurs qui ne
reviennent pas.

---

## 1. Ce qui fait perdre des données

Le seul défaut de cette liste qui soit **irréversible**. Tout le reste se
corrige par une deuxième publication.

- [ ] La structure de sauvegarde a-t-elle changé ? Si oui, l'ancien format est
      **lu** et migré, jamais écrasé. Un joueur absent depuis six mois revient
      avec l'ancienne forme.
- [ ] Une valeur par défaut n'écrase jamais une valeur existante. Le piège
      classique : `data.nouveauChamp = data.nouveauChamp or 0` est correct,
      `data.nouveauChamp = 0` détruit.
- [ ] Une sauvegarde échouée est **réessayée**, et l'échec final est journalisé.
      Un `pcall` dont on ignore le retour est une perte de données silencieuse.
- [ ] Le joueur qui part pendant une écriture ne perd rien : `BindToClose`
      couvre l'arrêt du serveur.
- [ ] Deux serveurs ne peuvent pas écrire la même clé en même temps
      (verrou de session), sinon le dernier qui ferme gagne.

Si tu ne peux cocher qu'une seule ligne de toute la fiche, prends celle-là :
**teste la migration sur une sauvegarde à l'ancien format**, pas sur un compte
neuf. Un compte neuf ne révèle jamais un bug de migration.

---

## 2. Ce qui se fait voler

- [ ] Chaque `RemoteEvent` valide côté serveur : le type, les bornes, et le
      **droit d'agir** — le joueur a-t-il cet objet, est-il à portée, le
      délai est-il écoulé ?
- [ ] Aucune décision d'économie ne vient du client. Le client demande, le
      serveur décide.
- [ ] Les Remotes ont une limite de fréquence. Sans elle, un appel en boucle
      suffit à saturer le serveur ou à répéter un gain.
- [ ] Aucune donnée sensible dans `ReplicatedStorage` : tout ce qui y est
      posé est lisible par n'importe quel client.
- [ ] Les modèles insérés depuis la Toolbox ne contiennent aucun script.
      `toolbox.py` les écarte par défaut ; un modèle ajouté à la main dans
      Studio, non.

---

## 3. Ce qui casse pour les autres, pas pour toi

Ces défauts ne se voient jamais chez le développeur. C'est ce qui les rend
coûteux : ils passent tous les tests de la personne qui a écrit le code.

- [ ] **Les animations appartiennent au propriétaire du jeu.** Une animation
      publiée sous ton compte personnel ne se charge pas dans un jeu détenu par
      un groupe — et inversement. Elle marchera chez toi et pour personne
      d'autre. `toolbox.py verifier --ids <id> --proprietaire "<compte du jeu>"`
      tranche sans Studio.
- [ ] Aucun chemin ne dépend d'un objet qui n'existe que dans ton Studio.
- [ ] Rien ne suppose un seul joueur. Deux joueurs qui font la même action à la
      même seconde, c'est le cas normal, pas le cas limite.
- [ ] Rien ne suppose que le personnage existe : entre la mort et la
      réapparition, il n'y en a pas.
- [ ] Testé à plusieurs clients dans Studio, pas seulement en solo.

---

## 4. Ce qui rame chez les joueurs

- [ ] Une bonne part des joueurs Roblox est sur téléphone. Le coût dominant des
      effets n'est pas le nombre de particules mais la surface transparente
      empilée.
- [ ] Aucune boucle `Heartbeat` ou `RenderStepped` ne fait un travail qui
      pourrait être événementiel.
- [ ] Ce qui est créé en masse est recyclé, pas recréé.
- [ ] Aucun `Attachment` ni emitter ne reste derrière après un effet.
- [ ] `python3 "<plugin>/scripts/luau_check.py" --dans src` passe.

---

## 5. Le retour arrière

- [ ] Tu sais revenir à la version précédente, et tu l'as vérifié **avant** d'en
      avoir besoin. Roblox garde l'historique des versions du lieu : sache où il
      est.
- [ ] Ce qui change la sauvegarde ne se revient pas en arrière si les données
      ont déjà migré. C'est la raison pour laquelle la section 1 passe en
      premier.
- [ ] Publie quand tu peux regarder ce qui se passe dans l'heure qui suit. Une
      publication le soir avant de se coucher est une nuit de dégâts.
