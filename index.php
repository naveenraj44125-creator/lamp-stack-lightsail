<?php
// Include database configuration
require_once 'config/database.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generic Application Deployment System v3.0.0</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Generic Application Deployment System</h1>
        </header>
        
        <main>
            <div class="welcome-message">
                <?php
                    echo "<h2>🚀 Hello Welcome - Generic Deployment System v3.0.0!</h2>";
                    echo "<p>This application is deployed using the new <strong>Generic Deployment System</strong> that works with any application stack!</p>";
                    echo "<p><strong>🎯 NEW ARCHITECTURE:</strong> Fully configurable dependency system - no more LAMP-only limitations!</p>";
                    echo "<p><strong>🔥 MAJOR UPGRADE:</strong> Support for Apache, Nginx, MySQL, PostgreSQL, PHP, Python, Node.js, Redis, Docker & more!</p>";
                    echo "<p><strong>✨ SMART DEPLOYMENT:</strong> Automatically installs only the dependencies you enable in config!</p>";
                    echo "<p><strong>🎉 ADAPTIVE TESTING:</strong> Runs PHP, Python, or Node.js tests based on your configuration!</p>";
                    echo "<p><strong>🚀 MODULAR DESIGN:</strong> Each dependency is independent and reusable across different application types!</p>";
                    echo "<p><strong>🛠️ PRODUCTION READY:</strong> Comprehensive error handling, file upload, and service optimization!</p>";
                    echo "<p><strong>🆕 VERSION 3.0.0:</strong> Complete transformation from LAMP-specific to fully generic system!</p>";
                    echo "<p><strong>⚡ CONFIGURATION-DRIVEN:</strong> Simple enabled: true/false flags control entire deployment stack!</p>";
                    echo "<p>Current date and time: " . date('Y-m-d H:i:s') . "</p>";
                    echo "<p>Server uptime: " . shell_exec('uptime') . "</p>";
                    echo "<p><em>Version: 3.0.0 - Generic Deployment System at " . date('H:i:s') . "</em></p>";
                ?>
            </div>
            
            <div class="info-section">
                <h3>Application Information</h3>
                <ul>
                    <li><strong>Server:</strong> Apache</li>
                    <li><strong>Language:</strong> PHP <?php echo phpversion(); ?></li>
                    <li><strong>Database:</strong> MySQL/MariaDB</li>
                    <li><strong>OS:</strong> Linux</li>
                    <li><strong>DB Status:</strong> <?php echo getDatabaseStatus(); ?></li>
                </ul>
            </div>
            
            <div class="info-section">
                <h3>🆕 System Status (Version 3.0.0)</h3>
                <ul>
                    <li><strong>Memory Usage:</strong> <?php echo round(memory_get_usage(true)/1024/1024, 2) . ' MB'; ?></li>
                    <li><strong>Peak Memory:</strong> <?php echo round(memory_get_peak_usage(true)/1024/1024, 2) . ' MB'; ?></li>
                    <li><strong>Deployment Status:</strong> ✅ Successfully deployed via GitHub Actions</li>
                    <li><strong>Last Updated:</strong> <?php echo date('Y-m-d H:i:s T'); ?></li>
                    <li><strong>Server Load:</strong> <?php echo sys_getloadavg()[0]; ?></li>
                    <li><strong>PHP Extensions:</strong> <?php echo count(get_loaded_extensions()); ?> loaded</li>
                </ul>
            </div>
            
            <div class="info-section">
                <h3>🔧 Health Check</h3>
                <ul>
                    <li><strong>Web Server:</strong> ✅ Apache is running</li>
                    <li><strong>PHP Status:</strong> ✅ PHP <?php echo phpversion(); ?> is working</li>
                    <li><strong>Database:</strong> <?php echo getDatabaseStatus(); ?></li>
                    <li><strong>File Permissions:</strong> <?php echo is_writable('.') ? '✅ Writable' : '⚠️ Read-only'; ?></li>
                    <li><strong>Session Support:</strong> <?php echo function_exists('session_start') ? '✅ Available' : '❌ Not available'; ?></li>
                </ul>
            </div>
        </main>
        
        <footer>
            <p>&copy; 2025 Generic Application Deployment System v3.0.0</p>
        </footer>
    </div>
</body>
</html>
<- Improved verification process with retry mechanisms Deployment test Mon Oct 13 09:23:30 PDT 2025 -->
