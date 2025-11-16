// Auto-refresh data every 5 seconds
let autoRefresh = true;

// Load all data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSystemInfo();
    loadHealthStatus();
    loadPerformanceMetrics();
    
    // Auto-refresh every 5 seconds
    setInterval(() => {
        if (autoRefresh) {
            loadHealthStatus();
            loadPerformanceMetrics();
        }
    }, 5000);
});

// Load system information
async function loadSystemInfo() {
    try {
        const response = await fetch('/api/info');
        const data = await response.json();
        
        const html = `
            <div class="info-item">
                <span class="info-label">Application:</span>
                <span class="info-value">${data.application}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Version:</span>
                <span class="info-value">${data.version}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Python:</span>
                <span class="info-value">${data.python_version}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Platform:</span>
                <span class="info-value">${data.platform}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Port:</span>
                <span class="info-value">${data.port}</span>
            </div>
        `;
        
        document.getElementById('system-info').innerHTML = html;
    } catch (error) {
        document.getElementById('system-info').innerHTML = 
            '<div class="error">Failed to load system info</div>';
    }
}

// Load health status
async function loadHealthStatus() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        const statusBox = document.getElementById('health-status');
        statusBox.className = 'status-box status-healthy';
        statusBox.innerHTML = `
            ✅ ${data.status.toUpperCase()}<br>
            <small style="font-size: 0.8rem; opacity: 0.8;">
                Last checked: ${new Date(data.timestamp).toLocaleTimeString()}
            </small>
        `;
    } catch (error) {
        const statusBox = document.getElementById('health-status');
        statusBox.className = 'status-box status-error';
        statusBox.innerHTML = '❌ UNHEALTHY';
    }
}

// Load performance metrics
async function loadPerformanceMetrics() {
    try {
        const response = await fetch('/api/system');
        const data = await response.json();
        
        const html = `
            <div class="metric-item">
                <div class="metric-label">CPU Usage</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${data.cpu.percent}%">
                        ${data.cpu.percent}% (${data.cpu.count} cores)
                    </div>
                </div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Memory Usage</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${data.memory.percent}%">
                        ${data.memory.percent}% (${data.memory.available} available)
                    </div>
                </div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Disk Usage</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${data.disk.percent}%">
                        ${data.disk.percent}% (${data.disk.free} free)
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('performance-metrics').innerHTML = html;
    } catch (error) {
        document.getElementById('performance-metrics').innerHTML = 
            '<div class="error">Failed to load metrics</div>';
    }
}

// Test API endpoint
async function testEndpoint() {
    const endpoint = document.getElementById('endpoint-select').value;
    const responseBox = document.getElementById('api-response');
    
    responseBox.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        
        responseBox.innerHTML = JSON.stringify(data, null, 2);
        responseBox.style.color = '#28a745';
    } catch (error) {
        responseBox.innerHTML = `Error: ${error.message}`;
        responseBox.style.color = '#dc3545';
    }
}

// Test echo endpoint
async function testEcho() {
    const input = document.getElementById('echo-input').value;
    const responseBox = document.getElementById('echo-response');
    
    responseBox.innerHTML = '<div class="loading">Sending...</div>';
    
    try {
        let jsonData;
        try {
            jsonData = JSON.parse(input || '{}');
        } catch (e) {
            throw new Error('Invalid JSON format');
        }
        
        const response = await fetch('/api/echo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData)
        });
        
        const data = await response.json();
        responseBox.innerHTML = JSON.stringify(data, null, 2);
        responseBox.style.color = '#28a745';
    } catch (error) {
        responseBox.innerHTML = `Error: ${error.message}`;
        responseBox.style.color = '#dc3545';
    }
}
