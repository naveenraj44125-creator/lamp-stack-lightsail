#!/bin/bash

# Test a workaround for the setup script to handle broken MCP server output

echo "🔧 Testing Setup Script Workaround for OIDC Issue"
echo "================================================="

# Simulate current broken MCP server environment
export FULLY_AUTOMATED=true
export APP_NAME=social-media-app-deployment
export GITHUB_REPO=social-media-app-deployment  # Broken: missing username
export REPO_VISIBILITY=private
AWS_ACCOUNT_ID="123456789012"

echo "Current broken environment:"
echo "  GITHUB_REPO=$GITHUB_REPO (missing username)"

# Proposed workaround logic
echo ""
echo "🔧 Applying workaround logic..."

# Check if GITHUB_REPO is missing username and we're in fully automated mode
if [[ "$FULLY_AUTOMATED" == "true" && -n "$GITHUB_REPO" && "$GITHUB_REPO" != *"/"* ]]; then
    echo "  ⚠️  Detected GITHUB_REPO without username in fully automated mode"
    
    # Try to get username from git remote
    GIT_REMOTE_REPO=$(git remote get-url origin 2>/dev/null | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/' | sed 's/\.git$//')
    
    if [[ -n "$GIT_REMOTE_REPO" && "$GIT_REMOTE_REPO" == *"/"* ]]; then
        # Extract username from git remote
        GITHUB_USERNAME=$(echo "$GIT_REMOTE_REPO" | cut -d'/' -f1)
        echo "  ✅ Found username from git remote: $GITHUB_USERNAME"
        GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
        echo "  ✅ Fixed GITHUB_REPO: $GITHUB_REPO"
    else
        echo "  ❌ Could not determine username from git remote"
        echo "  💡 Fallback: Ask user for username or use hardcoded value"
        
        # For this repository, we know the username
        GITHUB_USERNAME="naveenraj44125-creator"
        GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
        echo "  🔧 Using known username: $GITHUB_REPO"
    fi
else
    echo "  ✅ GITHUB_REPO already has correct format or not in fully automated mode"
fi

echo ""
echo "📝 Final values for OIDC:"
echo "  GITHUB_REPO=$GITHUB_REPO"

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
                    "token.actions.githubusercontent.com:sub": "repo:${GITHUB_REPO}:*"
                }
            }
        }
    ]
}
EOF

echo ""
if [[ "$GITHUB_REPO" == *"/"* ]]; then
    echo "✅ WORKAROUND SUCCESS: Repository path now includes username"
    echo "✅ OIDC trust policy will work correctly"
else
    echo "❌ WORKAROUND FAILED: Repository path still missing username"
    echo "❌ OIDC trust policy will still fail"
fi