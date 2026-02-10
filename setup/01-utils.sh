#!/bin/bash

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
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi
    
    # Check for GitHub CLI
    if ! command -v gh &> /dev/null; then
        missing_tools+=("gh")
    fi
    
    # Check for jq
    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing required tools: ${missing_tools[*]}${NC}"
        echo ""
        echo "Please install the missing tools:"
        for tool in "${missing_tools[@]}"; do
            case $tool in
                "aws-cli")
                    echo "  - AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
                    ;;
                "gh")
                    echo "  - GitHub CLI: https://cli.github.com/"
                    ;;
                "jq")
                    echo "  - jq: https://stedolan.github.io/jq/download/"
                    ;;
            esac
        done
        return 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials not configured${NC}"
        echo "Please run: aws configure"
        return 1
    fi
    
    # Check GitHub authentication
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI not authenticated${NC}"
        echo "Please run: gh auth login"
        return 1
    fi
    
    echo -e "${GREEN}✓ All prerequisites met${NC}"
    return 0
}

# Function to check if we're in a git repository
check_git_repo() {
    # Check if .git exists in current directory (not inherited from parent)
    if [ -d ".git" ]; then
        return 0
    fi
    return 1
}
