# Bob prompts — HR / ERP reconciliation (scenario 2)

Open the **repo root** in Bob, in a mode that can run commands **and** use the MCP server.
Replace `CTRL-IT-002` and `<RESOURCE_ID>` with the control name and Resource ID of your instance.

## Prompt 1 — The demo

```
You are a second-line IT auditor. Perform the ERP access review of control "CTRL-IT-002". Stop after each step so that I can approve.

Step 1 – Data
The two extracts are in the data/ folder:
- data/hr_employees.csv: HR records (employees, leavers, transfers)
- data/erp_accounts.csv: ERP accounts and roles
State in one sentence how many rows each file contains, and show the first 3 rows of each.

Step 2 – Reconciliation
Run: python3 scripts/compare_users.py
Show the gap table as is, then summarise the 3 most serious gaps for an auditor in 3 bullet points and propose a remediation priority.

Step 3 – Update the control in OpenPages (OpenPages MCP server)
a) Find control "CTRL-IT-002" (SOXControl, Resource ID <RESOURCE_ID>): its current name and description.
b) Update it with openpages_upsert_object:
   - object_type = control, id = <RESOURCE_ID>, name = its current name
   - description = its current description, copied VERBATIM (otherwise it is cleared)
   - fields:
       "OPSS-Ctl:Operating Effectiveness" = the script's conclusion (Ineffective)
       "OPSS-Ctl-Cert:OpEffExplain" = the script's "Explanation for OpenPages" text, word for word
c) Read the control again, confirm both stored values and give me its OpenPages link.
```

Expected result: see [`../../docs/expected-hr-erp-result.md`](../../docs/expected-hr-erp-result.md)
— 6 gaps, 3 blocking (GUERIN, BLANC, SIMON), conclusion **Ineffective**.

## Prompt 2 — Reset before the demo

```
Reset control "CTRL-IT-002" (id <RESOURCE_ID>) with openpages_upsert_object: "OPSS-Ctl:Operating Effectiveness" = "Not Determined" and "OPSS-Ctl-Cert:OpEffExplain" = "", copying its current name and description verbatim. Confirm the values.
```

## Variant without the script (if Bob cannot run commands)

Replace step 2 of prompt 1 with:

```
Step 2 – Reconciliation
Compare both files (key: employee_id) as of 2026-10-15 and list in a table (Severity | Gap type | Account | Detail):
- active ERP accounts of people who left more than 30 days ago (say whether a login happened after departure);
- active ERP accounts with no matching HR employee_id (orphan accounts);
- accounts holding both "Vendor creation" and "Vendor payment", "PO creation" and "PO approval", or "Invoice entry" and "Invoice approval";
- "Vendor creation" or "Vendor payment" rights held by someone outside Procurement/Finance (transfer).
Conclusion: Ineffective if a leaver has been active for more than 30 days or a conflict has no compensating control, otherwise Effective.
Write an explanation under 900 characters (typographic apostrophe ’ only).
```
