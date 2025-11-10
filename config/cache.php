<?php
/**
 * Redis Cache Configuration and Helper
 * 
 * Provides caching functionality using Redis
 */

class RedisCache {
    private static $instance = null;
    private $redis = null;
    private $enabled = false;
    
    private function __construct() {
        // Check if Redis extension is loaded
        if (!extension_loaded('redis')) {
            error_log('Redis extension not loaded');
            return;
        }
        
        try {
            $this->redis = new Redis();
            
            // Try to connect to Redis
            $host = getenv('REDIS_HOST') ?: 'localhost';
            $port = getenv('REDIS_PORT') ?: 6379;
            
            if ($this->redis->connect($host, $port, 2)) {
                $this->enabled = true;
                error_log('Redis connected successfully');
            } else {
                error_log('Redis connection failed');
            }
        } catch (Exception $e) {
            error_log('Redis error: ' . $e->getMessage());
            $this->enabled = false;
        }
    }
    
    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    public function isEnabled() {
        return $this->enabled;
    }
    
    public function get($key) {
        if (!$this->enabled) {
            error_log("Redis get failed: Redis not enabled for key: $key");
            return null;
        }
        
        try {
            $value = $this->redis->get($key);
            if ($value === false) {
                // Check if key exists - false could mean key doesn't exist or actual false value
                if (!$this->redis->exists($key)) {
                    error_log("Redis get: Key '$key' does not exist (cache miss)");
                    return null;
                }
            }
            error_log("Redis get: Successfully retrieved key '$key' (cache hit)");
            return $value;
        } catch (Exception $e) {
            error_log('Redis get error for key ' . $key . ': ' . $e->getMessage());
            return null;
        }
    }
    
    public function set($key, $value, $ttl = 3600) {
        if (!$this->enabled) {
            error_log("Redis set failed: Redis not enabled for key: $key");
            return false;
        }
        
        try {
            $result = $this->redis->setex($key, $ttl, $value);
            if ($result) {
                error_log("Redis set: Successfully cached key '$key' with TTL $ttl seconds");
            } else {
                error_log("Redis set: Failed to cache key '$key'");
            }
            return $result;
        } catch (Exception $e) {
            error_log('Redis set error for key ' . $key . ': ' . $e->getMessage());
            return false;
        }
    }
    
    public function delete($key) {
        if (!$this->enabled) {
            return false;
        }
        
        try {
            return $this->redis->del($key) > 0;
        } catch (Exception $e) {
            error_log('Redis delete error: ' . $e->getMessage());
            return false;
        }
    }
    
    public function flush() {
        if (!$this->enabled) {
            return false;
        }
        
        try {
            return $this->redis->flushDB();
        } catch (Exception $e) {
            error_log('Redis flush error: ' . $e->getMessage());
            return false;
        }
    }
    
    public function getInfo() {
        if (!$this->enabled) {
            return null;
        }
        
        try {
            return $this->redis->info();
        } catch (Exception $e) {
            error_log('Redis info error: ' . $e->getMessage());
            return null;
        }
    }
    
    public function getStats() {
        if (!$this->enabled) {
            return [
                'enabled' => false,
                'connected' => false
            ];
        }
        
        try {
            $info = $this->redis->info();
            return [
                'enabled' => true,
                'connected' => true,
                'version' => $info['redis_version'] ?? 'unknown',
                'uptime' => $info['uptime_in_seconds'] ?? 0,
                'used_memory' => $info['used_memory_human'] ?? 'unknown',
                'connected_clients' => $info['connected_clients'] ?? 0,
                'total_commands' => $info['total_commands_processed'] ?? 0,
                'keyspace_hits' => $info['keyspace_hits'] ?? 0,
                'keyspace_misses' => $info['keyspace_misses'] ?? 0
            ];
        } catch (Exception $e) {
            error_log('Redis stats error: ' . $e->getMessage());
            return [
                'enabled' => true,
                'connected' => false,
                'error' => $e->getMessage()
            ];
        }
    }
}

// Helper functions for easy access
function cache_get($key) {
    return RedisCache::getInstance()->get($key);
}

function cache_set($key, $value, $ttl = 3600) {
    return RedisCache::getInstance()->set($key, $value, $ttl);
}

function cache_delete($key) {
    return RedisCache::getInstance()->delete($key);
}

function cache_flush() {
    return RedisCache::getInstance()->flush();
}

function cache_enabled() {
    return RedisCache::getInstance()->isEnabled();
}

function cache_stats() {
    return RedisCache::getInstance()->getStats();
}
