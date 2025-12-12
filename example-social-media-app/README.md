# 📱 Employee Social Media App

A full-stack Node.js social media application with SQLite database, designed for employee networking and communication.

## 🚀 Features

- **User Authentication**: Register, login, and secure JWT-based sessions
- **Social Posts**: Create, view, and interact with posts
- **Comments System**: Comment on posts and engage with colleagues
- **Friends Network**: Connect with other employees
- **Real-time Updates**: Dynamic content loading
- **File Uploads**: Share images and documents
- **AWS Integration**: S3 bucket integration for file storage

## 🏗️ Architecture

```
example-social-media-app/
├── server.js              # Root entry point (deployment compatible)
├── package.json           # Dependencies and scripts
├── backend/               # Server-side application
│   ├── server.js         # Main Express server
│   ├── config/           # Database and configuration
│   ├── routes/           # API endpoints
│   └── middleware/       # Authentication and validation
├── frontend/             # Client-side application
│   ├── index.html        # Main HTML page
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript modules
└── database/             # SQLite database files
```

## 🔧 Deployment Configuration

This app uses `deployment-social-media-app.config.yml` with the following key settings:

- **Application Type**: `nodejs` (critical for proper deployment)
- **Entry Point**: `server.js` (delegates to `backend/server.js`)
- **Health Check**: `/api/health` endpoint returns `{"status": "healthy"}`
- **Database**: SQLite with PostgreSQL RDS option
- **Web Server**: Nginx proxy to Node.js on port 3000
- **Dependencies**: Node.js 18, PM2 process manager

## 🚦 Health Check

The application provides a health check endpoint at `/api/health`:

```json
{
  "status": "healthy",
  "message": "Employee Social App API is running",
  "timestamp": "2025-12-12T18:37:38.334Z",
  "uptime": 2.6995585
}
```

## 🛠️ Local Development

1. **Install Dependencies**:
   ```bash
   cd example-social-media-app
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - API: http://localhost:3000/api
   - Health Check: http://localhost:3000/api/health

## 📦 Dependencies

### Production Dependencies
- **express**: Web framework
- **cors**: Cross-origin resource sharing
- **dotenv**: Environment variable management
- **sqlite3**: SQLite database driver
- **mysql2**: MySQL database driver (for RDS)
- **bcryptjs**: Password hashing
- **jsonwebtoken**: JWT authentication
- **multer**: File upload handling
- **aws-sdk**: AWS services integration

### Development Dependencies
- **nodemon**: Development server with auto-reload

## 🔐 Environment Variables

```bash
# Application
NODE_ENV=production
PORT=3000
APP_ENV=production

# Database
DB_TYPE=postgresql
DB_HOST=RDS_ENDPOINT
DB_NAME=nodejs_app_db
DB_USER=app_user
DB_PASSWORD=secure_password_123

# AWS Integration
BUCKET_NAME=social-media-app-bucket
AWS_REGION=us-east-1
```

## 🚀 Deployment Process

1. **GitHub Actions** triggers on push to main branch
2. **Dependencies** installed (Node.js, Nginx, PM2)
3. **Application** deployed to `/var/www/html`
4. **PM2** starts Node.js service with `server.js`
5. **Nginx** configured to proxy requests to localhost:3000
6. **Health Check** verifies deployment success

## 🔍 Troubleshooting

### Common Issues

1. **Static Page Instead of App**:
   - Ensure `type: nodejs` in deployment config
   - Verify `server.js` exists at root level
   - Check PM2 service status: `sudo systemctl status nodejs-app.service`

2. **Health Check Fails**:
   - Verify endpoint returns `{"status": "healthy"}`
   - Check Node.js app is running on port 3000
   - Test locally: `curl http://localhost:3000/api/health`

3. **Database Connection Issues**:
   - Check SQLite file permissions
   - Verify database directory exists
   - Review environment variables

### Verification Commands

```bash
# Check Node.js service
sudo systemctl status nodejs-app.service

# Check port 3000 is listening
sudo ss -tlnp | grep :3000

# Test health endpoint
curl http://localhost:3000/api/health

# View application logs
sudo journalctl -u nodejs-app.service -f
```

## 📊 Monitoring

The deployment includes:
- **Health Checks**: Automated endpoint monitoring
- **Performance Tests**: Response time validation
- **Security Checks**: Basic security header verification
- **Logging**: Structured application and deployment logs

## 🎯 Success Criteria

✅ **Health Check**: Returns `{"status": "healthy"}`  
✅ **Frontend**: Serves Employee Social App interface  
✅ **API Endpoints**: All `/api/*` routes functional  
✅ **Database**: SQLite connection established  
✅ **File Uploads**: AWS S3 integration working  
✅ **Authentication**: JWT-based login system active

---

**Note**: This app demonstrates the fix for the "static page instead of dynamic content" issue by using proper entry point configuration and Node.js application type in the deployment settings.