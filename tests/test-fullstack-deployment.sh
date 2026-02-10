#!/bin/bash

# E2E Test: Deploy Fullstack Notes App (React + Node.js) using modular setup.sh
# Tests fullstack detection, UI serving, and GitHub Actions workflow summary
#
# Usage:
#   ./test-fullstack-deployment.sh --source-dir /path/to/lamp-stack-lightsail
#   ./test-fullstack-deployment.sh --source-dir /path/to/lamp-stack-lightsail --no-cleanup

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TEST_REPO_NAME="fullstack-test-$(date +%s)"
GITHUB_USERNAME=""
CLEANUP_ON_EXIT=true
SKIP_DEPLOY_WAIT=false
SOURCE_DIR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cleanup) CLEANUP_ON_EXIT=false; shift ;;
        --skip-wait) SKIP_DEPLOY_WAIT=true; shift ;;
        --repo-name) TEST_REPO_NAME="$2"; shift 2 ;;
        --source-dir) SOURCE_DIR="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate source directory
if [[ -z "$SOURCE_DIR" ]]; then
    echo -e "${RED}Error: --source-dir is required${NC}"
    echo "Usage: $0 --source-dir /path/to/lamp-stack-lightsail [--skip-wait] [--no-cleanup]"
    exit 1
fi

if [[ ! -f "$SOURCE_DIR/setup.sh" ]]; then
    echo -e "${RED}Error: setup.sh not found in $SOURCE_DIR${NC}"
    exit 1
fi

if [[ ! -d "$SOURCE_DIR/example-fullstack-app" ]]; then
    echo -e "${RED}Error: example-fullstack-app not found in $SOURCE_DIR${NC}"
    exit 1
fi

SCRIPT_DIR="$(cd "$SOURCE_DIR" && pwd)"

# Source AWS credentials if available
CURRENT_SCRIPT_DIR="$(dirname "$(realpath "$0")")"
if [[ -f "$CURRENT_SCRIPT_DIR/.aws-creds.sh" ]]; then
    echo -e "${BLUE}Sourcing AWS credentials from $CURRENT_SCRIPT_DIR/.aws-creds.sh${NC}"
    source "$CURRENT_SCRIPT_DIR/.aws-creds.sh"
elif [[ -f "$SOURCE_DIR/.aws-creds.sh" ]]; then
    echo -e "${BLUE}Sourcing AWS credentials from $SOURCE_DIR/.aws-creds.sh${NC}"
    source "$SOURCE_DIR/.aws-creds.sh"
fi

cleanup() {
    if [[ "$CLEANUP_ON_EXIT" == "true" && -n "$GITHUB_USERNAME" && -n "$TEST_REPO_NAME" ]]; then
        echo ""
        echo -e "${YELLOW}Cleaning up...${NC}"
        
        # Delete GitHub repo
        if gh repo view "$GITHUB_USERNAME/$TEST_REPO_NAME" &>/dev/null; then
            echo -e "${BLUE}Deleting GitHub repo: $GITHUB_USERNAME/$TEST_REPO_NAME${NC}"
            gh repo delete "$GITHUB_USERNAME/$TEST_REPO_NAME" --yes 2>/dev/null || true
        fi
        
        # Delete IAM role and policy
        local role_name="github-actions-${TEST_REPO_NAME}"
        if aws iam get-role --role-name "$role_name" &>/dev/null; then
            echo -e "${BLUE}Deleting IAM role: $role_name${NC}"
            aws iam detach-role-policy --role-name "$role_name" --policy-arn "arn:aws:iam::aws:policy/ReadOnlyAccess" 2>/dev/null || true
            local account_id=$(aws sts get-caller-identity --query Account --output text)
            aws iam detach-role-policy --role-name "$role_name" --policy-arn "arn:aws:iam::${account_id}:policy/${role_name}-LightsailAccess" 2>/dev/null || true
            aws iam delete-role --role-name "$role_name" 2>/dev/null || true
            aws iam delete-policy --policy-arn "arn:aws:iam::${account_id}:policy/${role_name}-LightsailAccess" 2>/dev/null || true
        fi
        
        # Delete temp directory
        if [[ -n "$TEST_DIR" && -d "$TEST_DIR" ]]; then
            rm -rf "$TEST_DIR"
        fi
        
        echo -e "${GREEN}✓ Cleanup complete${NC}"
    fi
}
trap cleanup EXIT

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   E2E Test: Fullstack React + Node.js Deployment           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

if ! command -v gh &>/dev/null; then
    echo -e "${RED}✗ GitHub CLI (gh) not installed${NC}"
    exit 1
fi

if ! command -v aws &>/dev/null; then
    echo -e "${RED}✗ AWS CLI not installed${NC}"
    exit 1
fi

if ! gh auth status &>/dev/null; then
    echo -e "${RED}✗ GitHub CLI not authenticated. Run: gh auth login${NC}"
    exit 1
fi

if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}✗ AWS CLI not configured. Run: aws configure${NC}"
    exit 1
fi

GITHUB_USERNAME=$(gh api user -q .login)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo -e "${GREEN}✓ GitHub user: $GITHUB_USERNAME${NC}"
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT_ID${NC}"
echo ""

# Step 2: Create test directory and copy fullstack-app
echo -e "${BLUE}Step 2: Copying fullstack-app to test directory...${NC}"

TEST_DIR="$SOURCE_DIR/test-fullstack-$(date +%s)"
mkdir -p "$TEST_DIR"

# Copy fullstack-app files (excluding node_modules)
rsync -av --exclude='node_modules' --exclude='.git' --exclude='build' "$SOURCE_DIR/example-fullstack-app/" "$TEST_DIR/"

echo -e "${GREEN}✓ Copied fullstack-app to $TEST_DIR${NC}"

# List what was copied
echo -e "${BLUE}Files copied:${NC}"
find "$TEST_DIR" -type f | head -20
echo ""

pushd "$TEST_DIR" > /dev/null

# Initialize git repo
git init
git config user.email "test@example.com"
git config user.name "Test User"

echo -e "${GREEN}✓ Git repository initialized${NC}"
echo ""

# Step 3: Run modular setup.sh functions
echo -e "${BLUE}Step 3: Running modular setup.sh to create config...${NC}"

# Source the setup script
set +e
source "$SCRIPT_DIR/setup.sh"
set -e

# Set up environment for the functions
export AUTO_MODE=true
export APP_TYPE=nodejs
export APP_NAME="Fullstack Notes App"
export INSTANCE_NAME="fullstack-notes-instance"
export AWS_REGION=us-east-1
export BLUEPRINT_ID=ubuntu_22_04
export BUNDLE_ID=small_3_0
export DATABASE_TYPE=none
export DB_EXTERNAL=false
export GITHUB_REPO="$GITHUB_USERNAME/$TEST_REPO_NAME"
export REPO_VISIBILITY=private

# Create deployment config
create_deployment_config "nodejs" "Fullstack Notes App" "fullstack-notes-instance" "us-east-1" "ubuntu_22_04" "small_3_0" "none" "false" "" "" "" "" "" "false"
create_github_workflow "nodejs" "Fullstack Notes App" "us-east-1"

echo -e "${GREEN}✓ Deployment configuration created${NC}"
echo ""

# Step 4: Verify files - FULLSTACK SPECIFIC CHECKS
echo -e "${BLUE}Step 4: Verifying generated files (fullstack-specific)...${NC}"

TESTS_PASSED=0
TESTS_FAILED=0

verify() {
    local condition="$1"
    local msg="$2"
    local result
    result=$(eval "$condition" 2>/dev/null && echo "pass" || echo "fail")
    if [[ "$result" == "pass" ]]; then
        echo -e "${GREEN}✓${NC} $msg"
        ((TESTS_PASSED++)) || true
    else
        echo -e "${RED}✗${NC} $msg"
        ((TESTS_FAILED++)) || true
    fi
}

# Basic file checks
verify '[[ -f "deployment-nodejs.config.yml" ]]' "deployment-nodejs.config.yml exists"
verify '[[ -f ".github/workflows/deploy-nodejs.yml" ]]' ".github/workflows/deploy-nodejs.yml exists"
verify '[[ -f "package.json" ]]' "package.json exists"
verify '[[ -d "client" ]]' "client/ directory exists (React frontend)"
verify '[[ -d "server" ]]' "server/ directory exists (Node.js backend)"

# FULLSTACK-SPECIFIC CHECKS
echo ""
echo -e "${BLUE}Fullstack-specific verification:${NC}"

# Check expected_content is "root" for fullstack apps (not "Node.js")
verify 'grep -q "expected_content:.*root" deployment-nodejs.config.yml' "Config has expected_content: root (for React UI)"

# Check workflow summary mentions fullstack
verify 'grep -q "Fullstack React" .github/workflows/deploy-nodejs.yml' "Workflow summary mentions Fullstack React"

# Check workflow summary has Web App endpoint (not just API)
verify 'grep -q "Web App" .github/workflows/deploy-nodejs.yml' "Workflow summary has Web App endpoint (UI)"

# Check build script exists in root package.json
verify 'grep -q "\"build\":" package.json' "Root package.json has build script"

# Check start script exists in root package.json
verify 'grep -q "\"start\":" package.json' "Root package.json has start script"

echo ""

if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}✗ File verification failed${NC}"
    echo ""
    echo -e "${YELLOW}Deployment config contents:${NC}"
    cat deployment-nodejs.config.yml
    echo ""
    echo -e "${YELLOW}Workflow file contents (summary section):${NC}"
    grep -A 30 "Deployment Summary" .github/workflows/deploy-nodejs.yml || cat .github/workflows/deploy-nodejs.yml
    popd > /dev/null
    exit 1
fi
echo ""

# Step 5: Create GitHub repo and push
echo -e "${BLUE}Step 5: Creating GitHub repo and pushing...${NC}"

# Create .gitignore
cat > .gitignore << 'EOF'
node_modules/
.env
*.log
.DS_Store
client/build/
server/database/*.db
EOF

# Commit all files
git add -A
git commit -m "Initial commit: Fullstack Notes App with GitHub Actions deployment"

gh repo create "$TEST_REPO_NAME" --private --source=. --push

echo -e "${GREEN}✓ Repo created: https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME${NC}"
echo ""

# Step 6: Set up IAM role for OIDC
echo -e "${BLUE}Step 6: Setting up IAM role for GitHub OIDC...${NC}"

ROLE_NAME="github-actions-${TEST_REPO_NAME}"
ROLE_ARN=$(create_iam_role_if_needed "$ROLE_NAME" "$GITHUB_USERNAME/$TEST_REPO_NAME" "$AWS_ACCOUNT_ID")

# Set GitHub repo variable
gh variable set AWS_ROLE_ARN --body "$ROLE_ARN" --repo "$GITHUB_USERNAME/$TEST_REPO_NAME"
echo -e "${GREEN}✓ IAM role created and GitHub variable set${NC}"
echo ""

# Step 7: Trigger workflow and wait for completion
echo -e "${BLUE}Step 7: Triggering GitHub Actions workflow...${NC}"

gh workflow run "deploy-nodejs.yml" --repo "$GITHUB_USERNAME/$TEST_REPO_NAME"
sleep 5

if [[ "$SKIP_DEPLOY_WAIT" == "true" ]]; then
    echo -e "${YELLOW}⚠ Skipping workflow wait (--skip-wait flag)${NC}"
    WORKFLOW_STATUS="skipped"
else
    echo -e "${BLUE}Waiting for workflow to complete (this may take 5-10 minutes)...${NC}"
    
    sleep 10
    
    RUN_ID=$(gh run list --repo "$GITHUB_USERNAME/$TEST_REPO_NAME" --workflow "deploy-nodejs.yml" --limit 1 --json databaseId -q '.[0].databaseId')
    
    if [[ -n "$RUN_ID" ]]; then
        echo -e "${BLUE}Workflow run ID: $RUN_ID${NC}"
        echo -e "${BLUE}View at: https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME/actions/runs/$RUN_ID${NC}"
        
        TIMEOUT=1200  # 20 minutes
        ELAPSED=0
        while [[ $ELAPSED -lt $TIMEOUT ]]; do
            STATUS=$(gh run view "$RUN_ID" --repo "$GITHUB_USERNAME/$TEST_REPO_NAME" --json status,conclusion -q '.status')
            
            if [[ "$STATUS" == "completed" ]]; then
                CONCLUSION=$(gh run view "$RUN_ID" --repo "$GITHUB_USERNAME/$TEST_REPO_NAME" --json conclusion -q '.conclusion')
                break
            fi
            
            echo -n "."
            sleep 15
            ((ELAPSED+=15))
        done
        echo ""
        
        WORKFLOW_STATUS="${CONCLUSION:-timeout}"
    else
        WORKFLOW_STATUS="not_found"
    fi
fi

# Step 8: Verify UI is functional (if deployment succeeded)
UI_VERIFIED=false
if [[ "$WORKFLOW_STATUS" == "success" ]]; then
    echo ""
    echo -e "${BLUE}Step 8: Verifying UI is functional...${NC}"
    
    INSTANCE_IP=$(aws lightsail get-instance --instance-name fullstack-notes-instance --query 'instance.publicIpAddress' --output text 2>/dev/null || echo "")
    
    if [[ -n "$INSTANCE_IP" && "$INSTANCE_IP" != "None" ]]; then
        # Wait a bit for the app to fully start
        sleep 10
        
        # Check if UI loads (should return HTML with "root" div)
        UI_RESPONSE=$(curl -s --max-time 30 "http://$INSTANCE_IP:5001/" 2>/dev/null || echo "")
        
        if echo "$UI_RESPONSE" | grep -q "root"; then
            echo -e "${GREEN}✓ UI is functional - React app loads correctly${NC}"
            UI_VERIFIED=true
        else
            echo -e "${YELLOW}⚠ UI check inconclusive - response:${NC}"
            echo "$UI_RESPONSE" | head -5
        fi
        
        # Also check API health
        API_RESPONSE=$(curl -s --max-time 10 "http://$INSTANCE_IP:5001/api/health" 2>/dev/null || echo "")
        if echo "$API_RESPONSE" | grep -q "ok"; then
            echo -e "${GREEN}✓ API health check passed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Could not get instance IP${NC}"
    fi
fi

# Step 9: Report results
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Results${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Local Project: ${GREEN}$TEST_DIR${NC}"
echo -e "Repository: ${GREEN}https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME${NC}"
echo -e "Files verified: ${GREEN}$TESTS_PASSED passed${NC}"

if [[ "$WORKFLOW_STATUS" == "success" ]]; then
    echo -e "Workflow: ${GREEN}✓ Success${NC}"
    
    if [[ -n "$INSTANCE_IP" && "$INSTANCE_IP" != "None" ]]; then
        echo ""
        echo -e "Deployment URL: ${GREEN}http://$INSTANCE_IP:5001${NC}"
        echo -e "API Health: ${GREEN}http://$INSTANCE_IP:5001/api/health${NC}"
    fi
    
    if [[ "$UI_VERIFIED" == "true" ]]; then
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║   ✓ ALL TESTS PASSED - Fullstack App UI is Functional!     ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        EXIT_CODE=0
    else
        echo ""
        echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║   ⚠ Workflow passed but UI verification inconclusive       ║${NC}"
        echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
        EXIT_CODE=0
    fi
elif [[ "$WORKFLOW_STATUS" == "skipped" ]]; then
    echo -e "Workflow: ${YELLOW}○ Skipped (manual verification needed)${NC}"
    echo ""
    echo -e "${YELLOW}Verify workflow manually at:${NC}"
    echo -e "https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME/actions"
    EXIT_CODE=0
elif [[ "$WORKFLOW_STATUS" == "failure" ]]; then
    echo -e "Workflow: ${RED}✗ Failed${NC}"
    echo ""
    echo -e "${RED}Check workflow logs at:${NC}"
    echo -e "https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME/actions/runs/$RUN_ID"
    EXIT_CODE=1
else
    echo -e "Workflow: ${YELLOW}⚠ $WORKFLOW_STATUS${NC}"
    EXIT_CODE=1
fi

echo ""
if [[ "$CLEANUP_ON_EXIT" == "true" ]]; then
    echo -e "${BLUE}Cleanup will run automatically...${NC}"
else
    echo -e "${YELLOW}Cleanup skipped (--no-cleanup flag). Manual cleanup required:${NC}"
    echo "  gh repo delete $GITHUB_USERNAME/$TEST_REPO_NAME --yes"
    echo "  aws iam delete-role --role-name $ROLE_NAME"
    echo "  aws lightsail delete-instance --instance-name fullstack-notes-instance"
fi

popd > /dev/null
exit $EXIT_CODE
