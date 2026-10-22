"""
Tests hors ligne : aucun appel réseau, aucune dépendance à watsonx Orchestrate.

Le décorateur @tool de l'ADK est remplacé par un faux module, pour pouvoir
importer et tester le bouchon simulate_control_test sans installer l'ADK.
"""

import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCENARIO_1 = REPO / "scenario-1-bouton-ia"
SCENARIO_2 = REPO / "scenario-2-rh-erp"


def _install_fake_adk() -> None:
    if "ibm_watsonx_orchestrate.agent_builder.tools" in sys.modules:
        return
    tools = types.ModuleType("ibm_watsonx_orchestrate.agent_builder.tools")

    class ToolPermission:  # noqa: D401 - simple stand-in
        READ_ONLY = "read_only"

    tools.ToolPermission = ToolPermission
    tools.tool = lambda **_kwargs: (lambda fn: fn)
    sys.modules["ibm_watsonx_orchestrate"] = types.ModuleType("ibm_watsonx_orchestrate")
    sys.modules["ibm_watsonx_orchestrate.agent_builder"] = types.ModuleType(
        "ibm_watsonx_orchestrate.agent_builder")
    sys.modules["ibm_watsonx_orchestrate.agent_builder.tools"] = tools


_install_fake_adk()
sys.path.insert(0, str(SCENARIO_1 / "tools" / "simulate_control_test"))
sys.path.insert(0, str(SCENARIO_2))
