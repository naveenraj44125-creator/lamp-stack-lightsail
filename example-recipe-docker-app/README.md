# 🍳 Recipe Manager - Docker + S3 Bucket Example

A complete recipe management application demonstrating Docker deployment with AWS Lightsail bucket integration.

## 🎯 Features

- **Recipe Management**: Create, view, edit, and delete recipes
- **Image Upload**: Upload recipe images to AWS Lightsail bucket
- **Admin Panel**: Manage recipes with image associations
- **Public Gallery**: Browse recipes with images from S3
- **Docker Deployment**: Multi-container architecture
- **S3 Integration**: Store images in Lightsail bucket, metadata in MySQL

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Docker Compose Stack                  │
├─────────────────────────────────────────────────┤
│  Web (Apache+PHP) → MySQL → Redis → S3 Bucket  │
└─────────────────────────────────────────────────┘
```

### Services
- **web**: Apache + PHP 8.1 application server
- **db**: MySQL 8.0 for recipe metadata
- **redis**: Session storage and caching
- **S3 Bucket**: AWS Lightsail bucket for recipe images

## 🚀 Quick Start

### Local Development

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your AWS credentials
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Access the app
open http://localhost
```

### Deploy to AWS Lightsail

1. **Create Lightsail Bucket** (if not exists):
   ```bash
   aws lightsail create-bucket --bucket-name recipe-images-bucket --bundle-id small_1_0
   ```

2. **Configure** `deployment-recipe-docker.config.yml`:
   ```yaml
   environment_variables:
     BUCKET_NAME: "recipe-images-bucket"
     AWS_REGION: "us-east-1"
   ```

3. **Push to GitHub** - Automatic deployment

## 📁 Project Structure

```
example-recipe-docker-app/
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Web server container
├── src/
│   ├── index.php              # Public recipe gallery
│   ├── admin/
│   │   ├── index.php          # Admin dashboard
│   │   ├── upload.php         # Recipe upload form
│   │   └── manage.php         # Recipe management
│   ├── api/
│   │   ├── recipes.php        # Recipe CRUD API
│   │   └── upload-image.php   # Image upload handler
│   ├── config/
│   │   ├── database.php       # Database connection
│   │   ├── bucket.php         # S3 bucket helper
│   │   └── session.php        # Session management
│   └── assets/
│       ├── css/style.css      # Styling
│       └── js/app.js          # Frontend logic
└── sql/
    └── init.sql               # Database schema
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DB_HOST=db
DB_NAME=recipe_db
DB_USER=recipe_user
DB_PASSWORD=secure_password

# AWS Lightsail Bucket
BUCKET_NAME=recipe-images-bucket
AWS_REGION=us-east-1

# Application
APP_ENV=production
UPLOAD_MAX_SIZE=5242880  # 5MB
```

### IAM Permissions

The Lightsail instance needs these permissions:
- `lightsail:GetBuckets`
- `lightsail:GetBucketAccessKeys`
- `s3:PutObject`
- `s3:GetObject`
- `s3:DeleteObject`

## 📸 How It Works

### 1. Admin Uploads Recipe
```
Admin Panel → Upload Form → PHP Handler → S3 Bucket
                                ↓
                          MySQL (metadata)
```

### 2. Public Views Recipe
```
Gallery Page → MySQL (get recipe) → S3 URL → Display Image
```

### 3. Image Storage
- **Images**: Stored in S3 bucket (`s3://recipe-images-bucket/recipes/`)
- **Metadata**: Stored in MySQL (recipe name, description, image key)
- **URLs**: Generated presigned URLs for secure access

## 🎨 Features Demonstrated

### Recipe Management
- Create recipes with name, description, ingredients, instructions
- Upload recipe images (JPG, PNG, GIF)
- Associate images with recipes
- Edit and delete recipes
- Search and filter recipes

### S3 Bucket Integration
- Direct upload to Lightsail bucket
- Automatic image optimization
- Presigned URL generation
- Secure image access
- Bucket lifecycle management

### Docker Benefits
- Isolated environment
- Easy scaling
- Consistent deployments
- Quick rollbacks
- Development/production parity

## 🔍 API Endpoints

### Public API
- `GET /api/recipes.php` - List all recipes
- `GET /api/recipes.php?id=1` - Get single recipe

### Admin API (requires auth)
- `POST /api/recipes.php` - Create recipe
- `PUT /api/recipes.php?id=1` - Update recipe
- `DELETE /api/recipes.php?id=1` - Delete recipe
- `POST /api/upload-image.php` - Upload image to S3

## 🧪 Testing

### Test Locally
```bash
# Start services
docker-compose up -d

# Test database connection
docker-compose exec web php -r "require 'config/database.php'; echo testDatabaseConnection()['connected'] ? 'DB OK' : 'DB Failed';"

# Test S3 connection
docker-compose exec web php -r "require 'config/bucket.php'; echo testBucketConnection() ? 'S3 OK' : 'S3 Failed';"

# Upload test recipe
curl -X POST http://localhost/api/recipes.php \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Recipe","description":"Test"}'
```

### Test Deployment
```bash
# SSH to instance
ssh ubuntu@your-instance-ip

# Check containers
sudo docker-compose ps

# View logs
sudo docker-compose logs web

# Test endpoint
curl http://localhost/api/recipes.php
```

## 🚨 Troubleshooting

### Images Not Uploading
```bash
# Check bucket permissions
aws lightsail get-bucket-access-keys --bucket-name recipe-images-bucket

# Verify environment variables
docker-compose exec web env | grep BUCKET
```

### Database Connection Failed
```bash
# Check MySQL container
docker-compose logs db

# Test connection
docker-compose exec db mysql -u recipe_user -p
```

### Container Won't Start
```bash
# View detailed logs
docker-compose logs --tail=100 web

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

## 📚 Learn More

- [AWS Lightsail Buckets](https://docs.aws.amazon.com/lightsail/latest/userguide/buckets-in-amazon-lightsail.html)
- [Docker Compose](https://docs.docker.com/compose/)
- [PHP S3 SDK](https://docs.aws.amazon.com/sdk-for-php/)
- [BUCKET-DEPLOYMENT-SUMMARY.md](../BUCKET-DEPLOYMENT-SUMMARY.md)

## 🎓 Next Steps

1. **Customize** recipes schema for your needs
2. **Add authentication** for admin panel
3. **Implement search** functionality
4. **Add categories** and tags
5. **Deploy** to production

---

**Demo**: Upload your first recipe at `/admin/upload.php`
