# Control Evaluation Agent — démo Air Liquide

Le service reçoit la **description d'un contrôle** OpenPages et renvoie un JSON plat :

```json
{"OperatingEffectiveness": "Ineffective", "Explanation": "[Test simulé – période 01/09/2026 - 30/09/2026] ..."}
```

C'est un **bouchon** : aucune donnée réelle n'est lue. Les résultats de test sont simulés, mais restent crédibles et toujours identiques, ce qui rend la démo reproductible.

| Contrôle OpenPages | Résultat de démo | Pourquoi |
|---|---|---|
| CTRL-AL-FIN001 (212540) — rapprochement commande/réception/facture | **Ineffective** | 1 paiement à +3,4 % (tolérance ±2 %) sans dérogation |
| CTRL-AL-TEC001 (212541) — revue des accès / SoD | **Effective** | aucun compte de partant au-delà de 30 jours, conflit SoD couvert par un contrôle compensatoire |
| Description vague (3ᵉ contrôle, optionnel) | **Not Determined** | impossible d'identifier ce qui est testé |

## Contenu

```
agents/Control_Evaluation_Agent.yaml        ← l'agent : prompt + règles de Thomas + format JSON
tools/simulate_control_test/                ← le bouchon Python qui simule le test
tests/test_cases.json, tests/run_tests.py   ← 3 cas de test + script qui appelle l'agent comme OpenPages
ai_insights/wxo-openapi-control-evaluation.yaml  ← spec de l'Extension OpenPages (instance eu-de)
ai_insights/operating_effectiveness/openpages_config.md  ← paramétrage du bouton AI Insights
deploy.sh                                   ← déploiement en une commande
.env                                        ← URL + clé API Orchestrate (ne pas committer)
```

## Mode d'emploi

### Étape 1 — Installer l'ADK et se connecter à Orchestrate (une seule fois)
```bash
cd control-evaluation
python3 -m venv .venv && source .venv/bin/activate
pip install ibm-watsonx-orchestrate requests
orchestrate env add -n demo-controls \
  -u https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/8a1ceb60-ab1e-48b4-86d0-bf012123ebfe \
  --type ibm_iam --activate
# → colle la clé API (WXO_API_KEY dans .env) quand elle est demandée
orchestrate models list      # vérifier que groq/openai/gpt-oss-120b est disponible
```
Si `gpt-oss-120b` n'apparaît pas, remplace la ligne `llm:` de l'agent par un modèle marqué ★ dans la liste.

### Étape 2 — Récupérer les infos OpenPages avec Bob (mode OpenPages)
Colle ce prompt dans Bob :
> Pour les contrôles 212540 (CTRL-AL-FIN001) et 212541 (CTRL-AL-TEC001), donne-moi la Description complète.
> Puis lis le schéma openpages://schema/SOXControl et donne-moi le nom technique exact et les valeurs possibles
> du champ « Operating Effectiveness », ainsi que le champ texte le plus adapté pour stocker une explication.

Ensuite :
- remplace les descriptions de `tests/test_cases.json` par les vraies descriptions (les miennes reprennent les specs de Thomas) ;
- vérifie que les valeurs du champ sont bien `Effective` / `Ineffective` / `Not Determined`.

### Étape 3 — Déployer
```bash
./deploy.sh
```

### Étape 4 — Tester
```bash
python tests/run_tests.py
python tests/run_tests.py "Ta description de contrôle libre..."
```
Les trois cas doivent afficher `[OK ]`. Le script affiche aussi l'**ID de l'agent**, dont tu as besoin pour OpenPages.
Tu peux aussi tester dans l'interface Orchestrate (Agents → Control Evaluation Agent → Preview), ou avec
`orchestrate chat ask --agent-name Control_Evaluation_Agent "<description>"`.

### Étape 5 — Brancher le bouton dans OpenPages
Suis `ai_insights/operating_effectiveness/openpages_config.md`.

## Pour modifier le comportement
- **Changer un résultat de démo** : dans `simulate_control_test.py`, en haut de fichier (tolérance, N = 30 jours, période) ou dans `_finance_evidence` / `_it_evidence`. Redéploie ensuite avec `./deploy.sh`.
- **Forcer un autre résultat** sans toucher au code : ajoute « scénario fail » ou « scénario pass » dans le message envoyé à l'agent.
- **Changer le ton ou la longueur de l'explication** : modifie la section `instructions` de `agents/Control_Evaluation_Agent.yaml`.

## Points ouverts à valider avec Thomas
- Faut-il aussi renvoyer la **date du test** ? Elle figure aujourd'hui au début de l'explication.
- La **longueur max** de l'explication est fixée à 1 200 caractères (l'exemple du deck plafonne à 1 900).
- Le 3ᵉ contrôle « Not Determined » doit-il être créé dans OpenPages pour la démo ?
