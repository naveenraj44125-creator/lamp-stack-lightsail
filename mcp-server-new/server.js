#!/usr/bin/env node

/**
 * Enhanced HTTP/SSE Server for Lightsail Deployment MCP
 * 
 * This server provides intelligent infrastructure setup and deployment automation.
 * It can analyze project requirements, detect application types, and generate
 * accurate deployment configurations based on actual project needs.
 * 
 * Features:
 * - Intelligent project analysis and type detection (AI-powered via Bedrock)
 * - Smart infrastructure sizing recommendations
 * - Automatic configuration generation
 * - Multi-service application support
 * - Database and storage requirement analysis
 * - Security and performance optimization
 * - AI-powered troubleshooting and Q&A
 * - ACTUALLY CREATES AWS RESOURCES (Lightsail instances, IAM roles)
 * - ACTUALLY WRITES FILES (deployment configs, GitHub workflows)
 * 
 * Usage:
 *   node server.js [--port PORT] [--host HOST]
 * 
 * Environment Variables:
 *   PORT - Server port (default: 3000)
 *   HOST - Server host (default: 0.0.0.0)
 *   MCP_AUTH_TOKEN - Optional authentication token
 *   AWS_REGION - AWS region for Bedrock (default: us-east-1)
 *   AWS_PROFILE - AWS profile for credentials (recommended: lightsail-deploy)
 *   BEDROCK_MODEL_ID - Bedrock model ID (default: anthropic.claude-3-sonnet-20240229-v1:0)
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import express from 'express';
import { execSync, exec } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// AWS SDK imports for actual resource creation
import { LightsailClient, CreateInstancesCommand, GetInstanceCommand, GetBundlesCommand, GetBlueprintsCommand, AllocateStaticIpCommand, AttachStaticIpCommand } from '@aws-sdk/client-lightsail';
import { IAMClient, CreateRoleCommand, AttachRolePolicyCommand, CreatePolicyCommand, GetRoleCommand, UpdateAssumeRolePolicyCommand, GetPolicyCommand } from '@aws-sdk/client-iam';
import { STSClient, GetCallerIdentityCommand } from '@aws-sdk/client-sts';
import { fromIni } from '@aws-sdk/credential-providers';

// Import Bedrock AI integration
import { BedrockAI } from './bedrock-ai.js';

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
        version: '3.0.0', // AI-powered version with Bedrock integration
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
    
    // Initialize default Bedrock AI (will be overridden per-request if credentials provided)
    this.bedrockAI = new BedrockAI({
      region: process.env.AWS_REGION || 'us-east-1',
      modelId: process.env.BEDROCK_MODEL_ID
    });
  }

  /**
   * Get BedrockAI instance with optional custom credentials
   * @param {Object} awsCredentials - Optional AWS credentials from tool input
   * @returns {BedrockAI} - BedrockAI instance configured with credentials
   */
  getBedrockAI(awsCredentials = null) {
    if (!awsCredentials) {
      return this.bedrockAI; // Use default instance
    }

    // Create new instance with provided credentials
    const options = {
      region: awsCredentials.region || process.env.AWS_REGION || 'us-east-1',
      modelId: process.env.BEDROCK_MODEL_ID
    };

    if (awsCredentials.profile) {
      options.profile = awsCredentials.profile;
    } else if (awsCredentials.access_key_id && awsCredentials.secret_access_key) {
      options.accessKeyId = awsCredentials.access_key_id;
      options.secretAccessKey = awsCredentials.secret_access_key;
      if (awsCredentials.session_token) {
        options.sessionToken = awsCredentials.session_token;
      }
    }

    return new BedrockAI(options);
  }

  /**
   * Get AWS client configuration with credentials
   * @param {Object} awsCredentials - Optional AWS credentials
   * @param {string} region - AWS region
   * @returns {Object} - AWS client configuration
   */
  getAwsClientConfig(awsCredentials = null, region = 'us-east-1') {
    const config = { region };
    
    if (awsCredentials?.profile) {
      config.credentials = fromIni({ profile: awsCredentials.profile });
    } else if (awsCredentials?.access_key_id && awsCredentials?.secret_access_key) {
      config.credentials = {
        accessKeyId: awsCredentials.access_key_id,
        secretAccessKey: awsCredentials.secret_access_key,
        ...(awsCredentials.session_token && { sessionToken: awsCredentials.session_token })
      };
    } else if (process.env.AWS_PROFILE) {
      config.credentials = fromIni({ profile: process.env.AWS_PROFILE });
    }
    // Otherwise use default credential chain
    
    return config;
  }

  /**
   * Get AWS Account ID
   * @param {Object} awsCredentials - Optional AWS credentials
   * @returns {Promise<string>} - AWS Account ID
   */
  async getAwsAccountId(awsCredentials = null) {
    const config = this.getAwsClientConfig(awsCredentials);
    const stsClient = new STSClient(config);
    const response = await stsClient.send(new GetCallerIdentityCommand({}));
    return response.Account;
  }

  /**
   * Create Lightsail instance
   * @param {Object} params - Instance parameters
   * @param {Object} awsCredentials - Optional AWS credentials
   * @returns {Promise<Object>} - Created instance details
   */
  async createLightsailInstance(params, awsCredentials = null) {
    const { instanceName, blueprintId, bundleId, region, availabilityZone, userData } = params;
    const config = this.getAwsClientConfig(awsCredentials, region);
    const lightsailClient = new LightsailClient(config);
    
    // Check if instance already exists
    try {
      const existingInstance = await lightsailClient.send(new GetInstanceCommand({ instanceName }));
      if (existingInstance.instance) {
        return {
          success: true,
          alreadyExists: true,
          instance: existingInstance.instance,
          message: `Instance ${instanceName} already exists`
        };
      }
    } catch (e) {
      // Instance doesn't exist, continue with creation
    }
    
    const az = availabilityZone || `${region}a`;
    
    const command = new CreateInstancesCommand({
      instanceNames: [instanceName],
      blueprintId: blueprintId || 'ubuntu_22_04',
      bundleId: bundleId || 'micro_3_0',
      availabilityZone: az,
      userData: userData || ''
    });
    
    const response = await lightsailClient.send(command);
    return {
      success: true,
      alreadyExists: false,
      operations: response.operations,
      message: `Instance ${instanceName} creation initiated`
    };
  }

  /**
   * Create IAM role for GitHub OIDC
   * @param {Object} params - Role parameters
   * @param {Object} awsCredentials - Optional AWS credentials
   * @returns {Promise<Object>} - Created role details
   */
  async createGitHubOidcRole(params, awsCredentials = null) {
    const { roleName, githubRepo, awsAccountId } = params;
    const config = this.getAwsClientConfig(awsCredentials);
    const iamClient = new IAMClient(config);
    
    // Trust policy for GitHub OIDC
    const trustPolicy = {
      Version: "2012-10-17",
      Statement: [{
        Effect: "Allow",
        Principal: {
          Federated: `arn:aws:iam::${awsAccountId}:oidc-provider/token.actions.githubusercontent.com`
        },
        Action: "sts:AssumeRoleWithWebIdentity",
        Condition: {
          StringEquals: {
            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
          },
          StringLike: {
            "token.actions.githubusercontent.com:sub": [
              `repo:${githubRepo}:ref:refs/heads/main`,
              `repo:${githubRepo}:ref:refs/heads/master`,
              `repo:${githubRepo}:pull_request`
            ]
          }
        }
      }]
    };
    
    let roleArn;
    let roleCreated = false;
    
    // Try to create role, or update if exists
    try {
      const createRoleResponse = await iamClient.send(new CreateRoleCommand({
        RoleName: roleName,
        AssumeRolePolicyDocument: JSON.stringify(trustPolicy),
        Description: `GitHub Actions OIDC role for ${githubRepo}`
      }));
      roleArn = createRoleResponse.Role.Arn;
      roleCreated = true;
    } catch (e) {
      if (e.name === 'EntityAlreadyExistsException') {
        // Update existing role's trust policy
        await iamClient.send(new UpdateAssumeRolePolicyCommand({
          RoleName: roleName,
          PolicyDocument: JSON.stringify(trustPolicy)
        }));
        const getRoleResponse = await iamClient.send(new GetRoleCommand({ RoleName: roleName }));
        roleArn = getRoleResponse.Role.Arn;
      } else {
        throw e;
      }
    }
    
    // Attach ReadOnlyAccess policy
    try {
      await iamClient.send(new AttachRolePolicyCommand({
        RoleName: roleName,
        PolicyArn: 'arn:aws:iam::aws:policy/ReadOnlyAccess'
      }));
    } catch (e) {
      // Ignore if already attached
    }
    
    // Create and attach Lightsail policy
    const lightsailPolicyName = `${roleName}-LightsailAccess`;
    const lightsailPolicyArn = `arn:aws:iam::${awsAccountId}:policy/${lightsailPolicyName}`;
    
    try {
      await iamClient.send(new CreatePolicyCommand({
        PolicyName: lightsailPolicyName,
        PolicyDocument: JSON.stringify({
          Version: "2012-10-17",
          Statement: [{
            Effect: "Allow",
            Action: "lightsail:*",
            Resource: "*"
          }]
        }),
        Description: "Full access to AWS Lightsail for GitHub Actions deployment"
      }));
    } catch (e) {
      // Ignore if policy already exists
    }
    
    try {
      await iamClient.send(new AttachRolePolicyCommand({
        RoleName: roleName,
        PolicyArn: lightsailPolicyArn
      }));
    } catch (e) {
      // Ignore if already attached
    }
    
    return {
      success: true,
      roleArn,
      roleName,
      roleCreated,
      message: roleCreated ? `IAM role ${roleName} created` : `IAM role ${roleName} updated`
    };
  }

  /**
   * Configure GitHub repository secrets using gh CLI
   * @param {Object} params - Secret parameters
   * @returns {Promise<Object>} - Result
   */
  async configureGitHubSecrets(params) {
    const { repo, secrets } = params;
    const results = [];
    
    for (const [name, value] of Object.entries(secrets)) {
      try {
        execSync(`gh secret set ${name} --repo ${repo} --body "${value}"`, {
          encoding: 'utf8',
          timeout: 30000,
          stdio: 'pipe'
        });
        results.push({ name, success: true });
      } catch (e) {
        results.push({ name, success: false, error: e.message });
      }
    }
    
    return { success: results.every(r => r.success), results };
  }

  /**
   * Write deployment configuration file
   * @param {Object} params - Config parameters
   * @returns {Object} - Result
   */
  writeDeploymentConfig(params) {
    const { projectPath, appType, config } = params;
    const configPath = path.join(projectPath, `deployment-${appType}.config.yml`);
    
    fs.writeFileSync(configPath, config, 'utf8');
    
    return {
      success: true,
      path: configPath,
      message: `Deployment config written to ${configPath}`
    };
  }

  /**
   * Write GitHub workflow file
   * @param {Object} params - Workflow parameters
   * @returns {Object} - Result
   */
  writeGitHubWorkflow(params) {
    const { projectPath, appType, workflow } = params;
    const workflowDir = path.join(projectPath, '.github', 'workflows');
    const workflowPath = path.join(workflowDir, `deploy-${appType}.yml`);
    
    // Create directory if it doesn't exist
    fs.mkdirSync(workflowDir, { recursive: true });
    fs.writeFileSync(workflowPath, workflow, 'utf8');
    
    return {
      success: true,
      path: workflowPath,
      message: `GitHub workflow written to ${workflowPath}`
    };
  }

  async initialize() {
    await this.setupToolHandlers();
    return this;
  }

  /**
   * List all available tools
   * @returns {Array} - Array of tool definitions
   */
  async listTools() {
    return this.tools;
  }

  /**
   * Handle a tool call directly (for HTTP endpoint testing)
   * @param {string} toolName - Name of the tool to call
   * @param {Object} args - Tool arguments
   * @returns {Object} - Tool result
   */
  async handleToolCall(toolName, args = {}) {
    // Input validation
    const validationError = this.validateToolInput(toolName, args);
    if (validationError) {
      return {
        content: [{ type: 'text', text: `❌ Validation Error: ${validationError}` }],
        isError: true,
      };
    }

    try {
      switch (toolName) {
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
        case 'list_lightsail_instances':
          return await this.listLightsailInstances(args);
        case 'check_deployment_status':
          return await this.checkDeploymentStatus(args);
        case 'validate_deployment_config':
          return await this.validateDeploymentConfig(args);
        // AI-Powered Tools
        case 'ai_analyze_project':
          return await this.aiAnalyzeProject(args);
        case 'ai_troubleshoot':
          return await this.aiTroubleshoot(args);
        case 'ai_ask_expert':
          return await this.aiAskExpert(args);
        case 'ai_review_config':
          return await this.aiReviewConfig(args);
        case 'ai_explain_code':
          return await this.aiExplainCode(args);
        case 'ai_generate_config':
          return await this.aiGenerateConfig(args);
        // Troubleshooting Tools
        case 'list_troubleshooting_scripts':
          return await this.listTroubleshootingScripts(args);
        case 'run_troubleshooting_script':
          return await this.runTroubleshootingScript(args);
        case 'diagnose_deployment_issue':
          return await this.diagnoseDeploymentIssue(args);
        case 'get_instance_logs':
          return await this.getInstanceLogs(args);
        default:
          return {
            content: [{ type: 'text', text: `Tool ${toolName} not implemented.` }],
            isError: true,
          };
      }
    } catch (error) {
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }

  async setupToolHandlers() {
    const { CallToolRequestSchema, ListToolsRequestSchema } = await import('@modelcontextprotocol/sdk/types.js');
    
    // Store tools array for listTools() method
    this.tools = [
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
          description: 'Complete intelligent deployment setup that ACTUALLY CREATES resources. This tool analyzes your project, writes deployment config files, creates Lightsail instances, sets up IAM roles for GitHub OIDC, and configures GitHub secrets. No manual steps needed!',
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
                  aws_region: { type: 'string', default: 'us-east-1' },
                  // Database configuration
                  db_name: { type: 'string', description: 'Database name (default: app_db)' },
                  db_rds_name: { type: 'string', description: 'RDS database instance name (for external databases)' },
                  // Bucket configuration
                  bucket_name: { type: 'string', description: 'S3-compatible bucket name' },
                  bucket_access: { type: 'string', enum: ['read_only', 'read_write'], default: 'read_write', description: 'Bucket access level' },
                  bucket_bundle: { type: 'string', default: 'small_1_0', description: 'Bucket bundle size' },
                  // API-only app configuration
                  api_only_app: { type: 'boolean', default: false, description: 'Set true for API-only apps without root route' },
                  verification_endpoint: { type: 'string', description: 'Custom endpoint for deployment verification' },
                  health_check_endpoint: { type: 'string', description: 'Custom health check endpoint' },
                  expected_content: { type: 'string', description: 'Expected content in health check response' }
                }
              },
              github_config: {
                type: 'object',
                properties: {
                  username: { type: 'string', description: 'GitHub username' },
                  repository: { type: 'string', description: 'Repository name' },
                  visibility: { type: 'string', enum: ['public', 'private'], default: 'private' }
                },
                description: 'GitHub configuration for OIDC setup and secrets'
              },
              aws_credentials: {
                type: 'object',
                properties: {
                  profile: { type: 'string', description: 'AWS profile name (e.g., "lightsail-deploy")' },
                  access_key_id: { type: 'string', description: 'AWS Access Key ID (alternative to profile)' },
                  secret_access_key: { type: 'string', description: 'AWS Secret Access Key' },
                  session_token: { type: 'string', description: 'AWS Session Token (for temporary credentials)' },
                  region: { type: 'string', description: 'AWS region (default: us-east-1)' }
                },
                description: 'AWS credentials for creating resources. Uses AWS_PROFILE env var or default chain if not provided.'
              },
              execute_actions: {
                type: 'boolean',
                default: true,
                description: 'Set to true to actually create resources (Lightsail instance, IAM role, write files). Set to false for dry-run analysis only.'
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
        },
        {
          name: 'list_lightsail_instances',
          description: 'List all Lightsail instances in the specified AWS region. Shows instance name, state, IP address, bundle, and blueprint information.',
          inputSchema: {
            type: 'object',
            properties: {
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region to list instances from'
              },
              filter_by_name: {
                type: 'string',
                description: 'Optional filter to match instance names (supports partial match)'
              },
              include_stopped: {
                type: 'boolean',
                default: true,
                description: 'Include stopped instances in the list'
              }
            }
          }
        },
        {
          name: 'check_deployment_status',
          description: 'Check the deployment status of a Lightsail instance including health check, running services, and application status.',
          inputSchema: {
            type: 'object',
            properties: {
              instance_name: {
                type: 'string',
                description: 'Name of the Lightsail instance to check'
              },
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region where the instance is located'
              },
              health_check_endpoint: {
                type: 'string',
                default: '/',
                description: 'Endpoint to check for health (e.g., "/", "/api/health")'
              },
              health_check_port: {
                type: 'number',
                default: 80,
                description: 'Port to check for health'
              },
              expected_content: {
                type: 'string',
                description: 'Optional content to expect in the health check response'
              }
            },
            required: ['instance_name']
          }
        },
        {
          name: 'validate_deployment_config',
          description: 'Validate a deployment configuration file for correctness and completeness. Checks for required fields, valid values, and potential issues.',
          inputSchema: {
            type: 'object',
            properties: {
              config: {
                type: 'object',
                description: 'Deployment configuration object to validate'
              },
              config_path: {
                type: 'string',
                description: 'Path to deployment configuration file (alternative to config object)'
              },
              strict_mode: {
                type: 'boolean',
                default: false,
                description: 'Enable strict validation (fail on warnings)'
              }
            }
          }
        },
        // AI-Powered Tools (via AWS Bedrock)
        {
          name: 'ai_analyze_project',
          description: 'Use AI (Claude via AWS Bedrock) to intelligently analyze project files and provide detailed deployment recommendations. More accurate than rule-based analysis.',
          inputSchema: {
            type: 'object',
            properties: {
              project_files: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    path: { type: 'string', description: 'File path' },
                    content: { type: 'string', description: 'File content' }
                  }
                },
                description: 'Array of project files to analyze'
              },
              user_description: {
                type: 'string',
                description: 'Optional description of the project to help AI understand context'
              },
              aws_credentials: {
                type: 'object',
                properties: {
                  profile: { type: 'string', description: 'AWS profile name from ~/.aws/credentials (e.g., "default", "dev", "prod")' },
                  access_key_id: { type: 'string', description: 'AWS Access Key ID (alternative to profile)' },
                  secret_access_key: { type: 'string', description: 'AWS Secret Access Key (required if access_key_id is provided)' },
                  session_token: { type: 'string', description: 'AWS Session Token (optional, for temporary credentials)' },
                  region: { type: 'string', description: 'AWS region for Bedrock (default: us-east-1)' }
                },
                description: 'AWS credentials for Bedrock. Provide either profile name OR access keys. If not provided, uses default credential chain.'
              }
            },
            required: ['project_files']
          }
        },
        {
          name: 'ai_troubleshoot',
          description: 'Use AI to troubleshoot deployment errors and issues. Provides root cause analysis and step-by-step solutions.',
          inputSchema: {
            type: 'object',
            properties: {
              error_message: {
                type: 'string',
                description: 'The error message or issue description'
              },
              context: {
                type: 'object',
                properties: {
                  app_type: { type: 'string', description: 'Application type (nodejs, python, php, etc.)' },
                  instance_name: { type: 'string', description: 'Lightsail instance name' },
                  logs: { type: 'string', description: 'Relevant log output' },
                  config: { type: 'object', description: 'Current deployment configuration' }
                },
                description: 'Additional context about the deployment'
              },
              aws_credentials: {
                type: 'object',
                properties: {
                  profile: { type: 'string', description: 'AWS profile name from ~/.aws/credentials (e.g., "default", "dev", "prod")' },
                  access_key_id: { type: 'string', description: 'AWS Access Key ID (alternative to profile)' },
                  secret_access_key: { type: 'string', description: 'AWS Secret Access Key (required if access_key_id is provided)' },
                  session_token: { type: 'string', description: 'AWS Session Token (optional, for temporary credentials)' },
                  region: { type: 'string', description: 'AWS region for Bedrock (default: us-east-1)' }
                },
                description: 'AWS credentials for Bedrock. Provide either profile name OR access keys. If not provided, uses default credential chain.'
              }
            },
            required: ['error_message']
          }
        },
        {
          name: 'ai_ask_expert',
          description: 'Ask the AI deployment expert any question about AWS Lightsail, deployment, configuration, or troubleshooting.',
          inputSchema: {
            type: 'object',
            properties: {
              question: {
                type: 'string',
                description: 'Your question about deployment'
              },
              project_context: {
                type: 'object',
                description: 'Optional project context to help AI provide more relevant answers'
              },
              aws_credentials: {
                type: 'object',
                properties: {
                  profile: { type: 'string', description: 'AWS profile name from ~/.aws/credentials (e.g., "default", "dev", "prod")' },
                  access_key_id: { type: 'string', description: 'AWS Access Key ID (alternative to profile)' },
                  secret_access_key: { type: 'string', description: 'AWS Secret Access Key (required if access_key_id is provided)' },
                  session_token: { type: 'string', description: 'AWS Session Token (optional, for temporary credentials)' },
                  region: { type: 'string', description: 'AWS region for Bedrock (default: us-east-1)' }
                },
                description: 'AWS credentials for Bedrock. Provide either profile name OR access keys. If not provided, uses default credential chain.'
              }
            },
            required: ['question']
          }
        },
        {
          name: 'ai_review_config',
          description: 'Use AI to review a deployment configuration and suggest improvements for security, performance, and cost optimization.',
          inputSchema: {
            type: 'object',
            properties: {
              config: {
                type: 'object',
                description: 'Deployment configuration to review'
              },
              config_yaml: {
                type: 'string',
                description: 'Deployment configuration as YAML string (alternative to config object)'
              },
              aws_credentials: {
                type: 'object',
                properties: {
                  profile: { type: 'string', description: 'AWS profile name from ~/.aws/credentials (e.g., "default", "dev", "prod")' },
                  access_key_id: { type: 'string', description: 'AWS Access Key ID (alternative to profile)' },
                  secret_access_key: { type: 'string', description: 'AWS Secret Access Key (required if access_key_id is provided)' },
                  session_token: { type: 'string', description: 'AWS Session Token (optional, for temporary credentials)' },
                  region: { type: 'string', description: 'AWS region for Bedrock (default: us-east-1)' }
                },
                description: 'AWS credentials for Bedrock. Provide either profile name OR access keys. If not provided, uses default credential chain.'
              }
            }
          }
        },
        {
          name: 'ai_explain_code',
          description: 'Use AI to explain code from a deployment perspective - what dependencies it needs, ports it uses, environment variables required, etc.',
          inputSchema: {
            type: 'object',
            properties: {
              code: {
                type: 'string',
                description: 'Code to analyze'
              },
              filename: {
                type: 'string',
                description: 'Optional filename for context'
              },
              aws_credentials: {
                type: 'object',
                properties: {
                  profile: { type: 'string', description: 'AWS profile name from ~/.aws/credentials (e.g., "default", "dev", "prod")' },
                  access_key_id: { type: 'string', description: 'AWS Access Key ID (alternative to profile)' },
                  secret_access_key: { type: 'string', description: 'AWS Secret Access Key (required if access_key_id is provided)' },
                  session_token: { type: 'string', description: 'AWS Session Token (optional, for temporary credentials)' },
                  region: { type: 'string', description: 'AWS region for Bedrock (default: us-east-1)' }
                },
                description: 'AWS credentials for Bedrock. Provide either profile name OR access keys. If not provided, uses default credential chain.'
              }
            },
            required: ['code']
          }
        },
        {
          name: 'ai_generate_config',
          description: 'Use AI to generate a complete deployment configuration based on project analysis and preferences.',
          inputSchema: {
            type: 'object',
            properties: {
              analysis: {
                type: 'object',
                description: 'Project analysis result (from ai_analyze_project or analyze_project_intelligently)'
              },
              preferences: {
                type: 'object',
                properties: {
                  budget: { type: 'string', enum: ['minimal', 'standard', 'performance'], default: 'standard' },
                  scale: { type: 'string', enum: ['small', 'medium', 'large'], default: 'small' },
                  environment: { type: 'string', enum: ['development', 'staging', 'production'], default: 'production' },
                  aws_region: { type: 'string', default: 'us-east-1' }
                }
              },
              aws_credentials: {
                type: 'object',
                properties: {
                  profile: { type: 'string', description: 'AWS profile name from ~/.aws/credentials (e.g., "default", "dev", "prod")' },
                  access_key_id: { type: 'string', description: 'AWS Access Key ID (alternative to profile)' },
                  secret_access_key: { type: 'string', description: 'AWS Secret Access Key (required if access_key_id is provided)' },
                  session_token: { type: 'string', description: 'AWS Session Token (optional, for temporary credentials)' },
                  region: { type: 'string', description: 'AWS region for Bedrock (default: us-east-1)' }
                },
                description: 'AWS credentials for Bedrock. Provide either profile name OR access keys. If not provided, uses default credential chain.'
              }
            },
            required: ['analysis']
          }
        },
        // Troubleshooting Tools
        {
          name: 'list_troubleshooting_scripts',
          description: 'List all available troubleshooting scripts organized by category (docker, general, lamp, nginx, nodejs, python, react). Use this to discover what troubleshooting tools are available.',
          inputSchema: {
            type: 'object',
            properties: {
              category: {
                type: 'string',
                enum: ['all', 'docker', 'general', 'lamp', 'nginx', 'nodejs', 'python', 'react'],
                default: 'all',
                description: 'Filter scripts by category. Use "all" to see all available scripts.'
              }
            }
          }
        },
        {
          name: 'run_troubleshooting_script',
          description: 'Run a specific troubleshooting script to diagnose or fix deployment issues on a Lightsail instance. Scripts can debug issues, fix common problems, or verify deployments.',
          inputSchema: {
            type: 'object',
            properties: {
              script_name: {
                type: 'string',
                description: 'Name of the script to run (e.g., "debug-nodejs.py", "fix-nginx.py"). Use list_troubleshooting_scripts to see available scripts.'
              },
              category: {
                type: 'string',
                enum: ['docker', 'general', 'lamp', 'nginx', 'nodejs', 'python', 'react'],
                description: 'Category of the script (e.g., "nodejs", "nginx")'
              },
              instance_name: {
                type: 'string',
                description: 'Name of the Lightsail instance to troubleshoot'
              },
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region where the instance is located'
              },
              additional_args: {
                type: 'object',
                description: 'Additional arguments to pass to the script (varies by script)'
              }
            },
            required: ['script_name', 'category', 'instance_name']
          }
        },
        {
          name: 'diagnose_deployment_issue',
          description: 'Use AI to analyze deployment errors and automatically recommend and optionally run the appropriate troubleshooting scripts. Combines AI analysis with automated troubleshooting.',
          inputSchema: {
            type: 'object',
            properties: {
              instance_name: {
                type: 'string',
                description: 'Name of the Lightsail instance with issues'
              },
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region where the instance is located'
              },
              error_description: {
                type: 'string',
                description: 'Description of the error or issue you are experiencing'
              },
              app_type: {
                type: 'string',
                enum: ['nodejs', 'python', 'php', 'lamp', 'docker', 'nginx', 'react', 'unknown'],
                description: 'Type of application deployed (helps narrow down troubleshooting)'
              },
              logs: {
                type: 'string',
                description: 'Any relevant log output or error messages'
              },
              auto_fix: {
                type: 'boolean',
                default: false,
                description: 'If true, automatically run recommended fix scripts after diagnosis'
              }
            },
            required: ['instance_name', 'error_description']
          }
        },
        {
          name: 'get_instance_logs',
          description: 'Retrieve logs from a Lightsail instance for troubleshooting. Can get application logs, system logs, or specific service logs.',
          inputSchema: {
            type: 'object',
            properties: {
              instance_name: {
                type: 'string',
                description: 'Name of the Lightsail instance'
              },
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region where the instance is located'
              },
              log_type: {
                type: 'string',
                enum: ['application', 'system', 'nginx', 'apache', 'pm2', 'docker', 'all'],
                default: 'application',
                description: 'Type of logs to retrieve'
              },
              lines: {
                type: 'number',
                default: 100,
                description: 'Number of log lines to retrieve'
              }
            },
            required: ['instance_name']
          }
        }
      ];

    // Set up ListToolsRequestSchema handler using stored tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: this.tools,
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        // Input validation
        const validationError = this.validateToolInput(name, args);
        if (validationError) {
          return {
            content: [{ type: 'text', text: `❌ Validation Error: ${validationError}` }],
            isError: true,
          };
        }

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
          case 'list_lightsail_instances':
            return await this.listLightsailInstances(args);
          case 'check_deployment_status':
            return await this.checkDeploymentStatus(args);
          case 'validate_deployment_config':
            return await this.validateDeploymentConfig(args);
          // AI-Powered Tools
          case 'ai_analyze_project':
            return await this.aiAnalyzeProject(args);
          case 'ai_troubleshoot':
            return await this.aiTroubleshoot(args);
          case 'ai_ask_expert':
            return await this.aiAskExpert(args);
          case 'ai_review_config':
            return await this.aiReviewConfig(args);
          case 'ai_explain_code':
            return await this.aiExplainCode(args);
          case 'ai_generate_config':
            return await this.aiGenerateConfig(args);
          // Troubleshooting Tools
          case 'list_troubleshooting_scripts':
            return await this.listTroubleshootingScripts(args);
          case 'run_troubleshooting_script':
            return await this.runTroubleshootingScript(args);
          case 'diagnose_deployment_issue':
            return await this.diagnoseDeploymentIssue(args);
          case 'get_instance_logs':
            return await this.getInstanceLogs(args);
          default:
            return {
              content: [{ type: 'text', text: `Tool ${name} not implemented.` }],
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

  // Input validation for all tools
  validateToolInput(toolName, args) {
    if (!args) args = {};

    switch (toolName) {
      case 'analyze_project_intelligently':
        if (!args.project_path && !args.project_files) {
          return 'Either project_path or project_files must be provided';
        }
        if (args.project_files && !Array.isArray(args.project_files)) {
          return 'project_files must be an array';
        }
        break;

      case 'generate_smart_deployment_config':
        if (!args.analysis_result) {
          return 'analysis_result is required';
        }
        if (!args.app_name) {
          return 'app_name is required';
        }
        if (args.app_name && !/^[a-zA-Z][a-zA-Z0-9-_]*$/.test(args.app_name)) {
          return 'app_name must start with a letter and contain only letters, numbers, hyphens, and underscores';
        }
        break;

      case 'setup_intelligent_deployment':
        if (!args.app_name) {
          return 'app_name is required';
        }
        if (args.app_name && !/^[a-zA-Z][a-zA-Z0-9-_]*$/.test(args.app_name)) {
          return 'app_name must start with a letter and contain only letters, numbers, hyphens, and underscores';
        }
        break;

      case 'optimize_infrastructure_costs':
        if (!args.current_config) {
          return 'current_config is required';
        }
        break;

      case 'detect_security_requirements':
        if (!args.project_analysis) {
          return 'project_analysis is required';
        }
        break;

      case 'check_deployment_status':
        if (!args.instance_name) {
          return 'instance_name is required';
        }
        break;

      case 'validate_deployment_config':
        if (!args.config && !args.config_path) {
          return 'Either config or config_path must be provided';
        }
        break;

      // AI tool validations
      case 'ai_analyze_project':
        if (!args.project_files || !Array.isArray(args.project_files)) {
          return 'project_files array is required';
        }
        if (args.project_files.length === 0) {
          return 'project_files cannot be empty';
        }
        break;

      case 'ai_troubleshoot':
        if (!args.error_message) {
          return 'error_message is required';
        }
        break;

      case 'ai_ask_expert':
        if (!args.question) {
          return 'question is required';
        }
        break;

      case 'ai_review_config':
        if (!args.config && !args.config_yaml) {
          return 'Either config or config_yaml must be provided';
        }
        break;

      case 'ai_explain_code':
        if (!args.code) {
          return 'code is required';
        }
        break;

      case 'ai_generate_config':
        if (!args.analysis) {
          return 'analysis is required';
        }
        break;

      // Troubleshooting tool validations
      case 'list_troubleshooting_scripts':
        // No required parameters
        break;

      case 'run_troubleshooting_script':
        if (!args.script_name) {
          return 'script_name is required';
        }
        if (!args.category) {
          return 'category is required';
        }
        if (!args.instance_name) {
          return 'instance_name is required';
        }
        break;

      case 'diagnose_deployment_issue':
        if (!args.instance_name) {
          return 'instance_name is required';
        }
        if (!args.error_description) {
          return 'error_description is required';
        }
        break;

      case 'get_instance_logs':
        if (!args.instance_name) {
          return 'instance_name is required';
        }
        break;
    }

    return null; // No validation errors
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
      github_config = {},
      aws_credentials = null,
      execute_actions = true  // Actually perform operations via setup script
    } = args;

    if (!app_name) {
      return {
        content: [{ type: 'text', text: '❌ Error: app_name is required' }],
        isError: true
      };
    }

    const results = {
      analysis: null,
      setupScriptOutput: null,
      errors: []
    };

    try {
      // Step 1: Analyze project
      console.log('📊 Step 1: Analyzing project...');
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
      results.analysis = analysis;

      const appType = analysis.detected_type || 'nodejs';
      const instanceName = deployment_preferences.instance_name || `${appType}-${app_name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
      const awsRegion = deployment_preferences.aws_region || 'us-east-1';
      const bundleId = analysis.infrastructure_needs?.bundle_size || 'micro_3_0';

      // Determine project path for file writing
      const targetPath = project_path || process.cwd();

      if (execute_actions) {
        // Use setup-complete-deployment.sh script with AUTO_MODE
        console.log('🚀 Step 2: Running setup-complete-deployment.sh with AUTO_MODE...');
        
        // Build environment variables for the setup script
        const githubRepo = github_config.repository 
          ? (github_config.username ? `${github_config.username}/${github_config.repository}` : github_config.repository)
          : '';
        
        // Database configuration
        const hasDatabase = analysis.databases && analysis.databases.length > 0;
        const dbType = hasDatabase ? analysis.databases[0].type : 'none';
        
        const envVars = {
          AUTO_MODE: 'true',
          APP_TYPE: appType,
          APP_NAME: app_name,
          INSTANCE_NAME: instanceName,
          AWS_REGION: awsRegion,
          BUNDLE_ID: bundleId,
          BLUEPRINT_ID: 'ubuntu_22_04',
          DATABASE_TYPE: dbType,
          DB_NAME: deployment_preferences.db_name || 'app_db',
          GITHUB_REPO: githubRepo,
          REPO_VISIBILITY: github_config.visibility || 'public',
          HEALTH_CHECK_ENDPOINT: deployment_preferences.health_check_endpoint || '/health',
          VERIFICATION_ENDPOINT: deployment_preferences.verification_endpoint || '/',
          API_ONLY_APP: deployment_preferences.api_only_app ? 'true' : 'false'
        };
        
        // Add bucket config if needed
        if (analysis.storage_needs?.needs_bucket || deployment_preferences.bucket_name) {
          envVars.ENABLE_BUCKET = 'true';
          envVars.BUCKET_NAME = deployment_preferences.bucket_name || `${app_name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-bucket`;
          envVars.BUCKET_ACCESS = deployment_preferences.bucket_access || 'read_write';
        }
        
        // Build the command with environment variables
        const envString = Object.entries(envVars)
          .map(([k, v]) => `${k}="${v}"`)
          .join(' ');
        
        // Get the script path relative to the MCP server
        const __filename = fileURLToPath(import.meta.url);
        const __dirname = path.dirname(__filename);
        const scriptPath = path.resolve(__dirname, '..', 'setup-complete-deployment.sh');
        
        try {
          // Change to the project directory and run the setup script
          const command = `cd "${targetPath}" && ${envString} bash "${scriptPath}"`;
          console.log(`Running: ${command}`);
          
          const output = execSync(command, {
            encoding: 'utf8',
            timeout: 600000, // 10 minute timeout
            maxBuffer: 10 * 1024 * 1024, // 10MB buffer
            stdio: ['pipe', 'pipe', 'pipe']
          });
          
          results.setupScriptOutput = {
            success: true,
            output: output
          };
        } catch (e) {
          results.setupScriptOutput = {
            success: false,
            error: e.message,
            stdout: e.stdout,
            stderr: e.stderr
          };
          results.errors.push({ step: 'setupScript', error: e.message });
        }
      }

      // Build response
      const hasErrors = results.errors.length > 0;

      return {
        content: [{
          type: 'text',
          text: `# ${hasErrors ? '⚠️' : '🎉'} Deployment Setup ${hasErrors ? 'Completed with Warnings' : 'Complete'}

## Summary
- **App Name**: ${app_name}
- **App Type**: ${appType}
- **Instance Name**: ${instanceName}
- **Instance Size**: ${bundleId}
- **Region**: ${awsRegion}
- **Estimated Cost**: ${analysis.estimated_costs?.monthly_min || 3.50}-${analysis.estimated_costs?.monthly_max || 10}/month

## Actions Performed

### 1. Project Analysis ✅
- Detected type: ${appType}
- Frameworks: ${analysis.frameworks?.map(f => f.name).join(', ') || 'None detected'}
- Database: ${analysis.databases?.length > 0 ? analysis.databases[0].type : 'None'}

### 2. Setup Script ${results.setupScriptOutput?.success ? '✅' : '❌'}
${results.setupScriptOutput?.success 
  ? `The setup-complete-deployment.sh script ran successfully!
  
This script handles:
- Creating Lightsail instance (via GitHub Actions)
- Setting up IAM roles for GitHub OIDC
- Configuring GitHub secrets
- Creating deployment workflow

**Script Output (last 50 lines):**
\`\`\`
${results.setupScriptOutput.output?.split('\n').slice(-50).join('\n') || 'No output'}
\`\`\``
  : `- Error: ${results.errors.find(e => e.step === 'setupScript')?.error || 'Not executed'}
${results.setupScriptOutput?.stderr ? `\n**Error Output:**\n\`\`\`\n${results.setupScriptOutput.stderr}\n\`\`\`` : ''}`}

## Next Steps

${hasErrors ? `### ⚠️ Fix Errors First
${results.errors.map(e => `- **${e.step}**: ${e.error}`).join('\n')}

` : ''}### Monitor Deployment
1. Check GitHub Actions: Go to your repository's Actions tab
2. The workflow will automatically:
   - Create the Lightsail instance
   - Deploy your application
   - Run health checks

### Verify Deployment
Once the GitHub Action completes, your app will be available at the instance's public IP.

\`\`\`bash
# Check instance status
aws lightsail get-instance --instance-name ${instanceName} --region ${awsRegion}
\`\`\``
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Setup failed: ${error.message}\n\nStack: ${error.stack}` }],
        isError: true
      };
    }
  }

  /**
   * Generate deployment configuration YAML
   */
  generateDeploymentConfigYaml(analysis, appName, deploymentPreferences) {
    const appType = analysis.detected_type || 'nodejs';
    const instanceName = `${appType}-${appName.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
    const awsRegion = deploymentPreferences.aws_region || 'us-east-1';
    const bundleId = analysis.infrastructure_needs?.bundle_size || 'micro_3_0';
    
    // Database configuration
    const hasDatabase = analysis.databases && analysis.databases.length > 0;
    const dbType = hasDatabase ? analysis.databases[0].type : 'none';
    const dbName = deploymentPreferences.db_name || 'app_db';
    
    // Bucket configuration
    const needsBucket = analysis.storage_needs?.needs_bucket || false;
    const bucketName = deploymentPreferences.bucket_name || `${appName.toLowerCase().replace(/[^a-z0-9]/g, '-')}-bucket`;

    let config = `# ${appName} Deployment Configuration
# Generated by MCP Server

aws:
  region: ${awsRegion}

lightsail:
  instance_name: ${instanceName}
  static_ip: ""
  bundle_id: "${bundleId}"
  blueprint_id: "ubuntu_22_04"
`;

    if (needsBucket) {
      config += `
  bucket:
    enabled: true
    name: "${bucketName}"
    access_level: "read_write"
    bundle_id: "small_1_0"
`;
    }

    config += `
application:
  name: ${appName.toLowerCase()}
  version: "1.0.0"
  type: ${appType}
  
  package_files:
    - "./"
  
  package_fallback: true
  
  environment_variables:
    APP_ENV: production
    NODE_ENV: production
`;

    if (dbType !== 'none') {
      config += `    DB_TYPE: ${dbType}
    DB_HOST: localhost
    DB_NAME: ${dbName}
    DB_USER: app_user
    DB_PASSWORD: CHANGE_ME_secure_password_123
`;
    }

    // Add type-specific config
    if (appType === 'nodejs') {
      const port = analysis.port || 3000;
      config += `    PORT: "${port}"
`;
    }

    config += `
dependencies:
`;

    // Database dependencies
    if (dbType === 'mysql') {
      config += `  mysql:
    enabled: true
    external: false
    config:
      version: "8.0"
      root_password: "CHANGE_ME_root_password_123"
      create_database: "${dbName}"
      create_user: "app_user"
      user_password: "CHANGE_ME_secure_password_123"
`;
    } else if (dbType === 'postgresql') {
      config += `  postgresql:
    enabled: true
    external: false
    config:
      version: "13"
      postgres_password: "CHANGE_ME_postgres_password_123"
      create_database: "${dbName}"
      create_user: "app_user"
      user_password: "CHANGE_ME_secure_password_123"
`;
    } else if (dbType === 'mongodb') {
      config += `  mongodb:
    enabled: true
    external: false
    config:
      version: "7.0"
      database: "${dbName}"
      auth_enabled: false
      bind_ip: "127.0.0.1"
      port: 27017
`;
    }

    // App-type specific dependencies
    if (appType === 'nodejs') {
      config += `
  nodejs:
    enabled: true
    config:
      version: "18"
      package_manager: "npm"
      
  pm2:
    enabled: true
    config:
      app_name: "${appName.toLowerCase()}"
      instances: 1
      exec_mode: "cluster"
`;
    } else if (appType === 'python') {
      config += `
  python:
    enabled: true
    config:
      version: "3.9"
      pip_packages:
        - flask
        - gunicorn
        
  gunicorn:
    enabled: true
    config:
      app_module: "app:app"
      workers: 2
      bind: "0.0.0.0:5000"
`;
    }

    config += `
  git:
    enabled: true
    config:
      install_lfs: false
  
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"
        - "80"
        - "443"
      deny_all_other: true

deployment:
  timeouts:
    ssh_connection: 120
    command_execution: 600
    health_check: 180
  
  retries:
    max_attempts: 3
    ssh_connection: 5
  
  steps:
    pre_deployment:
      common:
        enabled: true
        update_packages: true
        create_directories: true
        backup_enabled: true
    
    post_deployment:
      common:
        enabled: true
        verify_extraction: true
        create_env_file: true
        cleanup_temp_files: true
    
    verification:
      enabled: true
      health_check: true
      external_connectivity: true
      endpoints_to_test:
        - "/"
        - "/api/health"

github_actions:
  triggers:
    push_branches:
      - main
      - master
    workflow_dispatch: true
`;

    return config;
  }

  /**
   * Generate GitHub workflow YAML
   */
  generateGitHubWorkflowYaml(analysis, appName, instanceName, awsRegion) {
    const appType = analysis.detected_type || 'nodejs';
    
    return `# GitHub Actions Workflow for ${appName}
# Generated by MCP Server
# Deploys to AWS Lightsail using OIDC authentication

name: Deploy ${appName} to Lightsail

on:
  push:
    branches:
      - main
      - master
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: \${{ secrets.AWS_ROLE_ARN }}
          aws-region: \${{ secrets.AWS_REGION }}
      
      - name: Deploy to Lightsail
        uses: naveenraj44125-creator/lamp-stack-lightsail/.github/workflows/reusable-deploy.yml@main
        with:
          instance_name: \${{ secrets.LIGHTSAIL_INSTANCE_NAME }}
          aws_region: \${{ secrets.AWS_REGION }}
          app_type: ${appType}
          config_file: deployment-${appType}.config.yml
`;
  }

  generateEnvVarsForSetup(analysis, appName, deploymentPreferences, githubConfig) {
    const appType = analysis.detected_type || 'nodejs';
    const instanceName = `${appType}-${appName.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
    const awsRegion = deploymentPreferences.aws_region || 'us-east-1';
    
    // Database configuration
    const hasDatabase = analysis.databases && analysis.databases.length > 0;
    const dbType = hasDatabase ? analysis.databases[0].type : 'none';
    const dbExternal = hasDatabase && analysis.scale_preference !== 'small' && dbType !== 'mongodb';
    const dbName = deploymentPreferences.db_name || 'app_db';
    
    // Bucket configuration
    const needsBucket = analysis.storage_needs?.needs_bucket || false;
    const bucketName = deploymentPreferences.bucket_name || (needsBucket ? `${appName.toLowerCase().replace(/[^a-z0-9]/g, '-')}-bucket` : '');
    
    // Bundle size
    const bundleSize = analysis.infrastructure_needs?.bundle_size || 'micro_3_0';
    
    // Build environment variables string
    let envVars = `export FULLY_AUTOMATED=true
export APP_TYPE="${appType}"
export APP_NAME="${appName}"
export INSTANCE_NAME="${instanceName}"
export AWS_REGION="${awsRegion}"
export BLUEPRINT_ID="ubuntu_22_04"
export BUNDLE_ID="${bundleSize}"
export DATABASE_TYPE="${dbType}"
export DB_EXTERNAL="${dbExternal ? 'true' : 'false'}"
export DB_NAME="${dbName}"
export ENABLE_BUCKET="${needsBucket ? 'true' : 'false'}"`;

    if (needsBucket) {
      envVars += `
export BUCKET_NAME="${bucketName}"
export BUCKET_ACCESS="${deploymentPreferences.bucket_access || 'read_write'}"
export BUCKET_BUNDLE="${deploymentPreferences.bucket_bundle || 'small_1_0'}"`;
    }

    if (githubConfig.visibility) {
      envVars += `
export REPO_VISIBILITY="${githubConfig.visibility}"`;
    }

    if (githubConfig.username) {
      envVars += `
export GITHUB_USERNAME="${githubConfig.username}"`;
    }

    if (githubConfig.repository) {
      envVars += `
export GITHUB_REPO="${githubConfig.repository}"`;
    }

    return envVars;
  }

  generateSetupScript(analysis, appName, deploymentPreferences, githubConfig) {
    const appType = analysis.detected_type || 'nodejs';
    const instanceName = `${appType}-${appName.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;
    const awsRegion = deploymentPreferences.aws_region || 'us-east-1';
    
    // Database configuration
    const hasDatabase = analysis.databases && analysis.databases.length > 0;
    const dbType = hasDatabase ? analysis.databases[0].type : 'none';
    const dbExternal = hasDatabase && analysis.scale_preference !== 'small' && dbType !== 'mongodb'; // MongoDB doesn't support RDS
    const dbName = deploymentPreferences.db_name || 'app_db';
    const dbRdsName = deploymentPreferences.db_rds_name || (dbExternal ? `${appType}-${dbType}-db` : '');
    
    // MongoDB-specific configuration
    const isMongoDb = dbType === 'mongodb';
    const mongoDbUser = deploymentPreferences.mongodb_user || 'app_user';
    const mongoDbPort = deploymentPreferences.mongodb_port || '27017';
    
    // Bucket configuration
    const needsBucket = analysis.storage_needs?.needs_bucket || false;
    const bucketName = deploymentPreferences.bucket_name || (needsBucket ? `${appName.toLowerCase().replace(/[^a-z0-9]/g, '-')}-bucket` : '');
    const bucketAccess = deploymentPreferences.bucket_access || 'read_write';
    const bucketBundle = deploymentPreferences.bucket_bundle || 'small_1_0';
    
    // API-only app configuration (for apps without root route)
    const apiOnlyApp = deploymentPreferences.api_only_app || false;
    const verificationEndpoint = deploymentPreferences.verification_endpoint || '';
    const healthCheckEndpoint = deploymentPreferences.health_check_endpoint || '';
    const expectedContent = deploymentPreferences.expected_content || '';
    
    // Get bundle size safely
    const bundleSize = analysis.infrastructure_needs?.bundle_size || 'micro_3_0';
    
    // Build MongoDB-specific exports
    const mongoDbExports = isMongoDb ? `
# MongoDB-specific configuration
export MONGODB_USER="${mongoDbUser}"
export MONGODB_PORT="${mongoDbPort}"
export MONGODB_URI="mongodb://${mongoDbUser}:CHANGE_ME_PASSWORD@localhost:${mongoDbPort}/${dbName}"` : '';
    
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
export BUNDLE_ID="${bundleSize}"

# Database configuration
export DATABASE_TYPE="${dbType}"
export DB_EXTERNAL="${dbExternal ? 'true' : 'false'}"
export DB_NAME="${dbName}"
${dbExternal ? `export DB_RDS_NAME="${dbRdsName}"` : '# DB_RDS_NAME not needed for local database'}${mongoDbExports}

# Bucket configuration
export ENABLE_BUCKET="${needsBucket ? 'true' : 'false'}"
${needsBucket ? `export BUCKET_NAME="${bucketName}"
export BUCKET_ACCESS="${bucketAccess}"
export BUCKET_BUNDLE="${bucketBundle}"` : '# Bucket not enabled'}

# GitHub configuration
export REPO_VISIBILITY="${githubConfig.visibility || 'private'}"
${githubConfig.username ? `export GITHUB_USERNAME="${githubConfig.username}"` : ''}
${githubConfig.repository ? `export GITHUB_REPO="${githubConfig.repository}"` : ''}

# API-only app configuration (for apps without root route)
export API_ONLY_APP="${apiOnlyApp ? 'true' : 'false'}"
${verificationEndpoint ? `export VERIFICATION_ENDPOINT="${verificationEndpoint}"` : '# Using default verification endpoint'}
${healthCheckEndpoint ? `export HEALTH_CHECK_ENDPOINT="${healthCheckEndpoint}"` : '# Using default health check endpoint'}
${expectedContent ? `export EXPECTED_CONTENT="${expectedContent}"` : '# Using default expected content'}

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

  // New tool: List Lightsail instances
  async listLightsailInstances(args) {
    const { aws_region = 'us-east-1', filter_by_name = '', include_stopped = true } = args;

    try {
      // Execute AWS CLI command to list instances
      const command = `aws lightsail get-instances --region ${aws_region} --output json`;
      const result = execSync(command, { encoding: 'utf8', timeout: 30000 });
      const data = JSON.parse(result);

      if (!data.instances || data.instances.length === 0) {
        return {
          content: [{
            type: 'text',
            text: `# 📋 Lightsail Instances in ${aws_region}

No instances found in this region.

To create a new instance, use the \`setup_intelligent_deployment\` tool.`
          }]
        };
      }

      // Filter instances
      let instances = data.instances;
      
      if (filter_by_name) {
        instances = instances.filter(i => 
          i.name.toLowerCase().includes(filter_by_name.toLowerCase())
        );
      }

      if (!include_stopped) {
        instances = instances.filter(i => i.state.name === 'running');
      }

      // Format instance information
      const instanceList = instances.map(i => {
        const state = i.state.name;
        const stateEmoji = state === 'running' ? '🟢' : state === 'stopped' ? '🔴' : '🟡';
        return `### ${stateEmoji} ${i.name}
- **State**: ${state}
- **Public IP**: ${i.publicIpAddress || 'No public IP'}
- **Private IP**: ${i.privateIpAddress || 'N/A'}
- **Bundle**: ${i.bundleId}
- **Blueprint**: ${i.blueprintId}
- **Created**: ${new Date(i.createdAt).toLocaleDateString()}
- **Region**: ${i.location.regionName}
- **Availability Zone**: ${i.location.availabilityZone}`;
      }).join('\n\n');

      const runningCount = instances.filter(i => i.state.name === 'running').length;
      const stoppedCount = instances.filter(i => i.state.name === 'stopped').length;

      return {
        content: [{
          type: 'text',
          text: `# 📋 Lightsail Instances in ${aws_region}

## Summary
- **Total Instances**: ${instances.length}
- **Running**: ${runningCount} 🟢
- **Stopped**: ${stoppedCount} 🔴
${filter_by_name ? `- **Filter**: "${filter_by_name}"` : ''}

## Instance Details

${instanceList}

---
Use \`check_deployment_status\` to check the health of a specific instance.`
        }]
      };
    } catch (error) {
      // Check if AWS CLI is not configured
      if (error.message.includes('Unable to locate credentials') || 
          error.message.includes('could not be found')) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ AWS CLI Not Configured

Unable to list Lightsail instances. Please ensure:

1. AWS CLI is installed: \`aws --version\`
2. AWS credentials are configured: \`aws configure\`
3. You have permissions to access Lightsail

**Quick Setup:**
\`\`\`bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=${aws_region}
\`\`\`

Error: ${error.message}`
          }],
          isError: true
        };
      }

      return {
        content: [{ type: 'text', text: `❌ Failed to list instances: ${error.message}` }],
        isError: true
      };
    }
  }

  // New tool: Check deployment status
  async checkDeploymentStatus(args) {
    const { 
      instance_name, 
      aws_region = 'us-east-1', 
      health_check_endpoint = '/',
      health_check_port = 80,
      expected_content = ''
    } = args;

    try {
      // Get instance details
      const instanceCommand = `aws lightsail get-instance --instance-name "${instance_name}" --region ${aws_region} --output json`;
      let instanceData;
      
      try {
        const result = execSync(instanceCommand, { encoding: 'utf8', timeout: 30000 });
        instanceData = JSON.parse(result).instance;
      } catch (e) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ Instance Not Found

Instance \`${instance_name}\` was not found in region \`${aws_region}\`.

**Possible reasons:**
- Instance name is incorrect
- Instance is in a different region
- Instance has been deleted

Use \`list_lightsail_instances\` to see available instances.`
          }],
          isError: true
        };
      }

      const publicIp = instanceData.publicIpAddress;
      const state = instanceData.state.name;
      const stateEmoji = state === 'running' ? '🟢' : state === 'stopped' ? '🔴' : '🟡';

      // If instance is not running, return early
      if (state !== 'running') {
        return {
          content: [{
            type: 'text',
            text: `# 📊 Deployment Status: ${instance_name}

## Instance Status
- **State**: ${stateEmoji} ${state.toUpperCase()}
- **Public IP**: ${publicIp || 'No public IP'}
- **Bundle**: ${instanceData.bundleId}
- **Blueprint**: ${instanceData.blueprintId}

## ⚠️ Instance Not Running

The instance is currently ${state}. Health checks cannot be performed.

**To start the instance:**
\`\`\`bash
aws lightsail start-instance --instance-name "${instance_name}" --region ${aws_region}
\`\`\`

Then run this check again.`
          }]
        };
      }

      // Perform health check
      let healthStatus = 'unknown';
      let healthDetails = '';
      let responseTime = 0;

      if (publicIp) {
        const healthUrl = `http://${publicIp}:${health_check_port}${health_check_endpoint}`;
        
        try {
          const startTime = Date.now();
          const curlCommand = `curl -s -o /dev/null -w "%{http_code}|%{time_total}" --connect-timeout 10 --max-time 30 "${healthUrl}"`;
          const curlResult = execSync(curlCommand, { encoding: 'utf8', timeout: 35000 });
          const [httpCode, timeTotal] = curlResult.split('|');
          responseTime = Math.round(parseFloat(timeTotal) * 1000);

          if (httpCode === '200') {
            healthStatus = 'healthy';
            
            // Check for expected content if specified
            if (expected_content) {
              const contentCommand = `curl -s --connect-timeout 10 --max-time 30 "${healthUrl}"`;
              const content = execSync(contentCommand, { encoding: 'utf8', timeout: 35000 });
              
              if (content.includes(expected_content)) {
                healthDetails = `Response contains expected content: "${expected_content}"`;
              } else {
                healthStatus = 'degraded';
                healthDetails = `Response does not contain expected content: "${expected_content}"`;
              }
            }
          } else if (httpCode === '301' || httpCode === '302') {
            healthStatus = 'redirect';
            healthDetails = `Redirecting (HTTP ${httpCode}) - may need to check HTTPS`;
          } else if (httpCode === '000') {
            healthStatus = 'unreachable';
            healthDetails = 'Connection failed - service may not be running';
          } else {
            healthStatus = 'unhealthy';
            healthDetails = `HTTP ${httpCode} response`;
          }
        } catch (e) {
          healthStatus = 'unreachable';
          healthDetails = `Health check failed: ${e.message}`;
        }
      }

      const healthEmoji = {
        'healthy': '✅',
        'degraded': '⚠️',
        'unhealthy': '❌',
        'unreachable': '🔴',
        'redirect': '↪️',
        'unknown': '❓'
      }[healthStatus];

      // Get open ports
      let openPorts = [];
      try {
        const portsCommand = `aws lightsail get-instance-port-states --instance-name "${instance_name}" --region ${aws_region} --output json`;
        const portsResult = execSync(portsCommand, { encoding: 'utf8', timeout: 30000 });
        const portsData = JSON.parse(portsResult);
        openPorts = portsData.portStates || [];
      } catch (e) {
        // Ignore port check errors
      }

      return {
        content: [{
          type: 'text',
          text: `# 📊 Deployment Status: ${instance_name}

## Instance Status
- **State**: ${stateEmoji} ${state.toUpperCase()}
- **Public IP**: ${publicIp || 'No public IP'}
- **Bundle**: ${instanceData.bundleId}
- **Blueprint**: ${instanceData.blueprintId}
- **Region**: ${instanceData.location.regionName}

## Health Check
- **Status**: ${healthEmoji} ${healthStatus.toUpperCase()}
- **Endpoint**: http://${publicIp}:${health_check_port}${health_check_endpoint}
- **Response Time**: ${responseTime}ms
${healthDetails ? `- **Details**: ${healthDetails}` : ''}

## Open Ports
${openPorts.length > 0 ? 
  openPorts.map(p => `- Port ${p.fromPort}${p.fromPort !== p.toPort ? `-${p.toPort}` : ''} (${p.protocol}): ${p.state}`).join('\n') :
  '- No port information available'
}

## Quick Actions

**SSH into instance:**
\`\`\`bash
ssh -i ~/.ssh/lightsail-key.pem ubuntu@${publicIp}
\`\`\`

**View application logs:**
\`\`\`bash
# For Node.js (PM2)
pm2 logs

# For Apache/PHP
sudo tail -f /var/log/apache2/error.log

# For Docker
docker-compose logs -f
\`\`\`

**Restart services:**
\`\`\`bash
# For Node.js (PM2)
pm2 restart all

# For Apache
sudo systemctl restart apache2

# For Docker
docker-compose restart
\`\`\`

---
${healthStatus === 'healthy' ? '🎉 Your deployment is healthy and running!' : 
  healthStatus === 'unreachable' ? '⚠️ Application may not be running. Check the logs for errors.' :
  '⚠️ There may be issues with your deployment. Check the logs for details.'}`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Failed to check deployment status: ${error.message}` }],
        isError: true
      };
    }
  }

  // New tool: Validate deployment configuration
  async validateDeploymentConfig(args) {
    const { config, config_path, strict_mode = false } = args;

    let configToValidate = config;

    // Load config from file if path provided
    if (config_path && !config) {
      try {
        const configContent = fs.readFileSync(config_path, 'utf8');
        // Simple YAML parsing (for basic validation)
        configToValidate = this.parseSimpleYAML(configContent);
      } catch (e) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ Configuration File Error

Unable to read configuration file: \`${config_path}\`

Error: ${e.message}

Make sure the file exists and is readable.`
          }],
          isError: true
        };
      }
    }

    const errors = [];
    const warnings = [];
    const suggestions = [];

    // Validate required sections
    if (!configToValidate.aws) {
      errors.push('Missing required section: `aws`');
    } else {
      if (!configToValidate.aws.region) {
        warnings.push('`aws.region` not specified, will default to us-east-1');
      }
    }

    if (!configToValidate.lightsail) {
      errors.push('Missing required section: `lightsail`');
    } else {
      if (!configToValidate.lightsail.instance_name) {
        errors.push('Missing required field: `lightsail.instance_name`');
      }
      
      // Validate bundle_id
      const validBundles = ['nano_3_0', 'micro_3_0', 'small_3_0', 'medium_3_0', 'large_3_0', 'xlarge_3_0'];
      if (configToValidate.lightsail.bundle_id && !validBundles.includes(configToValidate.lightsail.bundle_id)) {
        warnings.push(`Unknown bundle_id: ${configToValidate.lightsail.bundle_id}. Valid options: ${validBundles.join(', ')}`);
      }

      // Validate blueprint_id
      const validBlueprints = ['ubuntu_22_04', 'ubuntu_20_04', 'amazon_linux_2', 'amazon_linux_2023', 'debian_11'];
      if (configToValidate.lightsail.blueprint_id && !validBlueprints.includes(configToValidate.lightsail.blueprint_id)) {
        warnings.push(`Unknown blueprint_id: ${configToValidate.lightsail.blueprint_id}. Common options: ${validBlueprints.join(', ')}`);
      }
    }

    if (!configToValidate.application) {
      errors.push('Missing required section: `application`');
    } else {
      if (!configToValidate.application.name) {
        errors.push('Missing required field: `application.name`');
      }
      if (!configToValidate.application.type) {
        errors.push('Missing required field: `application.type`');
      } else {
        const validTypes = ['lamp', 'nodejs', 'python', 'react', 'docker', 'nginx'];
        if (!validTypes.includes(configToValidate.application.type)) {
          errors.push(`Invalid application type: ${configToValidate.application.type}. Valid options: ${validTypes.join(', ')}`);
        }
      }
    }

    // Validate dependencies
    if (configToValidate.dependencies) {
      // Check for conflicting database configurations
      const enabledDbs = [];
      if (configToValidate.dependencies.mysql?.enabled) enabledDbs.push('mysql');
      if (configToValidate.dependencies.postgresql?.enabled) enabledDbs.push('postgresql');
      if (configToValidate.dependencies.mongodb?.enabled) enabledDbs.push('mongodb');
      
      if (enabledDbs.length > 1) {
        warnings.push(`Multiple databases enabled (${enabledDbs.join(', ')}). This may increase resource usage.`);
      }

      // Check for default passwords
      const checkDefaultPasswords = (obj, path = '') => {
        if (typeof obj === 'object' && obj !== null) {
          for (const [key, value] of Object.entries(obj)) {
            const currentPath = path ? `${path}.${key}` : key;
            if (typeof value === 'string' && 
                (key.toLowerCase().includes('password') || key.toLowerCase().includes('secret')) &&
                (value.includes('CHANGE_ME') || value === 'password' || value === 'secret')) {
              warnings.push(`Default password detected at \`${currentPath}\`. Change before production deployment.`);
            }
            if (typeof value === 'object') {
              checkDefaultPasswords(value, currentPath);
            }
          }
        }
      };
      checkDefaultPasswords(configToValidate);
    }

    // Validate deployment section
    if (!configToValidate.deployment) {
      suggestions.push('Consider adding a `deployment` section for timeout and retry configuration');
    }

    // Validate monitoring section
    if (!configToValidate.monitoring) {
      suggestions.push('Consider adding a `monitoring` section for health checks');
    } else {
      if (!configToValidate.monitoring.health_check?.endpoint) {
        suggestions.push('Consider specifying a health check endpoint in `monitoring.health_check.endpoint`');
      }
    }

    // Validate security section
    if (!configToValidate.security) {
      suggestions.push('Consider adding a `security` section for file permissions and SSL configuration');
    }

    // Determine overall status
    const isValid = errors.length === 0 && (!strict_mode || warnings.length === 0);
    const statusEmoji = isValid ? '✅' : errors.length > 0 ? '❌' : '⚠️';

    return {
      content: [{
        type: 'text',
        text: `# ${statusEmoji} Configuration Validation Results

## Status: ${isValid ? 'VALID' : errors.length > 0 ? 'INVALID' : 'VALID WITH WARNINGS'}

${errors.length > 0 ? `## ❌ Errors (${errors.length})
${errors.map(e => `- ${e}`).join('\n')}

` : ''}${warnings.length > 0 ? `## ⚠️ Warnings (${warnings.length})
${warnings.map(w => `- ${w}`).join('\n')}

` : ''}${suggestions.length > 0 ? `## 💡 Suggestions (${suggestions.length})
${suggestions.map(s => `- ${s}`).join('\n')}

` : ''}## Summary
- **Errors**: ${errors.length}
- **Warnings**: ${warnings.length}
- **Suggestions**: ${suggestions.length}
- **Strict Mode**: ${strict_mode ? 'Enabled' : 'Disabled'}

${isValid ? '✅ Configuration is ready for deployment!' : 
  errors.length > 0 ? '❌ Please fix the errors before deploying.' :
  '⚠️ Configuration is valid but has warnings. Review before deploying.'}`
      }]
    };
  }

  // Simple YAML parser for basic validation
  parseSimpleYAML(content) {
    // This is a very basic YAML parser for validation purposes
    // For production, use a proper YAML library
    const result = {};
    const lines = content.split('\n');
    const stack = [{ obj: result, indent: -1 }];

    for (const line of lines) {
      // Skip comments and empty lines
      if (line.trim().startsWith('#') || line.trim() === '') continue;

      const indent = line.search(/\S/);
      const trimmed = line.trim();

      // Handle key-value pairs
      const colonIndex = trimmed.indexOf(':');
      if (colonIndex > 0) {
        const key = trimmed.substring(0, colonIndex).trim();
        let value = trimmed.substring(colonIndex + 1).trim();

        // Pop stack to find parent
        while (stack.length > 1 && stack[stack.length - 1].indent >= indent) {
          stack.pop();
        }

        const parent = stack[stack.length - 1].obj;

        if (value === '' || value === '|' || value === '>') {
          // Nested object or multiline string
          parent[key] = {};
          stack.push({ obj: parent[key], indent });
        } else {
          // Simple value
          // Remove quotes
          if ((value.startsWith('"') && value.endsWith('"')) ||
              (value.startsWith("'") && value.endsWith("'"))) {
            value = value.slice(1, -1);
          }
          // Parse booleans and numbers
          if (value === 'true') value = true;
          else if (value === 'false') value = false;
          else if (!isNaN(value) && value !== '') value = Number(value);
          
          parent[key] = value;
        }
      }
    }

    return result;
  }

  // ============================================
  // AI-Powered Tools (AWS Bedrock Integration)
  // ============================================

  /**
   * AI-powered project analysis using Bedrock
   */
  async aiAnalyzeProject(args) {
    const { project_files, user_description = '', aws_credentials } = args;

    try {
      const bedrockAI = this.getBedrockAI(aws_credentials);
      const result = await bedrockAI.analyzeProject(project_files, user_description);

      if (!result.success) {
        const credentialHint = aws_credentials ? 
          `\n**Credential Source**: ${aws_credentials.profile ? `Profile: ${aws_credentials.profile}` : 'Direct credentials provided'}` :
          `\n**Tip**: You can provide AWS credentials via the \`aws_credentials\` parameter:
- \`profile\`: AWS profile name from ~/.aws/credentials
- \`access_key_id\` + \`secret_access_key\`: Direct credentials
- \`region\`: AWS region (default: us-east-1)`;

        return {
          content: [{
            type: 'text',
            text: `# ❌ AI Analysis Failed

**Error**: ${result.error}
${credentialHint}

**Possible causes**:
- AWS credentials not configured or invalid
- Bedrock model not available in your region
- Insufficient permissions for Bedrock

**To fix**:
1. Provide credentials via \`aws_credentials\` parameter
2. Or ensure AWS credentials are configured: \`aws configure\`
3. Check Bedrock model access in AWS Console
4. Verify IAM permissions include \`bedrock:InvokeModel\`

Falling back to rule-based analysis...`
          }],
          isError: true
        };
      }

      const analysis = result.analysis;
      
      return {
        content: [{
          type: 'text',
          text: `# 🤖 AI-Powered Project Analysis

## 📊 Detection Results
${analysis ? `
- **Application Type**: ${analysis.detected_type} (${Math.round((analysis.confidence || 0) * 100)}% confidence)
- **Deployment Complexity**: ${analysis.deployment_complexity || 'Unknown'}
- **Estimated Cost**: $${analysis.estimated_costs?.monthly_min || '?'} - $${analysis.estimated_costs?.monthly_max || '?'}/month

## 🛠️ Detected Technologies
${analysis.frameworks?.map(f => `- **${f.name}** (${f.type})`).join('\n') || '- None detected'}

## 💾 Database Requirements
${analysis.databases?.map(db => `- **${db.type}** - ${db.name}`).join('\n') || '- No database needed'}

## 📦 Infrastructure Needs
- **Recommended Bundle**: ${analysis.infrastructure_needs?.bundle_size || 'micro_3_0'}
- **Memory Intensive**: ${analysis.infrastructure_needs?.memory_intensive ? 'Yes' : 'No'}
- **CPU Intensive**: ${analysis.infrastructure_needs?.cpu_intensive ? 'Yes' : 'No'}
- **Needs Bucket**: ${analysis.storage_needs?.needs_bucket ? 'Yes' : 'No'}

## 🔒 Security Considerations
- **Needs SSL**: ${analysis.security_considerations?.needs_ssl ? 'Yes' : 'No'}
- **Needs Auth**: ${analysis.security_considerations?.needs_auth ? 'Yes' : 'No'}
- **Handles User Data**: ${analysis.security_considerations?.handles_user_data ? 'Yes' : 'No'}

## 💡 AI Recommendations
${analysis.recommendations?.map(r => `- ${r}`).join('\n') || '- No specific recommendations'}

## ⚠️ Warnings
${analysis.warnings?.map(w => `- ${w}`).join('\n') || '- No warnings'}
` : result.rawResponse}

---
*Analysis powered by AWS Bedrock (Claude) | Credentials: ${bedrockAI.credentialSource}*

## 📋 Raw Analysis Data
\`\`\`json
${JSON.stringify(analysis || {}, null, 2)}
\`\`\``
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ AI Analysis Error: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * AI-powered troubleshooting
   */
  async aiTroubleshoot(args) {
    const { error_message, context = {}, aws_credentials } = args;

    try {
      const bedrockAI = this.getBedrockAI(aws_credentials);
      const result = await bedrockAI.troubleshoot(error_message, context);

      if (!result.success) {
        const credentialHint = aws_credentials ? 
          `\n\n**Credential Source**: ${aws_credentials.profile ? `Profile: ${aws_credentials.profile}` : 'Direct credentials provided'}` :
          `\n\n**Tip**: You can provide AWS credentials via the \`aws_credentials\` parameter:
- \`profile\`: AWS profile name from ~/.aws/credentials
- \`access_key_id\` + \`secret_access_key\`: Direct credentials
- \`region\`: AWS region (default: us-east-1)`;

        return {
          content: [{
            type: 'text',
            text: `# ❌ AI Troubleshooting Unavailable

**Error**: ${result.error}${credentialHint}`
          }],
          isError: true
        };
      }

      return {
        content: [{
          type: 'text',
          text: `# 🔧 AI Troubleshooting Analysis

${result.content}

---
*Troubleshooting powered by AWS Bedrock (Claude) | Credentials: ${bedrockAI.credentialSource}*`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ AI Troubleshooting Error: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * AI deployment expert Q&A
   */
  async aiAskExpert(args) {
    const { question, project_context = null, aws_credentials } = args;

    try {
      const bedrockAI = this.getBedrockAI(aws_credentials);
      const result = await bedrockAI.askExpert(question, project_context);

      if (!result.success) {
        const credentialHint = aws_credentials ? 
          `\n\n**Credential Source**: ${aws_credentials.profile ? `Profile: ${aws_credentials.profile}` : 'Direct credentials provided'}` :
          `\n\n**Tip**: You can provide AWS credentials via the \`aws_credentials\` parameter.`;

        return {
          content: [{
            type: 'text',
            text: `# ❌ AI Expert Unavailable

**Error**: ${result.error}${credentialHint}`
          }],
          isError: true
        };
      }

      return {
        content: [{
          type: 'text',
          text: `# 🎓 AI Deployment Expert

${result.content}

---
*Powered by AWS Bedrock (Claude) | Credentials: ${bedrockAI.credentialSource}*
*Tokens used: ${result.usage?.inputTokens || '?'} input, ${result.usage?.outputTokens || '?'} output*`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ AI Expert Error: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * AI-powered config review
   */
  async aiReviewConfig(args) {
    const { config, config_yaml, aws_credentials } = args;

    try {
      const bedrockAI = this.getBedrockAI(aws_credentials);
      const configToReview = config_yaml || JSON.stringify(config, null, 2);
      const result = await bedrockAI.reviewConfig(configToReview);

      if (!result.success) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ AI Review Unavailable

**Error**: ${result.error}

Please check your AWS Bedrock configuration or provide credentials via \`aws_credentials\`.`
          }],
          isError: true
        };
      }

      return {
        content: [{
          type: 'text',
          text: `# 🔍 AI Configuration Review

${result.content}

---
*Review powered by AWS Bedrock (Claude) | Credentials: ${bedrockAI.credentialSource}*`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ AI Review Error: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * AI-powered code explanation
   */
  async aiExplainCode(args) {
    const { code, filename = '', aws_credentials } = args;

    try {
      const bedrockAI = this.getBedrockAI(aws_credentials);
      const result = await bedrockAI.explainCode(code, filename);

      if (!result.success) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ AI Explanation Unavailable

**Error**: ${result.error}

Please check your AWS Bedrock configuration or provide credentials via \`aws_credentials\`.`
          }],
          isError: true
        };
      }

      return {
        content: [{
          type: 'text',
          text: `# 📖 AI Code Explanation

${result.content}

---
*Explanation powered by AWS Bedrock (Claude) | Credentials: ${bedrockAI.credentialSource}*`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ AI Explanation Error: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * AI-powered config generation
   */
  async aiGenerateConfig(args) {
    const { analysis, preferences = {}, aws_credentials } = args;

    try {
      const bedrockAI = this.getBedrockAI(aws_credentials);
      const result = await bedrockAI.generateConfig(analysis, preferences);

      if (!result.success) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ AI Config Generation Unavailable

**Error**: ${result.error}

Please check your AWS Bedrock configuration or provide credentials via \`aws_credentials\`.`
          }],
          isError: true
        };
      }

      return {
        content: [{
          type: 'text',
          text: `# ⚙️ AI-Generated Deployment Configuration

${result.content}

---
*Configuration generated by AWS Bedrock (Claude) | Credentials: ${bedrockAI.credentialSource}*`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ AI Config Generation Error: ${error.message}` }],
        isError: true
      };
    }
  }

  // ============================================
  // Troubleshooting Tools Implementation
  // ============================================

  /**
   * Get the path to troubleshooting tools directory
   */
  getTroubleshootingToolsPath() {
    // Get the directory of this script
    const scriptDir = path.dirname(fileURLToPath(import.meta.url));
    return path.resolve(scriptDir, '..', 'troubleshooting-tools');
  }

  /**
   * List available troubleshooting scripts
   */
  async listTroubleshootingScripts(args) {
    const { category = 'all' } = args;
    const toolsPath = this.getTroubleshootingToolsPath();

    try {
      const categories = category === 'all' 
        ? ['docker', 'general', 'lamp', 'nginx', 'nodejs', 'python', 'react']
        : [category];

      const scripts = {};
      
      for (const cat of categories) {
        const catPath = path.join(toolsPath, cat);
        
        if (fs.existsSync(catPath)) {
          const files = fs.readdirSync(catPath)
            .filter(f => f.endsWith('.py') && !f.startsWith('__'))
            .map(f => {
              const scriptPath = path.join(catPath, f);
              let description = '';
              
              // Try to extract description from script docstring
              try {
                const content = fs.readFileSync(scriptPath, 'utf8');
                const docMatch = content.match(/"""([^"]+)"""/);
                if (docMatch) {
                  description = docMatch[1].trim().split('\n')[0];
                }
              } catch (e) {
                // Ignore read errors
              }

              // Determine script type from name
              const isDebug = f.startsWith('debug-');
              const isFix = f.startsWith('fix-');
              const isVerify = f.includes('verify') || f.includes('check') || f.includes('test');
              
              return {
                name: f,
                type: isDebug ? 'debug' : isFix ? 'fix' : isVerify ? 'verify' : 'utility',
                description: description || `${isDebug ? 'Debug' : isFix ? 'Fix' : 'Utility'} script for ${cat} deployments`
              };
            });
          
          if (files.length > 0) {
            scripts[cat] = files;
          }
        }
      }

      // Format output
      let output = `# 🔧 Available Troubleshooting Scripts\n\n`;
      
      if (Object.keys(scripts).length === 0) {
        output += `No troubleshooting scripts found${category !== 'all' ? ` in category "${category}"` : ''}.\n`;
      } else {
        for (const [cat, files] of Object.entries(scripts)) {
          const emoji = {
            docker: '🐳',
            general: '🔧',
            lamp: '💡',
            nginx: '🌐',
            nodejs: '📦',
            python: '🐍',
            react: '⚛️'
          }[cat] || '📁';
          
          output += `## ${emoji} ${cat.charAt(0).toUpperCase() + cat.slice(1)}\n\n`;
          
          for (const file of files) {
            const typeEmoji = file.type === 'debug' ? '🔍' : file.type === 'fix' ? '🔧' : file.type === 'verify' ? '✅' : '📄';
            output += `- ${typeEmoji} **${file.name}** - ${file.description}\n`;
          }
          output += '\n';
        }

        output += `---\n\n`;
        output += `## 📖 Usage\n\n`;
        output += `To run a script, use the \`run_troubleshooting_script\` tool:\n\n`;
        output += `\`\`\`json\n`;
        output += `{\n`;
        output += `  "script_name": "debug-nodejs.py",\n`;
        output += `  "category": "nodejs",\n`;
        output += `  "instance_name": "my-instance",\n`;
        output += `  "aws_region": "us-east-1"\n`;
        output += `}\n`;
        output += `\`\`\`\n\n`;
        output += `Or use \`diagnose_deployment_issue\` for AI-powered diagnosis and automatic script selection.`;
      }

      return {
        content: [{ type: 'text', text: output }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Failed to list troubleshooting scripts: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * Run a specific troubleshooting script
   */
  async runTroubleshootingScript(args) {
    const { 
      script_name, 
      category, 
      instance_name, 
      aws_region = 'us-east-1',
      additional_args = {}
    } = args;

    const toolsPath = this.getTroubleshootingToolsPath();
    const scriptPath = path.join(toolsPath, category, script_name);

    try {
      // Verify script exists
      if (!fs.existsSync(scriptPath)) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ Script Not Found

Script \`${script_name}\` not found in category \`${category}\`.

Use \`list_troubleshooting_scripts\` to see available scripts.`
          }],
          isError: true
        };
      }

      // Build environment variables for the script
      const env = {
        ...process.env,
        INSTANCE_NAME: instance_name,
        AWS_REGION: aws_region,
        AUTOMATED_MODE: 'true',
        ...Object.fromEntries(
          Object.entries(additional_args).map(([k, v]) => [k.toUpperCase(), String(v)])
        )
      };

      // Run the script
      const startTime = Date.now();
      let output = '';
      let success = false;

      try {
        output = execSync(`python3 "${scriptPath}"`, {
          encoding: 'utf8',
          timeout: 300000, // 5 minute timeout
          env,
          input: `${instance_name}\n${aws_region}\nn\n`, // Provide default inputs
          stdio: ['pipe', 'pipe', 'pipe']
        });
        success = true;
      } catch (execError) {
        output = execError.stdout || execError.stderr || execError.message;
        success = false;
      }

      const duration = ((Date.now() - startTime) / 1000).toFixed(1);

      return {
        content: [{
          type: 'text',
          text: `# ${success ? '✅' : '⚠️'} Troubleshooting Script Results

## Script Information
- **Script**: ${script_name}
- **Category**: ${category}
- **Instance**: ${instance_name}
- **Region**: ${aws_region}
- **Duration**: ${duration}s
- **Status**: ${success ? 'Completed' : 'Completed with warnings/errors'}

## Output

\`\`\`
${output.slice(0, 10000)}${output.length > 10000 ? '\n... (output truncated)' : ''}
\`\`\`

${success ? '✅ Script completed successfully.' : '⚠️ Script completed with some issues. Review the output above.'}

---
${!success ? `\n**Next Steps:**\n- Review the error messages above\n- Try running a fix script if available\n- Use \`diagnose_deployment_issue\` for AI-powered analysis\n` : ''}`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Failed to run troubleshooting script: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * AI-powered deployment issue diagnosis
   */
  async diagnoseDeploymentIssue(args) {
    const {
      instance_name,
      aws_region = 'us-east-1',
      error_description,
      app_type = 'unknown',
      logs = '',
      auto_fix = false
    } = args;

    try {
      // Step 1: Get instance status
      let instanceStatus = null;
      try {
        const statusResult = await this.checkDeploymentStatus({
          instance_name,
          aws_region
        });
        instanceStatus = statusResult.content[0].text;
      } catch (e) {
        instanceStatus = `Could not get instance status: ${e.message}`;
      }

      // Step 2: Use AI to analyze the issue
      const analysisPrompt = `You are a deployment troubleshooting expert. Analyze this deployment issue and recommend specific troubleshooting scripts to run.

## Instance Information
- Instance Name: ${instance_name}
- Region: ${aws_region}
- App Type: ${app_type}

## Instance Status
${instanceStatus}

## Error Description
${error_description}

## Logs
${logs || 'No logs provided'}

## Available Troubleshooting Scripts
- docker: debug-docker.py, fix-docker.py
- general: comprehensive-endpoint-check.py, fix-all-deployment-issues.py, test-all-deployments.py, verify-all-endpoints.py
- lamp: debug-lamp.py, fix-lamp.py
- nginx: debug-nginx.py, fix-nginx.py
- nodejs: debug-nodejs.py, fix-nodejs.py, debug-react-nodejs.py, fix-react-nodejs.py, quick-check.py
- python: debug-python.py, fix-python.py
- react: debug-react.py, fix-react.py

Please provide:
1. Root cause analysis
2. Recommended troubleshooting scripts to run (in order)
3. Step-by-step fix instructions
4. Prevention tips

Format your response with clear sections.`;

      const aiResult = await this.bedrockAI.askExpert(analysisPrompt);

      let aiAnalysis = '';
      if (aiResult.success) {
        aiAnalysis = aiResult.content;
      } else {
        // Fallback to rule-based diagnosis
        aiAnalysis = this.ruleBasedDiagnosis(error_description, app_type, logs);
      }

      // Step 3: Extract recommended scripts from AI analysis
      const recommendedScripts = this.extractRecommendedScripts(aiAnalysis, app_type);

      // Step 4: Optionally run fix scripts
      let fixResults = '';
      if (auto_fix && recommendedScripts.length > 0) {
        fixResults = '\n## 🔧 Auto-Fix Results\n\n';
        
        for (const script of recommendedScripts.slice(0, 2)) { // Run max 2 scripts
          try {
            const result = await this.runTroubleshootingScript({
              script_name: script.name,
              category: script.category,
              instance_name,
              aws_region
            });
            fixResults += `### ${script.name}\n${result.content[0].text}\n\n`;
          } catch (e) {
            fixResults += `### ${script.name}\n❌ Failed to run: ${e.message}\n\n`;
          }
        }
      }

      return {
        content: [{
          type: 'text',
          text: `# 🔍 Deployment Issue Diagnosis

## Instance: ${instance_name} (${aws_region})
## App Type: ${app_type}

---

## 🤖 AI Analysis

${aiAnalysis}

---

## 📋 Recommended Scripts

${recommendedScripts.length > 0 ? 
  recommendedScripts.map((s, i) => `${i + 1}. **${s.category}/${s.name}** - ${s.reason}`).join('\n') :
  'No specific scripts recommended. Try running general diagnostics.'}

${auto_fix ? fixResults : `
---

## 🚀 Next Steps

To run the recommended scripts, use:
\`\`\`json
{
  "tool": "run_troubleshooting_script",
  "script_name": "${recommendedScripts[0]?.name || 'debug-nodejs.py'}",
  "category": "${recommendedScripts[0]?.category || 'nodejs'}",
  "instance_name": "${instance_name}",
  "aws_region": "${aws_region}"
}
\`\`\`

Or set \`auto_fix: true\` to automatically run fix scripts.`}

---
*Diagnosis powered by ${aiResult.success ? 'AWS Bedrock (Claude)' : 'rule-based analysis'}*`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Diagnosis failed: ${error.message}` }],
        isError: true
      };
    }
  }

  /**
   * Rule-based diagnosis fallback when AI is unavailable
   */
  ruleBasedDiagnosis(errorDescription, appType, logs) {
    const error = (errorDescription + ' ' + logs).toLowerCase();
    let diagnosis = '## Root Cause Analysis\n\n';
    let recommendations = [];

    // Common error patterns
    if (error.includes('502') || error.includes('bad gateway')) {
      diagnosis += '**Likely Cause**: Backend service not running or not responding.\n\n';
      recommendations.push({ category: appType === 'nodejs' ? 'nodejs' : 'general', name: `debug-${appType}.py`, reason: 'Check backend service status' });
      recommendations.push({ category: appType === 'nodejs' ? 'nodejs' : 'general', name: `fix-${appType}.py`, reason: 'Restart backend service' });
    } else if (error.includes('503') || error.includes('service unavailable')) {
      diagnosis += '**Likely Cause**: Service overloaded or under maintenance.\n\n';
      recommendations.push({ category: 'general', name: 'comprehensive-endpoint-check.py', reason: 'Check all endpoints' });
    } else if (error.includes('connection refused') || error.includes('econnrefused')) {
      diagnosis += '**Likely Cause**: Service not listening on expected port.\n\n';
      recommendations.push({ category: appType !== 'unknown' ? appType : 'nodejs', name: `debug-${appType !== 'unknown' ? appType : 'nodejs'}.py`, reason: 'Check port configuration' });
    } else if (error.includes('permission denied') || error.includes('eacces')) {
      diagnosis += '**Likely Cause**: File or directory permission issues.\n\n';
      recommendations.push({ category: appType !== 'unknown' ? appType : 'nodejs', name: `fix-${appType !== 'unknown' ? appType : 'nodejs'}.py`, reason: 'Fix permissions' });
    } else if (error.includes('nginx') || error.includes('welcome to nginx')) {
      diagnosis += '**Likely Cause**: Nginx not configured correctly or serving default page.\n\n';
      recommendations.push({ category: 'nginx', name: 'debug-nginx.py', reason: 'Check nginx configuration' });
      recommendations.push({ category: 'nginx', name: 'fix-nginx.py', reason: 'Fix nginx configuration' });
    } else if (error.includes('pm2') || error.includes('node')) {
      diagnosis += '**Likely Cause**: Node.js application or PM2 process manager issue.\n\n';
      recommendations.push({ category: 'nodejs', name: 'debug-nodejs.py', reason: 'Check Node.js and PM2 status' });
      recommendations.push({ category: 'nodejs', name: 'fix-nodejs.py', reason: 'Restart PM2 processes' });
    } else if (error.includes('docker') || error.includes('container')) {
      diagnosis += '**Likely Cause**: Docker container not running or misconfigured.\n\n';
      recommendations.push({ category: 'docker', name: 'debug-docker.py', reason: 'Check Docker containers' });
      recommendations.push({ category: 'docker', name: 'fix-docker.py', reason: 'Restart Docker containers' });
    } else if (error.includes('apache') || error.includes('httpd') || error.includes('php')) {
      diagnosis += '**Likely Cause**: Apache/PHP configuration issue.\n\n';
      recommendations.push({ category: 'lamp', name: 'debug-lamp.py', reason: 'Check Apache and PHP' });
      recommendations.push({ category: 'lamp', name: 'fix-lamp.py', reason: 'Fix Apache configuration' });
    } else {
      diagnosis += '**Likely Cause**: Unable to determine specific cause from error description.\n\n';
      recommendations.push({ category: 'general', name: 'comprehensive-endpoint-check.py', reason: 'Run comprehensive diagnostics' });
      recommendations.push({ category: 'general', name: 'fix-all-deployment-issues.py', reason: 'Attempt general fixes' });
    }

    diagnosis += '## Recommendations\n\n';
    diagnosis += recommendations.map((r, i) => `${i + 1}. Run \`${r.category}/${r.name}\` - ${r.reason}`).join('\n');

    return diagnosis;
  }

  /**
   * Extract recommended scripts from AI analysis
   */
  extractRecommendedScripts(aiAnalysis, appType) {
    const scripts = [];
    const analysis = aiAnalysis.toLowerCase();

    // Map of script patterns to detect
    const scriptPatterns = [
      { pattern: /debug-nodejs\.py/i, category: 'nodejs', name: 'debug-nodejs.py' },
      { pattern: /fix-nodejs\.py/i, category: 'nodejs', name: 'fix-nodejs.py' },
      { pattern: /debug-nginx\.py/i, category: 'nginx', name: 'debug-nginx.py' },
      { pattern: /fix-nginx\.py/i, category: 'nginx', name: 'fix-nginx.py' },
      { pattern: /debug-docker\.py/i, category: 'docker', name: 'debug-docker.py' },
      { pattern: /fix-docker\.py/i, category: 'docker', name: 'fix-docker.py' },
      { pattern: /debug-lamp\.py/i, category: 'lamp', name: 'debug-lamp.py' },
      { pattern: /fix-lamp\.py/i, category: 'lamp', name: 'fix-lamp.py' },
      { pattern: /debug-python\.py/i, category: 'python', name: 'debug-python.py' },
      { pattern: /fix-python\.py/i, category: 'python', name: 'fix-python.py' },
      { pattern: /debug-react\.py/i, category: 'react', name: 'debug-react.py' },
      { pattern: /fix-react\.py/i, category: 'react', name: 'fix-react.py' },
      { pattern: /comprehensive-endpoint-check\.py/i, category: 'general', name: 'comprehensive-endpoint-check.py' },
      { pattern: /fix-all-deployment-issues\.py/i, category: 'general', name: 'fix-all-deployment-issues.py' },
    ];

    for (const { pattern, category, name } of scriptPatterns) {
      if (pattern.test(aiAnalysis)) {
        scripts.push({ category, name, reason: 'Recommended by AI analysis' });
      }
    }

    // If no scripts found, add defaults based on app type
    if (scripts.length === 0) {
      const typeMap = {
        nodejs: [{ category: 'nodejs', name: 'debug-nodejs.py' }, { category: 'nodejs', name: 'fix-nodejs.py' }],
        python: [{ category: 'python', name: 'debug-python.py' }, { category: 'python', name: 'fix-python.py' }],
        php: [{ category: 'lamp', name: 'debug-lamp.py' }, { category: 'lamp', name: 'fix-lamp.py' }],
        lamp: [{ category: 'lamp', name: 'debug-lamp.py' }, { category: 'lamp', name: 'fix-lamp.py' }],
        docker: [{ category: 'docker', name: 'debug-docker.py' }, { category: 'docker', name: 'fix-docker.py' }],
        nginx: [{ category: 'nginx', name: 'debug-nginx.py' }, { category: 'nginx', name: 'fix-nginx.py' }],
        react: [{ category: 'react', name: 'debug-react.py' }, { category: 'react', name: 'fix-react.py' }],
      };

      const defaults = typeMap[appType] || [
        { category: 'general', name: 'comprehensive-endpoint-check.py' },
        { category: 'general', name: 'fix-all-deployment-issues.py' }
      ];

      scripts.push(...defaults.map(s => ({ ...s, reason: 'Default for app type' })));
    }

    return scripts;
  }

  /**
   * Get logs from a Lightsail instance
   */
  async getInstanceLogs(args) {
    const {
      instance_name,
      aws_region = 'us-east-1',
      log_type = 'application',
      lines = 100
    } = args;

    try {
      // First, get instance IP using get-instance-access-details API
      let instanceIp = null;
      
      try {
        const instanceCommand = `aws lightsail get-instance --instance-name "${instance_name}" --region ${aws_region} --output json`;
        const instanceResult = execSync(instanceCommand, { encoding: 'utf8', timeout: 30000 });
        const instanceData = JSON.parse(instanceResult).instance;
        instanceIp = instanceData.publicIpAddress;
      } catch (e) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ Instance Not Found

Instance \`${instance_name}\` was not found in region \`${aws_region}\`.

Use \`list_lightsail_instances\` to see available instances.`
          }],
          isError: true
        };
      }

      if (!instanceIp) {
        return {
          content: [{
            type: 'text',
            text: `# ❌ No Public IP

Instance \`${instance_name}\` does not have a public IP address.

Cannot retrieve logs without SSH access.`
          }],
          isError: true
        };
      }

      // Build log retrieval commands based on log type
      const logCommands = {
        application: `pm2 logs --lines ${lines} --nostream 2>/dev/null || journalctl -u app -n ${lines} 2>/dev/null || tail -n ${lines} /var/log/app.log 2>/dev/null || echo "No application logs found"`,
        system: `journalctl -n ${lines} --no-pager 2>/dev/null || tail -n ${lines} /var/log/syslog 2>/dev/null || tail -n ${lines} /var/log/messages 2>/dev/null`,
        nginx: `tail -n ${lines} /var/log/nginx/error.log 2>/dev/null; echo "---ACCESS LOGS---"; tail -n ${Math.floor(lines/2)} /var/log/nginx/access.log 2>/dev/null`,
        apache: `tail -n ${lines} /var/log/apache2/error.log 2>/dev/null || tail -n ${lines} /var/log/httpd/error_log 2>/dev/null`,
        pm2: `pm2 logs --lines ${lines} --nostream 2>/dev/null || echo "PM2 not running or no logs"`,
        docker: `docker-compose logs --tail=${lines} 2>/dev/null || docker logs $(docker ps -q | head -1) --tail ${lines} 2>/dev/null || echo "No Docker containers running"`,
        all: `echo "=== SYSTEM LOGS ===" && journalctl -n 50 --no-pager 2>/dev/null; echo "\\n=== APPLICATION LOGS ===" && pm2 logs --lines 50 --nostream 2>/dev/null; echo "\\n=== NGINX LOGS ===" && tail -n 30 /var/log/nginx/error.log 2>/dev/null`
      };

      const command = logCommands[log_type] || logCommands.application;

      // Use get-instance-access-details to get SSH credentials
      // Note: This is the recommended approach instead of using default keypair
      let logs = '';
      
      try {
        // Try to get temporary SSH access
        const accessCommand = `aws lightsail get-instance-access-details --instance-name "${instance_name}" --region ${aws_region} --output json`;
        const accessResult = execSync(accessCommand, { encoding: 'utf8', timeout: 30000 });
        const accessData = JSON.parse(accessResult).accessDetails;
        
        if (accessData && accessData.privateKey) {
          // Write temporary key
          const tempKeyPath = `/tmp/lightsail-temp-${Date.now()}.pem`;
          fs.writeFileSync(tempKeyPath, accessData.privateKey, { mode: 0o600 });
          
          try {
            const sshCommand = `ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i "${tempKeyPath}" ${accessData.username}@${instanceIp} "${command}"`;
            logs = execSync(sshCommand, { encoding: 'utf8', timeout: 60000 });
          } finally {
            // Clean up temp key
            fs.unlinkSync(tempKeyPath);
          }
        } else {
          logs = `Could not get SSH access. Instance may not support temporary access.\n\nTo get logs manually:\n1. SSH into the instance\n2. Run: ${command}`;
        }
      } catch (sshError) {
        logs = `SSH connection failed: ${sshError.message}\n\nTo get logs manually, SSH into ${instanceIp} and run:\n${command}`;
      }

      return {
        content: [{
          type: 'text',
          text: `# 📋 Instance Logs: ${instance_name}

## Log Type: ${log_type}
## Lines: ${lines}
## Instance IP: ${instanceIp}

---

\`\`\`
${logs.slice(0, 15000)}${logs.length > 15000 ? '\n... (logs truncated)' : ''}
\`\`\`

---

**Tips:**
- Use \`log_type: "all"\` to get logs from multiple sources
- Increase \`lines\` parameter for more history
- Use \`diagnose_deployment_issue\` to analyze these logs with AI`
        }]
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Failed to get instance logs: ${error.message}` }],
        isError: true
      };
    }
  }
}

// Import the analysis classes
import { ProjectAnalyzer } from './project-analyzer.js';
import { InfrastructureOptimizer } from './infrastructure-optimizer.js';
import { ConfigurationGenerator } from './configuration-generator.js';

// Import Stdio transport for Cline integration
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// Check if running in stdio mode (for Cline integration)
const STDIO_MODE = process.argv.includes('--stdio') || process.env.MCP_TRANSPORT === 'stdio';

if (STDIO_MODE) {
  // Stdio transport mode - for Cline and other MCP clients
  async function runStdioServer() {
    const server = await new EnhancedLightsailDeploymentServer().initialize();
    const transport = new StdioServerTransport();
    await server.server.connect(transport);
    
    // Log to stderr so it doesn't interfere with MCP protocol on stdout
    console.error('🚀 Enhanced Lightsail Deployment MCP Server v3.0 (Stdio Mode)');
    console.error('🤖 AI Provider: AWS Bedrock (Claude)');
  }
  
  runStdioServer().catch((error) => {
    console.error('Failed to start stdio server:', error);
    process.exit(1);
  });
} else {
  // HTTP/SSE transport mode - for web clients and testing
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
      version: '3.0.0',
      features: [
        'intelligent-analysis', 
        'cost-optimization', 
        'security-assessment',
        'ai-powered-bedrock'
      ],
      ai: {
        provider: 'AWS Bedrock',
        model: process.env.BEDROCK_MODEL_ID || 'anthropic.claude-3-sonnet-20240229-v1:0',
        region: process.env.AWS_REGION || 'us-east-1'
      },
      timestamp: new Date().toISOString() 
    });
  });

  // Direct HTTP endpoint for tool calls (for testing)
  app.post('/call-tool', authenticate, async (req, res) => {
    try {
      const { tool_name, arguments: args } = req.body;
      
      if (!tool_name) {
        return res.status(400).json({ error: 'tool_name is required' });
      }

      console.log(`📞 Direct tool call: ${tool_name}`);
      const server = new EnhancedLightsailDeploymentServer();
      await server.initialize();
      
      // Call the tool handler directly
      const result = await server.handleToolCall(tool_name, args || {});
      res.json(result);
    } catch (error) {
      console.error('Tool call error:', error);
      res.status(500).json({ 
        error: error.message,
        stack: error.stack 
      });
    }
  });

  // List available tools
  app.get('/tools', authenticate, async (req, res) => {
    try {
      const server = new EnhancedLightsailDeploymentServer();
      await server.initialize();
      const tools = await server.listTools();
      res.json(tools);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
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
    console.log(`🚀 Enhanced Lightsail Deployment MCP Server v3.0 running on http://${HOST}:${PORT}`);
    console.log(`🤖 AI Provider: AWS Bedrock (Claude)`);
    console.log(`📊 Features: Intelligent Analysis, Cost Optimization, Security Assessment, AI-Powered Tools`);
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
}