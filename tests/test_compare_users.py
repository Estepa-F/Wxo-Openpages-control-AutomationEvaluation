"""The HR / ERP reconciliation must find the gaps planted in the demo data."""

from datetime import date

import compare_users


def run(review="2026-10-15"):
    return compare_users.analyse(date.fromisoformat(review))


def test_conclusion_and_counts():
    res = run()
    assert res["conclusion"] == "Ineffective"
    assert res["stats"]["hr_people"] == 25
    assert res["stats"]["erp_accounts"] == 27
    assert res["stats"]["gaps"] == 6
    assert res["stats"]["blocking_gaps"] == 3


def test_blocking_gaps():
    blocking = {g["account"] for g in run()["gaps"] if g["blocking"]}
    assert blocking == {"Alice GUERIN (aguerin)", "Pierre BLANC (pblanc)", "Nicolas SIMON (nsimon)"}


def test_recent_leaver_is_within_tolerance():
    boyer = [g for g in run()["gaps"] if "rboyer" in g["account"]]
    assert len(boyer) == 1 and boyer[0]["severity"] == "Info" and not boyer[0]["blocking"]


def test_login_after_departure_is_flagged():
    blanc = next(g for g in run()["gaps"] if "pblanc" in g["account"])
    assert "AFTER departure" in blanc["detail"]


def test_explanation_fits_openpages_field():
    text = run()["explanation"]
    assert len(text) <= 1000
    assert "'" not in text  # typographic apostrophe only


def test_earlier_review_date_changes_result():
    # On 2026-08-01: Pierre BLANC has not left yet (ignored), Alice GUERIN left exactly
    # 30 days ago (within the allowed delay) -> only the SoD conflict remains blocking.
    res = run("2026-08-01")
    assert res["stats"]["blocking_gaps"] == 1
    assert not any("pblanc" in g["account"] for g in res["gaps"] if g["type"] == "Leaver with active account")
