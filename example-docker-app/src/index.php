<?php
// Docker LAMP Stack Demo Application
require_once 'config/database.php';
require_once 'config/redis.php';

$pageTitle = "Docker LAMP Stack Demo";
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $pageTitle; ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .status.success {
            background: #10b981;
            color: white;
        }
        .status.error {
            background: #ef4444;
            color: white;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .info-row:last-child {
            border-bottom: none;
        }
        .info-label {
            font-weight: 600;
            color: #666;
        }
        .info-value {
            color: #333;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5568d3;
        }
        .actions {
            text-align: center;
            margin-top: 20px;
        }
        .docker-icon {
            font-size: 24px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐳 <?php echo $pageTitle; ?></h1>
            <p>Multi-container LAMP stack with Docker Compose</p>
        </div>

        <div class="grid">
            <!-- PHP Info Card -->
            <div class="card">
                <h2>🐘 PHP Information</h2>
                <div class="info-row">
                    <span class="info-label">PHP Version:</span>
                    <span class="info-value"><?php echo phpversion(); ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Server:</span>
                    <span class="info-value"><?php echo $_SERVER['SERVER_SOFTWARE']; ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Document Root:</span>
                    <span class="info-value"><?php echo $_SERVER['DOCUMENT_ROOT']; ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Environment:</span>
                    <span class="info-value"><?php echo getenv('APP_ENV') ?: 'production'; ?></span>
                </div>
            </div>

            <!-- Database Status Card -->
            <div class="card">
                <h2>🗄️ MySQL Database</h2>
                <?php
                $dbStatus = testDatabaseConnection();
                ?>
                <div class="info-row">
                    <span class="info-label">Status:</span>
                    <span class="status <?php echo $dbStatus['connected'] ? 'success' : 'error'; ?>">
                        <?php echo $dbStatus['connected'] ? 'Connected' : 'Disconnected'; ?>
                    </span>
                </div>
                <?php if ($dbStatus['connected']): ?>
                <div class="info-row">
                    <span class="info-label">Host:</span>
                    <span class="info-value"><?php echo getenv('DB_HOST') ?: 'db'; ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Database:</span>
                    <span class="info-value"><?php echo getenv('DB_NAME') ?: 'docker_app'; ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Version:</span>
                    <span class="info-value"><?php echo $dbStatus['version']; ?></span>
                </div>
                <?php else: ?>
                <div class="info-row">
                    <span class="info-label">Error:</span>
                    <span class="info-value"><?php echo $dbStatus['error']; ?></span>
                </div>
                <?php endif; ?>
            </div>

            <!-- Redis Status Card -->
            <div class="card">
                <h2>⚡ Redis Cache</h2>
                <?php
                $redisStatus = testRedisConnection();
                ?>
                <div class="info-row">
                    <span class="info-label">Status:</span>
                    <span class="status <?php echo $redisStatus['connected'] ? 'success' : 'error'; ?>">
                        <?php echo $redisStatus['connected'] ? 'Connected' : 'Disconnected'; ?>
                    </span>
                </div>
                <?php if ($redisStatus['connected']): ?>
                <div class="info-row">
                    <span class="info-label">Host:</span>
                    <span class="info-value"><?php echo getenv('REDIS_HOST') ?: 'redis'; ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Port:</span>
                    <span class="info-value"><?php echo getenv('REDIS_PORT') ?: '6379'; ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Version:</span>
                    <span class="info-value"><?php echo $redisStatus['version']; ?></span>
                </div>
                <?php else: ?>
                <div class="info-row">
                    <span class="info-label">Error:</span>
                    <span class="info-value"><?php echo $redisStatus['error']; ?></span>
                </div>
                <?php endif; ?>
            </div>

            <!-- Docker Info Card -->
            <div class="card">
                <h2>🐳 Docker Environment</h2>
                <div class="info-row">
                    <span class="info-label">Container:</span>
                    <span class="info-value"><?php echo gethostname(); ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">IP Address:</span>
                    <span class="info-value"><?php echo $_SERVER['SERVER_ADDR']; ?></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Deployment:</span>
                    <span class="info-value">Docker Compose</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Services:</span>
                    <span class="info-value">Web, DB, Redis, phpMyAdmin</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🚀 Quick Actions</h2>
            <div class="actions">
                <a href="/api/test.php" class="btn">Test API</a>
                <a href="http://<?php echo $_SERVER['HTTP_HOST']; ?>:8080" class="btn" target="_blank">phpMyAdmin</a>
                <a href="/api/cache-test.php" class="btn">Test Cache</a>
                <a href="https://github.com/yourusername/lamp-stack-lightsail" class="btn" target="_blank">GitHub Repo</a>
            </div>
        </div>
    </div>
</body>
</html>
