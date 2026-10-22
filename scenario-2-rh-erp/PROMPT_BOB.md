# Prompts Bob — démo « Rapprochement RH / ERP »

Contrôle de démo : **CTRL-IT-002** — remplacer `<RESOURCE_ID>` par son Resource ID OpenPages
(et le nom du contrôle s'il diffère dans votre instance).

---

## Prompt 1 — LA DÉMO (à coller dans Bob)

```
Tu es un auditeur IT. Effectue la revue des accès ERP du contrôle « CTRL-IT-002 ».

Étape 1 – Données
Les deux extractions sont dans le dossier data/ :
- data/referentiel_rh.csv : référentiel RH (salariés, départs, mobilités)
- data/comptes_erp.csv : comptes et rôles ERP
Montre-moi en une phrase combien de lignes contient chaque fichier.

Étape 2 – Rapprochement
Exécute : python3 compare_users.py
Affiche le tableau des écarts tel quel, puis résume en 3 points les écarts les plus graves.

Étape 3 – Mise à jour du contrôle dans OpenPages (serveur openpages-mcp-server)
a) Retrouve le contrôle « CTRL-IT-002 » (type SOXControl, Resource ID <RESOURCE_ID>) : Name et Description actuels.
b) Mets-le à jour avec openpages_upsert_object :
   - object_type = control, id = <RESOURCE_ID>, name = son Name actuel
   - description = la Description actuelle, recopiée À L'IDENTIQUE (sinon elle est effacée)
   - fields :
       "OPSS-Ctl:Operating Effectiveness" = la conclusion du script (Ineffective)
       "OPSS-Ctl-Cert:OpEffExplain" = le texte « Explication pour OpenPages » du script, mot pour mot
c) Relis le contrôle et confirme les deux valeurs enregistrées, avec le lien OpenPages du contrôle.
```

---

## Prompt 2 — REMISE À ZÉRO avant la démo

```
Remets le contrôle « CTRL-IT-002 » à zéro dans OpenPages avec openpages_upsert_object :
retrouve d'abord son Resource ID, son Name et sa Description, puis mets
"OPSS-Ctl:Operating Effectiveness" = "Not Determined" et "OPSS-Ctl-Cert:OpEffExplain" = "".
Recopie la Description actuelle à l'identique dans le paramètre description.
Confirme les valeurs après mise à jour.
```

---

## Variante sans script (si Bob ne peut pas exécuter de commande)

Remplacer l'étape 2 du prompt 1 par :

```
Étape 2 – Rapprochement
Compare les deux fichiers (clé : matricule) au 15/10/2026 et liste dans un tableau
(Gravité | Type d'écart | Compte | Détail) :
- les comptes ERP actifs de personnes parties depuis plus de 30 jours (précise si une connexion a eu lieu après le départ) ;
- les comptes ERP actifs sans matricule RH correspondant (comptes orphelins) ;
- les comptes qui cumulent « Création fournisseur » et « Paiement fournisseurs », « Création commande » et « Validation commande », ou « Saisie factures » et « Validation factures » ;
- les droits « Création fournisseur » ou « Paiement fournisseurs » détenus par une personne hors Achats/Finance (mobilité).
Conclusion : Ineffective s'il existe un partant actif depuis plus de 30 jours ou un conflit sans contrôle compensatoire, sinon Effective.
Rédige une explication de moins de 900 caractères (apostrophe ’ uniquement).
```

Le résultat attendu est dans `RESULTAT_ATTENDU.md` : comparer avant la démo.
