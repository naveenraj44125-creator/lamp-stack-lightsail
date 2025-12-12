const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const db = require('../config/database');

const router = express.Router();

// Add comment to a post
router.post('/', authenticateToken, async (req, res) => {
    try {
        const { postId, content } = req.body;

        if (!postId || !content || content.trim().length === 0) {
            return res.status(400).json({ error: 'Post ID and comment content are required' });
        }

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

        // Create comment
        const result = await db.run(
            'INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
            [postId, req.user.id, content]
        );

        // Get the created comment with user information
        const comment = await db.get(`
            SELECT c.*, u.username, u.full_name, u.profile_picture_url
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        `, [result.id]);

        res.status(201).json({
            message: 'Comment added successfully',
            comment
        });

    } catch (error) {
        console.error('Comment creation error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get comments for a post
router.get('/post/:postId', authenticateToken, async (req, res) => {
    try {
        const { postId } = req.params;
        const { page = 1, limit = 20 } = req.query;
        const offset = (page - 1) * limit;

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

        // Get comments
        const comments = await db.all(`
            SELECT c.*, u.username, u.full_name, u.profile_picture_url
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.created_at ASC
            LIMIT ? OFFSET ?
        `, [postId, parseInt(limit), parseInt(offset)]);

        res.json({ comments });

    } catch (error) {
        console.error('Comments fetch error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Delete a comment
router.delete('/:id', authenticateToken, async (req, res) => {
    try {
        const commentId = req.params.id;

        // Check if comment exists and belongs to user
        const comment = await db.get(
            'SELECT id FROM comments WHERE id = ? AND user_id = ?',
            [commentId, req.user.id]
        );

        if (!comment) {
            return res.status(404).json({ error: 'Comment not found or unauthorized' });
        }

        // Delete comment
        await db.run('DELETE FROM comments WHERE id = ?', [commentId]);

        res.json({ message: 'Comment deleted successfully' });

    } catch (error) {
        console.error('Comment deletion error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
