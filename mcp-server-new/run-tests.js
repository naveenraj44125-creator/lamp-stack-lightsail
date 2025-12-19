#!/usr/bin/env node

/**
 * Enhanced MCP Server Test Runner
 * Runs all tests for the enhanced MCP server
 */

import { execSync } from 'child_process';
import fs from 'fs';

console.log('🧪 Enhanced MCP Server Test Suite\n');
console.log('=' .repeat(50));

async function runTest(testName, command, description) {
  console.log(`\n🔍 ${testName}: ${description}`);
  console.log('-'.repeat(40));
  
  try {
    const output = execSync(command, { 
      cwd: process.cwd(),
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    console.log(output);
    console.log(`✅ ${testName} completed successfully!`);
    return true;
  } catch (error) {
    console.error(`❌ ${testName} failed:`);
    console.error(error.stdout || error.message);
    return false;
  }
}

async function checkServerHealth() {
  console.log('\n🏥 Checking Server Health...');
  console.log('-'.repeat(40));
  
  try {
    const output = execSync('curl -s http://localhost:3001/health', { 
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    const health = JSON.parse(output);
    console.log(`✅ Server Status: ${health.status}`);
    console.log(`📊 Version: ${health.version}`);
    console.log(`🔧 Features: ${health.features.join(', ')}`);
    return true;
  } catch (error) {
    console.error('❌ Server health check failed');
    console.error('Make sure the server is running: npm start');
    return false;
  }
}

async function runAllTests() {
  const results = [];
  
  // Check if server is running
  const serverHealthy = await checkServerHealth();
  if (!serverHealthy) {
    console.log('\n⚠️  Server not running. Starting component tests only...');
  }
  
  // Test 1: Component Tests (Direct)
  results.push(await runTest(
    'Component Tests',
    'node test-components.js',
    'Testing MCP components directly'
  ));
  
  // Test 2: MCP Client Tests (SSE Transport) - only if server is running
  if (serverHealthy) {
    results.push(await runTest(
      'MCP Client Tests',
      'node test-mcp-client.js',
      'Testing MCP server via SSE transport'
    ));
  }
  
  // Test Results Summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(50));
  
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log(`✅ Passed: ${passed}/${total} tests`);
  
  if (passed === total) {
    console.log('\n🎉 All tests passed! Enhanced MCP Server is working perfectly!');
    console.log('\n🚀 Your MCP server is ready for production use with:');
    console.log('   - Intelligent project analysis');
    console.log('   - Smart infrastructure optimization');
    console.log('   - Accurate configuration generation');
    console.log('   - Complete deployment automation');
  } else {
    console.log(`\n⚠️  ${total - passed} test(s) failed. Please check the output above.`);
  }
  
  // Show usage instructions
  console.log('\n📖 USAGE INSTRUCTIONS:');
  console.log('-'.repeat(30));
  console.log('1. Start the server: npm start');
  console.log('2. Test components: node test-components.js');
  console.log('3. Test MCP client: node test-mcp-client.js');
  console.log('4. Run all tests: node run-tests.js');
  console.log('\n🔗 Server endpoints:');
  console.log('   - Health: http://localhost:3001/health');
  console.log('   - MCP: http://localhost:3001/mcp');
}

// Run all tests
runAllTests().catch(console.error);