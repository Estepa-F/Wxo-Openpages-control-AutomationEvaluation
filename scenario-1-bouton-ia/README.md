# Scénario 1 — Bouton IA sur le contrôle OpenPages

Un bouton sur la fiche d'un contrôle OpenPages envoie sa **description** à un agent
**watsonx Orchestrate**, qui renvoie un JSON plat :

```json
{"OperatingEffectiveness": "Ineffective", "Explanation": "[Test simulé – période 01/09/2026 - 30/09/2026] ..."}
```

OpenPages range ensuite le statut dans *Operating Effectiveness* et l'explication dans
*Control Operating Effectively Explanation*.

L'agent s'appuie sur un **bouchon** (`simulate_control_test`) : aucune donnée réelle n'est lue,
les résultats de test sont simulés, crédibles et **toujours identiques** (démo reproductible).
Le **verdict est calculé par le bouchon** et recopié par l'agent ; l'agent rédige l'explication.

| Contrôle de démo | Résultat | Pourquoi |
|---|---|---|
| CTRL-FIN-001 — rapprochement commande / réception / facture | **Ineffective** | 1 paiement à +3,4 % (tolérance ±2 %) sans dérogation |
| CTRL-IT-001 — revue des accès / séparation des tâches | **Effective** | aucun partant actif au-delà de 30 jours, conflit SoD couvert par un contrôle compensatoire |
| Description vague | **Not Determined** | impossible d'identifier ce qui est testé |

> Les noms de contrôles sont des exemples : adaptez-les à votre instance OpenPages.

## Contenu
```
agents/Control_Evaluation_Agent.yaml          l'agent : instructions, règles métier, format JSON
tools/simulate_control_test/                  le bouchon Python (verdict déterministe)
tests/test_cases.json, tests/run_tests.py     4 cas + script qui appelle l'agent comme OpenPages
ai_insights/wxo-openapi-control-evaluation.yaml   spec OpenAPI de l'extension OpenPages
ai_insights/operating_effectiveness/openpages_config.md   paramétrage Extension / Custom ML Model / vue
BOB_INSTRUCTIONS.md                            reconstruire et déployer l'agent avec IBM Bob
deploy.sh                                      déploiement en une commande
```

## Mode d'emploi

### 1. Se connecter à Orchestrate (une seule fois)
Depuis la racine du repo (voir le README racine pour le `.venv` et le `.env`) :
```bash
source .venv/bin/activate
orchestrate env add -n demo-controls -u "<WXO_URL>" --type ibm_iam --activate
orchestrate models list      # vérifier que groq/openai/gpt-oss-120b est disponible
```
Si ce modèle n'est pas disponible, remplacez la ligne `llm:` de l'agent par un modèle marqué ★.

### 2. Déployer
```bash
cd scenario-1-bouton-ia
./deploy.sh
```

### 3. Tester
```bash
python tests/run_tests.py              # les 4 cas
python tests/run_tests.py --repeat 5   # stabilité (objectif : 20/20)
```
Le script affiche l'**ID de l'agent** (nécessaire pour OpenPages) et vérifie que chaque réponse est
un JSON valide, avec le bon statut et la période du bouchon (sinon : réponse inventée sans appel au tool).

### 4. Brancher le bouton dans OpenPages
Suivre `ai_insights/operating_effectiveness/openpages_config.md` :
**Extension** (connexion sécurisée à Orchestrate) → **Custom Machine Learning Model** (quoi envoyer,
où ranger la réponse) → **vue** (modèle ajouté sur le champ Description).

## Modifier le comportement
- **Résultats de démo** : constantes et fonctions `_finance_evidence` / `_it_evidence` de
  `simulate_control_test.py`, puis `./deploy.sh`.
- **Ton / longueur de l'explication** : section `instructions` de l'agent.

## Points d'attention
- Le style d'agent `default` est annoncé obsolète par l'ADK : migration vers `react_core` à prévoir,
  **à retester** avec `run_tests.py --repeat 5` avant toute démo.
- Champ explication `OPSS-Ctl-Cert:OpEffExplain` : vérifier sa longueur maximale sur votre instance
  (l'agent produit jusqu'à 1 200 caractères).
- Redéployer l'agent **sous le même nom** conserve son ID : OpenPages continue de l'appeler sans reconfiguration.
