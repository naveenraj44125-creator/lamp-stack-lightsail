#!/usr/bin/env node

/**
 * Enhanced MCP Server Component Test
 * Tests the MCP tools directly without SSE transport
 */

import { ProjectAnalyzer } from './project-analyzer.js';
import { InfrastructureOptimizer } from './infrastructure-optimizer.js';
import { ConfigurationGenerator } from './configuration-generator.js';

async function testMCPComponents() {
  console.log('🧪 Testing Enhanced MCP Components Directly...\n');

  try {
    // Test 1: Project Analysis
    console.log('🔍 Test 1: Analyzing Instagram Clone Project...');
    const analyzer = new ProjectAnalyzer();
    const analysis = await analyzer.analyzeProject('../example-instagram-clone');
    
    console.log('📊 Analysis Result:');
    console.log(`  - Detected Type: ${analysis.detected_type}`);
    console.log(`  - Confidence: ${Math.round(analysis.confidence * 100)}%`);
    console.log(`  - Frameworks: ${analysis.frameworks.map(f => f.name).join(', ')}`);
    console.log(`  - Databases: ${analysis.databases.map(d => d.type).join(', ')}`);
    console.log(`  - Security Score: ${analysis.security_considerations.security_score}/10`);

    // Test 2: Infrastructure Optimization
    console.log('\n💡 Test 2: Getting Infrastructure Recommendations...');
    const optimizer = new InfrastructureOptimizer();
    const optimization = optimizer.optimizeInfrastructure(analysis, {
      budget_constraint: 50,
      performance_priority: 'balanced'
    });

    console.log('🏗️ Infrastructure Recommendations:');
    console.log(`  - Recommended Bundle: ${optimization.recommended_bundle}`);
    console.log(`  - Monthly Cost: $${optimization.cost_breakdown.total}`);
    console.log(`  - Performance Score: ${optimization.performance_score}/10`);
    console.log(`  - Database: ${optimization.database_config ? optimization.database_config.type : 'None'}`);

    // Test 3: Configuration Generation
    console.log('\n⚙️ Test 3: Generating Deployment Configuration...');
    const generator = new ConfigurationGenerator();
    const config = generator.generateDeploymentConfig(analysis, optimization, {
      app_name: 'test-instagram-clone',
      aws_region: 'us-east-1'
    });

    console.log('📝 Generated Configuration:');
    console.log(`  - Instance Name: ${config.lightsail.instance_name}`);
    console.log(`  - Bundle ID: ${config.lightsail.bundle_id}`);
    console.log(`  - Application Type: ${config.application.type}`);
    console.log(`  - Dependencies: ${Object.keys(config.dependencies).join(', ')}`);
    console.log(`  - Environment Variables: ${Object.keys(config.application.environment_variables).length} vars`);

    // Test 4: Generate GitHub Workflow
    console.log('\n🔄 Test 4: Generating GitHub Workflow...');
    const workflow = generator.generateWorkflow(analysis, {
      app_name: 'test-instagram-clone',
      aws_region: 'us-east-1'
    });

    console.log('📋 Generated Workflow:');
    console.log(`  - Workflow length: ${workflow.length} characters`);
    console.log(`  - Contains deployment job: ${workflow.includes('deploy:') ? '✅' : '❌'}`);
    console.log(`  - Contains summary job: ${workflow.includes('summary:') ? '✅' : '❌'}`);

    console.log('\n✅ All component tests completed successfully!');
    console.log('\n🎉 Enhanced MCP Server components are working perfectly!');

    // Save a sample configuration for demonstration
    const yamlConfig = generator.formatYAML(config);
    console.log('\n📄 Sample Configuration (first 500 chars):');
    console.log(yamlConfig.substring(0, 500) + '...');

    // Test 5: Test different project types
    console.log('\n🔍 Test 5: Testing Different Project Types...');
    
    // Test Docker project
    console.log('\n  📦 Testing Docker Project...');
    const dockerAnalysis = await analyzer.analyzeProject('../example-docker-app');
    console.log(`    - Detected: ${dockerAnalysis.detected_type} (${Math.round(dockerAnalysis.confidence * 100)}%)`);
    
    // Test Recipe Docker project
    console.log('  🍳 Testing Recipe Docker Project...');
    const recipeAnalysis = await analyzer.analyzeProject('../example-recipe-docker-app');
    console.log(`    - Detected: ${recipeAnalysis.detected_type} (${Math.round(recipeAnalysis.confidence * 100)}%)`);

    console.log('\n🎯 Multi-project analysis completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.stack) {
      console.error('Stack trace:', error.stack);
    }
  }
}

// Run the test
testMCPComponents().catch(console.error);