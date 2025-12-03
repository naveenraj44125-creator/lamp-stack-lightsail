# 🐳 Docker Examples Comparison Guide

This guide compares the two Docker deployment examples and helps you choose the right one for your needs.

## 📦 Available Docker Examples

### 1. Basic Docker LAMP Stack (`example-docker-app/`)
**Purpose**: Demonstrate basic Docker deployment with multi-container architecture

**What's Included**:
- Apache + PHP 8.1 web server
- MySQL 8.0 database
- Redis cache
- phpMyAdmin
- Health monitoring dashboard

**Best For**:
- Learning Docker basics
- Testing Docker deployment
- Simple web applications
- Development environments

**Key Features**:
- ✅ Multi-container orchestration
- ✅ Service health checks
- ✅ Persistent data volumes
- ✅ Container networking
- ✅ Development-ready setup

**Deployment Time**:
- First: 15-20 minutes
- Subsequent: 2-3 minutes

---

### 2. Recipe Manager with S3 (`example-recipe-docker-app/`)
**Purpose**: Full-featured application demonstrating Docker + AWS S3 bucket integration

**What's Included**:
- Complete recipe management system
- Admin panel with authentication
- Image upload to AWS Lightsail buckets
- Public recipe gallery
- RESTful API
- Session management with Redis

**Best For**:
- Production applications
- S3 bucket integration examples
- CRUD operations with file uploads
- Real-world application patterns

**Key Features**:
- ✅ AWS S3 bucket integration
- ✅ Image upload/storage
- ✅ Admin authentication
- ✅ RESTful API
- ✅ Responsive UI
- ✅ Database relationships
- ✅ Session management

**Deployment Time**:
- First: 15-20 minutes
- Subsequent: 2-3 minutes

---

## 🔍 Detailed Comparison

| Feature | Basic LAMP | Recipe Manager |
|---------|------------|----------------|
| **Complexity** | Simple | Advanced |
| **Lines of Code** | ~500 | ~1,700 |
| **Database Tables** | 0 | 3 |
| **API Endpoints** | 1 | 3 |
| **File Upload** | ❌ | ✅ S3 Integration |
| **Authentication** | ❌ | ✅ Admin Login |
| **CRUD Operations** | ❌ | ✅ Full CRUD |
| **UI Design** | Basic | Modern/Responsive |
| **Session Management** | ❌ | ✅ Redis Sessions |
| **Image Storage** | ❌ | ✅ S3 Buckets |
| **Sample Data** | ❌ | ✅ 4 Recipes |
| **Production Ready** | No | Yes |

---

## 🎯 Which One Should You Use?

### Choose **Basic LAMP** (`example-docker-app/`) if:
- ✅ You're new to Docker
- ✅ You want to understand Docker basics
- ✅ You need a simple starting point
- ✅ You're testing Docker deployment
- ✅ You don't need file uploads
- ✅ You want minimal code to review

### Choose **Recipe Manager** (`example-recipe-docker-app/`) if:
- ✅ You need S3 bucket integration
- ✅ You want a production-ready example
- ✅ You need file upload functionality
- ✅ You want to see CRUD operations
- ✅ You need authentication examples
- ✅ You want a complete application

---

## 🚀 Quick Start Comparison

### Basic LAMP Stack

```bash
# 1. Local testing
cd example-docker-app
docker-compose up -d

# 2. Access
open http://localhost

# 3. Deploy
# Use deployment-docker.config.yml
```

**What you'll see**:
- Service status dashboard
- PHP/MySQL/Redis connection info
- Container information
- Health check results

---

### Recipe Manager

```bash
# 1. Setup bucket
aws lightsail create-bucket \
  --bucket-name recipe-images-bucket \
  --bundle-id small_1_0

# 2. Local testing
cd example-recipe-docker-app
cp .env.example .env
# Edit .env with your bucket name
docker-compose up -d

# 3. Access
open http://localhost          # Public gallery
open http://localhost/admin/   # Admin panel (admin/admin123)
open http://localhost:8080     # phpMyAdmin

# 4. Deploy
# Use deployment-recipe-docker.config.yml
```

**What you'll see**:
- Recipe gallery with images
- Admin panel for management
- Image upload to S3
- Full CRUD operations

---

## 📊 Architecture Comparison

### Basic LAMP Stack
```
┌─────────────────────────────────┐
│     Docker Compose Stack        │
├─────────────────────────────────┤
│  Web → MySQL → Redis            │
│   ↓                             │
│  Dashboard (Status Display)     │
└─────────────────────────────────┘
```

### Recipe Manager
```
┌──────────────────────────────────────────┐
│        Docker Compose Stack              │
├──────────────────────────────────────────┤
│  Web → MySQL → Redis → S3 Bucket         │
│   ↓      ↓       ↓        ↓              │
│  UI    Data   Sessions  Images           │
│   ↓                                       │
│  Admin Panel + Public Gallery            │
└──────────────────────────────────────────┘
```

---

## 💾 Database Schema Comparison

### Basic LAMP Stack
```sql
-- No tables (just connection testing)
```

### Recipe Manager
```sql
-- recipes table
CREATE TABLE recipes (
    id, name, description, ingredients,
    instructions, prep_time, cook_time,
    servings, difficulty, category,
    image_key, image_url, timestamps
);

-- admin_users table
CREATE TABLE admin_users (
    id, username, password_hash,
    email, timestamps
);

-- recipe_views table (analytics)
CREATE TABLE recipe_views (
    id, recipe_id, viewed_at, ip_address
);
```

---

## 🔧 Configuration Comparison

### Basic LAMP Stack
```yaml
# deployment-docker.config.yml
dependencies:
  docker:
    enabled: true

deployment:
  use_docker: true

environment_variables:
  DB_HOST: db
  DB_NAME: docker_app
  # No S3 configuration needed
```

### Recipe Manager
```yaml
# deployment-recipe-docker.config.yml
dependencies:
  docker:
    enabled: true

deployment:
  use_docker: true

environment_variables:
  DB_HOST: db
  DB_NAME: recipe_db
  BUCKET_NAME: recipe-images-bucket  # S3 bucket
  AWS_REGION: us-east-1
  UPLOAD_MAX_SIZE: "5242880"
```

---

## 📝 Code Examples

### Basic LAMP - Health Check
```php
<?php
// Simple connection test
$dbStatus = testDatabaseConnection();
$redisStatus = testRedisConnection();

echo "Database: " . ($dbStatus['connected'] ? 'OK' : 'Failed');
echo "Redis: " . ($redisStatus['connected'] ? 'OK' : 'Failed');
?>
```

### Recipe Manager - Image Upload
```php
<?php
// Upload image to S3 bucket
$validation = validateImageFile($_FILES['image']);
if ($validation['valid']) {
    $filename = generateUniqueFilename($_FILES['image']['name']);
    $result = uploadImageToBucket($_FILES['image'], $filename);
    
    if ($result['success']) {
        // Save to database
        $stmt->execute([
            $name, $description, $ingredients,
            $result['key'], $result['url']
        ]);
    }
}
?>
```

---

## 🎓 Learning Path

### Beginner Path
1. **Start with Basic LAMP** (`example-docker-app/`)
   - Understand Docker Compose
   - Learn container networking
   - See health checks in action
   - Test locally

2. **Move to Recipe Manager** (`example-recipe-docker-app/`)
   - Add S3 integration
   - Implement CRUD operations
   - Add authentication
   - Deploy to production

### Advanced Path
1. **Start with Recipe Manager** (`example-recipe-docker-app/`)
   - Full application example
   - Production patterns
   - S3 integration
   - Complete deployment

2. **Customize for Your Needs**
   - Modify database schema
   - Add new features
   - Implement your business logic
   - Scale as needed

---

## 🔐 Security Comparison

### Basic LAMP Stack
- ✅ Container isolation
- ✅ Network segmentation
- ✅ Health checks
- ❌ No authentication
- ❌ No file uploads (no upload risks)

### Recipe Manager
- ✅ Container isolation
- ✅ Network segmentation
- ✅ Health checks
- ✅ Admin authentication
- ✅ File validation
- ✅ S3 secure storage
- ✅ Session management
- ✅ SQL injection protection (PDO)
- ✅ XSS protection (htmlspecialchars)

---

## 📈 Performance Comparison

### Resource Usage (Approximate)

| Metric | Basic LAMP | Recipe Manager |
|--------|------------|----------------|
| **Memory** | ~400 MB | ~450 MB |
| **Disk** | ~1 GB | ~1.2 GB |
| **Containers** | 4 | 4 |
| **Startup Time** | 30-40s | 40-50s |
| **Response Time** | <100ms | <150ms |

### Recommended Instance Sizes

**Basic LAMP**:
- Minimum: 512 MB RAM, 1 vCPU
- Recommended: 1 GB RAM, 1 vCPU

**Recipe Manager**:
- Minimum: 1 GB RAM, 1 vCPU
- Recommended: 2 GB RAM, 2 vCPU (for image processing)

---

## 🧪 Testing Locally

### Basic LAMP Stack
```bash
# Start services
docker-compose up -d

# Test endpoints
curl http://localhost/
curl http://localhost/api/test.php

# Check containers
docker-compose ps

# View logs
docker-compose logs web
```

### Recipe Manager
```bash
# Start services
docker-compose up -d

# Test endpoints
curl http://localhost/
curl http://localhost/api/recipes.php
curl http://localhost/admin/

# Upload test recipe (requires form data)
# Use browser: http://localhost/admin/

# Check S3 connection
docker-compose exec web php -r "require 'config/bucket.php'; echo testBucketConnection() ? 'S3 OK' : 'S3 Failed';"
```

---

## 🚨 Common Issues & Solutions

### Basic LAMP Stack

**Issue**: Containers won't start
```bash
# Solution: Check logs
docker-compose logs
docker-compose down
docker-compose up --build -d
```

**Issue**: Can't connect to database
```bash
# Solution: Wait for MySQL to initialize
docker-compose logs db
# Wait for "ready for connections" message
```

### Recipe Manager

**Issue**: Images not uploading to S3
```bash
# Solution: Check bucket permissions
aws lightsail get-bucket-access-keys --bucket-name recipe-images-bucket

# Verify environment variables
docker-compose exec web env | grep BUCKET
```

**Issue**: Admin login not working
```bash
# Solution: Check session storage
docker-compose logs redis
docker-compose restart redis
```

---

## 📚 Next Steps

### After Basic LAMP Stack
1. ✅ Understand Docker concepts
2. ✅ Learn container networking
3. ✅ Practice with docker-compose
4. ➡️ Move to Recipe Manager
5. ➡️ Add S3 integration
6. ➡️ Deploy to production

### After Recipe Manager
1. ✅ Master Docker deployment
2. ✅ Understand S3 integration
3. ✅ Learn CRUD patterns
4. ➡️ Customize for your app
5. ➡️ Add more features
6. ➡️ Scale horizontally

---

## 🎯 Summary

| Aspect | Basic LAMP | Recipe Manager |
|--------|------------|----------------|
| **Purpose** | Learning | Production |
| **Complexity** | Low | Medium |
| **Features** | Minimal | Complete |
| **S3 Integration** | No | Yes |
| **Time to Deploy** | 15-20 min | 15-20 min |
| **Best For** | Beginners | Real Apps |

**Recommendation**: Start with **Basic LAMP** to learn Docker, then use **Recipe Manager** as a template for your production applications.

---

**Need Help?** Check the individual README files:
- [Basic LAMP README](example-docker-app/README.md)
- [Recipe Manager README](example-recipe-docker-app/README.md)
- [Docker Deployment Guide](DOCKER-DEPLOYMENT-GUIDE.md)
