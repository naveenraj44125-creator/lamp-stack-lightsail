# 🚀 Enhanced Lightsail Deployment MCP Server

An intelligent Model Context Protocol (MCP) server that provides automated AWS Lightsail deployment with smart project analysis, cost optimization, and security assessment.

## ✨ Features

### 🔍 Intelligent Project Analysis
- **Automatic Application Type Detection**: Analyzes your codebase to detect Node.js, Python, PHP, React, Docker, or static applications
- **Framework Recognition**: Identifies Express, Flask, Laravel, React, Vue, Angular, and more
- **Database Requirements**: Detects MySQL, PostgreSQL, MongoDB usage patterns
- **Storage Needs**: Identifies file upload requirements and S3 bucket needs
- **Security Analysis**: Detects authentication, user data handling, and security requirements

### 💰 Cost Optimization
- **Right-Sizing**: Recommends optimal instance sizes based on application requirements
- **Database Optimization**: Suggests local vs RDS database configurations
- **Storage Optimization**: Optimizes S3 bucket configurations
- **Cost Estimation**: Provides accurate monthly cost estimates
- **Performance vs Cost**: Balances performance needs with budget constraints

### 🔒 Security Assessment
- **Compliance Support**: GDPR, HIPAA, SOC2, PCI-DSS compliance configurations
- **SSL/TLS Configuration**: Automatic HTTPS setup and certificate management
- **Firewall Rules**: Intelligent firewall configuration based on application needs
- **Data Protection**: Encryption at rest and in transit recommendations
- **File Upload Security**: Secure file handling and validation

### 🛠️ Infrastructure Automation
- **Smart Configuration Generation**: Creates optimized deployment configurations
- **GitHub Actions Workflows**: Generates CI/CD pipelines
- **Environment Variables**: Intelligent environment configuration
- **Monitoring Setup**: Built-in health checks and monitoring
- **Backup Configuration**: Automated backup strategies

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git
cd lamp-stack-lightsail/mcp-server-new

# Install dependencies
npm install

# Start the server
npm start

# Test the installation
npm test
```

## 🔗 Cline IDE Integration

For complete step-by-step instructions on using this MCP server with Cline IDE, see:

**📖 [CLINE-INTEGRATION-GUIDE.md](./CLINE-INTEGRATION-GUIDE.md)**

This comprehensive guide covers:
- ⚙️ Complete setup from scratch
- 🔧 Cline configuration and MCP setup
- 🛠️ All available tools and usage examples
- 🔍 Troubleshooting and debugging
- 🚀 Real-world deployment workflows
- 💡 Advanced usage patterns

### Usage with AI Assistants

The server provides several intelligent tools for AI assistants:

#### 1. Analyze Project Intelligently
```javascript
// Analyze a project directory or files
{
  "name": "analyze_project_intelligently",
  "arguments": {
    "project_path": "/path/to/your/project",
    "user_description": "A Node.js API with PostgreSQL database",
    "deployment_preferences": {
      "budget": "standard",
      "scale": "medium",
      "environment": "production"
    }
  }
}
```

#### 2. Generate Smart Deployment Config
```javascript
// Generate optimized deployment configuration
{
  "name": "generate_smart_deployment_config",
  "arguments": {
    "analysis_result": { /* result from analyze_project_intelligently */ },
    "app_name": "my-awesome-app",
    "aws_region": "us-east-1"
  }
}
```

#### 3. Complete Intelligent Setup
```javascript
// One-click intelligent deployment setup
{
  "name": "setup_intelligent_deployment",
  "arguments": {
    "project_path": "/path/to/project",
    "app_name": "my-app",
    "deployment_preferences": {
      "budget": "standard",
      "scale": "small",
      "aws_region": "us-east-1"
    },
    "github_config": {
      "username": "your-username",
      "repository": "your-repo",
      "visibility": "private"
    }
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Server Configuration
PORT=3000                    # Server port (default: 3000)
HOST=0.0.0.0                # Server host (default: 0.0.0.0)
MCP_AUTH_TOKEN=your-token   # Optional authentication token

# AWS Configuration (for deployment)
AWS_REGION=us-east-1        # Default AWS region
AWS_PROFILE=default         # AWS profile to use
```

### MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "enhanced-lightsail-deployment": {
      "command": "node",
      "args": ["/path/to/mcp-server-new/server.js"],
      "env": {
        "PORT": "3000"
      }
    }
  }
}
```

## 🎯 Supported Application Types

| Type | Frameworks | Databases | Features |
|------|------------|-----------|----------|
| **Node.js** | Express, Fastify, Koa | MySQL, PostgreSQL, MongoDB | API, WebSocket, Real-time |
| **Python** | Flask, Django | PostgreSQL, MySQL | API, ML, Data Processing |
| **PHP (LAMP)** | Laravel, Symfony, Plain PHP | MySQL, PostgreSQL | Web Apps, CMS, E-commerce |
| **React** | React, Vue, Angular, Next.js | Any (via API) | SPA, PWA, Static Sites |
| **Docker** | Any containerized app | Any | Microservices, Complex Apps |
| **Static** | HTML, CSS, JS | None | Landing Pages, Documentation |

## 💡 Intelligent Analysis Examples

### Node.js API Detection
```javascript
// Detects from package.json
{
  "detected_type": "nodejs",
  "confidence": 0.9,
  "frameworks": [
    { "name": "express", "type": "nodejs", "confidence": 0.8 }
  ],
  "databases": [
    { "name": "postgresql", "type": "postgresql", "confidence": 0.7 }
  ],
  "infrastructure_needs": {
    "bundle_size": "small_3_0",
    "memory_intensive": false,
    "cpu_intensive": false
  },
  "estimated_costs": {
    "monthly_min": 25,
    "monthly_max": 45
  }
}
```

### Docker Application Detection
```javascript
// Detects from Dockerfile and docker-compose.yml
{
  "detected_type": "docker",
  "confidence": 0.9,
  "deployment_complexity": "complex",
  "infrastructure_needs": {
    "bundle_size": "medium_3_0",  // Docker needs more resources
    "memory_intensive": true
  },
  "estimated_costs": {
    "monthly_min": 40,
    "monthly_max": 80
  }
}
```

## 🔒 Security Features

### Automatic Security Configuration
- **SSL/TLS**: Automatic HTTPS setup with Let's Encrypt
- **Firewall**: Intelligent port configuration based on application type
- **Authentication**: JWT and session security for user-facing applications
- **File Uploads**: Secure file handling with validation and S3 storage
- **Rate Limiting**: DDoS protection and API rate limiting

### Compliance Support
- **GDPR**: Data protection and privacy configurations
- **HIPAA**: Healthcare data security requirements
- **SOC2**: Security controls for service organizations
- **PCI-DSS**: Payment card industry security standards

## 💰 Cost Optimization

### Intelligent Right-Sizing
```javascript
// Optimization recommendations
{
  "recommended_bundle": "small_3_0",
  "cost_breakdown": {
    "instance": 10,
    "database": 15,
    "storage": 1,
    "total": 26
  },
  "optimizations": [
    {
      "type": "performance",
      "priority": "medium",
      "message": "Consider upgrading to medium bundle for better performance",
      "impact": "20% performance improvement"
    }
  ],
  "performance_score": 85,
  "cost_efficiency_score": 92
}
```

## 🛠️ API Reference

### Health Check
```bash
GET /health
```

Returns server status and capabilities.

### MCP Endpoint
```bash
POST /mcp
Content-Type: application/json
Authorization: Bearer <token>  # If AUTH_TOKEN is set
```

MCP protocol endpoint for tool execution.

## 🔧 Development

### Running in Development Mode
```bash
npm run dev  # Uses nodemon for auto-restart
```

### Project Structure
```
mcp-server-new/
├── server.js                 # Main server file
├── project-analyzer.js       # Intelligent project analysis
├── infrastructure-optimizer.js # Cost and performance optimization
├── configuration-generator.js # Smart config generation
├── package.json              # Dependencies and scripts
└── README.md                 # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues)
- **Discussions**: [GitHub Discussions](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/discussions)
- **Documentation**: [Project Wiki](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/wiki)

## 🎉 What's New in v2.0

- ✨ **Intelligent Project Analysis**: Automatic application type detection
- 💰 **Cost Optimization Engine**: Right-sizing and cost estimation
- 🔒 **Security Assessment**: Compliance and security configuration
- 🛠️ **Smart Configuration Generation**: Optimized deployment configs
- 📊 **Performance Scoring**: Performance vs cost analysis
- 🎯 **One-Click Setup**: Complete deployment automation

---

**Made with ❤️ for developers who want intelligent infrastructure automation**