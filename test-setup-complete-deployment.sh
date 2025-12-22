#!/bin/bash

# End-to-End Integration Test for setup-complete-deployment.sh
# Creates a real GitHub repo, deploys via GitHub Actions, verifies, then cleans up
#
# Usage:
#   ./test-setup-complete-deployment.sh --source-dir /path/to/lamp-stack-lightsail
#   ./test-setup-complete-deployment.sh --source-dir /path/to/lamp-stack-lightsail --skip-wait
#   ./test-setup-complete-deployment.sh --source-dir /path/to/lamp-stack-lightsail --no-cleanup

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TEST_REPO_NAME="test-deployment-$(date +%s)"
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

if [[ ! -f "$SOURCE_DIR/setup-complete-deployment.sh" ]]; then
    echo -e "${RED}Error: setup-complete-deployment.sh not found in $SOURCE_DIR${NC}"
    exit 1
fi

SCRIPT_DIR="$SOURCE_DIR"

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
            # Detach policies first
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
echo -e "${BLUE}║   E2E Test: setup-complete-deployment.sh                   ║${NC}"
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

# Step 2: Create temp directory and run setup script
echo -e "${BLUE}Step 2: Running setup-complete-deployment.sh...${NC}"

TEST_DIR="$SOURCE_DIR/test-project-$(date +%s)"
mkdir -p "$TEST_DIR"
pushd "$TEST_DIR" > /dev/null

# Initialize git repo
git init
git config user.email "test@example.com"
git config user.name "Test User"

# Run the setup script in AUTO_MODE
export AUTO_MODE=true
export APP_TYPE=nodejs
export APP_NAME="Test Node App"
export INSTANCE_NAME="test-node-instance"
export AWS_REGION=us-east-1
export BLUEPRINT_ID=ubuntu_22_04
export BUNDLE_ID=micro_3_0
export DATABASE_TYPE=none
export GITHUB_REPO="$GITHUB_USERNAME/$TEST_REPO_NAME"
export REPO_VISIBILITY=private

# Source the setup script (disable exit on error temporarily)
set +e
source "$SCRIPT_DIR/setup-complete-deployment.sh"
set -e

# Manually call the functions we need (since main() would try interactive mode)
create_deployment_config "nodejs" "Test Node App" "test-node-instance" "us-east-1" "ubuntu_22_04" "micro_3_0" "none" "false" "" "app_db" "" "" "" "false"
create_github_workflow "nodejs" "Test Node App" "us-east-1"
create_example_app "nodejs" "Test Node App"

# Override with a better-looking Node.js app for testing
cat > "app.js" << 'NODEJS_APP_EOF'
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Main dashboard page with modern UI
app.get('/', (req, res) => {
    const uptime = process.uptime();
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    const seconds = Math.floor(uptime % 60);
    
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Node.js Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        .header h1 {
            font-size: 3rem;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .header p {
            color: #8892b0;
            font-size: 1.2rem;
        }
        .status-badge {
            display: inline-block;
            background: linear-gradient(90deg, #00ff88, #00d9ff);
            color: #1a1a2e;
            padding: 8px 20px;
            border-radius: 50px;
            font-weight: 600;
            margin-top: 20px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
            50% { box-shadow: 0 0 0 15px rgba(0, 255, 136, 0); }
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        .card-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        .card h3 {
            color: #00d9ff;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        .card-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #fff;
        }
        .card-label {
            color: #8892b0;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        .endpoints {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 40px;
        }
        .endpoints h2 {
            color: #00d9ff;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        .endpoint-list {
            display: grid;
            gap: 15px;
        }
        .endpoint {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 20px;
            background: rgba(0, 217, 255, 0.1);
            border-radius: 10px;
            transition: background 0.3s;
        }
        .endpoint:hover {
            background: rgba(0, 217, 255, 0.2);
        }
        .endpoint-method {
            background: #00ff88;
            color: #1a1a2e;
            padding: 5px 12px;
            border-radius: 5px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .endpoint a {
            color: #fff;
            text-decoration: none;
            flex: 1;
        }
        .endpoint a:hover {
            color: #00d9ff;
        }
        .footer {
            text-align: center;
            color: #8892b0;
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .tech-stack {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .tech-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #8892b0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Node.js Dashboard</h1>
            <p>Deployed via GitHub Actions to AWS Lightsail</p>
            <div class="status-badge">● System Online</div>
        </div>
        
        <div class="cards">
            <div class="card">
                <div class="card-icon">⚡</div>
                <h3>Node.js Version</h3>
                <div class="card-value">${process.version}</div>
                <div class="card-label">Runtime Engine</div>
            </div>
            <div class="card">
                <div class="card-icon">🕐</div>
                <h3>Uptime</h3>
                <div class="card-value">${hours}h ${minutes}m ${seconds}s</div>
                <div class="card-label">Since Last Restart</div>
            </div>
            <div class="card">
                <div class="card-icon">💾</div>
                <h3>Memory Usage</h3>
                <div class="card-value">${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB</div>
                <div class="card-label">Heap Used</div>
            </div>
            <div class="card">
                <div class="card-icon">🌐</div>
                <h3>Environment</h3>
                <div class="card-value">${process.env.NODE_ENV || 'production'}</div>
                <div class="card-label">Current Mode</div>
            </div>
        </div>
        
        <div class="endpoints">
            <h2>📡 API Endpoints</h2>
            <div class="endpoint-list">
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <a href="/api/health">/api/health</a>
                    <span style="color: #8892b0">Health check endpoint</span>
                </div>
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <a href="/api/info">/api/info</a>
                    <span style="color: #8892b0">System information</span>
                </div>
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <a href="/api/metrics">/api/metrics</a>
                    <span style="color: #8892b0">Performance metrics</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Deployed at ${new Date().toISOString()}</p>
            <div class="tech-stack">
                <div class="tech-item">🟢 Node.js</div>
                <div class="tech-item">⚡ Express</div>
                <div class="tech-item">☁️ AWS Lightsail</div>
                <div class="tech-item">🔄 GitHub Actions</div>
            </div>
        </div>
    </div>
</body>
</html>
    `);
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

app.get('/api/info', (req, res) => {
    res.json({
        status: 'success',
        application: 'Test Node App',
        version: '1.0.0',
        node_version: process.version,
        environment: process.env.NODE_ENV || 'production',
        platform: process.platform,
        arch: process.arch,
        timestamp: new Date().toISOString()
    });
});

app.get('/api/metrics', (req, res) => {
    const mem = process.memoryUsage();
    res.json({
        uptime_seconds: process.uptime(),
        memory: {
            heap_used_mb: Math.round(mem.heapUsed / 1024 / 1024),
            heap_total_mb: Math.round(mem.heapTotal / 1024 / 1024),
            rss_mb: Math.round(mem.rss / 1024 / 1024)
        },
        cpu: process.cpuUsage(),
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
NODEJS_APP_EOF

echo -e "${GREEN}✓ Configuration files created${NC}"

# Step 3: Verify files were created correctly
echo ""
echo -e "${BLUE}Step 3: Verifying generated files...${NC}"

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
verify '[[ -f "package.json" ]]' "package.json exists in root"
verify '[[ -f "app.js" ]]' "app.js exists in root"
verify '[[ ! -d "example-nodejs-app" ]]' "No example-nodejs-app subfolder created"
verify 'grep -q "\./" deployment-nodejs.config.yml' "Config uses root directory (./) for package_files"
verify 'grep -q "deploy-generic-reusable.yml" .github/workflows/deploy-nodejs.yml' "Workflow uses reusable workflow"

if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}✗ File verification failed${NC}"
    echo ""
    echo -e "${YELLOW}Debug info:${NC}"
    echo "Current directory: $(pwd)"
    echo "Files in directory:"
    ls -la
    echo ""
    echo "Config file content (if exists):"
    cat deployment-nodejs.config.yml 2>/dev/null | head -30 || echo "File not found"
    popd > /dev/null
    exit 1
fi
echo ""

# Step 4: Create GitHub repo and push
echo -e "${BLUE}Step 4: Creating GitHub repo and pushing...${NC}"

# Commit all files first
git add -A
git commit -m "Initial commit: Node.js app with GitHub Actions deployment"

gh repo create "$TEST_REPO_NAME" --private --source=. --push

echo -e "${GREEN}✓ Repo created: https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME${NC}"

# Step 5: Set up IAM role for OIDC
echo ""
echo -e "${BLUE}Step 5: Setting up IAM role for GitHub OIDC...${NC}"

ROLE_NAME="github-actions-${TEST_REPO_NAME}"
ROLE_ARN=$(create_iam_role_if_needed "$ROLE_NAME" "$GITHUB_USERNAME/$TEST_REPO_NAME" "$AWS_ACCOUNT_ID")

# Set GitHub repo variable
gh variable set AWS_ROLE_ARN --body "$ROLE_ARN" --repo "$GITHUB_USERNAME/$TEST_REPO_NAME"
echo -e "${GREEN}✓ IAM role created and GitHub variable set${NC}"

# Step 6: Trigger workflow and wait for completion
echo ""
echo -e "${BLUE}Step 6: Triggering GitHub Actions workflow...${NC}"

# Trigger workflow manually
gh workflow run "deploy-nodejs.yml" --repo "$GITHUB_USERNAME/$TEST_REPO_NAME"
sleep 5

if [[ "$SKIP_DEPLOY_WAIT" == "true" ]]; then
    echo -e "${YELLOW}⚠ Skipping workflow wait (--skip-wait flag)${NC}"
    WORKFLOW_STATUS="skipped"
else
    echo -e "${BLUE}Waiting for workflow to complete (this may take a few minutes)...${NC}"
    
    # Wait for workflow to start
    sleep 10
    
    # Get the latest run ID
    RUN_ID=$(gh run list --repo "$GITHUB_USERNAME/$TEST_REPO_NAME" --workflow "deploy-nodejs.yml" --limit 1 --json databaseId -q '.[0].databaseId')
    
    if [[ -n "$RUN_ID" ]]; then
        echo -e "${BLUE}Workflow run ID: $RUN_ID${NC}"
        echo -e "${BLUE}View at: https://github.com/$GITHUB_USERNAME/$TEST_REPO_NAME/actions/runs/$RUN_ID${NC}"
        
        # Wait for completion (max 15 minutes - deployments can take time)
        TIMEOUT=900
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

# Step 7: Report results
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
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ ALL TESTS PASSED                                       ║${NC}"
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
fi

exit $EXIT_CODE
