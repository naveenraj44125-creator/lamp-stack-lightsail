const express = require('express');
const cors = require('cors');
const os = require('os');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const START_TIME = new Date();

app.use(cors());
app.use(express.json());

// Health check endpoint (JSON for monitoring)
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// API endpoint
app.get('/api/info', (req, res) => {
  res.json({
    app: 'mcp-test-app',
    deployed: true,
    uptime: Math.floor((Date.now() - START_TIME.getTime()) / 1000),
    hostname: os.hostname(),
    platform: os.platform(),
    memory: {
      total: Math.round(os.totalmem() / 1024 / 1024) + ' MB',
      free: Math.round(os.freemem() / 1024 / 1024) + ' MB'
    }
  });
});

// Beautiful UI Dashboard
app.get('/', (req, res) => {
  const uptime = Math.floor((Date.now() - START_TIME.getTime()) / 1000);
  const hours = Math.floor(uptime / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  const seconds = uptime % 60;
  const uptimeStr = `${hours}h ${minutes}m ${seconds}s`;

  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MCP Deployment Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      min-height: 100vh;
      color: #fff;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px;
    }
    
    header {
      text-align: center;
      margin-bottom: 50px;
    }
    
    .logo {
      font-size: 3rem;
      margin-bottom: 10px;
    }
    
    h1 {
      font-size: 2.5rem;
      font-weight: 700;
      background: linear-gradient(90deg, #00d4ff, #7b2cbf);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
    }
    
    .subtitle {
      color: #8892b0;
      font-size: 1.1rem;
    }
    
    .status-banner {
      background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
      border: 1px solid rgba(0, 212, 255, 0.3);
      border-radius: 16px;
      padding: 20px 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 15px;
      margin-bottom: 40px;
    }
    
    .status-dot {
      width: 12px;
      height: 12px;
      background: #00ff88;
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
      50% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
    }
    
    .status-text {
      font-size: 1.2rem;
      font-weight: 600;
      color: #00ff88;
    }
    
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 25px;
      margin-bottom: 40px;
    }
    
    .card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 30px;
      transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .card-icon {
      font-size: 2.5rem;
      margin-bottom: 15px;
    }
    
    .card-title {
      font-size: 0.9rem;
      color: #8892b0;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }
    
    .card-value {
      font-size: 1.8rem;
      font-weight: 700;
    }
    
    .card-value.gradient {
      background: linear-gradient(90deg, #00d4ff, #7b2cbf);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .features {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 20px;
      padding: 40px;
      margin-bottom: 40px;
    }
    
    .features h2 {
      font-size: 1.5rem;
      margin-bottom: 25px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .feature-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
    }
    
    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 15px;
      background: rgba(0, 212, 255, 0.05);
      border-radius: 12px;
      border: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    .feature-icon {
      font-size: 1.5rem;
    }
    
    .feature-text {
      font-size: 0.95rem;
    }
    
    .endpoints {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 16px;
      padding: 30px;
      margin-bottom: 40px;
    }
    
    .endpoints h2 {
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .endpoint {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 15px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 10px;
      margin-bottom: 10px;
      font-family: 'Monaco', 'Menlo', monospace;
    }
    
    .method {
      background: #00d4ff;
      color: #1a1a2e;
      padding: 4px 12px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.8rem;
    }
    
    .path {
      color: #00ff88;
    }
    
    .desc {
      color: #8892b0;
      margin-left: auto;
      font-family: 'Inter', sans-serif;
    }
    
    footer {
      text-align: center;
      padding: 30px;
      color: #8892b0;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    footer a {
      color: #00d4ff;
      text-decoration: none;
    }
    
    .tech-stack {
      display: flex;
      justify-content: center;
      gap: 30px;
      margin-top: 20px;
      flex-wrap: wrap;
    }
    
    .tech-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 20px;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo">🚀</div>
      <h1>MCP Deployment Dashboard</h1>
      <p class="subtitle">Automated AWS Lightsail Deployment via GitHub Actions</p>
    </header>
    
    <div class="status-banner">
      <div class="status-dot"></div>
      <span class="status-text">All Systems Operational</span>
    </div>
    
    <div class="cards">
      <div class="card">
        <div class="card-icon">⏱️</div>
        <div class="card-title">Uptime</div>
        <div class="card-value gradient">${uptimeStr}</div>
      </div>
      
      <div class="card">
        <div class="card-icon">🖥️</div>
        <div class="card-title">Hostname</div>
        <div class="card-value">${os.hostname()}</div>
      </div>
      
      <div class="card">
        <div class="card-icon">💾</div>
        <div class="card-title">Memory</div>
        <div class="card-value">${Math.round(os.freemem() / 1024 / 1024)} MB free</div>
      </div>
      
      <div class="card">
        <div class="card-icon">🌍</div>
        <div class="card-title">Region</div>
        <div class="card-value gradient">us-east-1</div>
      </div>
    </div>
    
    <div class="features">
      <h2>✨ MCP Server Features</h2>
      <div class="feature-grid">
        <div class="feature-item">
          <span class="feature-icon">🔍</span>
          <span class="feature-text">Intelligent Project Analysis</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">⚙️</span>
          <span class="feature-text">Auto Config Generation</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">☁️</span>
          <span class="feature-text">AWS Lightsail Integration</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🔐</span>
          <span class="feature-text">GitHub OIDC Authentication</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🤖</span>
          <span class="feature-text">AI-Powered via Bedrock</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🛠️</span>
          <span class="feature-text">35+ Troubleshooting Scripts</span>
        </div>
      </div>
    </div>
    
    <div class="endpoints">
      <h2>🔗 API Endpoints</h2>
      <div class="endpoint">
        <span class="method">GET</span>
        <span class="path">/</span>
        <span class="desc">Dashboard UI</span>
      </div>
      <div class="endpoint">
        <span class="method">GET</span>
        <span class="path">/health</span>
        <span class="desc">Health check (JSON)</span>
      </div>
      <div class="endpoint">
        <span class="method">GET</span>
        <span class="path">/api/info</span>
        <span class="desc">System information</span>
      </div>
    </div>
    
    <footer>
      <p>Deployed with ❤️ using <a href="https://github.com/naveenraj44125-creator/mcp-lightsail-test-app">MCP Server Tools</a></p>
      <div class="tech-stack">
        <div class="tech-item">🟢 Node.js</div>
        <div class="tech-item">⚡ Express</div>
        <div class="tech-item">☁️ AWS Lightsail</div>
        <div class="tech-item">🔄 GitHub Actions</div>
      </div>
    </footer>
  </div>
  
  <script>
    // Auto-refresh uptime every second
    setInterval(() => {
      fetch('/api/info')
        .then(r => r.json())
        .then(data => {
          const h = Math.floor(data.uptime / 3600);
          const m = Math.floor((data.uptime % 3600) / 60);
          const s = data.uptime % 60;
          document.querySelector('.card-value.gradient').textContent = h + 'h ' + m + 'm ' + s + 's';
        });
    }, 1000);
  </script>
</body>
</html>
  `);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on http://0.0.0.0:${PORT}`);
});
