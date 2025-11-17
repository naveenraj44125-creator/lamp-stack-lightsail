import React, { useState, useEffect } from 'react';
import './SystemMetrics.css';

function SystemMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/system');
      const data = await response.json();
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading metrics...</div>;
  }

  if (!metrics) {
    return <div className="error">Failed to load metrics</div>;
  }

  return (
    <div className="system-metrics">
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>💻 CPU Usage</h3>
          <div className="metric-value">{metrics.cpu.percent}%</div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${metrics.cpu.percent}%` }}
            />
          </div>
          <div className="metric-detail">
            {metrics.cpu.count} cores available
          </div>
        </div>

        <div className="metric-card">
          <h3>🧠 Memory Usage</h3>
          <div className="metric-value">{metrics.memory.percent}%</div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${metrics.memory.percent}%` }}
            />
          </div>
          <div className="metric-detail">
            {metrics.memory.available} available of {metrics.memory.total}
          </div>
        </div>

        <div className="metric-card">
          <h3>💾 Disk Usage</h3>
          <div className="metric-value">{metrics.disk.percent}%</div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${metrics.disk.percent}%` }}
            />
          </div>
          <div className="metric-detail">
            {metrics.disk.free} free of {metrics.disk.total}
          </div>
        </div>
      </div>

      <div className="refresh-info">
        <span>🔄 Auto-refreshing every 3 seconds</span>
      </div>
    </div>
  );
}

export default SystemMetrics;
