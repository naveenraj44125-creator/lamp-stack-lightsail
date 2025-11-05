# GitHub Actions Log Example - Enhanced Command Logging

This document shows what you'll see in GitHub Actions logs with the enhanced command logging.

## 🚀 Example: Apache Installation with Detailed Logging

```bash
🔧 Installing apache...
🔧 Executing command on lamp-stack-demo:
   1: set -e
   2: echo "Installing Apache web server..."
   3: sudo apt-get update
   4: sudo apt-get install -y apache2
   5: sudo systemctl enable apache2
   ... (15 more lines)

📡 SSH Command: ssh ubuntu@18.206.107.24
   ✅ Success (exit code: 0)
   📤 Output:
     1: Installing Apache web server...
     2: Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
     3: Get:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease [119 kB]
     4: Get:3 http://security.ubuntu.com/ubuntu jammy-security InRelease [110 kB]
     5: Reading package lists... Done
     6: Reading package lists... Done
     7: Building dependency tree... Done
     8: Reading state information... Done
     9: The following additional packages will be installed:
    10:   apache2-bin apache2-data apache2-utils libapr1 libaprutil1 libaprutil1-dbd-sqlite3
    11: The following NEW packages will be installed:
    12:   apache2 apache2-bin apache2-data apache2-utils libapr1 libaprutil1
    13: 0 upgraded, 6 newly installed, 0 to remove and 0 not upgraded.
    14: Need to get 1,463 kB of archives.
    15: After this operation, 5,463 kB of additional disk space will be used.
    16: Get:1 http://archive.ubuntu.com/ubuntu jammy/main amd64 libapr1 amd64 1.7.0-8build1 [108 kB]
    17: Get:2 http://archive.ubuntu.com/ubuntu jammy/main amd64 libaprutil1 amd64 1.6.1-5ubuntu4.22.04.1 [91.9 kB]
    18: Fetched 1,463 kB in 1s (2,891 kB/s)
    19: Selecting previously unselected package libapr1:amd64.
    20: (Reading database ... 63524 files and directories currently installed.)
    ... (50 more lines of installation output)
    85: Setting up apache2 (2.4.52-1ubuntu4.4) ...
    86: Enabling module rewrite.
    87: Enabling conf security.
    88: Created symlink /etc/systemd/system/multi-user.target.wants/apache2.service → /lib/systemd/system/apache2.service.
    89: ✅ Apache installation completed

✅ apache installed successfully
```

## 🗄️ Example: MySQL Database Setup with Individual Commands

```bash
🔧 Configuring local MySQL database...
🔧 Executing with live output on lamp-stack-demo:
📋 Breaking down script into individual commands:
   📊 Found 8 individual commands to execute

   🔸 Command 1/8:
      1: echo "Setting up local MySQL database..."
      ✅ Command 1 completed successfully
         Setting up local MySQL database...

   🔸 Command 2/8:
      1: if ! command -v mysql &> /dev/null; then
      2:     echo "Installing MySQL server..."
      3:     sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
      4: fi
      ✅ Command 2 completed successfully
         MySQL server is already installed

   🔸 Command 3/8:
      1: sudo systemctl start mysql
      2: sudo systemctl enable mysql
      ✅ Command 3 completed successfully
         Synchronizing state of mysql.service with SysV service script

   🔸 Command 4/8:
      1: echo "Configuring MySQL root user..."
      2: sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';" 2>/dev/null || echo "Root password configuration attempted"
      ✅ Command 4 completed successfully
         Configuring MySQL root user...
         Root password configuration attempted

   🔸 Command 5/8:
      1: mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS app_db;" 2>/dev/null && echo "✅ app_db database created" || echo "❌ Failed to create database"
      ✅ Command 5 completed successfully
         ✅ app_db database created

   🔸 Command 6/8:
      1: mysql -u root -proot123 app_db -e "
      2: CREATE TABLE IF NOT EXISTS test_table (
      3:     id INT AUTO_INCREMENT PRIMARY KEY,
      4:     name VARCHAR(100) NOT NULL,
      5:     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      6: );
      7: INSERT IGNORE INTO test_table (id, name) VALUES 
      8:     (1, 'Test Entry'),
      9:     (2, 'Sample Data'),
     10:     (3, 'Database Working');
     11: " 2>/dev/null && echo "✅ Test table created with sample data" || echo "❌ Failed to create test table"
      ✅ Command 6 completed successfully
         ✅ Test table created with sample data

   🔸 Command 7/8:
      1: mysql -u root -proot123 -e "SELECT COUNT(*) as record_count FROM test_table;" app_db 2>/dev/null && echo "✅ MySQL connection test successful" || echo "❌ MySQL connection test failed"
      ✅ Command 7 completed successfully
         +---------------+
         | record_count  |
         +---------------+
         |             3 |
         +---------------+
         ✅ MySQL connection test successful

   🔸 Command 8/8:
      1: sudo tee /var/www/html/.env > /dev/null << 'EOF'
      2: # Database Configuration - Local MySQL
      3: DB_EXTERNAL=false
      4: DB_TYPE=MYSQL
      5: DB_HOST=localhost
      6: DB_PORT=3306
      7: DB_NAME=app_db
      8: DB_USERNAME=root
      9: DB_PASSWORD=root123
     10: DB_CHARSET=utf8mb4
     11: 
     12: # Application Configuration
     13: APP_ENV=production
     14: APP_DEBUG=false
     15: APP_NAME="Generic Application"
     16: EOF
     17: 
     18: # Set proper permissions
     19: sudo chown www-data:www-data /var/www/html/.env
     20: sudo chmod 644 /var/www/html/.env
     21: 
     22: echo "✅ Local MySQL database setup completed"
      ✅ Command 8 completed successfully
         ✅ Local MySQL database setup completed

✅ Local MySQL database setup completed
```

## 🔧 Example: Service Configuration with Error Handling

```bash
🔧 Configuring Apache for application...
🔧 Executing command on lamp-stack-demo:
   1: set -e
   2: echo "Configuring Apache for application..."
   3: cat > /tmp/app.conf << 'EOF'
   4: <VirtualHost *:80>
   5:     DocumentRoot /var/www/html
   ... (20 more lines)

📡 SSH Command: ssh ubuntu@18.206.107.24
   ✅ Success (exit code: 0)
   📤 Output:
     1: Configuring Apache for application...
     2: Enabling site app.
     3: Enabling module rewrite.
     4: Module rewrite already enabled
     5: Enabling module headers.
     6: Module headers already enabled
     7: ✅ Apache configured for application

✅ Apache configured for application
```

## ❌ Example: Error Handling with Detailed Output

```bash
🔧 Running: mysql -u root -pwrongpassword -e "SELECT 1;"
📡 SSH Command: ssh ubuntu@18.206.107.24
   ❌ Failed (exit code: 1)
   📤 Error Output:
     1: mysql: [Warning] Using a password on the command line interface can be insecure.
     2: ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)
   📤 Standard Output:
     1: 

🔄 Retry attempt 2/3
   ⏳ Waiting 25 seconds before retry...
   🔍 Testing network connectivity to 18.206.107.24...
   ✅ Network connectivity to SSH port successful
```

## 🎯 Key Benefits of Enhanced Logging

### 1. **Individual Command Visibility**
- Each command in a script is shown separately
- You can see exactly which command succeeded or failed
- Line-by-line output for complex commands

### 2. **Detailed Error Information**
- Both stderr and stdout are shown
- Line numbers for easy reference
- Context around errors

### 3. **Progress Tracking**
- Clear indication of which step is executing
- Progress counters (Command 3/8)
- Success/failure status for each step

### 4. **GitHub Actions Optimization**
- Automatic verbose mode when GITHUB_ACTIONS environment is detected
- Formatted output that's easy to read in GitHub Actions logs
- Proper error handling and retry logic

### 5. **Debugging Support**
- SSH command details shown
- Connection status information
- Timeout and retry information

## 🚀 How to Enable Enhanced Logging

### Automatic (GitHub Actions)
The enhanced logging is automatically enabled when running in GitHub Actions environment.

### Manual Activation
```bash
# Set environment variable for verbose logging
export GITHUB_ACTIONS=true

# Run deployment with enhanced logging
python3 workflows/deploy.py --verify --cleanup --monitor
```

### Test Enhanced Logging
```bash
# Test the enhanced logging functionality
python3 workflows/test_detailed_logging.py
```

This enhanced logging makes it much easier to:
- **Debug deployment issues** by seeing exactly which command failed
- **Track progress** during long-running deployments
- **Understand what's happening** on the remote server
- **Troubleshoot problems** with detailed error context