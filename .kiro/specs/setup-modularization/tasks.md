# Implementation Plan: Setup Script Modularization

## Overview

This plan transforms the monolithic 3,953-line setup.sh into a modular architecture with 9 focused modules and a lightweight orchestrator. The implementation preserves ALL existing functionality while improving maintainability and testability.

## Tasks

- [ ] 1. Backup and prepare for modularization
  - Create backup of current setup.sh as setup-monolithic.sh
  - Verify all existing tests pass with current setup.sh
  - Document current line count and structure
  - _Requirements: 3.1, 5.6_

- [ ] 2. Create Module 00: Variables (00-variables.sh)
  - [ ] 2.1 Extract all variable definitions from setup.sh
    - Copy color variables (RED, GREEN, YELLOW, BLUE, NC)
    - Copy configuration variables (AUTO_MODE, AWS_REGION, APP_VERSION)
    - Copy MCP recommendation variables
    - Copy fully automated mode variables
    - Copy verification endpoint variables
    - Add module header comment describing purpose
    - _Requirements: 1.1, 1.2, 3.5, 7.2_
  
  - [ ]* 2.2 Write unit test for variables module
    - Test module can be sourced without errors
    - Test all variables are defined with correct defaults
    - _Requirements: 6.3_

- [ ] 3. Create Module 01: Utilities (01-utils.sh)
  - [ ] 3.1 Extract utility functions from setup.sh
    - Copy to_lowercase() function
    - Copy to_uppercase() function
    - Copy check_prerequisites() function
    - Copy check_git_repo() function
    - Add module header with dependencies: 00-variables.sh
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 7.2_
  
  - [ ]* 3.2 Write unit tests for utility functions
    - Test to_lowercase("HELLO") returns "hello"
    - Test to_uppercase("hello") returns "HELLO"
    - Test check_prerequisites() validates required tools
    - Test check_git_repo() detects .git directory
    - _Requirements: 6.6_

- [ ] 4. Create Module 02: UI (02-ui.sh)
  - [ ] 4.1 Extract UI functions from setup.sh
    - Copy get_input() function
    - Copy get_yes_no() function
    - Copy select_option() function
    - Copy get_option_description() function
    - Add module header with dependencies: 00-variables.sh, 01-utils.sh
    - Preserve AUTO_MODE handling in all functions
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 7.2_
  
  - [ ]* 4.2 Write unit tests for UI functions
    - Test get_input() returns default in AUTO_MODE
    - Test get_yes_no() returns default in AUTO_MODE
    - Test select_option() returns default in AUTO_MODE
    - Test get_option_description() returns correct descriptions
    - _Requirements: 6.2_

- [ ] 5. Create Module 03: Project Analysis (03-project-analysis.sh)
  - [ ] 5.1 Extract project analysis functions from setup.sh
    - Copy analyze_project_for_recommendations() function
    - Copy detect_fullstack_react() function
    - Copy detect_node_port() function
    - Copy detect_health_endpoints() function
    - Copy build_react_client_if_needed() function
    - Copy show_app_deployment_warnings() function
    - Add module header with dependencies: 00-variables.sh, 01-utils.sh
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 7.2_
  
  - [ ]* 5.2 Write unit tests for project analysis
    - Test detect_node_port() returns correct port
    - Test detect_fullstack_react() detects client/ directory
    - Test detect_health_endpoints() finds endpoints in code
    - _Requirements: 6.2_

- [ ] 6. Create Module 04: GitHub (04-github.sh)
  - [ ] 6.1 Extract GitHub functions from setup.sh
    - Copy create_github_repo_if_needed() function
    - Copy setup_workflow_files() function
    - Copy create_gitignore() function
    - Copy commit_and_push() function
    - Add module header with dependencies: 00-variables.sh, 01-utils.sh
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 7.2_
  
  - [ ]* 6.2 Write unit tests for GitHub functions
    - Test setup_workflow_files() creates .github/workflows/
    - Test create_gitignore() creates .gitignore with correct patterns
    - _Requirements: 6.2_

- [ ] 7. Create Module 05: AWS (05-aws.sh)
  - [x] 7.1 Extract AWS functions from setup.sh
    - Copy create_iam_role_if_needed() function
    - **CRITICAL**: Preserve stderr redirection (>&2) for status messages
    - **CRITICAL**: Ensure role ARN goes to stdout (not stderr)
    - Copy setup_github_oidc() function
    - Add module header with dependencies: 00-variables.sh, 01-utils.sh
    - Add comment documenting IAM_Role_Bug_Fix
    - _Requirements: 1.1, 1.2, 1.5, 3.1, 3.2, 3.6, 7.2, 10.1, 10.2, 10.3_
  
  - [ ]* 7.2 Write unit test for IAM role bug fix
    - Test create_iam_role_if_needed() outputs role ARN to stdout
    - Test status messages go to stderr (not stdout)
    - Mock AWS CLI commands for testing
    - _Requirements: 10.1, 10.2, 10.3_

- [ ] 8. Create Module 06: Config Generation (06-config-generation.sh)
  - [ ] 8.1 Extract config generation functions from setup.sh
    - Copy create_deployment_config() function (large function ~500 lines)
    - Copy create_github_workflow() function
    - Copy create_example_app() function (large function ~800 lines)
    - Add module header with dependencies: 00-variables.sh, 01-utils.sh, 03-project-analysis.sh
    - Preserve all app type handling (lamp, nodejs, python, react, docker, nginx)
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 7.2_
  
  - [ ]* 8.2 Write unit tests for config generation
    - Test create_deployment_config() creates valid YAML
    - Test create_github_workflow() creates valid workflow file
    - Test create_example_app() creates app-specific files
    - _Requirements: 6.2_

- [ ] 9. Create Module 07: Deployment (07-deployment.sh)
  - [ ] 9.1 Extract deployment functions from setup.sh
    - Copy validate_configuration() function
    - Copy show_final_instructions() function
    - Add module header with dependencies: 00-variables.sh, 01-utils.sh, 04-github.sh, 06-config-generation.sh
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 7.2_
  
  - [ ]* 9.2 Write unit tests for deployment functions
    - Test validate_configuration() validates YAML syntax
    - Test validate_configuration() checks required sections
    - _Requirements: 6.2_

- [ ] 10. Create Module 08: Interactive (08-interactive.sh)
  - [ ] 10.1 Extract main execution functions from setup.sh
    - Copy main() function (large function ~600 lines)
    - Copy parse_args() function
    - Copy show_help() function
    - Add module header with dependencies: all previous modules
    - Preserve all workflow logic (interactive, auto, fully automated)
    - Preserve all user prompts and menus
    - Preserve all error handling
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.4, 7.2, 8.3, 8.5_
  
  - [ ]* 10.2 Write unit tests for interactive functions
    - Test parse_args() handles all command-line arguments
    - Test show_help() displays correct help text
    - _Requirements: 5.1, 6.2_

- [ ] 11. Create lightweight orchestrator (setup.sh)
  - [ ] 11.1 Create new setup.sh with module sourcing
    - Add shebang (#!/bin/bash)
    - Calculate SCRIPT_DIR for relative module paths
    - Source modules in dependency order:
      - 00-variables.sh
      - 01-utils.sh
      - 02-ui.sh
      - 03-project-analysis.sh
      - 04-github.sh
      - 05-aws.sh
      - 06-config-generation.sh
      - 07-deployment.sh
      - 08-interactive.sh
    - Add error handling for module loading failures
    - Call parse_args "$@"
    - Call main
    - Verify line count < 200 lines
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2_
  
  - [ ]* 11.2 Write unit test for orchestrator
    - Test orchestrator sources all modules
    - Test orchestrator line count < 200
    - Test all functions available after sourcing
    - _Requirements: 2.1, 6.2_

- [x] 12. Checkpoint - Run existing test suite
  - Run tests/test-modular-setup.sh
  - Verify all tests pass without modification
  - Fix any issues found
  - Ensure all tests pass, ask the user if questions arise.
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ] 13. Regression testing
  - [ ] 13.1 Test interactive mode
    - Run setup.sh in interactive mode
    - Verify all prompts appear correctly
    - Verify AI recommendations work
    - Verify all app types work (lamp, nodejs, python, react, docker, nginx)
    - _Requirements: 5.4, 5.6_
  
  - [ ] 13.2 Test auto mode
    - Run setup.sh with --auto flag
    - Verify defaults are used
    - Verify no prompts appear
    - _Requirements: 5.1, 5.6_
  
  - [ ] 13.3 Test fully automated mode
    - Set all environment variables (APP_TYPE, APP_NAME, etc.)
    - Run setup.sh
    - Verify no prompts appear
    - Verify correct configuration generated
    - _Requirements: 5.2, 5.6_
  
  - [ ] 13.4 Test all app types
    - Test lamp app type
    - Test nodejs app type
    - Test python app type
    - Test react app type
    - Test docker app type
    - Test nginx app type
    - Verify correct config files generated for each
    - _Requirements: 5.3, 5.6_
  
  - [ ] 13.5 Test database configurations
    - Test with mysql (local and RDS)
    - Test with postgresql (local and RDS)
    - Test with mongodb (local only)
    - Test with no database
    - _Requirements: 5.3, 5.6_
  
  - [ ] 13.6 Test bucket configurations
    - Test with bucket enabled
    - Test with bucket disabled
    - Test different bucket sizes
    - Test different access levels
    - _Requirements: 5.3, 5.6_
  
  - [ ]* 13.7 Compare outputs with monolithic version
    - Run both versions with identical inputs
    - Compare deployment config files
    - Compare workflow files
    - Compare example app files
    - Verify outputs are identical
    - _Requirements: 5.6_

- [ ] 14. Error handling verification
  - [ ] 14.1 Test module loading errors
    - Temporarily rename a module file
    - Run setup.sh
    - Verify error message appears
    - Verify script exits with code 1
    - Restore module file
    - _Requirements: 8.1_
  
  - [ ] 14.2 Test missing prerequisites
    - Mock missing tool (e.g., gh command)
    - Run setup.sh
    - Verify error message appears
    - Verify script exits with code 1
    - _Requirements: 8.3, 8.4_
  
  - [ ] 14.3 Test invalid inputs
    - Test with invalid app type
    - Test with invalid bundle ID
    - Test with invalid database type
    - Verify error messages appear
    - Verify script exits with code 1
    - _Requirements: 8.3, 8.4, 8.5_

- [ ] 15. Documentation updates
  - [ ] 15.1 Update setup/README.md
    - Document new modular structure
    - Document module dependencies
    - Document how to add new modules
    - _Requirements: 9.1, 9.2_
  
  - [ ] 15.2 Update setup/QUICK_REFERENCE.md
    - Add module reference section
    - Document key functions in each module
    - _Requirements: 9.1, 9.2_
  
  - [ ] 15.3 Update setup/IMPROVEMENTS.md
    - Document modularization improvements
    - Document benefits of new structure
    - _Requirements: 9.1_
  
  - [ ] 15.4 Update setup/SUMMARY.md
    - Update with new module structure
    - Document orchestrator design
    - _Requirements: 9.1_

- [ ] 16. Final checkpoint - Complete validation
  - Run all tests one final time
  - Verify line count of setup.sh < 200
  - Verify all modules have proper headers
  - Verify all documentation is updated
  - Verify IAM role bug fix is preserved
  - Verify backward compatibility
  - Ensure all tests pass, ask the user if questions arise.
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 10.5_

## Notes

- Tasks marked with `*` are optional test-related sub-tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- The IAM role bug fix (stderr redirection) is CRITICAL and must be preserved
- Module loading order is CRITICAL and must be maintained
- All existing functionality must be preserved - no behavior changes allowed
- The orchestrator must be under 200 lines
- All existing tests must pass without modification
