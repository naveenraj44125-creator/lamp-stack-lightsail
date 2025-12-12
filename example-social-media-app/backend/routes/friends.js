const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const db = require('../config/database');

const router = express.Router();

// Send friend request
router.post('/request', authenticateToken, async (req, res) => {
    try {
        const { userId } = req.body;

        if (!userId) {
            return res.status(400).json({ error: 'User ID is required' });
        }

        if (userId == req.user.id) {
            return res.status(400).json({ error: 'Cannot send friend request to yourself' });
        }

        // Check if target user exists
        const targetUser = await db.get(
            'SELECT id, username, full_name FROM users WHERE id = ? AND is_active = 1',
            [userId]
        );

        if (!targetUser) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Check if friendship already exists
        const existingFriendship = await db.get(
            `SELECT id, status FROM friendships 
             WHERE (requester_id = ? AND addressee_id = ?) 
                OR (requester_id = ? AND addressee_id = ?)`,
            [req.user.id, userId, userId, req.user.id]
        );

        if (existingFriendship) {
            if (existingFriendship.status === 'accepted') {
                return res.status(409).json({ error: 'Already friends' });
            } else if (existingFriendship.status === 'pending') {
                return res.status(409).json({ error: 'Friend request already sent' });
            }
        }

        // Create friend request
        await db.run(
            'INSERT INTO friendships (requester_id, addressee_id, status) VALUES (?, ?, ?)',
            [req.user.id, userId, 'pending']
        );

        res.status(201).json({
            message: 'Friend request sent successfully',
            targetUser
        });

    } catch (error) {
        console.error('Friend request error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Accept/Decline friend request
router.put('/request/:id', authenticateToken, async (req, res) => {
    try {
        const friendshipId = req.params.id;
        const { action } = req.body; // 'accept' or 'decline'

        if (!['accept', 'decline'].includes(action)) {
            return res.status(400).json({ error: 'Action must be "accept" or "decline"' });
        }

        // Check if friendship request exists and is for this user
        const friendship = await db.get(
            'SELECT * FROM friendships WHERE id = ? AND addressee_id = ? AND status = ?',
            [friendshipId, req.user.id, 'pending']
        );

        if (!friendship) {
            return res.status(404).json({ error: 'Friend request not found' });
        }

        const newStatus = action === 'accept' ? 'accepted' : 'declined';

        // Update friendship status
        await db.run(
            'UPDATE friendships SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            [newStatus, friendshipId]
        );

        // Get requester info
        const requester = await db.get(
            'SELECT id, username, full_name, profile_picture_url FROM users WHERE id = ?',
            [friendship.requester_id]
        );

        res.json({
            message: `Friend request ${action}ed successfully`,
            friendship: {
                id: friendshipId,
                status: newStatus,
                requester
            }
        });

    } catch (error) {
        console.error('Friend request response error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get friends list
router.get('/', authenticateToken, async (req, res) => {
    try {
        const friends = await db.all(`
            SELECT 
                f.id as friendship_id,
                f.created_at as friends_since,
                CASE 
                    WHEN f.requester_id = ? THEN u2.id
                    ELSE u1.id
                END as friend_id,
                CASE 
                    WHEN f.requester_id = ? THEN u2.username
                    ELSE u1.username
                END as username,
                CASE 
                    WHEN f.requester_id = ? THEN u2.full_name
                    ELSE u1.full_name
                END as full_name,
                CASE 
                    WHEN f.requester_id = ? THEN u2.profile_picture_url
                    ELSE u1.profile_picture_url
                END as profile_picture_url,
                CASE 
                    WHEN f.requester_id = ? THEN u2.department
                    ELSE u1.department
                END as department
            FROM friendships f
            JOIN users u1 ON f.requester_id = u1.id
            JOIN users u2 ON f.addressee_id = u2.id
            WHERE (f.requester_id = ? OR f.addressee_id = ?) 
                AND f.status = 'accepted'
                AND u1.is_active = 1 AND u2.is_active = 1
            ORDER BY f.created_at DESC
        `, [req.user.id, req.user.id, req.user.id, req.user.id, req.user.id, req.user.id, req.user.id]);

        res.json({ friends });

    } catch (error) {
        console.error('Friends list error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get pending friend requests (received)
router.get('/requests/received', authenticateToken, async (req, res) => {
    try {
        const requests = await db.all(`
            SELECT f.id, f.created_at, u.id as requester_id, u.username, u.full_name, u.profile_picture_url, u.department
            FROM friendships f
            JOIN users u ON f.requester_id = u.id
            WHERE f.addressee_id = ? AND f.status = 'pending' AND u.is_active = 1
            ORDER BY f.created_at DESC
        `, [req.user.id]);

        res.json({ requests });

    } catch (error) {
        console.error('Received requests error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get pending friend requests (sent)
router.get('/requests/sent', authenticateToken, async (req, res) => {
    try {
        const requests = await db.all(`
            SELECT f.id, f.created_at, u.id as addressee_id, u.username, u.full_name, u.profile_picture_url, u.department
            FROM friendships f
            JOIN users u ON f.addressee_id = u.id
            WHERE f.requester_id = ? AND f.status = 'pending' AND u.is_active = 1
            ORDER BY f.created_at DESC
        `, [req.user.id]);

        res.json({ requests });

    } catch (error) {
        console.error('Sent requests error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Remove friend
router.delete('/:friendId', authenticateToken, async (req, res) => {
    try {
        const friendId = req.params.friendId;

        // Find and delete friendship
        const result = await db.run(
            `DELETE FROM friendships 
             WHERE ((requester_id = ? AND addressee_id = ?) 
                    OR (requester_id = ? AND addressee_id = ?))
                AND status = 'accepted'`,
            [req.user.id, friendId, friendId, req.user.id]
        );

        if (result.changes === 0) {
            return res.status(404).json({ error: 'Friendship not found' });
        }

        res.json({ message: 'Friend removed successfully' });

    } catch (error) {
        console.error('Remove friend error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Search users (for adding friends)
router.get('/search', authenticateToken, async (req, res) => {
    try {
        const { q } = req.query;

        if (!q || q.trim().length < 2) {
            return res.status(400).json({ error: 'Search query must be at least 2 characters' });
        }

        const searchTerm = `%${q.trim()}%`;

        const users = await db.all(`
            SELECT u.id, u.username, u.full_name, u.profile_picture_url, u.department,
                   CASE 
                       WHEN f.id IS NOT NULL THEN f.status
                       ELSE NULL
                   END as friendship_status
            FROM users u
            LEFT JOIN friendships f ON (
                (f.requester_id = ? AND f.addressee_id = u.id) 
                OR (f.requester_id = u.id AND f.addressee_id = ?)
            )
            WHERE u.id != ? 
                AND u.is_active = 1
                AND (u.username LIKE ? OR u.full_name LIKE ?)
            ORDER BY u.full_name
            LIMIT 20
        `, [req.user.id, req.user.id, req.user.id, searchTerm, searchTerm]);

        res.json({ users });

    } catch (error) {
        console.error('User search error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
