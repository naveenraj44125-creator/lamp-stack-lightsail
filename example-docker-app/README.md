# 🐳 Docker Deployment Example

This is a complete example demonstrating Docker-based deployment with the Generic Deployment System.

## 📋 What's Included

- **Multi-container LAMP Stack** with Docker Compose
- **Apache + PHP 8.1** web server
- **MySQL 8.0** database
- **Redis** caching layer
- **phpMyAdmin** database management
- **Nginx** reverse proxy (optional)

## 🚀 Quick Start

### Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- **Web App**: http://localhost
- **phpMyAdmin**: http://localhost:8080
- **API**: http://localhost/api

### Deploy to AWS Lightsail

1. **Configure deployment** in `deployment-docker.config.yml`:
   ```yaml
   dependencies:
     docker:
       enabled: true
   
   deployment:
     use_docker: true
   ```

2. **Push to GitHub** - Deployment happens automatically

3. **Access your app** at your Lightsail instance IP

## 📁 Project Structure

```
example-docker-app/
├── docker-compose.yml       # Container orchestration
├── Dockerfile              # Web server container
├── nginx.conf              # Nginx configuration
├── src/                    # Application code
│   ├── index.php
│   ├── api/
│   └── config/
├── sql/                    # Database initialization
│   └── init.sql
└── .env.example           # Environment variables template
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Database
DB_HOST=db
DB_NAME=docker_app
DB_USER=app_user
DB_PASSWORD=secure_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Application
APP_ENV=production
APP_DEBUG=false
```

### Docker Compose Services

- **web**: Apache + PHP application server
- **db**: MySQL database with persistent storage
- **redis**: Redis cache server
- **phpmyadmin**: Database management UI
- **nginx**: (Optional) Reverse proxy with SSL

## 🎯 Features Demonstrated

### 1. Multi-Container Architecture
- Separate containers for web, database, cache
- Service isolation and scalability
- Inter-container networking

### 2. Persistent Data
- MySQL data persists in Docker volumes
- Redis data persistence
- Application uploads storage

### 3. Development Workflow
- Hot-reload with volume mounting
- Easy service restart
- Centralized logging

### 4. Production Ready
- Health checks for all services
- Automatic restart policies
- Resource limits
- Security best practices

## 🔍 Testing Locally

```bash
# Build and start
docker-compose up --build -d

# Check service health
docker-compose ps

# Test web server
curl http://localhost

# Test database connection
docker-compose exec web php -r "echo 'DB: ' . (new PDO('mysql:host=db;dbname=docker_app', 'app_user', 'secure_password') ? 'Connected' : 'Failed');"

# Test Redis
docker-compose exec web php -r "\$redis = new Redis(); \$redis->connect('redis', 6379); echo 'Redis: ' . (\$redis->ping() ? 'Connected' : 'Failed');"
```

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Resource Usage
```bash
docker stats
```

### Container Status
```bash
docker-compose ps
```

## 🔄 Deployment Process

When deployed to Lightsail with `use_docker: true`:

1. **Upload** - Application package uploaded to instance
2. **Extract** - Files extracted to `/opt/docker-app`
3. **Environment** - `.env` file created from config
4. **Build** - Docker images built from Dockerfile
5. **Start** - Containers started with `docker-compose up -d`
6. **Verify** - Health checks confirm services are running

## 🛠️ Customization

### Add New Service

Edit `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
    networks:
      - app-network
```

### Modify PHP Configuration

Edit `Dockerfile`:

```dockerfile
# Install additional PHP extensions
RUN apt-get update && apt-get install -y \
    php8.1-mongodb \
    php8.1-imagick
```

### Add Nginx SSL

Uncomment nginx service in `docker-compose.yml` and add certificates.

## 🚨 Troubleshooting

### Container Won't Start
```bash
docker-compose logs service-name
docker-compose up --force-recreate service-name
```

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :80

# Change port in docker-compose.yml
ports:
  - "8080:80"  # Use 8080 instead
```

### Database Connection Failed
```bash
# Check database is running
docker-compose ps db

# Verify credentials in .env
docker-compose exec db mysql -u app_user -p
```

### Out of Disk Space
```bash
# Clean up unused images/containers
docker system prune -a

# Check disk usage
docker system df
```

## 📚 Learn More

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [DOCKER-DEPLOYMENT-GUIDE.md](../DOCKER-DEPLOYMENT-GUIDE.md)
- [Lightsail Documentation](https://docs.aws.amazon.com/lightsail/)

## 🎓 Next Steps

1. **Customize** the application for your needs
2. **Test locally** with `docker-compose up`
3. **Configure** deployment settings
4. **Deploy** to Lightsail
5. **Monitor** with Docker logs and stats

---

**Need Help?** Check the main [DOCKER-DEPLOYMENT-GUIDE.md](../DOCKER-DEPLOYMENT-GUIDE.md) for comprehensive documentation.
