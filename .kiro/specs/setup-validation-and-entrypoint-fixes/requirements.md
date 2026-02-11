# Requirements Document

## Introduction

This specification addresses two critical issues in the AWS Lightsail deployment setup script that cause deployment failures and create confusion for users:

1. **Missing S3 Bucket Name Validation**: The setup script accepts any bucket name without validating it against AWS S3 naming requirements, leading to deployment failures when invalid names are used.

2. **Unnecessary app.js Creation**: The script creates an app.js file even when the application already has existing entry points (server.js, index.js, server/server.js, etc.), creating confusion and potentially conflicting with the existing application structure.

These issues were identified from user feedback after running the setup script, where deployment failed due to invalid bucket names and confusion arose from redundant file creation.

## Glossary

- **Setup_Script**: The AWS Lightsail deployment setup script (setup.sh and modular scripts in setup/ directory)
- **S3_Bucket**: AWS S3-compatible Lightsail bucket for object storage
- **Bucket_Name**: The unique identifier for an S3 bucket that must follow AWS naming conventions
- **Entry_Point**: The main application file that starts the application (e.g., server.js, index.js, app.js, app.py)
- **Node_Application**: A Node.js application that may have various entry point files
- **Validation_Error**: A descriptive error message shown to the user when input fails validation
- **Interactive_Mode**: The mode where the setup script prompts the user for configuration inputs
- **Automated_Mode**: The mode where the setup script uses environment variables for configuration

## Requirements

### Requirement 1: S3 Bucket Name Validation

**User Story:** As a developer, I want the setup script to validate S3 bucket names before proceeding with deployment, so that I don't encounter deployment failures due to invalid bucket names.

#### Acceptance Criteria

1. WHEN a user provides a bucket name in interactive mode, THE Setup_Script SHALL validate it against AWS S3 naming rules before proceeding
2. WHEN a bucket name contains uppercase letters, THE Setup_Script SHALL reject it with a Validation_Error explaining that bucket names must be lowercase
3. WHEN a bucket name contains underscores, THE Setup_Script SHALL reject it with a Validation_Error explaining that underscores are not allowed
4. WHEN a bucket name is shorter than 3 characters, THE Setup_Script SHALL reject it with a Validation_Error explaining the minimum length requirement
5. WHEN a bucket name is longer than 63 characters, THE Setup_Script SHALL reject it with a Validation_Error explaining the maximum length requirement
6. WHEN a bucket name starts with a hyphen, THE Setup_Script SHALL reject it with a Validation_Error explaining that bucket names must start with a letter or number
7. WHEN a bucket name ends with a hyphen, THE Setup_Script SHALL reject it with a Validation_Error explaining that bucket names must end with a letter or number
8. WHEN a bucket name contains consecutive periods, THE Setup_Script SHALL reject it with a Validation_Error explaining that consecutive periods are not allowed
9. WHEN a bucket name is formatted as an IP address, THE Setup_Script SHALL reject it with a Validation_Error explaining that IP address format is not allowed
10. WHEN a bucket name contains invalid characters (not lowercase letters, numbers, hyphens, or periods), THE Setup_Script SHALL reject it with a Validation_Error listing the allowed characters
11. WHEN a bucket name passes all validation rules, THE Setup_Script SHALL accept it and proceed with configuration
12. WHEN the BUCKET_NAME environment variable is set in automated mode, THE Setup_Script SHALL validate it before proceeding with deployment

### Requirement 2: Smart Entry Point Detection

**User Story:** As a developer, I want the setup script to detect my existing application entry points, so that it doesn't create redundant or conflicting files.

#### Acceptance Criteria

1. WHEN the Setup_Script detects an existing Node.js entry point file, THE Setup_Script SHALL NOT create a new app.js file
2. WHEN the Setup_Script checks for existing entry points, THE Setup_Script SHALL search for server.js in the root directory
3. WHEN the Setup_Script checks for existing entry points, THE Setup_Script SHALL search for index.js in the root directory
4. WHEN the Setup_Script checks for existing entry points, THE Setup_Script SHALL search for server/server.js in the server subdirectory
5. WHEN the Setup_Script checks for existing entry points, THE Setup_Script SHALL search for server/index.js in the server subdirectory
6. WHEN the Setup_Script checks for existing entry points, THE Setup_Script SHALL search for src/server.js in the src subdirectory
7. WHEN the Setup_Script checks for existing entry points, THE Setup_Script SHALL search for src/index.js in the src subdirectory
8. WHEN the Setup_Script checks for existing entry points, THE Setup_Script SHALL search for main.js in the root directory
9. WHEN no existing entry point is found, THE Setup_Script SHALL create app.js as a template
10. WHEN an existing entry point is found, THE Setup_Script SHALL display a message indicating which entry point was detected
11. WHEN an existing entry point is found, THE Setup_Script SHALL skip the app.js creation step entirely

### Requirement 3: Entry Point Detection for Python Applications

**User Story:** As a Python developer, I want the setup script to detect my existing Python entry points, so that it doesn't create redundant files.

#### Acceptance Criteria

1. WHEN the Setup_Script detects an existing Python entry point file, THE Setup_Script SHALL NOT create a new app.py file
2. WHEN the Setup_Script checks for existing Python entry points, THE Setup_Script SHALL search for app.py in the root directory
3. WHEN the Setup_Script checks for existing Python entry points, THE Setup_Script SHALL search for main.py in the root directory
4. WHEN the Setup_Script checks for existing Python entry points, THE Setup_Script SHALL search for server.py in the root directory
5. WHEN the Setup_Script checks for existing Python entry points, THE Setup_Script SHALL search for src/app.py in the src subdirectory
6. WHEN the Setup_Script checks for existing Python entry points, THE Setup_Script SHALL search for src/main.py in the src subdirectory
7. WHEN no existing Python entry point is found, THE Setup_Script SHALL create app.py as a template
8. WHEN an existing Python entry point is found, THE Setup_Script SHALL display a message indicating which entry point was detected

### Requirement 4: Entry Point Detection for PHP Applications

**User Story:** As a PHP developer, I want the setup script to detect my existing PHP entry points, so that it doesn't create redundant files.

#### Acceptance Criteria

1. WHEN the Setup_Script detects an existing PHP entry point file, THE Setup_Script SHALL NOT create a new index.php file
2. WHEN the Setup_Script checks for existing PHP entry points, THE Setup_Script SHALL search for index.php in the root directory
3. WHEN the Setup_Script checks for existing PHP entry points, THE Setup_Script SHALL search for app.php in the root directory
4. WHEN the Setup_Script checks for existing PHP entry points, THE Setup_Script SHALL search for public/index.php in the public subdirectory
5. WHEN no existing PHP entry point is found, THE Setup_Script SHALL create index.php as a template
6. WHEN an existing PHP entry point is found, THE Setup_Script SHALL display a message indicating which entry point was detected

### Requirement 5: Validation Error Messages

**User Story:** As a developer, I want clear and actionable error messages when validation fails, so that I can quickly fix the issue and proceed with setup.

#### Acceptance Criteria

1. WHEN a validation error occurs, THE Setup_Script SHALL display the error message in red color for visibility
2. WHEN a bucket name validation fails, THE Validation_Error SHALL include the specific rule that was violated
3. WHEN a bucket name validation fails, THE Validation_Error SHALL include an example of a valid bucket name
4. WHEN a bucket name validation fails, THE Setup_Script SHALL re-prompt the user for a valid bucket name
5. WHEN a bucket name validation fails in automated mode, THE Setup_Script SHALL exit with a non-zero status code
6. WHEN a bucket name validation fails in automated mode, THE Validation_Error SHALL include instructions for setting the correct environment variable

### Requirement 6: Validation Function Implementation

**User Story:** As a maintainer, I want a reusable validation function for bucket names, so that validation logic is consistent across the codebase.

#### Acceptance Criteria

1. THE Setup_Script SHALL implement a validate_bucket_name function that accepts a bucket name as input
2. WHEN validate_bucket_name is called with a valid bucket name, THE function SHALL return success (exit code 0)
3. WHEN validate_bucket_name is called with an invalid bucket name, THE function SHALL return failure (exit code 1)
4. WHEN validate_bucket_name is called with an invalid bucket name, THE function SHALL output a descriptive error message
5. THE validate_bucket_name function SHALL be called before any bucket creation or configuration steps
6. THE validate_bucket_name function SHALL be located in the utilities module (01-utils.sh) for reusability

### Requirement 7: Entry Point Detection Function Implementation

**User Story:** As a maintainer, I want a reusable function for detecting entry points, so that detection logic is consistent across different application types.

#### Acceptance Criteria

1. THE Setup_Script SHALL implement a detect_entry_point function that accepts an application type as input
2. WHEN detect_entry_point is called for a Node.js application, THE function SHALL return the path to the first detected entry point or empty string if none found
3. WHEN detect_entry_point is called for a Python application, THE function SHALL return the path to the first detected entry point or empty string if none found
4. WHEN detect_entry_point is called for a PHP application, THE function SHALL return the path to the first detected entry point or empty string if none found
5. THE detect_entry_point function SHALL search entry points in priority order (root directory first, then subdirectories)
6. THE detect_entry_point function SHALL be located in the project analysis module (03-project-analysis.sh)

### Requirement 8: Backward Compatibility

**User Story:** As a user of the existing setup script, I want the validation and detection features to work seamlessly with my existing workflows, so that I don't experience breaking changes.

#### Acceptance Criteria

1. WHEN the Setup_Script runs in interactive mode with the new validation, THE overall user experience SHALL remain consistent with the previous version
2. WHEN the Setup_Script runs in automated mode with valid inputs, THE behavior SHALL be identical to the previous version
3. WHEN existing environment variables are used, THE Setup_Script SHALL validate them without requiring changes to the variable names
4. WHEN the Setup_Script detects existing entry points, THE behavior SHALL be transparent to users who don't have existing entry points
5. THE Setup_Script SHALL maintain all existing command-line options and flags
