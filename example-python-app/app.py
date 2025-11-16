#!/usr/bin/env python3
"""
Flask API Application for AWS Lightsail Deployment
"""

from flask import Flask, jsonify, request
import os
import platform
import psutil
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['JSON_SORT_KEYS'] = False
PORT = int(os.environ.get('PORT', 5000))
ENV = os.environ.get('FLASK_ENV', 'production')

@app.route('/')
def home():
    """Home page with API information"""
    return jsonify({
        'message': 'Welcome to Python Flask API',
        'version': '1.0.1',
        'environment': ENV,
        'endpoints': {
            'health': '/api/health',
            'info': '/api/info',
            'system': '/api/system',
            'echo': '/api/echo (POST)'
        }
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'python-flask-api'
    })

@app.route('/api/info')
def info():
    """Application information"""
    return jsonify({
        'application': 'Python Flask API',
        'version': '1.0.0',
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'environment': ENV,
        'port': PORT
    })

@app.route('/api/system')
def system():
    """System information"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return jsonify({
        'cpu': {
            'percent': cpu_percent,
            'count': psutil.cpu_count()
        },
        'memory': {
            'total': f"{memory.total / (1024**3):.2f} GB",
            'available': f"{memory.available / (1024**3):.2f} GB",
            'percent': memory.percent
        },
        'disk': {
            'total': f"{disk.total / (1024**3):.2f} GB",
            'used': f"{disk.used / (1024**3):.2f} GB",
            'free': f"{disk.free / (1024**3):.2f} GB",
            'percent': disk.percent
        }
    })

@app.route('/api/echo', methods=['POST'])
def echo():
    """Echo endpoint - returns the posted data"""
    data = request.get_json()
    return jsonify({
        'received': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    print(f"🚀 Starting Flask application on port {PORT}")
    print(f"🌍 Environment: {ENV}")
    app.run(host='0.0.0.0', port=PORT, debug=(ENV == 'development'))
