"""
Offline tests: no network call, no dependency on watsonx Orchestrate.

The ADK @tool decorator is replaced by a fake module so that the
simulate_control_test stub can be imported and tested without installing the ADK.
"""

import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _install_fake_adk() -> None:
    if "ibm_watsonx_orchestrate.agent_builder.tools" in sys.modules:
        return
    tools = types.ModuleType("ibm_watsonx_orchestrate.agent_builder.tools")

    class ToolPermission:
        READ_ONLY = "read_only"

    tools.ToolPermission = ToolPermission
    tools.tool = lambda **_kwargs: (lambda fn: fn)
    sys.modules["ibm_watsonx_orchestrate"] = types.ModuleType("ibm_watsonx_orchestrate")
    sys.modules["ibm_watsonx_orchestrate.agent_builder"] = types.ModuleType(
        "ibm_watsonx_orchestrate.agent_builder")
    sys.modules["ibm_watsonx_orchestrate.agent_builder.tools"] = tools


_install_fake_adk()
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "scripts"))
