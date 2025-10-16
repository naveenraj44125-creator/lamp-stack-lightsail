#!/usr/bin/env python3
"""
LAMP stack specific operations for AWS Lightsail deployment workflows
This module provides LAMP-specific functionality separate from general Lightsail operations
"""

from lightsail_common import LightsailBase

class LightsailLAMPManager(LightsailBase):
    """LAMP stack specific operations manager"""
    
    def get_lamp_install_script(self):
        """Get the standard LAMP installation script"""
        return '''
set -e

# Fix any broken packages first
echo "Fixing any broken packages..."
sudo dpkg --configure -a || true
sudo apt-get -f install -y || true

# Update system
echo "Updating system packages..."
# Use timeout command to prevent hanging and add retries
timeout 600 sudo apt-get update -y || {
    echo "First update attempt failed, trying with different options..."
    sudo apt-get clean
    sudo rm -rf /var/lib/apt/lists/*
    timeout 600 sudo apt-get update -y --fix-missing || {
        echo "Second update attempt failed, trying minimal update..."
        timeout 300 sudo apt-get update -y --allow-releaseinfo-change || true
    }
}

# Check if Apache is already installed
if ! command -v apache2 &> /dev/null; then
    echo "Installing Apache..."
    timeout 600 sudo DEBIAN_FRONTEND=noninteractive apt-get install -y apache2
else
    echo "Apache already installed"
fi

# Check if MySQL is already installed
if ! command -v mysql &> /dev/null; then
    echo "Installing MariaDB (lighter alternative to MySQL)..."
    timeout 600 sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server mariadb-client
else
    echo "MySQL/MariaDB already installed"
fi

# Check if PHP is already installed
if ! command -v php &> /dev/null; then
    echo "Installing PHP and extensions..."
    timeout 600 sudo DEBIAN_FRONTEND=noninteractive apt-get install -y php php-mysql php-cli php-curl php-json php-mbstring php-xml php-zip
else
    echo "PHP already installed"
fi

# Start and enable services
echo "Starting services..."
sudo systemctl start apache2 || echo "Apache already running"
sudo systemctl enable apache2
sudo systemctl start mysql || echo "MySQL already running"
sudo systemctl enable mysql

# Configure Apache
echo "Configuring Apache..."
sudo a2enmod rewrite || echo "Rewrite module already enabled"
sudo systemctl restart apache2

# Set up web directory permissions
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

echo "✅ LAMP stack installation completed"
'''

    def get_database_setup_script(self):
        """Get the standard database setup script"""
        return '''
set -e

# Configure MySQL (basic setup)
echo "Setting up database..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS lamp_demo;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'lamp_user'@'localhost' IDENTIFIED BY 'lamp_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON lamp_demo.* TO 'lamp_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "✅ Database setup completed"
'''

    def get_deployment_script(self):
        """Get the standard application deployment script"""
        return '''
set -e

# Extract application
cd /tmp
echo "Extracting application archive..."
tar -xzf app.tar.gz

# Backup current version if it exists
if [ -f "/var/www/html/index.html" ]; then
    echo "Backing up default Apache page..."
    sudo mv /var/www/html/index.html /var/www/html/index.html.backup.$(date +%Y%m%d_%H%M%S)
fi

# Deploy new version
echo "Deploying application files..."
sudo cp -r * /var/www/html/
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

echo "✅ Application files deployed successfully"
'''

    def get_verification_script(self):
        """Get the standard verification script"""
        return '''
set -e

echo "=== LAMP Stack Verification ==="

# Check Apache
echo "Checking Apache..."
sudo systemctl is-active apache2 && echo "✅ Apache is running" || echo "❌ Apache is not running"

# Check MySQL/MariaDB
echo "Checking MySQL/MariaDB..."
sudo systemctl is-active mysql && echo "✅ MySQL is running" || echo "❌ MySQL is not running"

# Check PHP
echo "Checking PHP..."
php --version | head -1 && echo "✅ PHP is installed" || echo "❌ PHP is not installed"

# Check web server response
echo "Checking web server response..."
curl -f -s http://localhost/ > /dev/null && echo "✅ Web server responding" || echo "❌ Web server not responding"

# Check if application files exist
echo "Checking application files..."
ls -la /var/www/html/ | head -10

echo "=== LAMP Stack Verification Complete ==="
'''

    def install_lamp_stack(self, timeout=900, max_retries=8):
        """Install LAMP stack with enhanced retry logic"""
        print("📦 Installing LAMP stack components...")
        return self.run_command(self.get_lamp_install_script(), timeout=timeout, max_retries=max_retries)

    def setup_database(self, timeout=120, max_retries=3):
        """Set up the database"""
        print("🗄️ Setting up MySQL database...")
        return self.run_command(self.get_database_setup_script(), timeout=timeout, max_retries=max_retries)

    def deploy_application_files(self, timeout=300, max_retries=3):
        """Deploy application files"""
        print("🚀 Deploying application files...")
        return self.run_command(self.get_deployment_script(), timeout=timeout, max_retries=max_retries)

    def verify_lamp_stack(self, timeout=120, max_retries=3):
        """Verify LAMP stack installation"""
        print("🔍 Verifying LAMP stack components...")
        return self.run_command(self.get_verification_script(), timeout=timeout, max_retries=max_retries)

    def create_environment_file(self, env_vars, timeout=60):
        """Create environment file with given variables"""
        if not env_vars:
            return True, ""
        
        print("📝 Creating environment file...")
        env_content = "\\n".join([f"{k}={v}" for k, v in env_vars.items()])
        env_script = f'''
sudo tee /var/www/html/.env > /dev/null << 'ENVEOF'
{env_content}
ENVEOF
sudo chown www-data:www-data /var/www/html/.env
'''
        return self.run_command(env_script, timeout=timeout)
