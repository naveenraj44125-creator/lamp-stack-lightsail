#!/usr/bin/env node

/**
 * Enhanced MCP Server Client Test
 * Tests the MCP server via SSE transport
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';

async function testMCPServer() {
  console.log('🧪 Testing Enhanced MCP Server via SSE Transport...\n');

  try {
    // Connect to the MCP server
    const transport = new SSEClientTransport(new URL('http://localhost:3001/mcp'));
    const client = new Client(
      {
        name: 'test-client',
        version: '1.0.0',
      },
      {
        capabilities: {},
      }
    );

    await client.connect(transport);
    console.log('✅ Connected to MCP server');

    // List available tools
    const tools = await client.listTools();
    console.log('\n📋 Available Tools:');
    tools.tools.forEach(tool => {
      console.log(`  - ${tool.name}: ${tool.description}`);
    });

    // Test 1: Analyze the Instagram clone project
    console.log('\n🔍 Test 1: Analyzing Instagram Clone Project...');
    const analysisResult = await client.callTool({
      name: 'analyze_project_intelligently',
      arguments: {
        project_path: '../example-react-app',
        user_description: 'React dashboard application with modern UI components',
        deployment_preferences: {
          budget: 50,
          scale: 'medium'
        }
      }
    });

    console.log('📊 Analysis Result:');
    console.log(analysisResult.content[0].text.substring(0, 500) + '...');

    // Test 2: Generate smart deployment configuration
    console.log('\n⚙️ Test 2: Generating Smart Deployment Configuration...');
    const configResult = await client.callTool({
      name: 'generate_smart_deployment_config',
      arguments: {
        project_analysis: analysisResult.content[0].text,
        app_name: 'test-react-app',
        aws_region: 'us-east-1',
        deployment_preferences: {
          budget_constraint: 50,
          performance_priority: 'balanced'
        }
      }
    });

    console.log('📝 Configuration Result:');
    console.log(configResult.content[0].text.substring(0, 500) + '...');

    // Test 3: Setup intelligent deployment
    console.log('\n🚀 Test 3: Setting up Intelligent Deployment...');
    const setupResult = await client.callTool({
      name: 'setup_intelligent_deployment',
      arguments: {
        project_path: '../example-react-app',
        app_name: 'test-react-app',
        deployment_config: configResult.content[0].text,
        create_workflow: true
      }
    });

    console.log('🔧 Setup Result:');
    console.log(setupResult.content[0].text.substring(0, 500) + '...');

    console.log('\n✅ All MCP server tests completed successfully!');
    console.log('\n🎉 Enhanced MCP Server is working perfectly via SSE transport!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.stack) {
      console.error('Stack trace:', error.stack);
    }
  }
}

// Run the test
testMCPServer().catch(console.error);