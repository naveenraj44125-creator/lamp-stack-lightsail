# Quick Reference Guide

## Common Tasks

### Fix a Bug in User Input
```bash
# Edit the UI module
vim setup/02-ui.sh

# Test the fix
bash -c '
source setup/00-variables.sh
source setup/01-utils.sh  
source setup/02-ui.sh
result=$(get_yes_no "Test prompt?" "true")
echo "Result: $result"
'
```

### Add a New Project Detection
```bash
# Edit the analysis module
vim setup/03-project-analysis.sh

# Add your detection logic to analyze_project_for_recommendations()
# Test it
bash -c '
source setup/00-variables.sh
source setup/03-project-analysis.sh
analyze_project_for_recommendations "."
echo "Detected: $RECOMMENDED_APP_TYPE"
'
```

### Update GitHub Integration
```bash
# Edit the GitHub module
vim setup/04-github.sh

# Test specific function
bash -c '
source setup/00-variables.sh
source setup/04-github.sh
create_gitignore
cat .gitignore
'
```

### Add New AWS Resource
```bash
# Edit the AWS module
vim setup/05-aws.sh

# Add your function
create_lightsail_database() {
    echo "Creating database..."
}

# Source and test
source setup/05-aws.sh
create_lightsail_database
```

## Module Cheat Sheet

| Task | Module | Function |
|------|--------|----------|
| Get user input | `02-ui.sh` | `get_input()` |
| Yes/no prompt | `02-ui.sh` | `get_yes_no()` |
| Menu selection | `02-ui.sh` | `select_option()` |
| Detect app type | `03-project-analysis.sh` | `analyze_project_for_recommendations()` |
| Find health endpoint | `03-project-analysis.sh` | `detect_health_endpoints()` |
| Create GitHub repo | `04-github.sh` | `create_github_repo_if_needed()` |
| Create .gitignore | `04-github.sh` | `create_gitignore()` |
| Create IAM role | `05-aws.sh` | `create_iam_role_if_needed()` |
| Setup OIDC | `05-aws.sh` | `setup_github_oidc()` |

## Testing Patterns

### Test a Single Function
```bash
bash -c '
source setup/00-variables.sh
source setup/01-utils.sh
check_prerequisites
'
```

### Test with Mock Data
```bash
bash -c '
source setup/00-variables.sh
RECOMMENDED_APP_TYPE="nodejs"
RECOMMENDED_DATABASE="mysql"
source setup/02-ui.sh
result=$(select_option "Choose:" "nodejs" "app_type" "nodejs" "python" "lamp")
echo "Selected: $result"
'
```

### Test Module Dependencies
```bash
# This will fail if dependencies are missing
bash -c '
source setup/03-project-analysis.sh  # Needs 00-variables.sh
'

# This will work
bash -c '
source setup/00-variables.sh
source setup/03-project-analysis.sh
'
```

## Debugging Commands

### Check Syntax
```bash
# Check all modules
for f in setup/*.sh; do
    echo "Checking $f..."
    bash -n "$f" || echo "Error in $f"
done
```

### Find Function Definition
```bash
# Find where a function is defined
grep -r "^function_name()" setup/
```

### Count Lines
```bash
# See module sizes
wc -l setup/*.sh
```

### Check Dependencies
```bash
# See what functions a module uses
grep -o "[a-z_]*(" setup/03-project-analysis.sh | sort -u
```

## Common Fixes

### Fix "Command Not Found"
```bash
# Problem: Function not found
# Solution: Check module is sourced in setup.sh

# Add to setup.sh if missing:
source "$SCRIPT_DIR/setup/XX-your-module.sh"
```

### Fix Syntax Error
```bash
# Problem: Syntax error in module
# Solution: Check if/fi and case/esac pairs

# Count if statements
grep -c "^\s*if" setup/02-ui.sh

# Count fi statements  
grep -c "^\s*fi" setup/02-ui.sh

# Should be equal
```

### Fix Variable Not Set
```bash
# Problem: Variable undefined
# Solution: Check it's in 00-variables.sh

# Add to setup/00-variables.sh:
MY_VARIABLE=${MY_VARIABLE:-default_value}
```

## File Structure

```
.
├── setup.sh                    # Main script (run this)
├── setup/
│   ├── 00-variables.sh        # Config & variables
│   ├── 01-utils.sh            # Utility functions
│   ├── 02-ui.sh               # User interface
│   ├── 03-project-analysis.sh # Project detection
│   ├── 04-github.sh           # GitHub operations
│   ├── 05-aws.sh              # AWS operations
│   ├── README.md              # Detailed docs
│   └── QUICK_REFERENCE.md     # This file
├── MIGRATION_GUIDE.md         # Migration from old script
└── setup-complete-deployment.sh # Old monolithic script
```

## Quick Commands

```bash
# Run setup
./setup.sh

# Run in auto mode
./setup.sh --auto

# Get help
./setup.sh --help

# Test all modules load
bash -c 'source setup.sh && echo "OK"'

# Check syntax of all modules
bash -n setup.sh && echo "Syntax OK"
```

## Environment Variables

```bash
# Set before running
export AUTO_MODE=true
export APP_TYPE=nodejs
export APP_NAME="My App"
export GITHUB_REPO="user/repo"
export AWS_REGION=us-east-1

# Run
./setup.sh --auto
```

## Tips

1. **Always test in isolation** - Test modules individually before running full script
2. **Check dependencies** - Make sure required modules are sourced first
3. **Use descriptive names** - Function names should explain what they do
4. **Add comments** - Explain complex logic
5. **Keep modules focused** - One responsibility per module
6. **Test error cases** - Don't just test the happy path

## Getting Help

1. Check `setup/README.md` for detailed documentation
2. Review `MIGRATION_GUIDE.md` for migration info
3. Look at function comments in module files
4. Test functions individually to understand behavior
