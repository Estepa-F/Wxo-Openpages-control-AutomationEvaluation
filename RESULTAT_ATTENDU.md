# Résultat attendu (référence pour vérifier Bob)

```
## Rapprochement RH / ERP — revue du 15/10/2026

- Personnes au référentiel RH : 25 (dont 5 partants)
- Comptes ERP : 27 (dont 25 actifs)
- Écarts détectés : 6 (dont 3 bloquants)

| Gravité | Type d’écart | Compte | Détail |
|---|---|---|---|
| Critique 🔴 | Partant avec compte actif | Alice GUERIN (aguerin) | Départ le 02/07/2026, compte toujours actif 105 jours après (seuil 30 j). |
| Critique 🔴 | Partant avec compte actif | Pierre BLANC (pblanc) | Départ le 14/08/2026, compte toujours actif 62 jours après (seuil 30 j) ; connexion le 29/09/2026, APRÈS le départ. |
| Élevé | Compte orphelin | Compte technique test (svc_test_admin) | Compte actif sans correspondance RH (matricule « vide »), rôles : Administrateur ERP. |
| Élevé 🔴 | Conflit SoD | Nicolas SIMON (nsimon) | Cumule « Création fournisseur » et « Paiement fournisseurs », sans contrôle compensatoire. |
| Moyen | Compte orphelin | Marc DUPUIS (prestataire) (ext.dupuis) | Compte actif sans correspondance RH (matricule « X999 »), rôles : Saisie factures, Création fournisseur. |
| Moyen | Droits non revus après mobilité | Laura MICHEL (lmichel) | Conserve « Création fournisseur » alors que sa direction est désormais Marketing (Mobilité Achats → Marketing le 01/09/2026). |
| Info | Partant avec compte actif | Romain BOYER (rboyer) | Départ le 03/10/2026, compte toujours actif 12 jours après (seuil 30 j) ; dans le délai toléré. |

**Conclusion : Ineffective**

Explication pour OpenPages :
[Rapprochement RH / ERP du 15/10/2026] 25 personnes RH comparées à 27 comptes ERP : 6 écarts, dont 3 bloquants. Écarts bloquants : Alice GUERIN (aguerin) – compte actif 105 jours après le départ ; Pierre BLANC (pblanc) – compte actif 62 jours après le départ et utilisé après le départ ; Nicolas SIMON (nsimon) – cumule Création fournisseur et Paiement fournisseurs sans contrôle compensatoire. Remédiation : désactiver immédiatement les comptes des partants, retirer le cumul de rôles incompatibles, supprimer ou rattacher les comptes orphelins.
```
