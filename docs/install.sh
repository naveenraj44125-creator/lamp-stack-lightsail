#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
AUTO_MODE=${AUTO_MODE:-false}
AWS_REGION=${AWS_REGION:-us-east-1}
APP_VERSION=${APP_VERSION:-1.0.0}

# MCP Server integration - stores AI recommendations
MCP_RECOMMENDATIONS=""
RECOMMENDED_APP_TYPE=""
RECOMMENDED_DATABASE=""
RECOMMENDED_BUNDLE=""
RECOMMENDED_BUCKET="false"
ANALYSIS_CONFIDENCE=0

# Fully automated mode environment variables
APP_TYPE=${APP_TYPE:-}
APP_NAME=${APP_NAME:-}
INSTANCE_NAME=${INSTANCE_NAME:-}
BLUEPRINT_ID=${BLUEPRINT_ID:-ubuntu-22-04}
BUNDLE_ID=${BUNDLE_ID:-micro_3_0}
DATABASE_TYPE=${DATABASE_TYPE:-none}
DB_EXTERNAL=${DB_EXTERNAL:-false}
DB_RDS_NAME=${DB_RDS_NAME:-}
DB_NAME=${DB_NAME:-app_db}
ENABLE_BUCKET=${ENABLE_BUCKET:-false}
BUCKET_NAME=${BUCKET_NAME:-}
BUCKET_ACCESS=${BUCKET_ACCESS:-read_write}
BUCKET_BUNDLE=${BUCKET_BUNDLE:-small_1_0}
GITHUB_REPO=${GITHUB_REPO:-}
REPO_VISIBILITY=${REPO_VISIBILITY:-private}

# Verification endpoint customization (for API-only apps)
VERIFICATION_ENDPOINT=${VERIFICATION_ENDPOINT:-}
HEALTH_CHECK_ENDPOINT=${HEALTH_CHECK_ENDPOINT:-}
EXPECTED_CONTENT=${EXPECTED_CONTENT:-}
API_ONLY_APP=${API_ONLY_APP:-false}

# Function to convert string to lowercase (compatible with older bash versions)
to_lowercase() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Function to convert string to uppercase (compatible with older bash versions)
to_uppercase() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Function to show application-specific warnings for common deployment issues
show_app_deployment_warnings() {
    local app_type="$1"
    
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Pre-Deployment Checklist${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Common warnings for all app types
    echo -e "${BLUE}1. Health Check Endpoint:${NC}"
    echo -e "   Your app needs a PUBLIC endpoint (no auth) for health checks."
    echo -e "   The deployment will fail if the health endpoint returns 401/403."
    echo -e "   ${GREEN}Recommended:${NC} Add GET /api/health returning {\"status\": \"ok\"}"
    echo ""
    
    # Node.js specific warnings
    if [[ "$app_type" == "nodejs" ]]; then
        echo -e "${BLUE}2. Frontend Serving (Node.js):${NC}"
        echo -e "   If you have a React/Vue/Angular frontend in /client:"
        echo -e "   - Add 'npm run build' script to build the frontend"
        echo -e "   - Server must serve static files: app.use(express.static('client/build'))"
        echo -e "   - Add catch-all route for SPA: app.get('*', (req,res) => res.sendFile(...))"
        echo ""
        
        echo -e "${BLUE}3. Build Script:${NC}"
        echo -e "   Ensure package.json has a 'build' script if frontend needs building"
        echo -e "   ${GREEN}Example:${NC} \"build\": \"cd client && npm install && npm run build\""
        echo ""
        
        echo -e "${BLUE}4. Start Script:${NC}"
        echo -e "   Root package.json needs a 'start' script for production"
        echo -e "   ${GREEN}Example:${NC} \"start\": \"cd server && npm start\" or \"start\": \"node app.js\""
        echo ""
    fi
    
    # Check for common issues in current directory
    local issues_found=false
    
    # Check for health endpoint in Node.js apps
    if [[ "$app_type" == "nodejs" ]]; then
        # Check multiple possible server file locations (including server/ subdirectory)
        local server_file=""
        if [ -f "server/server.js" ]; then
            server_file="server/server.js"
        elif [ -f "server/index.js" ]; then
            server_file="server/index.js"
        elif [ -f "server.js" ]; then
            server_file="server.js"
        elif [ -f "app.js" ]; then
            server_file="app.js"
        fi
        
        if [ -n "$server_file" ]; then
            if ! grep -q "/api/health\|/health" "$server_file" 2>/dev/null; then
                echo -e "${RED}⚠️  WARNING: No /api/health endpoint found in $server_file${NC}"
                issues_found=true
            fi
            if ! grep -q "express.static" "$server_file" 2>/dev/null; then
                if [ -d "client" ]; then
                    echo -e "${RED}⚠️  WARNING: No express.static() found in $server_file - frontend won't be served${NC}"
                    issues_found=true
                fi
            fi
            # Check for SPA catch-all route
            if [ -d "client" ]; then
                if ! grep -q "sendFile.*index.html\|sendFile.*build" "$server_file" 2>/dev/null; then
                    echo -e "${RED}⚠️  WARNING: No SPA catch-all route found - React routing won't work${NC}"
                    issues_found=true
                fi
            fi
        fi
        
        # Check for build script
        if [ -f "package.json" ] && [ -d "client" ]; then
            if ! grep -q '"build"' package.json 2>/dev/null; then
                echo -e "${RED}⚠️  WARNING: No 'build' script in package.json - frontend won't be built${NC}"
                issues_found=true
            fi
        fi
        
        # Check for start script
        if [ -f "package.json" ]; then
            if ! grep -q '"start"' package.json 2>/dev/null; then
                echo -e "${RED}⚠️  WARNING: No 'start' script in package.json - PM2 won't know how to start the app${NC}"
                issues_found=true
            fi
        fi
    fi
    
    if [[ "$issues_found" == "true" ]]; then
        echo ""
        echo -e "${YELLOW}Please fix the above issues before deployment to avoid failures.${NC}"
        echo -e "${YELLOW}The deployment workflow expects these to be in place.${NC}"
    else
        echo -e "${GREEN}✓ No obvious issues detected in your application code.${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to detect fullstack React + Node.js application
detect_fullstack_react() {
    # Check for various fullstack structures:
    # 1. server.js + client/ (traditional)
    # 2. server/server.js + client/ (organized structure)
    # 3. server/index.js + client/ (organized structure)
    if [ -d "client" ] && [ -f "client/package.json" ]; then
        if [ -f "server.js" ] || [ -f "server/server.js" ] || [ -f "server/index.js" ]; then
            echo "fullstack-react"
            return 0
        fi
    fi
    return 1
}

# Function to auto-detect Node.js port from server.js or server/index.js
detect_node_port() {
    local server_file=""
    
    # Check multiple possible server file locations (including server/ subdirectory)
    if [ -f "server/server.js" ]; then
        server_file="server/server.js"
    elif [ -f "server/index.js" ]; then
        server_file="server/index.js"
    elif [ -f "server.js" ]; then
        server_file="server.js"
    elif [ -f "app.js" ]; then
        server_file="app.js"
    elif [ -f "index.js" ]; then
        server_file="index.js"
    fi
    
    if [ -n "$server_file" ]; then
        # Look for PORT environment variable usage with fallback
        PORT=$(grep -o "process\.env\.PORT.*||.*[0-9]\+" "$server_file" | grep -o "[0-9]\+" | head -1)
        if [ -n "$PORT" ]; then
            echo "$PORT"
        else
            # Look for direct port assignment
            PORT=$(grep -o "PORT.*=.*[0-9]\+" "$server_file" | grep -o "[0-9]\+" | head -1)
            echo "${PORT:-3000}"
        fi
    else
        echo "3000"
    fi
}

# Function to build React client if detected
build_react_client_if_needed() {
    local app_type="$1"

    if [[ "$app_type" == "nodejs" ]] && [ -d "client" ] && [ -f "client/package.json" ]; then
        echo -e "${BLUE}Detected fullstack React + Node.js application${NC}"
        
        # Get detected port for consistency
        local DETECTED_PORT=$(detect_node_port)
        
        # Fix package.json scripts if needed
        if [ -f "package.json" ]; then
            local needs_fix=false
            
            # Check for missing scripts
            if ! grep -q '"build"' package.json 2>/dev/null; then
                needs_fix=true
            fi
            if ! grep -q '"start"' package.json 2>/dev/null; then
                needs_fix=true
            fi
            
            if [[ "$needs_fix" == "true" ]]; then
                echo -e "${YELLOW}⚠️  Root package.json missing required scripts for deployment${NC}"
                
                local FIX_PACKAGE="true"
                if [[ "$FULLY_AUTOMATED" != "true" ]]; then
                    FIX_PACKAGE=$(get_yes_no "Add missing 'build' and 'start' scripts to package.json?" "true")
                fi
                
                if [[ "$FIX_PACKAGE" == "true" ]]; then
                    echo -e "${BLUE}Updating package.json with deployment scripts...${NC}"
                    
                    # Determine the server entry point (check server/ subdirectory first)
                    local server_entry=""
                    if [ -f "server/server.js" ]; then
                        server_entry="cd server && npm install && NODE_ENV=production node server.js"
                    elif [ -f "server/index.js" ]; then
                        server_entry="cd server && npm install && NODE_ENV=production node index.js"
                    elif [ -f "server.js" ]; then
                        server_entry="node server.js"
                    elif [ -f "app.js" ]; then
                        server_entry="node app.js"
                    else
                        server_entry="cd server && npm install && NODE_ENV=production node server.js"
                    fi
                    
                    # Use node to safely update package.json
                    node -e "
                        const fs = require('fs');
                        const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
                        pkg.scripts = pkg.scripts || {};
                        if (!pkg.scripts.build) {
                            pkg.scripts.build = 'cd client && npm install && npm run build';
                        }
                        if (!pkg.scripts.start) {
                            pkg.scripts.start = '$server_entry';
                        }
                        if (!pkg.scripts.test) {
                            pkg.scripts.test = 'echo \"Error: no test specified\" && exit 1';
                        }
                        fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
                        console.log('Updated package.json scripts');
                    " 2>/dev/null || {
                        echo -e "${YELLOW}⚠️  Could not auto-update package.json - please add scripts manually${NC}"
                    }
                    
                    echo -e "${GREEN}✓ Updated package.json with build and start scripts${NC}"
                fi
            fi
            
            # Also check if start script points to non-existent file and fix it
            local current_start=$(grep -o '"start"[[:space:]]*:[[:space:]]*"[^"]*"' package.json 2>/dev/null | head -1)
            if echo "$current_start" | grep -q "node app.js" && [[ ! -f "app.js" ]]; then
                echo -e "${YELLOW}⚠️  Start script points to non-existent app.js, fixing...${NC}"
                
                # Determine correct start command
                local correct_start=""
                if [ -f "server/server.js" ]; then
                    correct_start="cd server && npm install && NODE_ENV=production node server.js"
                elif [ -f "server/index.js" ]; then
                    correct_start="cd server && npm install && NODE_ENV=production node index.js"
                elif [ -f "server.js" ]; then
                    correct_start="node server.js"
                fi
                
                if [ -n "$correct_start" ]; then
                    node -e "
                        const fs = require('fs');
                        const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
                        pkg.scripts = pkg.scripts || {};
                        pkg.scripts.start = '$correct_start';
                        fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
                        console.log('Fixed package.json start script');
                    " 2>/dev/null || {
                        echo -e "${RED}❌ Could not auto-fix package.json${NC}"
                    }
                    echo -e "${GREEN}✓ Fixed package.json start script${NC}"
                fi
            fi
        fi
        
        # Check and fix server file for production static serving
        local server_file=""
        if [ -f "server/server.js" ]; then
            server_file="server/server.js"
        elif [ -f "server/index.js" ]; then
            server_file="server/index.js"
        elif [ -f "server.js" ]; then
            server_file="server.js"
        fi
        
        if [ -n "$server_file" ] && [ -d "client" ]; then
            local needs_static_fix=false
            
            # Check if express.static for client/build is missing
            if ! grep -q "express.static.*client/build\|express.static.*client.*build" "$server_file" 2>/dev/null; then
                if ! grep -q "express.static.*build" "$server_file" 2>/dev/null; then
                    needs_static_fix=true
                fi
            fi
            
            # Check if SPA catch-all is missing
            if ! grep -q "sendFile.*index.html" "$server_file" 2>/dev/null; then
                needs_static_fix=true
            fi
            
            if [[ "$needs_static_fix" == "true" ]]; then
                echo -e "${YELLOW}⚠️  Server file missing production static file serving${NC}"
                echo -e "${YELLOW}   Your server needs to serve the React build in production:${NC}"
                echo ""
                echo -e "${BLUE}   Add this BEFORE your routes:${NC}"
                echo "   if (process.env.NODE_ENV === 'production') {"
                echo "     app.use(express.static(path.join(__dirname, '../client/build')));"
                echo "   }"
                echo ""
                echo -e "${BLUE}   Add this AFTER your API routes:${NC}"
                echo "   if (process.env.NODE_ENV === 'production') {"
                echo "     app.get('*', (req, res) => {"
                echo "       res.sendFile(path.join(__dirname, '../client/build/index.html'));"
                echo "     });"
                echo "   }"
                echo ""
                echo -e "${YELLOW}   Without these, your React frontend won't load in production!${NC}"
                echo ""
            fi
        fi

        # Check if client/build already exists
        if [ -d "client/build" ]; then
            echo -e "${YELLOW}⚠️ client/build directory already exists${NC}"
            if [[ "$FULLY_AUTOMATED" != "true" ]]; then
                BUILD_CLIENT=$(get_yes_no "Rebuild React client?" "true")
            else
                BUILD_CLIENT="true"
            fi
        else
            if [[ "$FULLY_AUTOMATED" != "true" ]]; then
                BUILD_CLIENT=$(get_yes_no "Build React client locally before deployment?" "true")
            else
                BUILD_CLIENT="true"
            fi
        fi

        if [[ "$BUILD_CLIENT" == "true" ]]; then
            echo -e "${BLUE}Building React client...${NC}"
            cd client
            if [ -f "package-lock.json" ]; then
                npm ci
            elif [ -f "yarn.lock" ]; then
                yarn install --frozen-lockfile
            else
                npm install
            fi
            npm run build
            cd ..

            if [ -d "client/build" ]; then
                echo -e "${GREEN}✓ React client built successfully${NC}"
                git add client/build/
                return 0
            else
                echo -e "${RED}❌ Failed to build React client${NC}"
                return 1
            fi
        fi
    fi

    return 0
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    local missing_tools=()
    local install_instructions=()
    
    # Check for required tools
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
        install_instructions+=("  git: brew install git (macOS) or apt install git (Linux)")
    fi
    
    if ! command -v gh &> /dev/null; then
        missing_tools+=("gh (GitHub CLI)")
        install_instructions+=("  gh:  brew install gh (macOS) or see https://cli.github.com/")
    fi
    
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws (AWS CLI)")
        install_instructions+=("  aws: brew install awscli (macOS) or see https://aws.amazon.com/cli/")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
        install_instructions+=("  python3: brew install python3 (macOS) or apt install python3 (Linux)")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing required tools:${NC}"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        echo ""
        echo -e "${YELLOW}Installation instructions:${NC}"
        for instruction in "${install_instructions[@]}"; do
            echo "$instruction"
        done
        echo ""
        exit 1
    fi
    
    # Check for PyYAML (required for deployment workflows)
    if ! python3 -c "import yaml" &> /dev/null; then
        echo -e "${YELLOW}⚠️  PyYAML not installed (required for deployment)${NC}"
        echo -e "${BLUE}Installing PyYAML...${NC}"
        if pip3 install PyYAML &> /dev/null; then
            echo -e "${GREEN}✓ PyYAML installed successfully${NC}"
        else
            echo -e "${RED}❌ Failed to install PyYAML${NC}"
            echo "Please run manually: pip3 install PyYAML"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ PyYAML is installed${NC}"
    fi
    
    # Check GitHub CLI authentication
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI not authenticated${NC}"
        echo ""
        echo -e "${YELLOW}Please authenticate with GitHub CLI:${NC}"
        echo "  1. Run: gh auth login"
        echo "  2. Select: GitHub.com"
        echo "  3. Select: HTTPS"
        echo "  4. Authenticate with your browser"
        echo ""
        exit 1
    fi
    
    # Get and validate GitHub username (required for OIDC setup)
    GITHUB_USERNAME=$(gh api user -q .login 2>/dev/null)
    if [[ -z "$GITHUB_USERNAME" ]]; then
        echo -e "${YELLOW}⚠️  Could not auto-detect GitHub username${NC}"
        echo -e "${BLUE}Please enter your GitHub username:${NC}"
        read -r GITHUB_USERNAME
        if [[ -z "$GITHUB_USERNAME" ]]; then
            echo -e "${RED}❌ GitHub username is required for OIDC setup${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}✓ GitHub user: $GITHUB_USERNAME${NC}"
    export GITHUB_USERNAME
    
    # Check AWS CLI configuration
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not configured${NC}"
        echo ""
        echo -e "${YELLOW}Please configure AWS CLI:${NC}"
        echo "  Run: aws configure"
        echo "  Enter your AWS Access Key ID, Secret Access Key, and region"
        echo ""
        exit 1
    fi
    
    echo -e "${GREEN}✓ All prerequisites met${NC}"
}

# Function to analyze project using MCP server's project analyzer
# This provides intelligent recommendations for deployment configuration
analyze_project_for_recommendations() {
    local project_path="${1:-.}"
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  🔍 Analyzing Your Project...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Check if Node.js is available for running the analyzer
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}⚠ Node.js not found - skipping AI recommendations${NC}"
        return 1
    fi
    
    # Check if the MCP server project analyzer exists
    local analyzer_script=""
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Look for the analyzer in common locations
    if [ -f "${script_dir}/mcp-server-new/project-analyzer.js" ]; then
        analyzer_script="${script_dir}/mcp-server-new/project-analyzer.js"
    elif [ -f "./mcp-server-new/project-analyzer.js" ]; then
        analyzer_script="./mcp-server-new/project-analyzer.js"
    elif [ -f "../mcp-server-new/project-analyzer.js" ]; then
        analyzer_script="../mcp-server-new/project-analyzer.js"
    fi
    
    # Show thinking indicator
    echo -ne "${YELLOW}⏳ Scanning project files"
    
    # Run inline analysis using Node.js
    local analysis_result=$(node -e "
const fs = require('fs');
const path = require('path');

// Simplified project analyzer (inline version)
const patterns = {
    frameworks: {
        'express': { files: ['package.json'], content: ['\"express\"'], type: 'nodejs' },
        'fastify': { files: ['package.json'], content: ['\"fastify\"'], type: 'nodejs' },
        'koa': { files: ['package.json'], content: ['\"koa\"'], type: 'nodejs' },
        'flask': { files: ['requirements.txt', 'app.py'], content: ['Flask', 'from flask'], type: 'python' },
        'django': { files: ['requirements.txt', 'manage.py'], content: ['Django', 'django'], type: 'python' },
        'laravel': { files: ['composer.json'], content: ['laravel/framework'], type: 'lamp' },
        'symfony': { files: ['composer.json'], content: ['symfony/'], type: 'lamp' },
        'react': { files: ['package.json'], content: ['\"react\"'], type: 'react' },
        'vue': { files: ['package.json'], content: ['\"vue\"'], type: 'react' },
        'angular': { files: ['package.json'], content: ['\"@angular/'], type: 'react' },
        'next': { files: ['package.json'], content: ['\"next\"'], type: 'react' },
        'nuxt': { files: ['package.json'], content: ['\"nuxt\"'], type: 'react' }
    },
    databases: {
        'mysql': { files: ['package.json', 'requirements.txt', 'composer.json'], content: ['mysql', 'mysql2', 'PyMySQL', 'mysqlclient'], type: 'mysql' },
        'postgresql': { files: ['package.json', 'requirements.txt', 'composer.json'], content: ['pg', 'postgres', 'psycopg2', 'postgresql'], type: 'postgresql' },
        'mongodb': { files: ['package.json', 'requirements.txt'], content: ['mongodb', 'mongoose', 'pymongo'], type: 'mongodb' }
    },
    storage: {
        'file_uploads': { content: ['multer', 'upload', 'FileField', 'move_uploaded_file', 'FormData'] },
        'image_processing': { content: ['sharp', 'jimp', 'Pillow', 'PIL', 'imagemagick'] }
    }
};

const analysis = {
    detected_type: 'unknown',
    confidence: 0,
    frameworks: [],
    databases: [],
    storage_needs: { needs_bucket: false },
    infrastructure_needs: { bundle_size: 'micro_3_0' }
};

// Scan important files
const filesToCheck = ['package.json', 'requirements.txt', 'composer.json', 'Dockerfile', 'docker-compose.yml', 'app.py', 'manage.py'];
const projectPath = '${project_path}';

for (const filename of filesToCheck) {
    const filepath = path.join(projectPath, filename);
    if (fs.existsSync(filepath)) {
        try {
            const content = fs.readFileSync(filepath, 'utf8');
            
            // Framework detection
            for (const [framework, pattern] of Object.entries(patterns.frameworks)) {
                if (pattern.files.includes(filename)) {
                    if (pattern.content.some(c => content.includes(c))) {
                        analysis.frameworks.push({ name: framework, type: pattern.type, confidence: 0.8 });
                    }
                }
            }
            
            // Database detection
            for (const [db, pattern] of Object.entries(patterns.databases)) {
                if (pattern.files.includes(filename)) {
                    if (pattern.content.some(c => content.toLowerCase().includes(c.toLowerCase()))) {
                        analysis.databases.push({ name: db, type: pattern.type, confidence: 0.7 });
                    }
                }
            }
            
            // Storage detection
            for (const [feature, pattern] of Object.entries(patterns.storage)) {
                if (pattern.content.some(c => content.toLowerCase().includes(c.toLowerCase()))) {
                    analysis.storage_needs.needs_bucket = true;
                }
            }
        } catch (e) {}
    }
}

// Check for Docker
if (fs.existsSync(path.join(projectPath, 'Dockerfile')) || fs.existsSync(path.join(projectPath, 'docker-compose.yml'))) {
    analysis.frameworks.push({ name: 'docker', type: 'docker', confidence: 0.9 });
}

// Check for fullstack (client + server)
if (fs.existsSync(path.join(projectPath, 'client')) && fs.existsSync(path.join(projectPath, 'client/package.json'))) {
    analysis.is_fullstack = true;
}

// Determine application type
const typeScores = {};
for (const framework of analysis.frameworks) {
    const type = framework.type;
    if (!typeScores[type]) typeScores[type] = 0;
    typeScores[type] += framework.confidence;
}

// Backend takes priority for fullstack apps
const backendTypes = ['nodejs', 'python', 'lamp', 'docker'];
const frontendTypes = ['react'];
const hasBackend = backendTypes.some(t => typeScores[t] > 0);
const hasFrontend = frontendTypes.some(t => typeScores[t] > 0);

if (hasBackend && hasFrontend) {
    for (const backendType of backendTypes) {
        if (typeScores[backendType]) typeScores[backendType] += 0.5;
    }
}

let maxScore = 0;
let detectedType = 'unknown';
for (const [type, score] of Object.entries(typeScores)) {
    if (score > maxScore) {
        maxScore = score;
        detectedType = type;
    }
}

analysis.detected_type = detectedType;
analysis.confidence = Math.min(maxScore, 1.0);

// Determine bundle size
if (detectedType === 'docker') {
    analysis.infrastructure_needs.bundle_size = 'medium_3_0';
} else if (analysis.databases.length > 1 || analysis.storage_needs.needs_bucket) {
    analysis.infrastructure_needs.bundle_size = 'small_3_0';
}

// Output as JSON
console.log(JSON.stringify(analysis));
" 2>/dev/null)
    
    if [ -z "$analysis_result" ] || [ "$analysis_result" == "null" ]; then
        echo -e "${YELLOW}⚠ Could not analyze project - using defaults${NC}"
        return 1
    fi
    
    # Parse the analysis result
    MCP_RECOMMENDATIONS="$analysis_result"
    
    # Extract recommendations using node
    RECOMMENDED_APP_TYPE=$(echo "$analysis_result" | node -e "
        const data = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
        console.log(data.detected_type || 'unknown');
    " 2>/dev/null)
    
    RECOMMENDED_DATABASE=$(echo "$analysis_result" | node -e "
        const data = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
        const db = data.databases && data.databases[0];
        console.log(db ? db.type : 'none');
    " 2>/dev/null)
    
    RECOMMENDED_BUNDLE=$(echo "$analysis_result" | node -e "
        const data = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
        console.log(data.infrastructure_needs?.bundle_size || 'micro_3_0');
    " 2>/dev/null)
    
    RECOMMENDED_BUCKET=$(echo "$analysis_result" | node -e "
        const data = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
        console.log(data.storage_needs?.needs_bucket ? 'true' : 'false');
    " 2>/dev/null)
    
    ANALYSIS_CONFIDENCE=$(echo "$analysis_result" | node -e "
        const data = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
        console.log(Math.round((data.confidence || 0) * 100));
    " 2>/dev/null)
    
    # Clear the thinking indicator
    echo -e "\r${GREEN}✓ Scanning complete!${NC}                    "
    
    # Display analysis results
    if [ "$RECOMMENDED_APP_TYPE" != "unknown" ] && [ -n "$RECOMMENDED_APP_TYPE" ]; then
        echo ""
        echo -e "${GREEN}✓ Project Analysis Complete!${NC}"
        echo ""
        echo -e "${BLUE}┌─────────────────────────────────────────────────────────────┐${NC}"
        echo -e "${BLUE}│${NC} ${YELLOW}🤖 AI Recommendations (${ANALYSIS_CONFIDENCE}% confidence)${NC}"
        echo -e "${BLUE}├─────────────────────────────────────────────────────────────┤${NC}"
        
        # Show detected frameworks
        local frameworks=$(echo "$analysis_result" | node -e "
            const data = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
            const names = (data.frameworks || []).map(f => f.name).join(', ');
            console.log(names || 'None detected');
        " 2>/dev/null)
        printf "${BLUE}│${NC}   Detected Frameworks: ${GREEN}%-35s${NC} ${BLUE}│${NC}\n" "$frameworks"
        printf "${BLUE}│${NC}   Recommended App Type: ${GREEN}%-34s${NC} ${BLUE}│${NC}\n" "$RECOMMENDED_APP_TYPE"
        printf "${BLUE}│${NC}   Recommended Database: ${GREEN}%-34s${NC} ${BLUE}│${NC}\n" "$RECOMMENDED_DATABASE"
        printf "${BLUE}│${NC}   Recommended Instance: ${GREEN}%-34s${NC} ${BLUE}│${NC}\n" "$RECOMMENDED_BUNDLE"
        
        if [ "$RECOMMENDED_BUCKET" == "true" ]; then
            printf "${BLUE}│${NC}   Storage Bucket: ${GREEN}%-40s${NC} ${BLUE}│${NC}\n" "Recommended (file uploads detected)"
        fi
        
        echo -e "${BLUE}└─────────────────────────────────────────────────────────────┘${NC}"
        echo ""
        echo -e "${YELLOW}★ Recommended options will be highlighted in the menus below${NC}"
        echo ""
        return 0
    else
        echo -e "${YELLOW}⚠ Could not determine project type - please select manually${NC}"
        return 1
    fi
}

# Function to check if we're in a git repository (checks for .git in current directory, not parent)
check_git_repo() {
    # Check if .git exists in current directory (not inherited from parent)
    if [ -d ".git" ]; then
        return 0
    fi
    return 1
}

# Function to create GitHub repository if needed
create_github_repo_if_needed() {
    local repo_name="$1"
    local repo_desc="$2"
    local visibility="$3"
    
    echo -e "${BLUE}Creating GitHub repository: $repo_name${NC}"
    
    if gh repo create "$repo_name" --description "$repo_desc" $visibility --confirm; then
        echo -e "${GREEN}✓ Repository created successfully${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Repository might already exist${NC}"
        return 0
    fi
}

# Function to create IAM role for GitHub OIDC
create_iam_role_if_needed() {
    local role_name="$1"
    local github_repo="$2"
    local aws_account_id="$3"
    
    echo -e "${BLUE}Creating IAM role: $role_name${NC}" >&2
    
    # Create trust policy
    cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::${aws_account_id}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": [
                        "repo:${github_repo}:ref:refs/heads/main",
                        "repo:${github_repo}:ref:refs/heads/master",
                        "repo:${github_repo}:pull_request"
                    ]
                }
            }
        }
    ]
}
EOF

    # Create role (disable pager and redirect output to stderr so only the final ARN goes to stdout)
    if AWS_PAGER="" aws iam create-role --role-name "$role_name" --assume-role-policy-document file://trust-policy.json --no-cli-pager >&2 2>&1; then
        echo -e "${GREEN}✓ IAM role created${NC}" >&2
    else
        echo -e "${YELLOW}⚠️  IAM role already exists, updating trust policy...${NC}" >&2
        # Update the trust policy for existing role
        local update_result
        update_result=$(AWS_PAGER="" aws iam update-assume-role-policy --role-name "$role_name" --policy-document file://trust-policy.json --no-cli-pager 2>&1)
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Trust policy updated${NC}" >&2
            # Wait for IAM propagation
            echo -e "${BLUE}Waiting for IAM policy propagation...${NC}" >&2
            sleep 10
        else
            echo -e "${RED}❌ Failed to update trust policy: $update_result${NC}" >&2
            echo -e "${YELLOW}💡 You may need to manually delete the role and re-run: aws iam delete-role --role-name $role_name${NC}" >&2
        fi
    fi
    
    # Attach policies
    echo -e "${BLUE}Attaching IAM policies...${NC}" >&2
    AWS_PAGER="" aws iam attach-role-policy --role-name "$role_name" --policy-arn "arn:aws:iam::aws:policy/ReadOnlyAccess" --no-cli-pager &> /dev/null
    
    # Create custom Lightsail policy
    local lightsail_policy_name="${role_name}-LightsailAccess"
    local policy_arn="arn:aws:iam::${aws_account_id}:policy/${lightsail_policy_name}"
    
    if ! AWS_PAGER="" aws iam get-policy --policy-arn "$policy_arn" --no-cli-pager &> /dev/null; then
        local lightsail_policy='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"lightsail:*","Resource":"*"}]}'
        AWS_PAGER="" aws iam create-policy \
            --policy-name "$lightsail_policy_name" \
            --policy-document "$lightsail_policy" \
            --description "Full access to AWS Lightsail for GitHub Actions deployment" \
            --no-cli-pager &> /dev/null
        echo -e "${GREEN}✓ Custom Lightsail policy created${NC}" >&2
    else
        echo -e "${YELLOW}⚠️  Custom Lightsail policy already exists${NC}" >&2
    fi
    
    AWS_PAGER="" aws iam attach-role-policy --role-name "$role_name" --policy-arn "$policy_arn" --no-cli-pager &> /dev/null
    echo -e "${GREEN}✓ IAM policies attached${NC}" >&2
    
    # Set AWS_ROLE_ARN and echo it for capture by caller
    local role_arn="arn:aws:iam::${aws_account_id}:role/${role_name}"
    echo "$role_arn"
    
    # Clean up
    rm -f trust-policy.json
    
    return 0
}

# Function to setup workflow files
# NOTE: We no longer copy workflow files to new repos. Instead, the app-specific
# workflow calls the reusable workflow from the source repo directly. This ensures
# new repos always use the latest workflow code without needing manual updates.
setup_workflow_files() {
    echo -e "${BLUE}Setting up workflow directory...${NC}"
    
    mkdir -p .github/workflows
    
    echo -e "${GREEN}✓ Workflow directory created${NC}"
    echo -e "${BLUE}ℹ️  Using cross-repo workflow from naveenraj44125-creator/lamp-stack-lightsail${NC}"
    echo -e "${BLUE}ℹ️  No local workflow files needed - always uses latest from source repo${NC}"
    return 0
}

# Function to create deployment configuration based on existing examples
create_deployment_config() {
    local app_type="$1"
    local app_name="$2"
    local instance_name="$3"
    local aws_region="$4"
    local blueprint_id="$5"
    local bundle_id="$6"
    local db_type="$7"
    local db_external="$8"
    local db_rds_name="$9"
    local db_name="${10}"
    local bucket_name="${11}"
    local bucket_access="${12}"
    local bucket_bundle="${13}"
    local enable_bucket="${14}"
    
    echo -e "${BLUE}Creating deployment configuration for $app_type...${NC}"
    
    # Base configuration that matches our existing examples
    cat > "deployment-${app_type}.config.yml" << EOF
# ${app_name} Deployment Configuration

aws:
  region: ${aws_region}

lightsail:
  instance_name: ${instance_name}
  static_ip: ""
  
  # Instance size configuration (optional)
  # If not specified, defaults are: small_3_0 (2GB) for traditional apps, medium_3_0 (4GB) for Docker apps
  bundle_id: "${bundle_id}"
  
  # Operating system blueprint configuration (optional)
  # If not specified, defaults to ubuntu_22_04
  blueprint_id: "${blueprint_id}"

EOF

    # Add bucket configuration if enabled
    if [[ "$enable_bucket" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
  # Lightsail bucket configuration
  bucket:
    enabled: true
    name: "${bucket_name}"
    access_level: "${bucket_access}"
    bundle_id: "${bucket_bundle}"

EOF
    fi

    # Application configuration based on type
    cat >> "deployment-${app_type}.config.yml" << EOF
application:
  name: $(echo "${app_name}" | tr '[:upper:]' '[:lower:]')
  version: "1.0.0"
  type: ${app_type}
  
  package_files:
    - "./"
  
  package_fallback: true
  
  environment_variables:
    APP_ENV: production
EOF

    # Add database environment variables (available for all application types)
    if [[ "$db_type" != "none" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    # Database Configuration
    DB_TYPE: ${db_type}
    DB_HOST: $([ "$db_external" = "true" ] && echo "RDS_ENDPOINT" || echo "localhost")
    DB_NAME: ${db_name:-app_db}
    DB_USER: app_user
    DB_PASSWORD: CHANGE_ME_secure_password_123
EOF
        if [[ "$db_external" == "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
    DB_RDS_NAME: ${db_rds_name:-${app_type}-${db_type}-db}
EOF
        fi
        # MongoDB-specific connection string (no auth - MongoDB installed without authentication)
        if [[ "$db_type" == "mongodb" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
    # MongoDB specific (no authentication - local MongoDB)
    MONGODB_URI: mongodb://localhost:27017/${db_name:-app_db}
    MONGODB_PORT: "27017"
EOF
        fi
    fi

    # Add type-specific environment variables
    case $app_type in
        "lamp")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # LAMP Stack specific
    APACHE_DOCUMENT_ROOT: /var/www/html
EOF
            ;;
        "nodejs")
            # Detect actual port from server.js if it exists
            DETECTED_PORT=$(detect_node_port)
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Node.js specific
    NODE_ENV: production
    PORT: "${DETECTED_PORT}"
EOF
            ;;
        "python")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Python/Flask specific
    FLASK_ENV: production
    FLASK_APP: app.py
    PORT: "5000"
EOF
            ;;
        "react")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # React specific
    REACT_APP_ENV: production
    BUILD_PATH: build
EOF
            ;;
        "docker")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Docker specific
    COMPOSE_PROJECT_NAME: $(to_lowercase "${app_name}")
    DOCKER_BUILDKIT: "1"
EOF
            ;;
        "nginx")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Nginx specific
    NGINX_DOCUMENT_ROOT: /var/www/html
EOF
            ;;
    esac

    # Add bucket environment variables if enabled
    if [[ "$enable_bucket" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    BUCKET_NAME: ${bucket_name}
    AWS_REGION: ${aws_region}
EOF
    fi

    # Dependencies configuration based on app type
    cat >> "deployment-${app_type}.config.yml" << EOF

dependencies:
EOF

    # Database configuration (available for all application types)
    cat >> "deployment-${app_type}.config.yml" << EOF
  # Database Dependencies
  mysql:
    enabled: $([ "$db_type" = "mysql" ] && [ "$db_external" = "false" ] && echo "true" || echo "false")
    external: $([ "$db_external" = "true" ] && echo "true" || echo "false")
    config:
      version: "8.0"
      root_password: "CHANGE_ME_root_password_123"
      create_database: "${db_name:-app_db}"
      create_user: "app_user"
      user_password: "CHANGE_ME_secure_password_123"
EOF

    if [[ "$db_external" == "true" && "$db_type" == "mysql" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    rds:
      database_name: "${db_rds_name:-${app_type}-mysql-db}"
      region: "${aws_region}"
      master_database: "${db_name:-app_db}"
      environment:
        DB_CONNECTION_TIMEOUT: "30"
        DB_CHARSET: "utf8mb4"
EOF
    fi

    cat >> "deployment-${app_type}.config.yml" << EOF
  
  postgresql:
    enabled: $([ "$db_type" = "postgresql" ] && [ "$db_external" = "false" ] && echo "true" || echo "false")
    external: $([ "$db_external" = "true" ] && echo "true" || echo "false")
    config:
      version: "13"
      postgres_password: "CHANGE_ME_postgres_password_123"
      create_database: "${db_name:-app_db}"
      create_user: "app_user"
      user_password: "CHANGE_ME_secure_password_123"
EOF

    if [[ "$db_external" == "true" && "$db_type" == "postgresql" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    rds:
      database_name: "${db_rds_name:-${app_type}-postgres-db}"
      region: "${aws_region}"
      master_database: "${db_name:-app_db}"
      environment:
        DB_CONNECTION_TIMEOUT: "30"
EOF
    fi

    # MongoDB configuration (local only - no RDS support)
    cat >> "deployment-${app_type}.config.yml" << EOF
  
  mongodb:
    enabled: $([ "$db_type" = "mongodb" ] && echo "true" || echo "false")
    external: false
    config:
      version: "7.0"
      database: "${db_name:-app_db}"
      auth_enabled: true
      admin_user: "admin"
      admin_password: "CHANGE_ME_admin_password_123"
      app_user: "app_user"
      app_password: "CHANGE_ME_app_password_123"
      bind_ip: "127.0.0.1"
      port: 27017
EOF

    case $app_type in
        "lamp")
            cat >> "deployment-${app_type}.config.yml" << EOF
  
  php:
    enabled: true
    config:
      version: "8.1"
      extensions:
        - curl
        - json
        - mbstring
        - mysql
        - xml
        - zip
      
  apache:
    enabled: true
    config:
      enable_rewrite: true
      document_root: "/var/www/html"
EOF
            ;;
        "nodejs")
            cat >> "deployment-${app_type}.config.yml" << EOF
  
  nodejs:
    enabled: true
    config:
      version: "18"
      package_manager: "npm"
      
  pm2:
    enabled: true
    config:
      app_name: "$(to_lowercase "${app_name}")"
      instances: 1
      exec_mode: "cluster"
EOF
            ;;
        "python")
            cat >> "deployment-${app_type}.config.yml" << EOF
  
  python:
    enabled: true
    config:
      version: "3.9"
      pip_packages:
        - flask
        - gunicorn
        
  gunicorn:
    enabled: true
    config:
      app_module: "app:app"
      workers: 2
      bind: "0.0.0.0:5000"
EOF
            ;;
        "nginx")
            cat >> "deployment-${app_type}.config.yml" << EOF
  nginx:
    enabled: true
    config:
      document_root: "/var/www/html"
      enable_gzip: true
      client_max_body_size: "10M"
EOF
            ;;
        "docker")
            cat >> "deployment-${app_type}.config.yml" << EOF
  docker:
    enabled: true
    config:
      install_compose: true
EOF
            ;;
    esac

    # Common dependencies
    cat >> "deployment-${app_type}.config.yml" << EOF
  
  git:
    enabled: true
    config:
      install_lfs: false
  
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"    # SSH
        - "80"    # HTTP
        - "443"   # HTTPS
EOF

    # Add type-specific ports
    case $app_type in
        "nodejs")
            # Use detected port for firewall configuration
            DETECTED_PORT=$(detect_node_port)
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "${DETECTED_PORT}"  # Node.js
EOF
            ;;
        "python")
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "5000"  # Flask
EOF
            ;;
        "lamp")
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "8080"  # phpMyAdmin
EOF
            ;;
    esac

    cat >> "deployment-${app_type}.config.yml" << EOF
      deny_all_other: true

deployment:
EOF

    # Add Docker-specific deployment config
    if [[ "$app_type" == "docker" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
  use_docker: true
  docker_app_path: "/opt/$(to_lowercase "${app_name}")-app"
  docker_compose_file: "docker-compose.yml"
EOF
    fi

    # Common deployment configuration
    cat >> "deployment-${app_type}.config.yml" << EOF
  
  timeouts:
    ssh_connection: 120
    command_execution: 600
    health_check: 180
  
  retries:
    max_attempts: 3
    ssh_connection: 5
  
  steps:
    pre_deployment:
      common:
        enabled: true
        update_packages: true
        create_directories: true
        backup_enabled: true
      dependencies:
        enabled: true
        install_system_deps: true
        configure_services: true
    
    post_deployment:
      common:
        enabled: true
        verify_extraction: true
        create_env_file: true
        cleanup_temp_files: true
      dependencies:
        enabled: true
        configure_application: true
        set_permissions: true
        restart_services: true
    
    verification:
      enabled: true
      health_check: true
      external_connectivity: true
      endpoints_to_test:
EOF

    # Use custom endpoint if provided, otherwise use defaults
    if [[ -n "$VERIFICATION_ENDPOINT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
        - "${VERIFICATION_ENDPOINT}"
EOF
    elif [[ "$API_ONLY_APP" == "true" ]]; then
        # API-only apps don't have a root route
        cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/posts"
EOF
    else
        cat >> "deployment-${app_type}.config.yml" << EOF
        - "/"
EOF
    fi

    # Add type-specific endpoints and port configuration
    case $app_type in
        "nodejs")
            # Only add /api/health if not using custom endpoint and not API-only
            if [[ -z "$VERIFICATION_ENDPOINT" && "$API_ONLY_APP" != "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/health"
EOF
            fi
            # Use detected port for verification
            DETECTED_PORT=$(detect_node_port)
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: ${DETECTED_PORT}  # Node.js applications run on port ${DETECTED_PORT}
EOF
            ;;
        "python")
            if [[ -z "$VERIFICATION_ENDPOINT" && "$API_ONLY_APP" != "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/health"
EOF
            fi
            # Python/Flask apps typically run on port 5000
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 5000  # Flask applications run on port 5000
EOF
            ;;
        "lamp")
            if [[ -z "$VERIFICATION_ENDPOINT" && "$API_ONLY_APP" != "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/test.php"
EOF
            fi
            # LAMP apps run on port 80 (Apache)
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # Apache serves on port 80
EOF
            ;;
        "nginx")
            # Nginx apps run on port 80
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # Nginx serves on port 80
EOF
            ;;
        "react")
            # React apps are served via nginx on port 80
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # React build served via nginx on port 80
EOF
            ;;
        "docker")
            # Docker apps typically expose port 80
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # Docker container exposes port 80
EOF
            ;;
    esac

    # GitHub Actions configuration
    cat >> "deployment-${app_type}.config.yml" << EOF

github_actions:
  triggers:
    push_branches:
      - main
      - master
    pull_request_branches:
      - main
      - master
    workflow_dispatch: true
  
  jobs:
    test:
      enabled: true
EOF

    # Add type-specific test configuration
    case $app_type in
        "docker")
            cat >> "deployment-${app_type}.config.yml" << EOF
      docker_test: true
EOF
            ;;
        *)
            cat >> "deployment-${app_type}.config.yml" << EOF
      language_specific_tests: true
EOF
            ;;
    esac

    cat >> "deployment-${app_type}.config.yml" << EOF
    
    deployment:
      deploy_on_push: true
      deploy_on_pr: false
      artifact_retention_days: 1
      create_summary: true

monitoring:
  health_check:
EOF

    # Use custom health check endpoint if provided
    if [[ -n "$HEALTH_CHECK_ENDPOINT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "${HEALTH_CHECK_ENDPOINT}"
EOF
    elif [[ -n "$VERIFICATION_ENDPOINT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "${VERIFICATION_ENDPOINT}"
EOF
    elif [[ "$API_ONLY_APP" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "/api/posts"
EOF
    else
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "/"
EOF
    fi

    # Add type-specific expected content
    if [[ -n "$EXPECTED_CONTENT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "${EXPECTED_CONTENT}"
EOF
    elif [[ "$API_ONLY_APP" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "["
EOF
    else
        case $app_type in
            "lamp")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "LAMP Stack"
EOF
                ;;
            "nodejs")
                # For fullstack React + Node.js apps, look for React-specific content
                if [ -d "client" ] && [ -f "client/package.json" ]; then
                    cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "root"
EOF
                else
                    cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "Node.js"
EOF
                fi
                ;;
            "python")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "Flask"
EOF
                ;;
            "react")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "root"
EOF
                ;;
            "docker")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "Docker"
EOF
                ;;
            *)
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "${app_name}"
EOF
                ;;
        esac
    fi

    # Add nodejs port if applicable
    if [[ "$app_type" == "nodejs" ]]; then
        DETECTED_PORT=$(detect_node_port)
        cat >> "deployment-${app_type}.config.yml" << EOF
    port: ${DETECTED_PORT}  # Node.js applications run on port ${DETECTED_PORT}
EOF
    fi

    cat >> "deployment-${app_type}.config.yml" << EOF
    max_attempts: 15
    wait_between_attempts: 20
    initial_wait: 60

security:
  file_permissions:
    web_files: "644"
    directories: "755"
    config_files: "600"

backup:
  enabled: true
  retention_days: 7
  backup_location: "/var/backups/$(to_lowercase "${app_name}")-deployments"
EOF

    # Add Docker-specific monitoring
    if [[ "$app_type" == "docker" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
  
  docker_health:
    check_containers: true
    required_containers:
      - "$(to_lowercase "${app_name}")-web"
EOF
    fi

    echo -e "${GREEN}✓ Created deployment-${app_type}.config.yml${NC}"
    
    # Show deployment warnings and checks
    show_app_deployment_warnings "$app_type"
}

# Function to create GitHub Actions workflow that matches existing examples
create_github_workflow() {
    local app_type="$1"
    local app_name="$2"
    local aws_region="$3"
    
    echo -e "${BLUE}Creating GitHub Actions workflow...${NC}"
    
    mkdir -p .github/workflows
    
    # Create workflow that calls the reusable workflow from the source repo
    # This ensures new repos always use the latest workflow code
    
    # Determine file patterns based on app type
    local file_patterns=""
    case $app_type in
        "lamp")
            file_patterns="      - '**/*.php'
      - '**/*.html'
      - '**/*.css'
      - '**/*.js'"
            ;;
        "nodejs")
            file_patterns="      - '**/*.js'
      - '**/*.json'
      - '**/*.html'
      - '**/*.css'"
            ;;
        "python")
            file_patterns="      - '**/*.py'
      - 'requirements.txt'
      - '**/*.html'
      - '**/*.css'"
            ;;
        "react")
            file_patterns="      - 'src/**'
      - 'public/**'
      - 'package.json'"
            ;;
        "docker")
            file_patterns="      - 'Dockerfile*'
      - 'docker-compose*.yml'
      - '**/*.php'
      - '**/*.js'"
            ;;
        "nginx")
            file_patterns="      - '**/*.html'
      - '**/*.css'
      - '**/*.js'"
            ;;
    esac
    
    cat > ".github/workflows/deploy-${app_type}.yml" << EOF
name: ${app_name} Deployment

on:
  push:
    branches: [ main, master ]
    paths:
${file_patterns}
      - 'deployment-${app_type}.config.yml'
      - '.github/workflows/deploy-${app_type}.yml'
  pull_request:
    branches: [ main, master ]
    paths:
${file_patterns}
      - 'deployment-${app_type}.config.yml'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: false
        default: 'production'
        type: choice
        options:
          - production
          - staging

permissions:
  id-token: write   # Required for OIDC authentication
  contents: read    # Required to checkout code

jobs:
  deploy:
    name: Deploy ${app_name}
    # Use reusable workflow from source repo - always gets latest fixes
    uses: naveenraj44125-creator/lamp-stack-lightsail/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-${app_type}.config.yml'
      aws_region: '${aws_region}'
    secrets: inherit
  
  summary:
    name: Deployment Summary
    needs: deploy
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Show Deployment Results
        run: |
          echo "## 🚀 ${app_name} Deployment" >> \$GITHUB_STEP_SUMMARY
          echo "" >> \$GITHUB_STEP_SUMMARY
          echo "- **URL**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
          echo "- **Status**: \${{ needs.deploy.outputs.deployment_status }}" >> \$GITHUB_STEP_SUMMARY
          echo "" >> \$GITHUB_STEP_SUMMARY
          
          if [ "\${{ needs.deploy.outputs.deployment_status }}" = "success" ]; then
            echo "✅ Application deployed successfully!" >> \$GITHUB_STEP_SUMMARY
            echo "" >> \$GITHUB_STEP_SUMMARY
EOF

    # Add type-specific summary information
    case $app_type in
        "lamp")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🔧 LAMP Stack" >> \$GITHUB_STEP_SUMMARY
            echo "- **Linux**: Ubuntu 22.04" >> \$GITHUB_STEP_SUMMARY
            echo "- **Apache**: Web Server" >> \$GITHUB_STEP_SUMMARY
            echo "- **MySQL**: Database" >> \$GITHUB_STEP_SUMMARY
            echo "- **PHP**: Application Runtime" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "nodejs")
            # Check if this is a fullstack React + Node.js app
            if [ -d "client" ] && [ -f "client/package.json" ]; then
                # Fullstack React + Node.js app
                cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### ⚛️ Fullstack React + Node.js" >> \$GITHUB_STEP_SUMMARY
            echo "- **Web App**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **API Health**: \${{ needs.deploy.outputs.deployment_url }}api/health" >> \$GITHUB_STEP_SUMMARY
            echo "- **Frontend**: React (production build)" >> \$GITHUB_STEP_SUMMARY
            echo "- **Backend**: Node.js + Express" >> \$GITHUB_STEP_SUMMARY
EOF
            else
                # Regular Node.js API
                cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 📡 Endpoints" >> \$GITHUB_STEP_SUMMARY
            echo "- **Home**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **Health**: \${{ needs.deploy.outputs.deployment_url }}api/health" >> \$GITHUB_STEP_SUMMARY
            echo "- **Info**: \${{ needs.deploy.outputs.deployment_url }}api/info" >> \$GITHUB_STEP_SUMMARY
EOF
            fi
            ;;
        "python")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🐍 Flask API" >> \$GITHUB_STEP_SUMMARY
            echo "- **Home**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **Health**: \${{ needs.deploy.outputs.deployment_url }}api/health" >> \$GITHUB_STEP_SUMMARY
            echo "- **API**: \${{ needs.deploy.outputs.deployment_url }}api/" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "react")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### ⚛️ React Dashboard" >> \$GITHUB_STEP_SUMMARY
            echo "- **Dashboard**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **Build**: Production optimized" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "docker")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🐳 Docker Application" >> \$GITHUB_STEP_SUMMARY
            echo "- **Containers**: Multi-container setup" >> \$GITHUB_STEP_SUMMARY
            echo "- **Compose**: Docker Compose orchestration" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "nginx")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🌐 Static Site" >> \$GITHUB_STEP_SUMMARY
            echo "- **Server**: Nginx" >> \$GITHUB_STEP_SUMMARY
            echo "- **Content**: Static files" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
    esac

    cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
          else
            echo "❌ Deployment failed. Check logs above." >> \$GITHUB_STEP_SUMMARY
          fi
EOF

    echo -e "${GREEN}✓ Created .github/workflows/deploy-${app_type}.yml${NC}"
}

# Function to create example application that matches existing examples
create_example_app() {
    local app_type="$1"
    local app_name="$2"
    
    echo -e "${BLUE}Creating example ${app_type} application in root directory...${NC}"
    echo -e "${YELLOW}Note: Existing files will NOT be overwritten${NC}"
    
    # Helper function to create file only if it doesn't exist
    create_file_if_not_exists() {
        local filepath="$1"
        if [[ -f "$filepath" ]]; then
            echo -e "${YELLOW}  ⚠ Skipping $filepath (already exists)${NC}"
            return 1
        fi
        return 0
    }
    
    case $app_type in
        "lamp")
            # Create PHP application similar to existing examples
            if create_file_if_not_exists "index.php"; then
            cat > "index.php" << 'PHP_EOF'
<?php
header('Content-Type: text/html; charset=UTF-8');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LAMP Stack Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 LAMP Stack Application</h1>
            <p>Successfully deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>PHP Version:</strong> <?php echo phpversion(); ?></p>
            <p><strong>Server:</strong> <?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?></p>
            <p><strong>Timestamp:</strong> <?php echo date('Y-m-d H:i:s T'); ?></p>
        </div>
        
        <div class="info">
            <h3>Database Connection</h3>
            <?php
            try {
                $host = $_ENV['DB_HOST'] ?? 'localhost';
                $dbname = $_ENV['DB_NAME'] ?? 'app_db';
                $username = $_ENV['DB_USER'] ?? 'app_user';
                $password = $_ENV['DB_PASSWORD'] ?? '';
                
                if ($password) {
                    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
                    echo "<p>✅ Database connection successful</p>";
                } else {
                    echo "<p>⚠️ Database credentials not configured</p>";
                }
            } catch (PDOException $e) {
                echo "<p>⚠️ Database connection failed: " . $e->getMessage() . "</p>";
            }
            ?>
        </div>
    </div>
</body>
</html>
PHP_EOF
            fi

            # Create API test endpoint
            mkdir -p "api"
            if create_file_if_not_exists "api/test.php"; then
            cat > "api/test.php" << 'PHP_EOF'
<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

echo json_encode([
    'status' => 'success',
    'message' => 'LAMP Stack API is working',
    'php_version' => phpversion(),
    'timestamp' => date('c'),
    'server' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'
]);
?>
PHP_EOF
            fi
            ;;
        
        "nodejs")
            # Create Node.js application similar to existing examples
            local app_name_lower=$(to_lowercase "${app_name}")
            
            # Detect existing Node.js entry point (including server/ subdirectory)
            local existing_entry_point=""
            local server_in_subdir=false
            
            if [[ -f "server/server.js" ]]; then
                existing_entry_point="server/server.js"
                server_in_subdir=true
            elif [[ -f "server/index.js" ]]; then
                existing_entry_point="server/index.js"
                server_in_subdir=true
            elif [[ -f "server.js" ]]; then
                existing_entry_point="server.js"
            elif [[ -f "index.js" ]]; then
                existing_entry_point="index.js"
            elif [[ -f "app.js" ]]; then
                existing_entry_point="app.js"
            fi
            
            if [[ -n "$existing_entry_point" ]]; then
                echo -e "${GREEN}  ✓ Detected existing Node.js app with entry point: $existing_entry_point${NC}"
                echo -e "${YELLOW}  ⚠ Skipping template file creation - using existing application${NC}"
                
                # Determine the correct start command based on entry point location
                local start_command=""
                if [[ "$server_in_subdir" == "true" ]]; then
                    # For server in subdirectory, need to handle npm install in server dir too
                    start_command="cd server && npm install && NODE_ENV=production node $(basename $existing_entry_point)"
                else
                    start_command="node ${existing_entry_point}"
                fi
                
                # Only create package.json if it doesn't exist
                if create_file_if_not_exists "package.json"; then
                cat > "package.json" << EOF
{
  "name": "${app_name_lower}",
  "version": "1.0.0",
  "description": "${app_name} Node.js application deployed via GitHub Actions",
  "main": "${existing_entry_point}",
  "scripts": {
    "start": "${start_command}",
    "dev": "nodemon ${existing_entry_point}",
    "test": "echo \\"No tests specified\\" && exit 0"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF
                fi
                
                # Check if existing package.json has incorrect start script
                if [[ -f "package.json" ]] && [[ "$server_in_subdir" == "true" ]]; then
                    local current_start=$(grep -o '"start"[[:space:]]*:[[:space:]]*"[^"]*"' package.json 2>/dev/null | head -1)
                    if echo "$current_start" | grep -q "node app.js\|node index.js" && [[ ! -f "app.js" ]] && [[ ! -f "index.js" ]]; then
                        echo -e "${YELLOW}  ⚠ Fixing package.json start script for server/ structure${NC}"
                        
                        # Use node to safely update package.json
                        node -e "
                            const fs = require('fs');
                            const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
                            pkg.scripts = pkg.scripts || {};
                            pkg.scripts.start = '${start_command}';
                            pkg.main = '${existing_entry_point}';
                            fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
                            console.log('Fixed package.json start script');
                        " 2>/dev/null || {
                            echo -e "${RED}  ❌ Could not auto-fix package.json - please update start script manually${NC}"
                        }
                        echo -e "${GREEN}  ✓ Updated package.json start script${NC}"
                    fi
                fi
            else
                # No existing entry point found - create template files
                if create_file_if_not_exists "package.json"; then
                cat > "package.json" << EOF
{
  "name": "${app_name_lower}",
  "version": "1.0.0",
  "description": "${app_name} Node.js application deployed via GitHub Actions",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "echo \\"No tests specified\\" && exit 0"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF
                fi
            
                if create_file_if_not_exists "app.js"; then
                cat > "app.js" << EOF
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {
    res.send(\`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${app_name}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #333; margin-bottom: 30px; }
                .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 ${app_name}</h1>
                    <p>Node.js Application deployed via GitHub Actions</p>
                </div>
                
                <div class="success">
                    ✅ Application is running successfully!
                </div>
                
                <div class="info">
                    <h3>System Information</h3>
                    <p><strong>Node.js Version:</strong> \${process.version}</p>
                    <p><strong>Environment:</strong> \${process.env.NODE_ENV || 'development'}</p>
                    <p><strong>Timestamp:</strong> \${new Date().toISOString()}</p>
                </div>
                
                <div class="info">
                    <h3>API Endpoints</h3>
                    <p><a href="/api/health">Health Check</a></p>
                    <p><a href="/api/info">System Info</a></p>
                </div>
            </div>
        </body>
        </html>
    \`);
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
        message: '${app_name} Node.js Application',
        version: '1.0.0',
        node_version: process.version,
        environment: process.env.NODE_ENV || 'development',
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(\`🚀 ${app_name} server running on port \${PORT}\`);
    console.log(\`📍 Environment: \${process.env.NODE_ENV || 'development'}\`);
});
EOF
                fi
            fi
            ;;
        
        "python")
            # Create Python Flask application similar to existing examples
            if create_file_if_not_exists "requirements.txt"; then
            cat > "requirements.txt" << 'REQ_EOF'
Flask==3.0.0
gunicorn==21.2.0
flask-cors==4.0.0
REQ_EOF
            fi
            
            if create_file_if_not_exists "app.py"; then
            cat > "app.py" << EOF
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${app_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ${app_name}</h1>
            <p>Python Flask Application deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Python Version:</strong> {{ python_version }}</p>
            <p><strong>Flask Version:</strong> {{ flask_version }}</p>
            <p><strong>Environment:</strong> {{ environment }}</p>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
        </div>
        
        <div class="info">
            <h3>API Endpoints</h3>
            <p><a href="/api/health">Health Check</a></p>
            <p><a href="/api/info">System Info</a></p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    import sys
    import flask
    return render_template_string(HTML_TEMPLATE,
        python_version=sys.version.split()[0],
        flask_version=flask.__version__,
        environment=os.environ.get('FLASK_ENV', 'development'),
        timestamp=datetime.now().isoformat()
    )

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/info')
def info():
    import sys
    return jsonify({
        'status': 'success',
        'message': '${app_name} Python Flask Application',
        'version': '1.0.0',
        'python_version': sys.version.split()[0],
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
EOF
            fi
            ;;
        
        "react")
            # Create React application similar to existing examples
            local app_name_lower=$(to_lowercase "${app_name}")
            if create_file_if_not_exists "package.json"; then
            cat > "package.json" << EOF
{
  "name": "${app_name_lower}",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test --passWithNoTests",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF
            fi
            
            mkdir -p "public"
            mkdir -p "src"
            
            if create_file_if_not_exists "public/index.html"; then
            cat > "public/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="${app_name} React Application" />
    <title>${app_name}</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>
EOF
            fi
            
            if create_file_if_not_exists "src/index.js"; then
            cat > "src/index.js" << 'JS_EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
JS_EOF
            fi
            
            if create_file_if_not_exists "src/App.js"; then
            cat > "src/App.js" << EOF
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 ${app_name}</h1>
        <p>React Application deployed via GitHub Actions</p>
        
        <div className="success-message">
          ✅ Application is running successfully!
        </div>
        
        <div className="info-section">
          <h3>System Information</h3>
          <p><strong>React Version:</strong> {React.version}</p>
          <p><strong>Environment:</strong> {process.env.NODE_ENV}</p>
          <p><strong>Build Time:</strong> {process.env.REACT_APP_BUILD_TIME || 'Not set'}</p>
          <p><strong>Current Time:</strong> {currentTime.toLocaleString()}</p>
        </div>
        
        <div className="info-section">
          <h3>Features</h3>
          <ul>
            <li>Single Page Application (SPA)</li>
            <li>Production Build Optimization</li>
            <li>Static File Serving</li>
            <li>Responsive Design</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
EOF
            fi

            if create_file_if_not_exists "src/App.css"; then
            cat > "src/App.css" << 'CSS_EOF'
.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 40px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 15px;
  border-radius: 5px;
  margin: 20px 0;
  font-size: 16px;
}

.info-section {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 10px;
  margin: 20px 0;
  max-width: 600px;
}

.info-section h3 {
  margin-top: 0;
  color: #61dafb;
}

.info-section p, .info-section li {
  font-size: 14px;
  text-align: left;
}

.info-section ul {
  text-align: left;
}
CSS_EOF
            fi

            if create_file_if_not_exists "src/index.css"; then
            cat > "src/index.css" << 'CSS_EOF'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
CSS_EOF
            fi
            ;;
        
        "nginx")
            # Create static site similar to existing examples
            if create_file_if_not_exists "index.html"; then
            cat > "index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${app_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .feature-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ${app_name}</h1>
            <p>Nginx Static Site deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Server:</strong> Nginx</p>
            <p><strong>Content Type:</strong> Static HTML/CSS/JS</p>
            <p><strong>Timestamp:</strong> <span id="timestamp"></span></p>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card">
                <h4>🌐 Static Content</h4>
                <p>Fast, efficient static file serving with Nginx</p>
            </div>
            <div class="feature-card">
                <h4>📱 Responsive Design</h4>
                <p>Mobile-friendly responsive layout</p>
            </div>
            <div class="feature-card">
                <h4>⚡ High Performance</h4>
                <p>Optimized for speed and reliability</p>
            </div>
            <div class="feature-card">
                <h4>🔒 Secure</h4>
                <p>HTTPS ready with security headers</p>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
        
        // Update timestamp every second
        setInterval(() => {
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }, 1000);
    </script>
</body>
</html>
EOF
            fi
            ;;
        
        "docker")
            # Create Docker application similar to existing examples
            if create_file_if_not_exists "docker-compose.yml"; then
            cat > "docker-compose.yml" << EOF
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:80"
    environment:
      - APP_NAME=${app_name}
      - APP_ENV=production
    volumes:
      - ./html:/usr/share/nginx/html:ro
    restart: unless-stopped
    
  app:
    build:
      context: .
      dockerfile: Dockerfile.app
    environment:
      - APP_NAME=${app_name}
      - NODE_ENV=production
    restart: unless-stopped
    depends_on:
      - web

networks:
  default:
    name: $(to_lowercase "${app_name}")_network
EOF
            fi
            
            if create_file_if_not_exists "Dockerfile"; then
            cat > "Dockerfile" << 'DOCKER_EOF'
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static files
COPY html/ /usr/share/nginx/html/

# Create directory for logs
RUN mkdir -p /var/log/nginx

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
DOCKER_EOF
            fi

            if create_file_if_not_exists "Dockerfile.app"; then
            cat > "Dockerfile.app" << 'DOCKER_EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY app/ ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose port
EXPOSE 3000

# Start application
CMD ["node", "index.js"]
DOCKER_EOF
            fi

            mkdir -p "html"
            if create_file_if_not_exists "html/index.html"; then
            cat > "html/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${app_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .docker-info { background: #0db7ed; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ${app_name}</h1>
            <p>Docker Application deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="docker-info">
            <h3>🐳 Docker Configuration</h3>
            <p><strong>Container:</strong> Multi-container setup with Docker Compose</p>
            <p><strong>Web Server:</strong> Nginx (Alpine Linux)</p>
            <p><strong>Application:</strong> Node.js backend service</p>
            <p><strong>Network:</strong> Custom Docker network</p>
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Deployment:</strong> Docker Compose</p>
            <p><strong>Environment:</strong> Production</p>
            <p><strong>Timestamp:</strong> <span id="timestamp"></span></p>
        </div>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
        setInterval(() => {
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }, 1000);
    </script>
</body>
</html>
EOF
            fi

            if create_file_if_not_exists "nginx.conf"; then
            cat > "nginx.conf" << 'NGINX_EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    server {
        listen       80;
        server_name  localhost;
        
        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }
}
NGINX_EOF
            fi

            mkdir -p "app"
            local app_name_lower=$(to_lowercase "${app_name}")
            if create_file_if_not_exists "package.json"; then
            cat > "package.json" << EOF
{
  "name": "${app_name_lower}-backend",
  "version": "1.0.0",
  "description": "${app_name} Docker backend service",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF
            fi

            if create_file_if_not_exists "app/index.js"; then
            cat > "app/index.js" << EOF
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: '${app_name} Backend',
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(\`🚀 ${app_name} backend service running on port \${PORT}\`);
});
EOF
            fi
            ;;
    esac
    
    echo -e "${GREEN}✓ Created ${app_type} application files in root directory${NC}"
}

# Function to get user input with default value (enhanced styling)
get_input() {
    local prompt="$1"
    local default="$2"
    local value
    
    if [[ "$AUTO_MODE" == "true" ]]; then
        echo "$default"
        return
    fi
    
    echo "" >&2
    echo -ne "${YELLOW}➤ $prompt${NC}" >&2
    if [[ -n "$default" ]]; then
        echo -ne " [${GREEN}$default${NC}]" >&2
    fi
    echo -n ": " >&2
    read -r value
    
    # Use default if no value entered
    if [[ -z "$value" ]]; then
        value="$default"
        if [[ -n "$value" ]]; then
            echo -e "${GREEN}✓ Using default: $value${NC}" >&2
        fi
    else
        echo -e "${GREEN}✓ Set: $value${NC}" >&2
    fi
    
    echo "$value"
}

# Function to get yes/no input (enhanced styling)
get_yes_no() {
    local prompt="$1"
    local default="$2"
    local value
    local default_display
    
    if [[ "$AUTO_MODE" == "true" ]]; then
        echo "$default"
        return
    fi
    
    # Format default display
    if [[ "$default" == "true" ]]; then
        default_display="${GREEN}Y${NC}/n"
    else
        default_display="y/${GREEN}N${NC}"
    fi
    
    while true; do
        echo -ne "${YELLOW}$prompt${NC} ($default_display): " >&2
        read -r value
        value="${value:-$default}"
        case $value in
            [Yy]* | true ) 
                echo -e "${GREEN}✓ Yes${NC}" >&2
                echo "true"
                break
                ;;
            [Nn]* | false ) 
                echo -e "${BLUE}✓ No${NC}" >&2
                echo "false"
                break
                ;;
            * ) 
                echo -e "${RED}Please answer yes (y) or no (n).${NC}" >&2
                ;;
        esac
    done
}

# Function to select from options with enhanced dropdown-style menu
# Now includes AI recommendation highlighting
select_option() {
    local prompt="$1"
    local default="$2"
    local recommendation_type="${3:-}"  # Optional: app_type, database, bundle, bucket
    shift 3 2>/dev/null || shift 2
    local options=("$@")
    
    if [[ "$AUTO_MODE" == "true" ]]; then
        # Return the actual option value at the default index (1-based)
        # Convert default index to 0-based and return the option
        local default_index=$((default - 1))
        if [ "$default_index" -ge 0 ] && [ "$default_index" -lt "${#options[@]}" ]; then
            echo "${options[$default_index]}"
        else
            echo "${options[0]}"
        fi
        return
    fi
    
    # Determine the AI-recommended option based on type
    local ai_recommended=""
    case "$recommendation_type" in
        "app_type")
            ai_recommended="$RECOMMENDED_APP_TYPE"
            ;;
        "database")
            ai_recommended="$RECOMMENDED_DATABASE"
            ;;
        "bundle")
            ai_recommended="$RECOMMENDED_BUNDLE"
            ;;
    esac
    
    # Use /dev/tty for direct terminal interaction
    exec 3</dev/tty
    
    # Display enhanced menu to terminal
    echo "" > /dev/tty
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────┐${NC}" > /dev/tty
    echo -e "${BLUE}│${NC} ${YELLOW}$prompt${NC}" > /dev/tty
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────┤${NC}" > /dev/tty
    
    for i in "${!options[@]}"; do
        local option="${options[i]}"
        local marker="  "
        local color=""
        local ai_marker=""
        
        # Check if this is the AI-recommended option
        if [ -n "$ai_recommended" ] && [ "$option" == "$ai_recommended" ]; then
            ai_marker=" ${YELLOW}★ AI${NC}"
            # Update default to AI recommendation
            default=$((i+1))
        fi
        
        # Mark default option (which may now be the AI recommendation)
        if [ "$((i+1))" -eq "$default" ]; then
            marker="→ "
            color="${GREEN}"
        fi
        
        # Get description for known options
        local desc=""
        desc=$(get_option_description "$option")
        
        if [ -n "$desc" ]; then
            if [ -n "$ai_marker" ]; then
                printf "${BLUE}│${NC} %s${color}%2d. %-12s${NC} │ %-27s${ai_marker} ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" "$desc" > /dev/tty
            else
                printf "${BLUE}│${NC} %s${color}%2d. %-12s${NC} │ %-35s ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" "$desc" > /dev/tty
            fi
        else
            if [ -n "$ai_marker" ]; then
                printf "${BLUE}│${NC} %s${color}%2d. %-44s${NC}${ai_marker} ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" > /dev/tty
            else
                printf "${BLUE}│${NC} %s${color}%2d. %-52s${NC} ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" > /dev/tty
            fi
        fi
    done
    
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────┘${NC}" > /dev/tty
    echo "" > /dev/tty
    
    while true; do
        echo -ne "${YELLOW}Select option [1-${#options[@]}]${NC} (default: ${GREEN}$default${NC}): " > /dev/tty
        read -u 3 choice
        choice="${choice:-$default}"
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
            local selected="${options[$((choice-1))]}"
            echo -e "${GREEN}✓ Selected: $selected${NC}" > /dev/tty
            echo "$selected"
            break
        else
            echo -e "${RED}Invalid choice. Please select 1-${#options[@]}.${NC}" > /dev/tty
        fi
    done
    
    exec 3<&-
}

# Function to get description for known options
get_option_description() {
    local option="$1"
    
    case "$option" in
        # Application types
        "lamp")
            echo "Linux, Apache, MySQL, PHP stack"
            ;;
        "nodejs")
            echo "Node.js with Express.js"
            ;;
        "python")
            echo "Python with Flask framework"
            ;;
        "react")
            echo "React single-page application"
            ;;
        "docker")
            echo "Multi-container Docker app"
            ;;
        "nginx")
            echo "Static site with Nginx server"
            ;;
        
        # Database types
        "mysql")
            echo "MySQL relational database"
            ;;
        "postgresql")
            echo "PostgreSQL advanced database"
            ;;
        "mongodb")
            echo "MongoDB NoSQL database (local)"
            ;;
        "none")
            echo "No database required"
            ;;
        
        # Instance bundles
        "nano_3_0")
            echo "512MB RAM, 0.25 vCPU - \$3.50/mo"
            ;;
        "micro_3_0")
            echo "1GB RAM, 0.5 vCPU - \$5/mo"
            ;;
        "small_3_0")
            echo "2GB RAM, 1 vCPU - \$10/mo"
            ;;
        "medium_3_0")
            echo "4GB RAM, 2 vCPU - \$20/mo"
            ;;
        "large_3_0")
            echo "8GB RAM, 2 vCPU - \$40/mo"
            ;;
        
        # OS blueprints
        "ubuntu-22-04")
            echo "Ubuntu 22.04 LTS (Recommended)"
            ;;
        "ubuntu-20-04")
            echo "Ubuntu 20.04 LTS"
            ;;
        "amazon-linux-2023")
            echo "Amazon Linux 2023"
            ;;
        
        # Bucket access levels
        "read_only")
            echo "Read-only access to bucket"
            ;;
        "read_write")
            echo "Full read/write access"
            ;;
        
        # Bucket bundles
        "small_1_0")
            echo "5GB storage - \$1/mo"
            ;;
        "medium_1_0")
            echo "100GB storage - \$3/mo"
            ;;
        "large_1_0")
            echo "250GB storage - \$5/mo"
            ;;
        
        *)
            echo ""
            ;;
    esac
}

# Function to setup GitHub OIDC if needed
setup_github_oidc() {
    local github_repo="$1"
    local aws_account_id="$2"
    
    echo -e "${BLUE}Setting up GitHub OIDC...${NC}"
    
    # Check if OIDC provider exists
    if ! aws iam get-open-id-connect-provider --open-id-connect-provider-arn "arn:aws:iam::${aws_account_id}:oidc-provider/token.actions.githubusercontent.com" &> /dev/null; then
        echo -e "${BLUE}Creating GitHub OIDC provider...${NC}"
        
        # Get GitHub's OIDC thumbprint
        THUMBPRINT="6938fd4d98bab03faadb97b34396831e3780aea1"
        
        aws iam create-open-id-connect-provider \
            --url "https://token.actions.githubusercontent.com" \
            --client-id-list "sts.amazonaws.com" \
            --thumbprint-list "$THUMBPRINT" &> /dev/null
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ GitHub OIDC provider created${NC}"
        else
            echo -e "${YELLOW}⚠️  OIDC provider might already exist${NC}"
        fi
    else
        echo -e "${GREEN}✓ GitHub OIDC provider already exists${NC}"
    fi
}

# Function to create .gitignore file
create_gitignore() {
    echo -e "${BLUE}Creating .gitignore file...${NC}"
    
    cat > ".gitignore" << 'GITIGNORE_EOF'
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
node_modules/
jspm_packages/

# TypeScript v1 declaration files
typings/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variable files
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next
out

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/

# vuepress build output
.vuepress/dist

# Serverless directories
.serverless/

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/

# TernJS port file
.tern-port

# Stores VSCode versions used for testing VSCode extensions
.vscode-test

# yarn v2
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz
.pnp.*

# AWS credentials and sensitive files
.aws-creds.sh
*.pem
*.key
trust-policy.json

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
tmp/
temp/
GITIGNORE_EOF

    # Remove node_modules from git tracking if it was previously added
    # This prevents Code Defender from scanning AWS SDK example files
    if [ -d "node_modules" ]; then
        git rm -r --cached node_modules/ 2>/dev/null || true
    fi

    echo -e "${GREEN}✓ Created .gitignore${NC}"
}

# Function to commit and push changes
commit_and_push() {
    local app_type="$1"
    local app_name="$2"
    
    echo -e "${BLUE}Committing and pushing changes...${NC}"
    
    # Add all files
    git add .
    
    # Commit changes
    git commit -m "Add ${app_name} deployment configuration

- Added deployment-${app_type}.config.yml
- Added .github/workflows/deploy-${app_type}.yml  
- Added ${app_type} application files in root directory
- Configured for AWS Lightsail deployment via GitHub Actions

Generated by setup-complete-deployment.sh"
    
    # Push to GitHub
    if git push origin main; then
        echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"
        return 0
    elif git push origin master; then
        echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to push changes${NC}"
        return 1
    fi
}

# Function to validate generated configuration
validate_configuration() {
    local app_type="$1"
    local config_file="deployment-${app_type}.config.yml"
    local workflow_file=".github/workflows/deploy-${app_type}.yml"
    
    echo -e "${BLUE}Validating generated configuration...${NC}"
    
    # Check if files exist
    if [[ ! -f "$config_file" ]]; then
        echo -e "${RED}❌ Configuration file not found: $config_file${NC}"
        return 1
    fi
    
    if [[ ! -f "$workflow_file" ]]; then
        echo -e "${RED}❌ Workflow file not found: $workflow_file${NC}"
        return 1
    fi
    
    # Validate YAML syntax
    if command -v python3 &> /dev/null; then
        python3 -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Configuration YAML is valid${NC}"
        else
            echo -e "${RED}❌ Configuration YAML is invalid${NC}"
            return 1
        fi
        
        python3 -c "import yaml; yaml.safe_load(open('$workflow_file'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Workflow YAML is valid${NC}"
        else
            echo -e "${RED}❌ Workflow YAML is invalid${NC}"
            return 1
        fi
    fi
    
    # Check for required sections in config
    local required_sections=("aws" "lightsail" "application" "dependencies" "deployment" "github_actions" "monitoring")
    for section in "${required_sections[@]}"; do
        if grep -q "^${section}:" "$config_file"; then
            echo -e "${GREEN}✓ Found required section: $section${NC}"
        else
            echo -e "${YELLOW}⚠️  Missing section: $section${NC}"
        fi
    done
    
    # Check workflow uses reusable workflow (either local or cross-repo)
    if grep -q "uses:.*deploy-generic-reusable.yml" "$workflow_file"; then
        echo -e "${GREEN}✓ Workflow uses reusable deployment${NC}"
    else
        echo -e "${RED}❌ Workflow doesn't use reusable deployment${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Configuration validation passed${NC}"
    return 0
}

# Function to display final instructions
show_final_instructions() {
    local app_type="$1"
    local app_name="$2"
    local instance_name="$3"
    local github_repo="$4"
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                                                               ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}   ${GREEN}🎉 Setup Complete!${NC}                                          ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                               ${GREEN}║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Your ${YELLOW}${app_name}${BLUE} deployment is ready!${NC}"
    echo ""
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC} ${YELLOW}� Files Created:${NC}                                              ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   • deployment-${app_type}.config.yml                              ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   • .github/workflows/deploy-${app_type}.yml                       ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   • ${app_type} application files                                  ${BLUE}│${NC}"
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────────┤${NC}"
    echo -e "${BLUE}│${NC} ${YELLOW}🚀 Next Steps:${NC}                                                 ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   1. Review deployment-${app_type}.config.yml                      ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   2. Update default passwords in the config                    ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   3. Push changes: ${GREEN}git push origin main${NC}                       ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   4. Monitor: ${GREEN}https://github.com/${github_repo}/actions${NC}        ${BLUE}│${NC}"
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────────┤${NC}"
    echo -e "${BLUE}│${NC} ${YELLOW}🌐 After Deployment:${NC}                                           ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   Your app: ${GREEN}http://${instance_name}.lightsail.aws.com/${NC}         ${BLUE}│${NC}"
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Important Reminders:${NC}"
    echo "   • Change default passwords before deploying to production"
    echo "   • Ensure AWS_ROLE_ARN is set in GitHub repository secrets"
    echo "   • Review security settings and firewall configuration"
    echo ""
}

# Main execution function
main() {
    # Clear screen for fresh start (only in interactive mode)
    if [[ "$AUTO_MODE" != "true" ]]; then
        clear 2>/dev/null || true
    fi
    
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                                                               ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}   ${GREEN}🚀 AWS Lightsail Complete Deployment Setup${NC}                 ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                               ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}   ${YELLOW}Automated deployment via GitHub Actions${NC}                    ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}                                                               ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if we're in fully automated mode (all required env vars set) - check early!
    FULLY_AUTOMATED=false
    if [[ -n "$APP_TYPE" && -n "$APP_NAME" && -n "$INSTANCE_NAME" ]]; then
        FULLY_AUTOMATED=true
        echo -e "${GREEN}✓ Running in fully automated mode${NC}"
        echo -e "${BLUE}Configuration from environment variables:${NC}"
        echo "  App Type: $APP_TYPE"
        echo "  App Name: $APP_NAME"
        echo "  Instance: $INSTANCE_NAME"
        echo "  Region: $AWS_REGION"
        echo "  GitHub Repo: $GITHUB_REPO"
        echo ""
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Check if we're in a git repository, auto-initialize if not
    if ! check_git_repo; then
        echo -e "${YELLOW}⚠ Not in a git repository. Initializing git...${NC}"
        git init
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to initialize git repository${NC}"
            exit 1
        fi
        # Create initial .gitignore
        cat > .gitignore << 'GITIGNORE'
node_modules/
.env
.env.*
*.log
.DS_Store
__pycache__/
*.pyc
.venv/
venv/

# AWS credentials and sensitive files
.aws-creds*
*.pem
*.key
trust-policy.json
GITIGNORE
        git add .
        git commit -m "Initial commit"
        echo -e "${GREEN}✓ Git repository initialized${NC}"
    fi
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        echo -e "${RED}❌ Failed to get AWS account ID${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ AWS Account ID: $AWS_ACCOUNT_ID${NC}"
    
    # Get GitHub repository info
    if [[ "$FULLY_AUTOMATED" == "true" && -n "$GITHUB_REPO" ]]; then
        echo -e "${GREEN}✓ Using GITHUB_REPO: $GITHUB_REPO${NC}"
        
        # WORKAROUND: Fix GITHUB_REPO if it's missing username (for MCP server v1.1.0 compatibility)
        if [[ "$GITHUB_REPO" != *"/"* ]]; then
            echo -e "${YELLOW}⚠️  GITHUB_REPO missing username, applying workaround...${NC}"
            
            # Use GITHUB_USERNAME from prerequisites check (already validated)
            if [[ -n "$GITHUB_USERNAME" ]]; then
                GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
                echo -e "${GREEN}✓ Fixed GITHUB_REPO using validated username: $GITHUB_REPO${NC}"
            else
                # Try to get username from git remote first
                GIT_REMOTE_REPO=$(git remote get-url origin 2>/dev/null | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/' | sed 's/\.git$//')
                
                if [[ -n "$GIT_REMOTE_REPO" && "$GIT_REMOTE_REPO" == *"/"* ]]; then
                    # Extract username from git remote
                    GITHUB_USERNAME=$(echo "$GIT_REMOTE_REPO" | cut -d'/' -f1)
                    GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
                    echo -e "${GREEN}✓ Fixed GITHUB_REPO using git remote: $GITHUB_REPO${NC}"
                else
                    # Get GitHub username from gh CLI as fallback
                    GITHUB_USERNAME=$(gh api user --jq '.login' 2>/dev/null)
                    if [[ -n "$GITHUB_USERNAME" ]]; then
                        GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
                        echo -e "${GREEN}✓ Fixed GITHUB_REPO using gh CLI: $GITHUB_REPO${NC}"
                    else
                        # Last resort: prompt user for username
                        echo -e "${YELLOW}Could not auto-detect GitHub username${NC}"
                        echo -e "${BLUE}Please enter your GitHub username:${NC}"
                        read -r GITHUB_USERNAME
                        if [[ -n "$GITHUB_USERNAME" ]]; then
                            GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
                            echo -e "${GREEN}✓ Fixed GITHUB_REPO: $GITHUB_REPO${NC}"
                        else
                            echo -e "${RED}❌ GitHub username is required for OIDC setup${NC}"
                            exit 1
                        fi
                    fi
                fi
            fi
        fi
        
        # Create repo if it doesn't exist and set up git remote
        echo -e "${BLUE}Checking if GitHub repository exists...${NC}"
        if ! gh repo view "$GITHUB_REPO" &>/dev/null; then
            echo -e "${YELLOW}Repository doesn't exist, creating...${NC}"
            REPO_VISIBILITY_FLAG="--public"
            if [[ "$REPO_VISIBILITY" == "private" ]]; then
                REPO_VISIBILITY_FLAG="--private"
            fi
            if create_github_repo_if_needed "$GITHUB_REPO" "$APP_NAME deployment repository" "$REPO_VISIBILITY_FLAG"; then
                echo -e "${GREEN}✓ Repository created${NC}"
            else
                echo -e "${RED}❌ Failed to create repository${NC}"
                exit 1
            fi
        else
            echo -e "${GREEN}✓ Repository already exists${NC}"
        fi
        
        # Set up git remote
        if ! git remote get-url origin &>/dev/null; then
            git remote add origin "https://github.com/${GITHUB_REPO}.git"
            echo -e "${GREEN}✓ Git remote added${NC}"
        else
            git remote set-url origin "https://github.com/${GITHUB_REPO}.git"
            echo -e "${GREEN}✓ Git remote updated${NC}"
        fi
    else
        # Try to get from git remote or use environment variable as fallback
        if [[ -z "$GITHUB_REPO" ]]; then
            GITHUB_REPO=$(git remote get-url origin 2>/dev/null | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/' | sed 's/\.git$//')
        fi
        
        if [ -z "$GITHUB_REPO" ]; then
            if [[ "$FULLY_AUTOMATED" == "true" ]]; then
                # Use app name as repository name for fully automated mode
                DEFAULT_REPO_NAME=$(echo "$APP_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
                
                # Get GitHub username from gh CLI
                GITHUB_USERNAME=$(gh api user --jq '.login' 2>/dev/null)
                if [[ -z "$GITHUB_USERNAME" ]]; then
                    echo -e "${RED}❌ Could not get GitHub username from gh CLI${NC}"
                    echo -e "${YELLOW}💡 Please run 'gh auth login' first${NC}"
                    exit 1
                fi
                
                GITHUB_REPO="${GITHUB_USERNAME}/${DEFAULT_REPO_NAME}"
                
                # Create the repository
                echo -e "${BLUE}Creating GitHub repository: $GITHUB_REPO${NC}"
                REPO_VISIBILITY="${REPO_VISIBILITY:-private}"
                if [[ "$REPO_VISIBILITY" == "private" ]]; then
                    REPO_VISIBILITY_FLAG="--private"
                else
                    REPO_VISIBILITY_FLAG="--public"
                fi
                
                if create_github_repo_if_needed "$GITHUB_REPO" "$APP_NAME deployment repository" "$REPO_VISIBILITY_FLAG"; then
                    # Add the remote to current git repository
                    git remote add origin "https://github.com/${GITHUB_REPO}.git" 2>/dev/null || \
                    git remote set-url origin "https://github.com/${GITHUB_REPO}.git"
                    echo -e "${GREEN}✓ Git remote configured${NC}"
                else
                    echo -e "${RED}❌ Failed to create GitHub repository${NC}"
                    exit 1
                fi
                echo -e "${GREEN}✓ Using repository: $GITHUB_REPO${NC}"
            else
                # Ask for GitHub username and repository name
                echo -e "${YELLOW}⚠️  No GitHub repository found in git remote${NC}"
                echo "We need to create a new GitHub repository for your deployment."
                echo ""
                echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "${BLUE}  📦 GitHub Repository Setup${NC}"
                echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo ""
                
                # Try to get GitHub username from gh CLI first
                DEFAULT_GITHUB_USERNAME=$(gh api user --jq '.login' 2>/dev/null || echo "")
                
                # In auto mode, use gh CLI username directly or fail
                if [[ "$AUTO_MODE" == "true" ]]; then
                    if [[ -z "$DEFAULT_GITHUB_USERNAME" ]]; then
                        echo -e "${RED}❌ GitHub username is required but could not be determined${NC}"
                        echo -e "${YELLOW}💡 Please run 'gh auth login' first or provide GITHUB_USERNAME environment variable${NC}"
                        exit 1
                    fi
                    GITHUB_USERNAME="$DEFAULT_GITHUB_USERNAME"
                else
                    # Get GitHub username interactively
                    echo -e "${YELLOW}Please provide your GitHub username to create the repository.${NC}"
                    GITHUB_USERNAME=$(get_input "Enter your GitHub username" "$DEFAULT_GITHUB_USERNAME")
                    while [[ -z "$GITHUB_USERNAME" ]]; do
                        echo -e "${RED}❌ GitHub username is required${NC}"
                        GITHUB_USERNAME=$(get_input "Enter your GitHub username" "")
                    done
                fi
                
                # Get repository name (default to current directory name in lowercase)
                DEFAULT_REPO_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
                if [[ -z "$DEFAULT_REPO_NAME" ]] || [[ "$DEFAULT_REPO_NAME" == "." ]]; then
                    DEFAULT_REPO_NAME="my-app"
                fi
                echo -e "${BLUE}Suggested repository name: ${GREEN}$DEFAULT_REPO_NAME${NC}" >&2
                REPO_NAME=$(get_input "Enter repository name" "$DEFAULT_REPO_NAME")
                
                # Construct full repository path
                GITHUB_REPO="${GITHUB_USERNAME}/${REPO_NAME}"
                
                # Ask about repository visibility
                REPO_VISIBILITY=$(get_yes_no "Make repository private?" "true")
                if [[ "$REPO_VISIBILITY" == "true" ]]; then
                    REPO_VISIBILITY="--private"
                else
                    REPO_VISIBILITY="--public"
                fi
                
                # Create the repository
                echo -e "${BLUE}Creating GitHub repository: $GITHUB_REPO${NC}"
                if create_github_repo_if_needed "$GITHUB_REPO" "$APP_NAME deployment repository" "$REPO_VISIBILITY"; then
                    # Add the remote to current git repository
                    git remote add origin "https://github.com/${GITHUB_REPO}.git" 2>/dev/null || \
                    git remote set-url origin "https://github.com/${GITHUB_REPO}.git"
                    echo -e "${GREEN}✓ Git remote configured${NC}"
                else
                    echo -e "${RED}❌ Failed to create GitHub repository${NC}"
                    exit 1
                fi
            fi
        else
            echo -e "${GREEN}✓ GitHub Repository: $GITHUB_REPO${NC}"
        fi
    fi
    echo ""
    
    # Application type selection (FULLY_AUTOMATED was already set at the start of main())
    if [[ "$FULLY_AUTOMATED" == "true" ]]; then
        # Validate app type
        if [[ ! "$APP_TYPE" =~ ^(lamp|nodejs|python|react|docker|nginx)$ ]]; then
            echo -e "${RED}❌ Invalid APP_TYPE: $APP_TYPE. Must be one of: lamp, nodejs, python, react, docker, nginx${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Using APP_TYPE: $APP_TYPE${NC}"
    else
        # Run project analysis for AI recommendations (interactive mode only)
        analyze_project_for_recommendations "."
        
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  📦 STEP 1: Application Type${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        APP_TYPES=("lamp" "nodejs" "python" "react" "docker" "nginx")
        APP_TYPE=$(select_option "Choose your application type:" "1" "app_type" "${APP_TYPES[@]}")
    fi
    
    # Application name and instance configuration
    if [[ "$FULLY_AUTOMATED" != "true" ]]; then
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  🏷️  STEP 2: Application Details${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        APP_NAME=$(get_input "Enter application name" "$(to_uppercase "${APP_TYPE:0:1}")${APP_TYPE:1} Application")
    fi
    
    # Instance configuration
    if [[ "$FULLY_AUTOMATED" != "true" ]]; then
        INSTANCE_NAME=$(get_input "Enter Lightsail instance name" "${APP_TYPE}-app-$(date +%s)")
    fi
    
    # AWS Region
    if [[ "$FULLY_AUTOMATED" != "true" ]]; then
        AWS_REGION=$(get_input "Enter AWS region" "$AWS_REGION")
    fi
    
    # Instance size
    if [[ "$FULLY_AUTOMATED" == "true" ]]; then
        # Validate bundle for Docker
        if [[ "$APP_TYPE" == "docker" && "$BUNDLE_ID" =~ ^(nano_3_0|micro_3_0)$ ]]; then
            echo -e "${RED}❌ Docker applications require minimum small_3_0 bundle (2GB RAM). Current: $BUNDLE_ID${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Using BUNDLE_ID: $BUNDLE_ID${NC}"
    else
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  💻 STEP 3: Instance Configuration${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        if [[ "$APP_TYPE" == "docker" ]]; then
            BUNDLES=("small_3_0" "medium_3_0" "large_3_0")
            BUNDLE_ID=$(select_option "Choose instance size (Docker needs min 2GB):" "2" "bundle" "${BUNDLES[@]}")
        else
            BUNDLES=("nano_3_0" "micro_3_0" "small_3_0" "medium_3_0")
            BUNDLE_ID=$(select_option "Choose instance size:" "2" "bundle" "${BUNDLES[@]}")
        fi
    fi
    
    # Operating system
    if [[ "$FULLY_AUTOMATED" == "true" ]]; then
        # Validate blueprint
        if [[ ! "$BLUEPRINT_ID" =~ ^(ubuntu-22-04|ubuntu-20-04|amazon-linux-2023)$ ]]; then
            echo -e "${RED}❌ Invalid BLUEPRINT_ID: $BLUEPRINT_ID. Must be one of: ubuntu-22-04, ubuntu-20-04, amazon-linux-2023${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Using BLUEPRINT_ID: $BLUEPRINT_ID${NC}"
    else
        BLUEPRINTS=("ubuntu-22-04" "ubuntu-20-04" "amazon-linux-2023")
        BLUEPRINT_ID=$(select_option "Choose operating system:" "1" "${BLUEPRINTS[@]}")
    fi
    
    # Database configuration
    if [[ "$FULLY_AUTOMATED" == "true" ]]; then
        # Use environment variables
        DB_TYPE="$DATABASE_TYPE"
        # Validate database type
        if [[ ! "$DB_TYPE" =~ ^(mysql|postgresql|mongodb|none)$ ]]; then
            echo -e "${RED}❌ Invalid DATABASE_TYPE: $DB_TYPE. Must be one of: mysql, postgresql, mongodb, none${NC}"
            exit 1
        fi
        # MongoDB only supports local installation (no RDS)
        if [[ "$DB_TYPE" == "mongodb" && "$DB_EXTERNAL" == "true" ]]; then
            echo -e "${YELLOW}⚠ MongoDB does not support external RDS. Setting to local installation.${NC}"
            DB_EXTERNAL="false"
        fi
        echo -e "${GREEN}✓ Using DATABASE_TYPE: $DB_TYPE${NC}"
        
        if [[ "$DB_TYPE" != "none" ]]; then
            if [[ "$DB_EXTERNAL" == "true" && -z "$DB_RDS_NAME" ]]; then
                DB_RDS_NAME="${APP_TYPE}-${DB_TYPE}-db"
            fi
        fi
    else
        # Interactive mode
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  🗄️  STEP 4: Database Configuration${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        DB_TYPE="none"
        DB_EXTERNAL="false"
        DB_RDS_NAME=""
        DB_NAME="app_db"
        
        # Database configuration (available for all application types)
        DB_TYPES=("mysql" "postgresql" "mongodb" "none")
        DB_TYPE=$(select_option "Choose database type:" "4" "database" "${DB_TYPES[@]}")
        
        if [[ "$DB_TYPE" != "none" ]]; then
            # MongoDB only supports local installation
            if [[ "$DB_TYPE" == "mongodb" ]]; then
                echo -e "${YELLOW}ℹ MongoDB will be installed locally on the instance${NC}"
                DB_EXTERNAL="false"
            else
                DB_EXTERNAL=$(get_yes_no "Use external RDS database?" "false")
                if [[ "$DB_EXTERNAL" == "true" ]]; then
                    DB_RDS_NAME=$(get_input "Enter RDS instance name" "${APP_TYPE}-${DB_TYPE}-db")
                fi
            fi
            DB_NAME=$(get_input "Enter database name" "app_db")
        fi
    fi
    
    # Bucket configuration
    if [[ "$FULLY_AUTOMATED" == "true" ]]; then
        # Use environment variables
        if [[ "$ENABLE_BUCKET" == "true" && -z "$BUCKET_NAME" ]]; then
            BUCKET_NAME="${APP_TYPE}-bucket-$(date +%s)"
        fi
        # Validate bucket access
        if [[ "$ENABLE_BUCKET" == "true" && ! "$BUCKET_ACCESS" =~ ^(read_only|read_write)$ ]]; then
            echo -e "${RED}❌ Invalid BUCKET_ACCESS: $BUCKET_ACCESS. Must be one of: read_only, read_write${NC}"
            exit 1
        fi
        # Validate bucket bundle
        if [[ "$ENABLE_BUCKET" == "true" && ! "$BUCKET_BUNDLE" =~ ^(small_1_0|medium_1_0|large_1_0)$ ]]; then
            echo -e "${RED}❌ Invalid BUCKET_BUNDLE: $BUCKET_BUNDLE. Must be one of: small_1_0, medium_1_0, large_1_0${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Using ENABLE_BUCKET: $ENABLE_BUCKET${NC}"
    else
        # Interactive mode
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  📁 STEP 5: Storage Configuration${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}Lightsail buckets provide S3-compatible object storage for your app.${NC}"
        echo ""
        echo -e "Common use cases:"
        echo -e "  ${GREEN}✓${NC} User file uploads (images, documents, videos)"
        echo -e "  ${GREEN}✓${NC} Static assets (CSS, JS, images)"
        echo -e "  ${GREEN}✓${NC} Backups and logs"
        echo -e "  ${GREEN}✓${NC} Media storage for content-heavy apps"
        echo ""
        echo -e "${BLUE}Pricing:${NC} Small bucket (25GB, 25GB transfer) = \$1/month"
        echo ""
        
        # Show AI recommendation for bucket if detected
        local bucket_default="false"
        if [ "$RECOMMENDED_BUCKET" == "true" ]; then
            echo -e "${YELLOW}★ AI detected file upload patterns in your code - bucket recommended${NC}"
            echo ""
            bucket_default="true"
        fi
        
        ENABLE_BUCKET=$(get_yes_no "Enable Lightsail bucket for file storage?" "$bucket_default")
        BUCKET_NAME=""
        BUCKET_ACCESS="read_write"
        BUCKET_BUNDLE="small_1_0"
        
        if [[ "$ENABLE_BUCKET" == "true" ]]; then
            echo ""
            echo -e "${BLUE}Bucket Configuration:${NC}"
            BUCKET_NAME=$(get_input "Enter bucket name" "${APP_TYPE}-bucket-$(date +%s)")
            
            echo ""
            echo -e "${BLUE}Access Level:${NC}"
            echo -e "  ${GREEN}read_only${NC}  - App can only read files (for serving static content)"
            echo -e "  ${GREEN}read_write${NC} - App can upload and read files (for user uploads)"
            BUCKET_ACCESSES=("read_only" "read_write")
            BUCKET_ACCESS=$(select_option "Choose bucket access level:" "2" "${BUCKET_ACCESSES[@]}")
            
            echo ""
            echo -e "${BLUE}Bucket Size:${NC}"
            echo -e "  ${GREEN}small_1_0${NC}  - 25GB storage, 25GB transfer/month - \$1/mo"
            echo -e "  ${GREEN}medium_1_0${NC} - 100GB storage, 100GB transfer/month - \$3/mo"
            echo -e "  ${GREEN}large_1_0${NC}  - 250GB storage, 250GB transfer/month - \$5/mo"
            BUCKET_BUNDLES=("small_1_0" "medium_1_0" "large_1_0")
            BUCKET_BUNDLE=$(select_option "Choose bucket size:" "1" "${BUCKET_BUNDLES[@]}")
        fi
    fi
    
    # Verification endpoint configuration
    if [[ "$FULLY_AUTOMATED" == "true" ]]; then
        # Use environment variables (VERIFICATION_ENDPOINT, HEALTH_CHECK_ENDPOINT, API_ONLY_APP)
        if [[ -n "$VERIFICATION_ENDPOINT" ]]; then
            echo -e "${GREEN}✓ Using custom verification endpoint: $VERIFICATION_ENDPOINT${NC}"
        elif [[ "$API_ONLY_APP" == "true" ]]; then
            echo -e "${GREEN}✓ API-only app mode enabled${NC}"
        fi
    else
        # Interactive mode - ask about verification endpoint
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  🔍 STEP 6: Health Check Configuration${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}The deployment will test an endpoint to verify your app is running.${NC}"
        echo -e "${YELLOW}Default is '/' but API-only apps may need a different endpoint.${NC}"
        echo ""
        
        CUSTOM_ENDPOINT=$(get_yes_no "Customize verification endpoint?" "false")
        if [[ "$CUSTOM_ENDPOINT" == "true" ]]; then
            VERIFICATION_ENDPOINT=$(get_input "Enter verification endpoint path" "/api/health")
            echo -e "${GREEN}✓ Will verify deployment using: $VERIFICATION_ENDPOINT${NC}"
            
            # Ask about expected content
            EXPECTED_CONTENT=$(get_input "Enter expected content in response (leave empty for any)" "")
            if [[ -n "$EXPECTED_CONTENT" ]]; then
                echo -e "${GREEN}✓ Will check for content: $EXPECTED_CONTENT${NC}"
            fi
        fi
    fi
    
    echo ""
    echo -e "${BLUE}Creating deployment configuration...${NC}"
    
    # Create .gitignore file first
    create_gitignore
    
    # Create initial commit to establish main branch
    git add .gitignore
    git commit -m "Initial commit with .gitignore" || echo "Initial commit already exists"
    
    # Setup workflow files first
    setup_workflow_files
    
    # Create deployment configuration
    create_deployment_config "$APP_TYPE" "$APP_NAME" "$INSTANCE_NAME" "$AWS_REGION" \
        "$BLUEPRINT_ID" "$BUNDLE_ID" "$DB_TYPE" "$DB_EXTERNAL" "$DB_RDS_NAME" \
        "$DB_NAME" "$BUCKET_NAME" "$BUCKET_ACCESS" "$BUCKET_BUNDLE" "$ENABLE_BUCKET"
    
    # Create GitHub workflow
    create_github_workflow "$APP_TYPE" "$APP_NAME" "$AWS_REGION"
    
    # Create example application
    create_example_app "$APP_TYPE" "$APP_NAME"
    
    # Build React client if this is a fullstack Node.js + React app
    build_react_client_if_needed "$APP_TYPE"
    
    # Validate generated configuration
    if ! validate_configuration "$APP_TYPE"; then
        echo -e "${RED}❌ Configuration validation failed${NC}"
        exit 1
    fi
    
    # OIDC WORKAROUND: Ensure GITHUB_REPO has correct username/repository format
    if [[ -n "$GITHUB_REPO" && "$GITHUB_REPO" != *"/"* ]]; then
        echo -e "${YELLOW}⚠️  GITHUB_REPO missing username, applying workaround before OIDC setup...${NC}"
        
        # Use GITHUB_USERNAME from prerequisites check (already validated)
        if [[ -n "$GITHUB_USERNAME" ]]; then
            GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
            echo -e "${GREEN}✓ Fixed GITHUB_REPO for OIDC: $GITHUB_REPO${NC}"
        else
            # Fallback: Try to get username from git remote
            GIT_REMOTE_REPO=$(git remote get-url origin 2>/dev/null | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/' | sed 's/\.git$//')
            
            if [[ -n "$GIT_REMOTE_REPO" && "$GIT_REMOTE_REPO" == *"/"* ]]; then
                # Extract username from git remote
                GITHUB_USERNAME=$(echo "$GIT_REMOTE_REPO" | cut -d'/' -f1)
                GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
                echo -e "${GREEN}✓ Fixed GITHUB_REPO for OIDC: $GITHUB_REPO${NC}"
            else
                # Last resort: prompt user for username
                echo -e "${YELLOW}Could not auto-detect GitHub username${NC}"
                echo -e "${BLUE}Please enter your GitHub username:${NC}"
                read -r GITHUB_USERNAME
                if [[ -n "$GITHUB_USERNAME" ]]; then
                    GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
                    echo -e "${GREEN}✓ Fixed GITHUB_REPO for OIDC: $GITHUB_REPO${NC}"
                else
                    echo -e "${RED}❌ GitHub username is required for OIDC setup${NC}"
                    exit 1
                fi
            fi
        fi
    fi
    
    # Setup GitHub OIDC
    setup_github_oidc "$GITHUB_REPO" "$AWS_ACCOUNT_ID"
    
    # Create IAM role (sanitize name for AWS IAM requirements)
    ROLE_NAME="GitHubActions-$(echo "${APP_NAME}" | sed 's/[^a-zA-Z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')-deployment"
    AWS_ROLE_ARN=$(create_iam_role_if_needed "$ROLE_NAME" "$GITHUB_REPO" "$AWS_ACCOUNT_ID")
    
    echo -e "${GREEN}✓ IAM Role ARN: $AWS_ROLE_ARN${NC}"
    
    echo ""
    echo -e "${BLUE}Setting up GitHub repository secrets...${NC}"
    
    # Always set/update AWS_ROLE_ARN to ensure it has the correct value
    # This handles cases where the variable exists but has an incorrect value
    if gh variable list | grep -q "AWS_ROLE_ARN"; then
        echo -e "${YELLOW}Updating AWS_ROLE_ARN variable...${NC}"
        gh variable set AWS_ROLE_ARN --body "$AWS_ROLE_ARN"
        echo -e "${GREEN}✓ AWS_ROLE_ARN variable updated${NC}"
    elif gh secret list | grep -q "AWS_ROLE_ARN"; then
        echo -e "${GREEN}✓ AWS_ROLE_ARN secret already exists${NC}"
    else
        echo -e "${YELLOW}Setting AWS_ROLE_ARN as repository variable...${NC}"
        gh variable set AWS_ROLE_ARN --body "$AWS_ROLE_ARN"
        echo -e "${GREEN}✓ AWS_ROLE_ARN variable set${NC}"
    fi
    
    # Commit and push changes
    if commit_and_push "$APP_TYPE" "$APP_NAME"; then
        echo ""
        echo -e "${GREEN}✅ Deployment triggered!${NC}"
        echo -e "${BLUE}Monitor progress at: https://github.com/${GITHUB_REPO}/actions${NC}"
    fi
    
    # Show final instructions
    show_final_instructions "$APP_TYPE" "$APP_NAME" "$INSTANCE_NAME" "$GITHUB_REPO"
}

# Function to show help
show_help() {
    cat << EOF
🚀 Complete Deployment Setup Script
===================================

This script sets up automated deployment for various application types on AWS Lightsail
using GitHub Actions. It creates deployment configurations, workflows, and example applications
that match the existing working patterns in this repository.

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --interactive, -i   Run in interactive mode with AI recommendations (default)
    --auto              Run in automatic mode (uses defaults, no prompts)
    --aws-region REGION Set AWS region (default: us-east-1)
    --app-version VER   Set application version (default: 1.0.0)
    --help, -h          Show this help message

ENVIRONMENT VARIABLES:
    AUTO_MODE           Set to 'true' for automatic mode
    AWS_REGION          AWS region to use
    APP_VERSION         Application version

SUPPORTED APPLICATION TYPES:
    - lamp              LAMP stack (Linux, Apache, MySQL, PHP)
    - nodejs            Node.js with Express
    - python            Python with Flask
    - react             React single-page application
    - docker            Docker multi-container application
    - nginx             Static site with Nginx

PREREQUISITES:
    - git               Version control
    - gh                GitHub CLI (authenticated)
    - aws               AWS CLI (configured)
    - Active GitHub repository with proper permissions

EXAMPLES:
    # Interactive mode with AI recommendations (default)
    $0
    
    # Explicit interactive mode
    $0 --interactive

    # Automatic mode with defaults
    AUTO_MODE=true $0

    # Specify region
    $0 --aws-region us-west-2

    # Full automatic setup
    $0 --auto --aws-region eu-west-1 --app-version 2.0.0

WHAT IT CREATES:
    - deployment-{type}.config.yml    Deployment configuration
    - .github/workflows/deploy-{type}.yml    GitHub Actions workflow
    - Application files in root directory
    - AWS IAM role for GitHub OIDC    (if needed)
    - GitHub repository variables     (AWS_ROLE_ARN)

The generated configurations match the existing working examples in this repository
and are compatible with the deploy-generic-reusable.yml workflow.

For more information, see: https://github.com/naveenraj44125-creator/lamp-stack-lightsail
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --auto)
                AUTO_MODE=true
                shift
                ;;
            --interactive|-i)
                AUTO_MODE=false
                # Clear environment variables that would trigger fully automated mode
                unset APP_TYPE APP_NAME INSTANCE_NAME GITHUB_REPO
                shift
                ;;
            --aws-region)
                AWS_REGION="$2"
                shift 2
                ;;
            --app-version)
                APP_VERSION="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi