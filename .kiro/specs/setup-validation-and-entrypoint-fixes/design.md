# Design Document

## Overview

This design addresses two critical issues in the AWS Lightsail deployment setup script:

1. **S3 Bucket Name Validation**: Implement comprehensive validation of S3 bucket names against AWS naming rules before deployment configuration
2. **Smart Entry Point Detection**: Implement intelligent detection of existing application entry points to avoid creating redundant files

The solution involves adding a validation function for bucket names and enhancing the entry point detection logic in the project analysis module. These changes will be integrated into the existing modular setup script architecture without breaking backward compatibility.

## Architecture

### Module Organization

The implementation will span three existing modules:

1. **01-utils.sh**: Add `validate_bucket_name()` function for reusable validation logic
2. **03-project-analysis.sh**: Enhance `detect_entry_point()` function for comprehensive entry point detection
3. **08-interactive.sh**: Integrate validation and detection into the interactive configuration flow

### Data Flow

```
User Input (Bucket Name)
    ↓
validate_bucket_name() [01-utils.sh]
    ↓
[Valid] → Continue with configuration
[Invalid] → Display error → Re-prompt user
    ↓
create_deployment_config() [06-config-generation.sh]
```

```
Application Type Selection
    ↓
detect_entry_point(app_type) [03-project-analysis.sh]
    ↓
[Entry Point Found] → Skip template creation → Display detection message
[No Entry Point] → Create template files
    ↓
create_example_app() [06-config-generation.sh]
```

## Components and Interfaces

### Component 1: Bucket Name Validator

**Location**: `setup/01-utils.sh`

**Function Signature**:
```bash
validate_bucket_name() {
    local bucket_name="$1"
    # Returns: 0 (success) or 1 (failure)
    # Outputs: Error message to stderr on failure
}
```

**Validation Rules** (AWS S3 Bucket Naming Requirements):
- Length: 3-63 characters
- Characters: lowercase letters (a-z), numbers (0-9), hyphens (-), periods (.)
- Must start with lowercase letter or number
- Must end with lowercase letter or number
- No consecutive periods (..)
- No IP address format (e.g., 192.168.1.1)
- No uppercase letters
- No underscores

**Error Message Format**:
```
❌ Invalid bucket name: {bucket_name}
   Reason: {specific_violation}
   
   AWS S3 bucket naming rules:
   • 3-63 characters long
   • Lowercase letters, numbers, hyphens, and periods only
   • Must start and end with letter or number
   • No consecutive periods
   • No IP address format
   
   Example: my-app-bucket-2024
```

### Component 2: Entry Point Detector

**Location**: `setup/03-project-analysis.sh`

**Function Signature**:
```bash
detect_entry_point() {
    local app_type="$1"
    # Returns: Path to entry point file or empty string
    # Outputs: Entry point path to stdout
}
```

**Detection Priority** (searched in order):

For Node.js applications:
1. `server.js` (root)
2. `index.js` (root)
3. `main.js` (root)
4. `app.js` (root)
5. `server/server.js`
6. `server/index.js`
7. `src/server.js`
8. `src/index.js`
9. `src/app.js`

For Python applications:
1. `app.py` (root)
2. `main.py` (root)
3. `server.py` (root)
4. `src/app.py`
5. `src/main.py`

For PHP applications:
1. `index.php` (root)
2. `app.php` (root)
3. `public/index.php`

**Output Format**:
```
✓ Detected existing entry point: {path}
  Skipping template file creation
```

### Component 3: Interactive Configuration Integration

**Location**: `setup/08-interactive.sh`

**Integration Points**:

1. **Bucket Name Input** (line ~561):
```bash
# Before:
BUCKET_NAME=$(get_input "Enter bucket name" "${APP_TYPE}-bucket-$(date +%s)")

# After:
while true; do
    BUCKET_NAME=$(get_input "Enter bucket name" "${APP_TYPE}-bucket-$(date +%s)")
    if validate_bucket_name "$BUCKET_NAME"; then
        break
    fi
done
```

2. **Automated Mode Validation** (line ~513):
```bash
# Before:
if [[ "$ENABLE_BUCKET" == "true" && -z "$BUCKET_NAME" ]]; then
    BUCKET_NAME="${APP_TYPE}-bucket-$(date +%s)"
fi

# After:
if [[ "$ENABLE_BUCKET" == "true" && -z "$BUCKET_NAME" ]]; then
    BUCKET_NAME="${APP_TYPE}-bucket-$(date +%s)"
fi
if [[ "$ENABLE_BUCKET" == "true" ]]; then
    if ! validate_bucket_name "$BUCKET_NAME"; then
        echo -e "${RED}❌ Invalid BUCKET_NAME environment variable${NC}" >&2
        echo -e "${YELLOW}Set BUCKET_NAME to a valid S3 bucket name${NC}" >&2
        exit 1
    fi
fi
```

### Component 4: Template Creation Logic Enhancement

**Location**: `setup/06-config-generation.sh`

**Integration Point** (line ~1070):
```bash
# Before:
if [[ -z "$existing_entry_point" ]] || [[ "$CREATE_TEMPLATES" == "true" ]]; then
    # Create template files
    if create_file_if_not_exists "app.js"; then
        # ... create app.js
    fi
fi

# After:
local detected_entry=$(detect_entry_point "$app_type")
if [[ -n "$detected_entry" ]]; then
    echo -e "${GREEN}✓ Detected existing entry point: $detected_entry${NC}"
    echo -e "${BLUE}  Skipping template file creation${NC}"
elif [[ "$CREATE_TEMPLATES" == "true" ]]; then
    # Create template files
    if create_file_if_not_exists "app.js"; then
        # ... create app.js
    fi
fi
```

## Data Models

### Validation Result

```bash
# Success case
return 0

# Failure case
return 1
# stderr: "❌ Invalid bucket name: {name}\n   Reason: {reason}\n   ..."
```

### Entry Point Detection Result

```bash
# Entry point found
echo "/path/to/entry/point.js"
return 0

# No entry point found
echo ""
return 0
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Bucket Name Validation Completeness

*For any* string input, the validate_bucket_name function should either accept it as valid (returning 0) or reject it with a specific error message (returning 1), and the decision should be consistent with AWS S3 naming rules.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11**

### Property 2: Valid Bucket Names Are Accepted

*For any* bucket name that conforms to all AWS S3 naming rules (3-63 chars, lowercase alphanumeric with hyphens/periods, starts/ends with alphanumeric, no consecutive periods, not IP format), the validate_bucket_name function should return success (0).

**Validates: Requirements 1.11**

### Property 3: Invalid Bucket Names Are Rejected

*For any* bucket name that violates at least one AWS S3 naming rule, the validate_bucket_name function should return failure (1) and output an error message describing the violation.

**Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10**

### Property 4: Entry Point Detection Finds Existing Files

*For any* application type and any existing entry point file in the search paths, the detect_entry_point function should return the path to the first matching file in priority order.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4**

### Property 5: Entry Point Detection Returns Empty for Missing Files

*For any* application type where no entry point files exist in any of the search paths, the detect_entry_point function should return an empty string.

**Validates: Requirements 2.9, 3.7, 4.5**

### Property 6: Template Creation Skipped When Entry Point Exists

*For any* application type where an entry point is detected, the create_example_app function should not create a new template file for that entry point.

**Validates: Requirements 2.1, 2.10, 2.11, 3.1, 3.8, 4.1, 4.6**

### Property 7: Validation Error Messages Are Descriptive

*For any* invalid bucket name, the error message should include the specific rule violated, the general AWS naming rules, and an example of a valid name.

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 8: Interactive Mode Re-prompts on Validation Failure

*For any* invalid bucket name entered in interactive mode, the setup script should display an error and re-prompt the user until a valid name is provided.

**Validates: Requirements 5.4**

### Property 9: Automated Mode Exits on Validation Failure

*For any* invalid BUCKET_NAME environment variable in automated mode, the setup script should exit with a non-zero status code and display an error message.

**Validates: Requirements 5.5, 5.6**

## Error Handling

### Validation Errors

**Bucket Name Validation Failures**:
- Display error message in red with specific violation
- In interactive mode: re-prompt user
- In automated mode: exit with status code 1

**Entry Point Detection Failures**:
- If file system is inaccessible: log warning and proceed with template creation
- If multiple entry points found: use first in priority order
- No error state for "no entry point found" - this is expected behavior

### Edge Cases

1. **Empty bucket name**: Treated as invalid (length < 3)
2. **Whitespace in bucket name**: Treated as invalid (contains invalid characters)
3. **Bucket name with mixed case**: Treated as invalid (contains uppercase)
4. **Entry point file exists but is empty**: Still detected as existing entry point
5. **Symbolic links to entry points**: Followed and detected as existing files
6. **Entry point in unexpected location**: Not detected, template created

### Recovery Strategies

1. **Invalid bucket name in interactive mode**: Loop until valid input received
2. **Invalid bucket name in automated mode**: Exit immediately with clear error
3. **File system errors during detection**: Log warning, assume no entry point exists
4. **Permission errors reading entry point**: Log warning, assume no entry point exists

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples and edge cases:

1. **Bucket Name Validation Examples**:
   - Valid names: "my-bucket", "app-bucket-2024", "test.bucket.name"
   - Invalid uppercase: "MyBucket", "APP-BUCKET"
   - Invalid underscores: "my_bucket", "app_bucket_2024"
   - Invalid length: "ab", "a-very-long-bucket-name-that-exceeds-the-maximum-allowed-length-limit"
   - Invalid start/end: "-bucket", "bucket-", ".bucket", "bucket."
   - Invalid consecutive periods: "bucket..name"
   - Invalid IP format: "192.168.1.1"
   - Invalid characters: "bucket@name", "bucket#123"

2. **Entry Point Detection Examples**:
   - Node.js: server.js exists, index.js exists, both exist (priority)
   - Python: app.py exists, main.py exists, both exist (priority)
   - PHP: index.php exists, public/index.php exists, both exist (priority)
   - No entry points exist for each type

3. **Integration Examples**:
   - Interactive mode with invalid then valid bucket name
   - Automated mode with invalid bucket name (should exit)
   - Template creation skipped when entry point exists
   - Template creation proceeds when no entry point exists

### Property-Based Tests

Property-based tests will verify universal properties across randomized inputs:

1. **Property Test for Bucket Name Validation**:
   - Generate random strings with various characteristics
   - Verify that validation decision matches AWS rules
   - Verify that error messages are always provided for invalid names
   - Minimum 100 iterations

2. **Property Test for Entry Point Detection**:
   - Generate random file system states (files present/absent)
   - Verify that detection returns first match in priority order
   - Verify that empty string returned when no matches
   - Minimum 100 iterations

3. **Property Test for Template Creation Logic**:
   - Generate random combinations of existing entry points
   - Verify that templates are never created when entry points exist
   - Verify that templates are always created when no entry points exist
   - Minimum 100 iterations

### Test Configuration

- Property tests: Minimum 100 iterations per test
- Each property test tagged with: **Feature: setup-validation-and-entrypoint-fixes, Property {number}: {property_text}**
- Unit tests: Focus on specific examples and edge cases
- Integration tests: Test end-to-end workflows in both interactive and automated modes

### Test Environment

- Tests will use temporary directories for file system operations
- Tests will mock user input for interactive mode testing
- Tests will set environment variables for automated mode testing
- Tests will capture stdout/stderr for validation message verification
