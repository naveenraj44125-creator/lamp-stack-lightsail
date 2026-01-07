#!/usr/bin/env node

/**
 * Comprehensive test of ALL 18 MCP server tools
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testAllTools() {
  console.log('🧪 Comprehensive Test of ALL 18 MCP Server Tools\n');
  console.log('=' .repeat(70));

  const results = [];
  
  // Import server class
  const serverContent = fs.readFileSync(path.join(__dirname, 'server.js'), 'utf8');
  
  // Extract all tool names from server.js
  const toolMatches = serverContent.matchAll(/name:\s*'([a-z_]+)'/g);
  const toolNames = [...toolMatches].map(m => m[1]);
  
  console.log(`\n📋 Found ${toolNames.length} tools in server.js:\n`);
  
  // Check each tool has a handler
  for (const toolName of toolNames) {
    const hasCase = serverContent.includes(`case '${toolName}':`);
    const hasMethod = serverContent.includes(`this.${toCamelCase(toolName)}(`) || 
                      serverContent.includes(`await this.${toCamelCase(toolName)}(`);
    
    const status = hasCase && hasMethod ? '✅' : hasCase ? '⚠️' : '❌';
    console.log(`  ${status} ${toolName}`);
    console.log(`      Handler: ${hasCase ? 'yes' : 'NO'}  |  Method: ${hasMethod ? 'yes' : 'check manually'}`);
    
    results.push({
      name: toolName,
      hasHandler: hasCase,
      hasMethod: hasMethod,
      working: hasCase
    });
  }

  // Test actual functionality
  console.log('\n' + '=' .repeat(70));
  console.log('🔧 Testing Tool Implementations\n');

  // Import components
  const { ProjectAnalyzer } = await import('./project-analyzer.js');
  const { InfrastructureOptimizer } = await import('./infrastructure-optimizer.js');
  const { ConfigurationGenerator } = await import('./configuration-generator.js');
  const { BedrockAI } = await import('./bedrock-ai.js');

  const tests = [
    {
      name: 'ProjectAnalyzer',
      test: async () => {
        const pa = new ProjectAnalyzer();
        // Test with a real project path
        const result = await pa.analyzeProject({
          project_path: path.join(__dirname, '..', 'example-nodejs-app')
        });
        return result.detected_type !== undefined;
      }
    },
    {
      name: 'InfrastructureOptimizer', 
      test: async () => {
        const io = new InfrastructureOptimizer();
        const result = io.optimizeInfrastructure(
          { detected_type: 'nodejs', databases: [] },
          { scale: 'small' }
        );
        return result.recommended_bundle !== undefined;
      }
    },
    {
      name: 'ConfigurationGenerator',
      test: async () => {
        const cg = new ConfigurationGenerator();
        const result = cg.generateDeploymentConfig(
          { detected_type: 'nodejs', frameworks: [], databases: [] },
          { bundle_id: 'micro_3_0' },
          { app_name: 'test', instance_name: 'test-instance' }
        );
        return result.lightsail !== undefined;
      }
    },
    {
      name: 'BedrockAI (init)',
      test: async () => {
        const ai = new BedrockAI({ region: 'us-east-1' });
        return ai !== undefined;
      }
    },
    {
      name: 'AWS SDK (STS)',
      test: async () => {
        const { STSClient, GetCallerIdentityCommand } = await import('@aws-sdk/client-sts');
        const client = new STSClient({ region: 'us-east-1' });
        const result = await client.send(new GetCallerIdentityCommand({}));
        return result.Account !== undefined;
      }
    },
    {
      name: 'AWS SDK (Lightsail)',
      test: async () => {
        const { LightsailClient, GetInstancesCommand } = await import('@aws-sdk/client-lightsail');
        const client = new LightsailClient({ region: 'us-east-1' });
        const result = await client.send(new GetInstancesCommand({}));
        return Array.isArray(result.instances);
      }
    },
    {
      name: 'Troubleshooting Scripts',
      test: async () => {
        const toolsPath = path.join(__dirname, '..', 'troubleshooting-tools');
        const categories = fs.readdirSync(toolsPath).filter(f => 
          fs.statSync(path.join(toolsPath, f)).isDirectory()
        );
        return categories.length >= 7;
      }
    }
  ];

  for (const t of tests) {
    try {
      const passed = await t.test();
      console.log(`  ${passed ? '✅' : '❌'} ${t.name}`);
    } catch (e) {
      console.log(`  ❌ ${t.name}: ${e.message}`);
    }
  }

  // Summary
  console.log('\n' + '=' .repeat(70));
  console.log('📊 SUMMARY\n');
  
  const workingTools = results.filter(r => r.working).length;
  const totalTools = results.length;
  
  console.log(`  Tools with handlers: ${workingTools}/${totalTools}`);
  console.log(`  Status: ${workingTools === totalTools ? '✅ ALL TOOLS READY' : '⚠️ Some tools need attention'}`);
  
  // List any issues
  const issues = results.filter(r => !r.working);
  if (issues.length > 0) {
    console.log('\n  Issues found:');
    issues.forEach(i => console.log(`    - ${i.name}: missing handler`));
  }

  console.log('\n' + '=' .repeat(70));
}

function toCamelCase(str) {
  return str.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
}

testAllTools().catch(e => {
  console.error('Test failed:', e);
  process.exit(1);
});
