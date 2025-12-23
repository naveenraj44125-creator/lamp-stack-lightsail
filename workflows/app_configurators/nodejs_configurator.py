"""Node.js application configurator"""
from .base_configurator import BaseConfigurator

class NodeJSConfigurator(BaseConfigurator):
    """Handles Node.js application configuration"""
    
    def configure(self) -> bool:
        """Configure Node.js application - uses PM2 if enabled, otherwise systemd"""
        print("🔧 Configuring Node.js application...")
        
        # Check if PM2 is enabled in config
        pm2_config = self.config.get('dependencies.pm2', {})
        pm2_enabled = pm2_config.get('enabled', False)
        
        if pm2_enabled:
            return self._configure_with_pm2(pm2_config)
        else:
            return self._configure_with_systemd()
    
    def _get_env_fix_script(self) -> str:
        """Get the script to fix common environment variable issues"""
        # Using simpler quoting that works reliably through SSH
        return '''
# Fix common environment variable naming issues
if [ -f "/opt/nodejs-app/.env" ]; then
    # Add S3_BUCKET_NAME if BUCKET_NAME exists (for multer-s3 compatibility)
    if grep -q "^BUCKET_NAME=" /opt/nodejs-app/.env && ! grep -q "^S3_BUCKET_NAME=" /opt/nodejs-app/.env; then
        # Extract bucket name value using awk for reliable parsing
        BUCKET_VALUE=$(grep "^BUCKET_NAME=" /opt/nodejs-app/.env | head -1 | awk -F= '{print $2}' | sed 's/^"//;s/"$//;s/^'"'"'//;s/'"'"'$//')
        if [ -n "$BUCKET_VALUE" ]; then
            echo "S3_BUCKET_NAME=\\"$BUCKET_VALUE\\"" >> /opt/nodejs-app/.env
            echo "✅ Added S3_BUCKET_NAME=$BUCKET_VALUE for S3 compatibility"
        fi
    fi
fi

# Fix hardcoded PORT in server.js (common issue)
if [ -f "/opt/nodejs-app/server.js" ]; then
    # Check for hardcoded PORT like "const PORT = 5000;" or "const PORT = 3000;"
    if grep -qE "const PORT = [0-9]+;" /opt/nodejs-app/server.js; then
        sed -i -E 's/const PORT = [0-9]+;/const PORT = process.env.PORT || 3000;/' /opt/nodejs-app/server.js
        echo "✅ Fixed hardcoded PORT in server.js to use process.env.PORT"
    fi
fi
'''
    
    def _configure_with_pm2(self, pm2_config: dict) -> bool:
        """Configure Node.js application with PM2 process manager"""
        print("🔧 Using PM2 process manager (pm2.enabled: true)")
        
        # Get OS information from config if available
        os_type = getattr(self.config, 'os_type', 'ubuntu')
        os_info = getattr(self.config, 'os_info', {'user': 'ubuntu'})
        default_user = os_info.get('user', 'ubuntu')
        
        # Get PM2 configuration
        pm2_settings = pm2_config.get('config', {})
        app_name = pm2_settings.get('app_name', 'nodejs-app')
        instances = pm2_settings.get('instances', 1)
        exec_mode = pm2_settings.get('exec_mode', 'fork')
        
        # Build the ecosystem.config content separately to avoid f-string issues
        # Extension (.js or .cjs) is determined at runtime based on package.json "type" field
        ecosystem_js = '''const fs = require('fs');
const path = require('path');

// Load environment variables from .env file
const envPath = path.join(__dirname, '.env');
const env = {};

if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const [key, ...valueParts] = trimmed.split('=');
      if (key && valueParts.length > 0) {
        let value = valueParts.join('=');
        // Remove surrounding quotes if present
        if ((value.startsWith('"') && value.endsWith('"')) || 
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
        env[key.trim()] = value;
      }
    }
  });
}

// Detect entry point - check package.json first for explicit entry point
let script = null;
const pkgPath = path.join(__dirname, 'package.json');
if (fs.existsSync(pkgPath)) {
  try {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
    // Check scripts.start or scripts.server for entry point hints
    if (pkg.scripts) {
      const startScript = pkg.scripts.start || pkg.scripts.server || '';
      // Extract file path from "node server/index.js" or similar
      const nodeMatch = startScript.match(/node\\s+([\\w\\/.-]+\\.js)/);
      if (nodeMatch && fs.existsSync(path.join(__dirname, nodeMatch[1]))) {
        script = nodeMatch[1];
      }
    }
    // Check main field
    if (!script && pkg.main && fs.existsSync(path.join(__dirname, pkg.main))) {
      script = pkg.main;
    }
  } catch (e) {
    // Ignore JSON parse errors
  }
}

// Fallback to common entry points if not found in package.json
if (!script) {
  const candidates = [
    'server/index.js',  // Common for server subdirectory
    'src/index.js',     // Common for src subdirectory
    'server.js',
    'app.js',
    'index.js'
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(path.join(__dirname, candidate))) {
      script = candidate;
      break;
    }
  }
}

// Final fallback
if (!script) {
  script = 'server.js';
}

module.exports = {
  apps: [{
    name: 'nodejs-app',
    script: script,
    cwd: __dirname,
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
      ...env
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '500M',
    error_file: '/var/log/nodejs-app/error.log',
    out_file: '/var/log/nodejs-app/output.log',
    log_file: '/var/log/nodejs-app/combined.log',
    time: true
  }]
};'''
        
        env_fix_script = self._get_env_fix_script()
        
        script = f'''
set -e
echo "Configuring Node.js with PM2 process manager on {os_type}..."

# Detect entry point file - check package.json first
ENTRY_POINT=""
if [ -f "/opt/nodejs-app/package.json" ]; then
    # Try to extract entry point from package.json scripts
    SCRIPT_ENTRY=$(cat /opt/nodejs-app/package.json | python3 -c "
import sys, json
try:
    pkg = json.load(sys.stdin)
    scripts = pkg.get('scripts', {{}})
    # Check start or server script for 'node <file>' pattern
    for key in ['start', 'server']:
        script = scripts.get(key, '')
        if 'node ' in script:
            import re
            match = re.search(r'node\s+([\w/.-]+\.js)', script)
            if match:
                print(match.group(1))
                sys.exit(0)
    # Check main field
    main = pkg.get('main', '')
    if main:
        print(main)
except:
    pass
" 2>/dev/null || echo "")
    
    if [ -n "$SCRIPT_ENTRY" ] && [ -f "/opt/nodejs-app/$SCRIPT_ENTRY" ]; then
        ENTRY_POINT="$SCRIPT_ENTRY"
        echo "✅ Found entry point from package.json: $ENTRY_POINT"
    fi
fi

# Fallback to common entry points
if [ -z "$ENTRY_POINT" ]; then
    for candidate in "server/index.js" "src/index.js" "server.js" "app.js" "index.js"; do
        if [ -f "/opt/nodejs-app/$candidate" ]; then
            ENTRY_POINT="$candidate"
            echo "✅ Found $candidate as entry point"
            break
        fi
    done
fi

if [ -z "$ENTRY_POINT" ]; then
    echo "❌ No entry point file found"
    ls -la /opt/nodejs-app/ || echo "Directory does not exist"
    exit 1
fi

# Install dependencies if package.json exists
if [ -f "/opt/nodejs-app/package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd /opt/nodejs-app && sudo -u {default_user} npm install --production 2>&1 | tee /tmp/npm-install.log
    echo "✅ Dependencies installed"
else
    echo "ℹ️  No package.json found, skipping dependency installation"
fi

# Create log directory
sudo mkdir -p /var/log/nodejs-app
sudo chown {default_user}:{default_user} /var/log/nodejs-app

# Copy environment file if it exists in web root (for LAMP-style deployments)
if [ -f "/var/www/html/.env" ] && [ ! -f "/opt/nodejs-app/.env" ]; then
    echo "📋 Copying environment variables from web root to Node.js app..."
    sudo cp /var/www/html/.env /opt/nodejs-app/.env
    sudo chown {default_user}:{default_user} /opt/nodejs-app/.env
    echo "✅ Environment file copied"
fi

{env_fix_script}

# Install PM2 globally if not installed
echo "📦 Installing PM2 globally..."
if ! command -v pm2 &> /dev/null; then
    sudo npm install -g pm2
    echo "✅ PM2 installed"
else
    echo "✅ PM2 already installed"
fi

# Stop any existing PM2 processes for this app
echo "🔄 Stopping existing PM2 processes..."
pm2 delete "{app_name}" 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Set proper ownership
sudo chown -R {default_user}:{default_user} /opt/nodejs-app

# Start the app with PM2
echo "🚀 Starting Node.js application with PM2..."
cd /opt/nodejs-app

# Detect if project uses ES modules (has "type": "module" in package.json)
ECOSYSTEM_EXT="js"
if [ -f "/opt/nodejs-app/package.json" ]; then
    if grep -q '"type"[[:space:]]*:[[:space:]]*"module"' /opt/nodejs-app/package.json; then
        echo "📦 Detected ES modules project, using .cjs extension for PM2 config"
        ECOSYSTEM_EXT="cjs"
    fi
fi

# Create PM2 ecosystem file with environment variables
echo "📋 Creating PM2 ecosystem configuration..."
cat > /opt/nodejs-app/ecosystem.config.$ECOSYSTEM_EXT << 'EOFECO'
{ecosystem_js}
EOFECO

sudo chown {default_user}:{default_user} /opt/nodejs-app/ecosystem.config.$ECOSYSTEM_EXT

# Show loaded environment variables (without values for security)
if [ -f "/opt/nodejs-app/.env" ]; then
    echo "📋 Environment variables loaded from .env:"
    cat /opt/nodejs-app/.env | grep -v "^#" | grep "=" | cut -d'=' -f1 | while read key; do
        echo "   - $key"
    done
fi

# Start with PM2 using ecosystem file
pm2 start /opt/nodejs-app/ecosystem.config.$ECOSYSTEM_EXT

# Wait for app to start
sleep 5

# Check PM2 status
echo ""
echo "📊 PM2 Status:"
pm2 list

# Save PM2 process list for startup
pm2 save 2>/dev/null || true

# Setup PM2 to start on boot
pm2 startup systemd -u {default_user} --hp /home/{default_user} 2>/dev/null || true

# Check if app is listening on port 3000
if sudo ss -tlnp 2>/dev/null | grep -q ":3000" || sudo netstat -tlnp 2>/dev/null | grep -q ":3000"; then
    echo "✅ Application is listening on port 3000"
else
    echo "⚠️  Application may not be listening on port 3000"
    sudo ss -tlnp 2>/dev/null | grep node || sudo netstat -tlnp 2>/dev/null | grep node || echo "No node process found listening"
fi

# Test local connection
if curl -s http://localhost:3000/ > /dev/null; then
    echo "✅ Local connection to port 3000 successful"
else
    echo "⚠️  Local connection to port 3000 failed"
    echo "📋 PM2 logs:"
    pm2 logs "{app_name}" --lines 20 --nostream 2>&1 || true
fi

echo "✅ Node.js application configured with PM2 on {os_type}"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        print(output)
        return success
    
    def _configure_with_systemd(self) -> bool:
        """Configure Node.js application with systemd service (OS-agnostic)"""
        print("🔧 Using systemd service (pm2.enabled: false or not set)")
        
        # Get OS information from config if available
        os_type = getattr(self.config, 'os_type', 'ubuntu')
        os_info = getattr(self.config, 'os_info', {'user': 'ubuntu'})
        default_user = os_info.get('user', 'ubuntu')
        
        env_fix_script = self._get_env_fix_script()
        
        script = f'''
set -e
echo "Configuring Node.js for application on {os_type}..."

# Detect entry point file - check package.json first
ENTRY_POINT=""
if [ -f "/opt/nodejs-app/package.json" ]; then
    # Try to extract entry point from package.json scripts
    SCRIPT_ENTRY=$(cat /opt/nodejs-app/package.json | python3 -c "
import sys, json
try:
    pkg = json.load(sys.stdin)
    scripts = pkg.get('scripts', {{}})
    # Check start or server script for 'node <file>' pattern
    for key in ['start', 'server']:
        script = scripts.get(key, '')
        if 'node ' in script:
            import re
            match = re.search(r'node\s+([\w/.-]+\.js)', script)
            if match:
                print(match.group(1))
                sys.exit(0)
    # Check main field
    main = pkg.get('main', '')
    if main:
        print(main)
except:
    pass
" 2>/dev/null || echo "")
    
    if [ -n "$SCRIPT_ENTRY" ] && [ -f "/opt/nodejs-app/$SCRIPT_ENTRY" ]; then
        ENTRY_POINT="$SCRIPT_ENTRY"
        echo "✅ Found entry point from package.json: $ENTRY_POINT"
    fi
fi

# Fallback to common entry points
if [ -z "$ENTRY_POINT" ]; then
    for candidate in "server/index.js" "src/index.js" "server.js" "app.js" "index.js"; do
        if [ -f "/opt/nodejs-app/$candidate" ]; then
            ENTRY_POINT="$candidate"
            echo "✅ Found $candidate as entry point"
            break
        fi
    done
fi

if [ -z "$ENTRY_POINT" ]; then
    echo "❌ No entry point file found"
    ls -la /opt/nodejs-app/ || echo "Directory does not exist"
    exit 1
fi

# Install dependencies if package.json exists
if [ -f "/opt/nodejs-app/package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd /opt/nodejs-app && sudo -u {default_user} npm install --production 2>&1 | tee /tmp/npm-install.log
    echo "✅ Dependencies installed"
else
    echo "ℹ️  No package.json found, skipping dependency installation"
fi

# Create log directory
sudo mkdir -p /var/log/nodejs-app
sudo chown {default_user}:{default_user} /var/log/nodejs-app

# Copy environment file if it exists in web root (for LAMP-style deployments)
if [ -f "/var/www/html/.env" ] && [ ! -f "/opt/nodejs-app/.env" ]; then
    echo "📋 Copying environment variables from web root to Node.js app..."
    sudo cp /var/www/html/.env /opt/nodejs-app/.env
    sudo chown {default_user}:{default_user} /opt/nodejs-app/.env
    echo "✅ Environment file copied"
fi

{env_fix_script}

# Load environment variables from .env file for systemd
ENV_LINES=""
if [ -f "/opt/nodejs-app/.env" ]; then
    echo "📋 Loading environment variables for systemd..."
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Skip comments and empty lines
        case "$key" in
            \#*|"") continue ;;
        esac
        # Remove quotes from value
        value=$(echo "$value" | sed 's/^"//;s/"$//;s/^'"'"'//;s/'"'"'$//')
        ENV_LINES="$ENV_LINES
Environment=$key=$value"
    done < /opt/nodejs-app/.env
fi

# Create systemd service for Node.js app
echo "📝 Creating systemd service file with entry point: $ENTRY_POINT"
sudo tee /etc/systemd/system/nodejs-app.service > /dev/null << EOF
[Unit]
Description=Node.js Application
After=network.target

[Service]
Type=simple
User={default_user}
WorkingDirectory=/opt/nodejs-app
ExecStart=/usr/bin/node $ENTRY_POINT
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=3000$ENV_LINES
StandardOutput=append:/var/log/nodejs-app/output.log
StandardError=append:/var/log/nodejs-app/error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable the service
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable nodejs-app.service

# Stop any existing instance
sudo systemctl stop nodejs-app.service 2>/dev/null || true

# Start the service
echo "🚀 Starting Node.js application service..."
sudo systemctl start nodejs-app.service

# Wait and check if service started successfully
sleep 5

if systemctl is-active --quiet nodejs-app.service; then
    echo "✅ Node.js app service started successfully"
    sudo systemctl status nodejs-app.service --no-pager
    
    # Check if app is listening on port 3000
    sleep 2
    if sudo ss -tlnp 2>/dev/null | grep -q ":3000" || sudo netstat -tlnp 2>/dev/null | grep -q ":3000"; then
        echo "✅ Application is listening on port 3000"
    else
        echo "⚠️  Application may not be listening on port 3000"
        sudo ss -tlnp 2>/dev/null | grep node || sudo netstat -tlnp 2>/dev/null | grep node || echo "No node process found listening"
    fi
    
    # Test local connection
    if curl -s http://localhost:3000/ > /dev/null; then
        echo "✅ Local connection to port 3000 successful"
    else
        echo "⚠️  Local connection to port 3000 failed"
    fi
else
    echo "❌ Node.js app service failed to start"
    sudo systemctl status nodejs-app.service --no-pager || true
    echo "=== Service Logs ==="
    sudo journalctl -u nodejs-app.service -n 50 --no-pager || true
    echo "=== Application Error Log ==="
    sudo cat /var/log/nodejs-app/error.log 2>/dev/null || echo "No error log found"
    exit 1
fi

echo "✅ Node.js application configured successfully on {os_type}"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        print(output)
        return success


class NodeJSMinimalConfigurator(BaseConfigurator):
    """Minimal Node.js configurator that skips service creation"""
    
    def configure(self) -> bool:
        """Install Node.js dependencies without creating systemd service"""
        print("🔧 Configuring Node.js (minimal mode - no service creation)...")
        
        # Get OS information from config if available
        os_type = getattr(self.config, 'os_type', 'ubuntu')
        os_info = getattr(self.config, 'os_info', {'user': 'ubuntu'})
        default_user = os_info.get('user', 'ubuntu')
        
        script = f'''
set -e
echo "Configuring Node.js dependencies only (custom application mode)..."

# Install dependencies if package.json exists
if [ -f "/opt/nodejs-app/package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd /opt/nodejs-app && sudo -u {default_user} npm install --production 2>&1 | tee /tmp/npm-install.log
    echo "✅ Dependencies installed"
else
    echo "ℹ️  No package.json found, skipping dependency installation"
fi

# Create log directory
sudo mkdir -p /var/log/nodejs-app
sudo chown {default_user}:{default_user} /var/log/nodejs-app

# Set proper permissions
sudo chown -R {default_user}:{default_user} /opt/nodejs-app

echo "✅ Node.js minimal configuration completed"
echo "ℹ️  Skipping systemd service creation - application will handle its own startup"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        print(output)
        return success
