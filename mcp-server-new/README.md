# 🚀 Enhanced Lightsail Deployment MCP Server

An intelligent Model Context Protocol (MCP) server that provides automated AWS Lightsail deployment with smart project analysis, cost optimization, security assessment, and **AI-powered assistance via AWS Bedrock**.

## ✨ Features

### 🤖 AI-Powered Analysis (AWS Bedrock)
- **Intelligent Code Analysis**: Uses Claude via Bedrock to understand your codebase
- **Smart Troubleshooting**: AI-powered error diagnosis and solutions
- **Expert Q&A**: Ask deployment questions and get expert answers
- **Config Review**: AI reviews your configs for security and optimization
- **Code Explanation**: Understand code from a deployment perspective

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
```

### Running the Server

The server supports two transport modes:

**Option 1: Stdio Mode (for Cline/MCP clients)**
```bash
# Run in stdio mode - for Cline integration
node server.js --stdio
```

**Option 2: HTTP/SSE Mode (for web clients and testing)**
```bash
# Run in HTTP mode - starts server on port 3001
npm start

# Or with custom port
PORT=3002 npm start

# Test the health endpoint
curl http://localhost:3001/health
```

### Test the Installation
```bash
npm test
```

## 🛠️ Available Tools

The MCP server provides 14 intelligent tools:

### Core Tools
| Tool | Description |
|------|-------------|
| `analyze_project_intelligently` | Analyze project to detect app type, frameworks, databases, and requirements |
| `generate_smart_deployment_config` | Generate optimized deployment configuration from analysis |
| `setup_intelligent_deployment` | Complete one-click deployment setup (combines analysis + config) |
| `optimize_infrastructure_costs` | Analyze and optimize infrastructure costs |
| `detect_security_requirements` | Analyze security requirements and generate configurations |
| `list_lightsail_instances` | List all Lightsail instances in a region |
| `check_deployment_status` | Check deployment health and status of an instance |
| `validate_deployment_config` | Validate deployment configuration for errors and warnings |

### AI-Powered Tools (AWS Bedrock)
| Tool | Description |
|------|-------------|
| `ai_analyze_project` | Use Claude AI to intelligently analyze project files |
| `ai_troubleshoot` | AI-powered error diagnosis and solutions |
| `ai_ask_expert` | Ask the AI deployment expert any question |
| `ai_review_config` | AI reviews config for security and optimization |
| `ai_explain_code` | AI explains code from deployment perspective |
| `ai_generate_config` | AI generates complete deployment configuration |

### Troubleshooting Tools
| Tool | Description |
|------|-------------|
| `list_troubleshooting_scripts` | List all available troubleshooting scripts by category |
| `run_troubleshooting_script` | Run a specific troubleshooting script on an instance |
| `diagnose_deployment_issue` | AI-powered diagnosis with automatic script recommendations |
| `get_instance_logs` | Retrieve logs from a Lightsail instance for troubleshooting |

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
      // Basic preferences
      "budget": "standard",           // minimal, standard, performance
      "scale": "small",               // small, medium, large
      "environment": "production",    // development, staging, production
      "aws_region": "us-east-1",
      
      // Database configuration
      "db_name": "app_db",            // Database name
      "db_rds_name": "my-app-db",     // RDS instance name (for external DB)
      
      // Bucket configuration
      "bucket_name": "my-app-bucket", // S3-compatible bucket name
      "bucket_access": "read_write",  // read_only, read_write
      "bucket_bundle": "small_1_0",   // Bucket size
      
      // API-only app configuration (for apps without root route)
      "api_only_app": false,          // Set true for API-only apps
      "verification_endpoint": "/api/health",  // Custom verification endpoint
      "health_check_endpoint": "/api/health",  // Custom health check endpoint
      "expected_content": "ok"        // Expected response content
    },
    "github_config": {
      "username": "your-username",
      "repository": "your-repo",
      "visibility": "private"
    }
  }
}
```

#### 4. List Lightsail Instances
```javascript
// List all instances in a region
{
  "name": "list_lightsail_instances",
  "arguments": {
    "aws_region": "us-east-1",
    "filter_by_name": "my-app",      // Optional: filter by name
    "include_stopped": true          // Include stopped instances
  }
}
```

#### 5. Check Deployment Status
```javascript
// Check health and status of a deployed instance
{
  "name": "check_deployment_status",
  "arguments": {
    "instance_name": "nodejs-my-app",
    "aws_region": "us-east-1",
    "health_check_endpoint": "/api/health",
    "health_check_port": 80,
    "expected_content": "ok"         // Optional: verify response content
  }
}
```

#### 6. Validate Deployment Config
```javascript
// Validate a deployment configuration
{
  "name": "validate_deployment_config",
  "arguments": {
    "config": {
      "aws": { "region": "us-east-1" },
      "lightsail": { "instance_name": "my-instance", "bundle_id": "micro_3_0" },
      "application": { "name": "my-app", "type": "nodejs" }
    },
    "strict_mode": false             // Fail on warnings if true
  }
}

// Or validate from file path
{
  "name": "validate_deployment_config",
  "arguments": {
    "config_path": "./deployment-nodejs.config.yml",
    "strict_mode": true
  }
}
```

### AI-Powered Tools (AWS Bedrock)

#### 7. AI Analyze Project
```javascript
// Use AI to analyze project files
{
  "name": "ai_analyze_project",
  "arguments": {
    "project_files": [
      { "path": "package.json", "content": "{...}" },
      { "path": "server.js", "content": "const express = require('express')..." }
    ],
    "user_description": "A Node.js API with MongoDB"
  }
}
```

#### 8. AI Troubleshoot
```javascript
// Get AI help with deployment errors
{
  "name": "ai_troubleshoot",
  "arguments": {
    "error_message": "Error: ECONNREFUSED 127.0.0.1:27017",
    "context": {
      "app_type": "nodejs",
      "instance_name": "my-api",
      "logs": "MongoDB connection failed..."
    }
  }
}
```

#### 9. AI Ask Expert
```javascript
// Ask the AI deployment expert
{
  "name": "ai_ask_expert",
  "arguments": {
    "question": "What's the best way to set up SSL for my Node.js app on Lightsail?",
    "project_context": {
      "app_type": "nodejs",
      "has_domain": true
    }
  }
}
```

#### 10. AI Review Config
```javascript
// Get AI to review your deployment config
{
  "name": "ai_review_config",
  "arguments": {
    "config": {
      "aws": { "region": "us-east-1" },
      "lightsail": { "instance_name": "my-app", "bundle_id": "micro_3_0" },
      "dependencies": {
        "mysql": { "enabled": true, "password": "password123" }
      }
    }
  }
}
```

#### 11. AI Explain Code
```javascript
// Get AI to explain code for deployment
{
  "name": "ai_explain_code",
  "arguments": {
    "code": "const mongoose = require('mongoose');\nmongoose.connect(process.env.MONGODB_URI);",
    "filename": "db.js"
  }
}
```

#### 12. AI Generate Config
```javascript
// Get AI to generate deployment config
{
  "name": "ai_generate_config",
  "arguments": {
    "analysis": {
      "detected_type": "nodejs",
      "databases": [{ "type": "mongodb" }],
      "frameworks": [{ "name": "express" }]
    },
    "preferences": {
      "budget": "standard",
      "scale": "small",
      "environment": "production"
    }
  }
}
```

### Troubleshooting Tools

#### 13. List Troubleshooting Scripts
```javascript
// List all available troubleshooting scripts
{
  "name": "list_troubleshooting_scripts",
  "arguments": {
    "category": "all"  // or: docker, general, lamp, nginx, nodejs, python, react
  }
}
```

#### 14. Run Troubleshooting Script
```javascript
// Run a specific troubleshooting script
{
  "name": "run_troubleshooting_script",
  "arguments": {
    "script_name": "debug-nodejs.py",
    "category": "nodejs",
    "instance_name": "my-nodejs-app",
    "aws_region": "us-east-1"
  }
}

// Run a fix script
{
  "name": "run_troubleshooting_script",
  "arguments": {
    "script_name": "fix-nginx.py",
    "category": "nginx",
    "instance_name": "my-web-server",
    "aws_region": "us-east-1"
  }
}
```

#### 15. Diagnose Deployment Issue
```javascript
// AI-powered diagnosis with automatic script recommendations
{
  "name": "diagnose_deployment_issue",
  "arguments": {
    "instance_name": "my-nodejs-app",
    "aws_region": "us-east-1",
    "error_description": "Getting 502 Bad Gateway error when accessing the application",
    "app_type": "nodejs",
    "logs": "Error: connect ECONNREFUSED 127.0.0.1:3000",
    "auto_fix": false  // Set to true to automatically run fix scripts
  }
}
```

#### 16. Get Instance Logs
```javascript
// Get application logs
{
  "name": "get_instance_logs",
  "arguments": {
    "instance_name": "my-nodejs-app",
    "aws_region": "us-east-1",
    "log_type": "application",  // application, system, nginx, apache, pm2, docker, all
    "lines": 100
  }
}

// Get all logs for comprehensive troubleshooting
{
  "name": "get_instance_logs",
  "arguments": {
    "instance_name": "my-web-server",
    "log_type": "all",
    "lines": 200
  }
}
```

### Troubleshooting Workflow Example

Here's a typical troubleshooting workflow using the MCP tools:

```javascript
// Step 1: Check deployment status
{
  "name": "check_deployment_status",
  "arguments": {
    "instance_name": "my-app",
    "health_check_endpoint": "/api/health"
  }
}

// Step 2: If unhealthy, get logs
{
  "name": "get_instance_logs",
  "arguments": {
    "instance_name": "my-app",
    "log_type": "all"
  }
}

// Step 3: Use AI to diagnose the issue
{
  "name": "diagnose_deployment_issue",
  "arguments": {
    "instance_name": "my-app",
    "error_description": "502 Bad Gateway",
    "app_type": "nodejs",
    "auto_fix": true  // Automatically run recommended fix scripts
  }
}

// Step 4: Verify the fix
{
  "name": "check_deployment_status",
  "arguments": {
    "instance_name": "my-app",
    "health_check_endpoint": "/api/health"
  }
}
```

### Deployment Preferences Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `budget` | string | `standard` | Budget tier: `minimal`, `standard`, `performance` |
| `scale` | string | `small` | Scale tier: `small`, `medium`, `large` |
| `environment` | string | `production` | Environment: `development`, `staging`, `production` |
| `aws_region` | string | `us-east-1` | AWS region for deployment |
| `db_name` | string | `app_db` | Database name |
| `db_rds_name` | string | auto | RDS instance name (for external databases) |
| `bucket_name` | string | auto | S3-compatible bucket name |
| `bucket_access` | string | `read_write` | Bucket access: `read_only`, `read_write` |
| `bucket_bundle` | string | `small_1_0` | Bucket bundle size |
| `api_only_app` | boolean | `false` | Set `true` for API-only apps without root route |
| `verification_endpoint` | string | `/` | Custom endpoint for deployment verification |
| `health_check_endpoint` | string | `/` | Custom health check endpoint |
| `expected_content` | string | auto | Expected content in health check response |

## 🔧 Configuration

### Environment Variables

```bash
# Server Configuration
PORT=3000                    # Server port (default: 3000)
HOST=0.0.0.0                # Server host (default: 0.0.0.0)
MCP_AUTH_TOKEN=your-token   # Optional authentication token

# AWS Configuration (for deployment and Bedrock)
AWS_REGION=us-east-1        # Default AWS region
AWS_PROFILE=default         # AWS profile to use

# Bedrock AI Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0  # Bedrock model ID
```

### AWS Bedrock Setup

To use AI-powered tools, you need:

1. **AWS Credentials**: Configure via one of these methods:
   - AWS profile in `~/.aws/credentials`
   - Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
   - Pass credentials directly to each AI tool call
2. **Bedrock Model Access**: Enable Claude models in AWS Bedrock console
3. **IAM Permissions**: Your IAM user/role needs `bedrock:InvokeModel` permission

#### Credential Options for AI Tools

All AI-powered tools (`ai_analyze_project`, `ai_troubleshoot`, `ai_ask_expert`, `ai_review_config`, `ai_explain_code`, `ai_generate_config`) accept an optional `aws_credentials` parameter:

```javascript
// Option 1: Use AWS profile from ~/.aws/credentials
{
  "name": "ai_troubleshoot",
  "arguments": {
    "error_message": "Connection refused",
    "aws_credentials": {
      "profile": "my-aws-profile",  // Profile name from ~/.aws/credentials
      "region": "us-east-1"         // Optional, defaults to us-east-1
    }
  }
}

// Option 2: Pass credentials directly
{
  "name": "ai_troubleshoot",
  "arguments": {
    "error_message": "Connection refused",
    "aws_credentials": {
      "access_key_id": "AKIAIOSFODNN7EXAMPLE",
      "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
      "session_token": "optional-session-token",  // For temporary credentials
      "region": "us-east-1"
    }
  }
}

// Option 3: Use default credential chain (env vars, IAM role, etc.)
{
  "name": "ai_troubleshoot",
  "arguments": {
    "error_message": "Connection refused"
    // No aws_credentials - uses default chain
  }
}
```

```bash
# Quick setup with AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1

# Or use a specific profile
export AWS_PROFILE=my-profile

# Test Bedrock access
node test-bedrock-ai.js
```

### Supported Bedrock Models

| Model | ID | Best For |
|-------|-----|----------|
| Claude 3 Sonnet | `anthropic.claude-3-sonnet-20240229-v1:0` | Default, balanced |
| Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | Fast, simple tasks |
| Claude 3 Opus | `anthropic.claude-3-opus-20240229-v1:0` | Complex analysis |

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

## � CTesting

### Unit Tests
```bash
# Run all unit tests
npm test

# Run specific test suites
node test-new-tools.js      # Test new tools and validation
node test-components.js     # Test MCP components
node test-bedrock-ai.js     # Test Bedrock AI integration
```

### End-to-End Deployment Test
The E2E test demonstrates the full deployment workflow:

```bash
# Dry run (no actual deployment)
node test-e2e-deployment.js --dry-run

# Skip deployment but test other steps
node test-e2e-deployment.js --skip-deploy

# Full deployment test (creates real resources)
node test-e2e-deployment.js

# Cleanup resources after testing
node test-e2e-deployment.js --cleanup
```

The E2E test:
1. Creates a simple Node.js test application
2. Analyzes it using MCP tools
3. Generates deployment configuration
4. Sets up GitHub repository and Actions
5. Deploys to AWS Lightsail
6. Verifies the application is working
7. Provides the application endpoint URL

**Prerequisites for E2E test:**
- AWS credentials configured (`source .aws-creds.sh`)
- GitHub CLI authenticated (`gh auth login`)
- Node.js 18+

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