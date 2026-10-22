#!/usr/bin/env bash
# Full deployment script for watsonx Orchestrate.
# Imports the stub tool and the control evaluation agent, then publishes the agent (live).
# Usage: ./scripts/deploy_complete.sh   (from the repo root)

set -euo pipefail
cd "$(dirname "$0")/.."

ORCH="${ORCH:-orchestrate}"

echo "=========================================="
echo "Control evaluation agent - full deployment"
echo "=========================================="
echo ""

# Check that the orchestrate CLI exists
if ! command -v "$ORCH" >/dev/null 2>&1; then
  echo "ERROR: orchestrate CLI not found ($ORCH)"
  echo "Run: pip install ibm-watsonx-orchestrate"
  exit 1
fi

# Check that an environment is active
echo "📋 Checking the active environment..."
"$ORCH" env list | grep "(active)" || {
  echo "⚠️  No active watsonx Orchestrate environment"
  echo "Run: orchestrate env activate <environment-name>"
  exit 1
}
echo "✅ Environment active"
echo ""

echo "=========================================="
echo "🔧 Step 1/3: Importing the stub tool"
echo "=========================================="
"$ORCH" tools import -k python \
  -f tools/simulate_control_test.py \
  -r tools/requirements.txt
echo "✅ Tool simulate_control_test imported"
echo ""

echo "=========================================="
echo "🤖 Step 2/3: Importing the agent (draft)"
echo "=========================================="
"$ORCH" agents import -f agents/control_evaluation_agent.yaml
echo "✅ Agent Control_Evaluation_Agent imported"
echo ""

echo "=========================================="
echo "🚀 Step 3/3: Publishing the agent (live, required for OpenPages)"
echo "=========================================="
"$ORCH" agents deploy --name Control_Evaluation_Agent
echo ""

echo "=========================================="
echo "✅ Deployment complete"
echo "=========================================="
echo "Test it with: python scripts/test_agent.py"
