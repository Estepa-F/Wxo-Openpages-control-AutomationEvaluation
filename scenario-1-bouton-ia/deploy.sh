#!/usr/bin/env bash
# Déploie le tool et l'agent Control_Evaluation_Agent dans watsonx Orchestrate.
#
# Prérequis (une seule fois) :
#   pip install ibm-watsonx-orchestrate
#   orchestrate env add -n demo-controls -u "$WXO_URL" --type ibm_iam --activate
#   (la commande demande la clé API : colle WXO_API_KEY du fichier .env)
#
# Usage : ./deploy.sh   (depuis n'importe où ; le script se place dans son dossier)

set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/3 Import du tool simulate_control_test"
orchestrate tools import -k python \
  -f tools/simulate_control_test/simulate_control_test.py \
  -r tools/simulate_control_test/requirements.txt

echo "==> 2/3 Import de l'agent Control_Evaluation_Agent (brouillon)"
orchestrate agents import -f agents/Control_Evaluation_Agent.yaml

echo "==> 3/3 Publication en live (nécessaire pour l'appel depuis OpenPages)"
orchestrate agents deploy --name Control_Evaluation_Agent

echo ""
echo "Déploiement terminé. Teste avec :  python tests/run_tests.py"
