# 🐳 Docker Quick Start Guide

Get started with Docker deployment in 5 minutes!

## 🎯 Choose Your Example

### Option 1: Basic LAMP Stack (Learning)
**Best for**: Understanding Docker basics

```bash
cd example-docker-app
docker-compose up -d
open http://localhost
```

**What you get**:
- Service status dashboard
- MySQL + Redis + phpMyAdmin
- Health monitoring
- ~500 lines of code

---

### Option 2: Recipe Manager (Production)
**Best for**: Real applications with S3

```bash
# 1. Create S3 bucket
aws lightsail create-bucket \
  --bucket-name recipe-images-bucket \
  --bundle-id small_1_0

# 2. Start locally
cd example-recipe-docker-app
cp .env.example .env
nano .env  # Add your bucket name
docker-compose up -d

# 3. Access
open http://localhost              # Public gallery
open http://localhost/admin/       # Admin (admin/admin123)
open http://localhost:8080         # phpMyAdmin
```

**What you get**:
- Full recipe CRUD app
- Image upload to S3
- Admin authentication
- RESTful API
- ~1,700 lines of code

---

## 🚀 Deploy to AWS Lightsail

### Step 1: Choose Configuration

**Basic LAMP**:
```yaml
# Use: deployment-docker.config.yml
dependencies:
  docker:
    enabled: true
deployment:
  use_docker: true
```

**Recipe Manager**:
```yaml
# Use: deployment-recipe-docker.config.yml
dependencies:
  docker:
    enabled: true
deployment:
  use_docker: true
environment_variables:
  BUCKET_NAME: recipe-images-bucket  # Your bucket
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add Docker app"
git push origin main
```

### Step 3: Wait for Deployment

GitHub Actions will:
1. Install Docker on Lightsail instance (5-8 min)
2. Download Docker images (5-10 min)
3. Build custom images (3-5 min)
4. Start containers (1-2 min)

**Total**: 15-25 minutes first time, 2-5 minutes after

### Step 4: Access Your App

```
http://your-instance-ip/
```

---

## 📊 Comparison

| Feature | Basic LAMP | Recipe Manager |
|---------|------------|----------------|
| **Complexity** | Simple | Advanced |
| **S3 Integration** | ❌ | ✅ |
| **Authentication** | ❌ | ✅ |
| **File Upload** | ❌ | ✅ |
| **API** | Basic | RESTful |
| **UI** | Simple | Modern |
| **Production Ready** | No | Yes |

---

## 🔧 Common Commands

### Local Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up --build -d

# Check status
docker-compose ps
```

### Debugging

```bash
# Enter container
docker-compose exec web bash

# Check database
docker-compose exec db mysql -u root -p

# Test Redis
docker-compose exec redis redis-cli ping

# View specific logs
docker-compose logs web
docker-compose logs db
```

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "8080:80"  # Use 8080 instead of 80
```

### Container Won't Start
```bash
docker-compose logs service-name
docker-compose down
docker-compose up --build -d
```

### S3 Upload Fails (Recipe Manager)
```bash
# Check bucket exists
aws lightsail get-bucket --bucket-name recipe-images-bucket

# Verify environment
docker-compose exec web env | grep BUCKET
```

---

## 📚 Next Steps

1. ✅ Test locally with `docker-compose up`
2. ✅ Customize for your needs
3. ✅ Deploy to Lightsail
4. ✅ Monitor with `docker-compose logs`
5. ✅ Scale as needed

---

## 📖 Full Documentation

- [Docker Deployment Guide](DOCKER-DEPLOYMENT-GUIDE.md) - Complete guide
- [Docker Examples Comparison](DOCKER-EXAMPLES-GUIDE.md) - Detailed comparison
- [Basic LAMP README](example-docker-app/README.md) - Basic example docs
- [Recipe Manager README](example-recipe-docker-app/README.md) - Recipe app docs

---

**Ready?** Pick an example and run `docker-compose up -d` now! 🚀
