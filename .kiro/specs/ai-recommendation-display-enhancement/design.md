# Design Document: AI Recommendation Display Enhancement

## Overview

This design enhances the setup script's interactive mode to display AI recommendations for database, bucket, and health endpoint selections. The enhancement leverages existing recommendation detection in `analyze_project_for_recommendations()` and extends the display logic to show "★ AI" markers consistently across all configuration steps.

The implementation focuses on three key areas:
1. Extending the `select_option()` function to support database recommendations
2. Modifying the bucket prompt to display AI recommendations
3. Enhancing the health endpoint prompt to show detected endpoints with AI markers

## Architecture

### Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│  analyze_project_for_recommendations()                      │
│  (setup/03-project-analysis.sh)                             │
│                                                              │
│  Detects:                                                    │
│  - RECOMMENDED_DATABASE                                      │
│  - RECOMMENDED_BUCKET                                        │
│  - RECOMMENDED_HEALTH_ENDPOINT                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Sets global variables
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  main() - Interactive Mode                                   │
│  (setup/08-interactive.sh)                                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Database Selection                                     │ │
│  │ - Calls select_option() with "database" type          │ │
│  │ - Displays ★ AI marker for RECOMMENDED_DATABASE       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Bucket Configuration                                   │ │
│  │ - Checks RECOMMENDED_BUCKET                            │ │
│  │ - Shows AI message if true                             │ │
│  │ - Sets default based on recommendation                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Health Endpoint Detection                              │ │
│  │ - Checks RECOMMENDED_HEALTH_ENDPOINT                   │ │
│  │ - Shows detected endpoint with ★ AI marker             │ │
│  │ - Prompts user to confirm usage                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
setup/
├── 02-ui.sh                    # Contains select_option() function
│   └── select_option()         # Modified to support "database" type
├── 03-project-analysis.sh      # Already detects recommendations
│   └── analyze_project_for_recommendations()
└── 08-interactive.sh           # Main interactive flow
    └── main()                  # Modified to display AI markers
```

## Components and Interfaces

### 1. select_option() Function Enhancement

**Location:** `setup/02-ui.sh`

**Current Behavior:**
- Supports `recommendation_type` parameter with values: "app_type", "bundle"
- Displays "★ AI" marker for matching recommendations
- Updates default selection to AI-recommended option

**Required Changes:**
- Add support for `recommendation_type` value: "database"
- Map "database" type to `RECOMMENDED_DATABASE` variable
- Display "★ AI" marker when database option matches recommendation

**Function Signature:**
```bash
select_option() {
    local prompt="$1"
    local default="$2"
    local recommendation_type="${3:-}"  # app_type, database, bundle, bucket
    shift 3 2>/dev/null || shift 2
    local options=("$@")
    # ...
}
```

**Implementation Logic:**
```bash
# Determine the AI-recommended option based on type
local ai_recommended=""
case "$recommendation_type" in
    "app_type")
        ai_recommended="$RECOMMENDED_APP_TYPE"
        ;;
    "database")
        ai_recommended="$RECOMMENDED_DATABASE"
        ;;
    "bundle")
        ai_recommended="$RECOMMENDED_BUNDLE"
        ;;
esac
```

### 2. Database Selection Enhancement

**Location:** `setup/08-interactive.sh` - Database Configuration section

**Current Code:**
```bash
DB_TYPES=("mysql" "postgresql" "mongodb" "none")
DB_TYPE=$(select_option "Choose database type:" "4" "${DB_TYPES[@]}")
```

**Modified Code:**
```bash
DB_TYPES=("mysql" "postgresql" "mongodb" "none")
DB_TYPE=$(select_option "Choose database type:" "4" "database" "${DB_TYPES[@]}")
```

**Changes:**
- Add "database" as the third parameter to `select_option()`
- This enables the function to check `RECOMMENDED_DATABASE` and display the AI marker

### 3. Bucket Configuration Enhancement

**Location:** `setup/08-interactive.sh` - Storage Configuration section

**Current Code:**
```bash
ENABLE_BUCKET=$(get_yes_no "Enable Lightsail bucket for file storage?" "false")
```

**Modified Code:**
```bash
# Show AI recommendation for bucket if detected
local bucket_default="false"
if [ "$RECOMMENDED_BUCKET" == "true" ]; then
    echo -e "${YELLOW}★ AI detected file upload patterns in your code - bucket recommended${NC}"
    echo ""
    bucket_default="true"
fi

ENABLE_BUCKET=$(get_yes_no "Enable Lightsail bucket for file storage?" "$bucket_default")
```

**Changes:**
- Check `RECOMMENDED_BUCKET` before prompting
- Display AI message when recommendation exists
- Set default to "true" when bucket is recommended

### 4. Health Endpoint Detection Enhancement

**Location:** `setup/08-interactive.sh` - Health Check Configuration section

**Current Code:**
```bash
# Use recommended health endpoint from analysis if available
if [[ -n "$RECOMMENDED_HEALTH_ENDPOINT" ]]; then
    echo -e "${GREEN}★ AI detected health endpoint in your code: ${RECOMMENDED_HEALTH_ENDPOINT}${NC}"
    echo ""
    USE_DETECTED=$(get_yes_no "Use detected endpoint for health checks?" "true")
    if [[ "$USE_DETECTED" == "true" ]]; then
        VERIFICATION_ENDPOINT="$RECOMMENDED_HEALTH_ENDPOINT"
        echo -e "${GREEN}✓ Will verify deployment using: $VERIFICATION_ENDPOINT${NC}"
    else
        VERIFICATION_ENDPOINT=$(get_input "Enter verification endpoint path" "/")
        echo -e "${GREEN}✓ Will verify deployment using: $VERIFICATION_ENDPOINT${NC}"
    fi
else
    # ... existing fallback logic
fi
```

**Status:** Already implemented correctly!

**Changes Required:** 
- Change color from `${GREEN}` to `${YELLOW}` for consistency with other AI markers
- This ensures all "★ AI" markers use the same yellow color

**Modified Code:**
```bash
if [[ -n "$RECOMMENDED_HEALTH_ENDPOINT" ]]; then
    echo -e "${YELLOW}★ AI detected health endpoint in your code: ${RECOMMENDED_HEALTH_ENDPOINT}${NC}"
    # ... rest remains the same
```

## Data Models

### Recommendation Variables

These global variables are set by `analyze_project_for_recommendations()`:

```bash
# Application type recommendation
RECOMMENDED_APP_TYPE=""           # Values: "lamp", "nodejs", "python", "react", "docker", "nginx"

# Database recommendation
RECOMMENDED_DATABASE="none"       # Values: "mysql", "postgresql", "mongodb", "none"

# Instance size recommendation
RECOMMENDED_BUNDLE="micro_3_0"    # Values: "nano_3_0", "micro_3_0", "small_3_0", "medium_3_0", "large_3_0"

# Bucket recommendation
RECOMMENDED_BUCKET="false"        # Values: "true", "false"

# Health endpoint recommendation
RECOMMENDED_HEALTH_ENDPOINT=""    # Values: any valid endpoint path (e.g., "/health", "/api/health")

# Analysis confidence
ANALYSIS_CONFIDENCE=0             # Values: 0-100 (percentage)
```

### Menu Option Format

The `select_option()` function displays options in this format:

```
┌─────────────────────────────────────────────────────────────┐
│ Choose database type:                                        │
├─────────────────────────────────────────────────────────────┤
│ →  1. mysql        │ Relational database           ★ AI     │
│    2. postgresql   │ Advanced relational DB                 │
│    3. mongodb      │ NoSQL document database                │
│    4. none         │ No database needed                     │
└─────────────────────────────────────────────────────────────┘
```

Where:
- `→` indicates the default selection
- `★ AI` indicates the AI-recommended option
- The default automatically moves to the AI-recommended option

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Database AI Marker Display

*For any* valid database type (mysql, postgresql, mongodb), when `RECOMMENDED_DATABASE` is set to that type and the database selection menu is displayed, the menu output should contain the "★ AI" marker next to the matching database option.

**Validates: Requirements 1.1, 1.2, 1.3, 6.2**

### Property 2: No Marker for None Database

*For any* database selection menu display, when `RECOMMENDED_DATABASE` is set to "none" or is empty, the menu output should not contain any "★ AI" marker.

**Validates: Requirements 1.4, 6.4**

### Property 3: Default Selection Updates to AI Recommendation

*For any* database type that has an AI recommendation, when the database selection menu is displayed, the default selection index should point to the recommended database option.

**Validates: Requirements 1.5, 6.3**

### Property 4: Bucket Recommendation Message Display

*For any* bucket configuration prompt, when `RECOMMENDED_BUCKET` is set to "true", the output should contain a message with the "★ AI" marker indicating that file upload patterns were detected.

**Validates: Requirements 2.1, 2.4**

### Property 5: Bucket Default Based on Recommendation

*For any* bucket enable prompt, when `RECOMMENDED_BUCKET` is "true", the default value should be "true", and when `RECOMMENDED_BUCKET` is "false" or empty, the default value should be "false".

**Validates: Requirements 2.2, 2.3**

### Property 6: Health Endpoint Detection Display

*For any* health check configuration prompt, when `RECOMMENDED_HEALTH_ENDPOINT` is set to a non-empty value, the output should display that exact endpoint path with a "★ AI" marker and prompt the user to confirm usage.

**Validates: Requirements 3.1, 3.2, 3.5**

### Property 7: Health Endpoint Assignment on Confirmation

*For any* detected health endpoint, when the user confirms using it, the `VERIFICATION_ENDPOINT` variable should be set to the exact value of `RECOMMENDED_HEALTH_ENDPOINT`.

**Validates: Requirements 3.3**

### Property 8: Health Endpoint Fallback Behavior

*For any* health check configuration prompt, when `RECOMMENDED_HEALTH_ENDPOINT` is empty or unset, the system should display the default custom endpoint prompt without any AI marker.

**Validates: Requirements 3.4**

### Property 9: Visual Format Consistency

*For all* AI recommendation displays (database, bucket, health endpoint), the visual format (box-drawing characters, layout structure, marker symbol) should match the existing format used for app type and instance size recommendations.

**Validates: Requirements 4.1, 4.3**

### Property 10: AI Marker Color Consistency

*For all* "★ AI" markers displayed in the setup script, the color should be `${YELLOW}` to ensure visual consistency across all recommendation types.

**Validates: Requirements 4.2, 4.4**

### Property 11: Automated Mode Bypasses Interactive Prompts

*For any* configuration step (database, bucket, health endpoint), when `FULLY_AUTOMATED` mode is enabled, the system should not call interactive prompt functions (select_option, get_yes_no, get_input).

**Validates: Requirements 5.1**

### Property 12: Environment Variables Override AI Recommendations

*For any* configuration value in automated mode, when both an environment variable and an AI recommendation are set, the environment variable value should be used.

**Validates: Requirements 5.2**

### Property 13: AI Recommendations as Automated Mode Defaults

*For any* configuration value in automated mode, when the environment variable is not set but an AI recommendation exists, the AI recommendation value should be used as the default.

**Validates: Requirements 5.3**

### Property 14: Automated Mode Backward Compatibility

*For all* existing automated mode test cases, when executed with the enhanced AI recommendation display, they should produce the same configuration results as before the enhancement.

**Validates: Requirements 5.4**

### Property 15: Database Recommendation Type Parameter

*For any* call to `select_option()` with `recommendation_type` parameter set to "database", the function should read and use the `RECOMMENDED_DATABASE` variable to determine which option to mark with "★ AI".

**Validates: Requirements 6.1**

## Error Handling

### Invalid Recommendation Values

**Scenario:** `RECOMMENDED_DATABASE` is set to an invalid value not in the menu options

**Handling:**
- The `select_option()` function should gracefully handle this by not displaying any AI marker
- The default selection should remain at the original default index
- No error message should be displayed to the user

**Implementation:**
```bash
# Check if this is the AI-recommended option
if [ -n "$ai_recommended" ] && [ "$option" == "$ai_recommended" ]; then
    ai_marker=" ${YELLOW}★ AI${NC}"
    # Update default to AI recommendation
    default=$((i+1))
fi
```

This logic only adds the marker if there's an exact match, so invalid values are silently ignored.

### Missing Recommendation Variables

**Scenario:** Recommendation variables are not set (undefined)

**Handling:**
- Bash treats undefined variables as empty strings in string comparisons
- The `[ -n "$ai_recommended" ]` check will fail for undefined variables
- No AI marker will be displayed
- Default behavior continues normally

### Automated Mode with Missing Environment Variables

**Scenario:** `FULLY_AUTOMATED=true` but required environment variables are missing

**Handling:**
- The script should fall back to AI recommendations if available
- If no AI recommendations exist, use hardcoded defaults
- Validation should occur after all values are set to catch missing required values

**Example:**
```bash
if [[ "$FULLY_AUTOMATED" == "true" ]]; then
    DB_TYPE="${DATABASE_TYPE:-$RECOMMENDED_DATABASE}"
    DB_TYPE="${DB_TYPE:-none}"  # Final fallback
fi
```

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** will verify:
- Specific examples of AI marker display for each database type
- Edge cases like empty recommendations and invalid values
- Integration between analysis and display functions
- Automated mode behavior with various environment variable combinations

**Property-Based Tests** will verify:
- Universal properties across all database types and recommendation values
- Consistency of visual formatting across all recommendation displays
- Correct behavior across all possible combinations of recommendation variables

### Property-Based Testing Configuration

**Library:** Use `bats` (Bash Automated Testing System) with custom property test helpers

**Test Configuration:**
- Minimum 100 iterations per property test
- Each test must reference its design document property
- Tag format: **Feature: ai-recommendation-display-enhancement, Property {number}: {property_text}**

### Test Categories

#### 1. Display Logic Tests (Unit + Property)

**Unit Tests:**
- Test database marker display for mysql, postgresql, mongodb
- Test bucket message display when RECOMMENDED_BUCKET=true
- Test health endpoint display with specific endpoint paths
- Test no marker display when recommendations are "none" or empty

**Property Tests:**
- Property 1: Database AI marker display across all valid database types
- Property 2: No marker for none database across all menu displays
- Property 4: Bucket recommendation message display
- Property 6: Health endpoint detection display

#### 2. Default Selection Tests (Unit + Property)

**Unit Tests:**
- Test default changes to mysql when recommended
- Test default remains unchanged when no recommendation
- Test bucket default is true when RECOMMENDED_BUCKET=true

**Property Tests:**
- Property 3: Default selection updates to AI recommendation
- Property 5: Bucket default based on recommendation

#### 3. Visual Consistency Tests (Unit + Property)

**Unit Tests:**
- Compare database marker format to app type marker format
- Verify YELLOW color is used for all markers
- Check box-drawing characters are preserved

**Property Tests:**
- Property 9: Visual format consistency across all displays
- Property 10: AI marker color consistency

#### 4. Automated Mode Tests (Unit + Property)

**Unit Tests:**
- Test automated mode with all env vars set
- Test automated mode with no env vars (uses recommendations)
- Test automated mode with partial env vars
- Run existing automated mode test suite

**Property Tests:**
- Property 11: Automated mode bypasses interactive prompts
- Property 12: Environment variables override AI recommendations
- Property 13: AI recommendations as automated mode defaults
- Property 14: Automated mode backward compatibility

#### 5. Integration Tests (Unit)

**Unit Tests:**
- Test full flow: analysis → database selection → marker display
- Test full flow: analysis → bucket prompt → recommendation message
- Test full flow: analysis → health endpoint → detection display
- Test interaction between multiple recommendations (database + bucket + health)

### Test Implementation Notes

**Mocking Strategy:**
- Mock `select_option()` output to capture menu display
- Mock `get_yes_no()` to simulate user responses
- Mock `analyze_project_for_recommendations()` to set specific recommendation values

**Assertion Strategy:**
- Use regex matching to verify "★ AI" marker presence
- Use string comparison to verify exact endpoint paths
- Use index comparison to verify default selection changes
- Use color code matching to verify YELLOW is used

**Test Data Generation:**
- Generate random database types from valid set
- Generate random endpoint paths (e.g., /health, /api/health, /status)
- Generate random combinations of recommendation variables
- Generate random environment variable configurations for automated mode

### Example Property Test Structure

```bash
# Feature: ai-recommendation-display-enhancement, Property 1: Database AI Marker Display
@test "Property 1: Database marker displays for all valid database types" {
    for iteration in {1..100}; do
        # Generate random database type
        db_types=("mysql" "postgresql" "mongodb")
        random_db="${db_types[$RANDOM % ${#db_types[@]}]}"
        
        # Set recommendation
        export RECOMMENDED_DATABASE="$random_db"
        
        # Capture menu output
        output=$(select_option "Choose database type:" "4" "database" "mysql" "postgresql" "mongodb" "none")
        
        # Verify marker appears next to recommended option
        assert_output_contains "★ AI"
        assert_line_contains "$random_db" "★ AI"
    done
}
```

### Test Coverage Goals

- 100% coverage of all acceptance criteria
- 100% coverage of all correctness properties
- 100% coverage of error handling scenarios
- 100% coverage of automated mode variations
- Backward compatibility with existing test suite

### Continuous Integration

**Pre-commit Checks:**
- Run unit tests for modified functions
- Run visual consistency tests
- Run automated mode compatibility tests

**Pull Request Checks:**
- Run full unit test suite
- Run full property test suite (100 iterations each)
- Run integration tests
- Run existing automated mode test suite
- Verify no regressions in existing functionality

**Post-merge Checks:**
- Run extended property tests (1000 iterations each)
- Run performance tests to ensure no slowdown
- Run end-to-end deployment tests with AI recommendations
