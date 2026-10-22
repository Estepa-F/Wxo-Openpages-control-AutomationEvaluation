# Scénario 3 — Plan d'action 2ᵉ ligne → 1ʳᵉ ligne

**Situation** : la 1ʳᵉ ligne (propriétaire du contrôle) a auto-évalué un contrôle **Effective**,
mais le test de 2ᵉ ligne (l'agent du scénario 1) conclut **Ineffective**. La 2ᵉ ligne ne corrige
pas elle-même l'évaluation : elle ouvre un **plan d'action** tracé dans OpenPages, qui demande à
la 1ʳᵉ ligne de vérifier l'écart et de mettre à jour l'évaluation.

IBM Bob, connecté au serveur MCP OpenPages, réalise le scénario :
1. constate la contradiction (lecture du contrôle + appel de l'agent Orchestrate) ;
2. lit le modèle de données OpenPages (valeurs autorisées des listes, sans rien inventer) ;
3. crée, **après validation**, une **Issue** rattachée au contrôle et **deux actions** assignées à la 1ʳᵉ ligne ;
4. affiche un récapitulatif avec les liens OpenPages.

## Préparation
- Scénario 1 déployé (agent `Control_Evaluation_Agent` disponible).
- Un contrôle de démo (ex. **CTRL-FIN-002**) dont la description porte sur le rapprochement
  commande / réception / facture, mis **à la main** à `Effective` (auto-évaluation 1ʳᵉ ligne).
- Bob ouvert dans un mode qui peut exécuter des commandes **et** utiliser le MCP.

## Exécution
Coller le prompt de `PROMPT_BOB.md` dans Bob.

## Après la répétition
La suppression d'objets est désactivée dans le serveur MCP : clôturer l'Issue et ses actions
(statut « Closed » ou équivalent) ou les supprimer à la main, puis remettre le contrôle à `Effective`.
