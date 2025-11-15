const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Node.js Demo App</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          max-width: 800px;
          margin: 50px auto;
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }
        .container {
          background: rgba(255, 255, 255, 0.1);
          padding: 30px;
          border-radius: 10px;
          backdrop-filter: blur(10px);
        }
        h1 { margin-top: 0; }
        .info { background: rgba(255, 255, 255, 0.2); padding: 15px; border-radius: 5px; margin: 10px 0; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🚀 Node.js Express Application</h1>
        <p>Welcome to the Node.js demo application deployed on AWS Lightsail!</p>
        <div class="info">
          <strong>Environment:</strong> ${process.env.NODE_ENV || 'development'}<br>
          <strong>Node Version:</strong> ${process.version}<br>
          <strong>Port:</strong> ${port}
        </div>
        <h2>Available Endpoints:</h2>
        <ul>
          <li><a href="/api/health" style="color: #fff;">GET /api/health</a> - Health check</li>
          <li><a href="/api/info" style="color: #fff;">GET /api/info</a> - Application info</li>
        </ul>
      </div>
    </body>
    </html>
  `);
});

app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.get('/api/info', (req, res) => {
  res.json({
    name: 'Node.js Demo App',
    version: '1.0.0',
    node_version: process.version,
    environment: process.env.NODE_ENV || 'development',
    platform: process.platform,
    memory: process.memoryUsage()
  });
});

app.listen(port, () => {
  console.log(`✅ Server running on port ${port}`);
  console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
});
