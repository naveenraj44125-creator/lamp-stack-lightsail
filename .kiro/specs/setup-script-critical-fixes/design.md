# Design Document: Setup Script Critical Fixes

## Overview

This design addresses three critical issues in the AWS Lightsail deployment setup script:

1. **File Creation Location**: Files are being created in temporary directories instead of the user's working directory
2. **Deprecated Blueprint**: The blueprint "ubuntu-20-04" is deprecated and causes instance creation failures
3. **MCP Server Integration**: Missing AI-powered recommendations for deployment configuration

The solution involves fixing the working directory handling, updating blueprint identifiers to use underscores instead of hyphens, and integrating MCP server tools for intelligent project analysis.

## Architecture

### Current Architecture Issues

The setup script is modular with the following structure:
- `setup.sh` - Main orchestrator that sources all modules
- `setup/00-variables.sh` - Variable definitions and defaults
- `setup/02-ui.sh` - User interface and menu functions
- `setup/03-project-analysis.sh` - Project detection and analysis
- `setup/06-config-generation.sh` - Configuration file generation
- `setup/08-interactive.sh` - Main execution flow and interactive mode

**Issue 1**: The script doesn't explicitly set or maintain the working directory, causing files to be created relative to wherever the script executes from (potentially a temp directory).

**Issue 2**: Blueprint identifiers use hyphens ("ubuntu-22-04") but AWS Lightsail API expects underscores ("ubuntu_22_04").

**Issue 3**: The `analyze_project_for_recommendations()` function uses simple file detection instead of MCP server tools for intelligent analysis.

### Proposed Architecture

The solution maintains the modular structure while adding:

1. **Working Directory Management**: Explicit PWD capture and validation at script start
2. **Blueprint Identifier Normalization**: Consistent use of underscore format throughout
3. **MCP Server Integration**: Enhanced project analysis with AI recommendations

## Components and Interfaces

### Component 1: Working Directory Manager

**Location**: `setup/08-interactive.sh` (main() function)

**Responsibilities**:
- Capture the user's working directory at script start
- Validate that the working directory is writable
- Ensure all file creation operations use absolute paths relative to working directory

**Interface**:
```bash
# At the start of main() function
SCRIPT_START_DIR="$(pwd)"
export SCRIPT_START_DIR

# Validation
if [[ ! -w "$SCRIPT_START_DIR" ]]; then
    echo "Error: Working directory is not writable"
    exit 1
fi
```

### Component 2: Blueprint Identifier Normalizer

**Location**: Multiple modules (00-variables.sh, 02-ui.sh, 06-config-generation.sh, 08-interactive.sh)

**Responsibilities**:
- Define valid blueprint identifiers with underscores
- Validate blueprint identifiers against AWS Lightsail API format
- Display user-friendly names while using API-compatible identifiers

**Interface**:
```bash
# In 00-variables.sh
BLUEPRINT_ID=${BLUEPRINT_ID:-ubuntu_22_04}

# Valid blueprints (API format)
VALID_BLUEPRINTS=("ubuntu_22_04" "ubuntu_24_04" "amazon_linux_2023")

# Display names (user-friendly)
declare -A BLUEPRINT_DISPLAY_NAMES=(
    ["ubuntu_22_04"]="Ubuntu 22.04 LTS (Recommended)"
    ["ubuntu_24_04"]="Ubuntu 24.04 LTS (Newest)"
    ["amazon_linux_2023"]="Amazon Linux 2023"
)
```

### Component 3: MCP Server Integration Layer

**Location**: `setup/03-project-analysis.sh` (analyze_project_for_recommendations function)

**Responsibilities**:
- Call MCP server tools to analyze project structure
- Parse MCP server responses for recommendations
- Fall back to file-based detection if MCP server unavailable
- Store recommendations in global variables

**Interface**:
```bash
# MCP server tool invocation
analyze_project_with_mcp() {
    local project_path="$1"
    
    # Check if MCP server is available
    if ! command -v mcp &> /dev/null; then
        return 1  # Fall back to file-based detection
    fi
    
    # Call MCP server analyze tool
    local mcp_result=$(mcp analyze-project --path "$project_path" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        # Parse JSON response
        RECOMMENDED_APP_TYPE=$(echo "$mcp_result" | jq -r '.app_type // ""')
        RECOMMENDED_DATABASE=$(echo "$mcp_result" | jq -r '.database // "none"')
        RECOMMENDED_BUNDLE=$(echo "$mcp_result" | jq -r '.bundle // "micro_3_0"')
        RECOMMENDED_BUCKET=$(echo "$mcp_result" | jq -r '.needs_storage // "false"')
        ANALYSIS_CONFIDENCE=$(echo "$mcp_result" | jq -r '.confidence // 0')
        return 0
    fi
    
    return 1  # Fall back to file-based detection
}
```

### Component 4: File Creation Validator

**Location**: `setup/06-config-generation.sh`

**Responsibilities**:
- Verify files are created in the correct location
- Provide clear error messages if file creation fails
- Return success/failure status for each file operation

**Interface**:
```bash
create_file_with_validation() {
    local filepath="$1"
    local content="$2"
    
    # Ensure we're in the working directory
    cd "$SCRIPT_START_DIR" || {
        echo "Error: Cannot access working directory"
        return 1
    }
    
    # Create file
    echo "$content" > "$filepath"
    
    # Verify creation
    if [[ ! -f "$filepath" ]]; then
        echo "Error: Failed to create $filepath"
        return 1
    fi
    
    echo "✓ Created: $(realpath "$filepath")"
    return 0
}
```

## Data Models

### Blueprint Configuration

```yaml
blueprint:
  api_id: "ubuntu_22_04"           # AWS API format (underscores)
  display_name: "Ubuntu 22.04 LTS" # User-friendly name
  recommended: true                 # Default selection
  deprecated: false                 # Validation flag
```

### MCP Server Response

```json
{
  "app_type": "nodejs",
  "database": "postgresql",
  "bundle": "small_3_0",
  "needs_storage": true,
  "confidence": 85,
  "detected_frameworks": ["express", "react"],
  "detected_databases": ["pg"],
  "reasoning": "Detected Express server with React client and PostgreSQL driver"
}
```

### Recommendation State

```bash
# Global variables set by MCP analysis
RECOMMENDED_APP_TYPE="nodejs"
RECOMMENDED_DATABASE="postgresql"
RECOMMENDED_BUNDLE="small_3_0"
RECOMMENDED_BUCKET="true"
ANALYSIS_CONFIDENCE=85
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Working Directory Consistency

*For any* execution of the setup script, all generated files (deployment-*.config.yml, .github/workflows/deploy-*.yml) should be created in the directory from which the user invoked the script.

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Blueprint Identifier Format Validity

*For any* blueprint identifier used in deployment configuration files, the identifier should match the AWS Lightsail API format (underscores, not hyphens) and be one of the valid blueprint IDs.

**Validates: Requirements 2.3, 2.4, 2.5, 2.6**

### Property 3: Blueprint Validation Rejection

*For any* invalid blueprint identifier (including "ubuntu-20-04"), the validation function should reject it and prevent deployment configuration creation.

**Validates: Requirements 2.1, 2.4**

### Property 4: MCP Server Graceful Degradation

*For any* project analysis execution, if MCP server is unavailable or returns an error, the script should fall back to file-based detection without failing.

**Validates: Requirements 3.4, 3.8**

### Property 5: Recommendation Highlighting Consistency

*For any* interactive menu where an AI recommendation exists, the recommended option should be marked with a star (★) indicator and set as the default selection.

**Validates: Requirements 3.3, 3.6**

### Property 6: File Creation Verification

*For any* file creation operation, if the file does not exist after the creation attempt, the script should report an error and exit with non-zero status.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 7: Backward Compatibility Preservation

*For any* existing deployment configuration file with old blueprint format, the script should continue to function without breaking existing deployments.

**Validates: Requirements 4.1, 4.3**

## Error Handling

### Working Directory Errors

**Error**: Working directory is not writable
- **Detection**: Check write permissions at script start
- **Response**: Display error message with directory path and exit with code 1
- **User Action**: Run script from a writable directory or fix permissions

**Error**: Cannot change to working directory
- **Detection**: `cd "$SCRIPT_START_DIR"` fails
- **Response**: Display error message and exit with code 1
- **User Action**: Verify directory still exists and is accessible

### Blueprint Identifier Errors

**Error**: Invalid blueprint identifier provided
- **Detection**: Regex validation against allowed patterns
- **Response**: Display error with list of valid blueprints and exit with code 1
- **User Action**: Use one of the valid blueprint identifiers

**Error**: Deprecated blueprint "ubuntu-20-04" used
- **Detection**: Specific check for deprecated identifier
- **Response**: Display deprecation notice with migration path and exit with code 1
- **User Action**: Update to "ubuntu_22_04" or "ubuntu_24_04"

### MCP Server Errors

**Error**: MCP server command not found
- **Detection**: `command -v mcp` returns non-zero
- **Response**: Log info message and fall back to file-based detection
- **User Action**: None required (graceful degradation)

**Error**: MCP server returns invalid JSON
- **Detection**: `jq` parsing fails
- **Response**: Log warning and fall back to file-based detection
- **User Action**: None required (graceful degradation)

**Error**: MCP server timeout
- **Detection**: Command execution exceeds timeout threshold
- **Response**: Kill MCP process, log warning, fall back to file-based detection
- **User Action**: None required (graceful degradation)

### File Creation Errors

**Error**: Failed to create deployment config file
- **Detection**: File doesn't exist after write operation
- **Response**: Display error with expected path and exit with code 1
- **User Action**: Check disk space and permissions

**Error**: Failed to create .github/workflows directory
- **Detection**: `mkdir -p` fails or directory doesn't exist after creation
- **Response**: Display error and exit with code 1
- **User Action**: Check permissions and disk space

## Testing Strategy

### Unit Tests

Unit tests should focus on specific functions and edge cases:

1. **Blueprint Validation Tests**
   - Test valid blueprint identifiers (ubuntu_22_04, ubuntu_24_04, amazon_linux_2023)
   - Test invalid blueprint identifiers (ubuntu-20-04, ubuntu-18-04, invalid-name)
   - Test empty blueprint identifier
   - Test blueprint identifier with special characters

2. **Working Directory Tests**
   - Test file creation in current directory
   - Test file creation when script is sourced from different location
   - Test behavior when working directory is deleted during execution
   - Test behavior with read-only working directory

3. **MCP Server Integration Tests**
   - Test successful MCP server response parsing
   - Test MCP server unavailable (command not found)
   - Test MCP server returns invalid JSON
   - Test MCP server timeout
   - Test fallback to file-based detection

4. **File Creation Validation Tests**
   - Test successful file creation and verification
   - Test file creation failure detection
   - Test directory creation for nested paths
   - Test file creation with insufficient permissions

### Property-Based Tests

Property-based tests should verify universal correctness properties across many generated inputs. Each test should run a minimum of 100 iterations.

1. **Property Test: Working Directory Consistency**
   - **Property**: For any valid project directory, all generated files should be created in that directory
   - **Test**: Generate random project structures, run setup script, verify all files are in the starting directory
   - **Tag**: Feature: setup-script-critical-fixes, Property 1: Working Directory Consistency

2. **Property Test: Blueprint Format Validity**
   - **Property**: For any blueprint identifier in generated config files, it should use underscores and be valid
   - **Test**: Generate configs with various blueprints, parse YAML, verify format matches AWS API requirements
   - **Tag**: Feature: setup-script-critical-fixes, Property 2: Blueprint Identifier Format Validity

3. **Property Test: Invalid Blueprint Rejection**
   - **Property**: For any invalid blueprint identifier, validation should reject it
   - **Test**: Generate random invalid blueprint strings, verify all are rejected by validation
   - **Tag**: Feature: setup-script-critical-fixes, Property 3: Blueprint Validation Rejection

4. **Property Test: MCP Server Graceful Degradation**
   - **Property**: For any MCP server failure scenario, script should continue with file-based detection
   - **Test**: Simulate various MCP failures (timeout, invalid JSON, command not found), verify script completes
   - **Tag**: Feature: setup-script-critical-fixes, Property 4: MCP Server Graceful Degradation

5. **Property Test: Recommendation Highlighting**
   - **Property**: For any menu with AI recommendations, recommended options should be highlighted and default
   - **Test**: Generate various recommendation scenarios, verify UI displays star and sets correct default
   - **Tag**: Feature: setup-script-critical-fixes, Property 5: Recommendation Highlighting Consistency

6. **Property Test: File Creation Verification**
   - **Property**: For any file creation failure, script should detect and report error
   - **Test**: Simulate various file creation failures, verify script exits with error
   - **Tag**: Feature: setup-script-critical-fixes, Property 6: File Creation Verification

### Integration Tests

Integration tests should verify the complete workflow:

1. **End-to-End Setup Test**
   - Run complete setup script in test directory
   - Verify all files created in correct location
   - Verify blueprint identifiers use underscores
   - Verify MCP recommendations are displayed (if available)

2. **Automated Mode Test**
   - Run script with all environment variables set
   - Verify non-interactive execution completes
   - Verify files created with correct blueprint format

3. **Backward Compatibility Test**
   - Test with existing deployment configs using old format
   - Verify script doesn't break existing setups
   - Verify migration path for deprecated blueprints

### Test Configuration

All property-based tests should:
- Run minimum 100 iterations per test
- Use appropriate PBT library (e.g., `bats` with random input generation for bash)
- Tag each test with feature name and property number
- Generate diverse test inputs (various directory structures, blueprint names, MCP responses)
- Verify both success and failure paths

## Implementation Notes

### Phase 1: Working Directory Fix

1. Add `SCRIPT_START_DIR` capture at the beginning of `main()` in `setup/08-interactive.sh`
2. Update all file creation calls in `setup/06-config-generation.sh` to use absolute paths
3. Add validation to ensure working directory is writable
4. Add `cd "$SCRIPT_START_DIR"` before each file creation operation

### Phase 2: Blueprint Identifier Update

1. Update default in `setup/00-variables.sh` from "ubuntu-22-04" to "ubuntu_22_04"
2. Update blueprint arrays in `setup/08-interactive.sh` to use underscore format
3. Update validation regex to accept only underscore format
4. Update display names in `setup/02-ui.sh` to show user-friendly names
5. Update all blueprint references in `setup/06-config-generation.sh`

### Phase 3: MCP Server Integration

1. Add `analyze_project_with_mcp()` function to `setup/03-project-analysis.sh`
2. Update `analyze_project_for_recommendations()` to call MCP function first
3. Add JSON parsing for MCP server responses
4. Update `select_option()` in `setup/02-ui.sh` to highlight AI recommendations
5. Add confidence score display in project analysis output

### Phase 4: Validation and Testing

1. Add file creation verification after each file write
2. Add error messages with full file paths
3. Add exit code handling for all error conditions
4. Test all three fixes together in integration tests
