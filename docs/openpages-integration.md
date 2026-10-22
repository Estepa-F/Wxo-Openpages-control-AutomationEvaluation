# OpenPages integration guide

This guide wires the deployed `Control_Evaluation_Agent` to an **AI insights** action on the
Task View of an OpenPages control. It was validated on OpenPages SaaS with watsonx Orchestrate
on IBM Cloud. Menu labels can vary slightly between OpenPages versions.

Prerequisites:
- the agent is deployed and **live** (`./scripts/deploy_complete.sh`) and its ID is known
  (`python scripts/test_agent.py` prints it);
- an OpenPages account with administration rights (Integrations, Views).

## Step 1 — Extension (the connection)

**Administration (⚙) → Integrations → Extensions → New**

1. Upload [`openpages/wxo-openapi-extension.yaml`](../openpages/wxo-openapi-extension.yaml)
   (placeholders replaced, see [`openpages/README.md`](../openpages/README.md)).
2. Authentication screen — most values are pre-filled from the spec:

| Field | Value |
|---|---|
| Authentication scheme | `IBMCloudIAM` |
| Authentication type | `OAuth2` |
| Grant type | `Custom API key` |
| **API key** | your watsonx Orchestrate API key |
| Token URL | `https://iam.cloud.ibm.com/identity/token` |
| Client authentication | `Send as body` |
| Token prefix | `Bearer` |
| Servers | `https://api.<region>.watson-orchestrate.cloud.ibm.com/instances/<instance-id>` |

3. Save: the extension is saved **disabled**. From the extensions grid, run
   **Test connectivity** (it calls *List agents*), then **Enable** it.

> On OpenPages SaaS, extensions can only call allow-listed domains. If saving fails with a
> domain error, ask your OpenPages administrator to allow the watsonx Orchestrate domain.

## Step 2 — Custom Machine Learning Model (the use case)

**Administration (⚙) → Integrations → Custom Machine Learning Models → New**

### Model access
| Field | Value |
|---|---|
| Name | `Control_Evaluation` |
| Label | e.g. `Evaluate operating effectiveness (AI)` — shown to users |
| Watson service type | `Extension` |
| Response timeout | `120` seconds |
| Extension | the extension created in step 1 |
| Operation | **Chat with an agent – POST** |

### Inputs
Input type **Object fields**, object type **Control**, run mode **Manual**.

| Model input field | Source | Value |
|---|---|---|
| `agent_id` | Enter expression | `<AGENT_ID>` |
| `messages[0].role` | Enter expression | `user` |
| `messages[0].content` | Select a field | **Description** |
| `stream` | Enter expression | `false` (required by OpenPages) |

### Outputs
Insight type **Set fields**, **Single insight**. The *Target field* column appears only once
*Set fields* is selected. Enable *Advanced JSONata* on each output:

| Output label | JSONata string | Target field |
|---|---|---|
| Operating Effectiveness | `$eval($replace(choices[0].message.content, "\\'", "'")).OperatingEffectiveness` | Operating Effectiveness |
| Control Operating Effectively Explanation | `$eval($replace(choices[0].message.content, "\\'", "'")).Explanation` | Control Operating Effectively Explanation |

- `$eval` parses the JSON text returned by the agent; `$replace` is a safety net against an
  invalid `\'` escape in the model output.
- Confidence score: leave empty. Minimum threshold: `0`.
- Model action: **User set** (the AI proposes, the auditor applies) — switch to
  *Automatically set* for unattended campaigns.

### Guidance
Add a short model description for users, keep the *Body* text style, then **Save**.

### Test
Use **Test model** (top right) with a sample description: the *Output results* table must show
the status and the explanation, and *Raw JSON response* the full Orchestrate answer.

## Step 3 — Attach the model to the control view

**Administration (⚙) → Solution Configuration → Views → *Task View of the control* → Design**

1. Click the **Description** field (the model input).
2. In the right panel, **AI model configuration**: add `Control_Evaluation`
   (other models such as a 5W analysis can stay selected).
3. Make sure the **Operating Effectiveness** and **Control Operating Effectively Explanation**
   fields are visible in the view.
4. **Done**, then save and publish the view.

Equivalent JSON in the view definition:
```json
{
  "name": "System Fields:Description",
  "mlModels": ["Control_Evaluation"]
}
```

## Step 4 — Use it

Open a control → under **Description**, click the model label → the **Suggestions** panel
shows the proposed status and explanation → **Use suggestion** → **Save** the control.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Domain error when saving the extension | Orchestrate domain not allow-listed on the OpenPages tenant |
| 401 / 403 on call | Wrong API key or authentication scheme on the extension |
| Call succeeds but fields stay empty | JSONata expression: temporarily output `choices[0].message.content` raw to inspect it |
| Status not written | Value does not match the field's enum exactly (`Effective`, `Ineffective`, `Not Determined`) |
| Explanation truncated or save error | `OPSS-Ctl-Cert:OpEffExplain` max length: shorten the agent output or use a large-string field |

## Notes

- Redeploying the agent **under the same name** keeps its ID: the model keeps working with
  no OpenPages reconfiguration.
- One extension can serve several Custom ML Models (other agents, other use cases).
