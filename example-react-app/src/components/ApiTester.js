import React, { useState } from 'react';
import './ApiTester.css';

function ApiTester() {
  const [endpoint, setEndpoint] = useState('/');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [echoInput, setEchoInput] = useState('{"message": "Hello from React!", "timestamp": "' + new Date().toISOString() + '"}');
  const [echoResponse, setEchoResponse] = useState('');

  const testEndpoint = async () => {
    setLoading(true);
    setResponse('');
    
    try {
      const res = await fetch(endpoint);
      const data = await res.json();
      setResponse(JSON.stringify(data, null, 2));
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testEcho = async () => {
    setLoading(true);
    setEchoResponse('');
    
    try {
      const jsonData = JSON.parse(echoInput);
      const res = await fetch('/api/echo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData)
      });
      const data = await res.json();
      setEchoResponse(JSON.stringify(data, null, 2));
    } catch (error) {
      setEchoResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-tester">
      <div className="tester-section">
        <div className="card">
          <h2>🧪 GET Request Tester</h2>
          <div className="form-group">
            <label>Select Endpoint:</label>
            <select 
              value={endpoint} 
              onChange={(e) => setEndpoint(e.target.value)}
              className="select-input"
            >
              <option value="/">Home</option>
              <option value="/api/health">Health Check</option>
              <option value="/api/info">App Info</option>
              <option value="/api/system">System Metrics</option>
            </select>
          </div>
          <button 
            onClick={testEndpoint} 
            disabled={loading}
            className="btn"
          >
            {loading ? 'Testing...' : 'Test Endpoint'}
          </button>
          {response && (
            <div className="response-box">
              <h4>Response:</h4>
              <pre>{response}</pre>
            </div>
          )}
        </div>
      </div>

      <div className="tester-section">
        <div className="card">
          <h2>📡 POST Request Tester (Echo)</h2>
          <div className="form-group">
            <label>JSON Payload:</label>
            <textarea
              value={echoInput}
              onChange={(e) => setEchoInput(e.target.value)}
              className="textarea-input"
              rows="6"
            />
          </div>
          <button 
            onClick={testEcho} 
            disabled={loading}
            className="btn"
          >
            {loading ? 'Sending...' : 'Send Echo Request'}
          </button>
          {echoResponse && (
            <div className="response-box">
              <h4>Response:</h4>
              <pre>{echoResponse}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ApiTester;
