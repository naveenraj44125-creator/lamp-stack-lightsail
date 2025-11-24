# Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. SSH Connection Timeouts

**Symptoms:**
```
ssh: connect to host X.X.X.X port 22: Connection timed out
⏰ Command timed out after 180 seconds
```

**Causes:**
- Instance firewall (UFW) blocking SSH during configuration
- `apt-get update` taking too long
- Instance not fully booted
- SSH service not running

**Solutions:**

#### Quick Fix - Reboot Instance
```bash
aws lightsail reboot-instance --instance-name <instance-name> --region us-east-1
```

#### Check Connectivity
```bash
./check-instance-connectivity.sh <instance-name>
```

#### Fix UFW Firewall (via Lightsail Browser SSH)
1. Go to AWS Lightsail Console
2. Click on your instance
3. Click "Connect using SSH" (browser-based)
4. Run these commands:
```bash
sudo ufw disable
sudo ufw --force reset
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
```

### 2. OIDC Authentication Failures

**Symptoms:**
```
Could not assume role with OIDC: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**Causes:**
- Wrong role ARN in workflow
- Trust policy not configured correctly
- Role doesn't exist

**Solutions:**

#### Verify Role Name
Check that workflows use the correct role:
```yaml
role-to-assume: arn:aws:iam::257429339749:role/GitHubActionsRoleNew
```

#### Update Trust Policy
```bash
./setup-github-oidc.sh
# Choose option 1 to update existing role
```

### 3. Dependency Installation Failures

**Symptoms:**
```
❌ git installation failed
❌ nginx installation failed
⏰ Command timed out after 180 seconds
```

**Causes:**
- Multiple `apt-get update` commands running sequentially
- Slow package repository mirrors
- Network issues
- Insufficient timeout values

**Solutions:**

#### Increase Timeouts
Edit `workflows/dependency_manager.py`:
```python
# Change timeout from 180 to 300 seconds
success, output = self.client.run_command(install_script, timeout=300)
```

#### Optimize apt-get Updates
Run `apt-get update` once at the beginning instead of for each dependency.

#### Use Faster Mirrors
Configure faster apt mirrors in the instance.

### 4. Some Workflows Pass, Some Fail

**Symptoms:**
- "Deploy to AWS" workflow passes (authentication works)
- Deployment workflows fail (SSH timeouts)

**Explanation:**
- Authentication workflows only test AWS credentials
- Deployment workflows need SSH access to instances
- SSH access can be blocked by firewalls or network issues

**Solutions:**
1. Check instance connectivity: `./check-instance-connectivity.sh`
2. Verify firewall rules allow SSH from anywhere (0.0.0.0/0)
3. Reboot instance if needed
4. Check UFW firewall on instance

### 5. Instance Not Accessible

**Symptoms:**
```
Cannot connect to instance from local machine
Connection timed out
```

**Diagnostic Steps:**

1. **Check Instance Status:**
```bash
aws lightsail get-instance --instance-name <name> --region us-east-1
```

2. **Check Port States:**
```bash
aws lightsail get-instance-port-states --instance-name <name> --region us-east-1
```

3. **Test Connectivity:**
```bash
nc -zv <ip-address> 22
nc -zv <ip-address> 80
```

4. **Check from GitHub Actions:**
Add this step to workflow:
```yaml
- name: Test connectivity
  run: |
    nc -zv ${{ secrets.INSTANCE_IP }} 22 || echo "Cannot reach instance"
```

## Prevention Best Practices

### 1. Firewall Configuration
- Always allow SSH (port 22) before enabling UFW
- Test connectivity after firewall changes
- Use `--force` flag carefully with UFW

### 2. Timeout Management
- Set appropriate timeouts for long-running commands
- Use longer timeouts for package installations (300s+)
- Consider splitting large installations into smaller steps

### 3. Error Handling
- Always check command exit codes
- Log detailed output for debugging
- Implement retry logic for transient failures

### 4. Testing
- Test deployments on a staging instance first
- Verify SSH access before running full deployment
- Use browser-based SSH as backup access method

## Useful Commands

### Check All Instances
```bash
aws lightsail get-instances --region us-east-1 --query 'instances[].[name,state.name,publicIpAddress]' --output table
```

### Reboot Instance
```bash
aws lightsail reboot-instance --instance-name <name> --region us-east-1
```

### Open Firewall Ports
```bash
aws lightsail open-instance-public-ports \
  --instance-name <name> \
  --port-info fromPort=22,toPort=22,protocol=tcp \
  --region us-east-1
```

### Get Instance Logs
```bash
aws lightsail get-instance-access-details \
  --instance-name <name> \
  --region us-east-1
```

## Emergency Access

If you lose SSH access:

1. **Use Lightsail Browser SSH:**
   - Go to AWS Lightsail Console
   - Click instance → "Connect using SSH"
   - This bypasses network/firewall issues

2. **Create Instance Snapshot:**
   - Snapshot current instance
   - Create new instance from snapshot
   - Configure firewall correctly

3. **Use AWS Systems Manager:**
   - If SSM agent is installed
   - Connect via Session Manager

## Monitoring

### Check Workflow Status
```bash
gh run list --limit 10
gh run view <run-id> --log-failed
```

### Watch Workflow in Real-time
```bash
gh run watch
```

### Check Instance Metrics
```bash
aws lightsail get-instance-metric-data \
  --instance-name <name> \
  --metric-name CPUUtilization \
  --period 300 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --unit Percent \
  --statistics Average \
  --region us-east-1
```

## Getting Help

1. Check workflow logs: `gh run view <run-id> --log-failed`
2. Check instance connectivity: `./check-instance-connectivity.sh`
3. Review this troubleshooting guide
4. Check AWS Lightsail Console for instance status
5. Use browser-based SSH for emergency access
