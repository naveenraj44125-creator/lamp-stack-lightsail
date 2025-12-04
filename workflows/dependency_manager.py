#!/usr/bin/env python3
"""
Generic Dependency Manager for AWS Lightsail Deployments
This module handles installation and configuration of various dependencies
based on configuration settings (Apache, MySQL, PHP, Python, Node.js, etc.)
"""

import sys
import json
from typing import Dict, List, Any, Tuple
from config_loader import DeploymentConfig
from lightsail_rds import LightsailRDSManager

class DependencyManager:
    """Manages installation and configuration of application dependencies"""
    
    def __init__(self, lightsail_client, config: DeploymentConfig):
        """
        Initialize dependency manager
        
        Args:
            lightsail_client: Lightsail client instance for running commands
            config: Deployment configuration instance
        """
        self.client = lightsail_client
        self.config = config
        self.installed_dependencies = []
        self.failed_dependencies = []
    
    def get_enabled_dependencies(self) -> List[str]:
        """Get list of enabled dependencies from configuration"""
        dependencies = []
        deps_config = self.config.get('dependencies', {})
        
        for dep_name, dep_config in deps_config.items():
            if isinstance(dep_config, dict) and dep_config.get('enabled', False):
                dependencies.append(dep_name)
        
        return dependencies
    
    def install_all_dependencies(self) -> Tuple[bool, List[str], List[str]]:
        """
        Install all enabled dependencies
        
        Returns:
            Tuple of (success, installed_deps, failed_deps)
        """
        enabled_deps = self.get_enabled_dependencies()
        
        if not enabled_deps:
            print("ℹ️  No dependencies enabled in configuration")
            return True, [], []
        
        print(f"📦 Installing {len(enabled_deps)} enabled dependencies: {', '.join(enabled_deps)}")
        
        # First, check and fix dpkg if it's in a broken state
        print("\n🔧 Checking dpkg state...")
        dpkg_check_script = '''
# Check if dpkg is in a broken state
if sudo dpkg --audit 2>&1 | grep -q "broken"; then
    echo "⚠️  dpkg is in a broken state, fixing..."
    sudo dpkg --configure -a
    sudo apt-get install -f -y
    echo "✅ dpkg fixed"
else
    echo "✅ dpkg is healthy"
fi
'''
        success, output = self.client.run_command(dpkg_check_script, timeout=180)
        if not success:
            print("⚠️  dpkg check/fix failed, but continuing...")
        else:
            print("✅ dpkg state verified")
        
        # Run apt-get update once at the beginning to avoid repeated updates
        print("\n🔄 Updating package lists...")
        update_script = '''
set -e
echo "Running apt-get update..."
sudo apt-get update -qq
echo "✅ Package lists updated"
'''
        success, output = self.client.run_command(update_script, timeout=300)
        if not success:
            print("⚠️  apt-get update failed, but continuing with installations...")
        else:
            print("✅ Package lists updated successfully")
        
        # Install dependencies in order of priority
        dependency_order = [
            'git', 'firewall', 'apache', 'nginx', 'mysql', 'postgresql', 
            'php', 'python', 'nodejs', 'redis', 'memcached', 'docker',
            'ssl_certificates', 'monitoring'
        ]
        
        # Sort enabled dependencies by priority order
        sorted_deps = []
        for dep in dependency_order:
            if dep in enabled_deps:
                sorted_deps.append(dep)
        
        # Add any remaining dependencies not in the priority list
        for dep in enabled_deps:
            if dep not in sorted_deps:
                sorted_deps.append(dep)
        
        overall_success = True
        
        for dep_name in sorted_deps:
            print(f"\n🔧 Installing {dep_name}...")
            success = self._install_dependency(dep_name)
            
            if success:
                self.installed_dependencies.append(dep_name)
                print(f"✅ {dep_name} installed successfully")
            else:
                self.failed_dependencies.append(dep_name)
                print(f"❌ {dep_name} installation failed")
                overall_success = False
        
        return overall_success, self.installed_dependencies, self.failed_dependencies
    
    def _wait_for_dpkg_lock(self, timeout=60):
        """Wait for dpkg lock to be released (optimized)"""
        wait_script = '''
# Quick check for dpkg lock
if ! sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 && ! sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1; then
    echo "✅ dpkg lock is available"
    exit 0
fi

# Wait for lock to be released
echo "⏳ Waiting for dpkg lock (max 60s)..."
timeout=60
elapsed=0
while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        echo "⚠️  dpkg still locked after ${timeout}s, proceeding anyway..."
        # Kill any stuck apt processes
        sudo killall apt apt-get dpkg 2>/dev/null || true
        sleep 2
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    [ $((elapsed % 10)) -eq 0 ] && echo "   Still waiting... (${elapsed}s)"
done
echo "✅ Proceeding with installation"
'''
        self.client.run_command(wait_script, timeout=timeout + 10)
    
    def _install_dependency(self, dep_name: str) -> bool:
        """Install a specific dependency with retry logic"""
        dep_config = self.config.get(f'dependencies.{dep_name}', {})
        
        # Wait for any existing dpkg locks before starting
        self._wait_for_dpkg_lock()
        
        # Try installation with retry on failure
        max_retries = 2
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"🔄 Retry attempt {attempt + 1}/{max_retries} for {dep_name}...")
                # On retry, wait for locks and try to fix dpkg
                self._wait_for_dpkg_lock()
                fix_script = '''
sudo dpkg --configure -a 2>/dev/null || true
sudo apt-get install -f -y 2>/dev/null || true
'''
                self.client.run_command(fix_script, timeout=60)
            
            success = self._do_install_dependency(dep_name, dep_config)
            if success:
                return True
            
            if attempt < max_retries - 1:
                print(f"⚠️  Installation failed, will retry...")
        
        return False
    
    def _do_install_dependency(self, dep_name: str, dep_config: dict) -> bool:
        """Perform the actual dependency installation"""

        # Check if this is an external RDS database
        if dep_name in ['mysql', 'postgresql'] and dep_config.get('external', False):
            return self._install_external_database(dep_name, dep_config)

        if dep_name == 'apache':
            return self._install_apache(dep_config)
        elif dep_name == 'nginx':
            return self._install_nginx(dep_config)
        elif dep_name == 'mysql':
            return self._install_mysql(dep_config)
        elif dep_name == 'postgresql':
            return self._install_postgresql(dep_config)
        elif dep_name == 'php':
            return self._install_php(dep_config)
        elif dep_name == 'python':
            return self._install_python(dep_config)
        elif dep_name == 'nodejs':
            return self._install_nodejs(dep_config)
        elif dep_name == 'redis':
            return self._install_redis(dep_config)
        elif dep_name == 'memcached':
            return self._install_memcached(dep_config)
        elif dep_name == 'docker':
            return self._install_docker(dep_config)
        elif dep_name == 'git':
            return self._install_git(dep_config)
        elif dep_name == 'firewall':
            return self._configure_firewall(dep_config)
        elif dep_name == 'ssl_certificates':
            return self._install_ssl_certificates(dep_config)
        elif dep_name == 'monitoring':
            return self._install_monitoring_tools(dep_config)
        else:
            print(f"⚠️  Unknown dependency: {dep_name}")
            return False
    
    def _install_apache(self, config: Dict[str, Any]) -> bool:
        """Install and configure Apache web server"""
        version = config.get('version', 'latest')
        apache_config = config.get('config', {})
        document_root = apache_config.get('document_root', '/var/www/html')
        
        print("🔧 Installing Apache web server step by step...")
        
        # Step 1: Update package list (now done once at start)
        print("\n📦 Step 1: Package list already updated")
        
        # Step 2: Install Apache
        print("\n📦 Step 2: Installing Apache package")
        success, output = self.client.run_command("sudo apt-get install -y apache2")
        if not success:
            return False
        
        # Step 3: Enable Apache service
        print("\n🔧 Step 3: Enabling Apache service")
        success, output = self.client.run_command("sudo systemctl enable apache2")
        if not success:
            return False
        
        # Step 4: Create document root
        print(f"\n📁 Step 4: Creating document root: {document_root}")
        success, output = self.client.run_command(f"sudo mkdir -p {document_root}")
        if not success:
            return False
        
        # Step 5: Set ownership
        print("\n🔐 Step 5: Setting proper ownership")
        success, output = self.client.run_command(f"sudo chown -R www-data:www-data {document_root}")
        if not success:
            return False
        
        # Step 6: Set permissions
        print("\n🔐 Step 6: Setting proper permissions")
        success, output = self.client.run_command(f"sudo chmod -R 755 {document_root}")
        if not success:
            return False
        
        # Step 7: Enable mod_rewrite if requested
        if apache_config.get('enable_rewrite', True):
            print("\n🔧 Step 7: Enabling mod_rewrite")
            success, output = self.client.run_command("sudo a2enmod rewrite")
            if not success:
                return False
        
        # Step 8: Configure security settings
        if config.get('hide_version', True):
            print("\n🔒 Step 8: Configuring security settings")
            success, output = self.client.run_command('echo "ServerTokens Prod" | sudo tee -a /etc/apache2/conf-available/security.conf')
            if not success:
                return False
            
            success, output = self.client.run_command('echo "ServerSignature Off" | sudo tee -a /etc/apache2/conf-available/security.conf')
            if not success:
                return False
            
            success, output = self.client.run_command("sudo a2enconf security")
            if not success:
                return False
        
        # Step 9: Start Apache
        print("\n🚀 Step 9: Starting Apache service")
        success, output = self.client.run_command("sudo systemctl start apache2")
        if not success:
            return False
        
        # Step 10: Reload Apache
        print("\n🔄 Step 10: Reloading Apache configuration")
        success, output = self.client.run_command("sudo systemctl reload apache2")
        if not success:
            return False
        
        print("\n✅ Apache installation completed successfully!")
        return True
    
    def _install_nginx(self, config: Dict[str, Any]) -> bool:
        """Install and configure Nginx web server"""
        script = f'''
set -e
echo "Installing Nginx web server..."

# Install Nginx
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx

# Configure document root
DOCUMENT_ROOT="{config.get('config', {}).get('document_root', '/var/www/html')}"
sudo mkdir -p "$DOCUMENT_ROOT"
sudo chown -R www-data:www-data "$DOCUMENT_ROOT"
sudo chmod -R 755 "$DOCUMENT_ROOT"

# Start Nginx
sudo systemctl start nginx

echo "✅ Nginx installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success
    
    def _install_mysql(self, config: Dict[str, Any]) -> bool:
        """Install and configure MySQL database (local only, not for external RDS)"""
        # This method should only be called for local MySQL installations
        # External databases are handled by _install_external_database
        
        mysql_config = config.get('config', {})
        
        print("📦 Installing local MySQL database server...")
        print("⚠️  Note: For external RDS databases, only the MySQL client will be installed")
        
        script = f'''
set -e
echo "Installing MySQL database server..."

# Set non-interactive mode
export DEBIAN_FRONTEND=noninteractive

# Install MySQL
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y mysql-server

# Enable MySQL to start on boot
sudo systemctl enable mysql

# Start MySQL
sudo systemctl start mysql

# Secure MySQL installation (basic)
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';" || true

# Create application database if requested
if [ "{mysql_config.get('create_app_database', True)}" = "True" ]; then
    DB_NAME="{mysql_config.get('database_name', 'app_db')}"
    sudo mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;" || true
    echo "✅ Database '$DB_NAME' created"
fi

echo "✅ MySQL installation completed"
'''
        
        success, output = self.client.run_command_with_live_output(script, timeout=300)
        return success
    
    def _install_postgresql(self, config: Dict[str, Any]) -> bool:
        """Install and configure PostgreSQL database (local only, not for external RDS)"""
        # This method should only be called for local PostgreSQL installations
        # External databases are handled by _install_external_database
        
        pg_config = config.get('config', {})
        
        print("📦 Installing local PostgreSQL database server...")
        print("⚠️  Note: For external RDS databases, only the PostgreSQL client will be installed")
        
        script = f'''
set -e
echo "Installing PostgreSQL database server..."

# Install PostgreSQL
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y postgresql postgresql-contrib

# Enable PostgreSQL to start on boot
sudo systemctl enable postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Create application database if requested
if [ "{pg_config.get('create_app_database', True)}" = "True" ]; then
    DB_NAME="{pg_config.get('database_name', 'app_db')}"
    sudo -u postgres createdb "$DB_NAME" || true
    echo "✅ Database '$DB_NAME' created"
fi

echo "✅ PostgreSQL installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=300)
        return success
    
    def _install_php(self, config: Dict[str, Any]) -> bool:
        """Install and configure PHP"""
        version = config.get('version', '8.1')
        php_config = config.get('config', {})
        extensions = php_config.get('extensions', ['pdo', 'pdo_mysql'])
        
        # Build extension list
        ext_packages = []
        for ext in extensions:
            # Skip 'pdo' as it's built into PHP (part of php-common)
            if ext == 'pdo':
                continue  # PDO is included in php{version}-common, no separate package
            elif ext == 'pdo_mysql' or ext == 'mysql':
                # Install both generic and version-specific MySQL packages
                ext_packages.append('php-mysql')
                ext_packages.append(f'php{version}-mysql')
            elif ext == 'pdo_pgsql' or ext == 'pgsql':
                # Install both generic and version-specific PostgreSQL packages
                ext_packages.append('php-pgsql')
                ext_packages.append(f'php{version}-pgsql')
            elif ext == 'redis':
                # Install both generic and version-specific Redis packages
                ext_packages.append('php-redis')
                ext_packages.append(f'php{version}-redis')
            elif ext == 'json':
                continue  # JSON is built into PHP 8.0+, no separate package needed
            else:
                ext_packages.append(f'php-{ext}')
        
        ext_list = ' '.join(ext_packages) if ext_packages else ''
        
        script = f'''
set -e
echo "Installing PHP {version}..."

# Add Ondrej PPA for PHP (required for PHP 8.1+ on Ubuntu 22.04)
if ! grep -q "ondrej/php" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
    echo "Adding Ondrej PHP PPA..."
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:ondrej/php
    sudo apt-get update -qq
    echo "✅ Ondrej PHP PPA added"
else
    echo "✅ Ondrej PHP PPA already present"
fi

# Install PHP and extensions
sudo apt-get install -y php{version} php{version}-fpm {ext_list}

# Install Composer if requested
if [ "{php_config.get('enable_composer', True)}" = "True" ]; then
    curl -sS https://getcomposer.org/installer | php
    sudo mv composer.phar /usr/local/bin/composer
    sudo chmod +x /usr/local/bin/composer
    echo "✅ Composer installed"
fi

# Configure PHP-FPM if Apache is also enabled
if systemctl is-active --quiet apache2; then
    sudo apt-get install -y libapache2-mod-php{version}
    sudo a2enmod php{version}
    sudo systemctl reload apache2
fi

echo "✅ PHP {version} installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=300)
        return success
    
    def _install_python(self, config: Dict[str, Any]) -> bool:
        """Install and configure Python"""
        version = config.get('version', '3.9')
        python_config = config.get('config', {})
        
        script = f'''
set -e
echo "Installing Python {version}..."

# Install Python and pip
# For Ubuntu 22.04, python3 is already installed, just install additional tools
if [ "{version}" = "3.10" ] || [ "{version}" = "3" ]; then
    # Use system Python3 - install version-specific venv package
    sudo apt-get install -y python3 python3-pip python3-dev python3.10-venv
else
    # Try to install specific version
    sudo apt-get install -y python{version} python{version}-pip python{version}-venv python{version}-dev || {{
        echo "⚠️  Python {version} not available, using system python3"
        sudo apt-get install -y python3 python3-pip python3-dev python3.10-venv
    }}
fi

# Create virtual environment if requested
if [ "{python_config.get('virtual_env', True)}" = "True" ]; then
    sudo mkdir -p /opt/python-venv
    if [ "{version}" = "3.10" ] || [ "{version}" = "3" ]; then
        sudo python3 -m venv /opt/python-venv/app
    else
        sudo python{version} -m venv /opt/python-venv/app || sudo python3 -m venv /opt/python-venv/app
    fi
    sudo chown -R www-data:www-data /opt/python-venv
    echo "✅ Python virtual environment created"
fi

echo "✅ Python {version} installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=300)
        
        # Install pip packages if specified
        pip_packages = python_config.get('pip_packages', [])
        if pip_packages and success:
            pip_script = f'''
set -e
echo "Installing Python packages: {' '.join(pip_packages)}"

if [ -d "/opt/python-venv/app" ]; then
    source /opt/python-venv/app/bin/activate
    pip install --upgrade pip
    pip install {' '.join(pip_packages)}
else
    if [ "{version}" = "3.10" ] || [ "{version}" = "3" ]; then
        sudo pip3 install {' '.join(pip_packages)}
    else
        sudo pip{version} install {' '.join(pip_packages)} || sudo pip3 install {' '.join(pip_packages)}
    fi
fi

echo "✅ Python packages installed"
'''
            success, output = self.client.run_command(pip_script, timeout=420)
        
        return success
    
    def _install_nodejs(self, config: Dict[str, Any]) -> bool:
        """Install and configure Node.js"""
        version = config.get('version', '18')
        node_config = config.get('config', {})
        
        script = f'''
set -e
echo "Installing Node.js {version}..."

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_{version}.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Yarn if requested
if [ "{node_config.get('package_manager', 'npm')}" = "yarn" ]; then
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
#     sudo apt-get update  # Removed: apt-get update now runs once at start
    sudo apt-get install -y yarn
fi

echo "✅ Node.js {version} installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=300)
        
        # Install npm packages if specified
        npm_packages = node_config.get('npm_packages', [])
        if npm_packages and success:
            pkg_manager = node_config.get('package_manager', 'npm')
            npm_script = f'''
set -e
echo "Installing Node.js packages: {' '.join(npm_packages)}"
sudo {pkg_manager} install -g {' '.join(npm_packages)}
echo "✅ Node.js packages installed"
'''
            success, output = self.client.run_command(npm_script, timeout=420)
        
        return success
    
    def _install_redis(self, config: Dict[str, Any]) -> bool:
        """Install and configure Redis"""
        script = '''
set -e
echo "Installing Redis..."

# Install Redis
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y redis-server

# Enable Redis to start on boot
sudo systemctl enable redis-server

# Start Redis
sudo systemctl start redis-server

echo "✅ Redis installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success
    
    def _install_memcached(self, config: Dict[str, Any]) -> bool:
        """Install and configure Memcached"""
        script = '''
set -e
echo "Installing Memcached..."

# Install Memcached
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y memcached

# Enable Memcached to start on boot
sudo systemctl enable memcached

# Start Memcached
sudo systemctl start memcached

echo "✅ Memcached installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success
    
    def _install_docker(self, config: Dict[str, Any]) -> bool:
        """Install and configure Docker"""
        docker_config = config.get('config', {})
        
        script = f'''
set -e
echo "🐳 Installing Docker (optimized method)..."

# Remove old versions quickly
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install prerequisites (minimal set)
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key (faster method)
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update and install Docker (with compose plugin)
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
docker compose version

echo "✅ Docker installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=240)
        return success
    
    def _install_git(self, config: Dict[str, Any]) -> bool:
        """Install and configure Git"""
        git_config = config.get('config', {})
        
        script = f'''
set -e
echo "Installing Git..."

# Install Git
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y git

# Install Git LFS if requested
if [ "{git_config.get('install_lfs', False)}" = "True" ]; then
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
    sudo apt-get install -y git-lfs
    echo "✅ Git LFS installed"
fi

echo "✅ Git installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success
    
    def _install_awscli(self, config: Dict[str, Any]) -> bool:
        """Install AWS CLI for S3 bucket access"""
        awscli_config = config.get('config', {})
        version = awscli_config.get('version', '2')
        
        if version == '2':
            script = '''
set -e
echo "Installing AWS CLI v2..."

# Download and install AWS CLI v2
cd /tmp
curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt-get install -y unzip
unzip -q awscliv2.zip
sudo ./aws/install --update
rm -rf aws awscliv2.zip

# Verify installation
aws --version

echo "✅ AWS CLI v2 installation completed"
'''
        else:
            # AWS CLI v1 (legacy)
            script = '''
set -e
echo "Installing AWS CLI v1..."

# Install AWS CLI v1 via apt
sudo apt-get install -y awscli

# Verify installation
aws --version

echo "✅ AWS CLI v1 installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=300)
        return success
    
    def _configure_firewall(self, config: Dict[str, Any]) -> bool:
        """Configure firewall settings"""
        firewall_config = config.get('config', {})
        allowed_ports = firewall_config.get('allowed_ports', ['22', '80', '443'])
        
        # Ensure SSH port 22 is always in the allowed list to prevent lockout
        if '22' not in allowed_ports and 22 not in allowed_ports:
            allowed_ports.insert(0, '22')
        
        script = f'''
set -e
echo "Configuring firewall..."

# Check if UFW is already installed
if ! command -v ufw &> /dev/null; then
    echo "Installing UFW..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ufw
else
    echo "UFW already installed"
fi

# Disable UFW first to prevent lockout during configuration
sudo ufw --force disable

# Reset UFW to defaults
sudo ufw --force reset

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# CRITICAL: Allow SSH first to prevent lockout
sudo ufw allow 22/tcp

# Allow other specified ports
'''
        
        for port in allowed_ports:
            if str(port) != '22':  # Skip 22 since we already added it
                script += f'sudo ufw allow {port}\n'
        
        script += '''
# Enable UFW
sudo ufw --force enable

# Verify SSH is allowed
sudo ufw status | grep 22 || echo "⚠️  Warning: SSH port may not be properly configured"

echo "✅ Firewall configuration completed"
'''
        
        success, output = self.client.run_command(script, timeout=120)
        return success
    
    def _install_ssl_certificates(self, config: Dict[str, Any]) -> bool:
        """Install SSL certificates"""
        ssl_config = config.get('config', {})
        provider = ssl_config.get('provider', 'letsencrypt')
        
        if provider == 'letsencrypt':
            script = '''
set -e
echo "Installing Certbot for Let's Encrypt..."

# Install Certbot
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y certbot python3-certbot-apache

echo "✅ Certbot installation completed"
echo "ℹ️  Run 'sudo certbot --apache' to obtain SSL certificates"
'''
        else:
            print(f"⚠️  SSL provider '{provider}' not implemented")
            return True  # Don't fail deployment for this
        
        success, output = self.client.run_command(script, timeout=420)
        return success
    
    def _install_monitoring_tools(self, config: Dict[str, Any]) -> bool:
        """Install monitoring tools"""
        monitoring_config = config.get('config', {})
        tools = monitoring_config.get('tools', ['htop'])
        
        script = f'''
set -e
echo "Installing monitoring tools..."

# Install monitoring tools
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y {' '.join(tools)}

echo "✅ Monitoring tools installation completed"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success
    
    def configure_services(self) -> bool:
        """Configure installed services"""
        print("🔧 Configuring installed services...")
        
        success = True
        
        # Configure web server document root and permissions
        if 'apache' in self.installed_dependencies or 'nginx' in self.installed_dependencies:
            success &= self._configure_web_server()
        
        # Configure database connections
        if 'mysql' in self.installed_dependencies:
            success &= self._configure_mysql_app_access()
        
        if 'postgresql' in self.installed_dependencies:
            success &= self._configure_postgresql_app_access()
        
        return success
    
    def _configure_web_server(self) -> bool:
        """Configure web server for application"""
        script = '''
set -e
echo "Configuring web server..."

# Set proper permissions for web directory
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

# Remove default index files that might conflict
sudo rm -f /var/www/html/index.html
sudo rm -f /var/www/html/index.nginx-debian.html

echo "✅ Web server configuration completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success
    
    def _configure_mysql_app_access(self) -> bool:
        """Configure MySQL for application access"""
        # Skip configuration if using external RDS database
        mysql_config = self.config.get('dependencies', {}).get('mysql', {})
        if mysql_config.get('external', False):
            print("ℹ️  Skipping local MySQL configuration (using external RDS)")
            return True
        
        script = '''
set -e
echo "Configuring MySQL for application access..."

# Create application user (optional, basic setup)
# This is a basic setup - production should use more secure credentials
mysql -u root -proot123 -e "CREATE USER IF NOT EXISTS 'app'@'localhost' IDENTIFIED BY 'app123';" || true
mysql -u root -proot123 -e "GRANT ALL PRIVILEGES ON app_db.* TO 'app'@'localhost';" || true
mysql -u root -proot123 -e "FLUSH PRIVILEGES;" || true

echo "✅ MySQL application access configured"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success
    
    def _configure_postgresql_app_access(self) -> bool:
        """Configure PostgreSQL for application access"""
        # Skip configuration if using external RDS database
        pg_config = self.config.get('dependencies', {}).get('postgresql', {})
        if pg_config.get('external', False):
            print("ℹ️  Skipping local PostgreSQL configuration (using external RDS)")
            return True
        
        script = '''
set -e
echo "Configuring PostgreSQL for application access..."

# Create application user (basic setup)
sudo -u postgres createuser -D -A -P app || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE app_db TO app;" || true

echo "✅ PostgreSQL application access configured"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success
    
    def restart_services(self) -> bool:
        """Restart all installed services"""
        print("🔄 Restarting installed services...")
        
        service_map = {
            'apache': 'apache2',
            'nginx': 'nginx',
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'redis': 'redis-server',
            'memcached': 'memcached',
            'docker': 'docker',
            'nodejs': 'nodejs-app'
        }
        
        success = True
        
        for dep in self.installed_dependencies:
            if dep in service_map:
                service_name = service_map[dep]
                restart_script = f'''
set -e
echo "Restarting {service_name}..."

# Check if service exists first
if systemctl list-unit-files | grep -q "^{service_name}.service"; then
    sudo systemctl restart {service_name}
    sudo systemctl enable {service_name}
    
    # Wait a moment and verify it's running
    sleep 2
    if systemctl is-active --quiet {service_name}; then
        echo "✅ {service_name} restarted and running"
    else
        echo "⚠️  {service_name} restarted but not active"
        sudo systemctl status {service_name} --no-pager || true
    fi
else
    echo "ℹ️  {service_name} service not found, skipping"
fi
'''
                
                svc_success, output = self.client.run_command(restart_script, timeout=60)
                if not svc_success:
                    print(f"⚠️  Failed to restart {service_name}")
                    print(f"Output: {output}")
                    success = False
        
        return success

    def _install_external_database(self, db_type: str, config: Dict[str, Any]) -> bool:
        """
        Install external RDS database client and configure connection
        
        Args:
            db_type: Database type ('mysql' or 'postgresql')
            config: Database configuration from deployment config
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"🔗 Configuring external {db_type.upper()} RDS database...")
            
            # Get RDS configuration
            rds_config = config.get('rds', {})
            db_name = rds_config.get('database_name')
            
            if not db_name:
                print(f"❌ RDS database name not specified in configuration")
                return False
            
            # Initialize RDS manager
            # Note: Uses the same AWS credentials that GitHub Actions configured
            # No need to pass separate credentials - boto3 will use the environment
            rds_manager = LightsailRDSManager(
                instance_name=self.client.instance_name,
                region=rds_config.get('region', 'us-east-1')
            )
            
            # Get RDS connection details
            print(f"📡 Retrieving RDS connection details for {db_name}...")
            connection_details = rds_manager.get_rds_connection_details(db_name)
            
            if not connection_details:
                print(f"❌ Failed to retrieve RDS connection details for {db_name}")
                return False
            
            # Install database client
            print(f"📦 Installing {db_type} client...")
            client_success = self._install_database_client(db_type)
            
            if not client_success:
                print(f"❌ Failed to install {db_type} client")
                return False
            
            # Test database connectivity
            print(f"🔍 Testing database connectivity...")
            connectivity_success = rds_manager.test_rds_connectivity(
                connection_details, 
                rds_config.get('master_database', 'app_db')
            )
            
            if not connectivity_success:
                print(f"⚠️  Database connectivity test failed, but continuing...")
            
            # Configure environment variables for application
            print(f"⚙️  Configuring environment variables...")
            env_vars = rds_manager.create_database_env_vars(
                connection_details, 
                rds_config.get('master_database', 'app_db')
            )
            env_success = self._create_environment_file(env_vars, config)
            
            if not env_success:
                print(f"⚠️  Failed to configure environment variables")
                return False
            
            print(f"✅ External {db_type.upper()} RDS database configured successfully")
            print(f"   Host: {connection_details['endpoint']}")
            print(f"   Port: {connection_details['port']}")
            print(f"   Database: {connection_details['database_name']}")
            print(f"   Username: {connection_details['master_username']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configuring external {db_type} database: {str(e)}")
            return False
    
    def _install_database_client(self, db_type: str) -> bool:
        """Install database client tools"""
        if db_type == 'mysql':
            script = '''
set -e
echo "Installing MySQL client..."

# Install MySQL client
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y mysql-client

echo "✅ MySQL client installation completed"
'''
        elif db_type == 'postgresql':
            script = '''
set -e
echo "Installing PostgreSQL client..."

# Install PostgreSQL client
# sudo apt-get update  # Removed: apt-get update now runs once at start
sudo apt-get install -y postgresql-client

echo "✅ PostgreSQL client installation completed"
'''
        else:
            print(f"❌ Unsupported database type: {db_type}")
            return False
        
        success, output = self.client.run_command(script, timeout=420)
        return success
    
    def _create_environment_file(self, env_vars: Dict[str, str], config: Dict[str, Any]) -> bool:
        """Create environment file with database configuration"""
        try:
            # Add any custom environment variables from config
            custom_env = config.get('rds', {}).get('environment', {})
            env_vars.update(custom_env)
            
            # Create environment file
            env_content = '\n'.join([f'{key}={value}' for key, value in env_vars.items()])
            
            script = f'''
set -e
echo "Configuring database environment variables..."

# Create environment file in /opt/app
sudo mkdir -p /opt/app
cat << 'EOF' | sudo tee /opt/app/database.env > /dev/null
{env_content}
EOF

# Set proper permissions for /opt/app/database.env (readable by www-data group)
sudo chmod 640 /opt/app/database.env
sudo chown root:www-data /opt/app/database.env

# Also create a copy in web directory for direct access
sudo cp /opt/app/database.env /var/www/html/.env
sudo chmod 640 /var/www/html/.env
sudo chown www-data:www-data /var/www/html/.env

echo "✅ Database environment configuration completed"
echo "Environment file created at: /opt/app/database.env"
echo "Environment file copied to: /var/www/html/.env"
'''
            
            success, output = self.client.run_command(script, timeout=60)
            
            if success:
                print("📝 Database environment variables configured:")
                for key, value in env_vars.items():
                    if 'PASSWORD' in key:
                        print(f"   {key}=***")
                    else:
                        print(f"   {key}={value}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error creating environment file: {str(e)}")
            return False

    def _configure_database_environment(self, db_type: str, connection_details: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Configure environment variables for database connection"""
        try:
            # Create environment file for database configuration
            env_vars = {
                f'DB_TYPE': db_type.upper(),
                f'DB_HOST': connection_details['host'],
                f'DB_PORT': str(connection_details['port']),
                f'DB_NAME': connection_details['database'],
                f'DB_USERNAME': connection_details['username'],
                f'DB_PASSWORD': connection_details['password'],
                f'DB_EXTERNAL': 'true'
            }
            
            # Add any custom environment variables from config
            custom_env = config.get('environment', {})
            env_vars.update(custom_env)
            
            # Create environment file
            env_content = '\n'.join([f'{key}={value}' for key, value in env_vars.items()])
            
            script = f'''
set -e
echo "Configuring database environment variables..."

# Create environment file in /opt/app
sudo mkdir -p /opt/app
cat << 'EOF' | sudo tee /opt/app/database.env > /dev/null
{env_content}
EOF

# Set proper permissions for /opt/app/database.env (readable by www-data group)
sudo chmod 640 /opt/app/database.env
sudo chown root:www-data /opt/app/database.env

# Also create a copy in web directory for direct access
sudo cp /opt/app/database.env /var/www/html/.env
sudo chmod 640 /var/www/html/.env
sudo chown www-data:www-data /var/www/html/.env

echo "✅ Database environment configuration completed"
echo "Environment file created at: /opt/app/database.env"
echo "Environment file copied to: /var/www/html/.env"
'''
            
            success, output = self.client.run_command(script, timeout=60)
            
            if success:
                print("📝 Database environment variables configured:")
                for key, value in env_vars.items():
                    if 'PASSWORD' in key:
                        print(f"   {key}=***")
                    else:
                        print(f"   {key}={value}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error configuring database environment: {str(e)}")
            return False

    def get_installation_summary(self) -> Dict[str, Any]:
        """Get summary of dependency installation"""
        return {
            'installed': self.installed_dependencies,
            'failed': self.failed_dependencies,
            'total_enabled': len(self.get_enabled_dependencies()),
            'success_rate': len(self.installed_dependencies) / max(1, len(self.get_enabled_dependencies())) * 100
        }
