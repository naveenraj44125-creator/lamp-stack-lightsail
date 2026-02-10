#!/bin/bash

################################################################################
# Module: 07-deployment.sh
# Purpose: Deployment orchestration and validation functions
#
# Dependencies: 00-variables.sh, 01-utils.sh, 04-github.sh, 06-config-generation.sh
#
# Exports:
#   - validate_configuration(app_type): Validate generated configuration
#   - show_final_instructions(app_type, app_name, instance_name, github_repo): Display final instructions
#
# Usage: Source this module after dependencies are loaded
################################################################################

# Function to validate generated configuration
validate_configuration() {
    local app_type="$1"
    local config_file="deployment-${app_type}.config.yml"
    local workflow_file=".github/workflows/deploy-${app_type}.yml"
    
    echo -e "${BLUE}Validating generated configuration...${NC}"
    
    # Check if files exist
    if [[ ! -f "$config_file" ]]; then
        echo -e "${RED}❌ Configuration file not found: $config_file${NC}"
        return 1
    fi
    
    if [[ ! -f "$workflow_file" ]]; then
        echo -e "${RED}❌ Workflow file not found: $workflow_file${NC}"
        return 1
    fi
    
    # Validate YAML syntax
    if command -v python3 &> /dev/null; then
        python3 -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Configuration YAML is valid${NC}"
        else
            echo -e "${RED}❌ Configuration YAML is invalid${NC}"
            return 1
        fi
        
        python3 -c "import yaml; yaml.safe_load(open('$workflow_file'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Workflow YAML is valid${NC}"
        else
            echo -e "${RED}❌ Workflow YAML is invalid${NC}"
            return 1
        fi
    fi
    
    # Check for required sections in config
    local required_sections=("aws" "lightsail" "application" "dependencies" "deployment" "github_actions" "monitoring")
    for section in "${required_sections[@]}"; do
        if grep -q "^${section}:" "$config_file"; then
            echo -e "${GREEN}✓ Found required section: $section${NC}"
        else
            echo -e "${YELLOW}⚠️  Missing section: $section${NC}"
        fi
    done
    
    # Check workflow uses reusable workflow (either local or cross-repo)
    if grep -q "uses:.*deploy-generic-reusable.yml" "$workflow_file"; then
        echo -e "${GREEN}✓ Workflow uses reusable deployment${NC}"
    else
        echo -e "${RED}❌ Workflow doesn't use reusable deployment${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Configuration validation passed${NC}"
    return 0
}

# Function to display final instructions
show_final_instructions() {
    local app_type="$1"
    local app_name="$2"
    local instance_name="$3"
    local github_repo="$4"
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                                                               ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}   ${GREEN}🎉 Setup Complete!${NC}                                          ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                               ${GREEN}║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Your ${YELLOW}${app_name}${BLUE} deployment is ready!${NC}"
    echo ""
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC} ${YELLOW}📁 Files Created:${NC}                                              ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   • deployment-${app_type}.config.yml                              ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   • .github/workflows/deploy-${app_type}.yml                       ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   • ${app_type} application files                                  ${BLUE}│${NC}"
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────────┤${NC}"
    echo -e "${BLUE}│${NC} ${YELLOW}🚀 Next Steps:${NC}                                                 ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   1. Review deployment-${app_type}.config.yml                      ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   2. Update default passwords in the config                    ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   3. Push changes: ${GREEN}git push origin main${NC}                       ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   4. Monitor: ${GREEN}https://github.com/${github_repo}/actions${NC}        ${BLUE}│${NC}"
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────────┤${NC}"
    echo -e "${BLUE}│${NC} ${YELLOW}🌐 After Deployment:${NC}                                           ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC}   Your app: ${GREEN}http://${instance_name}.lightsail.aws.com/${NC}         ${BLUE}│${NC}"
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Important Reminders:${NC}"
    echo "   • Change default passwords before deploying to production"
    echo "   • Ensure AWS_ROLE_ARN is set in GitHub repository secrets"
    echo "   • Review security settings and firewall configuration"
    echo ""
}
