const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const dbPath = process.env.DB_PATH || './database/employee_social.db';
const schemaPath = path.join(__dirname, 'schema.sql');

// Ensure database directory exists
const dbDir = path.dirname(dbPath);
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}

// Initialize database
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
        process.exit(1);
    }
    console.log('Connected to SQLite database.');
});

// Read and execute schema
const schema = fs.readFileSync(schemaPath, 'utf8');
const statements = schema.split(';').filter(stmt => stmt.trim());

db.serialize(() => {
    statements.forEach((statement, index) => {
        if (statement.trim()) {
            db.run(statement, (err) => {
                if (err) {
                    console.error(`Error executing statement ${index + 1}:`, err.message);
                } else {
                    console.log(`Statement ${index + 1} executed successfully.`);
                }
            });
        }
    });
});

db.close((err) => {
    if (err) {
        console.error('Error closing database:', err.message);
    } else {
        console.log('Database initialization completed. Connection closed.');
    }
});
