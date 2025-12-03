<?php
// API Test Endpoint
header('Content-Type: application/json');

require_once '../config/database.php';
require_once '../config/redis.php';

$response = [
    'status' => 'success',
    'timestamp' => date('Y-m-d H:i:s'),
    'services' => []
];

// Test Database
$dbStatus = testDatabaseConnection();
$response['services']['database'] = [
    'name' => 'MySQL',
    'status' => $dbStatus['connected'] ? 'connected' : 'disconnected',
    'version' => $dbStatus['version'],
    'error' => $dbStatus['error']
];

// Test Redis
$redisStatus = testRedisConnection();
$response['services']['cache'] = [
    'name' => 'Redis',
    'status' => $redisStatus['connected'] ? 'connected' : 'disconnected',
    'version' => $redisStatus['version'],
    'error' => $redisStatus['error']
];

// PHP Info
$response['services']['php'] = [
    'version' => phpversion(),
    'extensions' => get_loaded_extensions()
];

// Environment
$response['environment'] = [
    'app_env' => getenv('APP_ENV') ?: 'production',
    'hostname' => gethostname(),
    'server_addr' => $_SERVER['SERVER_ADDR']
];

echo json_encode($response, JSON_PRETTY_PRINT);
