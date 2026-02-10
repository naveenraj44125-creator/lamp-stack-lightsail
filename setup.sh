#!/bin/bash

################################################################################
# AWS Lightsail Deployment Setup - Modular Orchestrator
################################################################################
#
# This is the main orchestrator script that sources all setup modules and
# coordinates the deployment setup workflow.
#
# Architecture:
#   - Lightweight orchestrator (<200 lines)
#   - Sources 9 focused modules in dependency order
#   - Preserves all functionality from monolithic version
#
# Modules:
#   00-variables.sh         - Environment variables and configuration
#   01-utils.sh             - Utility functions
#   02-ui.sh                - User interaction functions
#   03-project-analysis.sh  - Project detection and analysis
#   04-github.sh            - GitHub repository management
#   05-aws.sh               - AWS IAM and OIDC setup
#   06-config-generation.sh - Config and workflow file generation
#   07-deployment.sh        - Deployment orchestration
#   08-interactive.sh       - Interactive mode and main flow
#
# Usage:
#   ./setup.sh [options]
#
# Options:
#   --interactive, -i       Run in interactive mode (default)
#   --auto                  Run in auto mode with defaults
#   --aws-region REGION     Set AWS region (default: us-east-1)
#   --app-version VERSION   Set app version (default: 1.0.0)
#   --help, -h              Show help message
#
# Environment Variables:
#   See 00-variables.sh for full list of supported environment variables
#   for fully automated mode.
#
################################################################################

set -e  # Exit on error

# Calculate script directory for relative module paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Module loading function with error handling
load_module() {
    local module_name="$1"
    local module_path="${SCRIPT_DIR}/setup/${module_name}"
    
    if [[ ! -f "$module_path" ]]; then
        echo "ERROR: Module not found: ${module_name}" >&2
        echo "Expected location: ${module_path}" >&2
        exit 1
    fi
    
    if ! source "$module_path"; then
        echo "ERROR: Failed to load module: ${module_name}" >&2
        echo "Check module syntax and dependencies" >&2
        exit 1
    fi
}

################################################################################
# Load Modules in Dependency Order
################################################################################
#
# CRITICAL: Modules must be loaded in this exact order to satisfy dependencies.
# Later modules depend on functions and variables from earlier modules.
#
# Dependency Chain:
#   00-variables.sh         (no dependencies)
#   01-utils.sh             (depends on: 00)
#   02-ui.sh                (depends on: 00, 01)
#   03-project-analysis.sh  (depends on: 00, 01)
#   04-github.sh            (depends on: 00, 01)
#   05-aws.sh               (depends on: 00, 01)
#   06-config-generation.sh (depends on: 00, 01, 03)
#   07-deployment.sh        (depends on: 00, 01, 04, 06)
#   08-interactive.sh       (depends on: all previous)
#
################################################################################

# Load module 00: Variables
load_module "00-variables.sh"

# Load module 01: Utilities
load_module "01-utils.sh"

# Load module 02: UI
load_module "02-ui.sh"

# Load module 03: Project Analysis
load_module "03-project-analysis.sh"

# Load module 04: GitHub
load_module "04-github.sh"

# Load module 05: AWS
load_module "05-aws.sh"

# Load module 06: Config Generation
load_module "06-config-generation.sh"

# Load module 07: Deployment
load_module "07-deployment.sh"

# Load module 08: Interactive
load_module "08-interactive.sh"

################################################################################
# Main Execution
################################################################################
#
# The orchestrator delegates all execution logic to the modules:
#   - parse_args() handles command-line argument parsing (from 08-interactive.sh)
#   - main() orchestrates the entire setup workflow (from 08-interactive.sh)
#
# Only execute if script is run directly (not sourced)
#
################################################################################

# Only run main execution if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Parse command-line arguments
    parse_args "$@"
    
    # Execute main workflow
    main
fi
