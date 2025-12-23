const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/taskdb';
let db;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Connect to MongoDB
async function connectDB() {
    try {
        const client = new MongoClient(MONGODB_URI);
        await client.connect();
        db = client.db();
        console.log('✅ Connected to MongoDB');
        
        // Create indexes
        await db.collection('tasks').createIndex({ createdAt: -1 });
        await db.collection('tasks').createIndex({ status: 1 });
    } catch (error) {
        console.error('❌ MongoDB connection error:', error.message);
        process.exit(1);
    }
}

// API Routes

// Get all tasks
app.get('/api/tasks', async (req, res) => {
    try {
        const tasks = await db.collection('tasks')
            .find({})
            .sort({ createdAt: -1 })
            .toArray();
        res.json(tasks);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create task
app.post('/api/tasks', async (req, res) => {
    try {
        const { title, description, priority } = req.body;
        if (!title) {
            return res.status(400).json({ error: 'Title is required' });
        }
        
        const task = {
            title,
            description: description || '',
            priority: priority || 'medium',
            status: 'pending',
            createdAt: new Date(),
            updatedAt: new Date()
        };
        
        const result = await db.collection('tasks').insertOne(task);
        task._id = result.insertedId;
        res.status(201).json(task);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update task
app.put('/api/tasks/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const updates = { ...req.body, updatedAt: new Date() };
        delete updates._id;
        
        const result = await db.collection('tasks').findOneAndUpdate(
            { _id: new ObjectId(id) },
            { $set: updates },
            { returnDocument: 'after' }
        );
        
        if (!result) {
            return res.status(404).json({ error: 'Task not found' });
        }
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Delete task
app.delete('/api/tasks/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const result = await db.collection('tasks').deleteOne({ _id: new ObjectId(id) });
        
        if (result.deletedCount === 0) {
            return res.status(404).json({ error: 'Task not found' });
        }
        res.json({ message: 'Task deleted' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Health check
app.get('/api/health', async (req, res) => {
    try {
        await db.command({ ping: 1 });
        res.json({ 
            status: 'healthy', 
            mongodb: 'connected',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({ status: 'unhealthy', error: error.message });
    }
});

// Stats endpoint
app.get('/api/stats', async (req, res) => {
    try {
        const total = await db.collection('tasks').countDocuments();
        const pending = await db.collection('tasks').countDocuments({ status: 'pending' });
        const completed = await db.collection('tasks').countDocuments({ status: 'completed' });
        
        res.json({ total, pending, completed });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server
connectDB().then(() => {
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`🚀 Task Manager running on http://0.0.0.0:${PORT}`);
    });
});
