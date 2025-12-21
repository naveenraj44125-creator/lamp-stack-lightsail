"""Nginx web server configurator"""

from .base_configurator import BaseConfigurator
from os_detector import OSDetector


class NginxConfigurator(BaseConfigurator):
    """Configure Nginx for the application"""
    
    def configure(self) -> bool:
        """Configure Nginx for the application"""
        # Get OS information from client
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        os_info = getattr(self.client, 'os_info', {'package_manager': 'apt', 'user': 'ubuntu'})
        
        # Get OS-specific information - specify nginx as web server
        self.user_info = OSDetector.get_user_info(os_type, 'nginx')
        self.pkg_commands = OSDetector.get_package_manager_commands(os_info['package_manager'])
        self.svc_commands = OSDetector.get_service_commands(os_info.get('service_manager', 'systemd'))
        
        document_root = self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
        
        # CRITICAL: Fix directory ownership now that Nginx is installed
        print("🔧 Setting proper directory ownership for Nginx...")
        ownership_success = self._fix_directory_ownership(document_root)
        if not ownership_success:
            print("⚠️  Failed to set directory ownership, but continuing...")
        
        # Check if Node.js is enabled - if so, configure as reverse proxy
        nodejs_enabled = self.config.get('dependencies.nodejs.enabled', False)
        python_enabled = self.config.get('dependencies.python.enabled', False)
        
        if nodejs_enabled:
            return self._configure_nodejs_proxy()
        elif python_enabled:
            return self._configure_python_proxy()
        else:
            return self._configure_static_or_php(document_root)
    
    def _disable_default_server_block(self) -> bool:
        """Completely remove the default nginx server block to prevent conflicts"""
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        
        print("🔧 Completely removing default nginx server block...")
        
        if os_type in ['amazon_linux', 'amazon_linux_2023', 'centos', 'rhel']:
            # For Amazon Linux, completely remove the default server block from nginx.conf
            script = '''
set -e
echo "Removing default server block from nginx.conf..."

# Backup original nginx.conf if not already backed up
if [ ! -f /etc/nginx/nginx.conf.original ]; then
    sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.original
    echo "✅ Backed up original nginx.conf"
fi

# Completely remove the default server block from nginx.conf
sudo python3 << 'PYTHON_EOF'
import re

# Read the original nginx.conf
with open('/etc/nginx/nginx.conf', 'r') as f:
    content = f.read()

# Find and completely remove the server block within the http context
# This regex matches the server block and removes it entirely
lines = content.split('\\n')
new_lines = []
in_server_block = False
brace_count = 0
skip_server = False

for line in lines:
    stripped = line.strip()
    
    # Check if we're starting a server block
    if 'server' in stripped and '{' in stripped and not in_server_block:
        # This is the start of a server block - skip it entirely
        in_server_block = True
        skip_server = True
        brace_count = stripped.count('{') - stripped.count('}')
        continue
    
    if in_server_block:
        # Count braces to know when server block ends
        brace_count += line.count('{') - line.count('}')
        
        # If brace count reaches 0, we've closed the server block
        if brace_count <= 0:
            in_server_block = False
            skip_server = False
        continue
    
    # Keep all other lines
    new_lines.append(line)

# Write the new content without the server block
new_content = '\\n'.join(new_lines)
with open('/etc/nginx/nginx.conf', 'w') as f:
    f.write(new_content)

print("✅ Completely removed default server block from nginx.conf")
PYTHON_EOF

# Remove default files
sudo rm -f /etc/nginx/conf.d/default.conf
sudo rm -f /usr/share/nginx/html/index.html

echo "✅ Default server block completely removed"
'''
        else:  # Ubuntu/Debian
            script = '''
set -e
echo "Disabling default nginx site..."

# Remove default site symlink
sudo rm -f /etc/nginx/sites-enabled/default

# Remove default HTML file
sudo rm -f /var/www/html/index.nginx-debian.html

echo "✅ Default nginx site disabled"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        print(output)
        return success

    def _configure_nodejs_proxy(self) -> bool:
        """Configure Nginx as reverse proxy for Node.js"""
        print("🔧 Configuring Nginx as reverse proxy for Node.js...")
        
        # First disable the default server block
        if not self._disable_default_server_block():
            print("⚠️  Failed to disable default server block, but continuing...")
        
        # Get OS-specific nginx configuration directory
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        
        # Determine nginx config directory based on OS
        if os_type in ['amazon_linux', 'amazon_linux_2023', 'centos', 'rhel']:
            nginx_conf_dir = '/etc/nginx/conf.d'
            nginx_conf_file = f'{nginx_conf_dir}/app.conf'
        else:  # Ubuntu/Debian
            nginx_conf_dir = '/etc/nginx/sites-available'
            nginx_conf_file = '/etc/nginx/sites-enabled/app'
        
        script = f'''
set -e
echo "Configuring Nginx as reverse proxy for Node.js application..."

# Create server block configuration for Node.js proxy
cat > /tmp/app << 'EOF'
server {{
    listen 80;
    server_name _;
    
    location / {{
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}}
EOF

# Install the configuration based on OS type
sudo mkdir -p {nginx_conf_dir}
'''
        
        if os_type in ['amazon_linux', 'amazon_linux_2023', 'centos', 'rhel']:
            script += f'''
sudo mv /tmp/app {nginx_conf_file}
'''
        else:  # Ubuntu/Debian
            script += f'''
sudo mv /tmp/app {nginx_conf_dir}/app
sudo ln -sf {nginx_conf_dir}/app {nginx_conf_file}
'''
        
        script += '''
echo "✅ Nginx configured as reverse proxy for Node.js"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        print(output)
        return success
    
    def _configure_python_proxy(self) -> bool:
        """Configure Nginx as reverse proxy for Python"""
        print("🔧 Configuring Nginx as reverse proxy for Python...")
        
        # First disable the default server block
        if not self._disable_default_server_block():
            print("⚠️  Failed to disable default server block, but continuing...")
        
        # Get OS-specific nginx configuration directory
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        
        # Determine nginx config directory based on OS
        if os_type in ['amazon_linux', 'amazon_linux_2023', 'centos', 'rhel']:
            nginx_conf_dir = '/etc/nginx/conf.d'
            nginx_conf_file = f'{nginx_conf_dir}/app.conf'
        else:  # Ubuntu/Debian
            nginx_conf_dir = '/etc/nginx/sites-available'
            nginx_conf_file = '/etc/nginx/sites-enabled/app'
        
        script = f'''
set -e
echo "Configuring Nginx as reverse proxy for Python application..."

# Create server block configuration for Python proxy
cat > /tmp/app << 'EOF'
server {{
    listen 80;
    server_name _;
    
    location / {{
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Health check endpoint
    location /health {{
        proxy_pass http://localhost:5000/health;
        access_log off;
    }}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}}
EOF

# Install the configuration based on OS type
sudo mkdir -p {nginx_conf_dir}
'''
        
        if os_type in ['amazon_linux', 'amazon_linux_2023', 'centos', 'rhel']:
            script += f'''
sudo mv /tmp/app {nginx_conf_file}
'''
        else:  # Ubuntu/Debian
            script += f'''
sudo mv /tmp/app {nginx_conf_dir}/app
sudo ln -sf {nginx_conf_dir}/app {nginx_conf_file}
'''
        
        script += '''
echo "✅ Nginx configured as reverse proxy for Python"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        print(output)
        return success
    
    def _configure_static_or_php(self, document_root: str) -> bool:
        """Configure Nginx for static files or PHP application"""
        print("🔧 Configuring Nginx for static/PHP application...")
        
        # First disable the default server block
        if not self._disable_default_server_block():
            print("⚠️  Failed to disable default server block, but continuing...")
        
        # Get OS-specific nginx configuration directory
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        
        # Determine nginx config directory based on OS
        if os_type in ['amazon_linux', 'amazon_linux_2023', 'centos', 'rhel']:
            nginx_conf_dir = '/etc/nginx/conf.d'
            nginx_conf_file = f'{nginx_conf_dir}/app.conf'
        else:  # Ubuntu/Debian
            nginx_conf_dir = '/etc/nginx/sites-available'
            nginx_conf_file = '/etc/nginx/sites-enabled/app'
        
        script = f'''
set -e
echo "Configuring Nginx for application..."

# Check if this is a React/SPA application
if [ -f "{document_root}/index.html" ]; then
    echo "Detected React/SPA application"
    
    cat > /tmp/app << 'EOF'
server {{
    listen 80;
    server_name _;
    
    root {document_root};
    index index.html index.htm;
    
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}}
EOF
else
    echo "Detected PHP/traditional web application"
    
    cat > /tmp/app << 'EOF'
server {{
    listen 80;
    server_name _;
    
    root {document_root};
    index index.php index.html index.htm;
    
    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}
    
    location ~ \\.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php-fpm.sock;
    }}
    
    location ~ /\\.ht {{
        deny all;
    }}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}}
EOF
fi

# Install the configuration based on OS type
sudo mkdir -p {nginx_conf_dir}
'''

        if os_type in ['amazon_linux', 'amazon_linux_2023', 'centos', 'rhel']:
            script += f'''
sudo mv /tmp/app {nginx_conf_file}
'''
        else:  # Ubuntu/Debian
            script += f'''
sudo mv /tmp/app {nginx_conf_dir}/app
sudo ln -sf {nginx_conf_dir}/app {nginx_conf_file}
'''
        
        script += '''
echo "✅ Nginx configured for application"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        print(output)
        return success
    
    def _fix_directory_ownership(self, document_root: str) -> bool:
        """Fix directory ownership for Nginx"""
        print("🔧 Fixing directory ownership for Nginx...")
    
        # Get web server user/group from OS info
        nginx_user = self.user_info.get('nginx_user', 'nginx')
        nginx_group = self.user_info.get('nginx_group', 'nginx')
        
        script = f'''
set -e
echo "Fixing directory ownership for Nginx..."

# Check if nginx user exists
if id "{nginx_user}" &>/dev/null; then
    echo "✅ Nginx user '{nginx_user}' exists"
    
    # Set ownership for web directory
    echo "Setting ownership of {document_root} to {nginx_user}:{nginx_group}"
    sudo chown -R {nginx_user}:{nginx_group} {document_root}
    
    # Set proper permissions
    sudo chmod -R 755 {document_root}
    sudo chmod -R 777 {document_root}/tmp 2>/dev/null || true
    
    echo "✅ Directory ownership fixed for Nginx"
else
    echo "⚠️  Nginx user '{nginx_user}' does not exist yet, keeping current ownership"
fi
'''
        
        success, output = self.client.run_command(script, timeout=60)
        print(output)
        return success