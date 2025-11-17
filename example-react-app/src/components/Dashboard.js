import React, { useState, useEffect } from 'react';
import './Dashboard.css';

function Dashboard({ systemInfo }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchHealth = async () => {
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      setHealth(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch health:', error);
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="card-grid">
        <div className="card">
          <h2>💚 Health Status</h2>
          {loading ? (
            <div className="loading">Checking...</div>
          ) : health ? (
            <div className="status-box healthy">
              <div className="status-icon">✅</div>
              <div className="status-text">{health.status.toUpperCase()}</div>
              <div className="status-time">
                {new Date(health.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ) : (
            <div className="status-box error">
              <div className="status-icon">❌</div>
              <div className="status-text">UNHEALTHY</div>
            </div>
          )}
        </div>

        <div className="card">
          <h2>📋 System Information</h2>
          {systemInfo ? (
            <div className="info-list">
              <div className="info-item">
                <span className="label">Application:</span>
                <span className="value">{systemInfo.application}</span>
              </div>
              <div className="info-item">
                <span className="label">Version:</span>
                <span className="value">{systemInfo.version}</span>
              </div>
              <div className="info-item">
                <span className="label">Python:</span>
                <span className="value">{systemInfo.python_version}</span>
              </div>
              <div className="info-item">
                <span className="label">Platform:</span>
                <span className="value">{systemInfo.platform}</span>
              </div>
              <div className="info-item">
                <span className="label">Port:</span>
                <span className="value">{systemInfo.port}</span>
              </div>
            </div>
          ) : (
            <div className="loading">Loading...</div>
          )}
        </div>

        <div className="card full-width">
          <h2>🚀 Welcome to React Dashboard</h2>
          <p className="welcome-text">
            This is a modern React application deployed on AWS Lightsail using GitHub Actions.
            The app features real-time system monitoring, API testing capabilities, and a beautiful
            responsive design.
          </p>
          <div className="features">
            <div className="feature">
              <span className="feature-icon">⚡</span>
              <span>Real-time Metrics</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🧪</span>
              <span>API Testing</span>
            </div>
            <div className="feature">
              <span className="feature-icon">📱</span>
              <span>Responsive Design</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🔄</span>
              <span>Auto-refresh</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
