"""Apache web server configurator"""

from .base_configurator import BaseConfigurator


class ApacheConfigurator(BaseConfigurator):
    """Configure Apache for the application"""
    
    def configure(self) -> bool:
        """Configure Apache for the application"""
        app_type = self.config.get('application.type', 'web')
        document_root = self.config.get('dependencies.apache.config.document_root', '/var/www/html')
        
        print(f"🔧 Configuring Apache for {app_type} application...")
        
        # Get OS information from client
        if hasattr(self.client, 'os_info') and self.client.os_info:
            package_manager = self.client.os_info.get('package_manager', 'apt')
            web_user = self.client.os_info.get('web_user', 'www-data')
            web_group = self.client.os_info.get('web_group', 'www-data')
        else:
            # Fallback to Ubuntu defaults
            package_manager = 'apt'
            web_user = 'www-data'
            web_group = 'www-data'
        
        if package_manager == 'apt':
            # Ubuntu/Debian Apache configuration
            script = f'''
set -e
echo "Configuring Apache for application on Ubuntu/Debian..."

# Create virtual host configuration with proper DirectoryIndex
# IMPORTANT: Prioritize index.php over index.html for PHP applications
cat > /tmp/app.conf << 'EOF'
<VirtualHost *:80>
    DocumentRoot {document_root}
    
    # CRITICAL: Prioritize PHP files over HTML files
    DirectoryIndex index.php index.html index.htm
    
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

# Ensure proper permissions
sudo chown -R {web_user}:{web_group} {document_root}
sudo chmod -R 755 {document_root}

# IMPORTANT: Remove any default index.html if index.php exists
# This prevents the default page from being served instead of the PHP app
if [ -f "{document_root}/index.php" ] && [ -f "{document_root}/index.html" ]; then
    # Check if index.html is a default placeholder (contains "Application Deployed Successfully")
    if grep -q "Application Deployed Successfully" {document_root}/index.html 2>/dev/null; then
        echo "🗑️  Removing default index.html placeholder (index.php exists)..."
        sudo rm -f {document_root}/index.html
    fi
fi

echo "✅ Apache configured for application on Ubuntu/Debian"
'''
        else:
            # Amazon Linux/RHEL/CentOS Apache configuration
            script = f'''
set -e
echo "Configuring Apache for application on Amazon Linux/RHEL/CentOS..."

# Create virtual host configuration with proper DirectoryIndex
# IMPORTANT: Prioritize index.php over index.html for PHP applications
cat > /tmp/app.conf << 'EOF'
<VirtualHost *:80>
    DocumentRoot {document_root}
    
    # CRITICAL: Prioritize PHP files over HTML files
    DirectoryIndex index.php index.html index.htm
    
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
    
    ErrorLog /var/log/httpd/app_error.log
    CustomLog /var/log/httpd/app_access.log combined
</VirtualHost>
EOF

# Install the configuration
sudo mv /tmp/app.conf /etc/httpd/conf.d/app.conf

# Also update the main httpd.conf DirectoryIndex to prioritize PHP
# This ensures PHP files are served even if our vhost config isn't loaded first
if grep -q "DirectoryIndex index.html" /etc/httpd/conf/httpd.conf; then
    echo "📝 Updating main httpd.conf DirectoryIndex to prioritize PHP..."
    sudo sed -i 's/DirectoryIndex index.html/DirectoryIndex index.php index.html index.htm/' /etc/httpd/conf/httpd.conf
fi

# Ensure proper permissions
sudo chown -R {web_user}:{web_group} {document_root}
sudo chmod -R 755 {document_root}

# IMPORTANT: Remove any default index.html if index.php exists
# This prevents the default page from being served instead of the PHP app
if [ -f "{document_root}/index.php" ] && [ -f "{document_root}/index.html" ]; then
    # Check if index.html is a default placeholder (contains "Application Deployed Successfully")
    if grep -q "Application Deployed Successfully" {document_root}/index.html 2>/dev/null; then
        echo "🗑️  Removing default index.html placeholder (index.php exists)..."
        sudo rm -f {document_root}/index.html
    fi
fi

# Only create default index.html if document root is completely empty
# AND no PHP files will be deployed (check for .php in package files)
FILE_COUNT=$(find {document_root} -maxdepth 1 -type f | wc -l)
if [ "$FILE_COUNT" -eq 0 ]; then
    echo "📝 Document root is empty, creating default index.html..."
    cat > /tmp/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Application Deployed Successfully</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .success {{ color: #28a745; }}
        .info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1 class="success">✅ Application Deployed Successfully!</h1>
    <div class="info">
        <p><strong>Server:</strong> Apache on Amazon Linux</p>
        <p><strong>Document Root:</strong> {document_root}</p>
        <p><strong>Status:</strong> Web server is running and accessible</p>
    </div>
    <p>Your application has been deployed successfully. You can now upload your application files to {document_root}.</p>
</body>
</html>
EOF
    sudo mv /tmp/index.html {document_root}/index.html
    sudo chown {web_user}:{web_group} {document_root}/index.html
    sudo chmod 644 {document_root}/index.html
    echo "✅ Created default index.html"
else
    echo "ℹ️  Document root already has $FILE_COUNT file(s), skipping default index.html creation"
fi

# Restart Apache to apply configuration
sudo systemctl restart httpd

echo "✅ Apache configured for application on Amazon Linux/RHEL/CentOS"
'''
        
        success, output = self.client.run_command(script, timeout=120)
        print(output)
        return success
