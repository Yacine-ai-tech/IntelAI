#!/bin/bash
# Generate diverse benchmark scenarios for IntelAI
# This script creates multiple business health scenarios for comprehensive testing

set -e

cd "$(dirname "$0")/.."

echo "🎯 Generating IntelAI benchmark scenarios..."
echo ""

SCENARIOS=("healthy" "declining_financial" "high_churn_crisis" "operational_meltdown" "talent_crisis" "cybersecurity_breach" "esg_compliance_failure")

for scenario in "${SCENARIOS[@]}"; do
    echo "📊 Generating scenario: $scenario"
    python3 -m src.data.seed "$scenario"
    echo "✅ $scenario completed"
    echo ""
done

echo "🎉 All scenarios generated successfully!"
echo ""
echo "Available scenarios:"
for scenario in "${SCENARIOS[@]}"; do
    echo "  - $scenario"
done

echo ""
echo "To use a specific scenario:"
echo "  python3 -m src.data.seed <scenario_name>"
echo ""
echo "To seed with the default healthy scenario:"
echo "  python3 -m src.data.seed"
