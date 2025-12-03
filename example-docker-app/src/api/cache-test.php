<?php
// Redis Cache Test Endpoint
header('Content-Type: application/json');

require_once '../config/redis.php';

$response = [
    'status' => 'success',
    'operations' => []
];

try {
    $redis = getRedisConnection();
    
    if (!$redis) {
        throw new Exception('Failed to connect to Redis');
    }
    
    // Test SET operation
    $key = 'test_key_' . time();
    $value = 'Hello from Docker!';
    $redis->set($key, $value, 60); // Expire in 60 seconds
    $response['operations']['set'] = [
        'success' => true,
        'key' => $key,
        'value' => $value
    ];
    
    // Test GET operation
    $retrieved = $redis->get($key);
    $response['operations']['get'] = [
        'success' => ($retrieved === $value),
        'key' => $key,
        'value' => $retrieved
    ];
    
    // Test INCREMENT operation
    $counterKey = 'counter';
    $counter = $redis->incr($counterKey);
    $response['operations']['incr'] = [
        'success' => true,
        'key' => $counterKey,
        'value' => $counter
    ];
    
    // Test DELETE operation
    $deleted = $redis->del($key);
    $response['operations']['del'] = [
        'success' => ($deleted > 0),
        'key' => $key
    ];
    
    // Get Redis info
    $info = $redis->info();
    $response['redis_info'] = [
        'version' => $info['redis_version'],
        'uptime_days' => round($info['uptime_in_seconds'] / 86400, 2),
        'connected_clients' => $info['connected_clients'],
        'used_memory_human' => $info['used_memory_human']
    ];
    
} catch (Exception $e) {
    $response['status'] = 'error';
    $response['error'] = $e->getMessage();
}

echo json_encode($response, JSON_PRETTY_PRINT);
