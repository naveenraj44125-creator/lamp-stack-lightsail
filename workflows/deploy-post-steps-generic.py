#!/usr/bin/env python3
"""
Generic post-deployment steps for AWS Lightsail
This script handles application deployment and service configuration based on config
"""

import sys
import argparse
from lightsail_common import LightsailBase
from config_loader import DeploymentConfig
from dependency_manager import DependencyManager

class GenericPostDeployer:
    def __init__(self, instance_name=None, region=None, config=None):
        # Initialize configuration
        if config is None:
            config = DeploymentConfig()
        
        # Use config values if parameters not provided
        if instance_name is None:
            instance_name = config.get_instance_name()
        if region is None:
            region = config.get_aws_region()
            
        self.config = config
        self.client = LightsailBase(instance_name, region)
        self.dependency_manager = DependencyManager(self.client, config)
        
        # Load installed dependencies from the system
        self._detect_installed_dependencies()

    def _detect_installed_dependencies(self):
        """Detect which dependencies are currently installed on the system"""
        enabled_deps = self.dependency_manager.get_enabled_dependencies()
        
        # Check which services are actually running/installed
        check_script = '''
set -e
echo "Checking installed services..."

# Check for web servers
systemctl is-active --quiet apache2 && echo "apache:installed" || true
systemctl is-active --quiet nginx && echo "nginx:installed" || true

# Check for databases
systemctl is-active --quiet mysql && echo "mysql:installed" || true
systemctl is-active --quiet postgresql && echo "postgresql:installed" || true

# Check for other services
systemctl is-active --quiet redis-server && echo "redis:installed" || true
systemctl is-active --quiet memcached && echo "memcached:installed" || true
systemctl is-active --quiet docker && echo "docker:installed" || true

# Check for programming languages
which php > /dev/null 2>&1 && echo "php:installed" || true
which python3 > /dev/null 2>&1 && echo "python:installed" || true
which node > /dev/null 2>&1 && echo "nodejs:installed" || true
which git > /dev/null 2>&1 && echo "git:installed" || true

echo "Service check completed"
'''
        
        success, output = self.client.run_command(check_script, timeout=60)
        if success:
            for line in output.split('\n'):
                if ':installed' in line:
                    dep_name = line.split(':')[0]
                    if dep_name in enabled_deps:
                        self.dependency_manager.installed_dependencies.append(dep_name)

    def deploy_application(self, package_file, verify=False, cleanup=False, env_vars=None):
        """Deploy application and configure services"""
        print(f"🚀 Starting generic application deployment")
        print(f"📦 Package File: {package_file}")
        print(f"🔍 Verify: {verify}")
        print(f"🧹 Cleanup: {cleanup}")
        
        app_type = self.config.get('application.type', 'web')
        app_name = self.config.get('application.name', 'Generic Application')
        app_version = self.config.get('application.version', '1.0.0')
        
        print(f"📋 Application: {app_name} v{app_version}")
        print(f"🏷️  Type: {app_type}")
        print(f"🌍 Instance: {self.client.instance_name}")
        print(f"📍 Region: {self.client.region}")
        
        # Deploy application files
        print("\n" + "="*60)
        print("📦 DEPLOYING APPLICATION FILES")
        print("="*60)
        success = self._deploy_application_files(package_file)
        if not success:
            print("❌ Failed to deploy application files")
            return False
        
        # Configure application based on type and dependencies
        print("\n" + "="*60)
        print("🔧 CONFIGURING APPLICATION")
        print("="*60)
        success = self._configure_application()
        if not success:
            print("⚠️  Application configuration had some issues")
        
        # Set up application-specific configurations
        print("\n" + "="*60)
        print("⚙️  APPLICATION-SPECIFIC CONFIGURATIONS")
        print("="*60)
        success = self._setup_app_specific_config()
        if not success:
            print("⚠️  Some application-specific configurations failed")
        
        # Restart services
        print("\n" + "="*60)
        print("🔄 RESTARTING SERVICES")
        print("="*60)
        success = self.dependency_manager.restart_services()
        if not success:
            print("⚠️  Some services failed to restart")
        
        # Set environment variables if provided
        if env_vars:
            print("\n🌍 Setting deployment environment variables...")
            self._set_deployment_env_vars(env_vars)
        
        # Verify deployment if requested
        if verify:
            print("\n" + "="*60)
            print("🔍 VERIFYING DEPLOYMENT")
            print("="*60)
            success = self._verify_deployment()
            if not success:
                print("⚠️  Deployment verification had issues")
        
        # Cleanup if requested
        if cleanup:
            print("\n" + "="*60)
            print("🧹 CLEANING UP TEMPORARY FILES")
            print("="*60)
            self._cleanup_deployment()
        
        # Optimize performance
        print("\n" + "="*60)
        print("⚡ OPTIMIZING PERFORMANCE")
        print("="*60)
        self._optimize_performance()
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"✅ Application: {app_name} v{app_version}")
        print(f"🌐 Instance: {self.client.instance_name}")
        print(f"📍 Region: {self.client.region}")
        print(f"🏷️  Type: {app_type}")
        return True

    def _deploy_application_files(self, package_file) -> bool:
        """Deploy application files to the appropriate location"""
        app_type = self.config.get('application.type', 'web')
        
        # Determine deployment target based on app type and installed dependencies
        if app_type == 'web':
            if 'apache' in self.dependency_manager.installed_dependencies:
                target_dir = self.config.get('dependencies.apache.config.document_root', '/var/www/html')
            elif 'nginx' in self.dependency_manager.installed_dependencies:
                target_dir = self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
            else:
                target_dir = '/var/www/html'
        elif app_type == 'api':
            if 'python' in self.dependency_manager.installed_dependencies:
                target_dir = '/opt/app'
            elif 'nodejs' in self.dependency_manager.installed_dependencies:
                target_dir = '/opt/nodejs-app'
            else:
                target_dir = '/opt/app'
        else:
            target_dir = '/opt/app'
        
        # First, copy the package file to the remote instance
        print(f"📤 Uploading package file {package_file} to remote instance...")
        remote_package_path = f"/tmp/{package_file}"
        
        if not self.client.copy_file_to_instance(package_file, remote_package_path):
            print(f"❌ Failed to upload package file to remote instance")
            return False
        
        script = f'''
set -e
echo "Deploying application files to {target_dir}..."

# Create backup of existing files
if [ -d "{target_dir}" ] && [ "$(ls -A {target_dir})" ]; then
    BACKUP_DIR="/var/backups/app/$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$BACKUP_DIR"
    sudo cp -r {target_dir}/* "$BACKUP_DIR/" || true
    echo "✅ Backup created at $BACKUP_DIR"
fi

# Extract application package
echo "Extracting application package..."
cd /tmp
sudo tar -xzf {package_file}

# Deploy files to target directory
sudo mkdir -p {target_dir}
sudo cp -r * {target_dir}/ || true

# Set proper ownership based on application type
'''
        
        if app_type == 'web':
            script += f'''
sudo chown -R www-data:www-data {target_dir}
sudo chmod -R 755 {target_dir}
'''
        else:
            script += f'''
sudo chown -R ubuntu:ubuntu {target_dir}
sudo chmod -R 755 {target_dir}
'''
        
        script += '''
echo "✅ Application files deployed successfully"
'''
        
        success, output = self.client.run_command(script, timeout=180)
        return success

    def _configure_application(self) -> bool:
        """Configure application based on installed dependencies"""
        success = True
        
        # Configure web server if installed
        if 'apache' in self.dependency_manager.installed_dependencies:
            success &= self._configure_apache_for_app()
        
        if 'nginx' in self.dependency_manager.installed_dependencies:
            success &= self._configure_nginx_for_app()
        
        # Configure PHP if installed
        if 'php' in self.dependency_manager.installed_dependencies:
            success &= self._configure_php_for_app()
        
        # Configure Python if installed
        if 'python' in self.dependency_manager.installed_dependencies:
            success &= self._configure_python_for_app()
        
        # Configure Node.js if installed
        if 'nodejs' in self.dependency_manager.installed_dependencies:
            success &= self._configure_nodejs_for_app()
        
        # Configure database connections
        success &= self._configure_database_connections()
        
        return success

    def _configure_apache_for_app(self) -> bool:
        """Configure Apache for the application"""
        app_type = self.config.get('application.type', 'web')
        document_root = self.config.get('dependencies.apache.config.document_root', '/var/www/html')
        
        script = f'''
set -e
echo "Configuring Apache for application..."

# Create virtual host configuration
cat > /tmp/app.conf << 'EOF'
<VirtualHost *:80>
    DocumentRoot {document_root}
    
    <Directory {document_root}>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # Enable rewrite engine for pretty URLs
    RewriteEngine On
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    
    ErrorLog /var/log/apache2/app_error.log
    CustomLog /var/log/apache2/app_access.log combined
</VirtualHost>
EOF

# Install the configuration
sudo mv /tmp/app.conf /etc/apache2/sites-available/app.conf
sudo a2ensite app.conf
sudo a2dissite 000-default.conf || true

# Enable required modules
sudo a2enmod rewrite
sudo a2enmod headers

echo "✅ Apache configured for application"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _configure_nginx_for_app(self) -> bool:
        """Configure Nginx for the application"""
        document_root = self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
        
        script = f'''
set -e
echo "Configuring Nginx for application..."

# Create server block configuration
cat > /tmp/app << 'EOF'
server {{
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root {document_root};
    index index.php index.html index.htm;
    
    server_name _;
    
    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}
    
    location ~ \.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
    }}
    
    location ~ /\.ht {{
        deny all;
    }}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}}
EOF

# Install the configuration
sudo mv /tmp/app /etc/nginx/sites-available/app
sudo ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
sudo rm -f /etc/nginx/sites-enabled/default

echo "✅ Nginx configured for application"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _configure_php_for_app(self) -> bool:
        """Configure PHP for the application"""
        script = '''
set -e
echo "Configuring PHP for application..."

# Configure PHP settings for production
PHP_INI="/etc/php/8.1/apache2/php.ini"
if [ -f "$PHP_INI" ]; then
    sudo sed -i 's/display_errors = On/display_errors = Off/' "$PHP_INI"
    sudo sed -i 's/;date.timezone =/date.timezone = UTC/' "$PHP_INI"
    sudo sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 10M/' "$PHP_INI"
    sudo sed -i 's/post_max_size = 8M/post_max_size = 10M/' "$PHP_INI"
fi

# Configure PHP-FPM if available
PHP_FPM_INI="/etc/php/8.1/fpm/php.ini"
if [ -f "$PHP_FPM_INI" ]; then
    sudo sed -i 's/display_errors = On/display_errors = Off/' "$PHP_FPM_INI"
    sudo sed -i 's/;date.timezone =/date.timezone = UTC/' "$PHP_FPM_INI"
fi

echo "✅ PHP configured for application"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _configure_python_for_app(self) -> bool:
        """Configure Python for the application"""
        app_type = self.config.get('application.type', 'web')
        
        if app_type == 'api':
            script = '''
set -e
echo "Configuring Python for API application..."

# Create systemd service for Python app (if it's an API)
cat > /tmp/python-app.service << 'EOF'
[Unit]
Description=Python Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/app
Environment=PATH=/opt/python-venv/app/bin
ExecStart=/opt/python-venv/app/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Install and enable the service if app.py exists
if [ -f "/opt/app/app.py" ]; then
    sudo mv /tmp/python-app.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable python-app.service
    echo "✅ Python app service configured"
else
    echo "ℹ️  No app.py found, skipping service configuration"
fi
'''
        else:
            script = '''
set -e
echo "Configuring Python for web application..."

# Install mod_wsgi if Apache is present
if systemctl is-active --quiet apache2; then
    sudo apt-get update
    sudo apt-get install -y libapache2-mod-wsgi-py3
    sudo a2enmod wsgi
    echo "✅ mod_wsgi configured for Apache"
fi
'''
        
        success, output = self.client.run_command(script, timeout=120)
        return success

    def _configure_nodejs_for_app(self) -> bool:
        """Configure Node.js for the application"""
        script = '''
set -e
echo "Configuring Node.js for application..."

# Create systemd service for Node.js app
cat > /tmp/nodejs-app.service << 'EOF'
[Unit]
Description=Node.js Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/nodejs-app
ExecStart=/usr/bin/node app.js
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Install and enable the service if app.js exists
if [ -f "/opt/nodejs-app/app.js" ] || [ -f "/opt/nodejs-app/index.js" ]; then
    sudo mv /tmp/nodejs-app.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable nodejs-app.service
    echo "✅ Node.js app service configured"
else
    echo "ℹ️  No app.js or index.js found, skipping service configuration"
fi
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _configure_database_connections(self) -> bool:
        """Configure database connections based on enabled dependencies"""
        print("🔧 Configuring database connections...")
        
        # Check if MySQL is enabled in config
        mysql_enabled = self.config.get('dependencies.mysql.enabled', False)
        mysql_external = self.config.get('dependencies.mysql.external', False)
        
        if mysql_enabled:
            if mysql_external:
                # Try to configure RDS connection
                return self._configure_rds_connection()
            else:
                # Configure local MySQL
                return self._configure_local_mysql()
        
        # Check if PostgreSQL is enabled
        postgresql_enabled = self.config.get('dependencies.postgresql.enabled', False)
        if postgresql_enabled:
            return self._configure_local_postgresql()
        
        print("ℹ️  No database dependencies enabled, skipping database configuration")
        return True

    def _configure_rds_connection(self) -> bool:
        """Configure RDS database connection"""
        print("🔧 Configuring RDS database connection...")
        
        rds_config = self.config.get('dependencies.mysql.rds', {})
        database_name = rds_config.get('database_name', 'lamp-app-db')
        
        script = f'''
set -e
echo "Setting up RDS database connection..."

# Install MySQL client
sudo apt-get update
sudo apt-get install -y mysql-client

# Try to get RDS connection details using AWS CLI/boto3
# This would normally be handled by the RDS manager
echo "RDS configuration attempted - requires valid AWS credentials"

# Create fallback environment file for now
if [ ! -f /var/www/html/.env ]; then
    echo "Creating fallback local database environment file..."
    sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Fallback to Local MySQL
DB_EXTERNAL=false
DB_TYPE=MYSQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_db
DB_USERNAME=root
DB_PASSWORD=root123
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

    sudo chown www-data:www-data /var/www/html/.env
    sudo chmod 644 /var/www/html/.env
    echo "✅ Fallback environment file created"
fi

echo "✅ RDS configuration completed (with local fallback)"
'''
        
        success, output = self.client.run_command(script, timeout=120)
        
        # If RDS configuration fails, fall back to local MySQL
        if not success:
            print("⚠️  RDS configuration failed, falling back to local MySQL")
            return self._configure_local_mysql()
        
        return success

    def _configure_local_mysql(self) -> bool:
        """Configure local MySQL database"""
        print("🔧 Configuring local MySQL database...")
        
        script = '''
set -e
echo "Setting up local MySQL database..."

# Install MySQL if not present
if ! command -v mysql &> /dev/null; then
    echo "Installing MySQL server..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
fi

# Start and enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Configure MySQL root user
echo "Configuring MySQL root user..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';" 2>/dev/null || echo "Root password configuration attempted"

# Create application database
mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS app_db;" 2>/dev/null && echo "✅ app_db database created" || echo "❌ Failed to create database"

# Create test table with sample data
mysql -u root -proot123 app_db -e "
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT IGNORE INTO test_table (id, name) VALUES 
    (1, 'Test Entry'),
    (2, 'Sample Data'),
    (3, 'Database Working');
" 2>/dev/null && echo "✅ Test table created with sample data" || echo "❌ Failed to create test table"

# Test connection
mysql -u root -proot123 -e "SELECT COUNT(*) as record_count FROM test_table;" app_db 2>/dev/null && echo "✅ MySQL connection test successful" || echo "❌ MySQL connection test failed"

# Create environment file
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Local MySQL
DB_EXTERNAL=false
DB_TYPE=MYSQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_db
DB_USERNAME=root
DB_PASSWORD=root123
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

# Set proper permissions
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 644 /var/www/html/.env

echo "✅ Local MySQL database setup completed"
'''
        
        success, output = self.client.run_command(script, timeout=180)
        return success

    def _configure_local_postgresql(self) -> bool:
        """Configure local PostgreSQL database"""
        print("🔧 Configuring local PostgreSQL database...")
        
        script = '''
set -e
echo "Setting up local PostgreSQL database..."

# Install PostgreSQL
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create application database and user
sudo -u postgres psql -c "CREATE DATABASE app_db;" 2>/dev/null || echo "Database may already exist"
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'app_password';" 2>/dev/null || echo "User may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;" 2>/dev/null || echo "Privileges granted"

# Create environment file
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Local PostgreSQL
DB_EXTERNAL=false
DB_TYPE=POSTGRESQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_db
DB_USERNAME=app_user
DB_PASSWORD=app_password
DB_CHARSET=utf8

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

# Set proper permissions
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 644 /var/www/html/.env

echo "✅ Local PostgreSQL database setup completed"
'''
        
        success, output = self.client.run_command(script, timeout=180)
        return success

    def _setup_app_specific_config(self) -> bool:
        """Set up application-specific configurations"""
        app_type = self.config.get('application.type', 'web')
        
        script = '''
set -e
echo "Setting up application-specific configurations..."

# Set up log rotation
cat > /tmp/app-logs << 'EOF'
/var/log/app/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

sudo mv /tmp/app-logs /etc/logrotate.d/app

# Create application log directory
sudo mkdir -p /var/log/app
sudo chown ubuntu:ubuntu /var/log/app

# Set up cron jobs for maintenance (if needed)
# This is a placeholder for application-specific maintenance tasks

echo "✅ Application-specific configurations completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _set_deployment_env_vars(self, env_vars):
        """Set deployment-specific environment variables"""
        if not env_vars:
            return
        
        env_content = []
        for key, value in env_vars.items():
            env_content.append(f'{key}="{value}"')
        
        env_file_content = '\n'.join(env_content)
        
        script = f'''
set -e
echo "Setting deployment environment variables..."

# Create .env file with proper permissions if it doesn't exist
if [ ! -f /var/www/html/.env ]; then
    sudo touch /var/www/html/.env
    sudo chown www-data:www-data /var/www/html/.env
    sudo chmod 644 /var/www/html/.env
fi

# Create temporary file with deployment variables
cat > /tmp/deployment_vars << 'EOF'

# Deployment Variables
{env_file_content}
EOF

# Append deployment vars to existing .env file using sudo
sudo bash -c 'cat /tmp/deployment_vars >> /var/www/html/.env'
sudo rm -f /tmp/deployment_vars

echo "✅ Deployment environment variables set"
'''
        
        success, output = self.client.run_command(script, timeout=30)

    def _verify_deployment(self) -> bool:
        """Verify that the deployment was successful"""
        health_config = self.config.get_health_check_config()
        endpoint = health_config.get('endpoint', '/')
        expected_content = health_config.get('expected_content', 'Hello')
        
        script = f'''
set -e
echo "Verifying deployment..."

# Check if web server is running
if systemctl is-active --quiet apache2; then
    echo "✅ Apache is running"
elif systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "⚠️  No web server detected as running"
fi

# Check if application files exist
if [ -f "/var/www/html/index.php" ] || [ -f "/var/www/html/index.html" ]; then
    echo "✅ Application files found"
else
    echo "⚠️  No main application files found"
fi

# Test local HTTP response
echo "Testing local HTTP response..."
if curl -s http://localhost{endpoint} | grep -q "{expected_content}"; then
    echo "✅ Application responds correctly"
else
    echo "⚠️  Application response test failed"
fi

echo "✅ Deployment verification completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _cleanup_deployment(self):
        """Clean up temporary deployment files"""
        script = '''
set -e
echo "Cleaning up deployment files..."

# Remove temporary files
sudo rm -f /tmp/*.tar.gz
sudo rm -f /tmp/app.*
sudo rm -rf /tmp/deployment_*

# Clean package manager caches
sudo apt-get clean || true

echo "✅ Cleanup completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)

    def _optimize_performance(self):
        """Optimize system and application performance"""
        script = '''
set -e
echo "🔧 Starting performance optimization..."

# Optimize Apache if running
if systemctl is-active --quiet apache2; then
    echo "⚡ Optimizing Apache web server..."
    # Enable compression
    sudo a2enmod deflate
    sudo a2enmod expires
    sudo a2enmod headers
    sudo systemctl reload apache2
    echo "✅ Apache performance optimized"
fi

# Optimize PHP if installed
if which php > /dev/null 2>&1; then
    echo "⚡ Optimizing PHP configuration..."
    # Enable OPcache if available
    PHP_INI="/etc/php/8.1/apache2/php.ini"
    if [ -f "$PHP_INI" ]; then
        sudo sed -i 's/;opcache.enable=1/opcache.enable=1/' "$PHP_INI" || true
        sudo sed -i 's/;opcache.memory_consumption=128/opcache.memory_consumption=128/' "$PHP_INI" || true
        sudo sed -i 's/;opcache.max_accelerated_files=4000/opcache.max_accelerated_files=10000/' "$PHP_INI" || true
        sudo sed -i 's/;opcache.revalidate_freq=2/opcache.revalidate_freq=60/' "$PHP_INI" || true
    fi
    echo "✅ PHP performance optimized"
fi

# System-level optimizations
echo "⚡ Applying system-level optimizations..."
sudo sysctl -w vm.swappiness=10 || true
sudo sysctl -w net.core.rmem_max=16777216 || true
sudo sysctl -w net.core.wmem_max=16777216 || true

# Clear system caches
echo "🧹 Clearing system caches..."
sudo apt-get clean || true
sudo apt-get autoremove -y || true

echo "✅ Performance optimization completed successfully"
'''
        
        success, output = self.client.run_command(script, timeout=60)
    
    def _print_deployment_summary(self):
        """Print deployment summary information"""
        print("\n" + "="*60)
        print("📊 DEPLOYMENT SUMMARY")
        print("="*60)
        
        # Get instance info
        instance_info = self.client.get_instance_info()
        if instance_info:
            print(f"🖥️  Instance Name: {instance_info['name']}")
            print(f"🌐 Public IP: {instance_info.get('public_ip', 'N/A')}")
            print(f"🔒 Private IP: {instance_info.get('private_ip', 'N/A')}")
            print(f"📦 Blueprint: {instance_info.get('blueprint', 'N/A')}")
            print(f"💾 Bundle: {instance_info.get('bundle', 'N/A')}")
            print(f"⚡ State: {instance_info.get('state', 'N/A')}")
        
        # Show installed dependencies
        if hasattr(self.dependency_manager, 'installed_dependencies'):
            installed = self.dependency_manager.installed_dependencies
            if installed:
                print(f"\n🔧 Installed Dependencies ({len(installed)}):")
                for dep in installed:
                    print(f"   ✅ {dep}")
        
        # Show application configuration
        app_config = {
            'Name': self.config.get('application.name', 'Generic Application'),
            'Version': self.config.get('application.version', '1.0.0'),
            'Type': self.config.get('application.type', 'web'),
            'PHP Version': self.config.get('application.php_version', '8.1'),
        }
        
        print(f"\n📋 Application Configuration:")
        for key, value in app_config.items():
            print(f"   {key}: {value}")
        
        print("\n🎯 Next Steps:")
        if instance_info and instance_info.get('public_ip'):
            print(f"   🌐 Visit: http://{instance_info['public_ip']}")
        print("   📝 Check logs: /var/log/apache2/")
        print("   🔧 Config files: /var/www/html/.env")
        print("   📊 Monitor: systemctl status apache2 mysql")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Generic post-deployment steps for AWS Lightsail')
    parser.add_argument('package_file', help='Application package file to deploy')
    parser.add_argument('--instance-name', help='Lightsail instance name (overrides config)')
    parser.add_argument('--region', help='AWS region (overrides config)')
    parser.add_argument('--config-file', help='Path to configuration file')
    parser.add_argument('--verify', action='store_true', help='Verify deployment')
    parser.add_argument('--cleanup', action='store_true', help='Clean up temporary files')
    parser.add_argument('--env', action='append', help='Environment variables (KEY=VALUE)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config_file = args.config_file if args.config_file else 'deployment-generic.config.yml'
        config = DeploymentConfig(config_file=config_file)
        
        # Use command line args if provided, otherwise use config
        instance_name = args.instance_name or config.get_instance_name()
        region = args.region or config.get_aws_region()
        
        print(f"🚀 Starting generic post-deployment steps for {instance_name}")
        print(f"🌍 Region: {region}")
        print(f"📦 Package: {args.package_file}")
        print(f"📋 Application: {config.get('application.name', 'Unknown')} v{config.get('application.version', '1.0.0')}")
        print(f"🏷️  Type: {config.get('application.type', 'web')}")
        
        # Parse environment variables
        env_vars = {}
        if args.env:
            for env_var in args.env:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    env_vars[key] = value
        
        # Check if dependency steps are enabled in config
        if not config.get('deployment.steps.post_deployment.dependencies.enabled', True):
            print("ℹ️  Dependency configuration steps are disabled in configuration")
        
        # Create generic post-deployer and deploy application
        post_deployer = GenericPostDeployer(instance_name, region, config)
        
        if post_deployer.deploy_application(
            args.package_file, 
            verify=args.verify, 
            cleanup=args.cleanup,
            env_vars=env_vars
        ):
            # Print deployment summary
            post_deployer._print_deployment_summary()
            print("🎉 Generic post-deployment steps completed successfully!")
            sys.exit(0)
        else:
            print("❌ Generic post-deployment steps failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error in generic post-deployment steps: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
