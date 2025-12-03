# 🚀 Deployment Guide - Recipe Manager Docker

## GitHub Actions Workflow

This example has its own dedicated GitHub Actions workflow: `.github/workflows/deploy-recipe-docker.yml`

## 🎯 Automatic Deployment

The workflow automatically triggers on:

### 1. Push to Main/Master
```bash
git add .
git commit -m "Update recipe app"
git push origin main
```

**Triggers when**:
- Any file in `example-recipe-docker-app/` changes
- `deployment-recipe-docker.config.yml` changes
- The workflow file itself changes

### 2. Pull Request
```bash
git checkout -b feature/new-recipe-feature
# Make changes
git push origin feature/new-recipe-feature
# Create PR on GitHub
```

### 3. Manual Trigger

**Via GitHub UI**:
1. Go to **Actions** tab
2. Select **Deploy Recipe Manager Docker**
3. Click **Run workflow**
4. Optionally override bucket name
5. Click **Run workflow**

**Via GitHub CLI**:
```bash
gh workflow run deploy-recipe-docker.yml
```

## 📋 Pre-Deployment Setup

### 1. Create S3 Bucket

**Required** before first deployment:

```bash
aws lightsail create-bucket \
  --bucket-name recipe-images-bucket \
  --bundle-id small_1_0 \
  --region us-east-1
```

**Verify**:
```bash
aws lightsail get-bucket --bucket-name recipe-images-bucket
```

### 2. Configure Bucket Name

Edit `deployment-recipe-docker.config.yml`:

```yaml
environment_variables:
  BUCKET_NAME: recipe-images-bucket  # Your bucket name
  AWS_REGION: us-east-1
```

### 3. Update Passwords

**Important**: Change default passwords!

```yaml
environment_variables:
  DB_PASSWORD: YOUR_SECURE_PASSWORD_HERE
  DB_ROOT_PASSWORD: YOUR_ROOT_PASSWORD_HERE
```

## 🔍 Monitor Deployment

### View Logs
1. Go to **Actions** tab on GitHub
2. Click on the running workflow
3. Click on **Deploy Recipe Manager to Lightsail**
4. View real-time logs

### Check Deployment Status
```bash
# SSH to instance
ssh ubuntu@your-instance-ip

# Check containers
cd /opt/recipe-app
sudo docker-compose ps

# View logs
sudo docker-compose logs -f web
sudo docker-compose logs -f db

# Test S3 connection
sudo docker-compose exec web php -r "require 'config/bucket.php'; echo testBucketConnection() ? 'S3 OK' : 'S3 Failed';"
```

## ⏱️ Deployment Timeline

| Step | Duration | Description |
|------|----------|-------------|
| **Checkout Code** | 10s | Clone repository |
| **Setup Python** | 20s | Install dependencies |
| **Install Docker** | 5-8 min | First time only |
| **Install AWS CLI** | 1-2 min | For S3 access |
| **Download Images** | 5-10 min | MySQL, Redis, etc. |
| **Build Custom Image** | 3-5 min | Apache + PHP + AWS CLI |
| **Start Containers** | 1-2 min | Launch services |
| **Health Checks** | 1-2 min | Verify deployment |
| **S3 Connection Test** | 30s | Verify bucket access |

**Total**: 15-25 minutes (first deployment), 2-5 minutes (subsequent)

## 🎛️ Workflow Inputs

When manually triggering:

- **environment**: `production` (default), `staging`, `development`
- **bucket_name**: Override bucket name from config (optional)

## 🧪 Post-Deployment Testing

### 1. Access Application
```
Public Gallery: http://your-instance-ip/
Admin Panel: http://your-instance-ip/admin/
phpMyAdmin: http://your-instance-ip:8080
```

### 2. Test Admin Login
- Username: `admin`
- Password: `admin123`

### 3. Upload Test Recipe
1. Go to Admin Panel
2. Click "Add New Recipe"
3. Fill in recipe details
4. Upload an image (JPG, PNG, GIF)
5. Submit

### 4. Verify S3 Upload
```bash
# Check bucket contents
aws lightsail get-bucket-access-keys --bucket-name recipe-images-bucket

# List uploaded images
aws s3 ls s3://recipe-images-bucket/recipes/
```

### 5. Test API
```bash
# Get all recipes
curl http://your-instance-ip/api/recipes.php

# Get specific recipe
curl http://your-instance-ip/api/recipes.php?id=1
```

## 🔧 Troubleshooting

### S3 Upload Fails

**Symptoms**: Images don't upload, error in admin panel

**Check**:
```bash
# SSH to instance
ssh ubuntu@your-instance-ip

# Check AWS CLI
sudo docker-compose exec web aws --version

# Test bucket access
sudo docker-compose exec web aws s3 ls s3://recipe-images-bucket/

# Check environment variables
sudo docker-compose exec web env | grep BUCKET
```

**Fix**:
1. Verify bucket name in config
2. Check IAM instance profile has S3 permissions
3. Ensure bucket exists in correct region

### Database Connection Failed

**Check**:
```bash
# View database logs
sudo docker-compose logs db

# Wait for MySQL initialization
# Look for "ready for connections" message

# Test connection
sudo docker-compose exec db mysql -u recipe_user -p
```

### Container Won't Start

**Check**:
```bash
# View all logs
sudo docker-compose logs

# Check specific container
sudo docker-compose logs web

# Rebuild
sudo docker-compose down
sudo docker-compose up --build -d
```

### Images Not Displaying

**Check**:
1. Image uploaded successfully to S3
2. Bucket has public read access (if needed)
3. Image URL in database is correct
4. Browser can access S3 URL

**Fix**:
```bash
# Check database
sudo docker-compose exec db mysql -u recipe_user -p recipe_db
SELECT id, name, image_key, image_url FROM recipes;
```

## 🔄 Rollback

If deployment has issues:

```bash
# SSH to instance
ssh ubuntu@your-instance-ip

# Stop containers
cd /opt/recipe-app
sudo docker-compose down

# Restore from backup
sudo cp -r /var/backups/recipe-deployments/latest/* .

# Start containers
sudo docker-compose up -d
```

## 🔐 Security Checklist

Before production deployment:

- [ ] Change default admin password
- [ ] Update database passwords in config
- [ ] Configure bucket access policies
- [ ] Enable HTTPS (add SSL certificates)
- [ ] Set up firewall rules
- [ ] Enable backup retention
- [ ] Configure monitoring/alerts

## 📊 Monitoring

### Container Health
```bash
# Check all containers
sudo docker-compose ps

# Check specific service health
sudo docker inspect recipe-app-web --format='{{.State.Health.Status}}'
```

### Application Logs
```bash
# Web server logs
sudo docker-compose logs -f web

# Database logs
sudo docker-compose logs -f db

# Redis logs
sudo docker-compose logs -f redis
```

### Resource Usage
```bash
# Container stats
sudo docker stats

# Disk usage
sudo docker system df
```

## 📚 Related Documentation

- [Recipe Manager README](README.md)
- [Docker Deployment Guide](../../DOCKER-DEPLOYMENT-GUIDE.md)
- [Docker Examples Comparison](../../DOCKER-EXAMPLES-GUIDE.md)
- [S3 Bucket Integration](../../BUCKET-DEPLOYMENT-SUMMARY.md)

---

**Ready to deploy?** Make sure you've created your S3 bucket, then push to main! 🚀
