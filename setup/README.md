# Setup Module Structure

This directory contains modular components of the deployment setup script. Each file has a specific responsibility, making the codebase easier to maintain and debug.

## Module Overview

### 00-variables.sh
**Purpose:** Global variables and configuration
- Color definitions for terminal output
- Default values for all configuration options
- Environment variable declarations
- MCP server integration variables

**Key Variables:**
- `AUTO_MODE` - Enable/disable automated mode
- `AWS_REGION` - AWS region for deployment
- `RECOMMENDED_*` - AI-generated recommendations
- `APP_TYPE`, `APP_NAME`, etc. - User configuration

### 01-utils.sh
**Purpose:** Utility functions
- String manipulation (to_lowercase, to_uppercase)
- Prerequisites checking (AWS CLI, GitHub CLI, jq)
- Git repository detection
- Credential validation

**Key Functions:**
- `check_prerequisites()` - Validates all required tools are installed
- `check_git_repo()` - Checks if current directory is a git repository
- `to_lowercase()` / `to_uppercase()` - String conversion utilities

### 02-ui.sh
**Purpose:** User interface and interaction
- Input prompts with default values
- Yes/no confirmations
- Option selection menus with AI recommendations
- Terminal styling and formatting

**Key Functions:**
- `get_input()` - Get text input from user with default
- `get_yes_no()` - Get boolean input (Y/n or y/N)
- `select_option()` - Display menu and get user selection
- `get_option_description()` - Get human-readable descriptions

**Features:**
- AI recommendation highlighting (★ marker)
- Default value indicators (→ marker)
- Color-coded output for better UX
- Direct terminal interaction via /dev/tty

### 03-project-analysis.sh
**Purpose:** Project detection and analysis
- Automatic framework detection
- Database requirement analysis
- Storage needs detection
- AI-powered recommendations

**Key Functions:**
- `analyze_project_for_recommendations()` - Main analysis function
- `detect_fullstack_react()` - Detect React + Node.js apps
- `detect_node_port()` - Auto-detect Node.js port
- `detect_health_endpoints()` - Find existing health check endpoints

**Detection Capabilities:**
- Node.js (Express, React)
- Python (Flask, Django)
- PHP (Laravel, plain PHP)
- Docker containers
- Database drivers (MySQL, PostgreSQL, MongoDB)
- File upload libraries (Pillow, boto3)

### 04-github.sh
**Purpose:** GitHub integration
- Repository creation
- Workflow file setup
- Git operations (commit, push)
- .gitignore generation

**Key Functions:**
- `create_github_repo_if_needed()` - Create GitHub repo if it doesn't exist
- `setup_workflow_files()` - Create .github/workflows directory
- `commit_and_push()` - Commit and push changes
- `create_gitignore()` - Generate comprehensive .gitignore

### 05-aws.sh
**Purpose:** AWS integration
- IAM role creation for GitHub OIDC
- OIDC provider setup
- AWS credential management
- Lightsail resource configuration

**Key Functions:**
- `create_iam_role_if_needed()` - Create IAM role for GitHub Actions
- `setup_github_oidc()` - Setup OIDC provider for GitHub Actions

## Usage

### As a Complete Script
```bash
# Run the main setup script
./setup.sh

# Run in automated mode
./setup.sh --auto --app-type nodejs --app-name "My App"
```

### As Individual Modules
```bash
# Source specific modules in your own scripts
source setup/00-variables.sh
source setup/01-utils.sh
source setup/02-ui.sh

# Use the functions
check_prerequisites
APP_TYPE=$(select_option "Select type:" "nodejs" "app_type" "nodejs" "python" "lamp")
```

## Adding New Modules

To add a new module:

1. Create a new file with a numbered prefix (e.g., `06-new-feature.sh`)
2. Add the shebang: `#!/bin/bash`
3. Define your functions
4. Source it in `setup.sh` in the appropriate order
5. Update this README with documentation

Example:
```bash
# setup/06-monitoring.sh
#!/bin/bash

setup_monitoring() {
    echo "Setting up monitoring..."
    # Your code here
}
```

Then in `setup.sh`:
```bash
source "$SCRIPT_DIR/setup/06-monitoring.sh"
```

## Module Dependencies

```
00-variables.sh (no dependencies)
    ↓
01-utils.sh (depends on: 00-variables.sh)
    ↓
02-ui.sh (depends on: 00-variables.sh, 01-utils.sh)
    ↓
03-project-analysis.sh (depends on: 00-variables.sh, 02-ui.sh)
    ↓
04-github.sh (depends on: 00-variables.sh, 02-ui.sh)
    ↓
05-aws.sh (depends on: 00-variables.sh, 02-ui.sh)
```

## Testing Individual Modules

You can test individual modules by sourcing them:

```bash
# Test the UI module
bash -c '
source setup/00-variables.sh
source setup/01-utils.sh
source setup/02-ui.sh

# Test a function
result=$(get_yes_no "Test prompt?" "true")
echo "Result: $result"
'
```

## Debugging

Enable debug mode for any module:
```bash
# Add at the top of any module file
set -x  # Enable debug output
set -e  # Exit on error
```

Or run the main script with debug:
```bash
bash -x setup.sh
```

## Best Practices

1. **Keep modules focused** - Each module should have a single responsibility
2. **Document functions** - Add comments explaining what each function does
3. **Use consistent naming** - Follow the existing naming conventions
4. **Handle errors** - Check return codes and provide helpful error messages
5. **Test independently** - Each module should be testable on its own
6. **Avoid circular dependencies** - Keep the dependency tree simple

## Migration from Monolithic Script

The original `setup-complete-deployment.sh` has been split into these modules. To migrate:

1. Functions are now in their respective modules based on responsibility
2. Global variables are in `00-variables.sh`
3. The main execution flow is in `setup.sh`
4. All functionality is preserved, just better organized

## Troubleshooting

### Module not found
```bash
# Make sure you're running from the project root
cd /path/to/project
./setup.sh
```

### Function not defined
```bash
# Check that modules are sourced in the correct order
# Dependencies must be loaded before dependent modules
```

### Permission denied
```bash
# Make the main script executable
chmod +x setup.sh
```
