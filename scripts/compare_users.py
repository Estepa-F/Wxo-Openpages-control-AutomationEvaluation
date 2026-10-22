#!/usr/bin/env python3
"""
Reconciliation of ERP accounts against the HR records (GRC demo).

Usage (from the repo root):
    python3 scripts/compare_users.py                    # default review date: 2026-10-15
    python3 scripts/compare_users.py --date 2026-10-20
    python3 scripts/compare_users.py --json             # JSON output (for automation)

Reads data/hr_employees.csv and data/erp_accounts.csv (";" separator) and detects:
  1. active ERP accounts of people who left more than N days ago (N = 30)
  2. ERP accounts with no HR match (orphan accounts)
  3. segregation-of-duties (SoD) conflicts without a compensating control
  4. privileged accounts not justified by the HR job title
  5. sensitive rights incompatible with the current department (transfers not reviewed)

Conclusion (business rule): Ineffective if a leaver's account remains active more than
N days after departure, or if an SoD conflict is not covered by a compensating control.
Otherwise Effective.

Python standard library only: nothing to install.
"""

import argparse
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HR_FILE = ROOT / "data" / "hr_employees.csv"
ERP_FILE = ROOT / "data" / "erp_accounts.csv"

LEAVER_MAX_DAYS = 30
DEFAULT_REVIEW_DATE = "2026-10-15"

# Segregation-of-duties matrix: incompatible role pairs
SOD_MATRIX = [
    ("Vendor creation", "Vendor payment"),
    ("PO creation", "PO approval"),
    ("Invoice entry", "Invoice approval"),
]
# Documented compensating controls: {employee_id: reference}
COMPENSATING_CONTROLS: dict[str, str] = {}

PRIVILEGED_ROLES = {"ERP Administrator"}
PRIVILEGED_JUSTIFIED_JOBS = {"ERP Administrator", "IT Security Manager"}

# Sensitive rights: allowed departments
SENSITIVE_ROLE_DEPARTMENTS = {
    "Vendor creation": {"Procurement", "Finance"},
    "Vendor payment": {"Finance"},
}

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Info": 3}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def to_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def analyse(review_date: date) -> dict:
    hr = {r["employee_id"]: r for r in read_csv(HR_FILE)}
    erp = read_csv(ERP_FILE)
    gaps = []

    for acc in erp:
        active = acc["account_status"] == "Active"
        roles = [r.strip() for r in acc["roles"].split("|") if r.strip()]
        person = hr.get(acc["employee_id"])
        who = f"{acc['full_name']} ({acc['login']})"

        # 2. Orphan account
        if person is None:
            if active:
                privileged = PRIVILEGED_ROLES & set(roles)
                gaps.append({
                    "type": "Orphan account",
                    "severity": "High" if privileged else "Medium",
                    "account": who,
                    "detail": f"Active account with no HR match "
                              f"(employee ID '{acc['employee_id'] or 'empty'}'), roles: {', '.join(roles)}.",
                    "blocking": False,
                })
            continue

        # 1. Leaver with an active account
        leave = to_date(person["leave_date"])
        # A departure later than the review date is not effective yet
        if person["status"] == "Left" and active and leave and leave <= review_date:
            days = (review_date - leave).days
            last = to_date(acc["last_login"])
            used_after = last and last > leave
            beyond = days > LEAVER_MAX_DAYS
            detail = (f"Left on {leave:%Y-%m-%d}, account still active {days} days later "
                      f"(threshold {LEAVER_MAX_DAYS} days)")
            if used_after:
                detail += f"; login on {last:%Y-%m-%d}, AFTER departure"
            gaps.append({
                "type": "Leaver with active account",
                "severity": "Critical" if beyond else "Info",
                "account": who,
                "detail": detail + ("." if beyond else "; within the allowed delay."),
                "short": f"account active {days} days after departure"
                         + (" and used after departure" if used_after else ""),
                "blocking": beyond,
            })

        if not active:
            continue

        # 3. SoD conflicts
        for a, b in SOD_MATRIX:
            if a in roles and b in roles:
                comp = COMPENSATING_CONTROLS.get(acc["employee_id"])
                gaps.append({
                    "type": "SoD conflict",
                    "severity": "Info" if comp else "High",
                    "account": who,
                    "detail": f"Holds both '{a}' and '{b}'"
                              + (f", covered by {comp}." if comp else ", with no compensating control."),
                    "short": f"holds {a} and {b} with no compensating control",
                    "blocking": comp is None,
                })

        # 4. Privileged accounts
        if PRIVILEGED_ROLES & set(roles) and person["job_title"] not in PRIVILEGED_JUSTIFIED_JOBS:
            gaps.append({
                "type": "Unjustified privilege",
                "severity": "High",
                "account": who,
                "detail": f"Administrator role while the HR job title is '{person['job_title']}'.",
                "blocking": False,
            })

        # 5. Sensitive rights incompatible with the department (transfers)
        if person["status"] != "Left":
            for role in roles:
                allowed = SENSITIVE_ROLE_DEPARTMENTS.get(role)
                if allowed and person["department"] not in allowed:
                    origin = f" ({person['comment']} on {to_date(person['transfer_date']):%Y-%m-%d})" \
                        if person["transfer_date"] else ""
                    gaps.append({
                        "type": "Rights not reviewed after transfer",
                        "severity": "Medium",
                        "account": who,
                        "detail": f"Keeps '{role}' although now in {person['department']}{origin}.",
                        "blocking": False,
                    })

    gaps.sort(key=lambda g: (SEVERITY_ORDER[g["severity"]], g["type"], g["account"]))
    blocking = [g for g in gaps if g["blocking"]]
    conclusion = "Ineffective" if blocking else "Effective"

    stats = {
        "hr_people": len(hr),
        "erp_accounts": len(erp),
        "active_erp_accounts": sum(1 for a in erp if a["account_status"] == "Active"),
        "leavers": sum(1 for p in hr.values() if p["status"] == "Left"),
        "gaps": len([g for g in gaps if g["severity"] != "Info"]),
        "blocking_gaps": len(blocking),
    }
    return {"review_date": review_date.isoformat(), "stats": stats, "conclusion": conclusion,
            "gaps": gaps, "explanation": build_explanation(review_date, stats, gaps, conclusion)}


def build_explanation(review_date: date, stats: dict, gaps: list[dict], conclusion: str) -> str:
    """Text ready for 'Control Operating Effectively Explanation' (<= 1,000 characters)."""
    head = (f"[HR / ERP reconciliation of {review_date:%Y-%m-%d}] {stats['hr_people']} HR records "
            f"compared with {stats['erp_accounts']} ERP accounts: {stats['gaps']} gaps, "
            f"{stats['blocking_gaps']} of them blocking. ")
    if conclusion == "Effective":
        return head + "No leaver active beyond the threshold and no uncovered SoD conflict: control effective."
    blocking = [g for g in gaps if g["blocking"]]
    parts = [f"{g['account']} – {g['short']}" for g in blocking]
    text = (head + "Blocking gaps: " + "; ".join(parts) + ". "
            "Remediation: disable leavers' accounts immediately, remove incompatible role "
            "combinations, delete or assign orphan accounts.")
    return text.replace("'", "’")[:1000]


def print_report(result: dict) -> None:
    s = result["stats"]
    print(f"## HR / ERP reconciliation — review of {result['review_date']}\n")
    print(f"- HR records: {s['hr_people']} ({s['leavers']} leavers)")
    print(f"- ERP accounts: {s['erp_accounts']} ({s['active_erp_accounts']} active)")
    print(f"- Gaps found: {s['gaps']} ({s['blocking_gaps']} blocking)\n")
    print("| Severity | Gap type | Account | Detail |")
    print("|---|---|---|---|")
    for g in result["gaps"]:
        flag = " 🔴" if g["blocking"] else ""
        print(f"| {g['severity']}{flag} | {g['type']} | {g['account']} | {g['detail']} |")
    print(f"\n**Conclusion: {result['conclusion']}**\n")
    print(f"Explanation for OpenPages:\n{result['explanation']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--date", default=DEFAULT_REVIEW_DATE, help="review date YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    res = analyse(date.fromisoformat(args.date))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print_report(res)
