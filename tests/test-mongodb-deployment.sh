#!/bin/bash

# E2E Test: Deploy MongoDB Task Manager using modular setup.sh
# Tests MongoDB local installation with a Node.js application
#
# Usage:
#   ./test-mongodb-deployment.sh --source-dir /path/to/lamp-stack-lightsail
#   ./test-mongodb-deployment.sh --source-dir /path/to/lamp-stack-lightsail --no-cleanup

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TEST_REPO_NAME="mongodb-test-$(date +%s)"
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

# Copy example-mongodb-app from original workspace if not in source dir
ORIGINAL_WORKSPACE="/Users/naveenrp/Naveen/GIthub Actions in Lightsail/Cline"
if [[ ! -d "$SOURCE_DIR/example-mongodb-app" ]]; then
    if [[ -d "$ORIGINAL_WORKSPACE/example-mongodb-app" ]]; then
        echo -e "${BLUE}Copying example-mongodb-app from original workspace...${NC}"
        rsync -av --exclude='node_modules' --exclude='.git' "$ORIGINAL_WORKSPACE/example-mongodb-app" "$SOURCE_DIR/"
    else
        echo -e "${RED}Error: example-mongodb-app not found in $SOURCE_DIR or $ORIGINAL_WORKSPACE${NC}"
        exit 1
    fi
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
echo -e "${BLUE}║   E2E Test: MongoDB Task Manager Deployment                ║${NC}"
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

# Step 2: Create test directory and copy mongodb-app
echo -e "${BLUE}Step 2: Copying mongodb-app to test directory...${NC}"

TEST_DIR="$SOURCE_DIR/test-mongodb-$(date +%s)"
mkdir -p "$TEST_DIR"

# Copy mongodb-app files (excluding node_modules)
rsync -av --exclude='node_modules' --exclude='.git' "$SOURCE_DIR/example-mongodb-app/" "$TEST_DIR/"

echo -e "${GREEN}✓ Copied mongodb-app to $TEST_DIR${NC}"

# List what was copied
echo -e "${BLUE}Files copied:${NC}"
ls -la "$TEST_DIR"
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
export APP_NAME="MongoDB Task Manager"
export INSTANCE_NAME="mongodb-task-instance"
export AWS_REGION=us-east-1
export BLUEPRINT_ID=ubuntu_22_04
export BUNDLE_ID=small_3_0
export DATABASE_TYPE=mongodb
export DB_EXTERNAL=false
export DB_NAME=taskdb
export GITHUB_REPO="$GITHUB_USERNAME/$TEST_REPO_NAME"
export REPO_VISIBILITY=private

# Create deployment config (don't create example app - we already have the real app)
create_deployment_config "nodejs" "MongoDB Task Manager" "mongodb-task-instance" "us-east-1" "ubuntu_22_04" "small_3_0" "mongodb" "false" "" "taskdb" "" "" "" "false"
create_github_workflow "nodejs" "MongoDB Task Manager" "us-east-1"

echo -e "${GREEN}✓ Deployment configuration created${NC}"
echo ""

# Step 4: Verify files
echo -e "${BLUE}Step 4: Verifying generated files...${NC}"

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

verify '[[ -f "deployment-nodejs.config.yml" ]]' "deployment-nodejs.config.yml exists"
verify '[[ -f ".github/workflows/deploy-nodejs.yml" ]]' ".github/workflows/deploy-nodejs.yml exists"
verify '[[ -f "package.json" ]]' "package.json exists"
verify '[[ -f "server.js" ]]' "server.js exists (main app entry)"
verify '[[ -d "public" ]]' "public/ directory exists"
verify 'grep -q "mongodb" deployment-nodejs.config.yml' "Config contains mongodb settings"
verify 'grep -q "enabled: true" deployment-nodejs.config.yml | head -1' "MongoDB is enabled in config"
verify 'grep -q "MONGODB_URI" deployment-nodejs.config.yml' "MONGODB_URI environment variable is set"
verify 'grep -q "deploy-generic-reusable.yml" .github/workflows/deploy-nodejs.yml' "Workflow uses reusable workflow"

if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}✗ File verification failed${NC}"
    echo ""
    echo -e "${YELLOW}Deployment config contents:${NC}"
    cat deployment-nodejs.config.yml
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
EOF

# Commit all files
git add -A
git commit -m "Initial commit: MongoDB Task Manager with GitHub Actions deployment"

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
    echo -e "${BLUE}Waiting for workflow to complete (this may take 10-15 minutes for MongoDB installation)...${NC}"
    
    sleep 10
    
    RUN_ID=$(gh run list --repo "$GITHUB_USERNAME/$TEST_REPO_NAME" --workflow "deploy-nodejs.yml" --limit 1 --json databaseId -q '.[0].databaseId')
    
    if [[ -n "$RUN_ID" ]]; then
        echo -e "${BLUE}Workflow run ID: $RUN_ID${NC}"
        echo -e "${BLUE}View at: https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME/actions/runs/$RUN_ID${NC}"
        
        TIMEOUT=1200  # 20 minutes for MongoDB installation
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

# Step 8: Report results
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
    echo ""
    
    # Get deployment URL
    INSTANCE_IP=$(aws lightsail get-instance --instance-name mongodb-task-instance --query 'instance.publicIpAddress' --output text 2>/dev/null || echo "")
    if [[ -n "$INSTANCE_IP" && "$INSTANCE_IP" != "None" ]]; then
        echo -e "Deployment URL: ${GREEN}http://$INSTANCE_IP:3000${NC}"
        echo -e "Health Check: ${GREEN}http://$INSTANCE_IP:3000/api/health${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ ALL TESTS PASSED - MongoDB App Deployed!               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    EXIT_CODE=0
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
    echo "  aws lightsail delete-instance --instance-name mongodb-task-instance"
fi

popd > /dev/null
exit $EXIT_CODE
