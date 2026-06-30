#!/bin/bash

# IntelAI Presentation Verification Script
# Tests all critical functionality for presentation
# Run this from the IntelAI directory: ./scripts/test_intelai_presentation.sh

echo "=========================================="
echo "IntelAI Presentation Verification Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INTELAI_BASE="https://intelai.ysiddo-ai-projects.app"
INTELAI_API="https://intelai.ysiddo-ai-projects.app/api/v1"

# Change to IntelAI directory
cd "$(dirname "$0")/.." || { echo "IntelAI directory not found"; exit 1; }

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing: $test_name... "
    
    if output=$(eval "$test_command" 2>&1); then
        if echo "$output" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}PASSED${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo -e "${RED}FAILED${NC} (pattern not found)"
            echo "Output: $output"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        echo -e "${RED}FAILED${NC} (command failed)"
        echo "Error: $output"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "Phase 1: Live Endpoint Testing"
echo "-------------------------------"

# Test 1: Health endpoint
run_test "Health Check" \
    "curl -s -m 10 '$INTELAI_BASE/health'" \
    "healthy"

# Test 2: Demo login (CFO role)
run_test "Demo Login (CFO)" \
    "curl -s -m 10 -X POST '$INTELAI_API/auth/demo-login?role=cfo'" \
    "access_token"

# Test 3: Demo login (CEO role)  
run_test "Demo Login (CEO)" \
    "curl -s -m 10 -X POST '$INTELAI_API/auth/demo-login?role=ceo'" \
    "access_token"

# Test 4: Demo login (Analyst role)
run_test "Demo Login (Analyst)" \
    "curl -s -m 10 -X POST '$INTELAI_API/auth/demo-login?role=analyst'" \
    "access_token"

echo ""
echo "Phase 2: API Functionality Testing"
echo "-----------------------------------"

# Get a token for authenticated tests
TOKEN=$(curl -s -m 10 -X POST "$INTELAI_API/auth/demo-login?role=cfo" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✓ Got access token for authenticated tests"
    
    # Test 5: Get KPIs
    run_test "Get KPIs" \
        "curl -s -m 10 -H 'Authorization: Bearer $TOKEN' '$INTELAI_API/kpis'" \
        "metric"
    
    # Test 6: Get insights summary
    run_test "Get Insights Summary" \
        "curl -s -m 10 -H 'Authorization: Bearer $TOKEN' '$INTELAI_API/insights/summary'" \
        "summary"
    
    # Test 7: Get health index
    run_test "Get Health Index" \
        "curl -s -m 10 -H 'Authorization: Bearer $TOKEN' '$INTELAI_API/insights/health'" \
        "score"
    
    # Test 8: Get risk score
    run_test "Get Risk Score" \
        "curl -s -m 10 -H 'Authorization: Bearer $TOKEN' '$INTELAI_API/insights/risk'" \
        "score"
    
    # Test 9: Get personas
    run_test "Get Personas" \
        "curl -s -m 10 -H 'Authorization: Bearer $TOKEN' '$INTELAI_API/personas'" \
        "persona"
    
    # Test 10: Get glossary
    run_test "Get Glossary" \
        "curl -s -m 10 -H 'Authorization: Bearer $TOKEN' '$INTELAI_API/glossary'" \
        "term"
else
    echo -e "${YELLOW}⚠ Skipping authenticated tests (no token obtained)${NC}"
fi

echo ""
echo "Phase 3: PDF Export Verification"
echo "----------------------------------"

# Test 11: Check if reportlab is installed
run_test "ReportLab Installation" \
    "python3 -c 'import reportlab; print(reportlab.__version__)'" \
    "[0-9]"

# Test 12: Check if board_report module exists
run_test "Board Report Module" \
    "python3 -c 'from src.services.board_report import generate_board_pdf; print(\"OK\")'" \
    "OK"

echo ""
echo "Phase 4: Bilingual Support Verification"
echo "----------------------------------------"

# Test 13: Check i18n module
run_test "i18n Module" \
    "python3 -c 'from src.core.i18n import I18N, t; I18N.set_language(\"fr\"); print(t(\"AUTH\", \"login\"))'" \
    "Se connecter"

# Test 14: Check frontend translations file
run_test "Frontend Translations" \
    "test -f IntelAI/frontend/src/i18n/translations.js && echo 'exists'" \
    "exists"

# Test 15: Check I18nContext component
run_test "I18n Context Component" \
    "test -f IntelAI/frontend/src/i18n/I18nContext.jsx && echo 'exists'" \
    "exists"

echo ""
echo "Phase 5: Git and Repository Status"
echo "------------------------------------"

# Test 16: Check git status
run_test "Git Status" \
    "cd IntelAI && git status --porcelain || echo 'clean'" \
    ""

# Test 17: Check for AI co-authors (should return nothing)
run_test "No AI Co-Authors" \
    "cd IntelAI && git log --all --oneline | grep -i 'co-authored-by.*claude\|co-authored-by.*gpt\|co-authored-by.*ai' || echo 'clean'" \
    "clean"

# Test 18: Check current branch
run_test "Git Branch" \
    "cd IntelAI && git branch --show-current" \
    "main\|develop"

echo ""
echo "Phase 6: Configuration and Environment"
echo "---------------------------------------"

# Test 19: Check .env.example exists
run_test "Environment Example" \
    "test -f IntelAI/.env.example && echo 'exists'" \
    "exists"

# Test 20: Check DEFAULT_LANGUAGE in .env.example
run_test "Default Language Config" \
    "grep -q 'DEFAULT_LANGUAGE' IntelAI/.env.example && echo 'found'" \
    "found"

# Test 21: Check CURRENCY in .env.example  
run_test "Currency Config" \
    "grep -q 'CURRENCY' IntelAI/.env.example && echo 'found'" \
    "found"

echo ""
echo "Phase 7: Critical Feature Verification"
echo "---------------------------------------"

# Test 22: Check ExportMenu component
run_test "Export Menu Component" \
    "test -f IntelAI/frontend/src/components/ExportMenu.jsx && echo 'exists'" \
    "exists"

# Test 23: Check for PDF export function
run_test "PDF Export Function" \
    "grep -q 'printReport' IntelAI/frontend/src/components/ExportMenu.jsx && echo 'found'" \
    "found"

# Test 24: Check hybrid retrieval service
run_test "Hybrid Retrieval Service" \
    "test -f IntelAI/src/services/hybrid_retrieval.py && echo 'exists'" \
    "exists"

# Test 25: Check GraphRAG entity extractor
run_test "GraphRAG Entity Extractor" \
    "test -f IntelAI/src/services/entity_extractor.py && echo 'exists'" \
    "exists"

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! IntelAI is ready for presentation.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the failures above.${NC}"
    exit 1
fi