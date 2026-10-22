"""Le bouchon doit rendre le verdict attendu pour chaque cas de test du scénario 1."""

import json

import pytest

from conftest import SCENARIO_1
from simulate_control_test import _detect_domain, simulate_control_test

CASES = json.loads((SCENARIO_1 / "tests" / "test_cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_conclusion_matches_expected(case):
    result = simulate_control_test(case["control_description"])
    assert result["conclusion"] == case["expected"]
    assert result["test_period"]


def test_finance_evidence_contains_blocking_payment():
    result = simulate_control_test("Rapprochement commande / réception / facture (achats)")
    assert result["conclusion"] == "Ineffective"
    assert result["results"]["payments_out_of_tolerance_without_waiver"] == 1
    assert any(e["type"] == "payment_out_of_tolerance" for e in result["exceptions"])


def test_it_evidence_is_effective():
    result = simulate_control_test("Revue des accès ERP et séparation des tâches (SoD)")
    assert result["conclusion"] == "Effective"
    assert result["results"]["leaver_accounts_active_beyond_threshold"] == 0


def test_short_words_do_not_trigger_it_domain():
    # « role » est contenu dans « contrôle » : ne doit pas faire basculer en IT
    assert _detect_domain("Contrôle du rôle du contrôleur") == "unknown"


def test_html_is_ignored():
    assert _detect_domain("<p>Rapprochement <b>commande</b> facture</p>") == "finance_p2p"


def test_vague_description_is_not_determined():
    result = simulate_control_test("Contrôle périodique pour vérifier que tout est conforme.")
    assert result["conclusion"] == "Not Determined"
    assert result["evidence_available"] is False
