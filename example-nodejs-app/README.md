# Node.js Express Demo Application

A simple Node.js Express application demonstrating deployment to AWS Lightsail using the generic deployment system.

## Features

- Express.js web server
- Health check endpoint
- Application info API
- PM2 process management
- Nginx reverse proxy

## Local Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run in production mode
npm start
```

## Deployment

This application is automatically deployed to AWS Lightsail when changes are pushed to the main branch.

The deployment is configured in:
- `deployment-nodejs.config.yml` - Deployment configuration
- `.github/workflows/deploy-nodejs.yml` - GitHub Actions workflow

## Endpoints

- `GET /` - Home page
- `GET /api/health` - Health check
- `GET /api/info` - Application information

## Environment Variables

- `PORT` - Server port (default: 3000)
- `NODE_ENV` - Environment (development/production)
