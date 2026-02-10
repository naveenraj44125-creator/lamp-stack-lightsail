#!/bin/bash

################################################################################
# Module: 00-variables.sh
# Purpose: Define all environment variables and default configuration values
#          for the AWS Lightsail deployment setup script.
#
# Dependencies: None (foundation module)
#
# Exports:
#   - Color variables: RED, GREEN, YELLOW, BLUE, NC
#   - Configuration: AUTO_MODE, AWS_REGION, APP_VERSION
#   - MCP recommendations: RECOMMENDED_APP_TYPE, RECOMMENDED_DATABASE, etc.
#   - Fully automated mode variables: APP_TYPE, APP_NAME, INSTANCE_NAME, etc.
#   - Verification variables: VERIFICATION_ENDPOINT, HEALTH_CHECK_ENDPOINT, etc.
#
# Usage: This module should be sourced first before any other modules.
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
AUTO_MODE=${AUTO_MODE:-false}
AWS_REGION=${AWS_REGION:-us-east-1}
APP_VERSION=${APP_VERSION:-1.0.0}

# MCP Server integration - stores AI recommendations
MCP_RECOMMENDATIONS=""
RECOMMENDED_APP_TYPE=""
RECOMMENDED_DATABASE=""
RECOMMENDED_BUNDLE=""
RECOMMENDED_BUCKET="false"
ANALYSIS_CONFIDENCE=0

# Fully automated mode environment variables
APP_TYPE=${APP_TYPE:-}
APP_NAME=${APP_NAME:-}
INSTANCE_NAME=${INSTANCE_NAME:-}
BLUEPRINT_ID=${BLUEPRINT_ID:-ubuntu-22-04}
BUNDLE_ID=${BUNDLE_ID:-micro_3_0}
DATABASE_TYPE=${DATABASE_TYPE:-none}
DB_EXTERNAL=${DB_EXTERNAL:-false}
DB_RDS_NAME=${DB_RDS_NAME:-}
DB_NAME=${DB_NAME:-app_db}
ENABLE_BUCKET=${ENABLE_BUCKET:-false}
BUCKET_NAME=${BUCKET_NAME:-}
BUCKET_ACCESS=${BUCKET_ACCESS:-read_write}
BUCKET_BUNDLE=${BUCKET_BUNDLE:-small_1_0}
GITHUB_REPO=${GITHUB_REPO:-}
REPO_VISIBILITY=${REPO_VISIBILITY:-private}

# Verification endpoint customization (for API-only apps)
VERIFICATION_ENDPOINT=${VERIFICATION_ENDPOINT:-}
HEALTH_CHECK_ENDPOINT=${HEALTH_CHECK_ENDPOINT:-}
EXPECTED_CONTENT=${EXPECTED_CONTENT:-}
API_ONLY_APP=${API_ONLY_APP:-false}
