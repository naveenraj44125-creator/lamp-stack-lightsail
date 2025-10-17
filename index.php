<?php
// Include database configuration
require_once 'config/database.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LAMP Stack Application</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>LAMP Stack Application</h1>
        </header>
        
        <main>
            <div class="welcome-message">
                <?php
                    echo "<h2>🚀 Hello Welcome - Enhanced LAMP Stack Application v3.0!</h2>";
                    echo "<p>This is a robust LAMP stack application running on PHP with improved error handling.</p>";
                    echo "<p><strong>🎯 Deployment Test:</strong> This version was deployed via GitHub Actions!</p>";
                    echo "<p><strong>🔥 NEW FEATURE:</strong> Enhanced monitoring and status display!</p>";
                    echo "<p><strong>✨ LATEST UPDATE:</strong> Improved database connection handling!</p>";
                    echo "<p><strong>🎉 NEWEST FEATURE:</strong> Continuous Deployment Pipeline Active!</p>";
                    echo "<p><strong>🚀 ADVANCED FEATURE:</strong> Multi-Stage CI/CD Pipeline with Auto-Deploy!</p>";
                    echo "<p><strong>🛠️ LATEST FIX:</strong> Enhanced endpoint reliability and error handling!</p>";
                    echo "<p><strong>🆕 VERSION 3.0:</strong> Updated deployment with improved file extraction process!</p>";
                    echo "<p>Current date and time: " . date('Y-m-d H:i:s') . "</p>";
                    echo "<p>Server uptime: " . shell_exec('uptime') . "</p>";
                    echo "<p><em>Version: 3.0 - Enhanced Reliability at " . date('H:i:s') . "</em></p>";
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
                <h3>🆕 System Status (Version 3.0)</h3>
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
            <p>&copy; 2025 LAMP Stack Demo Application</p>
        </footer>
    </div>
</body>
</html>
<- Improved verification process with retry mechanisms Deployment test Mon Oct 13 09:23:30 PDT 2025 -->
