<?php
// Database configuration and connection helper

function getDatabaseConnection() {
    $host = getenv('DB_HOST') ?: 'db';
    $dbname = getenv('DB_NAME') ?: 'docker_app';
    $user = getenv('DB_USER') ?: 'app_user';
    $password = getenv('DB_PASSWORD') ?: 'secure_password';
    
    try {
        $dsn = "mysql:host=$host;dbname=$dbname;charset=utf8mb4";
        $options = [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ];
        
        $pdo = new PDO($dsn, $user, $password, $options);
        return $pdo;
    } catch (PDOException $e) {
        error_log("Database connection failed: " . $e->getMessage());
        return null;
    }
}

function testDatabaseConnection() {
    try {
        $pdo = getDatabaseConnection();
        if ($pdo) {
            $stmt = $pdo->query('SELECT VERSION() as version');
            $result = $stmt->fetch();
            return [
                'connected' => true,
                'version' => $result['version'],
                'error' => null
            ];
        }
        return [
            'connected' => false,
            'version' => null,
            'error' => 'Failed to establish connection'
        ];
    } catch (Exception $e) {
        return [
            'connected' => false,
            'version' => null,
            'error' => $e->getMessage()
        ];
    }
}
