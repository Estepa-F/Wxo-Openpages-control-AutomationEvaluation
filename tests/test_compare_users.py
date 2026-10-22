"""Le rapprochement RH / ERP du scénario 2 doit retrouver les écarts plantés dans les données."""

from datetime import date

import compare_users


def run(review="2026-10-15"):
    return compare_users.analyse(date.fromisoformat(review))


def test_conclusion_and_counts():
    res = run()
    assert res["conclusion"] == "Ineffective"
    assert res["stats"]["personnes_rh"] == 25
    assert res["stats"]["comptes_erp"] == 27
    assert res["stats"]["ecarts"] == 6
    assert res["stats"]["ecarts_bloquants"] == 3


def test_blocking_gaps():
    blocking = {g["compte"] for g in run()["ecarts"] if g["bloquant"]}
    assert blocking == {"Alice GUERIN (aguerin)", "Pierre BLANC (pblanc)", "Nicolas SIMON (nsimon)"}


def test_recent_leaver_is_within_tolerance():
    boyer = [g for g in run()["ecarts"] if "rboyer" in g["compte"]]
    assert len(boyer) == 1 and boyer[0]["gravite"] == "Info" and not boyer[0]["bloquant"]


def test_login_after_departure_is_flagged():
    blanc = next(g for g in run()["ecarts"] if "pblanc" in g["compte"])
    assert "APRÈS le départ" in blanc["detail"]


def test_explanation_fits_openpages_field():
    text = run()["explication"]
    assert len(text) <= 1000
    assert "'" not in text  # apostrophe typographique uniquement


def test_earlier_review_date_changes_result():
    # Au 2026-08-01 : Pierre BLANC n'est pas encore parti (ignoré), Alice GUERIN est
    # partie depuis 30 jours pile (dans le délai) -> seul le conflit SoD reste bloquant.
    res = run("2026-08-01")
    assert res["stats"]["ecarts_bloquants"] == 1
    assert not any("pblanc" in g["compte"] for g in res["ecarts"] if g["type"] == "Partant avec compte actif")
