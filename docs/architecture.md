# Architecture

## Overview

```
┌──────────────────────────── IBM OpenPages ────────────────────────────┐
│  Control (SOXControl) — Task View                                     │
│   Description ──▶ [Evaluate operating effectiveness (AI)]             │
│                         │                    ▲                        │
│                         ▼                    │ Set fields (JSONata)   │
│              Custom Machine Learning Model ──┘                        │
│                         │                                             │
│                    Extension (OpenAPI + IBM Cloud IAM)                │
└─────────────────────────┼─────────────────────────────────────────────┘
                          │ POST /v1/orchestrate/{agent_id}/chat/completions
                          ▼
┌──────────────────── watsonx Orchestrate ───────────────────┐
│  Control_Evaluation_Agent (native, gpt-oss-120b)           │
│        │ 1 call                                            │
│        ▼                                                   │
│  simulate_control_test (Python, read-only, stub)           │
└────────────────────────────────────────────────────────────┘

┌───────────── IBM Bob (scenarios 2 & 3) ─────────────┐
│  terminal: compare_users.py, orchestrate chat ask   │
│  OpenPages MCP server: read / upsert controls,      │
│  issues and actions (human approval before writes)  │
└─────────────────────────────────────────────────────┘
```

## Components

| Component | Role | Location |
|---|---|---|
| OpenPages Extension | Declares the Orchestrate API (OpenAPI 3) and its IAM authentication | [`openpages/wxo-openapi-extension.yaml`](../openpages/wxo-openapi-extension.yaml) |
| Custom ML Model | Maps the control **Description** to the agent input, and the agent answer to two fields | [`openpages-integration.md`](openpages-integration.md) |
| View configuration | Shows the AI action under the Description field | Task View, `mlModels` |
| Agent | Calls the tool, writes the explanation, returns strict JSON | [`agents/`](../agents/) |
| Tool | Detects the domain and returns the simulated test result and verdict | [`tools/`](../tools/) |
| Bob + MCP | Builds and deploys the solution, runs analyses, writes to OpenPages | [`bob/`](../bob/) |

## Request / response

Request sent by OpenPages:
```json
{
  "messages": [{"role": "user", "content": "<control description>"}],
  "stream": false
}
```

Answer used by OpenPages (`choices[0].message.content`):
```json
{"OperatingEffectiveness": "Ineffective", "Explanation": "[Simulated test – period 2026-09-01 to 2026-09-30] ..."}
```

| JSON key | OpenPages field |
|---|---|
| `OperatingEffectiveness` | `OPSS-Ctl:Operating Effectiveness` (Effective / Ineffective / Not Determined) |
| `Explanation` | `OPSS-Ctl-Cert:OpEffExplain` (*Control Operating Effectively Explanation*) |

## Security

- Authentication: IBM Cloud IAM API key, exchanged for a bearer token by OpenPages
  (extension) and by the scripts (`.env.sdk`).
- The tool is **read-only** and has no network access.
- Writes to OpenPages happen only through the user's **Use suggestion + Save** (scenario 1) or
  through Bob after an explicit approval (scenarios 2 and 3).

## Moving beyond the demo

- Replace the stub with real tests (ERP, IAM extracts) behind Orchestrate connections, with the same output shape.
- Switch the model action to *Automatically set* and trigger it on a campaign of controls.
- Add a second agent for the action plan (scenario 3) and call it from an OpenPages workflow.
