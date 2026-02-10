#!/bin/bash

# Main setup script that orchestrates the deployment setup
# This script sources modular components from the setup/ directory

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source all setup modules in order
echo "Loading setup modules..."

# 1. Variables and configuration
source "$SCRIPT_DIR/setup/00-variables.sh"

# 2. Utility functions
source "$SCRIPT_DIR/setup/01-utils.sh"

# 3. UI functions
source "$SCRIPT_DIR/setup/02-ui.sh"

# 4. Project analysis
source "$SCRIPT_DIR/setup/03-project-analysis.sh"

# 5. GitHub integration
source "$SCRIPT_DIR/setup/04-github.sh"

# 6. AWS integration
source "$SCRIPT_DIR/setup/05-aws.sh"

# 7. Config generation
source "$SCRIPT_DIR/setup/06-config-generation.sh"

echo "✓ All modules loaded"
echo ""

# Function to show help
show_help() {
    cat << EOF
🚀 Complete Deployment Setup Script (Modular Version)

USAGE:
    ./setup.sh [OPTIONS]

OPTIONS:
    --auto              Run in fully automated mode (requires environment variables)
    --app-type TYPE     Application type (lamp, nodejs, python, docker, react)
    --app-name NAME     Application name
    --help              Show this help message

AUTOMATED MODE ENVIRONMENT VARIABLES:
    APP_TYPE            Application type
    APP_NAME            Application name
    INSTANCE_NAME       Lightsail instance name
    BLUEPRINT_ID        OS blueprint (ubuntu-22-04, ubuntu-20-04, amazon-linux-2023)
    BUNDLE_ID           Instance size (micro_3_0, small_3_0, medium_3_0, etc.)
    DATABASE_TYPE       Database type (mysql, postgresql, none)
    ENABLE_BUCKET       Enable S3 bucket (true/false)
    GITHUB_REPO         GitHub repository (owner/repo)
    AWS_REGION          AWS region (default: us-east-1)

EXAMPLES:
    # Interactive mode
    ./setup.sh

    # Automated mode
    export APP_TYPE=nodejs
    export APP_NAME="My App"
    export GITHUB_REPO="myuser/myapp"
    ./setup.sh --auto

For more information, visit: https://github.com/naveenraj44125-creator/AiFunCheckApp1
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
            --app-type)
                APP_TYPE="$2"
                shift 2
                ;;
            --app-name)
                APP_NAME="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Main execution function
main() {
    # Clear screen for fresh start (only in interactive mode)
    if [[ "$AUTO_MODE" != "true" ]]; then
        clear
    fi
    
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║     🚀 AWS Lightsail Deployment Setup (Modular)           ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✓ Setup ready to begin${NC}"
    echo ""
    
    # Analyze project if in interactive mode
    if [[ "$AUTO_MODE" != "true" ]]; then
        analyze_project_for_recommendations "."
    fi
    
    # Get application type
    if [[ -z "$APP_TYPE" ]]; then
        APP_TYPE=$(select_option \
            "Select application type:" \
            "${RECOMMENDED_APP_TYPE:-nodejs}" \
            "app_type" \
            "lamp" "nodejs" "python" "docker" "react")
    fi
    
    echo -e "${BLUE}Selected app type: ${APP_TYPE}${NC}"
    
    # Get application name
    if [[ -z "$APP_NAME" ]]; then
        APP_NAME=$(get_input "Enter application name" "my-app")
    fi
    
    echo -e "${BLUE}Application name: ${APP_NAME}${NC}"
    
    # Get GitHub repository
    if [[ -z "$GITHUB_REPO" ]]; then
        local default_repo=$(gh api user --jq .login 2>/dev/null)/$(basename "$PWD")
        GITHUB_REPO=$(get_input "Enter GitHub repository (owner/repo)" "$default_repo")
    fi
    
    echo -e "${BLUE}GitHub repository: ${GITHUB_REPO}${NC}"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ Configuration Complete                                  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}App Type:${NC} $APP_TYPE"
    echo -e "${BLUE}App Name:${NC} $APP_NAME"
    echo -e "${BLUE}GitHub:${NC} $GITHUB_REPO"
    echo ""
    
    # Create GitHub repository if needed
    if ! check_git_repo; then
        git init
        echo -e "${GREEN}✓ Git repository initialized${NC}"
    fi
    
    create_github_repo_if_needed "$GITHUB_REPO" "$APP_NAME deployment" "${REPO_VISIBILITY:-private}"
    
    # Create .gitignore
    if [[ ! -f ".gitignore" ]]; then
        create_gitignore
    fi
    
    # Setup workflow files
    setup_workflow_files
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ Setup Complete!                                         ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Review the generated configuration files"
    echo -e "  2. Commit and push your changes"
    echo -e "  3. GitHub Actions will automatically deploy your application"
    echo ""
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi
