#!/usr/bin/env node

/**
 * Simple MCP Client to test the deployed Lightsail MCP Server
 * 
 * Usage: node test-mcp-client.js
 */

const SERVER_URL = 'http://52.202.252.239:3000';

console.log('🧪 Testing MCP Server on Lightsail');
console.log('==================================\n');

// Test 1: Health Check
async function testHealth() {
  console.log('1️⃣  Health Check:');
  try {
    const response = await fetch(`${SERVER_URL}/health`);
    const data = await response.json();
    console.log('✅ Server is healthy:', data);
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return false;
  }
}

// Test 2: SSE Connection
async function testSSE() {
  console.log('\n2️⃣  Testing SSE Connection:');
  console.log('   Note: SSE requires a persistent connection.');
  console.log('   For full testing, use an MCP client like Claude Desktop or the MCP Inspector.');
  console.log('   SSE Endpoint: ' + SERVER_URL + '/sse');
}

// Test 3: Available Tools Documentation
async function showAvailableTools() {
  console.log('\n3️⃣  Available MCP Tools:');
  console.log('   The server provides these tools:');
  console.log('   • setup_new_repository - Create a new GitHub repo with Lightsail deployment');
  console.log('   • deploy_to_lightsail - Deploy an application to Lightsail');
  console.log('   • list_instances - List all Lightsail instances');
  console.log('   • get_deployment_status - Check deployment status');
}

// Main test function
async function runTests() {
  const healthy = await testHealth();
  
  if (!healthy) {
    console.log('\n❌ Server is not responding. Please check the deployment.');
    process.exit(1);
  }
  
  await testSSE();
  await showAvailableTools();
  
  console.log('\n✅ Basic tests complete!');
  console.log('\n📝 Next Steps:');
  console.log('   1. Configure this server in your MCP client (Claude Desktop, etc.)');
  console.log('   2. Add to your MCP config:');
  console.log('      {');
  console.log('        "mcpServers": {');
  console.log('          "lightsail-deployment": {');
  console.log('            "url": "' + SERVER_URL + '"');
  console.log('          }');
  console.log('        }');
  console.log('      }');
  console.log('   3. Use the MCP Inspector for interactive testing:');
  console.log('      npx @modelcontextprotocol/inspector ' + SERVER_URL);
}

runTests().catch(console.error);
