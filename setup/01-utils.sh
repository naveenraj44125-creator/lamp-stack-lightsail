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
#   - validate_bucket_name(bucket_name): Validate S3 bucket name against AWS rules
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

# Function to validate S3 bucket name against AWS naming rules
validate_bucket_name() {
    local bucket_name="$1"
    
    # Check if bucket name is empty
    if [[ -z "$bucket_name" ]]; then
        echo -e "${RED}❌ Invalid bucket name: (empty)${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket name cannot be empty${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check length (3-63 characters)
    local length=${#bucket_name}
    if [[ $length -lt 3 ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket name must be at least 3 characters long (current: $length)${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    if [[ $length -gt 63 ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket name must be at most 63 characters long (current: $length)${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check for uppercase letters
    if [[ "$bucket_name" =~ [A-Z] ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket names must be lowercase (no uppercase letters allowed)${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check for underscores
    if [[ "$bucket_name" =~ _ ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Underscores are not allowed in bucket names${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check for invalid characters (only lowercase letters, numbers, hyphens, and periods allowed)
    if [[ ! "$bucket_name" =~ ^[a-z0-9.-]+$ ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket names can only contain lowercase letters, numbers, hyphens, and periods${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check if starts with hyphen or period
    if [[ "$bucket_name" =~ ^[-\.] ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket names must start with a lowercase letter or number${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check if ends with hyphen or period
    if [[ "$bucket_name" =~ [-\.]$ ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket names must end with a lowercase letter or number${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check for consecutive periods
    if [[ "$bucket_name" =~ \.\. ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Consecutive periods (..) are not allowed in bucket names${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # Check for IP address format (e.g., 192.168.1.1)
    if [[ "$bucket_name" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}❌ Invalid bucket name: $bucket_name${NC}" >&2
        echo -e "   ${YELLOW}Reason: Bucket names cannot be formatted as IP addresses${NC}" >&2
        echo "" >&2
        echo -e "   ${BLUE}AWS S3 bucket naming rules:${NC}" >&2
        echo "   • 3-63 characters long" >&2
        echo "   • Lowercase letters, numbers, hyphens, and periods only" >&2
        echo "   • Must start and end with letter or number" >&2
        echo "   • No consecutive periods" >&2
        echo "   • No IP address format" >&2
        echo "" >&2
        echo -e "   ${GREEN}Example: my-app-bucket-2024${NC}" >&2
        return 1
    fi
    
    # All validations passed
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

# Function to check if we're in a git repository (checks for .git in current directory, not parent)
check_git_repo() {
    # Check if .git exists in current directory (not inherited from parent)
    if [ -d ".git" ]; then
        return 0
    fi
    return 1
}
