#!/usr/bin/env node

/**
 * Test MCP Server using SSE (Server-Sent Events) protocol
 * This is how MCP actually works - SSE for server->client, POST for client->server
 */

const SERVER_URL = 'http://52.202.252.239:3000';

async function testWithSSE() {
  console.log('🧪 Testing MCP Server with SSE Protocol');
  console.log('========================================\n');

  // Step 1: Connect to SSE endpoint
  console.log('1️⃣  Connecting to SSE endpoint...');
  
  const { EventSource } = await import('eventsource');
  const eventSource = new EventSource(`${SERVER_URL}/sse`);
  
  let sessionId = null;
  let messageEndpoint = null;

  eventSource.onopen = () => {
    console.log('   ✅ SSE connection established');
  };

  eventSource.addEventListener('endpoint', (event) => {
    messageEndpoint = event.data;
    console.log('   📍 Message endpoint:', messageEndpoint);
    
    // Extract session ID from endpoint
    const match = messageEndpoint.match(/sessionId=([^&]+)/);
    if (match) {
      sessionId = match[1];
      console.log('   🔑 Session ID:', sessionId);
    }
  });

  const receivedMessages = [];
  
  eventSource.addEventListener('message', (event) => {
    console.log('   📨 Received message:', event.data);
    try {
      const data = JSON.parse(event.data);
      receivedMessages.push(data);
      console.log('      ', JSON.stringify(data, null, 2));
    } catch (e) {
      // Not JSON, just log as is
      console.log('       (not JSON)');
    }
  });

  eventSource.onerror = (error) => {
    console.error('   ❌ SSE Error:', error);
  };

  // Wait for connection to establish
  await new Promise(resolve => setTimeout(resolve, 2000));

  if (!messageEndpoint) {
    console.log('   ❌ Failed to get message endpoint');
    eventSource.close();
    return;
  }

  // Step 2: Send initialize command
  console.log('\n2️⃣  Sending initialize command...');
  const initMessage = {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'test-client',
        version: '1.0.0'
      }
    }
  };

  try {
    const response = await fetch(`${SERVER_URL}${messageEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(initMessage)
    });
    console.log('   Status:', response.status);
    if (!response.ok) {
      const errorText = await response.text();
      console.log('   Error:', errorText);
    }
  } catch (error) {
    console.error('   ❌ Error:', error.message);
  }

  // Wait for response
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Step 3: List tools
  console.log('\n3️⃣  Requesting tools list...');
  const toolsMessage = {
    jsonrpc: '2.0',
    id: 2,
    method: 'tools/list',
    params: {}
  };

  try {
    const response = await fetch(`${SERVER_URL}${messageEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(toolsMessage)
    });
    console.log('   Status:', response.status);
  } catch (error) {
    console.error('   ❌ Error:', error.message);
  }

  // Wait for response
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Step 4: Call a tool
  console.log('\n4️⃣  Calling list_instances tool...');
  const callMessage = {
    jsonrpc: '2.0',
    id: 3,
    method: 'tools/call',
    params: {
      name: 'list_instances',
      arguments: {
        aws_region: 'us-east-1'
      }
    }
  };

  try {
    const response = await fetch(`${SERVER_URL}${messageEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(callMessage)
    });
    console.log('   Status:', response.status);
  } catch (error) {
    console.error('   ❌ Error:', error.message);
  }

  // Wait for response
  await new Promise(resolve => setTimeout(resolve, 3000));

  console.log('\n✅ Test completed!');
  console.log(`\n📊 Summary: Received ${receivedMessages.length} messages`);
  
  if (receivedMessages.length > 0) {
    console.log('\n📋 All received messages:');
    receivedMessages.forEach((msg, i) => {
      console.log(`\n   Message ${i + 1}:`);
      console.log('   ', JSON.stringify(msg, null, 2).split('\n').join('\n    '));
    });
  }
  
  eventSource.close();
  process.exit(0);
}

// Check if eventsource is installed
import('eventsource')
  .then(() => testWithSSE())
  .catch(() => {
    console.log('❌ eventsource package not found');
    console.log('📦 Installing eventsource...\n');
    
    const { execSync } = require('child_process');
    execSync('npm install eventsource', { stdio: 'inherit' });
    
    console.log('\n✅ Package installed, running test...\n');
    testWithSSE();
  });
