# OpenPages

This folder contains what OpenPages needs to call the watsonx Orchestrate agent.

## Purpose

OpenPages does not host the AI: it **connects** to the agent deployed in watsonx Orchestrate
through two configuration objects, with no code on the OpenPages side:

- an **Extension**: the secure connection to Orchestrate (server URL, IBM Cloud IAM
  authentication, available API operations), configured once and reusable;
- a **Custom Machine Learning Model**: the use case plugged on that connection (which agent
  to call, what to send, where to store the answer).

A button in the control's Task View then triggers the model.

## Files in this folder

### [`wxo-openapi-extension.yaml`](wxo-openapi-extension.yaml)
OpenAPI specification uploaded when creating the OpenPages Extension. It exposes two operations:

- `GET /v1/orchestrate/agents` — list agents (used by the extension connectivity test)
- `POST /v1/orchestrate/{agent_id}/chat/completions` — chat with an agent (used by the model)

Before uploading it, replace the placeholders:

| Placeholder | Value |
|---|---|
| `<region>` | Region of your watsonx Orchestrate instance (e.g. `eu-de`, `us-south`) |
| `<instance-id>` | ID at the end of your Orchestrate service URL |
| `<AGENT_ID>` | ID of `Control_Evaluation_Agent` (printed by `python scripts/test_agent.py`) |

Authentication is OAuth 2.0 with the **IBMCloudIAM** scheme already declared in the spec:
you only paste your watsonx Orchestrate API key in the extension screen.

## Step-by-step configuration

See [`../docs/openpages-integration.md`](../docs/openpages-integration.md).
