import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import ApiTester from './components/ApiTester';
import SystemMetrics from './components/SystemMetrics';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemInfo, setSystemInfo] = useState(null);

  useEffect(() => {
    // Fetch system info on mount
    fetchSystemInfo();
  }, []);

  const fetchSystemInfo = async () => {
    try {
      const response = await fetch('/api/info');
      const data = await response.json();
      setSystemInfo(data);
    } catch (error) {
      console.error('Failed to fetch system info:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>⚛️ React Dashboard</h1>
        <p className="subtitle">Deployed on AWS Lightsail with GitHub Actions</p>
      </header>

      <nav className="nav-tabs">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={activeTab === 'metrics' ? 'active' : ''}
          onClick={() => setActiveTab('metrics')}
        >
          ⚡ Metrics
        </button>
        <button 
          className={activeTab === 'api' ? 'active' : ''}
          onClick={() => setActiveTab('api')}
        >
          🧪 API Tester
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && <Dashboard systemInfo={systemInfo} />}
        {activeTab === 'metrics' && <SystemMetrics />}
        {activeTab === 'api' && <ApiTester />}
      </main>

      <footer className="App-footer">
        <p>Version: 1.0.1 | Built with React 18</p>
        <p>Powered by AWS Lightsail & GitHub Actions CI/CD</p>
      </footer>
    </div>
  );
}

export default App;
