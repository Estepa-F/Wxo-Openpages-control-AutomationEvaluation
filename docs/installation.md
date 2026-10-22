# Installation and deployment guide

## Prerequisites

- **Python 3.12+**
- A **watsonx Orchestrate** instance (SaaS on IBM Cloud) and an API key for it
- An **IBM OpenPages** instance with administration rights (for the integration)
- *(Optional)* **IBM Bob** connected to an **OpenPages MCP server** (scenarios 2 and 3)

## 1. Clone and create the virtual environment

```bash
git clone https://github.com/Estepa-F/wxo-openpages-control-automationevaluation.git
cd wxo-openpages-control-automationevaluation
python3 -m venv .venv
source .venv/bin/activate
pip install ibm-watsonx-orchestrate
pip install -r requirements-dev.txt   # pytest and requests, for the tests
```

## 2. Configure `.env.sdk`

```bash
cp .env.sdk.exemple .env.sdk
```

| Variable | Where to find it |
|---|---|
| `WO_INSTANCE_ALIAS` | Any local name, e.g. `openpages-demo` |
| `WO_INSTANCE` | Orchestrate → profile → **Settings → API details** → service instance URL |
| `WO_API_KEY` | Same screen → **Generate API key** |
| `OPENPAGES_MCP_URL` | *(Optional)* URL of the OpenPages MCP server used by Bob |

`.env.sdk` is ignored by git. Never commit it.

## 3. Activate the Orchestrate environment

```bash
./scripts/configure_environment.sh
```

Equivalent to:
```bash
orchestrate env add -n "$WO_INSTANCE_ALIAS" -u "$WO_INSTANCE" --type ibm_iam
orchestrate env activate "$WO_INSTANCE_ALIAS" -a "$WO_API_KEY"
```

The IAM token lasts about one hour: re-run the script if a command returns 401.

## 4. Deploy the tool and the agent

```bash
./scripts/deploy_complete.sh
```

Step by step:
```bash
orchestrate tools import -k python -f tools/simulate_control_test.py -r tools/requirements.txt
orchestrate agents import -f agents/control_evaluation_agent.yaml
orchestrate agents deploy --name Control_Evaluation_Agent
```

## 5. Test

Offline (no Orchestrate access needed):
```bash
python3 -m pytest -q tests
```

Against the deployed agent:
```bash
python scripts/test_agent.py --repeat 5
```
Target: all cases `OK`. The script prints the **agent ID**: keep it for OpenPages.

Quick manual check:
```bash
orchestrate chat ask --agent-name Control_Evaluation_Agent \
  "Monthly three-way match between purchase orders, goods receipts and invoices with a ±2% tolerance."
```

## 6. Connect OpenPages

Follow [`openpages-integration.md`](openpages-integration.md): Extension → Custom Machine
Learning Model → attach the model to the control Task View.

## 7. *(Optional)* Set up IBM Bob

Add the OpenPages MCP server to Bob's MCP settings, open the repo root in Bob and use the
files in [`../bob/`](../bob/). Check first that Bob reaches the **right** OpenPages instance
(ask it to read a control you know).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `orchestrate: command not found` | Activate `.venv`, or `pip install ibm-watsonx-orchestrate` |
| 401 on any command | Token expired: `./scripts/configure_environment.sh` |
| Agent answers with text around the JSON | Redeploy from the repo, then `test_agent.py --repeat 5` |
| `Not Determined` for a real finance/IT control | The description has fewer than 2 domain keywords: enrich it |
