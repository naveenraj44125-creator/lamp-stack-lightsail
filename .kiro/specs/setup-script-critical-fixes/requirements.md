# Requirements Document

## Introduction

This specification addresses three critical issues in the AWS Lightsail deployment setup script that prevent successful deployments and limit the script's intelligence. The issues involve incorrect file placement, deprecated blueprint identifiers, and missing MCP server integration for intelligent project analysis.

## Glossary

- **Setup_Script**: The modular bash script system that generates deployment configurations and GitHub Actions workflows for AWS Lightsail
- **Working_Directory**: The directory from which the user executes the setup script, where deployment files should be created
- **Blueprint**: An AWS Lightsail operating system template identifier used to create instances
- **MCP_Server**: Model Context Protocol server that provides AI-powered project analysis capabilities
- **Config_Generation_Module**: The bash module (setup/06-config-generation.sh) responsible for creating deployment configuration files
- **Interactive_Module**: The bash module (setup/08-interactive.sh) that handles user interaction and orchestrates the setup workflow
- **Project_Analysis_Module**: The bash module (setup/03-project-analysis.sh) that analyzes project structure and provides recommendations

## Requirements

### Requirement 1: Fix File Creation in User's Working Directory

**User Story:** As a developer, I want deployment configuration files and GitHub workflows to be created in my project's root directory, so that they are properly tracked in version control and accessible for deployment.

#### Acceptance Criteria

1. WHEN the Setup_Script creates deployment configuration files, THE Config_Generation_Module SHALL create them in the user's Working_Directory
2. WHEN the Setup_Script creates GitHub workflow files, THE Config_Generation_Module SHALL create them in the Working_Directory/.github/workflows/ path
3. WHEN the Setup_Script executes from any location, THE Setup_Script SHALL explicitly set and maintain the Working_Directory as the current directory
4. WHEN deployment files are created, THE Setup_Script SHALL verify that files exist in the Working_Directory before proceeding
5. THE Setup_Script SHALL NOT create files in temporary directories or system directories

### Requirement 2: Update Blueprint Identifiers to Valid Values

**User Story:** As a developer, I want to use valid AWS Lightsail blueprint identifiers, so that instance creation succeeds without errors.

#### Acceptance Criteria

1. THE Setup_Script SHALL NOT include "ubuntu-20-04" in any blueprint selection menus or validation logic
2. THE Setup_Script SHALL use "ubuntu_22_04" as the default Blueprint identifier
3. WHEN displaying blueprint options, THE Setup_Script SHALL present "ubuntu_22_04", "ubuntu_24_04", and "amazon_linux_2023" as valid choices
4. WHEN validating Blueprint identifiers, THE Setup_Script SHALL accept only "ubuntu_22_04", "ubuntu_24_04", or "amazon_linux_2023"
5. THE Setup_Script SHALL use underscores in Blueprint identifiers, not hyphens
6. WHEN generating deployment configuration files, THE Config_Generation_Module SHALL write Blueprint identifiers with underscores
7. THE Setup_Script SHALL update all blueprint references in variables, validation, and UI modules

### Requirement 3: Integrate MCP Server for Intelligent Recommendations

**User Story:** As a developer, I want AI-powered recommendations for my application configuration, so that I can make informed decisions about deployment settings.

#### Acceptance Criteria

1. WHEN analyzing a project, THE Project_Analysis_Module SHALL call MCP_Server tools to analyze the project structure
2. WHEN MCP_Server analysis completes, THE Project_Analysis_Module SHALL extract recommendations for application type, database, instance size, and storage
3. WHEN displaying interactive menus, THE Interactive_Module SHALL highlight AI-recommended options with a star (★) indicator
4. WHEN no MCP_Server is available, THE Setup_Script SHALL fall back to file-based detection without errors
5. THE Project_Analysis_Module SHALL store MCP_Server recommendations in global variables (RECOMMENDED_APP_TYPE, RECOMMENDED_DATABASE, RECOMMENDED_BUNDLE, RECOMMENDED_BUCKET)
6. WHEN displaying options, THE Setup_Script SHALL automatically select AI-recommended options as defaults
7. THE Project_Analysis_Module SHALL display confidence scores for AI recommendations
8. WHEN MCP_Server analysis fails, THE Setup_Script SHALL log the error and continue with file-based detection

### Requirement 4: Maintain Backward Compatibility

**User Story:** As a developer with existing deployment configurations, I want the script updates to not break my current setup, so that I can continue using the tool without disruption.

#### Acceptance Criteria

1. WHEN the Setup_Script updates blueprint identifiers, THE Setup_Script SHALL maintain compatibility with existing deployment-*.config.yml files
2. WHEN MCP_Server integration is added, THE Setup_Script SHALL continue to work without MCP_Server available
3. WHEN file creation logic is fixed, THE Setup_Script SHALL not change the structure or content of generated files
4. THE Setup_Script SHALL preserve all existing functionality for non-interactive (automated) mode
5. THE Setup_Script SHALL maintain the same command-line interface and environment variables

### Requirement 5: Validate File Creation Success

**User Story:** As a developer, I want to be notified if file creation fails, so that I can troubleshoot issues before attempting deployment.

#### Acceptance Criteria

1. WHEN creating deployment configuration files, THE Config_Generation_Module SHALL verify the file exists after creation
2. WHEN creating GitHub workflow files, THE Config_Generation_Module SHALL verify the .github/workflows directory exists
3. IF file creation fails, THE Setup_Script SHALL display an error message with the expected file path
4. IF file creation fails, THE Setup_Script SHALL exit with a non-zero status code
5. WHEN all files are created successfully, THE Setup_Script SHALL display a success message listing created files
