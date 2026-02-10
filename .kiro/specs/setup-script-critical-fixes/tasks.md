# Implementation Plan: Setup Script Critical Fixes

## Overview

This implementation plan addresses three critical issues in the AWS Lightsail deployment setup script: incorrect file placement, deprecated blueprint identifiers, and missing MCP server integration. The tasks are organized to fix each issue systematically while maintaining backward compatibility.

## Tasks

- [x] 1. Fix working directory handling for file creation
  - [x] 1.1 Capture working directory at script start
    - Add `SCRIPT_START_DIR="$(pwd)"` at the beginning of `main()` function in `setup/08-interactive.sh`
    - Export the variable for use in all modules
    - Add validation to ensure directory is writable
    - _Requirements: 1.3, 1.4_
  
  - [x] 1.2 Update file creation functions to use working directory
    - Modify `create_deployment_config()` in `setup/06-config-generation.sh` to use `$SCRIPT_START_DIR`
    - Modify `create_github_workflow()` in `setup/06-config-generation.sh` to use `$SCRIPT_START_DIR`
    - Add `cd "$SCRIPT_START_DIR"` before each file write operation
    - _Requirements: 1.1, 1.2_
  
  - [x] 1.3 Add file creation verification
    - Add validation after each file creation to verify file exists
    - Display full absolute path of created files in success messages
    - Add error handling with descriptive messages if file creation fails
    - _Requirements: 1.4, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 1.4 Write property test for working directory consistency
    - **Property 1: Working Directory Consistency**
    - **Validates: Requirements 1.1, 1.2, 1.3**

- [x] 2. Update blueprint identifiers to valid AWS Lightsail format
  - [x] 2.1 Update default blueprint in variables module
    - Change `BLUEPRINT_ID=${BLUEPRINT_ID:-ubuntu-22-04}` to `BLUEPRINT_ID=${BLUEPRINT_ID:-ubuntu_22_04}` in `setup/00-variables.sh`
    - _Requirements: 2.2, 2.5_
  
  - [x] 2.2 Update blueprint arrays and validation in interactive module
    - Change blueprint array from `("ubuntu-22-04" "ubuntu-20-04" "amazon-linux-2023")` to `("ubuntu_22_04" "ubuntu_24_04" "amazon_linux_2023")` in `setup/08-interactive.sh`
    - Update validation regex from `^(ubuntu-22-04|ubuntu-20-04|amazon-linux-2023)$` to `^(ubuntu_22_04|ubuntu_24_04|amazon_linux_2023)$`
    - Update error messages to show correct format with underscores
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.7_
  
  - [x] 2.3 Update blueprint display names in UI module
    - Update display name mappings in `get_option_description()` function in `setup/02-ui.sh`
    - Change "ubuntu-22-04" to "ubuntu_22_04" with display name "Ubuntu 22.04 LTS (Recommended)"
    - Remove "ubuntu-20-04" entry completely
    - Add "ubuntu_24_04" with display name "Ubuntu 24.04 LTS (Newest)"
    - Update "amazon-linux-2023" to "amazon_linux_2023"
    - _Requirements: 2.1, 2.3, 2.7_
  
  - [ ]* 2.4 Write property test for blueprint format validity
    - **Property 2: Blueprint Identifier Format Validity**
    - **Validates: Requirements 2.3, 2.4, 2.5, 2.6**
  
  - [ ]* 2.5 Write property test for invalid blueprint rejection
    - **Property 3: Blueprint Validation Rejection**
    - **Validates: Requirements 2.1, 2.4**

- [x] 3. Integrate MCP server for intelligent recommendations
  - [x] 3.1 Add MCP server integration function
    - Create `analyze_project_with_mcp()` function in `setup/03-project-analysis.sh`
    - Implement MCP server command invocation with error handling
    - Add JSON response parsing using `jq`
    - Implement timeout handling (30 second timeout)
    - Return success/failure status
    - _Requirements: 3.1, 3.4, 3.8_
  
  - [x] 3.2 Update project analysis to use MCP server
    - Modify `analyze_project_for_recommendations()` in `setup/03-project-analysis.sh`
    - Call `analyze_project_with_mcp()` first, fall back to file-based detection on failure
    - Parse MCP response and set recommendation variables (RECOMMENDED_APP_TYPE, RECOMMENDED_DATABASE, RECOMMENDED_BUNDLE, RECOMMENDED_BUCKET, ANALYSIS_CONFIDENCE)
    - Add confidence score display in output
    - _Requirements: 3.1, 3.2, 3.5, 3.7_
  
  - [x] 3.3 Update UI to highlight AI recommendations
    - Modify `select_option()` function in `setup/02-ui.sh` to accept recommendation type parameter
    - Add logic to mark AI-recommended options with star (★) indicator
    - Automatically set AI-recommended option as default selection
    - Update all `select_option()` calls in `setup/08-interactive.sh` to pass recommendation type
    - _Requirements: 3.3, 3.6_
  
  - [ ]* 3.4 Write property test for MCP server graceful degradation
    - **Property 4: MCP Server Graceful Degradation**
    - **Validates: Requirements 3.4, 3.8**
  
  - [ ]* 3.5 Write property test for recommendation highlighting
    - **Property 5: Recommendation Highlighting Consistency**
    - **Validates: Requirements 3.3, 3.6**

- [x] 4. Add comprehensive error handling and validation
  - [x] 4.1 Add working directory validation
    - Check if `$SCRIPT_START_DIR` is writable at script start
    - Display error message with directory path if not writable
    - Exit with code 1 on validation failure
    - _Requirements: 1.3, 5.4_
  
  - [x] 4.2 Add file creation error handling
    - Wrap all file creation operations with error checking
    - Display error messages with expected file paths on failure
    - Exit with non-zero status code on file creation failure
    - _Requirements: 5.3, 5.4_
  
  - [x] 4.3 Add MCP server error handling
    - Add timeout handling for MCP server calls
    - Log informational messages when MCP server is unavailable
    - Ensure script continues with file-based detection on MCP errors
    - _Requirements: 3.4, 3.8_
  
  - [ ]* 4.4 Write property test for file creation verification
    - **Property 6: File Creation Verification**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

- [x] 5. Ensure backward compatibility
  - [x] 5.1 Test with existing deployment configurations
    - Verify script works with existing deployment-*.config.yml files
    - Ensure old blueprint format in existing configs doesn't break script
    - Test automated mode with all environment variables
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 5.2 Write property test for backward compatibility
    - **Property 7: Backward Compatibility Preservation**
    - **Validates: Requirements 4.1, 4.3**
  
  - [ ]* 5.3 Write integration tests for complete workflow
    - Test end-to-end setup with all three fixes
    - Test interactive mode with MCP recommendations
    - Test automated mode with environment variables
    - Test fallback behavior when MCP server unavailable

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- MCP server integration includes graceful degradation for environments without MCP
- Blueprint format changes maintain backward compatibility with existing configs
- File creation fixes ensure deployment files are always in the correct location
