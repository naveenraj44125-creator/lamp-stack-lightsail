# Requirements Document

## Introduction

This document specifies the requirements for investigating and fixing the deployment workflow failure in the AWS Lightsail deployment system. The system uses a test script (`test-setup-complete-deployment.sh`) that creates GitHub repositories, sets up AWS IAM roles, and triggers GitHub Actions workflows to deploy Node.js applications to AWS Lightsail. Currently, when the test runs without the `--skip-wait` flag, the workflow fails during deployment despite successfully creating the infrastructure.

The investigation will use existing troubleshooting tools in the `troubleshooting-tools/` directory to diagnose the failure, identify the root cause, and implement fixes.

## Glossary

- **Test_Script**: The bash script `test-setup-complete-deployment.sh` that orchestrates end-to-end deployment testing
- **Workflow_Run**: A specific execution of a GitHub Actions workflow, identified by a run ID
- **Troubleshooting_Tool**: Python scripts in `troubleshooting-tools/` directory that diagnose deployment issues
- **Lightsail_Instance**: AWS Lightsail virtual private server instance where the application is deployed
- **Health_Check**: HTTP endpoint verification that confirms the application is running correctly
- **Deployment_Config**: YAML configuration file (`deployment-nodejs.config.yml`) that specifies deployment parameters
- **Blueprint_ID**: AWS Lightsail operating system identifier (must use hyphens like `ubuntu-22-04`)
- **SSH_Connection**: Secure shell connection used to deploy and configure the Lightsail instance
- **Verification_Endpoint**: HTTP endpoint used to verify successful deployment (e.g., `/`, `/api/health`)
- **GitHub_CLI**: The `gh` command-line tool for interacting with GitHub Actions
- **Diagnostic_Script**: A troubleshooting script that collects information about deployment failures

## Requirements

### Requirement 1: Workflow Log Retrieval

**User Story:** As a developer, I want to retrieve workflow run logs from GitHub Actions, so that I can analyze what went wrong during deployment.

#### Acceptance Criteria

1. WHEN provided with a repository name and run ID, THE Log_Retriever SHALL use GitHub CLI to fetch the complete workflow logs
2. WHEN fetching logs, THE Log_Retriever SHALL retrieve logs for all jobs (load-config, test, pre-steps-generic, application-package, post-steps-generic, verification)
3. WHEN a job fails, THE Log_Retriever SHALL identify which step within the job failed
4. WHEN logs are retrieved, THE Log_Retriever SHALL save them to a file for analysis
5. IF GitHub CLI is not authenticated, THEN THE Log_Retriever SHALL provide clear instructions for authentication

### Requirement 2: Automated Failure Diagnosis

**User Story:** As a developer, I want to automatically diagnose common deployment failures, so that I can quickly identify the root cause.

#### Acceptance Criteria

1. WHEN analyzing workflow logs, THE Diagnostic_Tool SHALL identify SSH connection failures
2. WHEN analyzing workflow logs, THE Diagnostic_Tool SHALL identify health check endpoint failures
3. WHEN analyzing workflow logs, THE Diagnostic_Tool SHALL identify dependency installation failures
4. WHEN analyzing workflow logs, THE Diagnostic_Tool SHALL identify application startup failures
5. WHEN a failure pattern is identified, THE Diagnostic_Tool SHALL provide a specific diagnosis with recommended fixes

### Requirement 3: Instance State Verification

**User Story:** As a developer, I want to verify the Lightsail instance state, so that I can confirm the infrastructure was created correctly.

#### Acceptance Criteria

1. WHEN provided with an instance name, THE Instance_Checker SHALL retrieve the instance state from AWS Lightsail
2. WHEN checking instance state, THE Instance_Checker SHALL verify the instance is in "running" state
3. WHEN checking instance, THE Instance_Checker SHALL retrieve the public IP address
4. WHEN checking instance, THE Instance_Checker SHALL verify SSH port (22) is accessible
5. IF the instance does not exist, THEN THE Instance_Checker SHALL report that instance creation failed

### Requirement 4: SSH Connectivity Testing

**User Story:** As a developer, I want to test SSH connectivity to the Lightsail instance, so that I can verify remote access is working.

#### Acceptance Criteria

1. WHEN testing SSH connectivity, THE SSH_Tester SHALL attempt to connect to the instance using the Lightsail SSH key
2. WHEN SSH connection succeeds, THE SSH_Tester SHALL execute a simple command to verify command execution
3. WHEN SSH connection fails, THE SSH_Tester SHALL report the specific error (timeout, authentication failure, connection refused)
4. WHEN testing SSH, THE SSH_Tester SHALL retry up to 3 times with 10-second delays
5. IF SSH is accessible, THEN THE SSH_Tester SHALL report success with connection details

### Requirement 5: Application Diagnostics via SSH

**User Story:** As a developer, I want to run diagnostic commands on the Lightsail instance, so that I can understand the application state.

#### Acceptance Criteria

1. WHEN SSH is accessible, THE Diagnostic_Runner SHALL check if Node.js is installed and report the version
2. WHEN checking application, THE Diagnostic_Runner SHALL verify if npm packages are installed in the application directory
3. WHEN checking application, THE Diagnostic_Runner SHALL check PM2 process status
4. WHEN checking application, THE Diagnostic_Runner SHALL retrieve the last 50 lines of application logs
5. WHEN checking application, THE Diagnostic_Runner SHALL test if the application responds on localhost

### Requirement 6: Health Endpoint Testing

**User Story:** As a developer, I want to test health check endpoints from outside the instance, so that I can verify external accessibility.

#### Acceptance Criteria

1. WHEN testing health endpoints, THE Endpoint_Tester SHALL make HTTP requests to the configured verification endpoint
2. WHEN testing endpoints, THE Endpoint_Tester SHALL retry up to 10 times with 15-second intervals
3. WHEN an endpoint returns HTTP 200, THE Endpoint_Tester SHALL verify the response body contains expected content
4. WHEN an endpoint returns an error code, THE Endpoint_Tester SHALL report the HTTP status code and response body
5. IF the endpoint is not accessible, THEN THE Endpoint_Tester SHALL test if the port is open using telnet or nc

### Requirement 7: Configuration Validation

**User Story:** As a developer, I want to validate the deployment configuration, so that I can catch configuration errors before they cause failures.

#### Acceptance Criteria

1. WHEN validating configuration, THE Config_Validator SHALL check that blueprint_id uses hyphens (not underscores)
2. WHEN validating configuration, THE Config_Validator SHALL verify the verification port matches the application port
3. WHEN validating configuration, THE Config_Validator SHALL check that firewall rules include the application port
4. WHEN validating configuration, THE Config_Validator SHALL verify the health check endpoint exists in the application code
5. IF validation fails, THEN THE Config_Validator SHALL provide specific error messages for each issue

### Requirement 8: Automated Fix Application

**User Story:** As a developer, I want to automatically apply common fixes, so that deployment issues can be resolved without manual intervention.

#### Acceptance Criteria

1. WHEN blueprint_id uses underscores, THE Fix_Applier SHALL convert them to hyphens in the configuration file
2. WHEN port configuration is inconsistent, THE Fix_Applier SHALL update the configuration to match the application code
3. WHEN health check endpoint is missing, THE Fix_Applier SHALL add a default `/api/health` endpoint to the application
4. WHEN firewall rules are incomplete, THE Fix_Applier SHALL add the application port to the allowed ports list
5. WHEN fixes are applied, THE Fix_Applier SHALL create a summary report of all changes made

### Requirement 9: Comprehensive Diagnostic Report

**User Story:** As a developer, I want a comprehensive diagnostic report, so that I have all information needed to fix the deployment.

#### Acceptance Criteria

1. WHEN generating a report, THE Report_Generator SHALL include workflow run status and failure point
2. WHEN generating a report, THE Report_Generator SHALL include instance state and connectivity status
3. WHEN generating a report, THE Report_Generator SHALL include application diagnostics (Node.js version, PM2 status, logs)
4. WHEN generating a report, THE Report_Generator SHALL include health endpoint test results
5. WHEN generating a report, THE Report_Generator SHALL include recommended fixes based on the diagnosis

### Requirement 10: Integration with Existing Tools

**User Story:** As a developer, I want to use existing troubleshooting tools, so that I can leverage proven diagnostic capabilities.

#### Acceptance Criteria

1. WHEN diagnosing Node.js issues, THE Investigation_Tool SHALL use `troubleshooting-tools/nodejs/debug-nodejs.py`
2. WHEN extracting instance information, THE Investigation_Tool SHALL use `troubleshooting-tools/general/extract-instance-info.py`
3. WHEN monitoring deployment progress, THE Investigation_Tool SHALL use `troubleshooting-tools/general/monitor-deployment-progress.py`
4. WHEN fixing Node.js issues, THE Investigation_Tool SHALL use `troubleshooting-tools/nodejs/fix-nodejs.py`
5. WHEN running diagnostics, THE Investigation_Tool SHALL ensure all required Python dependencies are available
