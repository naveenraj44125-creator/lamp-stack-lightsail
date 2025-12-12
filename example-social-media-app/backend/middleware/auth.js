const jwt = require('jsonwebtoken');
const db = require('../config/database');

const authenticateToken = async (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        
        // Verify user still exists and is active
        const user = await db.get(
            'SELECT id, username, email, full_name, department, profile_picture_url, is_active FROM users WHERE id = ? AND is_active = 1',
            [decoded.userId]
        );

        if (!user) {
            return res.status(401).json({ error: 'Invalid token - user not found' });
        }

        req.user = user;
        next();
    } catch (error) {
        if (error.name === 'TokenExpiredError') {
            return res.status(401).json({ error: 'Token expired' });
        }
        return res.status(403).json({ error: 'Invalid token' });
    }
};

const generateToken = (userId) => {
    return jwt.sign(
        { userId },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
    );
};

module.exports = {
    authenticateToken,
    generateToken
};
