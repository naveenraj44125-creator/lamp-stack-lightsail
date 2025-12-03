-- Database initialization script
-- This runs automatically when the MySQL container starts for the first time

-- Create sample table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data
INSERT INTO users (username, email) VALUES
    ('admin', 'admin@example.com'),
    ('docker_user', 'docker@example.com'),
    ('test_user', 'test@example.com')
ON DUPLICATE KEY UPDATE username=username;

-- Create sample posts table
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample posts
INSERT INTO posts (user_id, title, content, status) VALUES
    (1, 'Welcome to Docker LAMP Stack', 'This is a sample post demonstrating the Docker deployment.', 'published'),
    (1, 'Getting Started with Docker Compose', 'Learn how to use Docker Compose for multi-container applications.', 'published'),
    (2, 'Database Migrations', 'This post explains database migration strategies.', 'draft')
ON DUPLICATE KEY UPDATE title=title;

-- Create sessions table for PHP sessions (optional)
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(128) NOT NULL PRIMARY KEY,
    data TEXT,
    last_activity INT NOT NULL,
    INDEX idx_last_activity (last_activity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Grant privileges (already handled by MYSQL_USER in docker-compose)
-- GRANT ALL PRIVILEGES ON docker_app.* TO 'app_user'@'%';
-- FLUSH PRIVILEGES;

SELECT 'Database initialization completed successfully!' AS message;
