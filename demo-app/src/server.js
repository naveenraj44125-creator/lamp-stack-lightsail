const express = require('express');
const os = require('os');

const app = express();
const PORT = process.env.PORT || 3000;
const START_TIME = new Date();

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/api/info', (req, res) => {
  const uptime = Math.floor((Date.now() - START_TIME.getTime()) / 1000);
  res.json({ uptime, hostname: os.hostname(), memory: Math.round(os.freemem() / 1024 / 1024) + ' MB' });
});

app.get('/', (req, res) => {
  const uptime = Math.floor((Date.now() - START_TIME.getTime()) / 1000);
  const h = Math.floor(uptime / 3600), m = Math.floor((uptime % 3600) / 60), s = uptime % 60;

  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MCP Demo Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }
    .container { text-align: center; padding: 40px; }
    .logo { font-size: 80px; margin-bottom: 20px; animation: bounce 2s infinite; }
    @keyframes bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-20px); }
    }
    h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 40px; }
    .status {
      background: rgba(255,255,255,0.2);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      padding: 30px 50px;
      display: inline-block;
      margin-bottom: 30px;
    }
    .status-dot {
      display: inline-block;
      width: 12px; height: 12px;
      background: #00ff88;
      border-radius: 50%;
      margin-right: 10px;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(0,255,136,0.4); }
      50% { box-shadow: 0 0 0 15px rgba(0,255,136,0); }
    }
    .cards { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-bottom: 40px; }
    .card {
      background: rgba(255,255,255,0.15);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 25px 35px;
      min-width: 150px;
    }
    .card-label { font-size: 0.8rem; opacity: 0.8; margin-bottom: 5px; }
    .card-value { font-size: 1.8rem; font-weight: 700; }
    .features {
      display: flex;
      gap: 15px;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 30px;
    }
    .feature {
      background: rgba(255,255,255,0.1);
      padding: 10px 20px;
      border-radius: 30px;
      font-size: 0.9rem;
    }
    footer { opacity: 0.7; font-size: 0.9rem; }
    footer a { color: #fff; }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">🚀</div>
    <h1>MCP Demo App</h1>
    <p class="subtitle">Deployed via GitHub Actions to AWS Lightsail</p>
    
    <div class="status">
      <span class="status-dot"></span>
      <span>All Systems Operational</span>
    </div>
    
    <div class="cards">
      <div class="card">
        <div class="card-label">UPTIME</div>
        <div class="card-value" id="uptime">${h}h ${m}m ${s}s</div>
      </div>
      <div class="card">
        <div class="card-label">HOST</div>
        <div class="card-value">${os.hostname().slice(0,8)}</div>
      </div>
      <div class="card">
        <div class="card-label">MEMORY</div>
        <div class="card-value">${Math.round(os.freemem()/1024/1024)}MB</div>
      </div>
    </div>
    
    <div class="features">
      <div class="feature">☁️ AWS Lightsail</div>
      <div class="feature">🔐 GitHub OIDC</div>
      <div class="feature">🤖 MCP Server</div>
      <div class="feature">⚡ Auto Deploy</div>
    </div>
    
    <footer>
      Built with ❤️ using <a href="#">MCP Deployment Tools</a>
    </footer>
  </div>
  <script>
    setInterval(() => {
      fetch('/api/info').then(r => r.json()).then(d => {
        const h = Math.floor(d.uptime/3600), m = Math.floor((d.uptime%3600)/60), s = d.uptime%60;
        document.getElementById('uptime').textContent = h+'h '+m+'m '+s+'s';
      });
    }, 1000);
  </script>
</body>
</html>`);
});

app.listen(PORT, '0.0.0.0', () => console.log('Server running on port ' + PORT));
