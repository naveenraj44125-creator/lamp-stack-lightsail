<?php
/**
 * Database Configuration for Generic Application
 * 
 * This file contains the database connection settings.
 * Supports both local database and external RDS configurations.
 * RDS configuration is loaded from environment variables.
 */

// Load environment variables from .env file if it exists
if (file_exists(__DIR__ . '/../.env')) {
    $lines = file(__DIR__ . '/../.env', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0) {
            continue; // Skip comments
        }
        if (strpos($line, '=') !== false) {
            list($name, $value) = explode('=', $line, 2);
            $_ENV[trim($name)] = trim($value, '"\'');
        }
    }
}

// Also check for environment file in /opt/app/database.env
if (file_exists('/opt/app/database.env')) {
    $lines = file('/opt/app/database.env', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0) {
            continue; // Skip comments
        }
        if (strpos($line, '=') !== false) {
            list($name, $value) = explode('=', $line, 2);
            $_ENV[trim($name)] = trim($value, '"\'');
        }
    }
}

// Check if external RDS database is configured
$isExternalDB = isset($_ENV['DB_EXTERNAL']) && $_ENV['DB_EXTERNAL'] === 'true';

if ($isExternalDB) {
    // External RDS Database configuration from environment variables
    define('DB_HOST', $_ENV['DB_HOST'] ?? 'localhost');
    define('DB_NAME', $_ENV['DB_NAME'] ?? 'app_db');
    define('DB_USER', $_ENV['DB_USERNAME'] ?? 'root');
    define('DB_PASS', $_ENV['DB_PASSWORD'] ?? '');
    define('DB_PORT', $_ENV['DB_PORT'] ?? '3306');
    define('DB_TYPE', $_ENV['DB_TYPE'] ?? 'MYSQL');
    define('DB_CHARSET', $_ENV['DB_CHARSET'] ?? 'utf8mb4');
    define('DB_EXTERNAL', true);
} else {
    // Local database configuration (fallback)
    define('DB_HOST', 'localhost');
    define('DB_NAME', 'app_db');  // Changed from 'lamp_app' to match deployment config
    define('DB_USER', 'root');
    define('DB_PASS', 'root123');  // Changed from empty to match deployment config
    define('DB_PORT', '3306');
    define('DB_TYPE', 'MYSQL');
    define('DB_CHARSET', 'utf8mb4');
    define('DB_EXTERNAL', false);
}

/**
 * Create database connection
 * 
 * @return PDO|null Database connection object or null on failure
 */
function getDatabaseConnection() {
    try {
        // Build DSN based on database type
        if (DB_TYPE === 'POSTGRESQL') {
            $dsn = "pgsql:host=" . DB_HOST . ";port=" . DB_PORT . ";dbname=" . DB_NAME;
        } else {
            // Default to MySQL
            $dsn = "mysql:host=" . DB_HOST . ";port=" . DB_PORT . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
        }
        
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];
        
        $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
        return $pdo;
    } catch (PDOException $e) {
        error_log("Database connection failed: " . $e->getMessage());
        return null;
    }
}

/**
 * Test database connection
 * 
 * @return bool True if connection successful, false otherwise
 */
function testDatabaseConnection() {
    $connection = getDatabaseConnection();
    if ($connection) {
        return true;
    }
    return false;
}

/**
 * Get database status for display
 * 
 * @return string Database status message
 */
function getDatabaseStatus() {
    try {
        if (testDatabaseConnection()) {
            $connection = getDatabaseConnection();
            if ($connection) {
                // Get database version based on type
                if (DB_TYPE === 'POSTGRESQL') {
                    $stmt = $connection->query('SELECT version() as version');
                } else {
                    $stmt = $connection->query('SELECT VERSION() as version');
                }
                $result = $stmt->fetch();
                
                $dbType = DB_EXTERNAL ? 'RDS ' . DB_TYPE : 'Local ' . DB_TYPE;
                return "✅ Connected to " . $dbType . " - " . $result['version'];
            }
        }
    } catch (Exception $e) {
        error_log("Database status check failed: " . $e->getMessage());
    }
    
    return "⚠️ Database connection unavailable (application still functional)";
}

/**
 * Get database configuration information
 * 
 * @return array Database configuration details
 */
function getDatabaseConfig() {
    return [
        'type' => DB_TYPE,
        'host' => DB_HOST,
        'port' => DB_PORT,
        'database' => DB_NAME,
        'username' => DB_USER,
        'external' => DB_EXTERNAL,
        'charset' => DB_CHARSET ?? 'N/A'
    ];
}

/**
 * Get server information
 * 
 * @return array Server information
 */
function getServerInfo() {
    return [
        'php_version' => phpversion(),
        'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
        'document_root' => $_SERVER['DOCUMENT_ROOT'] ?? 'Unknown',
        'server_name' => $_SERVER['SERVER_NAME'] ?? 'localhost',
        'request_time' => date('Y-m-d H:i:s', $_SERVER['REQUEST_TIME'] ?? time())
    ];
}
?>
