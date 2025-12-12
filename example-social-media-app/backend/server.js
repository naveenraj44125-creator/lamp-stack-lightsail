const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const db = require('./config/database');

// Import routes
const authRoutes = require('./routes/auth');
const postsRoutes = require('./routes/posts');
const commentsRoutes = require('./routes/comments');
const friendsRoutes = require('./routes/friends');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from frontend
app.use(express.static(path.join(__dirname, '../frontend')));

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/posts', postsRoutes);
app.use('/api/comments', commentsRoutes);
app.use('/api/friends', friendsRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy',  // CRITICAL: Must return 'healthy' for deployment verification
        message: 'Employee Social App API is running',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Serve frontend for all non-API routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err);
    
    if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(400).json({ error: 'File too large' });
    }
    
    if (err.type === 'entity.parse.failed') {
        return res.status(400).json({ error: 'Invalid JSON' });
    }
    
    res.status(500).json({ error: 'Internal server error' });
});

// Initialize database connection and start server
async function startServer() {
    try {
        await db.connect();
        
        app.listen(PORT, () => {
            console.log(`🚀 Employee Social App server running on port ${PORT}`);
            console.log(`📱 Frontend: http://localhost:${PORT}`);
            console.log(`🔗 API: http://localhost:${PORT}/api`);
            console.log(`💚 Health check: http://localhost:${PORT}/api/health`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down server...');
    try {
        await db.close();
        console.log('✅ Database connection closed');
        process.exit(0);
    } catch (error) {
        console.error('❌ Error during shutdown:', error);
        process.exit(1);
    }
});

startServer();
