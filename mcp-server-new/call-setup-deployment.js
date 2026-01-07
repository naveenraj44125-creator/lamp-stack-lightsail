#!/usr/bin/env node

/**
 * Call setup_intelligent_deployment directly
 * This script imports the server class and calls the tool method directly
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  console.log('🚀 Setting up deployment via setup-complete-deployment.sh...\n');
  
  // Get the demo-app path
  const demoAppPath = path.resolve(__dirname, '..', 'demo-app');
  const setupScriptPath = path.resolve(__dirname, '..', 'setup-complete-deployment.sh');
  
  console.log(`📁 Demo app path: ${demoAppPath}`);
  console.log(`📜 Setup script: ${setupScriptPath}`);

  // Environment variables for AUTO_MODE
  const envVars = {
    AUTO_MODE: 'true',
    APP_TYPE: 'nodejs',
    APP_NAME: 'MCP Demo App',
    INSTANCE_NAME: 'mcp-demo-instance',
    AWS_REGION: 'us-east-1',
    BUNDLE_ID: 'micro_3_0',
    BLUEPRINT_ID: 'ubuntu_22_04',
    DATABASE_TYPE: 'none',
    GITHUB_REPO: 'mcp-demo-app',
    REPO_VISIBILITY: 'public',
    HEALTH_CHECK_ENDPOINT: '/health',
    VERIFICATION_ENDPOINT: '/'
  };

  // Build the command
  const envString = Object.entries(envVars)
    .map(([k, v]) => `${k}="${v}"`)
    .join(' ');
  
  const command = `cd "${demoAppPath}" && ${envString} bash "${setupScriptPath}"`;
  
  console.log('\n📊 Running setup script with AUTO_MODE...\n');
  console.log('Environment variables:');
  Object.entries(envVars).forEach(([k, v]) => console.log(`  ${k}=${v}`));
  console.log('\n' + '='.repeat(70) + '\n');

  try {
    const output = execSync(command, {
      encoding: 'utf8',
      timeout: 600000, // 10 minute timeout
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    console.log(output);
    console.log('\n' + '='.repeat(70));
    console.log('✅ Setup completed successfully!');
  } catch (error) {
    console.error('❌ Setup failed:', error.message);
    if (error.stdout) console.log('STDOUT:', error.stdout);
    if (error.stderr) console.error('STDERR:', error.stderr);
    process.exit(1);
  }
}

main();
