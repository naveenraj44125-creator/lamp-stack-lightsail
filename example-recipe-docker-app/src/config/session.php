<?php
// Session management with Redis

function startSession() {
    if (session_status() === PHP_SESSION_NONE) {
        // Use Redis for session storage if available
        $redisHost = getenv('REDIS_HOST') ?: 'redis';
        $redisPort = getenv('REDIS_PORT') ?: 6379;
        
        try {
            ini_set('session.save_handler', 'redis');
            ini_set('session.save_path', "tcp://{$redisHost}:{$redisPort}");
            session_start();
        } catch (Exception $e) {
            // Fallback to file-based sessions
            session_start();
        }
    }
}

function isAdminLoggedIn() {
    startSession();
    return isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;
}

function requireAdmin() {
    if (!isAdminLoggedIn()) {
        header('HTTP/1.1 401 Unauthorized');
        echo json_encode(['error' => 'Authentication required']);
        exit;
    }
}

function loginAdmin($username) {
    startSession();
    $_SESSION['admin_logged_in'] = true;
    $_SESSION['admin_username'] = $username;
    $_SESSION['login_time'] = time();
}

function logoutAdmin() {
    startSession();
    session_destroy();
}
