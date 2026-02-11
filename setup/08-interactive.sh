#!/bin/bash

################################################################################
# Module: 08-interactive.sh
# Purpose: Interactive mode and main execution flow
# Dependencies: All previous modules (00-07)
#
# This module contains the main execution logic for the setup script, including:
# - main() function: Orchestrates the entire setup workflow
# - parse_args() function: Parses command-line arguments
# - show_help() function: Displays help text
#
# This module handles both interactive and automated modes, collecting user
# input, generating configurations, and coordinating all setup steps.
################################################################################

# Function to show help
show_help() {
    cat << EOF
🚀 Complete Deployment Setup Script
===================================

This script sets up automated deployment for various application types on AWS Lightsail
using GitHub Actions. It creates deployment configurations, workflows, and example applications
that match the existing working patterns in this repository.

USAGE:
    \$0 [OPTIONS]

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
    \$0
    
    # Explicit interactive mode
    \$0 --interactive

    # Automatic mode with defaults
    AUTO_MODE=true \$0

    # Specify region
    \$0 --aws-region us-west-2

    # Full automatic setup
    \$0 --auto --aws-region eu-west-1 --app-version 2.0.0

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

# Main execution function
main() {
    # Capture working directory at script start
    SCRIPT_START_DIR="$(pwd)"
    export SCRIPT_START_DIR
    
    # Validate working directory is writable
    if [[ ! -w "$SCRIPT_START_DIR" ]]; then
        echo -e "${RED}❌ Error: Working directory is not writable: $SCRIPT_START_DIR${NC}"
        echo -e "${YELLOW}Please run the script from a writable directory or fix permissions${NC}"
        exit 1
    fi
    
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
        if [[ ! "$BLUEPRINT_ID" =~ ^(ubuntu_22_04|ubuntu_24_04|amazon_linux_2023)$ ]]; then
            echo -e "${RED}❌ Invalid BLUEPRINT_ID: $BLUEPRINT_ID. Must be one of: ubuntu_22_04, ubuntu_24_04, amazon_linux_2023${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Using BLUEPRINT_ID: $BLUEPRINT_ID${NC}"
    else
        BLUEPRINTS=("ubuntu_22_04" "ubuntu_24_04" "amazon_linux_2023")
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
        echo ""
        
        # Use recommended health endpoint from analysis if available
        if [[ -n "$RECOMMENDED_HEALTH_ENDPOINT" ]]; then
            echo -e "${YELLOW}★ AI detected health endpoint in your code: ${RECOMMENDED_HEALTH_ENDPOINT}${NC}"
            echo ""
            USE_DETECTED=$(get_yes_no "Use detected endpoint for health checks?" "true")
            if [[ "$USE_DETECTED" == "true" ]]; then
                VERIFICATION_ENDPOINT="$RECOMMENDED_HEALTH_ENDPOINT"
                echo -e "${GREEN}✓ Will verify deployment using: $VERIFICATION_ENDPOINT${NC}"
            else
                VERIFICATION_ENDPOINT=$(get_input "Enter verification endpoint path" "/")
                echo -e "${GREEN}✓ Will verify deployment using: $VERIFICATION_ENDPOINT${NC}"
            fi
        else
            echo -e "${YELLOW}No health endpoint detected in your code.${NC}"
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
