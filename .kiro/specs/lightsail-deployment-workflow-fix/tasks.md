# Implementation Plan: Lightsail Deployment Workflow Fix

## Overview

This implementation plan creates a diagnostic tool that investigates GitHub Actions workflow failures for AWS Lightsail deployments. The tool retrieves workflow logs, diagnoses failures, and applies automated fixes. It leverages existing troubleshooting scripts and integrates with GitHub CLI and AWS APIs.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create `investigate-workflow.py` as main entry point
  - Create supporting modules: `log_retriever.py`, `diagnostic_engine.py`, `fix_applier.py`
  - Add dependencies to `requirements.txt`: boto3, pyyaml, hypothesis (for testing)
  - _Requirements: 10.5_

- [ ] 2. Implement Log Retriever module
  - [x] 2.1 Implement GitHub CLI integration
    - Create `LogRetriever` class with `fetch_logs()` method
    - Use subprocess to call `gh run view <run-id> --log`
    - Handle GitHub CLI not installed/authenticated errors
    - _Requirements: 1.1, 1.5_
  
  - [x] 2.2 Implement log parsing
    - Create `parse_logs()` method to parse raw logs into structured format
    - Create data classes: `WorkflowLogs`, `JobLog`, `StepLog`
    - Parse job names, step names, and output
    - _Requirements: 1.2_
  
  - [x] 2.3 Implement failure point identification
    - Create `identify_failure_point()` method
    - Identify which job failed (load-config, test, pre-steps, post-steps, verification)
    - Identify which step within the job failed
    - Create `FailurePoint` data class
    - _Requirements: 1.3, 2.2_
  
  - [x] 2.4 Implement error message extraction
    - Create `extract_error_messages()` method
    - Use regex patterns to match common errors (SSH timeout, HTTP error, npm error)
    - Extract stack traces and error details
    - _Requirements: 1.4, 2.3, 2.4, 2.5_
  
  - [ ]* 2.5 Write property test for log retrieval
    - **Property 1: Log Retrieval Completeness**
    - **Validates: Requirements 1.1, 1.2**
  
  - [ ]* 2.6 Write unit tests for log parsing
    - Test parsing successful workflow logs
    - Test parsing failed workflow logs
    - Test error message extraction
    - _Requirements: 1.2, 1.3_

- [ ] 3. Implement Diagnostic Engine module
  - [x] 3.1 Implement instance state checking
    - Create `DiagnosticEngine` class
    - Implement `check_instance_state()` using boto3 Lightsail client
    - Create `InstanceState` data class
    - Check if instance exists, get state, public IP, blueprint_id
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  
  - [x] 3.2 Implement SSH connectivity testing
    - Implement `test_ssh_connectivity()` method
    - Use existing `LightsailBase` class from workflows/lightsail_common.py
    - Implement retry logic with exponential backoff (up to 3 retries)
    - Create `SSHStatus` data class
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 3.3 Implement application diagnostics
    - Implement `run_application_diagnostics()` method
    - Check Node.js version, npm installation, PM2 status
    - Retrieve application logs (last 50 lines)
    - Test localhost connectivity
    - Create `AppDiagnostics` data class
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 3.4 Implement health endpoint testing
    - Implement `test_health_endpoints()` method
    - Make HTTP requests to configured endpoints
    - Retry up to 10 times with 15-second intervals
    - Check HTTP status code and response body
    - Create `EndpointResults` data class
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 3.5 Implement failure diagnosis logic
    - Implement `diagnose_failure()` method
    - Map failure points to root causes
    - Generate recommended fixes based on diagnosis
    - Create `Diagnosis` data class with confidence score
    - _Requirements: 2.1, 2.5_
  
  - [ ]* 3.6 Write property test for SSH retry logic
    - **Property 3: SSH Connectivity Retry**
    - **Validates: Requirements 4.4**
  
  - [ ]* 3.7 Write property test for health endpoint retry
    - **Property 6: Health Endpoint Retry Behavior**
    - **Validates: Requirements 6.2**
  
  - [ ]* 3.8 Write unit tests for diagnostic engine
    - Test instance state checking
    - Test SSH connectivity with mocked connections
    - Test application diagnostics
    - _Requirements: 3.1, 4.1, 5.1_

- [x] 4. Checkpoint - Ensure diagnostic components work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Fix Applier module
  - [x] 5.1 Implement blueprint_id fix
    - Create `FixApplier` class
    - Implement `fix_blueprint_id()` method
    - Convert underscores to hyphens in blueprint_id
    - Update deployment config file
    - _Requirements: 8.1_
  
  - [~] 5.2 Implement port configuration fix
    - Implement `fix_port_configuration()` method
    - Detect port from application code (parse server files)
    - Update verification port, firewall rules, and monitoring port
    - _Requirements: 8.2_
  
  - [~] 5.3 Implement health endpoint addition
    - Implement `add_health_endpoint()` method
    - Add default `/api/health` endpoint to application code
    - Handle different application types (Express, Flask, etc.)
    - _Requirements: 8.3_
  
  - [~] 5.4 Implement firewall rules fix
    - Implement `fix_firewall_rules()` method
    - Add application port to allowed_ports list
    - Update deployment config file
    - _Requirements: 8.4_
  
  - [~] 5.5 Implement apply_all_fixes method
    - Implement `apply_all_fixes()` method
    - Apply fixes based on diagnosis recommendations
    - Track which fixes succeeded/failed
    - Create `FixReport` data class
    - _Requirements: 8.5_
  
  - [ ]* 5.6 Write property test for fix idempotence
    - **Property 7: Fix Application Idempotence**
    - **Validates: Requirements 8.1, 8.2, 8.4**
  
  - [ ]* 5.7 Write unit tests for fix applier
    - Test blueprint_id conversion
    - Test port configuration updates
    - Test firewall rule additions
    - _Requirements: 8.1, 8.2, 8.4_

- [ ] 6. Implement Configuration Validator
  - [~] 6.1 Implement YAML validation
    - Create `ConfigValidator` class
    - Implement `validate_yaml_syntax()` method
    - Check for valid YAML structure
    - _Requirements: 7.1_
  
  - [~] 6.2 Implement blueprint_id validation
    - Implement `validate_blueprint_id()` method
    - Check for underscore format (invalid)
    - Verify hyphen format (valid)
    - _Requirements: 7.1_
  
  - [~] 6.3 Implement port consistency validation
    - Implement `validate_port_consistency()` method
    - Check verification port matches application port
    - Check firewall rules include application port
    - _Requirements: 7.2, 7.3_
  
  - [~] 6.4 Implement health endpoint validation
    - Implement `validate_health_endpoint()` method
    - Check if endpoint exists in application code
    - Parse application files for route definitions
    - _Requirements: 7.4_
  
  - [ ]* 6.5 Write property test for configuration validation
    - **Property 4: Configuration Validation Consistency**
    - **Validates: Requirements 7.1**
  
  - [ ]* 6.6 Write property test for port consistency
    - **Property 5: Port Configuration Consistency**
    - **Validates: Requirements 7.2, 7.3**
  
  - [ ]* 6.7 Write unit tests for configuration validator
    - Test YAML validation
    - Test blueprint_id validation
    - Test port consistency checks
    - _Requirements: 7.1, 7.2, 7.3_

- [~] 7. Checkpoint - Ensure fix and validation components work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Integration with Existing Tools
  - [~] 8.1 Create existing tools wrapper
    - Create `ExistingToolsIntegration` class
    - Implement `run_debug_nodejs()` method to call troubleshooting-tools/nodejs/debug-nodejs.py
    - Implement `run_extract_instance_info()` method
    - Implement `run_fix_nodejs()` method
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [~] 8.2 Integrate with diagnostic engine
    - Call existing tools from `DiagnosticEngine`
    - Use debug-nodejs.py for Node.js diagnostics
    - Use extract-instance-info.py for instance information
    - _Requirements: 10.1, 10.2_
  
  - [ ]* 8.3 Write property test for existing tool integration
    - **Property 10: Existing Tool Integration**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
  
  - [ ]* 8.4 Write unit tests for tool integration
    - Test calling existing tools
    - Test parsing tool output
    - _Requirements: 10.1, 10.2_

- [ ] 9. Implement Main Diagnostic Tool
  - [~] 9.1 Create main WorkflowInvestigator class
    - Create `WorkflowInvestigator` class
    - Implement `__init__()` with repo, run_id, region parameters
    - Initialize all component classes
    - _Requirements: 1.1_
  
  - [~] 9.2 Implement investigate method
    - Implement `investigate()` method as main entry point
    - Call retrieve_logs(), diagnose(), apply_fixes() in sequence
    - Handle errors at each stage
    - Return comprehensive `DiagnosticReport`
    - _Requirements: 2.1_
  
  - [~] 9.3 Implement report generation
    - Implement `generate_report()` method
    - Create human-readable report with all diagnostic information
    - Include workflow status, instance state, SSH status, app diagnostics
    - Include recommended fixes and applied fixes
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [~] 9.4 Implement command-line interface
    - Add argparse for command-line arguments
    - Support --repo, --run-id, --region, --apply-fixes flags
    - Add --help documentation
    - _Requirements: 1.1_
  
  - [ ]* 9.5 Write property test for diagnostic report completeness
    - **Property 8: Diagnostic Report Completeness**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
  
  - [ ]* 9.6 Write property test for failure point identification
    - **Property 2: Failure Point Identification**
    - **Validates: Requirements 2.2, 2.5**
  
  - [ ]* 9.7 Write property test for error message extraction
    - **Property 9: Error Message Extraction**
    - **Validates: Requirements 2.3, 2.4, 2.5**

- [ ] 10. Create usage documentation
  - [~] 10.1 Create README for the tool
    - Document installation steps
    - Document usage examples
    - Document command-line options
    - _Requirements: 1.1_
  
  - [~] 10.2 Add example workflow investigation
    - Provide example of investigating a real failure
    - Show sample output
    - Document common failure patterns
    - _Requirements: 2.1_
  
  - [~] 10.3 Document integration with existing tools
    - List all existing tools used
    - Explain when each tool is called
    - _Requirements: 10.1, 10.2, 10.3_

- [ ] 11. Integration testing with real workflow
  - [ ]* 11.1 Test with actual failed workflow
    - Use the provided workflow run ID: 21857245881
    - Use the provided repository: naveenraj44125-creator/test-deployment-1770711871
    - Verify complete investigation flow
    - Verify diagnostic report is generated
    - _Requirements: 1.1, 2.1, 9.5_
  
  - [ ]* 11.2 Test fix application
    - Apply fixes to the failed deployment
    - Verify configuration is corrected
    - Re-run deployment to verify fixes work
    - _Requirements: 8.5_
  
  - [ ]* 11.3 Test SSH diagnostics on real instance
    - Connect to the Lightsail instance
    - Run diagnostic commands
    - Verify results are captured correctly
    - _Requirements: 4.1, 5.1_

- [~] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests use real GitHub workflows and Lightsail instances
- The tool leverages existing troubleshooting scripts in `troubleshooting-tools/` directory
- GitHub CLI (`gh`) must be installed and authenticated
- AWS credentials must be configured for Lightsail access
