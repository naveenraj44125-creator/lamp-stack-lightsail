#!/bin/bash

# AWS Lightsail Deployment Setup Installer
# This script downloads and runs the modular setup.sh script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_URL="https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main"
TEMP_DIR=$(mktemp -d)

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AWS Lightsail Deployment Setup                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in interactive mode
INTERACTIVE_MODE=false
if [[ "$1" == "--interactive" ]]; then
    INTERACTIVE_MODE=true
fi

# Download setup.sh
echo -e "${BLUE}Downloading setup script...${NC}"
if curl -fsSL "${REPO_URL}/setup.sh" -o "${TEMP_DIR}/setup.sh"; then
    chmod +x "${TEMP_DIR}/setup.sh"
    echo -e "${GREEN}✓ Setup script downloaded${NC}"
else
    echo -e "${RED}❌ Failed to download setup script${NC}"
    exit 1
fi

# Download setup modules
echo -e "${BLUE}Downloading setup modules...${NC}"
mkdir -p "${TEMP_DIR}/setup"

MODULES=(
    "00-variables.sh"
    "01-utils.sh"
    "02-ui.sh"
    "03-project-analysis.sh"
    "04-github.sh"
    "05-aws.sh"
    "06-config-generation.sh"
    "07-deployment.sh"
    "08-interactive.sh"
)

for module in "${MODULES[@]}"; do
    if curl -fsSL "${REPO_URL}/setup/${module}" -o "${TEMP_DIR}/setup/${module}"; then
        echo -e "${GREEN}  ✓ ${module}${NC}"
    else
        echo -e "${RED}  ❌ Failed to download ${module}${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}✓ All modules downloaded successfully${NC}"
echo ""

# Run setup script
cd "${TEMP_DIR}"

if [[ "$INTERACTIVE_MODE" == "true" ]]; then
    echo -e "${BLUE}Running setup in interactive mode...${NC}"
    echo ""
    bash setup.sh
else
    echo -e "${BLUE}Running setup...${NC}"
    echo ""
    bash setup.sh "$@"
fi

# Cleanup
cd -
rm -rf "${TEMP_DIR}"

echo ""
echo -e "${GREEN}Setup complete!${NC}"
