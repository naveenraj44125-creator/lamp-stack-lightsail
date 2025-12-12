#!/bin/bash

# Test script to verify OIDC setup values in setup-complete-deployment.sh
# This simulates the environment that MCP server creates

echo "🧪 Testing OIDC Setup Values in setup-complete-deployment.sh"
echo "============================================================"

# Test Case 1: MCP Server with github_username (FIXED version)
echo ""
echo "📋 Test Case 1: MCP Server with github_username parameter (FIXED)"
echo "----------------------------------------------------------------"

export FULLY_AUTOMATED=true
export APP_TYPE=nodejs
export APP_NAME=social-media-app-deployment
export INSTANCE_NAME=social-media-app-deployment-instance
export AWS_REGION=us-east-1
export BLUEPRINT_ID=ubuntu_22_04
export BUNDLE_ID=nano_3_0
export DATABASE_TYPE=none
export DB_EXTERNAL=false
export ENABLE_BUCKET=false
export GITHUB_REPO=naveenraj44125-creator/social-media-app-deployment  # This is what FIXED MCP server should generate
export REPO_VISIBILITY=private

echo "Environment variables set:"
echo "  FULLY_AUTOMATED=$FULLY_AUTOMATED"
echo "  APP_NAME=$APP_NAME"
echo "  GITHUB_REPO=$GITHUB_REPO"

# Extract the relevant part of setup script to test OIDC logic
echo ""
echo "🔍 Simulating setup script OIDC logic..."

# Simulate AWS account ID (normally fetched from AWS)
AWS_ACCOUNT_ID="123456789012"
echo "  AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID (simulated)"

# This is the logic from setup-complete-deployment.sh lines 1848-1861
if [[ "$FULLY_AUTOMATED" == "true" && -n "$GITHUB_REPO" ]]; then
    echo "  ✅ Using provided GITHUB_REPO: $GITHUB_REPO"
    FINAL_GITHUB_REPO="$GITHUB_REPO"
else
    echo "  ❌ Would fall back to interactive mode or APP_NAME only"
    FINAL_GITHUB_REPO="$APP_NAME"
fi

echo ""
echo "📝 Values that would be passed to OIDC functions:"
echo "  setup_github_oidc \"$FINAL_GITHUB_REPO\" \"$AWS_ACCOUNT_ID\""
echo "  create_iam_role_if_needed \"GitHubActions-${APP_NAME}-deployment\" \"$FINAL_GITHUB_REPO\" \"$AWS_ACCOUNT_ID\""

echo ""
echo "🔒 Trust policy that would be created:"
cat << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:${FINAL_GITHUB_REPO}:*"
                }
            }
        }
    ]
}
EOF

echo ""
echo "✅ Result for Test Case 1:"
if [[ "$FINAL_GITHUB_REPO" == *"/"* ]]; then
    echo "  ✅ CORRECT: Repository path includes username: $FINAL_GITHUB_REPO"
    echo "  ✅ OIDC trust policy will work correctly"
else
    echo "  ❌ INCORRECT: Repository path missing username: $FINAL_GITHUB_REPO"
    echo "  ❌ OIDC trust policy will fail"
fi

# Test Case 2: MCP Server without github_username (BROKEN version)
echo ""
echo "📋 Test Case 2: MCP Server without github_username parameter (BROKEN)"
echo "---------------------------------------------------------------------"

unset GITHUB_REPO
export GITHUB_REPO=social-media-app-deployment  # This is what BROKEN MCP server generates

echo "Environment variables set:"
echo "  FULLY_AUTOMATED=$FULLY_AUTOMATED"
echo "  APP_NAME=$APP_NAME"
echo "  GITHUB_REPO=$GITHUB_REPO"

# This is the logic from setup-complete-deployment.sh lines 1848-1861
if [[ "$FULLY_AUTOMATED" == "true" && -n "$GITHUB_REPO" ]]; then
    echo "  ✅ Using provided GITHUB_REPO: $GITHUB_REPO"
    FINAL_GITHUB_REPO="$GITHUB_REPO"
else
    echo "  ❌ Would fall back to interactive mode or APP_NAME only"
    FINAL_GITHUB_REPO="$APP_NAME"
fi

echo ""
echo "📝 Values that would be passed to OIDC functions:"
echo "  setup_github_oidc \"$FINAL_GITHUB_REPO\" \"$AWS_ACCOUNT_ID\""
echo "  create_iam_role_if_needed \"GitHubActions-${APP_NAME}-deployment\" \"$FINAL_GITHUB_REPO\" \"$AWS_ACCOUNT_ID\""

echo ""
echo "🔒 Trust policy that would be created:"
cat << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:${FINAL_GITHUB_REPO}:*"
                }
            }
        }
    ]
}
EOF

echo ""
echo "❌ Result for Test Case 2:"
if [[ "$FINAL_GITHUB_REPO" == *"/"* ]]; then
    echo "  ✅ CORRECT: Repository path includes username: $FINAL_GITHUB_REPO"
    echo "  ✅ OIDC trust policy will work correctly"
else
    echo "  ❌ INCORRECT: Repository path missing username: $FINAL_GITHUB_REPO"
    echo "  ❌ OIDC trust policy will fail"
fi

# Test Case 3: No GITHUB_REPO provided (fallback case)
echo ""
echo "📋 Test Case 3: No GITHUB_REPO provided (fallback case)"
echo "-------------------------------------------------------"

unset GITHUB_REPO

echo "Environment variables set:"
echo "  FULLY_AUTOMATED=$FULLY_AUTOMATED"
echo "  APP_NAME=$APP_NAME"
echo "  GITHUB_REPO=(unset)"

# This is the logic from setup-complete-deployment.sh lines 1848-1861
if [[ "$FULLY_AUTOMATED" == "true" && -n "$GITHUB_REPO" ]]; then
    echo "  ✅ Using provided GITHUB_REPO: $GITHUB_REPO"
    FINAL_GITHUB_REPO="$GITHUB_REPO"
else
    echo "  ⚠️  No GITHUB_REPO provided, using APP_NAME fallback"
    FINAL_GITHUB_REPO="$APP_NAME"
fi

echo ""
echo "📝 Values that would be passed to OIDC functions:"
echo "  setup_github_oidc \"$FINAL_GITHUB_REPO\" \"$AWS_ACCOUNT_ID\""
echo "  create_iam_role_if_needed \"GitHubActions-${APP_NAME}-deployment\" \"$FINAL_GITHUB_REPO\" \"$AWS_ACCOUNT_ID\""

echo ""
echo "❌ Result for Test Case 3:"
if [[ "$FINAL_GITHUB_REPO" == *"/"* ]]; then
    echo "  ✅ CORRECT: Repository path includes username: $FINAL_GITHUB_REPO"
    echo "  ✅ OIDC trust policy will work correctly"
else
    echo "  ❌ INCORRECT: Repository path missing username: $FINAL_GITHUB_REPO"
    echo "  ❌ OIDC trust policy will fail - this is the BUG!"
fi

echo ""
echo "🎯 SUMMARY"
echo "=========="
echo "The OIDC issue occurs when:"
echo "1. MCP server doesn't provide github_username parameter (current deployed version)"
echo "2. MCP server generates GITHUB_REPO without username prefix"
echo "3. Setup script uses the incomplete repository path for trust policy"
echo ""
echo "The fix requires:"
echo "1. MCP server to include github_username parameter (already implemented in code)"
echo "2. MCP server to generate full repository path: username/repository"
echo "3. Deploy the updated MCP server (deployment issue)"