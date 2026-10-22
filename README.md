# watsonx Orchestrate × IBM OpenPages — évaluation automatisée des contrôles

Démonstrateur GRC : un agent IA **watsonx Orchestrate** évalue l'**efficacité opérationnelle**
(*Operating Effectiveness*) des contrôles internes **IBM OpenPages**, et **IBM Bob** pilote
OpenPages via son serveur MCP pour analyser des données et ouvrir des plans d'action.

> Les données, contrôles et résultats de test sont **fictifs** (démo reproductible).
> Aucune donnée client, aucun identifiant d'instance ni aucune clé n'est versionné.

## Les 3 scénarios

| Scénario | Ce qu'il montre | Déclencheur | Dossier |
|---|---|---|---|
| **1. Bouton IA sur le contrôle** | Un clic sur la fiche OpenPages appelle l'agent Orchestrate, qui propose `Effective` / `Ineffective` / `Not Determined` + une explication | Bouton *AI Insights* dans OpenPages | [`scenario-1-bouton-ia/`](scenario-1-bouton-ia/) |
| **2. Rapprochement RH / ERP** | Bob compare deux extractions (RH et comptes ERP), détecte les écarts et passe le contrôle à `Ineffective` | Prompt dans IBM Bob | [`scenario-2-rh-erp/`](scenario-2-rh-erp/) |
| **3. Plan d'action 2ᵉ → 1ʳᵉ ligne** | Contradiction entre l'auto-évaluation et le test IA → Bob crée une Issue et deux actions assignées au propriétaire du contrôle | Prompt dans IBM Bob | [`scenario-3-plan-action/`](scenario-3-plan-action/) |

## Architecture (scénario 1)

```
Fiche du contrôle (OpenPages)
   │ clic « Évaluer l'efficacité opérationnelle (IA) »
   ▼
Custom Machine Learning Model ── quoi envoyer (Description), où ranger la réponse (2 champs)
   │
Extension OpenPages ─────────── connexion sécurisée (IBM Cloud IAM) à l'instance Orchestrate
   │ POST /v1/orchestrate/{agent_id}/chat/completions
   ▼
Agent « Control_Evaluation_Agent » ── tool « simulate_control_test » (bouchon déterministe)
   │
   ▼ {"OperatingEffectiveness": "...", "Explanation": "..."}
OpenPages propose les valeurs → l'auditeur valide
```

Champs OpenPages utilisés : `OPSS-Ctl:Operating Effectiveness` (Effective / Ineffective / Not Determined)
et `OPSS-Ctl-Cert:OpEffExplain` (explication).

## Prérequis
- Python 3.10+
- Une instance **watsonx Orchestrate** (URL de service + clé API)
- **IBM OpenPages** avec droits d'administration (extensions, modèles IA, vues)
- **IBM Bob** connecté à un serveur MCP OpenPages (scénarios 2 et 3)

## Installation
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install ibm-watsonx-orchestrate requests
cp .env.sample .env        # puis renseigner WXO_URL et WXO_API_KEY
```
Puis suivre le README de chaque scénario.

## Tests hors ligne
Sans réseau ni instance : vérifient le bouchon (scénario 1) et le rapprochement RH / ERP (scénario 2).
```bash
pip install -r requirements-dev.txt
python -m pytest tests
```
Les tests de bout en bout contre l'agent déployé sont dans `scenario-1-bouton-ia/tests/run_tests.py`.

## Sécurité
- `.env` est ignoré par git ; ne jamais committer de clé (utiliser `.env.sample`).
- Les fichiers de configuration contiennent des **placeholders** (`<region>`, `<instance-id>`,
  `<AGENT_ID>`, `<RESOURCE_ID>`) à remplacer localement.
- Le serveur MCP OpenPages permet l'écriture (`openpages_upsert_object`) : les prompts imposent
  une validation humaine avant toute création ou modification, et la recopie de la Description
  (sinon elle est effacée).

## Structure
```
.env.sample                 modèle de configuration
requirements-dev.txt        dépendances des tests hors ligne
tests/                      tests hors ligne (pytest)
scenario-1-bouton-ia/       agent, bouchon, déploiement, config OpenPages, instructions Bob
scenario-2-rh-erp/          données fictives RH / ERP, script de rapprochement, prompts Bob
scenario-3-plan-action/     prompt Bob du plan d'action
```
