# Bob

This folder contains the instructions and prompts used with **IBM Bob**, connected to the
OpenPages MCP server.

## Purpose

Bob plays two roles in the demo:

- **builder**: it rebuilds the stub tool and the agent from a specification, deploys them to
  watsonx Orchestrate and tests them — showing that the whole solution can be produced in minutes;
- **operator**: it reads and writes OpenPages through the MCP server to run analyses (HR / ERP
  reconciliation) and open action plans, always with a human validation before any write.

Bob must run in a mode that can **execute commands** and **use MCP tools** (e.g. *Code* / *Agent*).

## Files in this folder

### [`BOB_INSTRUCTIONS.md`](BOB_INSTRUCTIONS.md)
Step-by-step specification Bob reads to rebuild, deploy and test `Control_Evaluation_Agent`
(scenario 1). Prompt to use: *"Read BOB_INSTRUCTIONS.md and run the steps in order. Stop after each step."*

### [`prompts/hr-erp-reconciliation.md`](prompts/hr-erp-reconciliation.md)
Scenario 2: compare the HR and ERP extracts, show the gaps, set the control to `Ineffective`.
Includes a reset prompt and a variant without script execution.

### [`prompts/action-plan.md`](prompts/action-plan.md)
Scenario 3: detect a contradiction between the first-line self-assessment and the AI test,
then create an Issue and two actions assigned to the control owner.

## Safety

- The MCP server can write (`openpages_upsert_object`): every prompt asks Bob to show the
  content and wait for approval before creating or updating anything.
- `openpages_upsert_object` clears the Description if it is not sent back: prompts always ask
  Bob to copy it verbatim.
- Bob must never display or store an API key.
