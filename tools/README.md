# Tools

This folder contains the Python tool called by the agent.

## Overview

There is no access to real ERP, IAM or HR data in the demo. The tool **simulates** a control
test and returns a realistic, **always identical** result, so the demo is reproducible.
The verdict is computed **in code**, not by the LLM.

## Tool

### [`simulate_control_test.py`](simulate_control_test.py)
`simulate_control_test(control_description: str, scenario: str = "auto") -> dict` — read-only.

1. **Normalise** the description: lower case, accents and HTML tags removed.
2. **Detect the domain** by counting English and French keywords:
   - *finance* (three-way match, purchase order, invoice, goods receipt, tolerance, duplicate...);
   - *IT* (access, IAM, segregation of duties, privileged, leaver, user access review...);
   - a domain wins with **≥ 2 keywords and a strict majority**, otherwise `unknown`.
3. **Return the simulated evidence** for test period `2026-09-01 to 2026-09-30`:

| Domain | Conclusion | Key facts |
|---|---|---|
| Finance | `Ineffective` | Payment PAY-2026-11307 invoiced EUR 52,714.00 vs PO EUR 50,980.00 (+3.4%, tolerance ±2%), no approved waiver; near-duplicate FAC-2026-08841 / 08B41 blocked |
| IT | `Effective` | 2,846 accounts, 41 leavers all disabled (worst case 6 days), 1 SoD conflict covered by CC-AP-07 |
| Unknown | `Not Determined` | `evidence_available: false` — objective, population and sources not identifiable |

The `scenario` parameter (`auto`, `pass`, `fail`) forces the outcome for testing.

### [`requirements.txt`](requirements.txt)
Empty on purpose: the tool uses the Python standard library only.

## Import

```bash
orchestrate tools import -k python -f tools/simulate_control_test.py -r tools/requirements.txt
```

## Replacing the stub with real data

Keep the same name and the same output shape (`conclusion`, `test_period`, `control_type`,
evidence fields): the agent and OpenPages need no change. Connections (ERP, IAM) can then be
added with `orchestrate connections` and bound to the tool with `--app-id`.
