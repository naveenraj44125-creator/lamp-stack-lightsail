#!/usr/bin/env python3
"""
Test script to demonstrate improved descriptive logging
"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_logging_format():
    """Simulate the new logging format for different script types"""
    
    print("🧪 Testing Improved Descriptive Logging")
    print("=" * 50)
    
    # Test cases that match your deployment scripts
    test_scripts = [
        {
            "name": "Git Installation Script",
            "script": """set -e
echo "Installing Git..."

# Install Git
sudo apt-get update
sudo apt-get install -y git

# Install Git LFS if requested
if [ "False" = "True" ]; then
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
    sudo apt-get install -y git-lfs
    echo "✅ Git LFS installed"
fi

echo "✅ Git installation completed" """
        },
        {
            "name": "Firewall Configuration Script", 
            "script": """set -e
echo "Configuring firewall..."

# Install UFW if not present
sudo apt-get update
sudo apt-get install -y ufw

# Reset UFW to defaults
sudo ufw --force reset

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow specified ports
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

# Enable UFW
sudo ufw --force enable

echo "✅ Firewall configuration completed" """
        },
        {
            "name": "PHP Installation Script",
            "script": """set -e
echo "🔧 Installing PHP 8.3..."

# Install PHP and extensions
sudo apt-get update
sudo apt-get install -y php8.3 php8.3-fpm php-pdo php-mysql php-curl php-json php-mbstring

# Install Composer if requested
if [ "True" = "True" ]; then
    curl -sS https://getcomposer.org/installer | php
    sudo mv composer.phar /usr/local/bin/composer
    sudo chmod +x /usr/local/bin/composer
    echo "✅ Composer installed"
fi

echo "✅ PHP 8.3 installation completed" """
        },
        {
            "name": "Script with Comment Description",
            "script": """set -e
# Configure Apache virtual host settings
sudo mkdir -p /etc/apache2/sites-available
sudo a2ensite default
sudo systemctl reload apache2"""
        },
        {
            "name": "Script without Clear Description",
            "script": """set -e
sudo mkdir -p /var/www/html
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html"""
        }
    ]
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    
    print("\n📋 How different scripts will appear in logs:")
    print("-" * 60)
    
    for i, test in enumerate(test_scripts, 1):
        print(f"\n{i}. {test['name']}:")
        
        # Simulate the logging logic
        command = test['script']
        lines = [line.strip() for line in command.split('\n') if line.strip()]
        line_count = len(lines)
        
        # Look for descriptive echo statements
        description = None
        for line in lines:
            if line.startswith('echo ') and ('"' in line or "'" in line):
                # Extract echo message
                if line.startswith('echo "'):
                    description = line.replace('echo "', '').replace('"', '').strip()
                elif line.startswith("echo '"):
                    description = line.replace("echo '", "").replace("'", "").strip()
                else:
                    # Handle echo without quotes
                    description = line.replace('echo ', '').strip()
                
                # Clean up common patterns
                if description.startswith('✅') or description.startswith('🔧') or description.startswith('📦'):
                    description = description[2:].strip()  # Remove emoji and space
                break
        
        # If no echo found, look for comments that describe the script
        if not description:
            for line in lines:
                if line.startswith('# ') and len(line) > 3:
                    description = line[2:].strip()
                    break
        
        # If still no description, use the first meaningful command
        if not description:
            for line in lines:
                if not line.startswith('#') and line != 'set -e' and len(line) > 5:
                    description = line[:40] + ('...' if len(line) > 40 else '')
                    break
        
        # Fallback to generic description
        if not description:
            description = "Multi-line script"
        
        log_entry = f"[{timestamp}] SCRIPT: {description} ({line_count} commands)"
        print(f"   {log_entry}")
    
    print("\n" + "=" * 60)
    print("✅ Much better than just 'SCRIPT: ... (X commands)'!")
    print("\n🎯 Key Improvements:")
    print("   • Extracts meaningful descriptions from echo statements")
    print("   • Falls back to comment descriptions")
    print("   • Shows first command if no description found")
    print("   • Removes emoji prefixes for cleaner logs")
    print("   • Always shows command count")

if __name__ == "__main__":
    simulate_logging_format()