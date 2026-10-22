#!/usr/bin/env python3
"""
End-to-end test of the deployed Control_Evaluation_Agent, called exactly the way
OpenPages calls it (POST /v1/orchestrate/{agent_id}/chat/completions).

Usage (from the repo root):
    python scripts/test_agent.py                 # all cases in tests/agent_test_cases.json
    python scripts/test_agent.py --repeat 5      # each case 5 times (stability)
    python scripts/test_agent.py "My control description..."   # ad-hoc case

Reads WO_INSTANCE and WO_API_KEY from the local .env.sdk file (repo root).
"""

import json
import os
import pathlib
import sys

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENT_NAME = "Control_Evaluation_Agent"
ALLOWED = {"Effective", "Ineffective", "Not Determined"}
TEST_PERIOD_MARK = "2026-09-01"  # start of TEST_PERIOD in tools/simulate_control_test.py


def load_env() -> None:
    env_file = ROOT / ".env.sdk"
    if not env_file.exists():
        sys.exit(".env.sdk not found: copy .env.sdk.exemple to .env.sdk at the repo root and fill it in.")
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


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
        sys.exit(f"Agent {AGENT_NAME} not found: has it been imported?")
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
        sys.exit("Unexpected response (adapt the OpenPages JSONata accordingly):\n"
                 + json.dumps(payload, indent=2, ensure_ascii=False)[:3000])
    if isinstance(content, list):  # possible "structured" format: keep the text blocks
        print("      (info) content returned as a list -> adapt the JSONata")
        content = "".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content


def check(raw: str) -> tuple[bool, str, dict | None]:
    """Check that the answer is exactly the expected flat JSON."""
    if not isinstance(raw, str):
        return False, f"content is not a string: {type(raw).__name__}", None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False, "answer is not pure JSON (text or ``` around it?)", None
    if set(data) != {"OperatingEffectiveness", "Explanation"}:
        return False, f"unexpected keys: {sorted(data)}", data
    if data["OperatingEffectiveness"] not in ALLOWED:
        return False, f"status not allowed: {data['OperatingEffectiveness']!r}", data
    # The stub's test period must appear in the explanation; otherwise the agent
    # answered without calling the tool (invented result).
    if TEST_PERIOD_MARK not in data["Explanation"]:
        return False, "stub test period missing: answer probably invented without calling the tool", data
    return True, "format OK", data


def main() -> None:
    load_env()
    base = os.environ["WO_INSTANCE"].rstrip("/")
    headers = {"Authorization": f"Bearer {iam_token(os.environ['WO_API_KEY'])}",
               "Content-Type": "application/json"}
    agent_id = find_agent_id(base, headers)
    print(f"Agent {AGENT_NAME}: {agent_id}\n")

    args = sys.argv[1:]
    repeat = 1
    if args[:1] == ["--repeat"]:
        repeat, args = int(args[1]), args[2:]

    if args:
        cases = [{"id": "AD_HOC", "expected": None, "control_description": " ".join(args)}]
    else:
        cases = json.loads((ROOT / "tests" / "agent_test_cases.json").read_text(encoding="utf-8"))

    failures = runs = 0
    for n in range(1, repeat + 1):
        if repeat > 1:
            print(f"===== Run {n}/{repeat} =====")
        for case in cases:
            raw = ask(base, headers, agent_id, case["control_description"])
            ok, msg, data = check(raw)
            if ok and case["expected"] and data["OperatingEffectiveness"] != case["expected"]:
                ok, msg = False, f"expected {case['expected']}, got {data['OperatingEffectiveness']}"
            failures += not ok
            runs += 1
            print(f"[{'OK' if ok else 'KO'}] {case['id']} — {msg}")
            print(f"      {raw}\n")

    print(f"All tests passed ({runs} calls)." if not failures
          else f"{failures} failure(s) out of {runs} calls.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
