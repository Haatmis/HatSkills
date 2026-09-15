# Résultats de mesure du routage

Une ligne par campagne. Une campagne, c'est **les onze prompts, trois fois
chacun**, sur une version donnée du plugin — protocole dans `README.md`.

Ce fichier existe pour une seule raison : sans lui, « le routage n'est pas
mesuré » dépend de la mémoire de quelqu'un. Avec lui, `validate.py` le dit.

| Version mesurée | Date | Cas couverts | Runs par cas | Verdict |
|---|---|---|---|---|
| — | — | — | — | **Aucune campagne à ce jour.** |

## Ce qui a été fait, et pourquoi ça ne compte pas

Un seul prompt a été joué à la main, le cas `combat-multi-domaine`, et il est
passé. C'était avant la `0.8.0`, sans que la version exacte ait été notée, et
une seule fois.

Ça ne rentre pas dans la table. Un cas sur onze, un run sur trois, une version
inconnue : ça dit que le plugin n'est pas complètement cassé, pas que le
routage marche. Le noter comme une campagne donnerait l'illusion d'une mesure
là où il n'y a qu'un signe de vie.

## Comment remplir une ligne

Verdict attendu : `11/11` si chaque prompt a donné le skill attendu en médiane
et aucun skill interdit. Sinon, écrire ce qui a dérapé, prompt par prompt —
un chiffre global sans le détail perd l'information au moment où elle sert.

Exemple d'une campagne qui ne serait pas parfaite :

| Version mesurée | Date | Cas couverts | Runs par cas | Verdict |
|---|---|---|---|---|
| 0.10.0 | 2026-09-20 | 11/11 | 3 | 10/11 — `remote-simple` part sur `game-design` 2 fois sur 3 |
