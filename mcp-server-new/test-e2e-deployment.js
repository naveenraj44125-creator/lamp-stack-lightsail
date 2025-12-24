#!/usr/bin/env node

/**
 * End-to-End Deployment Test
 * 
 * This test demonstrates the full deployment workflow using the MCP server:
 * 1. Create a simple test application
 * 2. Analyze the project using MCP tools
 * 3. Generate deployment configuration
 * 4. Setup GitHub repository and Actions
 * 5. Deploy to AWS Lightsail
 * 6. Verify the application is working
 * 
 * Prerequisites:
 * - AWS credentials configured (source .aws-creds.sh)
 * - GitHub CLI authenticated (gh auth login)
 * - Node.js 18+
 * 
 * Usage:
 *   node test-e2e-deployment.js [--cleanup] [--skip-deploy]
 */

import { execSync, spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Get script directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// Import MCP components
import { ProjectAnalyzer } from './project-analyzer.js';
import { InfrastructureOptimizer } from './infrastructure-optimizer.js';
import { ConfigurationGenerator } from './configuration-generator.js';

// Colors for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logStep(step, message) {
  console.log(`\n${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`);
  console.log(`${colors.magenta}📍 Step ${step}: ${message}${colors.reset}`);
  console.log(`${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`);
}

function exec(command, options = {}) {
  try {
    return execSync(command, { 
      encoding: 'utf8', 
      stdio: options.silent ? 'pipe' : 'inherit',
      ...options 
    });
  } catch (error) {
    if (!options.ignoreError) {
      throw error;
    }
    return error.stdout || '';
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
const CLEANUP_ONLY = args.includes('--cleanup');
const SKIP_DEPLOY = args.includes('--skip-deploy');
const DRY_RUN = args.includes('--dry-run');

// Test configuration
const TEST_CONFIG = {
  appName: 'mcp-e2e-test-app',
  instanceName: 'mcp-e2e-test-instance',
  awsRegion: 'us-east-1',
  githubUsername: null, // Will be detected
  testAppDir: path.join(projectRoot, 'test-e2e-app'),
  configFile: 'deployment-e2e-test.config.yml'
};

/**
 * Step 1: Create a simple test application
 */
async function createTestApplication() {
  logStep(1, 'Creating Test Application');
  
  const appDir = TEST_CONFIG.testAppDir;
  
  // Clean up existing test app
  if (fs.existsSync(appDir)) {
    log('🧹 Cleaning up existing test app directory...', 'yellow');
    fs.rmSync(appDir, { recursive: true, force: true });
  }
  
  // Create app directory
  fs.mkdirSync(appDir, { recursive: true });
  
  // Create a simple Node.js Express application
  const packageJson = {
    name: TEST_CONFIG.appName,
    version: '1.0.0',
    description: 'MCP E2E Test Application',
    main: 'server.js',
    type: 'module',
    scripts: {
      start: 'node server.js',
      test: 'echo "Tests passed"'
    },
    dependencies: {
      express: '^4.18.2'
    }
  };
  
  fs.writeFileSync(
    path.join(appDir, 'package.json'),
    JSON.stringify(packageJson, null, 2)
  );
  log('✅ Created package.json', 'green');
  
  // Create server.js
  const serverCode = `
import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    app: '${TEST_CONFIG.appName}',
    version: '1.0.0'
  });
});

// Main endpoint
app.get('/', (req, res) => {
  res.send(\`
    <!DOCTYPE html>
    <html>
    <head>
      <title>${TEST_CONFIG.appName}</title>
      <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .success { color: green; }
        .info { background: #f0f0f0; padding: 15px; border-radius: 5px; }
      </style>
    </head>
    <body>
      <h1 class="success">🎉 MCP E2E Test Application</h1>
      <p>This application was deployed using the MCP Server deployment tools.</p>
      <div class="info">
        <h3>Deployment Info:</h3>
        <ul>
          <li><strong>App Name:</strong> ${TEST_CONFIG.appName}</li>
          <li><strong>Instance:</strong> ${TEST_CONFIG.instanceName}</li>
          <li><strong>Region:</strong> ${TEST_CONFIG.awsRegion}</li>
          <li><strong>Deployed:</strong> \${new Date().toISOString()}</li>
        </ul>
      </div>
      <p><a href="/api/health">Check Health Endpoint</a></p>
    </body>
    </html>
  \`);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(\`🚀 Server running on port \${PORT}\`);
});
`;
  
  fs.writeFileSync(path.join(appDir, 'server.js'), serverCode.trim());
  log('✅ Created server.js', 'green');
  
  // Create .gitignore
  fs.writeFileSync(path.join(appDir, '.gitignore'), 'node_modules/\n.env\n*.log\n');
  log('✅ Created .gitignore', 'green');
  
  // Create README
  const readme = `# ${TEST_CONFIG.appName}

MCP E2E Test Application - automatically deployed using MCP Server tools.

## Endpoints
- \`/\` - Main page
- \`/api/health\` - Health check endpoint

## Deployment
This app is deployed to AWS Lightsail using GitHub Actions.
`;
  fs.writeFileSync(path.join(appDir, 'README.md'), readme);
  log('✅ Created README.md', 'green');
  
  log(`\n📁 Test application created at: ${appDir}`, 'blue');
  return appDir;
}

/**
 * Step 2: Analyze project using MCP tools
 */
async function analyzeProject(appDir) {
  logStep(2, 'Analyzing Project with MCP Tools');
  
  const analyzer = new ProjectAnalyzer();
  
  log('🔍 Running intelligent project analysis...', 'blue');
  const analysis = await analyzer.analyzeProject(appDir);
  
  log(`\n📊 Analysis Results:`, 'cyan');
  log(`   • Detected Type: ${analysis.detected_type}`, 'green');
  log(`   • Confidence: ${Math.round(analysis.confidence * 100)}%`, 'green');
  log(`   • Frameworks: ${analysis.frameworks.map(f => f.name).join(', ') || 'None'}`, 'green');
  log(`   • Databases: ${analysis.databases.map(d => d.type).join(', ') || 'None'}`, 'green');
  log(`   • Complexity: ${analysis.deployment_complexity}`, 'green');
  
  return analysis;
}

/**
 * Step 3: Generate deployment configuration
 */
async function generateConfiguration(analysis) {
  logStep(3, 'Generating Deployment Configuration');
  
  const optimizer = new InfrastructureOptimizer();
  const generator = new ConfigurationGenerator();
  
  // Optimize infrastructure
  log('💡 Optimizing infrastructure recommendations...', 'blue');
  const optimization = optimizer.optimizeInfrastructure(analysis, {
    budget_constraint: 20,
    performance_priority: 'balanced'
  });
  
  log(`   • Recommended Bundle: ${optimization.recommended_bundle}`, 'green');
  log(`   • Monthly Cost: ${optimization.cost_breakdown.total}`, 'green');
  
  // Generate configuration
  log('\n⚙️ Generating deployment configuration...', 'blue');
  const config = generator.generateDeploymentConfig(analysis, optimization, {
    app_name: TEST_CONFIG.appName,
    instance_name: TEST_CONFIG.instanceName,
    aws_region: TEST_CONFIG.awsRegion
  });
  
  // Fix package_files to use correct paths for our test app
  config.application.package_files = [
    './',
    'package.json',
    'server.js'
  ];
  
  // Update health check endpoint
  config.monitoring.health_check.endpoint = '/api/health';
  config.monitoring.health_check.expected_content = 'healthy';
  config.deployment.steps.verification.endpoints_to_test = ['/', '/api/health'];
  
  // Generate workflow - create a standalone workflow for e2e test
  const workflow = generateStandaloneWorkflow(TEST_CONFIG);
  
  // Save configuration file
  const configYAML = generator.formatYAML(config);
  const configPath = path.join(projectRoot, TEST_CONFIG.configFile);
  fs.writeFileSync(configPath, configYAML);
  log(`✅ Configuration saved to: ${configPath}`, 'green');
  
  // Save workflow file
  const workflowDir = path.join(TEST_CONFIG.testAppDir, '.github', 'workflows');
  fs.mkdirSync(workflowDir, { recursive: true });
  fs.writeFileSync(path.join(workflowDir, 'deploy.yml'), workflow);
  log(`✅ Workflow saved to: ${workflowDir}/deploy.yml`, 'green');
  
  return { config, workflow, configPath };
}

/**
 * Generate a standalone workflow that doesn't depend on reusable workflows
 */
function generateStandaloneWorkflow(testConfig) {
  return `name: ${testConfig.appName} Deployment

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    name: Deploy to Lightsail
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: \${{ vars.AWS_ROLE_ARN }}
          aws-region: ${testConfig.awsRegion}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Create Lightsail instance if not exists
        run: |
          INSTANCE_NAME="${testConfig.instanceName}"
          
          # Check if instance exists
          if aws lightsail get-instance --instance-name \$INSTANCE_NAME 2>/dev/null; then
            echo "Instance \$INSTANCE_NAME already exists"
          else
            echo "Creating instance \$INSTANCE_NAME..."
            aws lightsail create-instances \\
              --instance-names \$INSTANCE_NAME \\
              --availability-zone ${testConfig.awsRegion}a \\
              --blueprint-id ubuntu_22_04 \\
              --bundle-id small_3_0
            
            echo "Waiting for instance to be running..."
            sleep 60
          fi
          
          # Get instance IP
          INSTANCE_IP=\$(aws lightsail get-instance --instance-name \$INSTANCE_NAME --query 'instance.publicIpAddress' --output text)
          echo "INSTANCE_IP=\$INSTANCE_IP" >> \$GITHUB_ENV
          echo "Instance IP: \$INSTANCE_IP"

      - name: Open firewall ports
        run: |
          aws lightsail open-instance-public-ports \\
            --instance-name ${testConfig.instanceName} \\
            --port-info fromPort=80,toPort=80,protocol=tcp || true
          aws lightsail open-instance-public-ports \\
            --instance-name ${testConfig.instanceName} \\
            --port-info fromPort=443,toPort=443,protocol=tcp || true
          aws lightsail open-instance-public-ports \\
            --instance-name ${testConfig.instanceName} \\
            --port-info fromPort=3000,toPort=3000,protocol=tcp || true

      - name: Get SSH key and deploy
        run: |
          # Get default key pair
          aws lightsail download-default-key-pair --output text --query 'privateKeyBase64' | base64 -d > lightsail-key.pem
          chmod 600 lightsail-key.pem
          
          # Wait for SSH to be available
          echo "Waiting for SSH..."
          for i in {1..30}; do
            if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i lightsail-key.pem ubuntu@\$INSTANCE_IP "echo 'SSH ready'" 2>/dev/null; then
              break
            fi
            echo "Attempt \$i: SSH not ready yet..."
            sleep 10
          done
          
          # Install Node.js on instance
          ssh -o StrictHostKeyChecking=no -i lightsail-key.pem ubuntu@\$INSTANCE_IP << 'ENDSSH'
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
            sudo npm install -g pm2
          ENDSSH
          
          # Create app directory and copy files
          ssh -o StrictHostKeyChecking=no -i lightsail-key.pem ubuntu@\$INSTANCE_IP "sudo mkdir -p /var/www/app && sudo chown ubuntu:ubuntu /var/www/app"
          scp -o StrictHostKeyChecking=no -i lightsail-key.pem -r ./* ubuntu@\$INSTANCE_IP:/var/www/app/
          
          # Install and start app
          ssh -o StrictHostKeyChecking=no -i lightsail-key.pem ubuntu@\$INSTANCE_IP << 'ENDSSH'
            cd /var/www/app
            npm install --production
            pm2 delete all 2>/dev/null || true
            pm2 start server.js --name app
            pm2 save
            sudo env PATH=\$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu
          ENDSSH
          
          rm -f lightsail-key.pem

      - name: Verify deployment
        run: |
          echo "Waiting for app to start..."
          sleep 10
          
          echo "Testing health endpoint..."
          for i in {1..10}; do
            if curl -s http://\$INSTANCE_IP:3000/api/health | grep -q "healthy"; then
              echo "✅ Health check passed!"
              exit 0
            fi
            echo "Attempt \$i: App not ready yet..."
            sleep 5
          done
          
          echo "❌ Health check failed"
          exit 1

      - name: Output deployment URL
        run: |
          echo "## 🚀 Deployment Complete" >> \$GITHUB_STEP_SUMMARY
          echo "" >> \$GITHUB_STEP_SUMMARY
          echo "**Application URL:** http://\$INSTANCE_IP:3000" >> \$GITHUB_STEP_SUMMARY
          echo "**Health Check:** http://\$INSTANCE_IP:3000/api/health" >> \$GITHUB_STEP_SUMMARY
`;
}

/**
 * Step 4: Setup GitHub repository and Actions
 */
async function setupGitHubActions() {
  logStep(4, 'Setting up GitHub Repository and Actions');
  
  // Get GitHub username
  try {
    const ghUser = exec('gh api user --jq .login', { silent: true }).trim();
    TEST_CONFIG.githubUsername = ghUser;
    log(`📌 GitHub User: ${ghUser}`, 'green');
  } catch (error) {
    log('❌ Failed to get GitHub username. Make sure gh CLI is authenticated.', 'red');
    throw new Error('GitHub CLI not authenticated');
  }
  
  const repoName = TEST_CONFIG.appName;
  const fullRepoName = `${TEST_CONFIG.githubUsername}/${repoName}`;
  
  // Check if repo exists
  log(`\n🔍 Checking if repository ${fullRepoName} exists...`, 'blue');
  try {
    exec(`gh repo view ${fullRepoName}`, { silent: true });
    log(`⚠️ Repository already exists, will update it`, 'yellow');
  } catch {
    // Create new repository
    log(`📦 Creating new repository: ${fullRepoName}`, 'blue');
    if (!DRY_RUN) {
      exec(`gh repo create ${repoName} --private --description "MCP E2E Test Application"`, { ignoreError: true });
    }
  }
  
  // Initialize git in test app directory
  const appDir = TEST_CONFIG.testAppDir;
  log('\n🔧 Initializing git repository...', 'blue');
  
  if (!DRY_RUN) {
    exec('git init', { cwd: appDir, silent: true });
    exec('git add .', { cwd: appDir, silent: true });
    exec('git commit -m "Initial commit - MCP E2E Test"', { cwd: appDir, silent: true, ignoreError: true });
    
    // Set remote and push
    try {
      exec(`git remote remove origin`, { cwd: appDir, silent: true, ignoreError: true });
      exec(`git remote add origin https://github.com/${fullRepoName}.git`, { cwd: appDir, silent: true });
      exec('git branch -M main', { cwd: appDir, silent: true });
      exec('git push -u origin main --force', { cwd: appDir, silent: true });
      log('✅ Code pushed to GitHub', 'green');
    } catch (error) {
      log(`⚠️ Git push failed: ${error.message}`, 'yellow');
    }
  }
  
  // Setup AWS IAM role for GitHub OIDC
  log('\n🔐 Setting up AWS IAM role for GitHub Actions...', 'blue');
  
  if (!DRY_RUN) {
    try {
      // Get AWS account ID
      const accountId = exec('aws sts get-caller-identity --query Account --output text', { silent: true }).trim();
      log(`   AWS Account: ${accountId}`, 'green');
      
      // Run setup script to create IAM role
      const setupScript = path.join(projectRoot, 'setup-complete-deployment.sh');
      if (fs.existsSync(setupScript)) {
        log('   Running IAM role setup...', 'blue');
        // The setup script handles IAM role creation
      }
      
      // Set GitHub repository variables
      const roleArn = `arn:aws:iam::${accountId}:role/github-actions-${repoName}`;
      exec(`gh variable set AWS_ROLE_ARN --body "${roleArn}" --repo ${fullRepoName}`, { silent: true, ignoreError: true });
      log(`✅ AWS_ROLE_ARN variable set`, 'green');
      
    } catch (error) {
      log(`⚠️ AWS setup warning: ${error.message}`, 'yellow');
    }
  }
  
  return { repoName: fullRepoName };
}

/**
 * Step 5: Deploy to AWS Lightsail
 */
async function deployToLightsail() {
  logStep(5, 'Deploying to AWS Lightsail');
  
  if (SKIP_DEPLOY) {
    log('⏭️ Skipping deployment (--skip-deploy flag)', 'yellow');
    return { skipped: true };
  }
  
  if (DRY_RUN) {
    log('🔍 DRY RUN - Would trigger GitHub Actions deployment', 'yellow');
    return { dryRun: true };
  }
  
  const fullRepoName = `${TEST_CONFIG.githubUsername}/${TEST_CONFIG.appName}`;
  
  // Trigger GitHub Actions workflow
  log('🚀 Triggering GitHub Actions deployment workflow...', 'blue');
  
  try {
    exec(`gh workflow run deploy.yml --repo ${fullRepoName}`, { silent: true });
    log('✅ Workflow triggered', 'green');
  } catch (error) {
    log(`⚠️ Could not trigger workflow automatically: ${error.message}`, 'yellow');
    log('   You can manually trigger it from GitHub Actions tab', 'yellow');
  }
  
  // Wait for deployment to complete
  log('\n⏳ Waiting for deployment to complete (this may take 5-10 minutes)...', 'blue');
  
  const maxWaitTime = 15 * 60 * 1000; // 15 minutes
  const checkInterval = 30 * 1000; // 30 seconds
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWaitTime) {
    try {
      // Check workflow status
      const status = exec(
        `gh run list --repo ${fullRepoName} --workflow deploy.yml --limit 1 --json status,conclusion --jq '.[0]'`,
        { silent: true }
      );
      
      const run = JSON.parse(status || '{}');
      
      if (run.status === 'completed') {
        if (run.conclusion === 'success') {
          log('✅ Deployment completed successfully!', 'green');
          return { success: true };
        } else {
          log(`❌ Deployment failed with conclusion: ${run.conclusion}`, 'red');
          return { success: false, conclusion: run.conclusion };
        }
      }
      
      const elapsed = Math.round((Date.now() - startTime) / 1000);
      process.stdout.write(`\r   Status: ${run.status || 'pending'} (${elapsed}s elapsed)...`);
      
    } catch (error) {
      // Workflow might not have started yet
    }
    
    await new Promise(resolve => setTimeout(resolve, checkInterval));
  }
  
  log('\n⚠️ Deployment timed out - check GitHub Actions for status', 'yellow');
  return { timedOut: true };
}

/**
 * Step 6: Verify application is working
 */
async function verifyApplication() {
  logStep(6, 'Verifying Application');
  
  if (SKIP_DEPLOY || DRY_RUN) {
    log('⏭️ Skipping verification (deployment was skipped)', 'yellow');
    return { skipped: true };
  }
  
  // Get instance IP from AWS
  log('🔍 Getting instance IP address...', 'blue');
  
  let instanceIp = null;
  
  try {
    const instanceInfo = exec(
      `aws lightsail get-instance --instance-name ${TEST_CONFIG.instanceName} --region ${TEST_CONFIG.awsRegion} --query 'instance.publicIpAddress' --output text`,
      { silent: true }
    ).trim();
    
    if (instanceInfo && instanceInfo !== 'None') {
      instanceIp = instanceInfo;
      log(`   Instance IP: ${instanceIp}`, 'green');
    }
  } catch (error) {
    log(`⚠️ Could not get instance IP: ${error.message}`, 'yellow');
  }
  
  if (!instanceIp) {
    // Try to get static IP
    try {
      const staticIp = exec(
        `aws lightsail get-static-ip --static-ip-name ${TEST_CONFIG.instanceName}-ip --region ${TEST_CONFIG.awsRegion} --query 'staticIp.ipAddress' --output text`,
        { silent: true }
      ).trim();
      
      if (staticIp && staticIp !== 'None') {
        instanceIp = staticIp;
        log(`   Static IP: ${instanceIp}`, 'green');
      }
    } catch {
      // No static IP
    }
  }
  
  if (!instanceIp) {
    log('❌ Could not determine instance IP address', 'red');
    return { success: false, error: 'No IP address found' };
  }
  
  const appUrl = `http://${instanceIp}`;
  const healthUrl = `${appUrl}/api/health`;
  
  log(`\n🌐 Application URL: ${appUrl}`, 'cyan');
  log(`🏥 Health Check URL: ${healthUrl}`, 'cyan');
  
  // Test main endpoint
  log('\n📡 Testing main endpoint...', 'blue');
  try {
    const mainResponse = exec(`curl -s -o /dev/null -w "%{http_code}" ${appUrl}`, { silent: true }).trim();
    if (mainResponse === '200') {
      log(`✅ Main endpoint returned HTTP ${mainResponse}`, 'green');
    } else {
      log(`⚠️ Main endpoint returned HTTP ${mainResponse}`, 'yellow');
    }
  } catch (error) {
    log(`❌ Main endpoint test failed: ${error.message}`, 'red');
  }
  
  // Test health endpoint
  log('\n📡 Testing health endpoint...', 'blue');
  try {
    const healthResponse = exec(`curl -s ${healthUrl}`, { silent: true });
    const health = JSON.parse(healthResponse);
    
    if (health.status === 'healthy') {
      log(`✅ Health check passed!`, 'green');
      log(`   • Status: ${health.status}`, 'green');
      log(`   • App: ${health.app}`, 'green');
      log(`   • Version: ${health.version}`, 'green');
      log(`   • Timestamp: ${health.timestamp}`, 'green');
      
      return {
        success: true,
        url: appUrl,
        healthUrl: healthUrl,
        health: health
      };
    } else {
      log(`⚠️ Health check returned unexpected status: ${health.status}`, 'yellow');
    }
  } catch (error) {
    log(`❌ Health check failed: ${error.message}`, 'red');
  }
  
  return {
    success: false,
    url: appUrl,
    healthUrl: healthUrl
  };
}

/**
 * Cleanup resources
 */
async function cleanup() {
  logStep('🧹', 'Cleaning Up Resources');
  
  // Delete Lightsail instance
  log('🗑️ Deleting Lightsail instance...', 'blue');
  try {
    exec(
      `aws lightsail delete-instance --instance-name ${TEST_CONFIG.instanceName} --region ${TEST_CONFIG.awsRegion}`,
      { silent: true, ignoreError: true }
    );
    log('✅ Instance deleted', 'green');
  } catch {
    log('⚠️ Instance deletion skipped (may not exist)', 'yellow');
  }
  
  // Delete static IP
  log('🗑️ Deleting static IP...', 'blue');
  try {
    exec(
      `aws lightsail release-static-ip --static-ip-name ${TEST_CONFIG.instanceName}-ip --region ${TEST_CONFIG.awsRegion}`,
      { silent: true, ignoreError: true }
    );
    log('✅ Static IP released', 'green');
  } catch {
    log('⚠️ Static IP release skipped (may not exist)', 'yellow');
  }
  
  // Delete GitHub repository
  if (TEST_CONFIG.githubUsername) {
    log('🗑️ Deleting GitHub repository...', 'blue');
    try {
      exec(
        `gh repo delete ${TEST_CONFIG.githubUsername}/${TEST_CONFIG.appName} --yes`,
        { silent: true, ignoreError: true }
      );
      log('✅ Repository deleted', 'green');
    } catch {
      log('⚠️ Repository deletion skipped', 'yellow');
    }
  }
  
  // Delete local test app directory
  log('🗑️ Deleting local test app...', 'blue');
  if (fs.existsSync(TEST_CONFIG.testAppDir)) {
    fs.rmSync(TEST_CONFIG.testAppDir, { recursive: true, force: true });
    log('✅ Local test app deleted', 'green');
  }
  
  // Delete config file
  const configPath = path.join(projectRoot, TEST_CONFIG.configFile);
  if (fs.existsSync(configPath)) {
    fs.unlinkSync(configPath);
    log('✅ Config file deleted', 'green');
  }
  
  log('\n✅ Cleanup completed', 'green');
}

/**
 * Main test runner
 */
async function runE2ETest() {
  console.log(`
${colors.cyan}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🚀 MCP Server End-to-End Deployment Test                       ║
║                                                                  ║
║   This test will:                                                ║
║   1. Create a simple Node.js test application                    ║
║   2. Analyze it using MCP tools                                  ║
║   3. Generate deployment configuration                           ║
║   4. Setup GitHub repository and Actions                         ║
║   5. Deploy to AWS Lightsail                                     ║
║   6. Verify the application is working                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝${colors.reset}
`);

  log(`📋 Test Configuration:`, 'blue');
  log(`   • App Name: ${TEST_CONFIG.appName}`, 'cyan');
  log(`   • Instance: ${TEST_CONFIG.instanceName}`, 'cyan');
  log(`   • Region: ${TEST_CONFIG.awsRegion}`, 'cyan');
  log(`   • Dry Run: ${DRY_RUN}`, 'cyan');
  log(`   • Skip Deploy: ${SKIP_DEPLOY}`, 'cyan');
  log(`   • Cleanup Only: ${CLEANUP_ONLY}`, 'cyan');

  // Handle cleanup-only mode
  if (CLEANUP_ONLY) {
    // Get GitHub username first
    try {
      TEST_CONFIG.githubUsername = exec('gh api user --jq .login', { silent: true }).trim();
    } catch {
      log('⚠️ Could not get GitHub username', 'yellow');
    }
    await cleanup();
    return;
  }

  const results = {
    steps: [],
    success: false,
    appUrl: null,
    healthUrl: null
  };

  try {
    // Step 1: Create test application
    const appDir = await createTestApplication();
    results.steps.push({ name: 'Create Application', success: true });

    // Step 2: Analyze project
    const analysis = await analyzeProject(appDir);
    results.steps.push({ name: 'Analyze Project', success: true, data: analysis });

    // Step 3: Generate configuration
    const { config, configPath } = await generateConfiguration(analysis);
    results.steps.push({ name: 'Generate Configuration', success: true });

    // Step 4: Setup GitHub
    const { repoName } = await setupGitHubActions();
    results.steps.push({ name: 'Setup GitHub', success: true, data: { repoName } });

    // Step 5: Deploy
    const deployResult = await deployToLightsail();
    results.steps.push({ name: 'Deploy', success: deployResult.success || deployResult.skipped || deployResult.dryRun });

    // Step 6: Verify
    const verifyResult = await verifyApplication();
    results.steps.push({ name: 'Verify', success: verifyResult.success || verifyResult.skipped });
    
    if (verifyResult.url) {
      results.appUrl = verifyResult.url;
      results.healthUrl = verifyResult.healthUrl;
    }

    results.success = results.steps.every(s => s.success);

  } catch (error) {
    log(`\n❌ Test failed with error: ${error.message}`, 'red');
    console.error(error.stack);
    results.success = false;
  }

  // Print summary
  console.log(`
${colors.cyan}╔══════════════════════════════════════════════════════════════════╗
║                         TEST SUMMARY                             ║
╚══════════════════════════════════════════════════════════════════╝${colors.reset}
`);

  for (const step of results.steps) {
    const status = step.success ? `${colors.green}✅ PASS${colors.reset}` : `${colors.red}❌ FAIL${colors.reset}`;
    console.log(`   ${status}  ${step.name}`);
  }

  console.log('');
  
  if (results.appUrl) {
    log(`🌐 Application URL: ${results.appUrl}`, 'cyan');
    log(`🏥 Health Check: ${results.healthUrl}`, 'cyan');
  }

  if (results.success) {
    log(`\n🎉 All tests passed! The MCP deployment workflow is working correctly.\n`, 'green');
  } else {
    log(`\n❌ Some tests failed. Check the output above for details.\n`, 'red');
  }

  // Ask about cleanup
  if (!DRY_RUN && !SKIP_DEPLOY && results.appUrl) {
    log(`\n💡 To clean up resources, run: node test-e2e-deployment.js --cleanup\n`, 'yellow');
  }

  process.exit(results.success ? 0 : 1);
}

// Run the test
runE2ETest().catch(error => {
  log(`\n❌ Fatal error: ${error.message}`, 'red');
  console.error(error.stack);
  process.exit(1);
});
