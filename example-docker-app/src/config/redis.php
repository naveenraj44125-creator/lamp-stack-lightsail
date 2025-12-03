<?php
// Redis configuration and connection helper

function getRedisConnection() {
    $host = getenv('REDIS_HOST') ?: 'redis';
    $port = getenv('REDIS_PORT') ?: 6379;
    
    try {
        $redis = new Redis();
        $redis->connect($host, $port, 2.5); // 2.5 second timeout
        return $redis;
    } catch (Exception $e) {
        error_log("Redis connection failed: " . $e->getMessage());
        return null;
    }
}

function testRedisConnection() {
    try {
        $redis = getRedisConnection();
        if ($redis && $redis->ping()) {
            $info = $redis->info();
            return [
                'connected' => true,
                'version' => $info['redis_version'] ?? 'Unknown',
                'error' => null
            ];
        }
        return [
            'connected' => false,
            'version' => null,
            'error' => 'Failed to ping Redis'
        ];
    } catch (Exception $e) {
        return [
            'connected' => false,
            'version' => null,
            'error' => $e->getMessage()
        ];
    }
}
