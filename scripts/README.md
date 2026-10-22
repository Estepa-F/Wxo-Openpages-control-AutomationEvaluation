# Scripts

This folder contains the setup, deployment, test and analysis scripts. Run them **from the
repo root**, with the virtual environment that has the ADK activated.

## Setup and deployment

### [`configure_environment.sh`](configure_environment.sh)
Reads `.env.sdk` and registers then activates the watsonx Orchestrate environment
(`orchestrate env add --type ibm_iam` + `orchestrate env activate`).
Requires `WO_INSTANCE_ALIAS`, `WO_INSTANCE` and `WO_API_KEY`.

### [`deploy_complete.sh`](deploy_complete.sh)
Full deployment in three steps: checks the CLI and the active environment, imports the
`simulate_control_test` tool, imports and deploys `Control_Evaluation_Agent`.
Safe to re-run: the agent keeps its ID.

## Tests

### [`test_agent.py`](test_agent.py)
End-to-end test of the **deployed** agent, called exactly like OpenPages calls it
(`POST /v1/orchestrate/{agent_id}/chat/completions`). It checks that the answer is valid JSON,
that the status matches the expected one and that the tool was really called (test period marker).

```bash
python scripts/test_agent.py                # cases in tests/agent_test_cases.json
python scripts/test_agent.py --repeat 5     # stability check
python scripts/test_agent.py "My control description..."
```

It also prints the agent ID needed in the OpenPages Custom ML Model.

## Analysis

### [`compare_users.py`](compare_users.py)
HR / ERP reconciliation used in scenario 2. Compares
[`../data/hr_employees.csv`](../data/hr_employees.csv) and
[`../data/erp_accounts.csv`](../data/erp_accounts.csv) and reports leavers with active accounts,
orphan accounts, SoD conflicts, unjustified privileges and rights not reviewed after a transfer.
Prints a Markdown table, a conclusion and an explanation ready for OpenPages.

```bash
python3 scripts/compare_users.py
python3 scripts/compare_users.py --json
```

Expected output: [`../docs/expected-hr-erp-result.md`](../docs/expected-hr-erp-result.md).
