/**
 * AWS Bedrock AI Integration for Intelligent Deployment Analysis
 * 
 * Uses Claude via Amazon Bedrock for:
 * - Intelligent code analysis
 * - Deployment troubleshooting
 * - Configuration recommendations
 * - Natural language deployment assistance
 * 
 * Credential Options:
 * - AWS_PROFILE environment variable or profile option
 * - Direct credentials via accessKeyId, secretAccessKey, sessionToken
 * - Default AWS credential chain (env vars, ~/.aws/credentials, IAM role)
 */

import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import { fromIni } from '@aws-sdk/credential-providers';

// Default model - Claude 3 Sonnet via Bedrock
const DEFAULT_MODEL = 'anthropic.claude-3-sonnet-20240229-v1:0';
const HAIKU_MODEL = 'anthropic.claude-3-haiku-20240307-v1:0';

export class BedrockAI {
  constructor(options = {}) {
    this.region = options.region || process.env.AWS_REGION || 'us-east-1';
    this.modelId = options.modelId || DEFAULT_MODEL;
    this.maxTokens = options.maxTokens || 4096;
    
    // Build client configuration
    const clientConfig = { region: this.region };
    
    // Option 1: Direct credentials provided
    if (options.accessKeyId && options.secretAccessKey) {
      clientConfig.credentials = {
        accessKeyId: options.accessKeyId,
        secretAccessKey: options.secretAccessKey,
        ...(options.sessionToken && { sessionToken: options.sessionToken })
      };
    }
    // Option 2: AWS profile name provided
    else if (options.profile || process.env.AWS_PROFILE) {
      const profileName = options.profile || process.env.AWS_PROFILE;
      clientConfig.credentials = fromIni({ profile: profileName });
    }
    // Option 3: Fall back to default credential chain (env vars, IAM role, etc.)
    
    this.client = new BedrockRuntimeClient(clientConfig);
    
    // Store credential info for status reporting
    this.credentialSource = options.accessKeyId ? 'direct' : 
                            (options.profile || process.env.AWS_PROFILE) ? `profile:${options.profile || process.env.AWS_PROFILE}` : 
                            'default-chain';

    // System prompt for deployment expertise
    this.systemPrompt = `You are an expert AWS Lightsail deployment assistant. You help developers:
- Analyze codebases and recommend optimal deployment configurations
- Troubleshoot deployment issues and errors
- Optimize infrastructure costs and performance
- Configure databases, storage, and security settings
- Generate deployment scripts and configurations

You have deep knowledge of:
- Node.js, Python, PHP, React, Docker applications
- MySQL, PostgreSQL, MongoDB databases
- Apache, Nginx, PM2 process managers
- AWS Lightsail instances, buckets, and databases
- GitHub Actions CI/CD workflows
- SSL/TLS, firewalls, and security best practices

Always provide practical, actionable advice. When analyzing code, focus on deployment requirements.
Format responses in markdown for readability.`;
  }

  /**
   * Send a message to Bedrock and get AI response
   */
  async chat(userMessage, context = '') {
    const fullSystemPrompt = context 
      ? `${this.systemPrompt}\n\nAdditional Context:\n${context}`
      : this.systemPrompt;

    const body = {
      anthropic_version: "bedrock-2023-05-31",
      max_tokens: this.maxTokens,
      system: fullSystemPrompt,
      messages: [
        { role: "user", content: userMessage }
      ]
    };

    try {
      const command = new InvokeModelCommand({
        modelId: this.modelId,
        body: JSON.stringify(body),
        contentType: 'application/json',
        accept: 'application/json'
      });

      const response = await this.client.send(command);
      const responseBody = JSON.parse(new TextDecoder().decode(response.body));
      
      return {
        success: true,
        content: responseBody.content[0].text,
        usage: {
          inputTokens: responseBody.usage?.input_tokens,
          outputTokens: responseBody.usage?.output_tokens
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        code: error.name
      };
    }
  }

  /**
   * Analyze project files intelligently using AI
   */
  async analyzeProject(projectFiles, userDescription = '') {
    const filesContext = projectFiles.map(f => 
      `### ${f.path}\n\`\`\`\n${f.content?.substring(0, 2000) || 'No content'}\n\`\`\``
    ).join('\n\n');

    const prompt = `Analyze this project and provide deployment recommendations:

${userDescription ? `User Description: ${userDescription}\n\n` : ''}
## Project Files:
${filesContext}

Please analyze and provide:
1. **Application Type**: What kind of app is this? (nodejs, python, php, react, docker, etc.)
2. **Frameworks Detected**: What frameworks/libraries are used?
3. **Database Requirements**: What database does it need? (mysql, postgresql, mongodb, none)
4. **Storage Needs**: Does it need file storage/S3 bucket?
5. **Recommended Instance Size**: What Lightsail bundle would you recommend?
6. **Security Considerations**: Any security requirements detected?
7. **Deployment Complexity**: Simple, moderate, or complex?
8. **Estimated Monthly Cost**: Rough estimate in USD

Respond in JSON format:
\`\`\`json
{
  "detected_type": "string",
  "confidence": 0.0-1.0,
  "frameworks": [{"name": "string", "type": "string", "confidence": 0.0-1.0}],
  "databases": [{"type": "string", "name": "string", "confidence": 0.0-1.0}],
  "storage_needs": {"file_uploads": boolean, "needs_bucket": boolean},
  "infrastructure_needs": {"bundle_size": "string", "memory_intensive": boolean, "cpu_intensive": boolean},
  "security_considerations": {"needs_ssl": boolean, "needs_auth": boolean, "handles_user_data": boolean},
  "deployment_complexity": "simple|moderate|complex",
  "estimated_costs": {"monthly_min": number, "monthly_max": number},
  "recommendations": ["string"],
  "warnings": ["string"]
}
\`\`\``;

    const response = await this.chat(prompt);
    
    if (!response.success) {
      return { success: false, error: response.error };
    }

    // Extract JSON from response
    try {
      const jsonMatch = response.content.match(/```json\n([\s\S]*?)\n```/);
      if (jsonMatch) {
        const analysis = JSON.parse(jsonMatch[1]);
        return { success: true, analysis, rawResponse: response.content };
      }
      return { success: true, analysis: null, rawResponse: response.content };
    } catch (e) {
      return { success: true, analysis: null, rawResponse: response.content };
    }
  }

  /**
   * Troubleshoot deployment issues
   */
  async troubleshoot(errorMessage, context = {}) {
    const contextStr = Object.entries(context)
      .map(([k, v]) => `- ${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`)
      .join('\n');

    const prompt = `I'm having a deployment issue. Please help troubleshoot:

## Error Message:
\`\`\`
${errorMessage}
\`\`\`

## Context:
${contextStr || 'No additional context provided'}

Please provide:
1. **Root Cause**: What's likely causing this error?
2. **Solution Steps**: Step-by-step fix instructions
3. **Prevention**: How to prevent this in the future
4. **Commands**: Any specific commands to run`;

    return await this.chat(prompt);
  }

  /**
   * Generate optimized deployment configuration
   */
  async generateConfig(analysis, preferences = {}) {
    const prompt = `Generate an optimized deployment configuration based on this analysis:

## Project Analysis:
\`\`\`json
${JSON.stringify(analysis, null, 2)}
\`\`\`

## User Preferences:
- Budget: ${preferences.budget || 'standard'}
- Scale: ${preferences.scale || 'small'}
- Environment: ${preferences.environment || 'production'}
- Region: ${preferences.aws_region || 'us-east-1'}

Generate a complete deployment-*.config.yml file that's optimized for this application.
Include all necessary sections: aws, lightsail, application, dependencies, deployment, monitoring, security.`;

    return await this.chat(prompt);
  }

  /**
   * Ask deployment expert - general Q&A
   */
  async askExpert(question, projectContext = null) {
    let context = '';
    if (projectContext) {
      context = `Current Project Context:\n${JSON.stringify(projectContext, null, 2)}`;
    }
    return await this.chat(question, context);
  }

  /**
   * Explain code for deployment purposes
   */
  async explainCode(code, filename = '') {
    const prompt = `Analyze this code from a deployment perspective:

${filename ? `File: ${filename}\n` : ''}
\`\`\`
${code}
\`\`\`

Explain:
1. What this code does
2. What dependencies it requires
3. What environment variables it needs
4. What ports it uses
5. Any deployment considerations`;

    return await this.chat(prompt);
  }

  /**
   * Review and improve deployment config
   */
  async reviewConfig(config) {
    const prompt = `Review this deployment configuration and suggest improvements:

\`\`\`yaml
${typeof config === 'string' ? config : JSON.stringify(config, null, 2)}
\`\`\`

Check for:
1. Security issues (default passwords, open ports)
2. Performance optimizations
3. Cost savings opportunities
4. Missing configurations
5. Best practices violations

Provide specific recommendations with code examples.`;

    return await this.chat(prompt);
  }

  /**
   * Use faster/cheaper Haiku model for simple tasks
   */
  async quickAnalysis(prompt) {
    const originalModel = this.modelId;
    this.modelId = HAIKU_MODEL;
    const result = await this.chat(prompt);
    this.modelId = originalModel;
    return result;
  }
}

// Export singleton instance
export const bedrockAI = new BedrockAI();

// Export class for custom instances
export default BedrockAI;
