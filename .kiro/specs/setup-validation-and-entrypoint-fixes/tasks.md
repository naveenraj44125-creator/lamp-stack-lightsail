# Implementation Plan: Setup Validation and Entry Point Fixes

## Overview

This implementation plan addresses two critical issues in the AWS Lightsail deployment setup script:
1. Add S3 bucket name validation against AWS naming rules
2. Implement smart entry point detection to avoid creating redundant files

The implementation will enhance three existing modules (01-utils.sh, 03-project-analysis.sh, 08-interactive.sh) and modify the template creation logic in 06-config-generation.sh.

## Tasks

- [x] 1. Implement S3 bucket name validation function
  - [x] 1.1 Add validate_bucket_name() function to setup/01-utils.sh
    - Implement all AWS S3 naming rule checks (length, characters, format)
    - Return 0 for valid names, 1 for invalid names
    - Output descriptive error messages to stderr for invalid names
    - Include examples of valid bucket names in error messages
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 1.2 Write property test for bucket name validation
    - **Property 1: Bucket Name Validation Completeness**
    - **Property 2: Valid Bucket Names Are Accepted**
    - **Property 3: Invalid Bucket Names Are Rejected**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11**
  
  - [ ]* 1.3 Write unit tests for bucket name validation edge cases
    - Test valid names: "my-bucket", "app-bucket-2024", "test.bucket.name"
    - Test invalid uppercase, underscores, length violations
    - Test invalid start/end characters, consecutive periods, IP format
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_

- [x] 2. Implement entry point detection function
  - [x] 2.1 Add detect_entry_point() function to setup/03-project-analysis.sh
    - Accept application type as parameter (nodejs, python, lamp)
    - Search for entry points in priority order for each app type
    - Return path to first detected entry point or empty string
    - Output detection message when entry point is found
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_
  
  - [ ]* 2.2 Write property test for entry point detection
    - **Property 4: Entry Point Detection Finds Existing Files**
    - **Property 5: Entry Point Detection Returns Empty for Missing Files**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.2, 4.3, 4.4, 4.5**
  
  - [ ]* 2.3 Write unit tests for entry point detection scenarios
    - Test Node.js entry point priority (server.js > index.js > main.js)
    - Test Python entry point priority (app.py > main.py > server.py)
    - Test PHP entry point priority (index.php > app.php > public/index.php)
    - Test no entry points found for each app type
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.2, 4.3, 4.4, 4.5_

- [x] 3. Integrate validation into interactive mode
  - [x] 3.1 Update bucket name input in setup/08-interactive.sh (line ~561)
    - Add validation loop that re-prompts on invalid input
    - Call validate_bucket_name() before accepting bucket name
    - Display validation errors in red color
    - Continue loop until valid bucket name is provided
    - _Requirements: 1.1, 5.1, 5.2, 5.3, 5.4, 6.5_
  
  - [x] 3.2 Add validation for automated mode in setup/08-interactive.sh (line ~513)
    - Validate BUCKET_NAME environment variable if ENABLE_BUCKET is true
    - Exit with status code 1 if validation fails
    - Display error message with instructions for setting correct variable
    - _Requirements: 1.12, 5.5, 5.6, 6.5_
  
  - [ ]* 3.3 Write integration tests for interactive mode validation
    - Test invalid then valid bucket name input flow
    - Test error message display and re-prompting
    - Test automated mode validation failure and exit
    - _Requirements: 5.4, 5.5, 5.6_

- [ ] 4. Checkpoint - Ensure validation tests pass
  - Ensure all validation tests pass, ask the user if questions arise.

- [x] 5. Integrate entry point detection into template creation
  - [x] 5.1 Update create_example_app() in setup/06-config-generation.sh for Node.js
    - Call detect_entry_point("nodejs") before creating templates
    - Skip app.js creation if entry point is detected
    - Display detection message when entry point is found
    - Only create templates when no entry point exists
    - _Requirements: 2.1, 2.10, 2.11_
  
  - [x] 5.2 Update create_example_app() in setup/06-config-generation.sh for Python
    - Call detect_entry_point("python") before creating templates
    - Skip app.py creation if entry point is detected
    - Display detection message when entry point is found
    - Only create templates when no entry point exists
    - _Requirements: 3.1, 3.8_
  
  - [x] 5.3 Update create_example_app() in setup/06-config-generation.sh for PHP
    - Call detect_entry_point("lamp") before creating templates
    - Skip index.php creation if entry point is detected
    - Display detection message when entry point is found
    - Only create templates when no entry point exists
    - _Requirements: 4.1, 4.6_
  
  - [ ]* 5.4 Write property test for template creation logic
    - **Property 6: Template Creation Skipped When Entry Point Exists**
    - **Validates: Requirements 2.1, 2.10, 2.11, 3.1, 3.8, 4.1, 4.6**
  
  - [ ]* 5.5 Write integration tests for template creation
    - Test template creation skipped when entry point exists
    - Test template creation proceeds when no entry point exists
    - Test for each application type (nodejs, python, lamp)
    - _Requirements: 2.1, 2.9, 2.10, 2.11, 3.1, 3.7, 3.8, 4.1, 4.5, 4.6_

- [x] 6. Verify backward compatibility
  - [x] 6.1 Test existing workflows with valid inputs
    - Run setup script in interactive mode with valid bucket names
    - Run setup script in automated mode with valid environment variables
    - Verify behavior is identical to previous version
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [x] 6.2 Test with projects that have no entry points
    - Verify templates are still created when no entry points exist
    - Verify user experience is unchanged for new projects
    - _Requirements: 8.4_
  
  - [x] 6.3 Verify all command-line options still work
    - Test --interactive, --auto, --aws-region, --app-version flags
    - Verify no breaking changes to CLI interface
    - _Requirements: 8.5_

- [ ] 7. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- Backward compatibility is critical - existing users should not experience breaking changes
