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
                    echo "<h2>Hello Welcome!</h2>";
                    echo "<p>This is a simple LAMP stack application running on PHP.</p>";
                    echo "<p>Current date and time: " . date('Y-m-d H:i:s') . "</p>";
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
        </main>
        
        <footer>
            <p>&copy; 2025 LAMP Stack Demo Application</p>
        </footer>
    </div>
</body>
</html>
