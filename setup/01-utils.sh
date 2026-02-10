#!/bin/bash

################################################################################
# Module: 01-utils.sh
# Purpose: Provide utility functions used across multiple modules
#
# Dependencies: 00-variables.sh
#
# Exports:
#   - to_lowercase(string): Convert string to lowercase
#   - to_uppercase(string): Convert string to uppercase
#   - check_prerequisites(): Verify required tools are installed
#   - check_git_repo(): Check if current directory is a git repository
#
# Usage: Source this module after 00-variables.sh
################################################################################

# Function to convert string to lowercase (compatible with older bash versions)
to_lowercase() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Function to convert string to uppercase (compatible with older bash versions)
to_uppercase() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
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

# Function to check if we're in a git repository (checks for .git in current directory, not parent)
check_git_repo() {
    # Check if .git exists in current directory (not inherited from parent)
    if [ -d ".git" ]; then
        return 0
    fi
    return 1
}
