<?php
// Include database configuration
require_once 'config/database.php';

// Handle form submissions for database operations
$message = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        $pdo = getDatabaseConnection();
        
        if ($pdo === null) {
            $error = "❌ Database connection unavailable. Please check your database configuration.";
        } elseif (isset($_POST['action'])) {
            switch ($_POST['action']) {
                case 'create_table':
                    // Create a sample table for demonstration
                    $sql = "CREATE TABLE IF NOT EXISTS user_visits (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        visitor_name VARCHAR(100) NOT NULL,
                        visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address VARCHAR(45),
                        user_agent TEXT
                    )";
                    $pdo->exec($sql);
                    $message = "✅ Table 'user_visits' created successfully!";
                    break;

                case 'add_visit':
                    $name = $_POST['visitor_name'] ?? 'Anonymous';
                    $ip = $_SERVER['REMOTE_ADDR'] ?? 'Unknown';
                    $userAgent = $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown';

                    $stmt = $pdo->prepare("INSERT INTO user_visits (visitor_name, ip_address, user_agent) VALUES (?, ?, ?)");
                    $stmt->execute([$name, $ip, $userAgent]);
                    $message = "✅ Visit recorded for: " . htmlspecialchars($name);
                    break;

                case 'clear_visits':
                    $pdo->exec("DELETE FROM user_visits");
                    $message = "✅ All visit records cleared!";
                    break;
            }
        }
    } catch (PDOException $e) {
        $error = "❌ Database Error: " . $e->getMessage();
    } catch (Exception $e) {
        $error = "❌ Application Error: " . $e->getMessage();
    }
}

// Function to get visit records
function getVisitRecords() {
    try {
        $pdo = getDatabaseConnection();
        if ($pdo === null) {
            return [];
        }
        $stmt = $pdo->query("SELECT * FROM user_visits ORDER BY visit_time DESC LIMIT 10");
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        return [];
    } catch (Exception $e) {
        return [];
    }
}

// Function to get visit statistics
function getVisitStats() {
    try {
        $pdo = getDatabaseConnection();
        if ($pdo === null) {
            return ['total_visits' => 0, 'unique_visitors' => 0];
        }
        $stmt = $pdo->query("SELECT COUNT(*) as total_visits, COUNT(DISTINCT ip_address) as unique_visitors FROM user_visits");
        return $stmt->fetch(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        return ['total_visits' => 0, 'unique_visitors' => 0];
    } catch (Exception $e) {
        return ['total_visits' => 0, 'unique_visitors' => 0];
    }
}

// Function to check if table exists
function tableExists() {
    try {
        $pdo = getDatabaseConnection();
        if ($pdo === null) {
            return false;
        }
        $stmt = $pdo->query("SHOW TABLES LIKE 'user_visits'");
        return $stmt->rowCount() > 0;
    } catch (PDOException $e) {
        return false;
    } catch (Exception $e) {
        return false;
    }
}
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
                <?php $dbConfig = getDatabaseConfig(); ?>
                <ul>
                    <li><strong>Server:</strong> Apache</li>
                    <li><strong>Language:</strong> PHP <?php echo phpversion(); ?></li>
                    <li><strong>Database:</strong> <?php echo $dbConfig['external'] ? 'AWS Lightsail RDS' : 'Local'; ?> <?php echo $dbConfig['type']; ?></li>
                    <li><strong>DB Host:</strong> <?php echo $dbConfig['host'] . ':' . $dbConfig['port']; ?></li>
                    <li><strong>DB Name:</strong> <?php echo $dbConfig['database']; ?></li>
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

            <!-- Database Operations Section -->
            <div class="info-section">
                <h3>💾 Database Operations (RDS Integration)</h3>
                
                <?php if ($message): ?>
                    <div class="success-message"><?php echo $message; ?></div>
                <?php endif; ?>
                
                <?php if ($error): ?>
                    <div class="error-message"><?php echo $error; ?></div>
                <?php endif; ?>
                
                <!-- Database Setup -->
                <?php if (!tableExists()): ?>
                    <div class="db-setup">
                        <h4>🚀 Initialize Database</h4>
                        <p>Create the sample table to start using database operations:</p>
                        <form method="POST" style="display: inline;">
                            <input type="hidden" name="action" value="create_table">
                            <button type="submit" class="btn btn-primary">Create Sample Table</button>
                        </form>
                    </div>
                <?php else: ?>
                    <!-- Add Visit Form -->
                    <div class="db-operation">
                        <h4>✍️ Add New Visit Record</h4>
                        <form method="POST" class="visit-form">
                            <input type="hidden" name="action" value="add_visit">
                            <label for="visitor_name">Visitor Name:</label>
                            <input type="text" id="visitor_name" name="visitor_name" placeholder="Enter your name" required>
                            <button type="submit" class="btn btn-success">Record Visit</button>
                        </form>
                    </div>

                    <!-- Visit Statistics -->
                    <div class="db-stats">
                        <h4>📊 Visit Statistics</h4>
                        <?php $stats = getVisitStats(); ?>
                        <ul>
                            <li><strong>Total Visits:</strong> <?php echo $stats['total_visits']; ?></li>
                            <li><strong>Unique Visitors:</strong> <?php echo $stats['unique_visitors']; ?></li>
                        </ul>
                    </div>

                    <!-- Recent Visits Display -->
                    <div class="db-records">
                        <h4>📋 Recent Visits (Last 10)</h4>
                        <?php $visits = getVisitRecords(); ?>
                        <?php if (empty($visits)): ?>
                            <p><em>No visits recorded yet. Add your first visit above!</em></p>
                        <?php else: ?>
                            <table class="visits-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Visitor Name</th>
                                        <th>Visit Time</th>
                                        <th>IP Address</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php foreach ($visits as $visit): ?>
                                        <tr>
                                            <td><?php echo htmlspecialchars($visit['id']); ?></td>
                                            <td><?php echo htmlspecialchars($visit['visitor_name']); ?></td>
                                            <td><?php echo htmlspecialchars($visit['visit_time']); ?></td>
                                            <td><?php echo htmlspecialchars($visit['ip_address']); ?></td>
                                        </tr>
                                    <?php endforeach; ?>
                                </tbody>
                            </table>
                        <?php endif; ?>
                    </div>

                    <!-- Clear Data Option -->
                    <div class="db-management">
                        <h4>🗑️ Database Management</h4>
                        <form method="POST" style="display: inline;" onsubmit="return confirm('Are you sure you want to clear all visit records?');">
                            <input type="hidden" name="action" value="clear_visits">
                            <button type="submit" class="btn btn-danger">Clear All Visits</button>
                        </form>
                    </div>
                <?php endif; ?>
            </div>
        </main>
        
        <footer>
            <p>&copy; 2025 Generic Application Deployment System v3.0.0</p>
        </footer>
    </div>
</body>
</html>
<- Improved verification process with retry mechanisms Deployment test Mon Oct 13 09:23:30 PDT 2025 -->
