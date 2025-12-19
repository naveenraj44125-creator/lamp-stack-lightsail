const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');

// Ensure data directory exists
async function ensureDataDir() {
    try {
        await fs.access(DATA_DIR);
    } catch {
        await fs.mkdir(DATA_DIR, { recursive: true });
    }
}

// Initialize data file
async function initializeData() {
    const postsFile = path.join(DATA_DIR, 'posts.json');
    try {
        await fs.access(postsFile);
    } catch {
        const initialPosts = [
            {
                id: uuidv4(),
                title: "Welcome to Your New Blog!",
                content: "This is your first blog post. You can edit or delete this post and create new ones using the interface above.",
                author: "Blog Admin",
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                tags: ["welcome", "first-post"]
            },
            {
                id: uuidv4(),
                title: "Getting Started with Your Blog",
                content: "Here are some tips for using your new blog:\\n\\n1. Click 'New Post' to create articles\\n2. Use the search feature to find posts\\n3. Edit posts by clicking the edit button\\n4. Delete posts you no longer need\\n\\nEnjoy blogging!",
                author: "Blog Admin",
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                tags: ["tutorial", "getting-started"]
            }
        ];
        await fs.writeFile(postsFile, JSON.stringify(initialPosts, null, 2));
    }
}

// Middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            fontSrc: ["'self'", "https://fonts.gstatic.com"],
            scriptSrc: ["'self'"],
            imgSrc: ["'self'", "data:", "https:"]
        }
    }
}));

app.use(cors());
app.use(compression());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Helper functions
async function readPosts() {
    try {
        const data = await fs.readFile(path.join(DATA_DIR, 'posts.json'), 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error reading posts:', error);
        return [];
    }
}

async function writePosts(posts) {
    try {
        await fs.writeFile(path.join(DATA_DIR, 'posts.json'), JSON.stringify(posts, null, 2));
        return true;
    } catch (error) {
        console.error('Error writing posts:', error);
        return false;
    }
}

// API Routes

// Get all posts
app.get('/api/posts', async (req, res) => {
    try {
        const posts = await readPosts();
        const { search, limit = 10, offset = 0 } = req.query;
        
        let filteredPosts = posts;
        
        if (search) {
            const searchLower = search.toLowerCase();
            filteredPosts = posts.filter(post => 
                post.title.toLowerCase().includes(searchLower) ||
                post.content.toLowerCase().includes(searchLower) ||
                post.author.toLowerCase().includes(searchLower) ||
                (post.tags && post.tags.some(tag => tag.toLowerCase().includes(searchLower)))
            );
        }
        
        // Sort by creation date (newest first)
        filteredPosts.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        
        // Pagination
        const paginatedPosts = filteredPosts.slice(parseInt(offset), parseInt(offset) + parseInt(limit));
        
        res.json({
            posts: paginatedPosts,
            total: filteredPosts.length,
            hasMore: parseInt(offset) + parseInt(limit) < filteredPosts.length
        });
    } catch (error) {
        console.error('Error fetching posts:', error);
        res.status(500).json({ error: 'Failed to fetch posts' });
    }
});

// Get single post
app.get('/api/posts/:id', async (req, res) => {
    try {
        const posts = await readPosts();
        const post = posts.find(p => p.id === req.params.id);
        
        if (!post) {
            return res.status(404).json({ error: 'Post not found' });
        }
        
        res.json(post);
    } catch (error) {
        console.error('Error fetching post:', error);
        res.status(500).json({ error: 'Failed to fetch post' });
    }
});

// Create new post
app.post('/api/posts', async (req, res) => {
    try {
        const { title, content, author, tags } = req.body;
        
        if (!title || !content) {
            return res.status(400).json({ error: 'Title and content are required' });
        }
        
        const posts = await readPosts();
        const newPost = {
            id: uuidv4(),
            title: title.trim(),
            content: content.trim(),
            author: author?.trim() || 'Anonymous',
            tags: Array.isArray(tags) ? tags.filter(tag => tag.trim()) : [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        
        posts.push(newPost);
        
        if (await writePosts(posts)) {
            res.status(201).json(newPost);
        } else {
            res.status(500).json({ error: 'Failed to save post' });
        }
    } catch (error) {
        console.error('Error creating post:', error);
        res.status(500).json({ error: 'Failed to create post' });
    }
});

// Update post
app.put('/api/posts/:id', async (req, res) => {
    try {
        const { title, content, author, tags } = req.body;
        
        if (!title || !content) {
            return res.status(400).json({ error: 'Title and content are required' });
        }
        
        const posts = await readPosts();
        const postIndex = posts.findIndex(p => p.id === req.params.id);
        
        if (postIndex === -1) {
            return res.status(404).json({ error: 'Post not found' });
        }
        
        posts[postIndex] = {
            ...posts[postIndex],
            title: title.trim(),
            content: content.trim(),
            author: author?.trim() || posts[postIndex].author,
            tags: Array.isArray(tags) ? tags.filter(tag => tag.trim()) : posts[postIndex].tags,
            updatedAt: new Date().toISOString()
        };
        
        if (await writePosts(posts)) {
            res.json(posts[postIndex]);
        } else {
            res.status(500).json({ error: 'Failed to update post' });
        }
    } catch (error) {
        console.error('Error updating post:', error);
        res.status(500).json({ error: 'Failed to update post' });
    }
});

// Delete post
app.delete('/api/posts/:id', async (req, res) => {
    try {
        const posts = await readPosts();
        const postIndex = posts.findIndex(p => p.id === req.params.id);
        
        if (postIndex === -1) {
            return res.status(404).json({ error: 'Post not found' });
        }
        
        posts.splice(postIndex, 1);
        
        if (await writePosts(posts)) {
            res.json({ message: 'Post deleted successfully' });
        } else {
            res.status(500).json({ error: 'Failed to delete post' });
        }
    } catch (error) {
        console.error('Error deleting post:', error);
        res.status(500).json({ error: 'Failed to delete post' });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: require('./package.json').version
    });
});

// Serve the main page for all non-API routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Initialize and start server
async function startServer() {
    try {
        await ensureDataDir();
        await initializeData();
        
        app.listen(PORT, () => {
            console.log(`🚀 Blog server running on port ${PORT}`);
            console.log(`📝 Environment: ${process.env.NODE_ENV || 'development'}`);
            console.log(`💾 Data directory: ${DATA_DIR}`);
            console.log(`🌐 Access your blog at: http://localhost:${PORT}`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer();

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});