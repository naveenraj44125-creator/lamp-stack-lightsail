# Requirements Document: Setup Script Modularization

## Introduction

This document specifies the requirements for modularizing the monolithic setup.sh script (3,953 lines) into a maintainable, modular architecture using the existing setup/ directory structure. The goal is to transform setup.sh into a lightweight orchestrator that sources and calls functions from focused, single-responsibility modules while preserving ALL existing functionality.

## Glossary

- **Setup_Script**: The main setup.sh orchestrator file that sources modules and coordinates the deployment setup workflow
- **Module**: A self-contained bash script file in the setup/ directory that provides specific functionality
- **Orchestrator**: The main setup.sh file that coordinates module loading and function execution
- **Function**: A bash function that performs a specific task
- **Skeleton_Module**: An existing module file in setup/ that contains minimal or no implementation
- **Monolithic_Script**: The current 3,953-line setup.sh file with all functionality embedded
- **Source**: The bash `source` command that loads a module's functions into the current shell environment
- **IAM_Role_Bug_Fix**: The critical stderr redirection fix in 05-aws.sh for create_iam_role_if_needed function

## Requirements

### Requirement 1: Module Structure

**User Story:** As a developer, I want the setup script split into logical modules, so that I can easily find and modify specific functionality.

#### Acceptance Criteria

1. THE System SHALL organize code into these modules in the setup/ directory:
   - 00-variables.sh (environment variables and configuration)
   - 01-utils.sh (utility functions: to_lowercase, to_uppercase, check_prerequisites, check_git_repo)
   - 02-ui.sh (user interaction functions: get_input, get_yes_no, select_option, get_option_description)
   - 03-project-analysis.sh (project analysis and detection functions)
   - 04-github.sh (GitHub repository and workflow management)
   - 05-aws.sh (AWS IAM and OIDC setup)
   - 06-config-generation.sh (deployment config and workflow file generation)
   - 07-deployment.sh (deployment orchestration and validation)
   - 08-interactive.sh (interactive mode and main execution flow)

2. WHEN a module is created, THE System SHALL ensure it contains only functions related to its specific responsibility

3. WHEN organizing functions, THE System SHALL group related functions together in the same module

4. THE System SHALL maintain the existing module file structure in the setup/ directory

5. THE System SHALL preserve the IAM_Role_Bug_Fix in 05-aws.sh (stderr redirection for status messages in create_iam_role_if_needed)

### Requirement 2: Orchestrator Transformation

**User Story:** As a developer, I want setup.sh to be a lightweight orchestrator, so that the codebase is easier to navigate and maintain.

#### Acceptance Criteria

1. THE Setup_Script SHALL be reduced to under 200 lines of code

2. THE Setup_Script SHALL source all required modules from the setup/ directory in the correct dependency order

3. THE Setup_Script SHALL contain only:
   - Module sourcing logic
   - Command-line argument parsing
   - Main execution entry point
   - Help text display

4. THE Setup_Script SHALL NOT contain function implementations (except parse_args, show_help, and main)

5. WHEN the Setup_Script is executed, THE System SHALL load all modules before executing any functions

6. THE Setup_Script SHALL maintain the same command-line interface as the Monolithic_Script

### Requirement 3: Function Preservation

**User Story:** As a user, I want all existing functionality preserved, so that the modularized version works exactly like the original.

#### Acceptance Criteria

1. THE System SHALL preserve ALL functions from the Monolithic_Script without modification to their logic

2. WHEN a function is moved to a module, THE System SHALL maintain its exact implementation including:
   - Function signature
   - Internal logic
   - Variable names
   - Error handling
   - Return values

3. THE System SHALL preserve all function dependencies and calling relationships

4. THE System SHALL maintain the exact same behavior for all user-facing features

5. THE System SHALL preserve all environment variable handling

6. THE System SHALL preserve the IAM_Role_Bug_Fix (stderr redirection in create_iam_role_if_needed function)

### Requirement 4: Module Dependencies

**User Story:** As a developer, I want modules to have clear dependencies, so that I understand the loading order and relationships.

#### Acceptance Criteria

1. THE Setup_Script SHALL source modules in this order:
   - 00-variables.sh (no dependencies)
   - 01-utils.sh (depends on 00-variables.sh)
   - 02-ui.sh (depends on 00-variables.sh, 01-utils.sh)
   - 03-project-analysis.sh (depends on 00-variables.sh, 01-utils.sh)
   - 04-github.sh (depends on 00-variables.sh, 01-utils.sh)
   - 05-aws.sh (depends on 00-variables.sh, 01-utils.sh)
   - 06-config-generation.sh (depends on 00-variables.sh, 01-utils.sh, 03-project-analysis.sh)
   - 07-deployment.sh (depends on 00-variables.sh, 01-utils.sh, 04-github.sh, 06-config-generation.sh)
   - 08-interactive.sh (depends on all previous modules)

2. WHEN a module is sourced, THE System SHALL ensure all its dependencies are already loaded

3. THE System SHALL NOT create circular dependencies between modules

4. WHEN a module uses a function from another module, THE System SHALL ensure that dependency is documented

### Requirement 5: Backward Compatibility

**User Story:** As a user, I want the modularized script to work exactly like the original, so that I don't need to change my workflow.

#### Acceptance Criteria

1. THE Setup_Script SHALL accept the same command-line arguments as the Monolithic_Script:
   - --interactive, -i
   - --auto
   - --aws-region REGION
   - --app-version VERSION
   - --help, -h

2. THE Setup_Script SHALL support the same environment variables as the Monolithic_Script

3. THE Setup_Script SHALL produce the same output files as the Monolithic_Script

4. THE Setup_Script SHALL display the same user interface and prompts as the Monolithic_Script

5. THE Setup_Script SHALL maintain the same exit codes and error handling as the Monolithic_Script

6. WHEN executed with the same inputs, THE Setup_Script SHALL produce identical results to the Monolithic_Script

### Requirement 6: Test Compatibility

**User Story:** As a developer, I want all existing tests to pass, so that I can verify the modularization is correct.

#### Acceptance Criteria

1. THE System SHALL pass all tests in tests/test-modular-setup.sh without modification

2. WHEN tests check for module files, THE System SHALL have all required module files present

3. WHEN tests check for function availability, THE System SHALL make all functions available after sourcing

4. WHEN tests check module syntax, THE System SHALL have valid bash syntax in all modules

5. WHEN tests check module loading order, THE System SHALL load modules in the correct dependency order

6. WHEN tests check utility functions, THE System SHALL preserve the exact behavior of to_lowercase and to_uppercase

### Requirement 7: Code Organization

**User Story:** As a developer, I want clear code organization, so that I can quickly find and modify specific functionality.

#### Acceptance Criteria

1. WHEN a module contains functions, THE System SHALL group related functions together

2. WHEN a module is opened, THE System SHALL have a header comment describing its purpose and dependencies

3. THE System SHALL maintain consistent coding style across all modules

4. THE System SHALL preserve all existing comments and documentation

5. WHEN a function is complex, THE System SHALL preserve its internal comments

### Requirement 8: Error Handling

**User Story:** As a user, I want clear error messages, so that I can troubleshoot issues quickly.

#### Acceptance Criteria

1. WHEN a module fails to load, THE Setup_Script SHALL display an error message indicating which module failed

2. WHEN a required function is missing, THE Setup_Script SHALL display an error message indicating which function is missing

3. THE System SHALL preserve all existing error handling from the Monolithic_Script

4. WHEN an error occurs, THE Setup_Script SHALL exit with the same exit code as the Monolithic_Script

5. THE System SHALL preserve all existing error messages and warnings

### Requirement 9: Documentation

**User Story:** As a developer, I want clear documentation, so that I can understand the modular structure.

#### Acceptance Criteria

1. THE System SHALL maintain the existing documentation files in setup/:
   - README.md
   - QUICK_REFERENCE.md
   - IMPROVEMENTS.md
   - SUMMARY.md

2. WHEN a module is created, THE System SHALL include a header comment describing:
   - Module purpose
   - Dependencies on other modules
   - Key functions provided

3. THE Setup_Script SHALL maintain the existing --help output

4. THE System SHALL preserve all existing inline documentation

### Requirement 10: Critical Bug Fixes

**User Story:** As a developer, I want critical bug fixes preserved, so that the modularized version doesn't reintroduce known issues.

#### Acceptance Criteria

1. THE System SHALL preserve the IAM_Role_Bug_Fix in 05-aws.sh

2. WHEN create_iam_role_if_needed function outputs status messages, THE System SHALL redirect them to stderr (>&2)

3. WHEN create_iam_role_if_needed function returns the role ARN, THE System SHALL output it to stdout (not stderr)

4. THE System SHALL preserve all other bug fixes present in the Monolithic_Script

5. WHEN moving code to modules, THE System SHALL NOT introduce new bugs or regressions
