"""Database configurator for MySQL and PostgreSQL"""
from .base_configurator import BaseConfigurator
from os_detector import OSDetector

class DatabaseConfigurator(BaseConfigurator):
    """Handles database configuration (MySQL, PostgreSQL, RDS)"""
    
    def configure(self) -> bool:
        """Configure database connections based on enabled dependencies"""
        print("🔧 Configuring database connections...")
        
        # Get OS information from client
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        os_info = getattr(self.client, 'os_info', {'package_manager': 'apt', 'user': 'ubuntu'})
        
        # Get OS-specific information
        # Detect web server from config to use correct user for file ownership
        nginx_enabled = self.config.get('dependencies.nginx.enabled', False)
        web_server = 'nginx' if nginx_enabled else 'apache'
        self.user_info = OSDetector.get_user_info(os_type, web_server)
        self.pkg_commands = OSDetector.get_package_manager_commands(os_info['package_manager'])
        self.svc_commands = OSDetector.get_service_commands(os_info.get('service_manager', 'systemd'))
        
        # Check if MySQL is enabled in config
        mysql_enabled = self.config.get('dependencies.mysql.enabled', False)
        mysql_external = self.config.get('dependencies.mysql.external', False)
        
        if mysql_enabled:
            if mysql_external:
                return self._configure_rds_connection()
            else:
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
{self.pkg_commands['update']}
mysql_client_pkg=$(if [ "{self.pkg_commands['install']}" = *"apt-get"* ]; then echo "mysql-client"; else echo "mysql"; fi)
{self.pkg_commands['install']} $mysql_client_pkg

# Create fallback environment file
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

    sudo chown {self.user_info['web_user']}:{self.user_info['web_group']} /var/www/html/.env
    sudo chmod 644 /var/www/html/.env
    echo "✅ Fallback environment file created"
fi

echo "✅ RDS configuration completed (with local fallback)"
'''
        
        success, output = self.client.run_command(script, timeout=120)
        
        if not success:
            print("⚠️  RDS configuration failed, falling back to local MySQL")
            return self._configure_local_mysql()
        
        return success
    
    def _configure_local_mysql(self) -> bool:
        """Configure local MySQL database using safe mode approach
        
        Uses safe mode (--skip-grant-tables) for reliable user/database creation
        that works even when MySQL has authentication issues.
        """
        print("🔧 Configuring local MySQL database with safe mode approach...")
        
        # Get MySQL configuration from config
        mysql_config = self.config.get('dependencies.mysql.config', {})
        root_password = mysql_config.get('root_password', 'root123')
        create_database = mysql_config.get('create_database', mysql_config.get('database_name', 'app_db'))
        create_user = mysql_config.get('create_user', 'app_user')
        user_password = mysql_config.get('user_password', 'app_password_123')
        
        # Determine app directory based on deployment type
        nodejs_enabled = self.config.get('dependencies.nodejs.enabled', False)
        app_dir = '/opt/nodejs-app' if nodejs_enabled else '/var/www/html'
        
        script = f'''
set -e
echo "Setting up local MySQL database with safe mode approach..."

# Detect MySQL service name
if systemctl list-unit-files | grep -q "^mysql.service"; then
    MYSQL_SERVICE="mysql"
elif systemctl list-unit-files | grep -q "^mysqld.service"; then
    MYSQL_SERVICE="mysqld"
elif systemctl list-unit-files | grep -q "^mariadb.service"; then
    MYSQL_SERVICE="mariadb"
else
    echo "⚠️  Could not detect MySQL service name, trying mysql..."
    MYSQL_SERVICE="mysql"
fi

echo "Using MySQL service: $MYSQL_SERVICE"

# Stop MySQL if running
echo "Stopping MySQL..."
sudo systemctl stop $MYSQL_SERVICE 2>/dev/null || true
sleep 2

# Ensure MySQL run directory exists with correct permissions
sudo mkdir -p /var/run/mysqld
sudo chown mysql:mysql /var/run/mysqld

# Start MySQL in safe mode (skip grant tables)
echo "Starting MySQL in safe mode..."
sudo mysqld_safe --skip-grant-tables &
sleep 5

# Wait for MySQL to be ready
for i in 1 2 3 4 5 6 7 8 9 10; do
    if sudo mysqladmin ping 2>/dev/null; then
        echo "✅ MySQL is ready"
        break
    fi
    echo "Waiting for MySQL to start... ($i/10)"
    sleep 2
done

# Configure MySQL - reset root password and create user/database
echo "Configuring MySQL users and database..."
mysql -u root << 'MYSQL_CONFIG'
FLUSH PRIVILEGES;
-- Reset root password
ALTER USER 'root'@'localhost' IDENTIFIED BY '{root_password}';
-- Create application database
CREATE DATABASE IF NOT EXISTS `{create_database}`;
-- Drop user if exists (clean slate)
DROP USER IF EXISTS '{create_user}'@'localhost';
-- Create application user
CREATE USER '{create_user}'@'localhost' IDENTIFIED BY '{user_password}';
-- Grant privileges
GRANT ALL PRIVILEGES ON `{create_database}`.* TO '{create_user}'@'localhost';
FLUSH PRIVILEGES;
SELECT 'MySQL configured successfully' as status;
MYSQL_CONFIG

# Stop safe mode MySQL
echo "Stopping safe mode MySQL..."
sudo pkill -9 -f mysqld_safe 2>/dev/null || true
sleep 1
sudo pkill -9 -f mysqld 2>/dev/null || true
sleep 3

# Verify all MySQL processes are stopped
if pgrep -f mysqld > /dev/null; then
    echo "⚠️  MySQL processes still running, force killing..."
    sudo killall -9 mysqld 2>/dev/null || true
    sudo killall -9 mysqld_safe 2>/dev/null || true
    sleep 3
fi

# Start MySQL normally
echo "Starting MySQL normally..."
sudo systemctl start $MYSQL_SERVICE
sleep 3

# Verify MySQL is running
if sudo systemctl is-active --quiet $MYSQL_SERVICE; then
    echo "✅ MySQL service is running"
else
    echo "⚠️  MySQL service status unclear, attempting restart..."
    sudo systemctl restart $MYSQL_SERVICE || true
    sleep 2
fi

# Test the connection with the new user
echo "🔍 Testing MySQL connection with application user..."
if mysql -u {create_user} -p'{user_password}' -e "USE {create_database}; SELECT 'Connection successful' as status;" 2>&1; then
    echo "✅ MySQL user '{create_user}' can connect to database '{create_database}'"
else
    echo "⚠️  Connection test with app user failed, trying root..."
    mysql -u root -p'{root_password}' -e "USE {create_database}; SELECT 'Root connection successful' as status;" 2>&1 || echo "⚠️  Root connection also failed"
fi

# Create test table with sample data
echo "Creating test table..."
mysql -u {create_user} -p'{user_password}' {create_database} -e "
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT IGNORE INTO test_table (id, name) VALUES 
    (1, 'Test Entry'),
    (2, 'Sample Data'),
    (3, 'Database Working');
" 2>/dev/null && echo "✅ Test table created with sample data" || echo "⚠️  Test table creation skipped"

# Create environment file in the appropriate directory
echo "Creating .env file in {app_dir}..."
sudo mkdir -p {app_dir}
sudo tee {app_dir}/.env > /dev/null << 'EOF'
# Database Configuration - Local MySQL
DB_EXTERNAL=false
DB_TYPE=MYSQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME={create_database}
DB_USERNAME={create_user}
DB_PASSWORD={user_password}
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

# Set proper permissions
sudo chown {self.user_info['web_user']}:{self.user_info['web_group']} {app_dir}/.env
sudo chmod 644 {app_dir}/.env

# Also create in /var/www/html for PHP apps that might need it
if [ "{app_dir}" != "/var/www/html" ]; then
    sudo mkdir -p /var/www/html
    sudo cp {app_dir}/.env /var/www/html/.env 2>/dev/null || true
    sudo chown {self.user_info['web_user']}:{self.user_info['web_group']} /var/www/html/.env 2>/dev/null || true
fi

echo "✅ Local MySQL database setup completed with safe mode approach"
'''
        
        success, output = self.client.run_command_with_live_output(script, timeout=420)
        return success
    
    def _configure_local_postgresql(self) -> bool:
        """Configure local PostgreSQL database"""
        print("🔧 Configuring local PostgreSQL database...")
        
        script = '''
set -e
echo "Setting up local PostgreSQL database..."

# Install PostgreSQL
{self.pkg_commands['update']}
pg_packages=$(if [ "{self.pkg_commands['install']}" = *"apt-get"* ]; then echo "postgresql postgresql-contrib"; else echo "postgresql-server postgresql-contrib"; fi)
{self.pkg_commands['install']} $pg_packages

# Start and enable PostgreSQL
pg_service=$(if [ "{self.pkg_commands['install']}" = *"apt-get"* ]; then echo "postgresql"; else echo "postgresql"; fi)
{self.svc_commands['start']} $pg_service
{self.svc_commands['enable']} $pg_service

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
sudo chown {self.user_info['web_user']}:{self.user_info['web_group']} /var/www/html/.env
sudo chmod 644 /var/www/html/.env

echo "✅ Local PostgreSQL database setup completed"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success
