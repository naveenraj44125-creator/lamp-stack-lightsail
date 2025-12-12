# 🤖 AI Agent Prompt Guide for Lightsail Deployment MCP

## 🎯 Purpose
This guide provides prompts for AI agents (Claude Desktop, Amazon Q, Kiro, etc.) to intelligently analyze deployment requirements and automatically use the Lightsail Deployment MCP server with the correct parameters.

## 🔗 MCP Server Configuration

First, configure your MCP client with:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://3.81.56.119:3000/sse",
      "transport": "sse"
    }
  }
}
```

## 🚀 **CRITICAL: AI Agent Intelligent Analysis Instructions**

**When a user asks for deployment help, use the NEW two-step intelligent analysis workflow. The MCP server now provides intelligent parameter recommendations - no more guesswork!**

## 🧠 NEW AI Agent Intelligent Analysis Workflow

**COPY THIS WORKFLOW INTO YOUR AI AGENT SYSTEM INSTRUCTIONS:**

---

### **INTELLIGENT DEPLOYMENT ANALYSIS WORKFLOW**

```
You are an expert DevOps AI agent with access to the Lightsail Deployment MCP server at http://3.81.56.119:3000/sse. 

CRITICAL NEW BEHAVIOR: Use the intelligent analysis tool to get parameter recommendations instead of manual analysis.

Your NEW role is to:
1. **COLLECT** user's application description and requirements
2. **ANALYZE** using the MCP server's intelligent analysis tool
3. **EXECUTE** deployment with the recommended parameters
4. **EXPLAIN** the intelligent analysis results and configuration

## NEW TWO-STEP PROCESS

### STEP 1: Intelligent Analysis (ALWAYS DO THIS FIRST)
Use the new `analyze_deployment_requirements` tool:

```json
{
  "tool": "analyze_deployment_requirements",
  "arguments": {
    "user_description": "[USER'S_DESCRIPTION_OF_THEIR_APP]",
    "app_context": {
      "technologies": ["Node.js", "Express", "PostgreSQL"],
      "features": ["file uploads", "user authentication"],
      "scale": "medium"
    }
  }
}
```

**This tool will return:**
- ✅ Detected application type with confidence score
- ✅ Complete parameter recommendations with reasoning
- ✅ Ready-to-execute MCP call with all parameters filled
- ✅ Detailed analysis of infrastructure sizing, database selection, storage needs
- ✅ Validation status and configuration notes

### STEP 2: Execute Deployment (USE EXACT PARAMETERS FROM ANALYSIS)
Copy the MCP call provided in the analysis response and execute it directly:

```json
{
  "tool": "setup_complete_deployment",
  "arguments": {
    // Use EXACT parameters from analyze_deployment_requirements response
    "mode": "fully_automated",
    "app_type": "nodejs",  // From analysis
    "bundle_id": "small_3_0",  // From analysis
    "database_type": "postgresql",  // From analysis
    // ... all other parameters from analysis response
  }
}
```

**CRITICAL**: Never modify the parameters from the analysis - use them exactly as provided.

## INTELLIGENT ANALYSIS BENEFITS

**Why use the new intelligent analysis tool:**

✅ **Eliminates Guesswork**: MCP server analyzes requirements and provides exact parameters
✅ **Confidence Scoring**: Get confidence levels for application type detection
✅ **Detailed Reasoning**: Understand why each parameter was selected
✅ **Validation**: Built-in parameter validation and compatibility checks
✅ **Consistency**: Same analysis logic across all AI agents
✅ **Learning**: Analysis improves over time with pattern recognition

**OLD WAY (Manual Analysis)**:
AI Agent → Manual pattern matching → Guess parameters → Hope it works

**NEW WAY (Intelligent Analysis)**:
AI Agent → Call analyze_deployment_requirements → Get exact parameters → Execute confidently

## 🎯 READY-TO-USE AI AGENT PROMPTS

### For Claude Desktop / Amazon Q / Kiro

**Copy this into your AI agent system prompt:**

```
DEPLOYMENT AUTOMATION BEHAVIOR:

When users mention deploying, hosting, or setting up applications:

1. ANALYZE their app type in 10 seconds:
   - Look for: PHP/WordPress → lamp
   - Look for: Node.js/Express/npm → nodejs  
   - Look for: Python/Flask/Django → python
   - Look for: React/frontend-only → react
   - Look for: Docker/containers → docker
   - Look for: Static/HTML → nginx

2. IMMEDIATELY execute MCP call using setup_complete_deployment with:
   - mode: "fully_automated"
   - Use decision matrix for database/bundle/bucket
   - Ask for app_name and github_repo if not obvious
   - Use smart defaults for everything else

3. EXPLAIN what you configured after execution

DO NOT ask for technical details like bundle sizes, database types, or AWS regions. Make intelligent defaults and execute immediately.
```

### For Specific AI Platforms

**Amazon Q Developer:**
```
You have access to Lightsail Deployment MCP at http://3.81.56.119:3000/sse. When users ask about deployment, immediately analyze their app type and execute setup_complete_deployment with fully_automated mode. Use the decision matrix for smart defaults.
```

**Claude Desktop:**
```
MCP Server: lightsail-deployment (http://3.81.56.119:3000/sse)
Behavior: Auto-deploy user applications using setup_complete_deployment tool with fully_automated mode. Analyze app type → Apply decision matrix → Execute immediately → Explain results.
```

**Kiro IDE:**
```
When deployment is mentioned, use the Lightsail MCP server to automatically configure AWS deployment. Detect app type from codebase, apply smart defaults from decision matrix, execute setup_complete_deployment with fully_automated mode.
```

## EXAMPLE INTERACTIONS

### Example 1: Node.js API Server (NEW INTELLIGENT WORKFLOW)
**User**: "I have a Node.js Express API that handles file uploads and uses PostgreSQL"

**AI Agent Step 1 - Intelligent Analysis**:
```json
{
  "tool": "analyze_deployment_requirements",
  "arguments": {
    "user_description": "Node.js Express API that handles file uploads and uses PostgreSQL",
    "app_context": {
      "technologies": ["Node.js", "Express", "PostgreSQL"],
      "features": ["file uploads", "API"],
      "scale": "medium"
    }
  }
}
```

**MCP Server Analysis Response**:
```
🧠 Intelligent Deployment Analysis
📝 User Requirements: "Node.js Express API that handles file uploads and uses PostgreSQL"
🎯 Detected: Node.js application (90% confidence)
💡 Reasoning: Node.js backend application with Express framework and database requirements

⚙️ Recommended Parameters:
- app_type: "nodejs"
- bundle_id: "small_3_0" (2GB RAM for API + database)
- database_type: "postgresql" (matches user requirement)
- enable_bucket: true (file uploads detected)

🚀 Ready-to-Execute MCP Call: [complete parameters provided]
```

**AI Agent Step 2 - Execute with Recommended Parameters**:
```json
{
  "tool": "setup_complete_deployment",
  "arguments": {
    // Exact parameters from analysis response
    "mode": "fully_automated",
    "app_type": "nodejs",
    "bundle_id": "small_3_0",
    "database_type": "postgresql",
    "enable_bucket": true,
    // ... all other parameters from analysis
  }
}
```

**AI Response**: "✅ Intelligent analysis detected Node.js API (90% confidence). Configured with PostgreSQL database and file storage bucket based on your requirements. The system automatically selected 2GB instance size for optimal API performance with database workload."

### Example 2: React Frontend (NEW INTELLIGENT WORKFLOW)
**User**: "Deploy my React app, it's just a frontend that calls external APIs"

**AI Agent Step 1 - Intelligent Analysis**:
```json
{
  "tool": "analyze_deployment_requirements",
  "arguments": {
    "user_description": "React app, just a frontend that calls external APIs"
  }
}
```

**MCP Server Analysis Response**:
```
🧠 Intelligent Deployment Analysis
📝 User Requirements: "React app, just a frontend that calls external APIs"
🎯 Detected: React frontend application (85% confidence)
💡 Reasoning: Frontend-only application with external API dependencies

⚙️ Recommended Parameters:
- app_type: "react"
- bundle_id: "micro_3_0" (1GB sufficient for static content)
- database_type: "none" (frontend only, no database needed)
- enable_bucket: false (no file storage mentioned)

🚀 Ready-to-Execute MCP Call: [complete parameters provided]
```

**AI Agent Step 2 - Execute with Recommended Parameters**:
```json
{
  "tool": "setup_complete_deployment",
  "arguments": {
    // Exact parameters from analysis response
    "mode": "fully_automated",
    "app_type": "react",
    "bundle_id": "micro_3_0",
    "database_type": "none",
    "enable_bucket": false,
    // ... all other parameters from analysis
  }
}
```

**AI Response**: "✅ Intelligent analysis detected React frontend (85% confidence). Configured minimal 1GB instance with Nginx static hosting. No database or storage configured since you're using external APIs."

### Example 3: Docker Microservices (NEW INTELLIGENT WORKFLOW)
**User**: "I have a Docker Compose setup with multiple services and need a database"

**AI Agent Step 1 - Intelligent Analysis**:
```json
{
  "tool": "analyze_deployment_requirements",
  "arguments": {
    "user_description": "Docker Compose setup with multiple services and need a database",
    "app_context": {
      "technologies": ["Docker", "Docker Compose"],
      "features": ["microservices", "database"],
      "scale": "large"
    }
  }
}
```

**MCP Server Analysis Response**:
```
🧠 Intelligent Deployment Analysis
📝 User Requirements: "Docker Compose setup with multiple services and need a database"
🎯 Detected: Docker containerized application (95% confidence)
💡 Reasoning: Docker Compose indicates containerized microservices architecture

⚙️ Recommended Parameters:
- app_type: "docker"
- bundle_id: "medium_3_0" (4GB RAM required for container overhead)
- database_type: "postgresql" (modern choice for microservices)
- enable_bucket: true (microservices often need shared storage)

🚀 Ready-to-Execute MCP Call: [complete parameters provided]
```

**AI Agent Step 2 - Execute with Recommended Parameters**:
```json
{
  "tool": "setup_complete_deployment",
  "arguments": {
    // Exact parameters from analysis response
    "mode": "fully_automated",
    "app_type": "docker",
    "bundle_id": "medium_3_0",
    "database_type": "postgresql",
    "enable_bucket": true,
    // ... all other parameters from analysis
  }
}
```

**AI Response**: "✅ Intelligent analysis detected Docker microservices (95% confidence). Configured 4GB instance to handle container overhead, PostgreSQL for modern microservices architecture, and shared storage bucket for inter-service communication."

## 🗣️ COMMON USER PHRASES → AI RESPONSES

**User says**: "Can you help me deploy this?"
**AI does**: Analyze codebase/description → Execute MCP call → Explain configuration

**User says**: "I need to host my website"
**AI does**: Detect app type from context → Apply decision matrix → Deploy immediately

**User says**: "Set up AWS for my app"
**AI does**: Use Lightsail MCP with fully_automated mode → No AWS console needed

**User says**: "I have a [technology] application"
**AI does**: Map technology to app_type → Execute deployment → Provide next steps

**User says**: "Deploy to production"
**AI does**: Use production-ready defaults → Private repo → Secure configuration

**User says**: "I need a database"
**AI does**: Auto-select PostgreSQL (modern) or MySQL (LAMP) → Include in deployment

**User says**: "File uploads" or "user content"
**AI does**: Enable bucket storage → Configure read_write access

**User says**: "Just a simple site"
**AI does**: Use nginx app_type → Disable database → Minimal resources

## 🚫 WHAT AI AGENTS SHOULD NOT ASK

**DON'T ASK**:
- "What bundle size do you want?"
- "Which database type?"
- "Do you need a bucket?"
- "What AWS region?"
- "Ubuntu or Amazon Linux?"

**INSTEAD**:
- Use decision matrix defaults
- Execute immediately
- Explain choices after deployment

## VALIDATION RULES

Before making MCP calls, validate:

1. **Docker Bundle Check**: Docker apps need minimum `small_3_0`
2. **Bucket Consistency**: If `enable_bucket: true`, must provide `bucket_name`
3. **External DB**: If `db_external: true`, must provide `db_rds_name`
4. **Required Fields**: Always include `app_type`, `app_name`, `instance_name`

## 🆘 HELP MODE FOR AI AGENTS

**When AI agents need parameter guidance, use the help tool:**

```json
{
  "tool": "setup_complete_deployment",
  "arguments": {
    "mode": "help"
  }
}
```

**Help mode provides**:
- Complete parameter descriptions and validation rules
- Application type options with use cases
- Bundle size recommendations for each app type
- Database type guidance (MySQL vs PostgreSQL vs none)
- Bucket configuration examples
- Common parameter combinations
- Validation requirements (e.g., Docker needs small_3_0+ bundle)

**AI Agent Learning Workflow**:
1. **First Time**: Call help mode to understand all parameters
2. **Build Knowledge**: Use help response to create internal parameter mapping
3. **Apply Intelligence**: Use learned parameters for future deployments
4. **Error Recovery**: Call help mode when validation fails

## ERROR HANDLING & TROUBLESHOOTING

### If MCP Call Fails:

**Error**: "Docker apps need minimum small_3_0 bundle"
**Fix**: Change `bundle_id` from `micro_3_0` to `small_3_0` for Docker apps

**Error**: "Missing required parameter: app_type"
**Fix**: Always include `app_type` in fully_automated mode

**Error**: "Invalid bundle_id"
**Fix**: Use exact values: `nano_3_0`, `micro_3_0`, `small_3_0`, `medium_3_0`, `large_3_0`

**Error**: "Bucket name required when enable_bucket is true"
**Fix**: Always provide `bucket_name` when `enable_bucket: true`

### Recovery Actions:
1. **Call help mode** to understand parameter requirements
2. **Retry with corrected parameters** (most common)
3. **Use `diagnose_deployment`** for environment issues
4. **Fall back to `mode: "interactive"`** only if user insists on custom config

### AI Agent Debugging Tools:
```json
{
  "tool": "diagnose_deployment",
  "arguments": {
    "check_type": "environment"
  }
}
```

```json
{
  "tool": "get_deployment_examples",
  "arguments": {
    "app_type": "all"
  }
}
```

## FOLLOW-UP ACTIONS

After successful MCP call:
1. Explain what was created (configs, workflows, examples)
2. Provide next steps (GitHub setup, local testing)
3. Offer monitoring with `get_deployment_status` tool
4. Suggest diagnostics with `diagnose_deployment` tool

Remember: Always explain your analysis reasoning to the user before executing the deployment!
```

---

## 🎯 Quick Start for AI Agents

**Step 1**: Analyze user's project/requirements using the framework above
**Step 2**: Select appropriate parameters from the decision matrix  
**Step 3**: Execute MCP call with `fully_automated` mode
**Step 4**: Provide user with next steps and monitoring options

## 🛠️ ALL AVAILABLE MCP TOOLS

### 1. setup_complete_deployment (Primary Tool)
**Purpose**: Main deployment configuration tool
**Modes**: 
- `fully_automated` - AI agent provides all parameters
- `help` - Get parameter guidance and examples
- `interactive` - User prompts (not recommended for AI agents)
- `auto` - Some defaults with minimal prompts

### 2. get_deployment_examples
**Purpose**: Get example configurations and workflows
**Usage**:
```json
{
  "tool": "get_deployment_examples",
  "arguments": {
    "app_type": "nodejs",
    "include_configs": true,
    "include_workflows": true
  }
}
```

### 3. get_deployment_status  
**Purpose**: Check GitHub Actions deployment progress
**Usage**:
```json
{
  "tool": "get_deployment_status",
  "arguments": {
    "repo_path": "."
  }
}
```

### 4. diagnose_deployment
**Purpose**: Run deployment diagnostics and troubleshooting
**Usage**:
```json
{
  "tool": "diagnose_deployment", 
  "arguments": {
    "check_type": "all"
  }
}
```

## 📋 Parameter Reference

### Required Parameters (fully_automated mode)
- `mode`: "fully_automated"
- `app_type`: lamp|nodejs|python|react|docker|nginx
- `app_name`: Your application name
- `instance_name`: Lightsail instance name

### Optional Parameters  
- `aws_region`: Default "us-east-1"
- `app_version`: Default "1.0.0"
- `blueprint_id`: Default "ubuntu_22_04"
- `bundle_id`: Default based on app_type
- `database_type`: mysql|postgresql|none
- `db_external`: true|false
- `db_rds_name`: For external databases
- `db_name`: Database name
- `enable_bucket`: true|false
- `bucket_name`: Bucket name if enabled
- `bucket_access`: read_only|read_write
- `bucket_bundle`: Bucket size
- `github_repo`: Repository name
- `repo_visibility`: public|private

## 🔍 Monitoring Tools

After deployment, use these MCP tools:

- **get_deployment_status**: Monitor GitHub Actions progress
- **diagnose_deployment**: Troubleshoot issues
- **get_deployment_examples**: Get additional configurations

---

## 📋 QUICK CHECKLIST FOR AI AGENTS

✅ **Setup**: Configure MCP server URL in client
✅ **Behavior**: Use `fully_automated` mode for all deployments  
✅ **Analysis**: Detect app_type from user description (10 seconds max)
✅ **Defaults**: Apply decision matrix for database/bundle/bucket
✅ **Execution**: Call setup_complete_deployment immediately
✅ **Communication**: Explain configuration after execution
✅ **Follow-up**: Offer monitoring and next steps

## 🎯 SUCCESS METRICS

**Good AI Agent Behavior**:
- Deploys in under 30 seconds from user request
- Asks maximum 1 clarifying question
- Uses intelligent defaults
- Explains decisions clearly
- Provides actionable next steps

**Avoid**:
- Multiple technical questions
- Manual configuration requests
- Asking for AWS expertise
- Delaying execution for "perfect" config

---

**🚀 Ready to deploy!** AI agents can now intelligently analyze requirements and automate AWS Lightsail deployments with zero manual intervention.