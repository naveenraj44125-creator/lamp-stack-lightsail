<?php
/**
 * Database Configuration for LAMP Stack Application
 * 
 * This file contains the database connection settings.
 * Modify these settings according to your MySQL/MariaDB setup.
 */

// Database configuration
define('DB_HOST', 'localhost');
define('DB_NAME', 'lamp_app');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_CHARSET', 'utf8mb4');

/**
 * Create database connection
 * 
 * @return PDO|null Database connection object or null on failure
 */
function getDatabaseConnection() {
    try {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
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
    if (testDatabaseConnection()) {
        return "✅ Database connection successful";
    } else {
        return "❌ Database connection failed - Please check your MySQL/MariaDB setup";
    }
}
?>
