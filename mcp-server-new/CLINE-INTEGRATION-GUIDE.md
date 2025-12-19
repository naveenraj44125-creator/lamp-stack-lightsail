# 🚀 Enhanced MCP Server - Cline Integration Guide

Complete guide for using the Enhanced Lightsail Deployment MCP Server with Cline IDE from start to finish.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Cline Configuration](#cline-configuration)
4. [Using the MCP Server](#using-the-mcp-server)
5. [Available Tools](#available-tools)
6. [Example Workflows](#example-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## 🔧 Prerequisites

### Required Software
- **Node.js** 18.0.0 or higher
- **npm** (comes with Node.js)
- **Cline IDE** with MCP support
- **Git** (for cloning repositories)

### AWS Requirements
- AWS account with Lightsail access
- AWS credentials configured (optional, for actual deployments)

---

## 📦 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/lamp-stack-lightsail.git
cd lamp-stack-lightsail/mcp-server-new
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Test the Installation
```bash
npm test
```

You should see:
```
🎉 All tests passed! Enhanced MCP Server is working perfectly!
```

### Step 4: Start the MCP Server
```bash
npm start
```

The server will start on `http://localhost:3001` with these endpoints:
- **Health Check**: `http://localhost:3001/health`
- **MCP Endpoint**: `http://localhost:3001/mcp`

---

## ⚙️ Cline Configuration

### Step 1: Open Cline Settings
1. Open Cline IDE
2. Go to **Settings** → **Extensions** → **MCP Configuration**
3. Or create/edit `.kiro/settings/mcp.json` in your workspace

### Step 2: Add MCP Server Configuration
Create or update your MCP configuration file:

```json
{
  "mcpServers": {
    "enhanced-lightsail-deployment": {
      "command": "node",
      "args": ["server.js"],
      "cwd": "./mcp-server-new",
      "env": {
        "PORT": "3001",
        "NODE_ENV": "development"
      },
      "disabled": false,
      "autoApprove": [
        "analyze_project_intelligently",
        "generate_smart_deployment_config",
        "optimize_infrastructure_costs",
        "detect_security_requirements"
      ]
    }
  }
}
```

### Step 3: Alternative HTTP Configuration
If you prefer to run the server separately:

```json
{
  "mcpServers": {
    "enhanced-lightsail-deployment": {
      "url": "http://localhost:3001/mcp",
      "disabled": false,
      "autoApprove": [
        "analyze_project_intelligently",
        "generate_smart_deployment_config",
        "setup_intelligent_deployment",
        "optimize_infrastructure_costs",
        "detect_security_requirements"
      ]
    }
  }
}
```

### Step 4: Restart Cline
Restart Cline IDE to load the new MCP server configuration.

---

## 🎯 Using the MCP Server

### Basic Usage in Cline

Once configured, you can use the MCP server directly in Cline chat:

#### 1. **Analyze Your Project**
```
@mcp analyze my project and tell me what type of application it is
```

#### 2. **Get Infrastructure Recommendations**
```
@mcp analyze my Node.js app and recommend the best AWS Lightsail configuration for a $50/month budget
```

#### 3. **Generate Deployment Configuration**
```
@mcp create a complete deployment configuration for my React app with database support
```

#### 4. **Setup Complete Deployment**
```
@mcp set up intelligent deployment for my project with GitHub Actions workflow
```

---

## 🛠️ Available Tools

### 1. `analyze_project_intelligently`
**Purpose**: Intelligent project analysis and type detection

**Parameters**:
- `project_path` (string): Path to your project directory
- `project_files` (array, optional): Specific files to analyze
- `user_description` (string, optional): Description of your project
- `deployment_preferences` (object, optional): Budget and scale preferences

**Example**:
```
Analyze my project at ./my-app and tell me what infrastructure it needs
```

### 2. `generate_smart_deployment_config`
**Purpose**: Generate intelligent deployment configurations

**Parameters**:
- `project_analysis` (string): Result from project analysis
- `app_name` (string): Name for your application
- `aws_region` (string, optional): AWS region (default: us-east-1)
- `deployment_preferences` (object, optional): Budget and performance preferences

**Example**:
```
Generate a deployment config for my Instagram clone app with medium performance requirements
```

### 3. `setup_intelligent_deployment`
**Purpose**: Complete deployment setup with files and workflows

**Parameters**:
- `project_path` (string): Path to your project
- `app_name` (string): Application name
- `deployment_config` (string): Generated deployment configuration
- `create_workflow` (boolean, optional): Create GitHub Actions workflow

**Example**:
```
Set up complete deployment for my app including GitHub Actions workflow
```

### 4. `optimize_infrastructure_costs`
**Purpose**: Optimize infrastructure costs and performance

**Parameters**:
- `current_config` (object): Current deployment configuration
- `usage_patterns` (object, optional): Expected traffic and usage
- `budget_constraints` (object, optional): Budget limits and priorities

**Example**:
```
Optimize my current deployment to reduce costs while maintaining performance
```

### 5. `detect_security_requirements`
**Purpose**: Analyze security requirements and generate configurations

**Parameters**:
- `project_analysis` (object): Project analysis result
- `compliance_requirements` (array, optional): GDPR, HIPAA, SOC2, PCI-DSS
- `data_sensitivity` (string, optional): public, internal, confidential, restricted

**Example**:
```
Analyze my app's security requirements for GDPR compliance
```

---

## 📝 Example Workflows

### Workflow 1: New Project Setup

1. **Start with project analysis**:
   ```
   @mcp I have a new Node.js project with Express and React. Can you analyze it and recommend the best deployment setup?
   ```

2. **Cline will**:
   - Analyze your project structure
   - Detect frameworks and dependencies
   - Recommend optimal infrastructure
   - Generate deployment configuration
   - Create GitHub Actions workflow

3. **Review and deploy**:
   ```
   @mcp The configuration looks good. Please create all the deployment files and set up the GitHub workflow.
   ```

### Workflow 2: Existing Project Optimization

1. **Analyze current setup**:
   ```
   @mcp I have an existing deployment that costs $80/month. Can you analyze it and suggest optimizations to reduce costs?
   ```

2. **Get recommendations**:
   ```
   @mcp Based on the analysis, what's the most cost-effective configuration that maintains good performance?
   ```

3. **Implement changes**:
   ```
   @mcp Please update my deployment configuration with the optimized settings.
   ```

### Workflow 3: Security Assessment

1. **Security analysis**:
   ```
   @mcp My app handles user data and needs to be GDPR compliant. Can you analyze the security requirements?
   ```

2. **Get security configuration**:
   ```
   @mcp Generate a secure deployment configuration with proper SSL, firewall, and data protection settings.
   ```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **MCP Server Not Starting**
```bash
# Check if port 3001 is available
lsof -ti:3001

# Kill any process using the port
kill -9 $(lsof -ti:3001)

# Restart the server
npm start
```

#### 2. **Cline Can't Connect to MCP Server**
- Verify the server is running: `curl http://localhost:3001/health`
- Check Cline MCP configuration
- Restart Cline IDE
- Check firewall settings

#### 3. **Tool Not Found Errors**
- Verify MCP server is properly configured in Cline
- Check the `autoApprove` list in your MCP configuration
- Restart both the MCP server and Cline

#### 4. **Analysis Errors**
```bash
# Test components directly
cd mcp-server-new
npm run test:components
```

### Debug Mode

Enable debug logging:
```bash
# Set environment variable
export DEBUG=mcp:*

# Start server with debug info
npm start
```

### Health Check

Always verify server health:
```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "features": ["intelligent-analysis", "cost-optimization", "security-assessment"]
}
```

---

## 🚀 Advanced Usage

### Custom Project Analysis

For complex projects, provide detailed context:

```
@mcp I have a microservices architecture with:
- 3 Node.js APIs
- 1 React frontend
- PostgreSQL database
- Redis cache
- File uploads to S3

Please analyze this and recommend the optimal Lightsail setup with proper scaling and security.
```

### Multi-Environment Setup

Configure different environments:

```
@mcp Set up deployment configurations for:
1. Development environment (cost-optimized)
2. Staging environment (production-like)
3. Production environment (performance-optimized)
```

### Integration with Existing CI/CD

```
@mcp I already have a Jenkins pipeline. Can you generate deployment configurations that work with my existing CI/CD setup?
```

### Cost Optimization Strategies

```
@mcp My current AWS bill is $200/month. Analyze my deployment and suggest ways to reduce costs by 40% while maintaining performance.
```

---

## 📊 Performance Tips

### 1. **Optimize Analysis Speed**
- Keep project directories clean
- Use `.gitignore` to exclude unnecessary files
- Provide specific file lists for large projects

### 2. **Efficient Configuration Generation**
- Cache analysis results for similar projects
- Use deployment preferences to guide recommendations
- Specify exact requirements upfront

### 3. **Better Recommendations**
- Provide accurate traffic estimates
- Specify compliance requirements early
- Include performance requirements in initial analysis

---

## 🔗 Integration Examples

### With GitHub Actions
The MCP server automatically generates GitHub Actions workflows that integrate with your existing repository structure.

### With AWS CLI
Generated configurations work seamlessly with AWS CLI and Terraform.

### With Docker
Supports Docker-based applications with intelligent container optimization.

---

## 📞 Support

### Getting Help
1. **Check the logs**: `npm start` shows detailed logging
2. **Run tests**: `npm test` verifies everything is working
3. **Health check**: `curl http://localhost:3001/health`
4. **Debug mode**: Set `DEBUG=mcp:*` environment variable

### Common Commands
```bash
# Start server
npm start

# Run all tests
npm test

# Test components only
npm run test:components

# Test MCP client
npm run test:client

# Development mode with auto-restart
npm run dev
```

---

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ **Server starts successfully** on port 3001
2. ✅ **Health check returns healthy status**
3. ✅ **All tests pass** (2/2 tests)
4. ✅ **Cline can connect** to the MCP server
5. ✅ **Tools are available** in Cline chat
6. ✅ **Analysis produces accurate results**
7. ✅ **Configurations are generated successfully**

---

**🚀 You're now ready to use the Enhanced MCP Server with Cline for intelligent AWS Lightsail deployments!**

The server provides intelligent project analysis, cost optimization, and complete deployment automation - making your infrastructure setup as simple as a conversation with Cline.