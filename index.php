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
                    echo "<h2>🚀 Hello Welcome - Latest Version!</h2>";
                    echo "<p>This is a simple LAMP stack application running on PHP.</p>";
                    echo "<p><strong>🎯 Deployment Test:</strong> This version was deployed via GitHub Actions!</p>";
                    echo "<p><strong>🔥 NEW FEATURE:</strong> Enhanced monitoring and status display!</p>";
                    echo "<p>Current date and time: " . date('Y-m-d H:i:s') . "</p>";
                    echo "<p>Server uptime: " . shell_exec('uptime') . "</p>";
                    echo "<p><em>Version: 2.5 - Enhanced with server monitoring at " . date('H:i:s') . "</em></p>";
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
                <h3>🆕 System Status (Version 2.5)</h3>
                <ul>
                    <li><strong>Memory Usage:</strong> <?php echo round(memory_get_usage(true)/1024/1024, 2) . ' MB'; ?></li>
                    <li><strong>Peak Memory:</strong> <?php echo round(memory_get_peak_usage(true)/1024/1024, 2) . ' MB'; ?></li>
                    <li><strong>Deployment Status:</strong> ✅ Successfully deployed via GitHub Actions</li>
                    <li><strong>Last Updated:</strong> <?php echo date('Y-m-d H:i:s T'); ?></li>
                </ul>
            </div>
        </main>
        
        <footer>
            <p>&copy; 2025 LAMP Stack Demo Application</p>
        </footer>
    </div>
</body>
</html>
