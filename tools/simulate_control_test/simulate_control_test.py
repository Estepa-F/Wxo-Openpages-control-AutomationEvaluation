"""
simulate_control_test — BOUCHON (stub) de test d'efficacité opérationnelle.

Ce tool ne se connecte à aucun système réel (ERP, IAM, RH...). Il reconnaît le
type de contrôle à partir de sa description et renvoie un jeu de résultats de
test SIMULÉ, réaliste et toujours identique (démo reproductible).

Scénarios par défaut ("auto") :
  - Finance / rapprochement commande-réception-facture -> 1 paiement hors tolérance
    sans dérogation  => l'agent conclura "Ineffective"
  - IT / revue des accès et SoD                       -> aucune anomalie bloquante
                                                       => l'agent conclura "Effective"
  - Description non reconnue / trop vague             -> pas de preuve exploitable
                                                       => l'agent conclura "Not Determined"

Le paramètre `scenario` permet de forcer "pass" ou "fail" pour d'autres démos.

Import :
    orchestrate tools import -k python \
        -f tools/simulate_control_test/simulate_control_test.py \
        -r tools/simulate_control_test/requirements.txt
"""

import re
import unicodedata

from ibm_watsonx_orchestrate.agent_builder.tools import ToolPermission, tool

# ── Paramètres métier (specs de Thomas) ──────────────────────────────────────
TOLERANCE_PCT = 2.0          # Finance : tolérance d'écart facture / commande
LEAVER_MAX_DAYS = 30         # IT : N jours max entre départ et désactivation
TEST_PERIOD = "01/09/2026 - 30/09/2026"

# ── Détection du type de contrôle ────────────────────────────────────────────
_FIN_KEYWORDS = [
    "rapprochement", "commande", "reception", "facture", "three-way", "3-way",
    "three way", "tolerance", "bon de commande", "purchase order", "invoice",
    "goods receipt", "achats", "procure", "p2p", "doublon", "duplicate",
]
_IT_KEYWORDS = [
    "acces", "access", "habilitation", "iam", "annuaire", "directory",
    "separation des taches", "segregation", "sod", "privilegi", "privileged",
    "comptes utilisateurs", "user account", "droits", "roles erp", "role erp",
    "depart", "leaver", "mobilite", "revue des acces", "user access review",
]
# NB : éviter les mots trop courts ("role" est contenu dans "controle",
# "compte" dans "comptable"...).


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"<[^>]+>", " ", text)          # retire le HTML OpenPages
    return text.lower()


def _score(text: str, keywords: list[str]) -> int:
    return sum(1 for k in keywords if k in text)


def _detect_domain(description: str) -> str:
    text = _normalize(description)
    fin, it = _score(text, _FIN_KEYWORDS), _score(text, _IT_KEYWORDS)
    if max(fin, it) < 2:
        return "unknown"
    if fin == it:
        return "unknown"
    return "finance_p2p" if fin > it else "it_access_sod"


# ── Jeux de résultats simulés ────────────────────────────────────────────────
def _finance_evidence(fail: bool) -> dict:
    exceptions = [
        {
            "type": "near_duplicate_invoice",
            "detail": "Factures FAC-2026-08841 et FAC-2026-08B41 (fournisseur "
                      "Fournitures Industrielles SAS, 18 450,00 EUR) : doublon proche "
                      "détecté et bloqué avant paiement.",
            "resolved": True,
        }
    ]
    if fail:
        exceptions.append({
            "type": "payment_out_of_tolerance",
            "detail": "Paiement PAY-2026-11307 (commande PO-4500172233, fournisseur "
                      "Transports Rhône Logistique) : facturé 52 714,00 EUR pour une "
                      "commande de 50 980,00 EUR, écart +3,4 % (tolérance ±2 %), "
                      "aucune dérogation approuvée trouvée.",
            "resolved": False,
            "deviation_pct": 3.4,
            "approved_waiver": False,
        })
    return {
        "control_type": "Finance - Rapprochement commande / réception / facture",
        "test_period": TEST_PERIOD,
        "data_sources": ["ERP : commandes, réceptions, factures, paiements",
                         "Factures PDF (extraction IA)"],
        "population": {"purchase_orders": 1312, "goods_receipts": 1298,
                       "invoices": 1287, "payments": 1265,
                       "invoice_pdfs_extracted": 1287},
        "results": {
            "three_way_matched": 1263 if fail else 1265,
            "tolerance_pct": TOLERANCE_PCT,
            "payments_out_of_tolerance_without_waiver": 1 if fail else 0,
            "payments_out_of_tolerance_with_waiver": 2,
            "near_duplicates_detected": 1,
            "near_duplicates_paid": 0,
        },
        "exceptions": exceptions,
        "rule": f"Ineffective si au moins un paiement sort de la tolérance "
                f"(±{TOLERANCE_PCT:g} %) sans dérogation approuvée.",
    }


def _it_evidence(fail: bool) -> dict:
    exceptions = [
        {
            "type": "sod_conflict",
            "detail": "Utilisateur M. LEROY : rôles 'Création fournisseur' et "
                      "'Proposition de paiement' dans l'ERP. Conflit couvert par le "
                      "contrôle compensatoire CC-AP-07 (revue mensuelle des paiements "
                      "par le contrôle de gestion), exécuté et documenté en septembre.",
            "compensating_control": "CC-AP-07",
            "resolved": True,
        }
    ]
    if fail:
        exceptions.append({
            "type": "leaver_account_active",
            "detail": "Compte ERP 'jmartin' toujours actif 47 jours après le départ "
                      "(date de sortie RH : 14/08/2026), au-delà du seuil de 30 jours.",
            "resolved": False,
            "days_after_departure": 47,
        })
    return {
        "control_type": "IT - Revue des accès et séparation des tâches (ERP)",
        "test_period": TEST_PERIOD,
        "data_sources": ["Annuaire / IAM", "Référentiel RH (départs, mobilités)",
                         "Rôles ERP", "Matrice de séparation des tâches"],
        "population": {"active_erp_accounts": 2846, "hr_leavers_in_period": 41,
                       "hr_mobilities_in_period": 63, "privileged_accounts": 18},
        "results": {
            "leaver_max_days_threshold": LEAVER_MAX_DAYS,
            "leaver_accounts_disabled": 40 if fail else 41,
            "leaver_accounts_active_beyond_threshold": 1 if fail else 0,
            "max_days_between_departure_and_deactivation_worst_case": 47 if fail else 6,
            "sod_conflicts_detected": 1,
            "sod_conflicts_without_compensating_control": 0,
            "privileged_accounts_without_justification": 0,
            "mobility_rights_reviewed": 63,
        },
        "exceptions": exceptions,
        "remediation_priority": (["P1 - Désactiver immédiatement le compte 'jmartin'"]
                                 if fail else [])
        + ["P3 - Réduire le conflit SoD de M. LEROY lors de la prochaine revue des rôles"],
        "rule": f"Ineffective s'il reste un compte d'une personne partie plus de "
                f"{LEAVER_MAX_DAYS} jours après son départ, ou un conflit de tâches "
                f"non couvert par un contrôle compensatoire.",
    }


@tool(
    name="simulate_control_test",
    description=(
        "Exécute un test SIMULÉ d'efficacité opérationnelle à partir de la description "
        "d'un contrôle interne, et renvoie les résultats du test (population testée, "
        "anomalies, règle de conclusion). À appeler une fois par contrôle à évaluer."
    ),
    permission=ToolPermission.READ_ONLY,
)
def simulate_control_test(control_description: str, scenario: str = "auto") -> dict:
    """
    Simule le test d'un contrôle interne et renvoie les preuves collectées.

    Args:
        control_description (str): Description complète du contrôle, telle que saisie dans OpenPages.
        scenario (str): "auto" (par défaut, résultat de démo standard), "pass" (forcer un test sans anomalie) ou "fail" (forcer une anomalie bloquante).

    Returns:
        dict: Résultats simulés du test : type de contrôle, période, sources, population, résultats chiffrés, anomalies et règle de conclusion.
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
            "control_type": "Non reconnu",
            "test_period": TEST_PERIOD,
            "evidence_available": False,
            "reason": "La description ne permet pas d'identifier l'objectif du "
                      "contrôle, la population à tester ni les sources de données. "
                      "Aucun test n'a pu être exécuté.",
        }

    # Verdict calculé ici, de façon déterministe : l'agent doit le recopier tel quel.
    evidence = {"conclusion": "Ineffective" if fail else "Effective", **evidence}
    evidence["evidence_available"] = True
    evidence["simulated"] = True
    return evidence
