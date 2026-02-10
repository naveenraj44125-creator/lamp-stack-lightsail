#!/bin/bash

# Test script for modular setup
# Verifies all modules load correctly and functions are available

# Don't exit on error - we want to count failures
set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Modular Setup Test Suite                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Helper function
test_result() {
    local test_name="$1"
    local result="$2"
    
    if [[ "$result" == "pass" ]]; then
        echo -e "  ${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗${NC} $test_name"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check all module files exist
echo -e "${BLUE}Test 1: Module Files Exist${NC}"
for module in 00-variables.sh 01-utils.sh 02-ui.sh 03-project-analysis.sh 04-github.sh 05-aws.sh; do
    if [[ -f "setup/$module" ]]; then
        test_result "$module exists" "pass"
    else
        test_result "$module exists" "fail"
    fi
done
echo ""

# Test 2: Check syntax of all modules
echo -e "${BLUE}Test 2: Module Syntax${NC}"
for module in setup/*.sh; do
    if bash -n "$module" 2>/dev/null; then
        test_result "$(basename $module) syntax valid" "pass"
    else
        test_result "$(basename $module) syntax valid" "fail"
    fi
done
echo ""

# Test 3: Check main script syntax
echo -e "${BLUE}Test 3: Main Script${NC}"
if bash -n setup.sh 2>/dev/null; then
    test_result "setup.sh syntax valid" "pass"
else
    test_result "setup.sh syntax valid" "fail"
fi
echo ""

# Test 4: Check modules can be sourced
echo -e "${BLUE}Test 4: Module Loading${NC}"
if bash -c 'source setup.sh 2>/dev/null' &>/dev/null; then
    test_result "All modules load successfully" "pass"
else
    test_result "All modules load successfully" "fail"
fi
echo ""

# Test 5: Check key functions exist
echo -e "${BLUE}Test 5: Function Availability${NC}"
bash -c '
source setup.sh 2>/dev/null
declare -f to_lowercase &>/dev/null && echo "to_lowercase:pass" || echo "to_lowercase:fail"
declare -f check_prerequisites &>/dev/null && echo "check_prerequisites:pass" || echo "check_prerequisites:fail"
declare -f get_input &>/dev/null && echo "get_input:pass" || echo "get_input:fail"
declare -f get_yes_no &>/dev/null && echo "get_yes_no:pass" || echo "get_yes_no:fail"
declare -f select_option &>/dev/null && echo "select_option:pass" || echo "select_option:fail"
declare -f analyze_project_for_recommendations &>/dev/null && echo "analyze_project_for_recommendations:pass" || echo "analyze_project_for_recommendations:fail"
declare -f detect_health_endpoints &>/dev/null && echo "detect_health_endpoints:pass" || echo "detect_health_endpoints:fail"
declare -f create_github_repo_if_needed &>/dev/null && echo "create_github_repo_if_needed:pass" || echo "create_github_repo_if_needed:fail"
declare -f create_iam_role_if_needed &>/dev/null && echo "create_iam_role_if_needed:pass" || echo "create_iam_role_if_needed:fail"
' | while IFS=: read func result; do
    test_result "$func() exists" "$result"
done
echo ""

# Test 6: Check documentation exists
echo -e "${BLUE}Test 6: Documentation${NC}"
for doc in setup/README.md setup/QUICK_REFERENCE.md setup/IMPROVEMENTS.md; do
    if [[ -f "$doc" ]]; then
        test_result "$(basename $doc) exists" "pass"
    else
        test_result "$(basename $doc) exists" "fail"
    fi
done
echo ""

# Test 7: Check module dependencies
echo -e "${BLUE}Test 7: Module Dependencies${NC}"
# Test that modules can be loaded in order
if bash -c '
source setup/00-variables.sh 2>/dev/null &&
source setup/01-utils.sh 2>/dev/null &&
source setup/02-ui.sh 2>/dev/null &&
source setup/03-project-analysis.sh 2>/dev/null &&
source setup/04-github.sh 2>/dev/null &&
source setup/05-aws.sh 2>/dev/null
' &>/dev/null; then
    test_result "Modules load in correct order" "pass"
else
    test_result "Modules load in correct order" "fail"
fi
echo ""

# Test 8: Check utility functions work
echo -e "${BLUE}Test 8: Utility Functions${NC}"
result=$(bash -c '
source setup/00-variables.sh 2>/dev/null
source setup/01-utils.sh 2>/dev/null
to_lowercase "HELLO"
' 2>/dev/null)
if [[ "$result" == "hello" ]]; then
    test_result "to_lowercase() works" "pass"
else
    test_result "to_lowercase() works" "fail"
fi

result=$(bash -c '
source setup/00-variables.sh 2>/dev/null
source setup/01-utils.sh 2>/dev/null
to_uppercase "hello"
' 2>/dev/null)
if [[ "$result" == "HELLO" ]]; then
    test_result "to_uppercase() works" "pass"
else
    test_result "to_uppercase() works" "fail"
fi
echo ""

# Results summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Results Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "  Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ ALL TESTS PASSED                                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ✗ SOME TESTS FAILED                                       ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
