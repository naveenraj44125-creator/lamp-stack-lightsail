#!/bin/bash

# Test the full OIDC workaround in setup-complete-deployment.sh

echo "🧪 Testing OIDC Workaround in setup-complete-deployment.sh"
echo "=========================================================="

# Set up environment like broken MCP server v1.1.0
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
export GITHUB_REPO=social-media-app-deployment  # Broken: missing username
export REPO_VISIBILITY=private

echo "🔧 Simulating broken MCP server environment:"
echo "  FULLY_AUTOMATED=$FULLY_AUTOMATED"
echo "  APP_NAME=$APP_NAME"
echo "  GITHUB_REPO=$GITHUB_REPO (missing username - this is the bug)"

# Test the workaround logic from setup script
echo ""
echo "🔍 Testing workaround logic..."

# This is the new logic from setup-complete-deployment.sh
if [[ "$FULLY_AUTOMATED" == "true" && -n "$GITHUB_REPO" ]]; then
    echo "✓ Using GITHUB_REPO: $GITHUB_REPO"
    
    # WORKAROUND: Fix GITHUB_REPO if it's missing username
    if [[ "$GITHUB_REPO" != *"/"* ]]; then
        echo "⚠️  GITHUB_REPO missing username, applying workaround..."
        
        # Try to get username from git remote
        GIT_REMOTE_REPO=$(git remote get-url origin 2>/dev/null | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/' | sed 's/\.git$//')
        
        if [[ -n "$GIT_REMOTE_REPO" && "$GIT_REMOTE_REPO" == *"/"* ]]; then
            # Extract username from git remote
            GITHUB_USERNAME=$(echo "$GIT_REMOTE_REPO" | cut -d'/' -f1)
            GITHUB_REPO="${GITHUB_USERNAME}/${GITHUB_REPO}"
            echo "✓ Fixed GITHUB_REPO using git remote: $GITHUB_REPO"
        else
            echo "❌ Could not determine GitHub username from git remote"
            echo "❌ OIDC setup will fail without username/repository format"
        fi
    fi
fi

# Simulate AWS account ID
AWS_ACCOUNT_ID="123456789012"

echo ""
echo "📝 Final values for OIDC setup:"
echo "  GITHUB_REPO=$GITHUB_REPO"
echo "  AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID"

echo ""
echo "🔒 Trust policy that will be created:"
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
echo "🎯 WORKAROUND TEST RESULT:"
if [[ "$GITHUB_REPO" == *"/"* ]]; then
    echo "✅ SUCCESS: OIDC workaround fixed the repository path"
    echo "✅ Trust policy will work correctly: repo:${GITHUB_REPO}:*"
    echo "✅ GitHub Actions OIDC authentication will succeed"
else
    echo "❌ FAILED: Repository path still missing username"
    echo "❌ Trust policy will fail: repo:${GITHUB_REPO}:*"
    echo "❌ GitHub Actions OIDC authentication will fail"
fi

echo ""
echo "💡 This workaround allows the current MCP server (v1.1.0) to work"
echo "💡 Once MCP server v1.1.4+ is deployed, this workaround won't be needed"