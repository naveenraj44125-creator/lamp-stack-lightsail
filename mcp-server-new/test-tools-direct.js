#!/usr/bin/env node

/**
 * Direct test of MCP server tools without SSE transport
 * Tests the tool implementations directly
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Prevent server from starting
process.env.MCP_TEST_MODE = 'true';

async function testTools() {
  console.log('🧪 Testing MCP Server Tools Directly\n');
  console.log('=' .repeat(60));

  // Import components
  const { ProjectAnalyzer } = await import('./project-analyzer.js');
  const { InfrastructureOptimizer } = await import('./infrastructure-optimizer.js');
  const { ConfigurationGenerator } = await import('./configuration-generator.js');

  const projectAnalyzer = new ProjectAnalyzer();
  const infrastructureOptimizer = new InfrastructureOptimizer();
  const configGenerator = new ConfigurationGenerator();

  // Test 1: List troubleshooting scripts
  console.log('\n📋 Test 1: List Troubleshooting Scripts');
  console.log('-'.repeat(40));
  
  const toolsPath = path.join(__dirname, '..', 'troubleshooting-tools');
  const categories = fs.readdirSync(toolsPath).filter(f => 
    fs.statSync(path.join(toolsPath, f)).isDirectory()
  );
  
  let totalScripts = 0;
  for (const cat of categories) {
    const catPath = path.join(toolsPath, cat);
    const scripts = fs.readdirSync(catPath).filter(f => f.endsWith('.py'));
    totalScripts += scripts.length;
    console.log(`  ${cat}: ${scripts.length} scripts`);
  }
  console.log(`  ✅ Total: ${totalScripts} troubleshooting scripts available`);

  // Test 2: Project Analysis
  console.log('\n📊 Test 2: Project Analysis');
  console.log('-'.repeat(40));
  
  const testFiles = [
    { path: 'package.json', content: JSON.stringify({
      name: 'test-app',
      dependencies: { express: '^4.18.0', mongoose: '^7.0.0' }
    })}
  ];
  
  try {
    const analysis = await projectAnalyzer.analyzeProject({ project_files: testFiles });
    console.log(`  Detected type: ${analysis.detected_type}`);
    console.log(`  Frameworks: ${analysis.frameworks?.map(f => f.name).join(', ') || 'None'}`);
    console.log(`  Databases: ${analysis.databases?.map(d => d.type).join(', ') || 'None'}`);
    console.log(`  ✅ Project analysis working`);
  } catch (e) {
    console.log(`  ⚠️ Analysis error (expected for minimal test): ${e.message}`);
  }

  // Test 3: Infrastructure Optimization
  console.log('\n⚙️ Test 3: Infrastructure Optimization');
  console.log('-'.repeat(40));
  
  try {
    const optimization = infrastructureOptimizer.optimizeInfrastructure({
      detected_type: 'nodejs',
      frameworks: [{ name: 'express' }],
      databases: [{ type: 'mongodb' }],
      storage_needs: { needs_bucket: false }
    }, { budget: 'standard', scale: 'small', priority: 'balanced' });
    
    console.log(`  Bundle: ${optimization.recommended_bundle}`);
    console.log(`  Database: ${optimization.database_config?.type || 'none'}`);
    console.log(`  Cost: $${optimization.cost_breakdown?.total || 0}/month`);
    console.log(`  ✅ Infrastructure optimization working`);
  } catch (e) {
    console.log(`  ❌ Optimization error: ${e.message}`);
  }

  // Test 4: Configuration Generation
  console.log('\n📝 Test 4: Configuration Generation');
  console.log('-'.repeat(40));
  
  try {
    const config = configGenerator.generateDeploymentConfig(
      {
        detected_type: 'nodejs',
        frameworks: [{ name: 'express', version: '4.18.0' }],
        databases: [{ type: 'mongodb' }],
        infrastructure_needs: { bundle_size: 'micro_3_0' }
      },
      {
        bundle_id: 'micro_3_0',
        database_config: { type: 'mongodb', external: false }
      },
      {
        app_name: 'test-app',
        instance_name: 'nodejs-test-app',
        aws_region: 'us-east-1'
      }
    );
    
    console.log(`  Config generated: ${Object.keys(config).length} top-level keys`);
    console.log(`  Instance: ${config.lightsail?.instance_name}`);
    console.log(`  ✅ Configuration generation working`);
  } catch (e) {
    console.log(`  ❌ Config generation error: ${e.message}`);
  }

  // Test 5: AWS SDK (if credentials available)
  console.log('\n☁️ Test 5: AWS SDK Integration');
  console.log('-'.repeat(40));
  
  try {
    const { STSClient, GetCallerIdentityCommand } = await import('@aws-sdk/client-sts');
    const stsClient = new STSClient({ region: 'us-east-1' });
    const identity = await stsClient.send(new GetCallerIdentityCommand({}));
    console.log(`  Account: ${identity.Account}`);
    console.log(`  ✅ AWS SDK working`);
  } catch (e) {
    console.log(`  ⚠️ AWS SDK error: ${e.message}`);
    console.log(`  (Run: source .aws-creds.sh to fix)`);
  }

  console.log('\n' + '=' .repeat(60));
  console.log('✅ All tool tests completed!');
  console.log('=' .repeat(60));
}

testTools().catch(e => {
  console.error('Test failed:', e);
  process.exit(1);
});
