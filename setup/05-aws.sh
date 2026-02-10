#!/bin/bash

################################################################################
# Module: 05-aws.sh
# Purpose: Manage AWS IAM roles and OIDC provider setup
#
# Dependencies: 00-variables.sh, 01-utils.sh
#
# Exports:
#   - create_iam_role_if_needed(role_name, github_repo, aws_account_id): 
#       Create IAM role for GitHub OIDC
#   - setup_github_oidc(github_repo, aws_account_id): 
#       Setup GitHub OIDC provider
#
# Critical: This module contains the IAM_Role_Bug_Fix
#   - Status messages MUST be redirected to stderr (>&2)
#   - Only the role ARN should go to stdout
#   - This allows callers to capture the ARN without capturing status messages
#
# Usage: Source this module after 00-variables.sh and 01-utils.sh
################################################################################

# Function to create IAM role for GitHub OIDC
# CRITICAL IAM_Role_Bug_Fix: Status messages go to stderr, role ARN goes to stdout
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
