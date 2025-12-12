#!/usr/bin/env node

/**
 * Instagram Clone - Production Server
 * 
 * This server serves the React build in production and provides
 * a simple API for health checks and basic functionality.
 */

const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from React build
const buildPath = path.join(__dirname, 'build');
if (fs.existsSync(buildPath)) {
    app.use(express.static(buildPath));
    console.log('✅ Serving React build from:', buildPath);
} else {
    console.log('⚠️  React build not found at:', buildPath);
    console.log('📝 Run "npm run build" to generate the build');
}

// API Routes
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        message: 'Instagram Clone API is running',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: '1.0.0',
        features: {
            react_app: fs.existsSync(buildPath) ? 'active' : 'build_missing',
            static_files: 'active'
        }
    });
});

app.get('/api/status', (req, res) => {
    res.json({
        app: 'Instagram Clone',
        version: '1.0.0',
        status: 'operational',
        build_exists: fs.existsSync(buildPath),
        build_path: buildPath
    });
});

// Mock API endpoints for development/demo
app.get('/api/posts', (req, res) => {
    res.json({
        success: true,
        posts: [
            {
                id: 1,
                username: 'demo_user',
                caption: 'Welcome to Instagram Clone!',
                image: 'https://picsum.photos/400/400?random=1',
                likes: 42,
                comments: 5,
                timestamp: new Date().toISOString()
            }
        ]
    });
});

app.get('/api/user/:username', (req, res) => {
    const { username } = req.params;
    res.json({
        success: true,
        user: {
            username: username,
            fullName: 'Demo User',
            bio: 'Instagram Clone Demo Account',
            posts: 12,
            followers: 150,
            following: 89,
            profilePicture: 'https://picsum.photos/150/150?random=2'
        }
    });
});

// Catch all handler: send back React's index.html file for client-side routing
app.get('*', (req, res) => {
    const indexPath = path.join(buildPath, 'index.html');
    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(404).json({
            error: 'React build not found',
            message: 'Please run "npm run build" to generate the React build',
            buildPath: buildPath,
            suggestion: 'This is a React app that needs to be built for production'
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('❌ Server error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message
    });
});

// Start server
app.listen(PORT, () => {
    console.log('🚀 Instagram Clone Server Started!');
    console.log(`📍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🌐 Server running on port: ${PORT}`);
    console.log(`🔗 Health check: http://localhost:${PORT}/api/health`);
    console.log(`📱 App: http://localhost:${PORT}`);
    
    if (!fs.existsSync(buildPath)) {
        console.log('');
        console.log('⚠️  IMPORTANT: React build not found!');
        console.log('📝 Run the following commands to build the React app:');
        console.log('   npm install');
        console.log('   npm run build');
    }
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 SIGTERM received, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('🛑 SIGINT received, shutting down gracefully...');
    process.exit(0);
});