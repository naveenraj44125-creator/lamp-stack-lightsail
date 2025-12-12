const express = require('express');
const bcrypt = require('bcryptjs');
const { generateToken, authenticateToken } = require('../middleware/auth');
const db = require('../config/database');
const { upload, uploadToS3 } = require('../config/s3');

const router = express.Router();

// Register new user
router.post('/register', upload.single('profilePicture'), async (req, res) => {
    try {
        const { username, email, password, fullName, department, bio } = req.body;

        // Validate required fields
        if (!username || !email || !password || !fullName) {
            return res.status(400).json({ error: 'Username, email, password, and full name are required' });
        }

        // Check if user already exists
        const existingUser = await db.get(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            [username, email]
        );

        if (existingUser) {
            return res.status(409).json({ error: 'Username or email already exists' });
        }

        // Hash password
        const saltRounds = 10;
        const passwordHash = await bcrypt.hash(password, saltRounds);

        // Handle profile picture upload
        let profilePictureUrl = null;
        if (req.file) {
            try {
                profilePictureUrl = await uploadToS3(req.file, 'profile-pictures');
            } catch (uploadError) {
                console.error('Profile picture upload failed:', uploadError);
                // Continue without profile picture
            }
        }

        // Create user
        const result = await db.run(
            `INSERT INTO users (username, email, password_hash, full_name, department, bio, profile_picture_url)
             VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [username, email, passwordHash, fullName, department || null, bio || null, profilePictureUrl]
        );

        // Generate token
        const token = generateToken(result.id);

        // Return user data (without password)
        const newUser = await db.get(
            'SELECT id, username, email, full_name, department, bio, profile_picture_url, created_at FROM users WHERE id = ?',
            [result.id]
        );

        res.status(201).json({
            message: 'User registered successfully',
            user: newUser,
            token
        });

    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Login user
router.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;

        if (!username || !password) {
            return res.status(400).json({ error: 'Username and password are required' });
        }

        // Find user by username or email
        const user = await db.get(
            'SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = 1',
            [username, username]
        );

        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // Verify password
        const isValidPassword = await bcrypt.compare(password, user.password_hash);
        if (!isValidPassword) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        // Generate token
        const token = generateToken(user.id);

        // Return user data (without password)
        const { password_hash, ...userWithoutPassword } = user;

        res.json({
            message: 'Login successful',
            user: userWithoutPassword,
            token
        });

    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get current user profile
router.get('/profile', authenticateToken, async (req, res) => {
    try {
        const user = await db.get(
            'SELECT id, username, email, full_name, department, bio, profile_picture_url, created_at FROM users WHERE id = ?',
            [req.user.id]
        );

        res.json({ user });
    } catch (error) {
        console.error('Profile fetch error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Update user profile
router.put('/profile', authenticateToken, upload.single('profilePicture'), async (req, res) => {
    try {
        const { fullName, department, bio } = req.body;
        let profilePictureUrl = req.user.profile_picture_url;

        // Handle profile picture upload
        if (req.file) {
            try {
                profilePictureUrl = await uploadToS3(req.file, 'profile-pictures');
            } catch (uploadError) {
                console.error('Profile picture upload failed:', uploadError);
                return res.status(500).json({ error: 'Failed to upload profile picture' });
            }
        }

        // Update user
        await db.run(
            `UPDATE users SET full_name = ?, department = ?, bio = ?, profile_picture_url = ?, updated_at = CURRENT_TIMESTAMP
             WHERE id = ?`,
            [fullName || req.user.full_name, department, bio, profilePictureUrl, req.user.id]
        );

        // Get updated user data
        const updatedUser = await db.get(
            'SELECT id, username, email, full_name, department, bio, profile_picture_url, created_at, updated_at FROM users WHERE id = ?',
            [req.user.id]
        );

        res.json({
            message: 'Profile updated successfully',
            user: updatedUser
        });

    } catch (error) {
        console.error('Profile update error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
