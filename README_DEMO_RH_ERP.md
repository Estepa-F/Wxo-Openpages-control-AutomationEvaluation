# Démo « Rapprochement RH / ERP » depuis Bob

Bob compare deux listes d'utilisateurs (RH et ERP), montre les écarts, puis passe
le contrôle OpenPages en **Ineffective** avec l'explication, via le serveur MCP de Thomas.

## Contenu
```
data/referentiel_rh.csv   25 personnes (20 actives, 1 mobilité, 5 parties) — séparateur ;
data/comptes_erp.csv      27 comptes ERP (dont 2 sans correspondance RH)
compare_users.py          rapprochement déterministe (Python standard, rien à installer)
PROMPT_BOB.md             prompt de démo + prompt de remise à zéro + variante sans script
RESULTAT_ATTENDU.md       ce que Bob doit trouver
```

## Écarts plantés dans les données
| # | Écart | Bloquant ? |
|---|---|---|
| 1 | Alice GUERIN partie le 02/07 : compte actif 105 jours après | 🔴 oui |
| 2 | Pierre BLANC parti le 14/08 : compte actif 62 jours après **et utilisé le 29/09** | 🔴 oui |
| 3 | Nicolas SIMON : Création fournisseur + Paiement fournisseurs, sans contrôle compensatoire | 🔴 oui |
| 4 | `svc_test_admin` : compte administrateur sans propriétaire RH | non |
| 5 | `ext.dupuis` (prestataire) : compte inconnu des RH | non |
| 6 | Laura MICHEL : mutée au Marketing, garde « Création fournisseur » | non |
| — | Romain BOYER parti le 03/10 : actif 12 jours, **dans le délai toléré** (nuance) | non |
| — | Inès GARNIER et Arthur CHEVALIER partis : comptes bien désactivés (le contrôle marche) | non |

Conclusion : **Ineffective** (3 écarts bloquants).

## Préparation (une fois)
1. Copier ce dossier dans le workspace ouvert dans Bob.
2. Vérifier : `python3 compare_users.py` → doit afficher le tableau et « Conclusion : Ineffective ».
3. Dans Bob, utiliser un mode qui a **à la fois** l'exécution de commandes et le MCP
   (mode *Code* / *Agent*). Le mode « OpenPages » du repo de Julien n'exécute pas de commande :
   soit ajouter `- command` dans ses `groups` (fichier `.bob/custom_modes.yaml`),
   soit utiliser la variante sans script de `PROMPT_BOB.md`.
4. Contrôle cible : **CTRL-AL-TEC002** (Resource ID 213037), déjà renseigné dans les prompts.
5. Faire une répétition complète, puis **remettre le contrôle à zéro** (prompt 2).

## Déroulé de la démo (≈ 5 min)
1. **Le problème** : ouvrir les deux CSV (Excel) — « deux sources qui devraient concorder ».
2. **Bob** : coller le prompt 1. Bob lit les fichiers, lance le rapprochement, affiche les écarts.
3. **Commenter** : Pierre BLANC s'est connecté *après* son départ ; le conflit SoD de Nicolas SIMON ;
   la nuance Romain BOYER (dans le délai).
4. **OpenPages** : Bob met à jour le contrôle. Ouvrir la fiche (lien donné par Bob) :
   Operating Effectiveness = **Ineffective**, explication renseignée.
5. **Ouverture** : « demain, la même analyse tourne en campagne sur tous les contrôles ».

## Points d'attention
- `openpages_upsert_object` **efface la Description si on ne la renvoie pas** : le prompt la fait recopier.
- Date de revue figée au 15/10/2026 (jour de la démo) pour des chiffres stables :
  `python3 compare_users.py --date AAAA-MM-JJ` pour la changer.
- Plan B si le MCP ne répond pas : montrer le tableau de Bob, puis appliquer le résultat
  à la main dans OpenPages (copier l'explication).
