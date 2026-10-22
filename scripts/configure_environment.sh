#!/usr/bin/env bash
# Registers and activates the watsonx Orchestrate environment from the local .env.sdk file.
# Usage: ./scripts/configure_environment.sh   (from the repo root)

set -euo pipefail
cd "$(dirname "$0")/.."

ORCH="${ORCH:-orchestrate}"

if [ ! -f .env.sdk ]; then
  echo "ERROR: .env.sdk not found. Copy .env.sdk.exemple to .env.sdk and fill it in."
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env.sdk
set +a

: "${WO_INSTANCE_ALIAS:?WO_INSTANCE_ALIAS is not set in .env.sdk}"
: "${WO_INSTANCE:?WO_INSTANCE is not set in .env.sdk}"
: "${WO_API_KEY:?WO_API_KEY is not set in .env.sdk}"

echo "📋 Registering environment '$WO_INSTANCE_ALIAS'..."
"$ORCH" env add -n "$WO_INSTANCE_ALIAS" -u "$WO_INSTANCE" --type ibm_iam 2>/dev/null \
  || echo "ℹ️  Environment already registered"

echo "🔑 Activating environment..."
"$ORCH" env activate "$WO_INSTANCE_ALIAS" -a "$WO_API_KEY"
echo "✅ Environment '$WO_INSTANCE_ALIAS' active"
