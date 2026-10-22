# Data

Fictional extracts used by the HR / ERP reconciliation (scenario 2). All names, IDs and dates
are invented. Files are UTF-8 with BOM, `;` separated, so that they open cleanly in Excel.

### [`hr_employees.csv`](hr_employees.csv)
HR records — 25 people.

`employee_id;last_name;first_name;department;job_title;status;hire_date;leave_date;transfer_date;comment`

`status` is `Active`, `Transfer` or `Left`.

### [`erp_accounts.csv`](erp_accounts.csv)
ERP accounts and roles — 27 accounts.

`login;employee_id;full_name;account_status;roles;last_login;created_on`

`account_status` is `Active` or `Disabled`; `roles` is a comma-separated list
(Vendor creation, Vendor payment, PO creation, PO approval, Invoice entry, Invoice approval,
ERP Administrator...).

## Planted gaps

The data deliberately contains: two leavers with active accounts (one used after departure),
one recent leaver within the allowed delay, a technical orphan account with administrator
rights, a contractor orphan account, a Vendor creation + Vendor payment SoD conflict and a
transfer whose rights were not reviewed. See
[`../docs/expected-hr-erp-result.md`](../docs/expected-hr-erp-result.md).
