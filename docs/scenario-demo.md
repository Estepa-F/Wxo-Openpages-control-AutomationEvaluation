# Demo scenario

Three scenarios, about 15 minutes in total. Replace the control names with those of your
instance (`CTRL-FIN-002` for finance, `CTRL-IT-002` for IT access).

## Before the demo

- [ ] `./scripts/configure_environment.sh` (fresh token) and `python scripts/test_agent.py` → all `OK`
- [ ] `CTRL-FIN-002`: Operating Effectiveness = `Not Determined`, explanation empty
- [ ] `CTRL-IT-002`: reset with the Bob reset prompt ([`bob/prompts/hr-erp-reconciliation.md`](../bob/prompts/hr-erp-reconciliation.md))
- [ ] Bob open on the repo root, MCP server connected to the right instance
- [ ] `data/hr_employees.csv` and `data/erp_accounts.csv` open in Excel (scenario 2)

## Scenario 1 — AI button on the control (≈ 5 min)

**Message**: an auditor evaluates a control in one click, with a justified, traceable result.

| # | Screen | Path | What to show |
|---|---|---|---|
| 1 | Extension | ⚙ → Integrations → **Extensions** | OpenAPI spec of Orchestrate, IAM authentication |
| 2 | Custom ML Model | ⚙ → Integrations → **Custom Machine Learning Models** → `Control_Evaluation` | Input = Description, outputs = 2 fields via JSONata, action *User set* |
| 3 | Agent | watsonx Orchestrate → **Build → Agents** → `Control_Evaluation_Agent` | Instructions + `simulate_control_test` tool |
| 4 | Control | Search → `CTRL-FIN-002` → Task View | Description, Operating Effectiveness empty |
| 5 | AI action | Under **Description**, click *Evaluate operating effectiveness (AI)* | Suggestions panel: **Ineffective** + PAY-2026-11307, +3.4% vs ±2% |
| 6 | Apply | **Use suggestion** → **Save** | Fields filled, change visible in the history |

Optional: run the action on an IT control → **Effective** with the evidence (41 leavers disabled, CC-AP-07).

**Variant "built live by Bob"**: Bob rebuilds and redeploys the agent from
[`bob/BOB_INSTRUCTIONS.md`](../bob/BOB_INSTRUCTIONS.md) (≈ 10 min more), then step 5 again.

## Scenario 2 — HR / ERP reconciliation with Bob (≈ 5 min)

**Message**: the agent works on data the auditor has, and writes the result into the GRC tool.

| # | Where | What to show |
|---|---|---|
| 1 | Excel | The two extracts: 25 HR records, 27 ERP accounts |
| 2 | Bob | Prompt 1 of [`bob/prompts/hr-erp-reconciliation.md`](../bob/prompts/hr-erp-reconciliation.md), step 1 (data) |
| 3 | Bob | Step 2: gap table — 6 gaps, 3 blocking ([expected result](expected-hr-erp-result.md)) |
| 4 | Bob | Step 3: approval, then upsert of `CTRL-IT-002` through the MCP server |
| 5 | OpenPages | `CTRL-IT-002` → **Ineffective** + explanation naming GUERIN, BLANC, SIMON |

## Scenario 3 — Second-line action plan (≈ 5 min)

**Message**: the AI spots a contradiction and opens the remediation, the first line stays accountable.

Prerequisite: `CTRL-FIN-002` set **manually** to `Effective` (first-line self-assessment).

| # | Where | What to show |
|---|---|---|
| 1 | OpenPages | `CTRL-FIN-002` rated **Effective** by the first line |
| 2 | Bob | Prompt [`bob/prompts/action-plan.md`](../bob/prompts/action-plan.md), step 1: First line *Effective* vs AI *Ineffective* |
| 3 | Bob | Step 2: data model read (Issue / Action fields and allowed values) |
| 4 | Bob | Step 3: content shown, approval, then Issue + 2 actions created |
| 5 | OpenPages | `CTRL-FIN-002` → **Issues** tab → `CTRL-FIN-002_ISS_01` and its actions assigned to the control owner |

## After the demo

- Reset `CTRL-FIN-002` and `CTRL-IT-002` (`Not Determined`, empty explanation).
- Close (or delete manually) the Issue and actions created in scenario 3: deletion is
  disabled in the MCP server.
