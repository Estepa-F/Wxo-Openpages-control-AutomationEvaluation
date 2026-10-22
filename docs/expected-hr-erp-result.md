# Expected result — HR / ERP reconciliation

Output of `python3 scripts/compare_users.py` on the demo extracts in [`data/`](../data/)
(review date 2026-10-15). The data is fictional and the result is deterministic: Bob should
show exactly this table. The *Info* row is within the allowed delay and is not counted as a gap.

## Script output — HR / ERP reconciliation — review of 2026-10-15

- HR records: 25 (5 leavers)
- ERP accounts: 27 (25 active)
- Gaps found: 6 (3 blocking)

| Severity | Gap type | Account | Detail |
|---|---|---|---|
| Critical 🔴 | Leaver with active account | Alice GUERIN (aguerin) | Left on 2026-07-02, account still active 105 days later (threshold 30 days). |
| Critical 🔴 | Leaver with active account | Pierre BLANC (pblanc) | Left on 2026-08-14, account still active 62 days later (threshold 30 days); login on 2026-09-29, AFTER departure. |
| High | Orphan account | Technical test account (svc_test_admin) | Active account with no HR match (employee ID 'empty'), roles: ERP Administrator. |
| High 🔴 | SoD conflict | Nicolas SIMON (nsimon) | Holds both 'Vendor creation' and 'Vendor payment', with no compensating control. |
| Medium | Orphan account | Marc DUPUIS (contractor) (ext.dupuis) | Active account with no HR match (employee ID 'X999'), roles: Invoice entry, Vendor creation. |
| Medium | Rights not reviewed after transfer | Laura MICHEL (lmichel) | Keeps 'Vendor creation' although now in Marketing (Transfer Procurement → Marketing on 2026-09-01). |
| Info | Leaver with active account | Romain BOYER (rboyer) | Left on 2026-10-03, account still active 12 days later (threshold 30 days); within the allowed delay. |

**Conclusion: Ineffective**

Explanation for OpenPages:
[HR / ERP reconciliation of 2026-10-15] 25 HR records compared with 27 ERP accounts: 6 gaps, 3 of them blocking. Blocking gaps: Alice GUERIN (aguerin) – account active 105 days after departure; Pierre BLANC (pblanc) – account active 62 days after departure and used after departure; Nicolas SIMON (nsimon) – holds Vendor creation and Vendor payment with no compensating control. Remediation: disable leavers’ accounts immediately, remove incompatible role combinations, delete or assign orphan accounts.
