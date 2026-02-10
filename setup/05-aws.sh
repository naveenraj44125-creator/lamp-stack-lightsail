#!/bin/bash

# Function to create IAM role for GitHub OIDC
create_iam_role_if_needed() {
    local role_name="$1"
    local github_repo="$2"
    local aws_account_id="$3"
    
    echo -e "${BLUE}Checking IAM role for GitHub OIDC...${NC}" >&2
    
    # Get AWS account ID if not provided
    if [[ -z "$aws_account_id" ]]; then
        aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    fi
    
    # Construct role ARN
    local role_arn="arn:aws:iam::${aws_account_id}:role/${role_name}"
    
    # Check if role exists
    if aws iam get-role --role-name "$role_name" &> /dev/null; then
        echo -e "${GREEN}✓ IAM role already exists${NC}" >&2
        echo "$role_arn"
        return 0
    fi
    
    echo -e "${YELLOW}Creating IAM role: $role_name${NC}" >&2
    
    # Create trust policy
    local trust_policy=$(cat <<EOF
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
          "token.actions.githubusercontent.com:sub": "repo:${github_repo}:*"
        }
      }
    }
  ]
}
EOF
)
    
    # Create role
    aws iam create-role \
        --role-name "$role_name" \
        --assume-role-policy-document "$trust_policy" \
        --description "Role for GitHub Actions to deploy to AWS Lightsail" >&2
    
    # Create custom Lightsail policy (since AmazonLightsailFullAccess doesn't exist)
    local policy_name="${role_name}-LightsailAccess"
    local policy_document=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lightsail:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
)
    
    # Create the policy
    local policy_arn=$(aws iam create-policy \
        --policy-name "$policy_name" \
        --policy-document "$policy_document" \
        --query 'Policy.Arn' \
        --output text 2>/dev/null || echo "arn:aws:iam::${aws_account_id}:policy/${policy_name}")
    
    # Attach policies
    aws iam attach-role-policy \
        --role-name "$role_name" \
        --policy-arn "$policy_arn" >&2
    
    aws iam attach-role-policy \
        --role-name "$role_name" \
        --policy-arn "arn:aws:iam::aws:policy/ReadOnlyAccess" >&2
    
    echo -e "${GREEN}✓ IAM role created${NC}" >&2
    
    # Return the role ARN (to stdout, not stderr)
    echo "$role_arn"
}

# Function to setup GitHub OIDC if needed
setup_github_oidc() {
    local github_repo="$1"
    local aws_account_id="$2"
    
    echo -e "${BLUE}Setting up GitHub OIDC provider...${NC}"
    
    # Check if OIDC provider exists
    if aws iam get-open-id-connect-provider \
        --open-id-connect-provider-arn "arn:aws:iam::${aws_account_id}:oidc-provider/token.actions.githubusercontent.com" \
        &> /dev/null; then
        echo -e "${GREEN}✓ OIDC provider already exists${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}Creating OIDC provider${NC}"
    
    aws iam create-open-id-connect-provider \
        --url "https://token.actions.githubusercontent.com" \
        --client-id-list "sts.amazonaws.com" \
        --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"
    
    echo -e "${GREEN}✓ OIDC provider created${NC}"
}
