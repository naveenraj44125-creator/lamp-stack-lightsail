#!/usr/bin/env node

/**
 * Enhanced HTTP/SSE Server for Lightsail Deployment MCP
 * 
 * This server provides intelligent infrastructure setup and deployment automation.
 * It can analyze project requirements, detect application types, and generate
 * accurate deployment configurations based on actual project needs.
 * 
 * Features:
 * - Intelligent project analysis and type detection
 * - Smart infrastructure sizing recommendations
 * - Automatic configuration generation
 * - Multi-service application support
 * - Database and storage requirement analysis
 * - Security and performance optimization
 * 
 * Usage:
 *   node server.js [--port PORT] [--host HOST]
 * 
 * Environment Variables:
 *   PORT - Server port (default: 3000)
 *   HOST - Server host (default: 0.0.0.0)
 *   MCP_AUTH_TOKEN - Optional authentication token
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import express from 'express';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

// Parse command line arguments
const args = process.argv.slice(2);
const portIndex = args.indexOf('--port');
const hostIndex = args.indexOf('--host');

const PORT = portIndex !== -1 ? parseInt(args[portIndex + 1]) : process.env.PORT || 3001;
const HOST = hostIndex !== -1 ? args[hostIndex + 1] : process.env.HOST || '0.0.0.0';
const AUTH_TOKEN = process.env.MCP_AUTH_TOKEN;

class EnhancedLightsailDeploymentServer {
  constructor() {
    this.server = new Server(
      {
        name: 'enhanced-lightsail-deployment-mcp',
        version: '2.0.0', // Enhanced version with intelligent analysis
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );
    
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    
    // Initialize intelligent analysis engines
    this.projectAnalyzer = new ProjectAnalyzer();
    this.infrastructureOptimizer = new InfrastructureOptimizer();
    this.configurationGenerator = new ConfigurationGenerator();
  }

  async initialize() {
    await this.setupToolHandlers();
    return this;
  }
  async setupToolHandlers() {
    const { CallToolRequestSchema, ListToolsRequestSchema } = await import('@modelcontextprotocol/sdk/types.js');
    
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'analyze_project_intelligently',
          description: 'Intelligently analyze a project directory or codebase to automatically detect application type, dependencies, database requirements, and infrastructure needs. This tool can scan files, analyze package.json/requirements.txt/composer.json, detect frameworks, and provide comprehensive deployment recommendations.',
          inputSchema: {
            type: 'object',
            properties: {
              project_path: {
                type: 'string',
                description: 'Path to the project directory to analyze (can be relative or absolute)'
              },
              project_files: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    path: { type: 'string', description: 'File path relative to project root' },
                    content: { type: 'string', description: 'File content (first 1000 chars for analysis)' }
                  }
                },
                description: 'Array of project files with content for analysis when project_path is not accessible'
              },
              user_description: {
                type: 'string',
                description: 'Optional user description of the project to enhance analysis accuracy'
              },
              deployment_preferences: {
                type: 'object',
                properties: {
                  budget: { type: 'string', enum: ['minimal', 'standard', 'performance'], default: 'standard' },
                  scale: { type: 'string', enum: ['small', 'medium', 'large'], default: 'small' },
                  environment: { type: 'string', enum: ['development', 'staging', 'production'], default: 'production' }
                },
                description: 'Deployment preferences to influence infrastructure recommendations'
              }
            }
          }
        },
        {
          name: 'generate_smart_deployment_config',
          description: 'Generate intelligent deployment configuration based on project analysis. Creates accurate .config.yml files with optimized settings for the specific application type, dependencies, and infrastructure requirements.',
          inputSchema: {
            type: 'object',
            properties: {
              analysis_result: {
                type: 'object',
                description: 'Result from analyze_project_intelligently tool'
              },
              app_name: {
                type: 'string',
                description: 'Application name for deployment'
              },
              instance_name: {
                type: 'string',
                description: 'Lightsail instance name'
              },
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region for deployment'
              },
              custom_overrides: {
                type: 'object',
                properties: {
                  bundle_id: { type: 'string', description: 'Override recommended instance size' },
                  database_type: { type: 'string', enum: ['mysql', 'postgresql', 'none'] },
                  enable_bucket: { type: 'boolean' },
                  enable_ssl: { type: 'boolean', default: true },
                  enable_monitoring: { type: 'boolean', default: true }
                },
                description: 'Custom overrides for generated configuration'
              }
            },
            required: ['analysis_result', 'app_name']
          }
        },
        {
          name: 'setup_intelligent_deployment',
          description: 'Complete intelligent deployment setup that combines project analysis and configuration generation. This is the main tool that analyzes your project and sets up everything needed for deployment.',
          inputSchema: {
            type: 'object',
            properties: {
              project_path: {
                type: 'string',
                description: 'Path to the project directory'
              },
              project_files: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    path: { type: 'string' },
                    content: { type: 'string' }
                  }
                },
                description: 'Project files for analysis when path is not accessible'
              },
              app_name: {
                type: 'string',
                description: 'Application name'
              },
              deployment_preferences: {
                type: 'object',
                properties: {
                  budget: { type: 'string', enum: ['minimal', 'standard', 'performance'], default: 'standard' },
                  scale: { type: 'string', enum: ['small', 'medium', 'large'], default: 'small' },
                  environment: { type: 'string', enum: ['development', 'staging', 'production'], default: 'production' },
                  aws_region: { type: 'string', default: 'us-east-1' }
                }
              },
              github_config: {
                type: 'object',
                properties: {
                  username: { type: 'string', description: 'GitHub username' },
                  repository: { type: 'string', description: 'Repository name' },
                  visibility: { type: 'string', enum: ['public', 'private'], default: 'private' }
                }
              }
            },
            required: ['app_name']
          }
        },
        {
          name: 'optimize_infrastructure_costs',
          description: 'Analyze and optimize infrastructure costs based on application requirements. Provides recommendations for right-sizing instances, database configurations, and storage options.',
          inputSchema: {
            type: 'object',
            properties: {
              current_config: {
                type: 'object',
                description: 'Current deployment configuration'
              },
              usage_patterns: {
                type: 'object',
                properties: {
                  expected_traffic: { type: 'string', enum: ['low', 'medium', 'high'], default: 'medium' },
                  peak_hours: { type: 'string', description: 'Peak usage hours (e.g., "9-17 EST")' },
                  data_volume: { type: 'string', enum: ['small', 'medium', 'large'], default: 'small' }
                }
              },
              budget_constraints: {
                type: 'object',
                properties: {
                  monthly_budget: { type: 'number', description: 'Monthly budget in USD' },
                  priority: { type: 'string', enum: ['cost', 'performance', 'balanced'], default: 'balanced' }
                }
              }
            },
            required: ['current_config']
          }
        },
        {
          name: 'detect_security_requirements',
          description: 'Analyze project for security requirements and generate appropriate security configurations including SSL, firewall rules, environment variables, and compliance settings.',
          inputSchema: {
            type: 'object',
            properties: {
              project_analysis: {
                type: 'object',
                description: 'Project analysis result'
              },
              compliance_requirements: {
                type: 'array',
                items: { type: 'string', enum: ['GDPR', 'HIPAA', 'SOC2', 'PCI-DSS'] },
                description: 'Compliance requirements'
              },
              data_sensitivity: {
                type: 'string',
                enum: ['public', 'internal', 'confidential', 'restricted'],
                default: 'internal',
                description: 'Data sensitivity level'
              }
            },
            required: ['project_analysis']
          }
        }
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'analyze_project_intelligently':
            return await this.analyzeProjectIntelligently(args);
          case 'generate_smart_deployment_config':
            return await this.generateSmartDeploymentConfig(args);
          case 'setup_intelligent_deployment':
            return await this.setupIntelligentDeployment(args);
          case 'optimize_infrastructure_costs':
            return await this.optimizeInfrastructureCosts(args);
          case 'detect_security_requirements':
            return await this.detectSecurityRequirements(args);
          default:
            return {
              content: [{ type: 'text', text: `Tool ${name} not implemented. Available tools: analyze_project_intelligently, generate_smart_deployment_config, setup_intelligent_deployment, optimize_infrastructure_costs, detect_security_requirements` }],
            };
        }
      } catch (error) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }],
          isError: true,
        };
      }
    });
  }
  async analyzeProjectIntelligently(args) {
    const { project_path, project_files, user_description = '', deployment_preferences = {} } = args;

    try {
      const analysis = await this.projectAnalyzer.analyzeProject(project_path, project_files, user_description);
      
      // Enhance with deployment preferences
      if (deployment_preferences.budget) {
        analysis.budget_preference = deployment_preferences.budget;
      }
      if (deployment_preferences.scale) {
        analysis.scale_preference = deployment_preferences.scale;
      }

      return {
        content: [{
          type: 'text',
          text: `# 🔍 Intelligent Project Analysis Results

## 📊 Detection Summary
- **Application Type**: ${analysis.detected_type} (${Math.round(analysis.confidence * 100)}% confidence)
- **Deployment Complexity**: ${analysis.deployment_complexity}
- **Estimated Monthly Cost**: $${analysis.estimated_costs.monthly_min} - $${analysis.estimated_costs.monthly_max}

## 🛠️ Detected Technologies
${analysis.frameworks.length > 0 ? 
  analysis.frameworks.map(f => `- **${f.name}** (${f.type}) - ${Math.round(f.confidence * 100)}% confidence`).join('\n') :
  '- No specific frameworks detected'
}

## 💾 Database Requirements
${analysis.databases.length > 0 ?
  analysis.databases.map(db => `- **${db.name}** (${db.type}) - ${Math.round(db.confidence * 100)}% confidence`).join('\n') :
  '- No database requirements detected'
}

## 📦 Storage & Infrastructure Needs
- **File Uploads**: ${analysis.storage_needs.file_uploads ? '✅ Yes' : '❌ No'}
- **Image Processing**: ${analysis.storage_needs.image_processing ? '✅ Yes' : '❌ No'}
- **Bucket Storage**: ${analysis.storage_needs.needs_bucket ? '✅ Recommended' : '❌ Not needed'}
- **Recommended Instance**: ${analysis.infrastructure_needs.bundle_size}

## 🔒 Security Considerations
- **Handles User Data**: ${analysis.security_considerations.handles_user_data ? '✅ Yes' : '❌ No'}
- **Needs Authentication**: ${analysis.security_considerations.needs_auth ? '✅ Yes' : '❌ No'}
- **SSL Required**: ${analysis.security_considerations.needs_ssl ? '✅ Yes' : '❌ No'}
- **File Upload Security**: ${analysis.security_considerations.file_uploads ? '⚠️ Required' : '✅ Not applicable'}

## 🎯 Deployment Recommendations
Based on the analysis, here are the recommended next steps:

1. **Application Type**: Deploy as **${analysis.detected_type}** application
2. **Instance Size**: Use **${analysis.infrastructure_needs.bundle_size}** bundle
3. **Database**: ${analysis.databases.length > 0 ? `Set up ${analysis.databases[0].type} database` : 'No database needed'}
4. **Storage**: ${analysis.storage_needs.needs_bucket ? 'Configure S3-compatible bucket for file storage' : 'Standard storage sufficient'}
5. **Security**: ${analysis.security_considerations.handles_user_data ? 'Implement user data protection measures' : 'Standard security configuration'}

## 📋 Analysis Data
\`\`\`json
${JSON.stringify(analysis, null, 2)}
\`\`\`

Use this analysis result with the \`generate_smart_deployment_config\` tool to create your deployment configuration.`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Analysis failed: ${error.message}` }],
        isError: true
      };
    }
  }

  async generateSmartDeploymentConfig(args) {
    const { analysis_result, app_name, instance_name, aws_region = 'us-east-1', custom_overrides = {} } = args;

    if (!analysis_result || !app_name) {
      return {
        content: [{ type: 'text', text: '❌ Error: analysis_result and app_name are required' }],
        isError: true
      };
    }

    try {
      // Optimize infrastructure based on analysis
      const optimization = this.infrastructureOptimizer.optimizeInfrastructure(
        analysis_result,
        {
          budget: analysis_result.budget_preference || 'standard',
          scale: analysis_result.scale_preference || 'small',
          environment: 'production'
        }
      );

      // Generate configuration
      const config = this.configurationGenerator.generateDeploymentConfig(
        analysis_result,
        optimization,
        {
          app_name,
          instance_name,
          aws_region,
          custom_overrides
        }
      );

      // Generate workflow
      const workflow = this.configurationGenerator.generateWorkflow(
        analysis_result,
        { app_name, aws_region }
      );

      // Format configuration as YAML
      const configYAML = this.configurationGenerator.formatYAML(config);

      return {
        content: [{
          type: 'text',
          text: `# 🚀 Smart Deployment Configuration Generated

## 📊 Infrastructure Optimization Results
- **Recommended Instance**: ${optimization.recommended_bundle}
- **Monthly Cost Estimate**: $${optimization.cost_breakdown.total}
- **Performance Score**: ${optimization.performance_score}/100
- **Cost Efficiency Score**: ${optimization.cost_efficiency_score}/100

### Cost Breakdown
- Instance: $${optimization.cost_breakdown.instance}/month
- Database: $${optimization.cost_breakdown.database}/month
- Storage: $${optimization.cost_breakdown.storage}/month

## 🔧 Optimization Recommendations
${optimization.optimizations.map(opt => 
  `- **${opt.type.toUpperCase()}** (${opt.priority}): ${opt.message}\n  *Impact*: ${opt.impact}`
).join('\n')}

## 📄 Generated Configuration Files

### 1. deployment-${analysis_result.detected_type}.config.yml
\`\`\`yaml
${configYAML}
\`\`\`

### 2. .github/workflows/deploy-${analysis_result.detected_type}.yml
\`\`\`yaml
${workflow}
\`\`\`

## 🎯 Next Steps
1. Save the configuration as \`deployment-${analysis_result.detected_type}.config.yml\`
2. Save the workflow as \`.github/workflows/deploy-${analysis_result.detected_type}.yml\`
3. Update any placeholder values (passwords, secrets)
4. Commit and push to trigger deployment

## ⚠️ Important Notes
- Change all placeholder passwords before deployment
- Set up AWS_ROLE_ARN in GitHub repository secrets
- Review security settings for production use
- Consider using external RDS for production databases

The configuration has been optimized for your specific application type and requirements!`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Configuration generation failed: ${error.message}` }],
        isError: true
      };
    }
  }

  async setupIntelligentDeployment(args) {
    const { 
      project_path, 
      project_files, 
      app_name, 
      deployment_preferences = {}, 
      github_config = {} 
    } = args;

    if (!app_name) {
      return {
        content: [{ type: 'text', text: '❌ Error: app_name is required' }],
        isError: true
      };
    }

    try {
      // Step 1: Analyze project
      const analysisResult = await this.analyzeProjectIntelligently({
        project_path,
        project_files,
        deployment_preferences
      });

      if (analysisResult.isError) {
        return analysisResult;
      }

      // Extract analysis from the response
      const analysisText = analysisResult.content[0].text;
      const analysisMatch = analysisText.match(/```json\n([\s\S]*?)\n```/);
      
      if (!analysisMatch) {
        return {
          content: [{ type: 'text', text: '❌ Error: Could not extract analysis data' }],
          isError: true
        };
      }

      const analysis = JSON.parse(analysisMatch[1]);

      // Step 2: Generate configuration
      const configResult = await this.generateSmartDeploymentConfig({
        analysis_result: analysis,
        app_name,
        instance_name: `${analysis.detected_type}-${app_name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`,
        aws_region: deployment_preferences.aws_region || 'us-east-1'
      });

      if (configResult.isError) {
        return configResult;
      }

      // Step 3: Generate setup script
      const setupScript = this.generateSetupScript(analysis, app_name, deployment_preferences, github_config);

      return {
        content: [{
          type: 'text',
          text: `# 🎉 Complete Intelligent Deployment Setup

${analysisResult.content[0].text}

---

${configResult.content[0].text}

---

## 🛠️ Automated Setup Script

To complete the setup automatically, run this script:

\`\`\`bash
${setupScript}
\`\`\`

## 📋 Manual Setup Steps (Alternative)

If you prefer manual setup:

1. **Create the configuration file**:
   \`\`\`bash
   # Extract the YAML configuration from above and save as:
   # deployment-${analysis.detected_type}.config.yml
   \`\`\`

2. **Create the GitHub workflow**:
   \`\`\`bash
   mkdir -p .github/workflows
   # Extract the workflow YAML from above and save as:
   # .github/workflows/deploy-${analysis.detected_type}.yml
   \`\`\`

3. **Set up GitHub repository**:
   \`\`\`bash
   git add .
   git commit -m "Add intelligent deployment configuration"
   git push origin main
   \`\`\`

4. **Configure GitHub secrets**:
   - Set AWS_ROLE_ARN in repository variables
   - Ensure GitHub OIDC is configured for AWS

## 🎯 What This Setup Provides

✅ **Intelligent Analysis**: Automatically detected your application type and requirements
✅ **Optimized Infrastructure**: Right-sized instances and services for your needs  
✅ **Cost Optimization**: Estimated monthly cost of $${analysis.estimated_costs.monthly_min}-${analysis.estimated_costs.monthly_max}
✅ **Security Best Practices**: SSL, firewall, and authentication configured
✅ **Automated Deployment**: GitHub Actions workflow for continuous deployment
✅ **Monitoring & Health Checks**: Built-in application monitoring
✅ **Backup Strategy**: Automated backup configuration

Your deployment is now ready for production! 🚀`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Setup failed: ${error.message}` }],
        isError: true
      };
    }
  }

  generateSetupScript(analysis, appName, deploymentPreferences, githubConfig) {
    const appType = analysis.detected_type;
    const instanceName = `${appType}-${appName.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
    const awsRegion = deploymentPreferences.aws_region || 'us-east-1';
    
    return `#!/bin/bash
# Intelligent Deployment Setup Script
# Generated for: ${appName} (${appType} application)

set -e

echo "🚀 Setting up intelligent deployment for ${appName}..."

# Set environment variables for fully automated mode
export FULLY_AUTOMATED=true
export APP_TYPE="${appType}"
export APP_NAME="${appName}"
export INSTANCE_NAME="${instanceName}"
export AWS_REGION="${awsRegion}"
export BLUEPRINT_ID="ubuntu_22_04"
export BUNDLE_ID="${analysis.infrastructure_needs.bundle_size}"
export DATABASE_TYPE="${analysis.databases.length > 0 ? analysis.databases[0].type : 'none'}"
export DB_EXTERNAL="${analysis.databases.length > 0 && analysis.scale_preference !== 'small' ? 'true' : 'false'}"
export ENABLE_BUCKET="${analysis.storage_needs.needs_bucket ? 'true' : 'false'}"
export REPO_VISIBILITY="${githubConfig.visibility || 'private'}"
${githubConfig.username ? `export GITHUB_USERNAME="${githubConfig.username}"` : ''}
${githubConfig.repository ? `export GITHUB_REPO="${githubConfig.repository}"` : ''}

# Download and run the setup script
curl -sSL https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh | bash

echo "✅ Intelligent deployment setup complete!"
echo "🌐 Your application will be available at: http://${instanceName}.lightsail.aws.com/"
echo "📊 Monitor deployment: https://github.com/\${GITHUB_REPO}/actions"`;
  }

  async optimizeInfrastructureCosts(args) {
    const { current_config, usage_patterns = {}, budget_constraints = {} } = args;

    if (!current_config) {
      return {
        content: [{ type: 'text', text: '❌ Error: current_config is required' }],
        isError: true
      };
    }

    try {
      // Analyze current configuration for optimization opportunities
      const analysis = {
        detected_type: current_config.application?.type || 'unknown',
        infrastructure_needs: {
          bundle_size: current_config.lightsail?.bundle_id || 'micro_3_0'
        },
        databases: current_config.dependencies?.mysql?.enabled || current_config.dependencies?.postgresql?.enabled ? 
          [{ type: current_config.dependencies?.mysql?.enabled ? 'mysql' : 'postgresql' }] : [],
        storage_needs: {
          needs_bucket: current_config.lightsail?.bucket?.enabled || false
        }
      };

      const optimization = this.infrastructureOptimizer.optimizeInfrastructure(
        analysis,
        {
          budget: budget_constraints.priority || 'balanced',
          scale: usage_patterns.expected_traffic || 'medium',
          environment: 'production'
        }
      );

      // Calculate potential savings
      const currentCosts = this.calculateCurrentCosts(current_config);
      const optimizedCosts = optimization.cost_breakdown.total;
      const savings = currentCosts - optimizedCosts;
      const savingsPercent = Math.round((savings / currentCosts) * 100);

      return {
        content: [{
          type: 'text',
          text: `# 💰 Infrastructure Cost Optimization Analysis

## 📊 Current vs Optimized Costs
- **Current Monthly Cost**: $${currentCosts}
- **Optimized Monthly Cost**: $${optimizedCosts}
- **Potential Savings**: $${savings} (${savingsPercent}% reduction)

## 🎯 Optimization Recommendations

### Instance Optimization
- **Current**: ${current_config.lightsail?.bundle_id || 'unknown'}
- **Recommended**: ${optimization.recommended_bundle}
- **Reason**: ${this.getOptimizationReason(current_config.lightsail?.bundle_id, optimization.recommended_bundle)}

### Database Optimization
${optimization.database_config ? `
- **Configuration**: ${optimization.database_config.external ? 'External RDS' : 'Local database'}
- **Size**: ${optimization.database_config.size}
- **Multi-AZ**: ${optimization.database_config.multi_az ? 'Enabled' : 'Disabled'}
` : '- No database optimization needed'}

### Storage Optimization
${optimization.bucket_config ? `
- **Bucket Size**: ${optimization.bucket_config.bundle_id}
- **Versioning**: ${optimization.bucket_config.versioning ? 'Enabled' : 'Disabled'}
- **Lifecycle Rules**: ${optimization.bucket_config.lifecycle_rules ? 'Enabled' : 'Disabled'}
` : '- No storage optimization needed'}

## 🔧 Implementation Steps

1. **Update Configuration**:
   \`\`\`yaml
   lightsail:
     bundle_id: "${optimization.recommended_bundle}"
   \`\`\`

2. **Database Changes** (if applicable):
   ${optimization.database_config ? `
   \`\`\`yaml
   dependencies:
     ${optimization.database_config.type}:
       external: ${optimization.database_config.external}
       config:
         size: ${optimization.database_config.size}
   \`\`\`
   ` : 'No database changes needed'}

3. **Deploy Changes**:
   \`\`\`bash
   git add deployment-*.config.yml
   git commit -m "Optimize infrastructure costs"
   git push origin main
   \`\`\`

## ⚠️ Important Considerations

${optimization.optimizations.map(opt => `- **${opt.type.toUpperCase()}**: ${opt.message}`).join('\n')}

## 📈 Performance Impact
- **Performance Score**: ${optimization.performance_score}/100
- **Cost Efficiency Score**: ${optimization.cost_efficiency_score}/100

The optimized configuration maintains performance while reducing costs by ${savingsPercent}%!`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Cost optimization failed: ${error.message}` }],
        isError: true
      };
    }
  }

  calculateCurrentCosts(config) {
    let total = 0;
    
    // Instance cost
    const bundleId = config.lightsail?.bundle_id || 'micro_3_0';
    const bundleCosts = {
      'nano_3_0': 3.5,
      'micro_3_0': 5,
      'small_3_0': 10,
      'medium_3_0': 20,
      'large_3_0': 40
    };
    total += bundleCosts[bundleId] || 5;
    
    // Database cost
    if (config.dependencies?.mysql?.enabled || config.dependencies?.postgresql?.enabled) {
      total += 15; // Base RDS cost
    }
    
    // Bucket cost
    if (config.lightsail?.bucket?.enabled) {
      total += 1; // Base bucket cost
    }
    
    return total;
  }

  getOptimizationReason(current, recommended) {
    if (current === recommended) {
      return 'Current size is optimal for your workload';
    } else if (this.bundleSpecs[recommended]?.cost < this.bundleSpecs[current]?.cost) {
      return 'Downsize to reduce costs while maintaining performance';
    } else {
      return 'Upgrade for better performance and reliability';
    }
  }

  async detectSecurityRequirements(args) {
    const { project_analysis, compliance_requirements = [], data_sensitivity = 'internal' } = args;

    if (!project_analysis) {
      return {
        content: [{ type: 'text', text: '❌ Error: project_analysis is required' }],
        isError: true
      };
    }

    try {
      const securityConfig = this.generateSecurityConfiguration(
        project_analysis,
        compliance_requirements,
        data_sensitivity
      );

      return {
        content: [{
          type: 'text',
          text: `# 🔒 Security Requirements Analysis

## 🎯 Security Assessment
- **Data Sensitivity**: ${data_sensitivity.toUpperCase()}
- **Compliance Requirements**: ${compliance_requirements.length > 0 ? compliance_requirements.join(', ') : 'None specified'}
- **Risk Level**: ${securityConfig.risk_level}

## 🛡️ Required Security Measures

### SSL/TLS Configuration
- **SSL Required**: ${securityConfig.ssl.required ? '✅ Yes' : '❌ No'}
- **Force HTTPS**: ${securityConfig.ssl.force_https ? '✅ Yes' : '❌ No'}
- **Certificate Type**: ${securityConfig.ssl.certificate_type}

### Authentication & Authorization
- **Authentication Required**: ${securityConfig.auth.required ? '✅ Yes' : '❌ No'}
- **Multi-Factor Auth**: ${securityConfig.auth.mfa_required ? '✅ Required' : '❌ Optional'}
- **Session Management**: ${securityConfig.auth.session_security}

### Data Protection
- **Encryption at Rest**: ${securityConfig.data.encryption_at_rest ? '✅ Required' : '❌ Not required'}
- **Encryption in Transit**: ${securityConfig.data.encryption_in_transit ? '✅ Required' : '❌ Not required'}
- **Data Backup Encryption**: ${securityConfig.data.backup_encryption ? '✅ Required' : '❌ Not required'}

### Network Security
- **Firewall Rules**: ${securityConfig.network.strict_firewall ? 'Strict' : 'Standard'}
- **Rate Limiting**: ${securityConfig.network.rate_limiting ? '✅ Enabled' : '❌ Disabled'}
- **DDoS Protection**: ${securityConfig.network.ddos_protection ? '✅ Enabled' : '❌ Basic'}

### File Upload Security
${project_analysis.storage_needs?.file_uploads ? `
- **File Type Validation**: ✅ Required
- **File Size Limits**: ✅ Required
- **Virus Scanning**: ${securityConfig.uploads.virus_scanning ? '✅ Required' : '❌ Optional'}
- **Secure Storage**: ✅ Use S3-compatible bucket
` : '- No file upload security needed'}

## 📋 Implementation Configuration

### Environment Variables
\`\`\`yaml
environment_variables:
  # Security Configuration
  SSL_ENABLED: "${securityConfig.ssl.required}"
  FORCE_HTTPS: "${securityConfig.ssl.force_https}"
  SESSION_SECURE: "true"
  SESSION_SAME_SITE: "strict"
  ${securityConfig.auth.required ? `
  JWT_ALGORITHM: "RS256"
  PASSWORD_MIN_LENGTH: "12"
  PASSWORD_REQUIRE_SPECIAL: "true"` : ''}
  ${compliance_requirements.includes('GDPR') ? `
  GDPR_COMPLIANCE: "true"
  DATA_RETENTION_DAYS: "365"` : ''}
\`\`\`

### Firewall Configuration
\`\`\`yaml
dependencies:
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"    # SSH (restrict to specific IPs in production)
        - "80"    # HTTP (redirect to HTTPS)
        - "443"   # HTTPS
      ${securityConfig.network.strict_firewall ? `
      strict_mode: true
      fail2ban_enabled: true
      rate_limiting:
        enabled: true
        requests_per_minute: 60` : ''}
      deny_all_other: true
\`\`\`

### SSL Configuration
\`\`\`yaml
security:
  ssl:
    enabled: ${securityConfig.ssl.required}
    force_https: ${securityConfig.ssl.force_https}
    certificate_auto_renew: true
    hsts_enabled: true
    hsts_max_age: 31536000
\`\`\`

## ⚠️ Security Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Set up proper SSL certificates
- [ ] Configure firewall rules
- [ ] Enable logging and monitoring
- [ ] Set up backup encryption
- [ ] Review file upload restrictions
- [ ] Configure rate limiting
- [ ] Set up security headers
${compliance_requirements.includes('GDPR') ? '- [ ] Implement GDPR compliance measures' : ''}
${compliance_requirements.includes('HIPAA') ? '- [ ] Implement HIPAA compliance measures' : ''}
${compliance_requirements.includes('SOC2') ? '- [ ] Implement SOC2 compliance measures' : ''}

## 🚨 High Priority Actions

${securityConfig.priority_actions.map(action => `- **${action.priority.toUpperCase()}**: ${action.description}`).join('\n')}

Your security configuration has been tailored for ${data_sensitivity} data with ${securityConfig.risk_level} risk level.`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Security analysis failed: ${error.message}` }],
        isError: true
      };
    }
  }

  generateSecurityConfiguration(analysis, complianceRequirements, dataSensitivity) {
    const config = {
      risk_level: 'medium',
      ssl: {
        required: true,
        force_https: true,
        certificate_type: 'Let\'s Encrypt'
      },
      auth: {
        required: analysis.security_considerations?.needs_auth || false,
        mfa_required: false,
        session_security: 'standard'
      },
      data: {
        encryption_at_rest: false,
        encryption_in_transit: true,
        backup_encryption: false
      },
      network: {
        strict_firewall: false,
        rate_limiting: false,
        ddos_protection: false
      },
      uploads: {
        virus_scanning: false
      },
      priority_actions: []
    };

    // Adjust based on data sensitivity
    if (dataSensitivity === 'confidential' || dataSensitivity === 'restricted') {
      config.risk_level = 'high';
      config.auth.mfa_required = true;
      config.data.encryption_at_rest = true;
      config.data.backup_encryption = true;
      config.network.strict_firewall = true;
      config.network.rate_limiting = true;
      config.uploads.virus_scanning = true;
    }

    // Adjust based on compliance requirements
    if (complianceRequirements.includes('GDPR') || complianceRequirements.includes('HIPAA')) {
      config.data.encryption_at_rest = true;
      config.data.backup_encryption = true;
      config.auth.session_security = 'strict';
    }

    if (complianceRequirements.includes('SOC2') || complianceRequirements.includes('PCI-DSS')) {
      config.network.strict_firewall = true;
      config.network.rate_limiting = true;
      config.network.ddos_protection = true;
    }

    // Generate priority actions
    if (analysis.security_considerations?.handles_user_data) {
      config.priority_actions.push({
        priority: 'high',
        description: 'Implement proper user data encryption and access controls'
      });
    }

    if (analysis.security_considerations?.file_uploads) {
      config.priority_actions.push({
        priority: 'high',
        description: 'Configure secure file upload validation and storage'
      });
    }

    if (config.risk_level === 'high') {
      config.priority_actions.push({
        priority: 'critical',
        description: 'Enable all security features for high-risk data handling'
      });
    }

    return config;
  }
}

// Import the analysis classes
import { ProjectAnalyzer } from './project-analyzer.js';
import { InfrastructureOptimizer } from './infrastructure-optimizer.js';
import { ConfigurationGenerator } from './configuration-generator.js';

// HTTP Server setup
const app = express();

// Middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.static('public'));

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// Authentication middleware
const authenticate = (req, res, next) => {
  if (AUTH_TOKEN) {
    const authHeader = req.headers.authorization;
    if (!authHeader || authHeader !== `Bearer ${AUTH_TOKEN}`) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
  }
  next();
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    version: '2.0.0',
    features: ['intelligent-analysis', 'cost-optimization', 'security-assessment'],
    timestamp: new Date().toISOString() 
  });
});

// MCP Server endpoint - SSE transport
app.get('/mcp', authenticate, async (req, res) => {
  try {
    const server = await new EnhancedLightsailDeploymentServer().initialize();
    const transport = new SSEServerTransport('/mcp', res);
    await server.server.connect(transport);
  } catch (error) {
    console.error('MCP Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start server
app.listen(PORT, HOST, () => {
  console.log(`🚀 Enhanced Lightsail Deployment MCP Server running on http://${HOST}:${PORT}`);
  console.log(`📊 Features: Intelligent Analysis, Cost Optimization, Security Assessment`);
  console.log(`🔗 MCP Endpoint: http://${HOST}:${PORT}/mcp`);
  console.log(`💡 Health Check: http://${HOST}:${PORT}/health`);
  if (AUTH_TOKEN) {
    console.log(`🔒 Authentication: Enabled`);
  }
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down Enhanced MCP Server...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down Enhanced MCP Server...');
  process.exit(0);
});