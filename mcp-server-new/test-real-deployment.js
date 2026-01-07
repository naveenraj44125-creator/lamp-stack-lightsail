#!/usr/bin/env node

/**
 * Real deployment test - actually creates Lightsail instance
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

import { LightsailClient, CreateInstancesCommand, GetInstanceCommand, GetInstancesCommand, OpenInstancePublicPortsCommand } from '@aws-sdk/client-lightsail';
import { STSClient, GetCallerIdentityCommand } from '@aws-sdk/client-sts';

const TEST_APP_PATH = path.join(__dirname, '..', 'example-test-app');
const INSTANCE_NAME = 'mcp-test-instance';
const REGION = 'us-east-1';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitForInstance(lightsailClient, instanceName, maxWaitSeconds = 300) {
  console.log(`   Waiting for instance to be running (max ${maxWaitSeconds}s)...`);
  const startTime = Date.now();
  
  while ((Date.now() - startTime) < maxWaitSeconds * 1000) {
    try {
      const response = await lightsailClient.send(new GetInstanceCommand({ instanceName }));
      const state = response.instance?.state?.name;
      const ip = response.instance?.publicIpAddress;
      
      process.stdout.write(`\r   State: ${state}, IP: ${ip || 'pending'}          `);
      
      if (state === 'running' && ip) {
        console.log('\n   ✅ Instance is running!');
        return response.instance;
      }
    } catch (e) {
      // Instance might not exist yet
    }
    await sleep(10000);
  }
  
  throw new Error('Timeout waiting for instance');
}

async function testRealDeployment() {
  console.log('🚀 REAL Deployment Test - Creating Lightsail Instance\n');
  console.log('=' .repeat(70));
  console.log('⚠️  This will create actual AWS resources!\n');

  const lightsailClient = new LightsailClient({ region: REGION });

  // Step 1: Check AWS credentials
  console.log('📋 Step 1: Verifying AWS Credentials...');
  try {
    const stsClient = new STSClient({ region: REGION });
    const identity = await stsClient.send(new GetCallerIdentityCommand({}));
    console.log(`   ✅ AWS Account: ${identity.Account}`);
  } catch (e) {
    console.log(`   ❌ AWS credentials failed: ${e.message}`);
    process.exit(1);
  }

  // Step 2: Check if instance already exists
  console.log('\n☁️ Step 2: Checking for existing instance...');
  let instance = null;
  try {
    const response = await lightsailClient.send(new GetInstanceCommand({ instanceName: INSTANCE_NAME }));
    instance = response.instance;
    console.log(`   ✅ Instance "${INSTANCE_NAME}" already exists`);
    console.log(`      State: ${instance.state?.name}`);
    console.log(`      IP: ${instance.publicIpAddress || 'pending'}`);
  } catch (e) {
    console.log(`   ℹ️ Instance not found, will create new one`);
  }

  // Step 3: Create instance if needed
  if (!instance) {
    console.log('\n🔨 Step 3: Creating Lightsail Instance...');
    
    const userData = `#!/bin/bash
# Setup script for MCP test app
apt-get update
apt-get install -y nodejs npm git

# Create app directory
mkdir -p /opt/mcp-test-app
cd /opt/mcp-test-app

# Create a simple test app
cat > server.js << 'EOF'
const http = require('http');
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({status: 'healthy', timestamp: new Date().toISOString()}));
  } else {
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({message: 'MCP Test App Running!', deployed: true}));
  }
});
server.listen(3000, '0.0.0.0', () => console.log('Server on port 3000'));
EOF

# Install PM2 and start app
npm install -g pm2
pm2 start server.js --name mcp-test-app
pm2 startup
pm2 save

echo "Setup complete!"
`;

    try {
      const createResponse = await lightsailClient.send(new CreateInstancesCommand({
        instanceNames: [INSTANCE_NAME],
        blueprintId: 'ubuntu_22_04',
        bundleId: 'nano_3_0',
        availabilityZone: `${REGION}a`,
        userData: userData
      }));
      
      console.log(`   ✅ Instance creation initiated`);
      
      // Wait for instance to be running
      instance = await waitForInstance(lightsailClient, INSTANCE_NAME);
    } catch (e) {
      console.log(`   ❌ Instance creation failed: ${e.message}`);
      process.exit(1);
    }
  }

  // Step 4: Open port 3000
  console.log('\n🔓 Step 4: Opening port 3000...');
  try {
    await lightsailClient.send(new OpenInstancePublicPortsCommand({
      instanceName: INSTANCE_NAME,
      portInfo: {
        fromPort: 3000,
        toPort: 3000,
        protocol: 'tcp'
      }
    }));
    console.log('   ✅ Port 3000 opened');
  } catch (e) {
    console.log(`   ⚠️ Port config: ${e.message}`);
  }

  // Step 5: Wait for app to start (give it time for user-data script)
  console.log('\n⏳ Step 5: Waiting for application to start (60s for user-data)...');
  await sleep(60000);

  // Step 6: Test the deployment
  console.log('\n🧪 Step 6: Testing deployment...');
  const instanceIp = instance?.publicIpAddress;
  
  if (!instanceIp) {
    // Refresh instance info
    const response = await lightsailClient.send(new GetInstanceCommand({ instanceName: INSTANCE_NAME }));
    instance = response.instance;
  }
  
  const ip = instance?.publicIpAddress;
  console.log(`   Instance IP: ${ip}`);
  
  if (ip) {
    // Test health endpoint
    console.log(`\n   Testing http://${ip}:3000/health ...`);
    try {
      const result = execSync(`curl -s --connect-timeout 10 http://${ip}:3000/health 2>&1 || echo "FAILED"`, {
        encoding: 'utf8'
      });
      
      if (result.includes('healthy')) {
        console.log(`   ✅ Health check passed!`);
        console.log(`   Response: ${result.trim()}`);
      } else {
        console.log(`   ⚠️ Health check response: ${result.trim()}`);
        console.log('   (App may still be starting up from user-data script)');
      }
    } catch (e) {
      console.log(`   ⚠️ Health check failed: ${e.message}`);
      console.log('   (This is normal if the app is still starting)');
    }

    // Test root endpoint
    console.log(`\n   Testing http://${ip}:3000/ ...`);
    try {
      const result = execSync(`curl -s --connect-timeout 10 http://${ip}:3000/ 2>&1 || echo "FAILED"`, {
        encoding: 'utf8'
      });
      console.log(`   Response: ${result.trim()}`);
    } catch (e) {
      console.log(`   ⚠️ Root endpoint: ${e.message}`);
    }
  }

  // Summary
  console.log('\n' + '=' .repeat(70));
  console.log('📊 DEPLOYMENT SUMMARY\n');
  console.log(`   Instance Name: ${INSTANCE_NAME}`);
  console.log(`   Instance IP: ${ip || 'pending'}`);
  console.log(`   Region: ${REGION}`);
  console.log(`   Bundle: nano_3_0 ($3.50/month)`);
  console.log(`\n   URLs:`);
  console.log(`   - App: http://${ip}:3000/`);
  console.log(`   - Health: http://${ip}:3000/health`);
  console.log(`   - Console: https://lightsail.aws.amazon.com/ls/webapp/home/instances`);
  console.log('\n' + '=' .repeat(70));
  
  console.log('\n✅ Real deployment test complete!');
  console.log('\nNote: If health check failed, wait 2-3 minutes for user-data script to complete,');
  console.log('then test manually: curl http://' + ip + ':3000/health');
}

testRealDeployment().catch(e => {
  console.error('Deployment failed:', e);
  process.exit(1);
});
