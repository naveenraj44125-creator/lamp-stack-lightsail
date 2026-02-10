# Design Document: Setup Script Modularization

## Overview

This design transforms the monolithic 3,953-line setup.sh script into a modular architecture with a lightweight orchestrator and focused, single-responsibility modules. The design preserves ALL existing functionality while improving maintainability, testability, and code organization.

### Key Design Principles

1. **Single Responsibility**: Each module handles one specific aspect of the setup process
2. **Dependency Order**: Modules are loaded in a specific order to satisfy dependencies
3. **Zero Behavior Change**: The modularized version must behave identically to the original
4. **Preserve Bug Fixes**: Critical fixes (like IAM role stderr redirection) must be maintained
5. **Test Compatibility**: All existing tests must pass without modification

## Architecture

### Module Structure

```
setup/
├── 00-variables.sh           # Environment variables and configuration
├── 01-utils.sh               # Utility functions (lowercase, uppercase, prerequisites)
├── 02-ui.sh                  # User interaction (input, yes/no, select menus)
├── 03-project-analysis.sh    # Project detection and analysis
├── 04-github.sh              # GitHub repository and workflow management
├── 05-aws.sh                 # AWS IAM and OIDC setup
├── 06-config-generation.sh   # Config and workflow file generation
├── 07-deployment.sh          # Deployment orchestration and validation
├── 08-interactive.sh         # Interactive mode and main flow
├── README.md                 # Module documentation
├── QUICK_REFERENCE.md        # Quick reference guide
├── IMPROVEMENTS.md           # Improvement suggestions
└── SUMMARY.md                # Module summary

setup.sh                      # Lightweight orchestrator (<200 lines)
```

### Orchestrator Design (setup.sh)

The orchestrator is responsible for:
1. Sourcing all modules in dependency order
2. Parsing command-line arguments
3. Displaying help text
4. Calling the main() function from 08-interactive.sh

```bash
#!/bin/bash

# Source modules in dependency order
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/setup/00-variables.sh"
source "${SCRIPT_DIR}/setup/01-utils.sh"
source "${SCRIPT_DIR}/setup/02-ui.sh"
source "${SCRIPT_DIR}/setup/03-project-analysis.sh"
source "${SCRIPT_DIR}/setup/04-github.sh"
source "${SCRIPT_DIR}/setup/05-aws.sh"
source "${SCRIPT_DIR}/setup/06-config-generation.sh"
source "${SCRIPT_DIR}/setup/07-deployment.sh"
source "${SCRIPT_DIR}/setup/08-interactive.sh"

# Parse arguments and execute
parse_args "$@"
main
```

## Components and Interfaces

### Module 00: Variables (00-variables.sh)

**Purpose**: Define all environment variables and default configuration values

**Dependencies**: None

**Exports**:
- Color variables: RED, GREEN, YELLOW, BLUE, NC
- Configuration: AUTO_MODE, AWS_REGION, APP_VERSION
- MCP recommendations: RECOMMENDED_APP_TYPE, RECOMMENDED_DATABASE, etc.
- Fully automated mode variables: APP_TYPE, APP_NAME, INSTANCE_NAME, etc.
- Verification variables: VERIFICATION_ENDPOINT, HEALTH_CHECK_ENDPOINT, etc.

**Interface**:
```bash
# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration variables
AUTO_MODE=${AUTO_MODE:-false}
AWS_REGION=${AWS_REGION:-us-east-1}
APP_VERSION=${APP_VERSION:-1.0.0}
# ... (all other variables)
```

### Module 01: Utilities (01-utils.sh)

**Purpose**: Provide utility functions used across multiple modules

**Dependencies**: 00-variables.sh

**Exports**:
- `to_lowercase(string)`: Convert string to lowercase
- `to_uppercase(string)`: Convert string to uppercase
- `check_prerequisites()`: Verify required tools are installed
- `check_git_repo()`: Check if current directory is a git repository

**Interface**:
```bash
# Convert string to lowercase
to_lowercase() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Convert string to uppercase
to_uppercase() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Check prerequisites (git, gh, aws, python3, PyYAML)
check_prerequisites() {
    # Returns 0 on success, 1 on failure
}

# Check if in git repository
check_git_repo() {
    # Returns 0 if .git exists, 1 otherwise
}
```

### Module 02: UI (02-ui.sh)

**Purpose**: Handle all user interaction and input collection

**Dependencies**: 00-variables.sh, 01-utils.sh

**Exports**:
- `get_input(prompt, default)`: Get text input from user
- `get_yes_no(prompt, default)`: Get yes/no input from user
- `select_option(prompt, default, recommendation_type, options...)`: Display menu and get selection
- `get_option_description(option)`: Get description for known options

**Interface**:
```bash
# Get text input with default value
get_input(prompt, default) {
    # Returns user input or default
    # Respects AUTO_MODE
}

# Get yes/no input
get_yes_no(prompt, default) {
    # Returns "true" or "false"
    # Respects AUTO_MODE
}

# Display menu and get selection
select_option(prompt, default, recommendation_type, options...) {
    # Returns selected option
    # Highlights AI recommendations
    # Respects AUTO_MODE
}

# Get description for option
get_option_description(option) {
    # Returns description string
}
```

### Module 03: Project Analysis (03-project-analysis.sh)

**Purpose**: Analyze project structure and provide AI recommendations

**Dependencies**: 00-variables.sh, 01-utils.sh

**Exports**:
- `analyze_project_for_recommendations(project_path)`: Analyze project and set recommendation variables
- `detect_fullstack_react()`: Detect fullstack React + Node.js structure
- `detect_node_port()`: Auto-detect Node.js port from server files
- `detect_health_endpoints(app_type)`: Detect existing health check endpoints
- `build_react_client_if_needed(app_type)`: Build React client if detected
- `show_app_deployment_warnings(app_type)`: Show app-specific deployment warnings

**Interface**:
```bash
# Analyze project and set RECOMMENDED_* variables
analyze_project_for_recommendations(project_path) {
    # Sets: RECOMMENDED_APP_TYPE, RECOMMENDED_DATABASE, 
    #       RECOMMENDED_BUNDLE, RECOMMENDED_BUCKET, ANALYSIS_CONFIDENCE
}

# Detect fullstack React + Node.js
detect_fullstack_react() {
    # Returns 0 if detected, 1 otherwise
}

# Detect Node.js port
detect_node_port() {
    # Returns port number (default: 3000)
}

# Detect health endpoints
detect_health_endpoints(app_type) {
    # Returns endpoint path or empty
}

# Build React client if needed
build_react_client_if_needed(app_type) {
    # Returns 0 on success, 1 on failure
}

# Show deployment warnings
show_app_deployment_warnings(app_type) {
    # Displays warnings and checks
}
```

### Module 04: GitHub (04-github.sh)

**Purpose**: Manage GitHub repository creation and configuration

**Dependencies**: 00-variables.sh, 01-utils.sh

**Exports**:
- `create_github_repo_if_needed(repo_name, repo_desc, visibility)`: Create GitHub repository
- `setup_workflow_files()`: Setup workflow directory
- `create_gitignore()`: Create .gitignore file
- `commit_and_push(app_type, app_name)`: Commit and push changes

**Interface**:
```bash
# Create GitHub repository if it doesn't exist
create_github_repo_if_needed(repo_name, repo_desc, visibility) {
    # Returns 0 on success
}

# Setup workflow directory
setup_workflow_files() {
    # Creates .github/workflows/
}

# Create .gitignore file
create_gitignore() {
    # Creates .gitignore with standard patterns
}

# Commit and push changes
commit_and_push(app_type, app_name) {
    # Returns 0 on success, 1 on failure
}
```

### Module 05: AWS (05-aws.sh)

**Purpose**: Manage AWS IAM roles and OIDC provider setup

**Dependencies**: 00-variables.sh, 01-utils.sh

**Exports**:
- `create_iam_role_if_needed(role_name, github_repo, aws_account_id)`: Create IAM role for GitHub OIDC
- `setup_github_oidc(github_repo, aws_account_id)`: Setup GitHub OIDC provider

**Critical**: This module contains the IAM_Role_Bug_Fix (stderr redirection)

**Interface**:
```bash
# Create IAM role for GitHub OIDC
# CRITICAL: Status messages go to stderr, role ARN goes to stdout
create_iam_role_if_needed(role_name, github_repo, aws_account_id) {
    # Outputs status to stderr (>&2)
    # Returns role ARN to stdout
    # Preserves IAM_Role_Bug_Fix
}

# Setup GitHub OIDC provider
setup_github_oidc(github_repo, aws_account_id) {
    # Returns 0 on success
}
```

### Module 06: Config Generation (06-config-generation.sh)

**Purpose**: Generate deployment configuration and workflow files

**Dependencies**: 00-variables.sh, 01-utils.sh, 03-project-analysis.sh

**Exports**:
- `create_deployment_config(...)`: Create deployment-{type}.config.yml
- `create_github_workflow(app_type, app_name, aws_region)`: Create GitHub Actions workflow
- `create_example_app(app_type, app_name)`: Create example application files

**Interface**:
```bash
# Create deployment configuration file
create_deployment_config(app_type, app_name, instance_name, aws_region, 
                        blueprint_id, bundle_id, db_type, db_external, 
                        db_rds_name, db_name, bucket_name, bucket_access, 
                        bucket_bundle, enable_bucket) {
    # Creates deployment-{app_type}.config.yml
}

# Create GitHub Actions workflow
create_github_workflow(app_type, app_name, aws_region) {
    # Creates .github/workflows/deploy-{app_type}.yml
}

# Create example application
create_example_app(app_type, app_name) {
    # Creates app-specific example files
}
```

### Module 07: Deployment (07-deployment.sh)

**Purpose**: Orchestrate deployment setup and validation

**Dependencies**: 00-variables.sh, 01-utils.sh, 04-github.sh, 06-config-generation.sh

**Exports**:
- `validate_configuration(app_type)`: Validate generated configuration
- `show_final_instructions(app_type, app_name, instance_name, github_repo)`: Display final instructions

**Interface**:
```bash
# Validate generated configuration
validate_configuration(app_type) {
    # Returns 0 if valid, 1 if invalid
}

# Show final instructions
show_final_instructions(app_type, app_name, instance_name, github_repo) {
    # Displays success message and next steps
}
```

### Module 08: Interactive (08-interactive.sh)

**Purpose**: Implement the main interactive workflow and execution logic

**Dependencies**: All previous modules

**Exports**:
- `main()`: Main execution function
- `parse_args(args...)`: Parse command-line arguments
- `show_help()`: Display help text

**Interface**:
```bash
# Main execution function
main() {
    # Orchestrates entire setup workflow
    # Handles both interactive and automated modes
}

# Parse command-line arguments
parse_args(args...) {
    # Parses --interactive, --auto, --aws-region, --app-version, --help
}

# Display help text
show_help() {
    # Shows usage information
}
```

## Data Models

### Configuration State

The system maintains configuration state through environment variables defined in 00-variables.sh:

```bash
# Mode configuration
AUTO_MODE: boolean (default: false)
FULLY_AUTOMATED: boolean (computed)

# AWS configuration
AWS_REGION: string (default: "us-east-1")
AWS_ACCOUNT_ID: string (computed)
APP_VERSION: string (default: "1.0.0")

# Application configuration
APP_TYPE: string (lamp|nodejs|python|react|docker|nginx)
APP_NAME: string
INSTANCE_NAME: string
BLUEPRINT_ID: string (default: "ubuntu-22-04")
BUNDLE_ID: string (default: "micro_3_0")

# Database configuration
DATABASE_TYPE: string (mysql|postgresql|mongodb|none)
DB_EXTERNAL: boolean (default: false)
DB_RDS_NAME: string
DB_NAME: string (default: "app_db")

# Bucket configuration
ENABLE_BUCKET: boolean (default: false)
BUCKET_NAME: string
BUCKET_ACCESS: string (read_only|read_write)
BUCKET_BUNDLE: string (default: "small_1_0")

# GitHub configuration
GITHUB_REPO: string (format: "username/repo")
GITHUB_USERNAME: string
REPO_VISIBILITY: string (private|public)

# Verification configuration
VERIFICATION_ENDPOINT: string
HEALTH_CHECK_ENDPOINT: string
EXPECTED_CONTENT: string
API_ONLY_APP: boolean (default: false)

# AI Recommendations
RECOMMENDED_APP_TYPE: string
RECOMMENDED_DATABASE: string
RECOMMENDED_BUNDLE: string
RECOMMENDED_BUCKET: string
ANALYSIS_CONFIDENCE: integer (0-100)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Module Loading Order Preservation

*For any* execution of setup.sh, modules SHALL be sourced in the exact dependency order (00, 01, 02, 03, 04, 05, 06, 07, 08), and all modules SHALL load successfully before any function is called.

**Validates: Requirements 4.1, 4.2**

### Property 2: Function Availability After Sourcing

*For any* function that exists in the monolithic setup.sh, after sourcing all modules, that function SHALL be available in the shell environment with the same signature and behavior.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 3: Orchestrator Size Constraint

*For any* version of the modularized setup.sh, the line count SHALL be less than 200 lines (excluding blank lines and comments).

**Validates: Requirements 2.1**

### Property 4: Command-Line Interface Preservation

*For any* valid command-line argument accepted by the monolithic setup.sh (--interactive, --auto, --aws-region, --app-version, --help), the modularized setup.sh SHALL accept the same argument and produce equivalent behavior.

**Validates: Requirements 5.1, 5.5**

### Property 5: Environment Variable Preservation

*For any* environment variable used by the monolithic setup.sh, the modularized version SHALL recognize and use that variable with identical semantics.

**Validates: Requirements 3.5, 5.2**

### Property 6: Output File Equivalence

*For any* set of inputs, when both the monolithic and modularized setup.sh are executed with identical inputs, they SHALL produce identical output files (deployment config, workflow files, example apps).

**Validates: Requirements 5.3, 5.6**

### Property 7: Test Suite Compatibility

*For any* test in tests/test-modular-setup.sh, the modularized setup.sh SHALL pass that test without requiring modifications to the test.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

### Property 8: IAM Role Bug Fix Preservation

*For any* execution of create_iam_role_if_needed function, status messages SHALL be redirected to stderr (>&2), and the role ARN SHALL be output to stdout (not stderr).

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 9: Module Self-Containment

*For any* module file, all functions defined in that module SHALL only depend on functions from modules with lower numbers (earlier in the dependency chain) or from the same module.

**Validates: Requirements 4.3, 4.4**

### Property 10: Error Handling Preservation

*For any* error condition that causes the monolithic setup.sh to exit with a specific exit code, the modularized setup.sh SHALL exit with the same exit code.

**Validates: Requirements 8.4, 5.5**

## Error Handling

### Module Loading Errors

If a module fails to source:
1. Display error message: "Failed to load module: {module_name}"
2. Exit with code 1
3. Do not attempt to continue execution

### Missing Function Errors

If a required function is not available after sourcing:
1. Display error message: "Required function not found: {function_name}"
2. Display hint: "Check that all modules loaded successfully"
3. Exit with code 1

### Dependency Errors

If modules are sourced out of order:
1. Functions may fail with "command not found" errors
2. Variables may be undefined
3. This is prevented by strict ordering in orchestrator

### Preserved Error Handling

All error handling from the monolithic script is preserved:
- AWS CLI errors
- GitHub CLI errors
- Git errors
- File creation errors
- Network errors
- Validation errors

## Testing Strategy

### Unit Testing

**Focus**: Individual module functionality
- Test each module can be sourced independently (with dependencies)
- Test utility functions (to_lowercase, to_uppercase)
- Test function availability after sourcing
- Test module syntax validity

**Example Unit Tests**:
```bash
# Test to_lowercase function
test_to_lowercase() {
    source setup/00-variables.sh
    source setup/01-utils.sh
    result=$(to_lowercase "HELLO")
    assert_equals "hello" "$result"
}

# Test module loading
test_module_loading() {
    source setup/00-variables.sh
    source setup/01-utils.sh
    assert_function_exists "to_lowercase"
    assert_function_exists "check_prerequisites"
}
```

### Integration Testing

**Focus**: Module interaction and orchestrator behavior
- Test modules load in correct order
- Test functions can call functions from other modules
- Test orchestrator sources all modules
- Test command-line argument parsing
- Test main execution flow

**Example Integration Tests**:
```bash
# Test orchestrator loads all modules
test_orchestrator_loading() {
    source setup.sh
    assert_function_exists "main"
    assert_function_exists "parse_args"
    assert_function_exists "show_help"
}

# Test module dependency chain
test_module_dependencies() {
    source setup/00-variables.sh
    source setup/01-utils.sh
    source setup/02-ui.sh
    # 02-ui.sh should be able to use functions from 01-utils.sh
    assert_function_exists "get_input"
}
```

### Compatibility Testing

**Focus**: Backward compatibility with existing tests
- Run tests/test-modular-setup.sh without modification
- Verify all tests pass
- Verify test expectations are met

**Test Coverage**:
- Module files exist
- Module syntax valid
- Modules load successfully
- Functions available
- Utility functions work correctly
- Documentation exists
- Module dependencies correct

### Regression Testing

**Focus**: Ensure no behavior changes
- Compare output files between monolithic and modularized versions
- Test with same inputs
- Verify identical results
- Test all app types (lamp, nodejs, python, react, docker, nginx)
- Test all modes (interactive, auto, fully automated)

**Test Scenarios**:
1. Interactive mode with all options
2. Auto mode with defaults
3. Fully automated mode with environment variables
4. Each app type with database
5. Each app type with bucket
6. Each app type without database or bucket
7. Error conditions (missing tools, invalid inputs)

### Property-Based Testing

**Configuration**: Minimum 100 iterations per property test

**Property Test 1: Module Loading Order**
```bash
# Feature: setup-modularization, Property 1: Module Loading Order Preservation
test_module_loading_order() {
    for i in {1..100}; do
        # Source modules in order
        source setup/00-variables.sh
        source setup/01-utils.sh
        source setup/02-ui.sh
        source setup/03-project-analysis.sh
        source setup/04-github.sh
        source setup/05-aws.sh
        source setup/06-config-generation.sh
        source setup/07-deployment.sh
        source setup/08-interactive.sh
        
        # Verify all functions available
        assert_function_exists "to_lowercase"
        assert_function_exists "get_input"
        assert_function_exists "analyze_project_for_recommendations"
        assert_function_exists "create_github_repo_if_needed"
        assert_function_exists "create_iam_role_if_needed"
        assert_function_exists "create_deployment_config"
        assert_function_exists "validate_configuration"
        assert_function_exists "main"
    done
}
```

**Property Test 2: Function Availability**
```bash
# Feature: setup-modularization, Property 2: Function Availability After Sourcing
test_function_availability() {
    # List of all functions from monolithic script
    functions=(
        "to_lowercase" "to_uppercase" "check_prerequisites" "check_git_repo"
        "get_input" "get_yes_no" "select_option" "get_option_description"
        "analyze_project_for_recommendations" "detect_fullstack_react"
        "detect_node_port" "detect_health_endpoints"
        "build_react_client_if_needed" "show_app_deployment_warnings"
        "create_github_repo_if_needed" "setup_workflow_files"
        "create_gitignore" "commit_and_push"
        "create_iam_role_if_needed" "setup_github_oidc"
        "create_deployment_config" "create_github_workflow"
        "create_example_app" "validate_configuration"
        "show_final_instructions" "main" "parse_args" "show_help"
    )
    
    for i in {1..100}; do
        source setup.sh
        for func in "${functions[@]}"; do
            assert_function_exists "$func"
        done
    done
}
```

**Property Test 3: Orchestrator Size**
```bash
# Feature: setup-modularization, Property 3: Orchestrator Size Constraint
test_orchestrator_size() {
    for i in {1..100}; do
        # Count non-blank, non-comment lines
        line_count=$(grep -v '^\s*$' setup.sh | grep -v '^\s*#' | wc -l)
        assert_less_than "$line_count" 200
    done
}
```

**Property Test 4: Command-Line Interface**
```bash
# Feature: setup-modularization, Property 4: Command-Line Interface Preservation
test_cli_interface() {
    args=(
        "--interactive"
        "-i"
        "--auto"
        "--aws-region us-west-2"
        "--app-version 2.0.0"
        "--help"
        "-h"
    )
    
    for i in {1..100}; do
        for arg in "${args[@]}"; do
            # Test that argument is accepted (doesn't error)
            bash setup.sh $arg --help &>/dev/null
            assert_equals 0 $?
        done
    done
}
```

**Property Test 5: IAM Role Bug Fix**
```bash
# Feature: setup-modularization, Property 8: IAM Role Bug Fix Preservation
test_iam_role_bug_fix() {
    for i in {1..100}; do
        source setup/00-variables.sh
        source setup/01-utils.sh
        source setup/05-aws.sh
        
        # Mock AWS commands
        aws() { echo "mock"; }
        export -f aws
        
        # Capture stdout and stderr separately
        output=$(create_iam_role_if_needed "test-role" "user/repo" "123456789012" 2>/dev/null)
        
        # Verify role ARN goes to stdout
        assert_contains "$output" "arn:aws:iam::"
        
        # Verify status messages don't go to stdout
        assert_not_contains "$output" "Creating IAM role"
        assert_not_contains "$output" "IAM role created"
    done
}
```

## Implementation Notes

### Critical Considerations

1. **IAM Role Bug Fix**: The stderr redirection in create_iam_role_if_needed is CRITICAL. Status messages must go to stderr (>&2), and only the role ARN should go to stdout. This allows the caller to capture the ARN without capturing status messages.

2. **Module Loading Order**: The order is critical because later modules depend on functions and variables from earlier modules. The orchestrator must source modules in the exact order specified.

3. **Function Signatures**: All function signatures must remain identical to preserve compatibility with existing code that calls these functions.

4. **Environment Variables**: All environment variables must be defined in 00-variables.sh before any other module is loaded.

5. **Error Handling**: Error handling must be preserved exactly as it exists in the monolithic script to maintain the same exit codes and error messages.

### Migration Strategy

1. **Phase 1**: Create module files with function definitions
   - Copy functions from monolithic script to appropriate modules
   - Add module headers with purpose and dependencies
   - Preserve all comments and documentation

2. **Phase 2**: Create orchestrator
   - Create new setup.sh with module sourcing
   - Move parse_args, show_help, and main to 08-interactive.sh
   - Keep orchestrator minimal (<200 lines)

3. **Phase 3**: Test and validate
   - Run tests/test-modular-setup.sh
   - Fix any issues
   - Verify all tests pass

4. **Phase 4**: Regression testing
   - Test with various inputs
   - Compare outputs with monolithic version
   - Verify identical behavior

### Rollback Plan

If modularization causes issues:
1. Keep monolithic setup.sh as setup-monolithic.sh backup
2. Can quickly revert by renaming files
3. All tests should catch issues before deployment

## Future Enhancements

1. **Module-Level Testing**: Add unit tests for each module
2. **Function Documentation**: Add detailed function documentation
3. **Module Versioning**: Track module versions for compatibility
4. **Lazy Loading**: Load modules only when needed
5. **Module Caching**: Cache module loading for faster execution
