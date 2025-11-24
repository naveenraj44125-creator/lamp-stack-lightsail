// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Set build time
    const buildTime = new Date().toLocaleString();
    document.getElementById('buildTime').textContent = buildTime;
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add scroll animation
    observeElements();
});

// Show info modal
function showInfo() {
    alert('This is a static website deployed on AWS Lightsail using Nginx web server.\\n\\n' +
          'Features:\\n' +
          '• Automated deployment with GitHub Actions\\n' +
          '• OIDC authentication for secure AWS access\\n' +
          '• Fast content delivery with Nginx\\n' +
          '• Responsive design for all devices');
}

// Check server status
async function checkStatus() {
    const statusBox = document.getElementById('statusBox');
    const statusMessage = document.getElementById('statusMessage');
    
    statusMessage.innerHTML = '<div class="loading">Checking server status...</div>';
    
    // Simulate status check
    setTimeout(() => {
        const status = {
            server: 'Nginx',
            status: 'Running',
            uptime: Math.floor(Math.random() * 100) + ' hours',
            connections: Math.floor(Math.random() * 1000) + 100,
            requests: Math.floor(Math.random() * 10000) + 1000,
            deployment: 'GitHub Actions',
            lastDeploy: new Date().toLocaleString()
        };
        
        statusMessage.innerHTML = `
            <div class="status-grid">
                <div class="status-item">
                    <strong>Server:</strong> ${status.server}
                </div>
                <div class="status-item">
                    <strong>Status:</strong> <span class="status-badge success">${status.status}</span>
                </div>
                <div class="status-item">
                    <strong>Uptime:</strong> ${status.uptime}
                </div>
                <div class="status-item">
                    <strong>Active Connections:</strong> ${status.connections}
                </div>
                <div class="status-item">
                    <strong>Total Requests:</strong> ${status.requests}
                </div>
                <div class="status-item">
                    <strong>Deployment Method:</strong> ${status.deployment}
                </div>
                <div class="status-item">
                    <strong>Last Deploy:</strong> ${status.lastDeploy}
                </div>
            </div>
        `;
        
        // Add CSS for status display
        if (!document.getElementById('statusStyles')) {
            const style = document.createElement('style');
            style.id = 'statusStyles';
            style.textContent = `
                .loading {
                    text-align: center;
                    padding: 1rem;
                    color: #64748b;
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                    margin-top: 1rem;
                }
                .status-item {
                    padding: 0.75rem;
                    background: #f8fafc;
                    border-radius: 8px;
                }
                .status-badge {
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    font-size: 0.875rem;
                    font-weight: 600;
                }
                .status-badge.success {
                    background: #d1fae5;
                    color: #065f46;
                }
            `;
            document.head.appendChild(style);
        }
    }, 1000);
}

// Handle form submission
function handleSubmit(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;
    
    // Simulate form submission
    alert(`Thank you, ${name}!\\n\\nYour message has been received.\\n\\n` +
          `We'll respond to ${email} shortly.`);
    
    // Reset form
    event.target.reset();
}

// Observe elements for scroll animations
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s, transform 0.6s';
        observer.observe(card);
    });
}

// Add some interactivity to feature cards
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.background = 'linear-gradient(135deg, #f8fafc, #e2e8f0)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.background = '#f8fafc';
        });
    });
});
