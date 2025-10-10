# LAMP Stack Installation Fix

## Problem Analysis

The GitHub Action was failing during the LAMP stack installation with the error:
```
❌ Failed (exit code: 255)
Error: Warning: Permanently added '98.91.3.69' (ED25519) to the list of known hosts.
client_loop: send disconnect: Broken pipe
```

This indicated SSH connection issues during the installation process.

## Root Causes Identified

1. **SSH Connection Timeout**: The original script executed the entire LAMP installation as one large command, causing SSH timeouts
2. **No Connection Keep-alive**: SSH connections lacked proper keep-alive settings
3. **No Retry Logic**: Connection failures weren't handled with retry mechanisms
4. **Monolithic Installation**: Large script execution increased chances of connection drops

## Solutions Implemented

### 1. Restructured Installation Script (`install-lamp-on-lightsail.py`)

**Before**: Functional approach with basic SSH handling
**After**: Class-based approach following the working `deploy-with-run-command.py` pattern

Key improvements:
- `LightsailLAMPInstaller` class for better organization
- Proper error handling with `ClientError` and `NoCredentialsError`
- Instance state checking before installation
- Modular step-by-step installation process

### 2. Enhanced SSH Connection Handling

**Improved SSH Options**:
```python
ssh_cmd = [
    'ssh', '-i', key_path, '-o', f'CertificateFile={cert_path}',
    '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
    '-o', 'ConnectTimeout=15', '-o', 'IdentitiesOnly=yes',
    f'{ssh_details["username"]}@{ssh_details["ipAddress"]}', command
]
```

### 3. Robust Retry Logic

**New `run_command_with_retry()` method**:
- Detects connection-specific errors (Broken pipe, Connection reset, etc.)
- Implements exponential backoff (10-15 second delays)
- Maximum 3 retry attempts for connection issues
- Smart error classification (connection vs. application errors)

**Connection Errors Handled**:
- "Broken pipe"
- "Connection reset" 
- "Connection timed out"
- "Connection refused"
- "Network is unreachable"
- "Host is down"
- "ssh_exchange_identification"
- "Connection closed by remote host"

### 4. Modular Installation Steps

**Before**: Single large script execution
**After**: 7 separate installation steps:

1. **Fixing broken packages** - Handle any existing package issues
2. **Updating system packages** - Ensure latest package lists
3. **Installing Apache** - Web server installation
4. **Installing MariaDB** - Database server installation  
5. **Installing PHP** - PHP runtime and extensions
6. **Starting services** - Enable and start services
7. **Configuring Apache** - Set permissions and enable modules

Each step:
- Has individual retry logic
- Includes error handling with `set -e`
- Uses `|| true` for non-critical operations
- Has 2-second pause between steps

### 5. Better Error Reporting

- Detailed step-by-step progress logging
- Clear success/failure indicators with emojis
- Comprehensive error output for debugging
- Instance state verification before installation

### 6. Verification Process

Enhanced verification with:
- Apache version check
- MySQL version check  
- PHP version check
- Service status verification
- Retry logic for verification commands

## Expected Results

With these fixes, the GitHub Action should:

1. **Handle Connection Issues**: Automatically retry on SSH connection problems
2. **Provide Better Logging**: Clear progress indicators and error messages
3. **Reduce Failure Rate**: Modular approach reduces chance of complete failure
4. **Faster Recovery**: Quick retry with smart backoff for transient issues
5. **Better Debugging**: Detailed error output for troubleshooting

## Testing Recommendations

1. **Monitor Next Deployment**: Check if the "Broken pipe" error is resolved
2. **Review Logs**: Verify step-by-step progress is visible
3. **Connection Resilience**: Test behavior during network instability
4. **Retry Logic**: Confirm retries occur for connection issues but not for application errors

## Rollback Plan

If issues persist, the original approach can be restored by:
1. Reverting to the previous `install-lamp-on-lightsail.py`
2. Using the original `install-lamp-stack.sh` as a single script
3. Investigating alternative deployment methods (AWS Systems Manager, etc.)

## Additional Improvements for Future

1. **Timeout Configuration**: Make SSH timeouts configurable
2. **Parallel Installation**: Consider parallel package installation where safe
3. **Health Checks**: Add more comprehensive service health verification
4. **Caching**: Cache package lists to reduce installation time
5. **Alternative Protocols**: Consider AWS Systems Manager Session Manager as SSH alternative
