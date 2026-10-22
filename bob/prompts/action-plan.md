# Bob prompt — second-line → first-line action plan (scenario 3)

Prerequisites: the agent is deployed; control `CTRL-FIN-002` (PO / goods receipt / invoice
matching) is set **manually** to `Effective` (first-line self-assessment). Replace the control
name if needed.

```
You are a second-line internal controller. Through the OpenPages MCP server, work on control CTRL-FIN-002 (SOXControl). Stop after each step so that I can approve.

Step 1 – Identify the contradiction (read-only)
- Read CTRL-FIN-002: Resource ID, description, owner (OPSS-Ctl:Control Owner) and value of OPSS-Ctl:Operating Effectiveness (= first-line self-assessment).
- Get the second-line assessment by running:
  orchestrate chat ask --agent-name Control_Evaluation_Agent "<exact control description>"
- Show a table: First-line assessment | Second-line assessment (AI) | Reason for the gap.
  If there is no contradiction, stop.

Step 2 – Read the data model (read-only)
- Read openpages://catalog/object_types, then the schema of SOXIssue and of the "Action Item" type attached to Issues.
- Give me the technical names and allowed values of: assignee, priority, status, due date, issue type, "identified by" (Issue) and assignee, status, due date (Action). Do not invent any list value.

Step 3 – Create the action plan (show me the exact content first, create only after my OK)
With openpages_upsert_object:
1) An Issue, child of CTRL-FIN-002 (primaryParentId = its Resource ID):
   - Name: CTRL-FIN-002_ISS_01 – Contradiction between first-line assessment and second-line test
   - Description: "The second-line test of <today's date> concludes that control CTRL-FIN-002 is ineffective, whereas the first-line self-assessment rates it effective. Reason: <reason returned by the agent, with the payment reference, amounts, variance and tolerance>. The first line must investigate the exception, correct it or provide the approved waiver, then update the control assessment."
   - Assignee: the control owner; Priority: the highest; Status: open; Due date: today + 15 days; Identified by: second line / internal control if the value exists.
2) Two actions, children of the Issue, assigned to the control owner:
   - ACT-01 – Investigate the variance: check the payment in exception, find any approved waiver, otherwise start the correction. Due: today + 7 days.
   - ACT-02 – Update the control assessment: after the investigation, update "Operating Effectiveness" and "Control Operating Effectively Explanation" of CTRL-FIN-002 with supporting evidence. Due: today + 15 days.
Do not change the control assessment yourself: that is the first line's job.
If a list value is rejected, use an allowed value read in step 2.

Step 4 – Summary
Read back what you created and show a table: Object | Name | Assignee | Due date | Status | OpenPages link.
```

After the rehearsal: object deletion is disabled in the MCP server — close the Issue and its
actions (status "Closed" or equivalent) or delete them manually, then set the control back to `Effective`.
