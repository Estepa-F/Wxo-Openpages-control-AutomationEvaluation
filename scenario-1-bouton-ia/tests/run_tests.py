"""
Teste l'agent Control_Evaluation_Agent déployé dans watsonx Orchestrate,
exactement comme OpenPages l'appellera (POST /v1/orchestrate/{agent_id}/chat/completions).

Usage (depuis le dossier scenario-1-bouton-ia) :
    python tests/run_tests.py              # tous les cas de tests/test_cases.json
    python tests/run_tests.py --repeat 3   # chaque cas 3 fois (stabilité)
    python tests/run_tests.py "Ma description de contrôle..."   # un cas libre

Lit WXO_URL et WXO_API_KEY dans le fichier .env (racine du repo).
"""

import json
import os
import pathlib
import sys

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENT_NAME = "Control_Evaluation_Agent"
ALLOWED = {"Effective", "Ineffective", "Not Determined"}
TEST_PERIOD_MARK = "01/09/2026"  # début de TEST_PERIOD dans simulate_control_test.py


def load_env() -> None:
    # .env à la racine du repo (recommandé) ou dans le dossier du scénario
    candidates = [ROOT.parent / ".env", ROOT / ".env"]
    env_file = next((c for c in candidates if c.exists()), None)
    if env_file is None:
        sys.exit("Fichier .env introuvable : copier .env.sample en .env à la racine du repo et le remplir.")
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def iam_token(api_key: str) -> str:
    r = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
        headers={"Accept": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def find_agent_id(base: str, headers: dict) -> str:
    r = requests.get(f"{base}/v1/orchestrate/agents", headers=headers,
                     params={"names": AGENT_NAME}, timeout=30)
    r.raise_for_status()
    agents = [a for a in r.json() if a.get("name") == AGENT_NAME]
    if not agents:
        sys.exit(f"Agent {AGENT_NAME} introuvable : l'as-tu importé ?")
    return agents[0]["id"]


def ask(base: str, headers: dict, agent_id: str, description: str) -> str:
    body = {"messages": [{"role": "user", "content": description}], "stream": False}
    r = requests.post(f"{base}/v1/orchestrate/{agent_id}/chat/completions",
                      headers=headers, json=body, timeout=180)
    r.raise_for_status()
    payload = r.json()
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        sys.exit("Réponse inattendue (adapter le JSONata en conséquence) :\n"
                 + json.dumps(payload, indent=2, ensure_ascii=False)[:3000])
    if isinstance(content, list):  # format "structuré" possible : on garde les blocs texte
        print("      (info) content renvoyé sous forme de liste -> adapter le JSONata")
        content = "".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content


def check(raw: str) -> tuple[bool, str, dict | None]:
    """Vérifie que la réponse est exactement le JSON attendu."""
    if not isinstance(raw, str):
        return False, f"content n'est pas une chaîne : {type(raw).__name__}", None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False, "la réponse n'est pas du JSON pur (texte ou ``` autour ?)", None
    if set(data) != {"OperatingEffectiveness", "Explanation"}:
        return False, f"clés inattendues : {sorted(data)}", data
    if data["OperatingEffectiveness"] not in ALLOWED:
        return False, f"statut non autorisé : {data['OperatingEffectiveness']!r}", data
    # La période du bouchon doit figurer dans l'explication : sinon l'agent a
    # répondu sans appeler le tool (résultat inventé).
    if TEST_PERIOD_MARK not in data["Explanation"]:
        return False, "période du bouchon absente : réponse probablement inventée sans appel au tool", data
    return True, "format OK", data


def main() -> None:
    load_env()
    base = os.environ["WXO_URL"].rstrip("/")
    headers = {"Authorization": f"Bearer {iam_token(os.environ['WXO_API_KEY'])}",
               "Content-Type": "application/json"}
    agent_id = find_agent_id(base, headers)
    print(f"Agent {AGENT_NAME} : {agent_id}\n")

    args = sys.argv[1:]
    repeat = 1
    if args[:1] == ["--repeat"]:
        repeat, args = int(args[1]), args[2:]

    if args:
        cases = [{"id": "LIBRE", "expected": None, "control_description": " ".join(args)}]
    else:
        cases = json.loads((ROOT / "tests" / "test_cases.json").read_text())

    failures = runs = 0
    for n in range(1, repeat + 1):
        if repeat > 1:
            print(f"===== Passage {n}/{repeat} =====")
        for case in cases:
            raw = ask(base, headers, agent_id, case["control_description"])
            ok, msg, data = check(raw)
            if ok and case["expected"] and data["OperatingEffectiveness"] != case["expected"]:
                ok, msg = False, f"attendu {case['expected']}, obtenu {data['OperatingEffectiveness']}"
            failures += not ok
            runs += 1
            print(f"[{'OK ' if ok else 'KO '}] {case['id']} — {msg}")
            print(f"      {raw}\n")

    print(f"Tous les tests passent ({runs} appels)." if not failures
          else f"{failures} échec(s) sur {runs} appels.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
