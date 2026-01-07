#!/usr/bin/env node

/**
 * Full GitHub Integration Test
 * 
 * This script automates the ENTIRE GitHub Actions integration:
 * 1. Creates a new GitHub repository
 * 2. Configures GitHub secrets (AWS_ROLE_ARN, AWS_REGION, etc.)
 * 3. Initializes git and pushes the code
 * 4. Triggers the deployment workflow
 * 
 * No manual steps needed!
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const CONFIG = {
  appName: 'mcp-test-app',
  repoName: 'mcp-lightsail-test-app',
  githubUsername: 'naveenraj44125-creator',
  awsRegion: 'us-east-1',
  roleArn: 'arn:aws:iam::257429339749:role/github-actions-mcp-test',
  instanceName: 'mcp-test-instance',
  instanceIp: '98.83.151.39',
  appDir: path.join(__dirname, '..', 'example-test-app')
};

function run(cmd, options = {}) {
  console.log(`\n$ ${cmd}`);
  try {
    const result = execSync(cmd, { 
      encoding: 'utf8', 
      stdio: options.silent ? 'pipe' : 'inherit',
      cwd: options.cwd || process.cwd(),
      ...options
    });
    return { success: true, output: result };
  } catch (e) {
    if (options.ignoreError) {
      return { success: false, error: e.message };
    }
    throw e;
  }
}

function runSilent(cmd, options = {}) {
  return run(cmd, { ...options, silent: true, stdio: 'pipe' });
}

async function main() {
  console.log('='.repeat(60));
  console.log('🚀 Full GitHub Integration Test');
  console.log('='.repeat(60));
  console.log('\nThis will:');
  console.log('1. Create GitHub repository');
  console.log('2. Configure GitHub secrets');
  console.log('3. Push code to trigger deployment');
  console.log('');

  // Step 1: Check gh CLI
  console.log('\n📋 Step 1: Checking GitHub CLI...');
  const ghAuth = runSilent('gh auth status', { ignoreError: true });
  if (!ghAuth.success) {
    console.error('❌ GitHub CLI not authenticated. Run: gh auth login');
    process.exit(1);
  }
  console.log('✅ GitHub CLI authenticated');

  // Step 2: Check if repo exists, create if not
  console.log('\n📋 Step 2: Creating GitHub repository...');
  const repoCheck = runSilent(`gh repo view ${CONFIG.githubUsername}/${CONFIG.repoName}`, { ignoreError: true });
  
  if (repoCheck.success) {
    console.log(`✅ Repository ${CONFIG.repoName} already exists`);
  } else {
    console.log(`Creating new repository: ${CONFIG.repoName}`);
    run(`gh repo create ${CONFIG.repoName} --public --description "MCP Lightsail Deployment Test App"`);
    console.log('✅ Repository created');
  }

  // Step 3: Configure GitHub secrets
  console.log('\n📋 Step 3: Configuring GitHub secrets...');
  const secrets = {
    'AWS_ROLE_ARN': CONFIG.roleArn,
    'AWS_REGION': CONFIG.awsRegion,
    'LIGHTSAIL_INSTANCE_NAME': CONFIG.instanceName
  };

  for (const [name, value] of Object.entries(secrets)) {
    console.log(`  Setting ${name}...`);
    runSilent(`gh secret set ${name} --repo ${CONFIG.githubUsername}/${CONFIG.repoName} --body "${value}"`, { ignoreError: true });
  }
  console.log('✅ Secrets configured');

  // Step 4: Prepare the app directory for push
  console.log('\n📋 Step 4: Preparing app for deployment...');
  
  // Create a temporary directory for the standalone app
  const tempDir = path.join(__dirname, '..', 'temp-deploy-app');
  if (fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true });
  }
  fs.mkdirSync(tempDir, { recursive: true });

  // Copy app files
  const filesToCopy = [
    'package.json',
    'src/server.js',
    '.env.example',
    '.github/workflows/deploy.yml'
  ];

  for (const file of filesToCopy) {
    const srcPath = path.join(CONFIG.appDir, file);
    const destPath = path.join(tempDir, file);
    
    if (fs.existsSync(srcPath)) {
      fs.mkdirSync(path.dirname(destPath), { recursive: true });
      fs.copyFileSync(srcPath, destPath);
      console.log(`  Copied: ${file}`);
    }
  }

  // Create .gitignore
  fs.writeFileSync(path.join(tempDir, '.gitignore'), 'node_modules/\n.env\n*.log\n');

  // Create README
  fs.writeFileSync(path.join(tempDir, 'README.md'), `# ${CONFIG.appName}

Test application for MCP Lightsail deployment tools.

## Deployment

This app is automatically deployed to AWS Lightsail via GitHub Actions.

- Instance: ${CONFIG.instanceName}
- IP: ${CONFIG.instanceIp}
- URL: http://${CONFIG.instanceIp}:3000

## Endpoints

- \`GET /\` - Hello World
- \`GET /health\` - Health check
`);

  console.log('✅ App files prepared');

  // Step 5: Initialize git and push
  console.log('\n📋 Step 5: Pushing to GitHub...');
  
  run('git init', { cwd: tempDir });
  run('git add .', { cwd: tempDir });
  run('git commit -m "Initial commit - MCP deployment test"', { cwd: tempDir });
  run('git branch -M main', { cwd: tempDir });
  run(`git remote add origin https://github.com/${CONFIG.githubUsername}/${CONFIG.repoName}.git`, { cwd: tempDir, ignoreError: true });
  run('git push -u origin main --force', { cwd: tempDir });
  
  console.log('✅ Code pushed to GitHub');

  // Step 6: Check workflow status
  console.log('\n📋 Step 6: Checking workflow status...');
  
  // Wait a moment for GitHub to process
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  const workflowStatus = runSilent(`gh run list --repo ${CONFIG.githubUsername}/${CONFIG.repoName} --limit 1`, { ignoreError: true });
  if (workflowStatus.success && workflowStatus.output) {
    console.log('Workflow runs:');
    console.log(workflowStatus.output);
  }

  // Cleanup temp directory
  fs.rmSync(tempDir, { recursive: true });

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('✅ FULL GITHUB INTEGRATION COMPLETE!');
  console.log('='.repeat(60));
  console.log(`
📦 Repository: https://github.com/${CONFIG.githubUsername}/${CONFIG.repoName}
🔐 Secrets configured: AWS_ROLE_ARN, AWS_REGION, LIGHTSAIL_INSTANCE_NAME
🚀 Workflow: GitHub Actions will deploy on push to main

🌐 Application URLs:
   - App: http://${CONFIG.instanceIp}:3000
   - Health: http://${CONFIG.instanceIp}:3000/health

📊 Monitor workflow:
   gh run watch --repo ${CONFIG.githubUsername}/${CONFIG.repoName}
`);
}

main().catch(console.error);
