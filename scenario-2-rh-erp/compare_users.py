#!/usr/bin/env python3
"""
Rapprochement des comptes ERP avec le référentiel RH (démo GRC).

Usage :
    python3 compare_users.py                      # date de revue par défaut : 2026-10-15
    python3 compare_users.py --date 2026-10-20
    python3 compare_users.py --json               # sortie JSON (pour automatiser)

Lit data/referentiel_rh.csv et data/comptes_erp.csv (séparateur ;) et détecte :
  1. comptes ERP actifs de personnes parties depuis plus de N jours (N = 30)
  2. comptes ERP sans correspondance RH (comptes orphelins)
  3. conflits de séparation des tâches (matrice SoD) sans contrôle compensatoire
  4. comptes à privilèges sans justification par le poste RH
  5. droits sensibles incompatibles avec la direction actuelle (mobilités non revues)

Conclusion (règle métier) : Ineffective s'il reste un compte de personne partie
plus de N jours après son départ, ou un conflit SoD non couvert par un contrôle
compensatoire. Sinon Effective.

Uniquement la bibliothèque standard Python : aucune installation nécessaire.
"""

import argparse
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RH_FILE = ROOT / "data" / "referentiel_rh.csv"
ERP_FILE = ROOT / "data" / "comptes_erp.csv"

LEAVER_MAX_DAYS = 30
DEFAULT_REVIEW_DATE = "2026-10-15"

# Matrice de séparation des tâches : couples de rôles incompatibles
SOD_MATRIX = [
    ("Création fournisseur", "Paiement fournisseurs"),
    ("Création commande", "Validation commande"),
    ("Saisie factures", "Validation factures"),
]
# Contrôles compensatoires documentés : {matricule: référence}
COMPENSATING_CONTROLS: dict[str, str] = {}

PRIVILEGED_ROLES = {"Administrateur ERP"}
PRIVILEGED_JUSTIFIED_POSTS = {"Administrateur ERP", "Responsable sécurité SI"}

# Droits sensibles : directions autorisées
SENSITIVE_ROLE_DIRECTIONS = {
    "Création fournisseur": {"Achats", "Finance"},
    "Paiement fournisseurs": {"Finance"},
}

SEVERITY_ORDER = {"Critique": 0, "Élevé": 1, "Moyen": 2, "Info": 3}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def to_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def analyse(review_date: date) -> dict:
    rh = {r["matricule"]: r for r in read_csv(RH_FILE)}
    erp = read_csv(ERP_FILE)
    gaps = []

    for acc in erp:
        active = acc["statut_compte"] == "Actif"
        roles = [r.strip() for r in acc["roles"].split("|") if r.strip()]
        person = rh.get(acc["matricule"])
        who = f"{acc['nom_complet']} ({acc['login']})"

        # 2. Compte orphelin
        if person is None:
            if active:
                privileged = PRIVILEGED_ROLES & set(roles)
                gaps.append({
                    "type": "Compte orphelin",
                    "gravite": "Élevé" if privileged else "Moyen",
                    "compte": who,
                    "detail": f"Compte actif sans correspondance RH "
                              f"(matricule « {acc['matricule'] or 'vide'} »), rôles : {', '.join(roles)}.",
                    "bloquant": False,
                })
            continue

        # 1. Personne partie avec compte actif
        leave = to_date(person["date_sortie"])
        # Un départ postérieur à la date de revue n'est pas encore effectif
        if person["statut"] == "Parti" and active and leave and leave <= review_date:
            days = (review_date - leave).days
            last = to_date(acc["derniere_connexion"])
            used_after = last and last > leave
            beyond = days > LEAVER_MAX_DAYS
            detail = (f"Départ le {leave:%d/%m/%Y}, compte toujours actif {days} jours après "
                      f"(seuil {LEAVER_MAX_DAYS} j)")
            if used_after:
                detail += f" ; connexion le {last:%d/%m/%Y}, APRÈS le départ"
            gaps.append({
                "type": "Partant avec compte actif",
                "gravite": "Critique" if beyond else "Info",
                "compte": who,
                "detail": detail + ("." if beyond else " ; dans le délai toléré."),
                "short": f"compte actif {days} jours après le départ"
                         + (" et utilisé après le départ" if used_after else ""),
                "bloquant": beyond,
            })

        if not active:
            continue

        # 3. Conflits SoD
        for a, b in SOD_MATRIX:
            if a in roles and b in roles:
                comp = COMPENSATING_CONTROLS.get(acc["matricule"])
                gaps.append({
                    "type": "Conflit SoD",
                    "gravite": "Info" if comp else "Élevé",
                    "compte": who,
                    "detail": f"Cumule « {a} » et « {b} »"
                              + (f", couvert par {comp}." if comp else ", sans contrôle compensatoire."),
                    "short": f"cumule {a} et {b} sans contrôle compensatoire",
                    "bloquant": comp is None,
                })

        # 4. Comptes à privilèges
        if PRIVILEGED_ROLES & set(roles) and person["poste"] not in PRIVILEGED_JUSTIFIED_POSTS:
            gaps.append({
                "type": "Privilège non justifié",
                "gravite": "Élevé",
                "compte": who,
                "detail": f"Rôle administrateur alors que le poste RH est « {person['poste']} ».",
                "bloquant": False,
            })

        # 5. Droits sensibles incompatibles avec la direction (mobilités)
        if person["statut"] != "Parti":
            for role in roles:
                allowed = SENSITIVE_ROLE_DIRECTIONS.get(role)
                if allowed and person["direction"] not in allowed:
                    origin = f" ({person['commentaire']} le {to_date(person['date_mobilite']):%d/%m/%Y})" \
                        if person["date_mobilite"] else ""
                    gaps.append({
                        "type": "Droits non revus après mobilité",
                        "gravite": "Moyen",
                        "compte": who,
                        "detail": f"Conserve « {role} » alors que sa direction est "
                                  f"désormais {person['direction']}{origin}.",
                        "bloquant": False,
                    })

    gaps.sort(key=lambda g: (SEVERITY_ORDER[g["gravite"]], g["type"], g["compte"]))
    blocking = [g for g in gaps if g["bloquant"]]
    conclusion = "Ineffective" if blocking else "Effective"

    stats = {
        "personnes_rh": len(rh),
        "comptes_erp": len(erp),
        "comptes_erp_actifs": sum(1 for a in erp if a["statut_compte"] == "Actif"),
        "partants": sum(1 for p in rh.values() if p["statut"] == "Parti"),
        "ecarts": len([g for g in gaps if g["gravite"] != "Info"]),
        "ecarts_bloquants": len(blocking),
    }
    return {"date_revue": review_date.isoformat(), "stats": stats, "conclusion": conclusion,
            "ecarts": gaps, "explication": build_explanation(review_date, stats, gaps, conclusion)}


def build_explanation(review_date: date, stats: dict, gaps: list[dict], conclusion: str) -> str:
    """Texte prêt à écrire dans « Control Operating Effectively Explanation » (≤ 1 000 car.)."""
    head = (f"[Rapprochement RH / ERP du {review_date:%d/%m/%Y}] {stats['personnes_rh']} personnes RH "
            f"comparées à {stats['comptes_erp']} comptes ERP : {stats['ecarts']} écarts, "
            f"dont {stats['ecarts_bloquants']} bloquants. ")
    if conclusion == "Effective":
        return head + "Aucun partant actif au-delà du seuil ni conflit SoD non couvert : contrôle efficace."
    blocking = [g for g in gaps if g["bloquant"]]
    parts = [f"{g['compte']} – {g['short']}" for g in blocking]
    text = (head + "Écarts bloquants : " + " ; ".join(parts) + ". "
            "Remédiation : désactiver immédiatement les comptes des partants, retirer le cumul "
            "de rôles incompatibles, supprimer ou rattacher les comptes orphelins.")
    return text.replace("'", "’")[:1000]


def print_report(result: dict) -> None:
    s = result["stats"]
    print(f"## Rapprochement RH / ERP — revue du {date.fromisoformat(result['date_revue']):%d/%m/%Y}\n")
    print(f"- Personnes au référentiel RH : {s['personnes_rh']} (dont {s['partants']} partants)")
    print(f"- Comptes ERP : {s['comptes_erp']} (dont {s['comptes_erp_actifs']} actifs)")
    print(f"- Écarts détectés : {s['ecarts']} (dont {s['ecarts_bloquants']} bloquants)\n")
    print("| Gravité | Type d’écart | Compte | Détail |")
    print("|---|---|---|---|")
    for g in result["ecarts"]:
        flag = " 🔴" if g["bloquant"] else ""
        print(f"| {g['gravite']}{flag} | {g['type']} | {g['compte']} | {g['detail']} |")
    print(f"\n**Conclusion : {result['conclusion']}**\n")
    print(f"Explication pour OpenPages :\n{result['explication']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--date", default=DEFAULT_REVIEW_DATE, help="date de revue AAAA-MM-JJ")
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    args = parser.parse_args()
    res = analyse(date.fromisoformat(args.date))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print_report(res)
