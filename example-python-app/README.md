# Python Flask API Application

A simple Flask-based REST API application for AWS Lightsail deployment.

## Features

- RESTful API endpoints
- Health check endpoint
- System information endpoint
- JSON responses
- Production-ready with Gunicorn

## Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/info` - Application information
- `GET /api/system` - System metrics (CPU, memory, disk)
- `POST /api/echo` - Echo endpoint (returns posted data)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Or use Gunicorn for production-like environment
gunicorn --bind 0.0.0.0:5000 app:app
```

## Environment Variables

- `PORT` - Port to run the application (default: 5000)
- `FLASK_ENV` - Environment mode (development/production)

## Deployment

This application is configured for automatic deployment to AWS Lightsail via GitHub Actions.

The deployment workflow:
1. Runs tests
2. Creates deployment package
3. Deploys to Lightsail instance
4. Configures Nginx as reverse proxy
5. Runs health checks

## Testing

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test system endpoint
curl http://localhost:5000/api/system

# Test echo endpoint
curl -X POST http://localhost:5000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello World"}'
```
# Trigger deployment
# Updated Mon Nov 17 10:47:45 PST 2025
# OIDC Test - Mon Nov 17 11:01:49 PST 2025
Sat Nov 22 15:42:50 PST 2025
Mon Nov 24 06:46:50 PST 2025
Mon Nov 24 06:54:56 PST 2025
Mon Nov 24 07:23:19 PST 2025
Mon Nov 24 09:01:22 PST 2025
