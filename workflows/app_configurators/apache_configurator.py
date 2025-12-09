"""Apache web server configurator"""

from .base_configurator import BaseConfigurator


class ApacheConfigurator(BaseConfigurator):
    """Configure Apache for the application"""
    
    def configure(self) -> bool:
        """Configure Apache for the application"""
        app_type = self.config.get('application.type', 'web')
        document_root = self.config.get('dependencies.apache.config.document_root', '/var/www/html')
        
        print(f"🔧 Configuring Apache for {app_type} application...")
        
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
        print(output)
        return success
