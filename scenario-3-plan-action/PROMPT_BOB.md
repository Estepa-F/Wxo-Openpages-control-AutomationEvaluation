# Prompt Bob — plan d'action 2ᵉ ligne → 1ʳᵉ ligne

Remplacer `CTRL-FIN-002` par le nom du contrôle de démo si besoin.

```
Tu es contrôleur interne de 2e ligne. Via le serveur MCP OpenPages, travaille sur le contrôle CTRL-FIN-002 (SOXControl). Arrête-toi après chaque étape pour que je valide.

Étape 1 – Constater la contradiction (lecture seule)
- Lis CTRL-FIN-002 : Resource ID, description, propriétaire (OPSS-Ctl:Control Owner) et valeur de OPSS-Ctl:Operating Effectiveness (= auto-évaluation de la 1re ligne).
- Obtiens l'évaluation de 2e ligne en exécutant :
  orchestrate chat ask --agent-name Control_Evaluation_Agent "<description exacte du contrôle>"
- Affiche un tableau : Évaluation 1re ligne | Évaluation 2e ligne (IA) | Motif de l'écart.
  S'il n'y a pas de contradiction, arrête-toi.

Étape 2 – Lire le modèle de données (lecture seule)
- Lis openpages://catalog/object_types, puis le schéma de SOXIssue et celui du type « Action Item » rattaché aux Issues.
- Donne-moi les noms techniques et les valeurs autorisées des champs : assignataire, priorité, statut, échéance, type d'issue, « identifié par » (Issue) et assignataire, statut, échéance (Action). N'invente aucune valeur de liste.

Étape 3 – Créer le plan d'action (montre-moi d'abord le contenu exact, puis crée seulement après mon OK)
Avec openpages_upsert_object :
1) Une Issue, enfant de CTRL-FIN-002 (primaryParentId = son Resource ID) :
   - Nom : CTRL-FIN-002_ISS_01 – Contradiction évaluation 1re ligne / test 2e ligne
   - Description : « Le test de 2e ligne du <date du jour> conclut que le contrôle CTRL-FIN-002 est inefficace, alors que l’auto-évaluation de 1re ligne le déclare efficace. Motif : <motif renvoyé par l’agent, avec la référence du paiement, les montants, l’écart et la tolérance>. La 1re ligne doit vérifier l’anomalie, la régulariser ou produire la dérogation, puis mettre à jour l’évaluation du contrôle. »
   - Assignataire : le propriétaire du contrôle ; Priorité : la plus élevée ; Statut : ouvert ; Échéance : aujourd’hui + 15 jours ; Identifié par : 2e ligne / contrôle interne si la valeur existe.
2) Deux actions, enfants de l'Issue, assignées au propriétaire du contrôle :
   - ACT-01 – Analyser l’écart : vérifier le paiement en anomalie, retrouver une éventuelle dérogation approuvée, sinon lancer la régularisation. Échéance : aujourd’hui + 7 jours.
   - ACT-02 – Mettre à jour l’évaluation du contrôle : après analyse, mettre à jour « Operating Effectiveness » et « Control Operating Effectively Explanation » de CTRL-FIN-002 avec les justificatifs. Échéance : aujourd’hui + 15 jours.
Ne modifie pas l'évaluation du contrôle lui-même : c'est le rôle de la 1re ligne.
Si une valeur de liste est refusée, corrige avec une valeur autorisée lue à l'étape 2.

Étape 4 – Récapitulatif
Relis ce que tu as créé et affiche un tableau : Objet | Nom | Assignataire | Échéance | Statut | Lien OpenPages.
```
