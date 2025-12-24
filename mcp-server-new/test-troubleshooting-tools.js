#!/usr/bin/env node

/**
 * Test script for troubleshooting tools integration
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// Colors for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testTroubleshootingTools() {
  log('\n🔧 Testing Troubleshooting Tools Integration\n', 'cyan');
  
  const results = [];
  
  // Test 1: Verify troubleshooting-tools directory exists
  log('Test 1: Checking troubleshooting-tools directory...', 'blue');
  const toolsPath = path.join(projectRoot, 'troubleshooting-tools');
  if (fs.existsSync(toolsPath)) {
    log('  ✅ Directory exists', 'green');
    results.push({ name: 'Directory exists', passed: true });
  } else {
    log('  ❌ Directory not found', 'red');
    results.push({ name: 'Directory exists', passed: false });
  }
  
  // Test 2: Verify all categories exist
  log('\nTest 2: Checking script categories...', 'blue');
  const categories = ['docker', 'general', 'lamp', 'nginx', 'nodejs', 'python', 'react'];
  let allCategoriesExist = true;
  
  for (const cat of categories) {
    const catPath = path.join(toolsPath, cat);
    if (fs.existsSync(catPath)) {
      const scripts = fs.readdirSync(catPath).filter(f => f.endsWith('.py'));
      log(`  ✅ ${cat}: ${scripts.length} scripts`, 'green');
    } else {
      log(`  ❌ ${cat}: not found`, 'red');
      allCategoriesExist = false;
    }
  }
  results.push({ name: 'All categories exist', passed: allCategoriesExist });
  
  // Test 3: Verify server.js has troubleshooting tools
  log('\nTest 3: Checking server.js for troubleshooting tools...', 'blue');
  const serverPath = path.join(__dirname, 'server.js');
  const serverContent = fs.readFileSync(serverPath, 'utf8');
  
  const toolsToCheck = [
    'list_troubleshooting_scripts',
    'run_troubleshooting_script',
    'diagnose_deployment_issue',
    'get_instance_logs'
  ];
  
  let allToolsFound = true;
  for (const tool of toolsToCheck) {
    if (serverContent.includes(tool)) {
      log(`  ✅ ${tool} found`, 'green');
    } else {
      log(`  ❌ ${tool} not found`, 'red');
      allToolsFound = false;
    }
  }
  results.push({ name: 'All tools in server.js', passed: allToolsFound });
  
  // Test 4: Verify server starts correctly
  log('\nTest 4: Testing server startup...', 'blue');
  try {
    const output = execSync('timeout 3 node server.js 2>&1 || true', {
      cwd: __dirname,
      encoding: 'utf8'
    });
    
    if (output.includes('Enhanced Lightsail Deployment MCP Server')) {
      log('  ✅ Server starts correctly', 'green');
      results.push({ name: 'Server startup', passed: true });
    } else {
      log('  ❌ Server startup failed', 'red');
      results.push({ name: 'Server startup', passed: false });
    }
  } catch (error) {
    log(`  ❌ Server startup error: ${error.message}`, 'red');
    results.push({ name: 'Server startup', passed: false });
  }
  
  // Test 5: Verify README has troubleshooting documentation
  log('\nTest 5: Checking README documentation...', 'blue');
  const readmePath = path.join(__dirname, 'README.md');
  const readmeContent = fs.readFileSync(readmePath, 'utf8');
  
  const docsToCheck = [
    'Troubleshooting Tools',
    'list_troubleshooting_scripts',
    'diagnose_deployment_issue'
  ];
  
  let allDocsFound = true;
  for (const doc of docsToCheck) {
    if (readmeContent.includes(doc)) {
      log(`  ✅ "${doc}" documented`, 'green');
    } else {
      log(`  ❌ "${doc}" not documented`, 'red');
      allDocsFound = false;
    }
  }
  results.push({ name: 'README documentation', passed: allDocsFound });
  
  // Summary
  log('\n' + '='.repeat(50), 'cyan');
  log('TEST SUMMARY', 'cyan');
  log('='.repeat(50), 'cyan');
  
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  
  for (const result of results) {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    const color = result.passed ? 'green' : 'red';
    log(`  ${status}  ${result.name}`, color);
  }
  
  log('\n' + '='.repeat(50), 'cyan');
  log(`Results: ${passed}/${total} tests passed`, passed === total ? 'green' : 'yellow');
  
  if (passed === total) {
    log('\n🎉 All troubleshooting tools tests passed!\n', 'green');
  } else {
    log('\n⚠️ Some tests failed. Check the output above.\n', 'yellow');
  }
  
  return passed === total;
}

// Run tests
testTroubleshootingTools()
  .then(success => process.exit(success ? 0 : 1))
  .catch(error => {
    log(`\n❌ Test error: ${error.message}`, 'red');
    process.exit(1);
  });
