const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const db = require('../config/database');
const { upload, uploadToS3 } = require('../config/s3');

const router = express.Router();

// Create a new post
router.post('/', authenticateToken, upload.single('image'), async (req, res) => {
    try {
        const { content, postType = 'normal', visibility = 'public' } = req.body;

        if (!content || content.trim().length === 0) {
            return res.status(400).json({ error: 'Post content is required' });
        }

        // Validate post type
        if (!['normal', 'anomaly'].includes(postType)) {
            return res.status(400).json({ error: 'Invalid post type' });
        }

        // Validate visibility (anomaly posts are always public)
        let finalVisibility = visibility;
        if (postType === 'anomaly') {
            finalVisibility = 'public';
        } else if (!['public', 'friends'].includes(visibility)) {
            return res.status(400).json({ error: 'Invalid visibility setting' });
        }

        // Handle image upload
        let imageUrl = null;
        if (req.file) {
            try {
                imageUrl = await uploadToS3(req.file, 'post-images');
            } catch (uploadError) {
                console.error('Image upload failed:', uploadError);
                return res.status(500).json({ error: 'Failed to upload image' });
            }
        }

        // Create post
        const result = await db.run(
            `INSERT INTO posts (user_id, content, image_url, post_type, visibility)
             VALUES (?, ?, ?, ?, ?)`,
            [req.user.id, content, imageUrl, postType, finalVisibility]
        );

        // Get the created post with user information
        const post = await db.get(`
            SELECT p.*, u.username, u.full_name, u.profile_picture_url, u.department,
                   0 as like_count, 0 as comment_count, 0 as user_liked
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        `, [result.id]);

        res.status(201).json({
            message: 'Post created successfully',
            post
        });

    } catch (error) {
        console.error('Post creation error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get posts feed
router.get('/feed', authenticateToken, async (req, res) => {
    try {
        const { page = 1, limit = 10, type = 'all' } = req.query;
        const offset = (page - 1) * limit;

        let whereClause = 'WHERE p.is_active = 1';

        // Filter by post type
        if (type === 'anomaly') {
            whereClause += ' AND p.post_type = "anomaly"';
        } else if (type === 'normal') {
            whereClause += ' AND p.post_type = "normal"';
        }

        // Add visibility logic
        whereClause += ` AND (
            p.visibility = 'public' 
            OR p.user_id = ?
            OR (p.visibility = 'friends' AND EXISTS (
                SELECT 1 FROM friendships f 
                WHERE ((f.requester_id = ? AND f.addressee_id = p.user_id) 
                       OR (f.requester_id = p.user_id AND f.addressee_id = ?))
                AND f.status = 'accepted'
            ))
        )`;
        
        // Build complete parameter array in correct order
        // Count all placeholders in the full query:
        // 1. ul.user_id = ? (in LEFT JOIN)
        // 2. p.user_id = ? (in visibility check)  
        // 3. f.requester_id = ? (first friendship check)
        // 4. f.addressee_id = ? (second friendship check)
        // 5. LIMIT ?
        // 6. OFFSET ?
        const queryParams = [
            req.user.id,  // for ul.user_id = ?
            req.user.id,  // for p.user_id = ? (visibility check)
            req.user.id,  // for f.requester_id = ? (friendship check)
            req.user.id,  // for f.addressee_id = ? (friendship check)
            parseInt(limit),   // for LIMIT ?
            parseInt(offset)   // for OFFSET ?
        ];

        const fullQuery = `
            SELECT p.*, u.username, u.full_name, u.profile_picture_url, u.department,
                   COUNT(DISTINCT l.id) as like_count,
                   COUNT(DISTINCT c.id) as comment_count,
                   CASE WHEN ul.id IS NOT NULL THEN 1 ELSE 0 END as user_liked
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            LEFT JOIN likes ul ON p.id = ul.post_id AND ul.user_id = ?
            ${whereClause}
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        `;

        console.log('Full query:', fullQuery);
        console.log('Query parameters:', queryParams);
        console.log('Parameter count:', queryParams.length);
        console.log('Placeholder count in query:', (fullQuery.match(/\?/g) || []).length);

        const posts = await db.all(fullQuery, queryParams);

        res.json({ posts });

    } catch (error) {
        console.error('Feed fetch error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get single post
router.get('/:id', authenticateToken, async (req, res) => {
    try {
        const postId = req.params.id;

        const post = await db.get(`
            SELECT p.*, u.username, u.full_name, u.profile_picture_url, u.department,
                   COUNT(DISTINCT l.id) as like_count,
                   COUNT(DISTINCT c.id) as comment_count,
                   CASE WHEN ul.id IS NOT NULL THEN 1 ELSE 0 END as user_liked
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            LEFT JOIN likes ul ON p.id = ul.post_id AND ul.user_id = ?
            WHERE p.id = ? AND p.is_active = 1
            AND (
                p.visibility = 'public' 
                OR p.user_id = ?
                OR (p.visibility = 'friends' AND EXISTS (
                    SELECT 1 FROM friendships f 
                    WHERE ((f.requester_id = ? AND f.addressee_id = p.user_id) 
                           OR (f.requester_id = p.user_id AND f.addressee_id = ?))
                    AND f.status = 'accepted'
                ))
            )
            GROUP BY p.id
        `, [req.user.id, postId, req.user.id, req.user.id, req.user.id]);

        if (!post) {
            return res.status(404).json({ error: 'Post not found' });
        }

        res.json({ post });

    } catch (error) {
        console.error('Post fetch error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Like/Unlike a post
router.post('/:id/like', authenticateToken, async (req, res) => {
    try {
        const postId = req.params.id;

        // Check if post exists and user can see it
        const post = await db.get(`
            SELECT p.id FROM posts p
            WHERE p.id = ? AND p.is_active = 1
            AND (
                p.visibility = 'public' 
                OR p.user_id = ?
                OR (p.visibility = 'friends' AND EXISTS (
                    SELECT 1 FROM friendships f 
                    WHERE ((f.requester_id = ? AND f.addressee_id = p.user_id) 
                           OR (f.requester_id = p.user_id AND f.addressee_id = ?))
                    AND f.status = 'accepted'
                ))
            )
        `, [postId, req.user.id, req.user.id, req.user.id]);

        if (!post) {
            return res.status(404).json({ error: 'Post not found' });
        }

        // Check if already liked
        const existingLike = await db.get(
            'SELECT id FROM likes WHERE post_id = ? AND user_id = ?',
            [postId, req.user.id]
        );

        if (existingLike) {
            // Unlike
            await db.run('DELETE FROM likes WHERE id = ?', [existingLike.id]);
            res.json({ message: 'Post unliked', liked: false });
        } else {
            // Like
            await db.run(
                'INSERT INTO likes (post_id, user_id) VALUES (?, ?)',
                [postId, req.user.id]
            );
            res.json({ message: 'Post liked', liked: true });
        }

    } catch (error) {
        console.error('Like toggle error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Delete a post
router.delete('/:id', authenticateToken, async (req, res) => {
    try {
        const postId = req.params.id;

        // Check if post exists and belongs to user
        const post = await db.get(
            'SELECT id FROM posts WHERE id = ? AND user_id = ? AND is_active = 1',
            [postId, req.user.id]
        );

        if (!post) {
            return res.status(404).json({ error: 'Post not found or unauthorized' });
        }

        // Soft delete
        await db.run(
            'UPDATE posts SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            [postId]
        );

        res.json({ message: 'Post deleted successfully' });

    } catch (error) {
        console.error('Post deletion error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
