"""
simulate_control_test — STUB operating-effectiveness test for an internal control.

This tool does not connect to any real system (ERP, IAM, HR...). It recognises the
type of control from its description and returns a SIMULATED, realistic and always
identical set of test results (reproducible demo).

Default scenarios ("auto"):
  - Finance / PO - goods receipt - invoice matching -> 1 payment out of tolerance with
    no approved waiver                             => conclusion "Ineffective"
  - IT / user access review and SoD                -> no blocking exception
                                                   => conclusion "Effective"
  - Unrecognised / too vague description           -> no usable evidence
                                                   => conclusion "Not Determined"

The `scenario` parameter can force "pass" or "fail" for other demos.

The verdict ("conclusion") is computed here, deterministically; the agent must copy it.

Import:
    orchestrate tools import -k python -f tools/simulate_control_test.py -r tools/requirements.txt
"""

import re
import unicodedata

from ibm_watsonx_orchestrate.agent_builder.tools import ToolPermission, tool

# ── Business parameters ─────────────────────────────────────────────────────
TOLERANCE_PCT = 2.0          # Finance: allowed invoice / PO variance
LEAVER_MAX_DAYS = 30         # IT: max days between departure and account deactivation
TEST_PERIOD = "2026-09-01 to 2026-09-30"

# ── Control type detection (French and English descriptions) ────────────────
_FIN_KEYWORDS = [
    # English
    "three-way", "3-way", "three way", "purchase order", "invoice", "goods receipt",
    "procure", "p2p", "duplicate", "tolerance", "reconciliation",
    # French
    "rapprochement", "commande", "reception", "facture", "achats", "doublon",
]
_IT_KEYWORDS = [
    # English
    "access", "iam", "directory", "segregation", "sod", "privileged",
    "user account", "erp role", "leaver", "user access review",
    # French
    "acces", "habilitation", "annuaire", "separation des taches", "privilegi",
    "comptes utilisateurs", "droits", "roles erp", "role erp", "depart", "mobilite",
]
# Avoid very short keywords: "role" is contained in "controle", "compte" in "comptable".


def _normalize(text: str) -> str:
    """Lower-case, strip accents and HTML tags (OpenPages descriptions may contain HTML)."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"<[^>]+>", " ", text)
    return text.lower()


def _score(text: str, keywords: list[str]) -> int:
    return sum(1 for k in keywords if k in text)


def _detect_domain(description: str) -> str:
    """Return finance_p2p, it_access_sod or unknown (needs >= 2 keywords and a strict majority)."""
    text = _normalize(description)
    fin, it = _score(text, _FIN_KEYWORDS), _score(text, _IT_KEYWORDS)
    if max(fin, it) < 2 or fin == it:
        return "unknown"
    return "finance_p2p" if fin > it else "it_access_sod"


# ── Simulated evidence ──────────────────────────────────────────────────────
def _finance_evidence(fail: bool) -> dict:
    exceptions = [{
        "type": "near_duplicate_invoice",
        "detail": "Invoices FAC-2026-08841 and FAC-2026-08B41 (supplier Industrial Supplies Ltd, "
                  "EUR 18,450.00): near-duplicate detected and blocked before payment.",
        "resolved": True,
    }]
    if fail:
        exceptions.append({
            "type": "payment_out_of_tolerance",
            "detail": "Payment PAY-2026-11307 (PO-4500172233, supplier Rhone Valley Logistics): "
                      "invoiced EUR 52,714.00 for a PO of EUR 50,980.00, variance +3.4% "
                      "(tolerance ±2%), no approved waiver found.",
            "resolved": False,
            "deviation_pct": 3.4,
            "approved_waiver": False,
        })
    return {
        "control_type": "Finance - PO / goods receipt / invoice matching",
        "test_period": TEST_PERIOD,
        "data_sources": ["ERP: purchase orders, goods receipts, invoices, payments",
                         "PDF invoices (AI extraction)"],
        "population": {"purchase_orders": 1312, "goods_receipts": 1298, "invoices": 1287,
                       "payments": 1265, "invoice_pdfs_extracted": 1287},
        "results": {
            "three_way_matched": 1263 if fail else 1265,
            "tolerance_pct": TOLERANCE_PCT,
            "payments_out_of_tolerance_without_waiver": 1 if fail else 0,
            "payments_out_of_tolerance_with_waiver": 2,
            "near_duplicates_detected": 1,
            "near_duplicates_paid": 0,
        },
        "exceptions": exceptions,
        "rule": f"Ineffective if at least one payment is outside the ±{TOLERANCE_PCT:g}% "
                f"tolerance without an approved waiver.",
    }


def _it_evidence(fail: bool) -> dict:
    exceptions = [{
        "type": "sod_conflict",
        "detail": "User M. LEROY holds both 'Vendor creation' and 'Payment proposal' ERP roles. "
                  "Conflict covered by compensating control CC-AP-07 (monthly payment review by "
                  "management control), performed and documented in September.",
        "compensating_control": "CC-AP-07",
        "resolved": True,
    }]
    if fail:
        exceptions.append({
            "type": "leaver_account_active",
            "detail": "ERP account 'jmartin' still active 47 days after departure "
                      "(HR leave date: 2026-08-14), beyond the 30-day threshold.",
            "resolved": False,
            "days_after_departure": 47,
        })
    return {
        "control_type": "IT - ERP user access review and segregation of duties",
        "test_period": TEST_PERIOD,
        "data_sources": ["Directory / IAM", "HR records (leavers, transfers)", "ERP roles",
                         "Segregation-of-duties matrix"],
        "population": {"active_erp_accounts": 2846, "hr_leavers_in_period": 41,
                       "hr_transfers_in_period": 63, "privileged_accounts": 18},
        "results": {
            "leaver_max_days_threshold": LEAVER_MAX_DAYS,
            "leaver_accounts_disabled": 40 if fail else 41,
            "leaver_accounts_active_beyond_threshold": 1 if fail else 0,
            "worst_case_days_between_departure_and_deactivation": 47 if fail else 6,
            "sod_conflicts_detected": 1,
            "sod_conflicts_without_compensating_control": 0,
            "privileged_accounts_without_justification": 0,
            "transfer_rights_reviewed": 63,
        },
        "exceptions": exceptions,
        "remediation_priority": (["P1 - Disable account 'jmartin' immediately"] if fail else [])
        + ["P3 - Remove M. LEROY's SoD conflict at the next role review"],
        "rule": f"Ineffective if a leaver's account remains active more than {LEAVER_MAX_DAYS} "
                f"days after departure, or if an SoD conflict is not covered by a compensating "
                f"control.",
    }


@tool(
    name="simulate_control_test",
    description=(
        "Runs a SIMULATED operating-effectiveness test from the description of an internal "
        "control and returns the test results (tested population, exceptions, conclusion rule "
        "and conclusion). Call it once per control to evaluate."
    ),
    permission=ToolPermission.READ_ONLY,
)
def simulate_control_test(control_description: str, scenario: str = "auto") -> dict:
    """
    Simulates the test of an internal control and returns the collected evidence.

    Args:
        control_description (str): Full description of the control, as stored in OpenPages.
        scenario (str): "auto" (default, standard demo result), "pass" (force a clean test) or "fail" (force a blocking exception).

    Returns:
        dict: Simulated test results: conclusion, control type, period, sources, population, figures, exceptions and conclusion rule.
    """
    domain = _detect_domain(control_description)
    scenario = (scenario or "auto").strip().lower()

    if domain == "finance_p2p":
        fail = scenario != "pass"          # auto -> fail
        evidence = _finance_evidence(fail)
    elif domain == "it_access_sod":
        fail = scenario == "fail"          # auto -> pass
        evidence = _it_evidence(fail)
    else:
        return {
            "conclusion": "Not Determined",
            "control_type": "Unrecognised",
            "test_period": TEST_PERIOD,
            "evidence_available": False,
            "reason": "The description does not identify the control objective, the population "
                      "to test or the data sources. No test could be performed.",
        }

    # Deterministic verdict: the agent must copy it as is.
    evidence = {"conclusion": "Ineffective" if fail else "Effective", **evidence}
    evidence["evidence_available"] = True
    evidence["simulated"] = True
    return evidence
