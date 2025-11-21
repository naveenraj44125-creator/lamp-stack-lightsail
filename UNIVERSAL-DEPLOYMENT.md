# Universal Deployment System

A distribution-agnostic deployment system that works with any Linux distribution on AWS Lightsail.

## Features

✅ **Auto-detects OS** - Ubuntu, Amazon Linux, CentOS, Debian, RHEL, etc.
✅ **Auto-detects default user** - ubuntu, ec2-user, centos, admin, bitnami, root
✅ **Auto-detects package manager** - apt-get, yum, dnf, zypper
✅ **Auto-detects service manager** - systemctl, service
✅ **Works with any application type** - PHP, Python, Node.js, React, static sites

## How It Works

### 1. System Detection

The universal deployer automatically detects:

```bash
# OS Information
OS_NAME="Ubuntu"
OS_ID="ubuntu"
OS_VERSION="22.04"

# User Configuration
DEFAULT_USER="ubuntu"  # or ec2-user, centos, etc.

# Package Manager
PKG_MANAGER="apt-get"  # or yum, dnf, zypper

# Service Manager
SERVICE_MANAGER="systemctl"  # or service

# Web Root
WEB_ROOT="/var/www/html"  # or /usr/share/nginx/html
```

### 2. Deployment Process

1. **Detect System** - Identifies OS, user, and tools
2. **Upload Package** - Transfers application files
3. **Extract & Deploy** - Unpacks to correct location
4. **Configure** - Sets up services based on app type
5. **Restart Services** - Restarts web server and app services
6. **Verify** - Checks deployment success

## Usage

### Manual Deployment

```bash
python workflows/deploy-post-steps-universal.py \
  --instance-name my-instance \
  --region us-east-1 \
  --package-file app.tar.gz \
  --config-file deployment.config.yml
```

### GitHub Actions Workflow

```yaml
- name: Deploy with universal script
  run: |
    python workflows/deploy-post-steps-universal.py \
      --instance-name "${{ inputs.instance_name }}" \
      --region "${{ secrets.AWS_REGION }}" \
      --package-file app.tar.gz
```

### Workflow Dispatch

Use the "Universal Deployment" workflow from GitHub Actions:

1. Go to Actions tab
2. Select "Universal Deployment"
3. Click "Run workflow"
4. Enter:
   - Instance name
   - Application type (php/python/nodejs/react/static)
   - Config file (optional)

## Supported Distributions

### Tested On

- ✅ Ubuntu 20.04, 22.04, 24.04
- ✅ Amazon Linux 2, 2023
- ✅ CentOS 7, 8, 9
- ✅ Debian 10, 11, 12
- ✅ RHEL 8, 9

### Should Work On

- Fedora
- Rocky Linux
- AlmaLinux
- openSUSE

## Application Types

### PHP Applications

- Detects Apache or Nginx
- Enables required PHP modules
- Configures web server
- Restarts services

### Python Applications

- Installs dependencies from requirements.txt
- Creates systemd service
- Configures application port
- Manages process lifecycle

### Node.js Applications

- Runs npm install
- Creates systemd service
- Configures application port
- Manages process lifecycle

### React Applications

- Deploys static build files
- Configures web server
- Sets up routing

### Static Sites

- Deploys files to web root
- Configures web server
- Sets permissions

## Configuration

### Config File Format

```yaml
application:
  name: "My App"
  type: "python"  # php, python, nodejs, react, static
  version: "1.0.0"
  deploy_path: "/var/www/html"
  port: 5000

instance:
  name: "my-instance"
  region: "us-east-1"

dependencies:
  - apache
  - php
  - mysql
```

## Advantages Over Distribution-Specific Scripts

| Feature | Universal | Distribution-Specific |
|---------|-----------|----------------------|
| Works on any OS | ✅ Yes | ❌ No |
| Auto-detects user | ✅ Yes | ❌ Hardcoded |
| Auto-detects package manager | ✅ Yes | ❌ Hardcoded |
| Single script for all apps | ✅ Yes | ❌ Multiple scripts |
| Easy to maintain | ✅ Yes | ❌ Complex |

## Troubleshooting

### Detection Issues

If system detection fails, the script falls back to safe defaults:
- User: ubuntu
- Package Manager: apt-get
- Service Manager: systemctl
- Web Root: /var/www/html

### Permission Issues

The script automatically uses the detected default user for file ownership.

### Service Issues

The script detects the service manager and uses appropriate commands:
- systemctl (modern systems)
- service (older systems)

## Examples

### Deploy PHP Application

```bash
python workflows/deploy-post-steps-universal.py \
  --instance-name lamp-stack \
  --package-file lamp-app.tar.gz
```

### Deploy Python Application

```bash
python workflows/deploy-post-steps-universal.py \
  --instance-name python-app \
  --package-file python-app.tar.gz \
  --config-file deployment-python.config.yml
```

### Deploy Node.js Application

```bash
python workflows/deploy-post-steps-universal.py \
  --instance-name nodejs-app \
  --package-file nodejs-app.tar.gz
```

## Migration from Distribution-Specific Scripts

1. Replace your existing deployment script with the universal script
2. Remove hardcoded user names (ubuntu, ec2-user, etc.)
3. Remove hardcoded package manager commands
4. Use the universal workflow instead of distribution-specific workflows

## Contributing

To add support for a new distribution:

1. Add detection logic in `_detect_system_config()`
2. Add package manager commands
3. Add service manager commands
4. Test on the new distribution

## License

MIT License - See LICENSE file for details
