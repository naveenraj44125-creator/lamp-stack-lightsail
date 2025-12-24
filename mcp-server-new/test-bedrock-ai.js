#!/usr/bin/env node

/**
 * Test Suite for AWS Bedrock AI Integration
 * 
 * Tests the AI-powered tools using AWS Bedrock
 * Requires AWS credentials configured with Bedrock access
 */

import { BedrockAI } from './bedrock-ai.js';

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

async function runTests() {
  log('\n🤖 Testing AWS Bedrock AI Integration\n', 'cyan');
  
  const ai = new BedrockAI({
    region: process.env.AWS_REGION || 'us-east-1'
  });

  let passed = 0;
  let failed = 0;

  // Test 1: Basic chat
  log('📋 Test 1: Basic AI Chat', 'blue');
  try {
    const result = await ai.chat('What is AWS Lightsail in one sentence?');
    if (result.success) {
      log(`  ✅ PASS - Got response (${result.usage?.outputTokens || '?'} tokens)`, 'green');
      log(`  Response: ${result.content.substring(0, 100)}...`, 'yellow');
      passed++;
    } else {
      log(`  ❌ FAIL - ${result.error}`, 'red');
      failed++;
    }
  } catch (e) {
    log(`  ❌ FAIL - ${e.message}`, 'red');
    failed++;
  }

  // Test 2: Project Analysis
  log('\n📋 Test 2: AI Project Analysis', 'blue');
  try {
    const projectFiles = [
      {
        path: 'package.json',
        content: JSON.stringify({
          name: 'test-api',
          dependencies: {
            'express': '^4.18.0',
            'mongoose': '^7.0.0',
            'jsonwebtoken': '^9.0.0'
          },
          scripts: {
            start: 'node server.js'
          }
        })
      },
      {
        path: 'server.js',
        content: `
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));
app.listen(3000);
        `
      }
    ];

    const result = await ai.analyzeProject(projectFiles, 'A Node.js API with MongoDB');
    if (result.success) {
      log(`  ✅ PASS - Analysis completed`, 'green');
      if (result.analysis) {
        log(`  Detected: ${result.analysis.detected_type} (${Math.round((result.analysis.confidence || 0) * 100)}% confidence)`, 'yellow');
        log(`  Databases: ${result.analysis.databases?.map(d => d.type).join(', ') || 'none'}`, 'yellow');
      }
      passed++;
    } else {
      log(`  ❌ FAIL - ${result.error}`, 'red');
      failed++;
    }
  } catch (e) {
    log(`  ❌ FAIL - ${e.message}`, 'red');
    failed++;
  }

  // Test 3: Troubleshooting
  log('\n📋 Test 3: AI Troubleshooting', 'blue');
  try {
    const result = await ai.troubleshoot(
      'Error: ECONNREFUSED 127.0.0.1:27017',
      { app_type: 'nodejs', instance_name: 'my-app' }
    );
    if (result.success) {
      log(`  ✅ PASS - Got troubleshooting advice`, 'green');
      log(`  Response preview: ${result.content.substring(0, 100)}...`, 'yellow');
      passed++;
    } else {
      log(`  ❌ FAIL - ${result.error}`, 'red');
      failed++;
    }
  } catch (e) {
    log(`  ❌ FAIL - ${e.message}`, 'red');
    failed++;
  }

  // Test 4: Ask Expert
  log('\n📋 Test 4: AI Expert Q&A', 'blue');
  try {
    const result = await ai.askExpert('What instance size should I use for a small Node.js API?');
    if (result.success) {
      log(`  ✅ PASS - Got expert answer`, 'green');
      log(`  Response preview: ${result.content.substring(0, 100)}...`, 'yellow');
      passed++;
    } else {
      log(`  ❌ FAIL - ${result.error}`, 'red');
      failed++;
    }
  } catch (e) {
    log(`  ❌ FAIL - ${e.message}`, 'red');
    failed++;
  }

  // Test 5: Quick Analysis (Haiku)
  log('\n📋 Test 5: Quick Analysis (Haiku model)', 'blue');
  try {
    const result = await ai.quickAnalysis('Is MySQL or PostgreSQL better for a small web app? Answer in 2 sentences.');
    if (result.success) {
      log(`  ✅ PASS - Got quick response`, 'green');
      log(`  Response: ${result.content}`, 'yellow');
      passed++;
    } else {
      log(`  ❌ FAIL - ${result.error}`, 'red');
      failed++;
    }
  } catch (e) {
    log(`  ❌ FAIL - ${e.message}`, 'red');
    failed++;
  }

  // Summary
  log('\n' + '='.repeat(50), 'cyan');
  log(`📊 Test Results: ${passed}/${passed + failed} passed`, passed === passed + failed ? 'green' : 'red');
  log('='.repeat(50) + '\n', 'cyan');

  if (failed === 0) {
    log('🎉 All Bedrock AI tests passed!\n', 'green');
  } else {
    log(`⚠️ ${failed} test(s) failed. Check AWS credentials and Bedrock access.\n`, 'yellow');
    log('To fix:', 'yellow');
    log('1. Run: aws configure', 'yellow');
    log('2. Ensure Bedrock model access is enabled in AWS Console', 'yellow');
    log('3. Check IAM permissions include bedrock:InvokeModel', 'yellow');
  }

  process.exit(failed > 0 ? 1 : 0);
}

// Check for --skip-ai flag
if (process.argv.includes('--skip-ai')) {
  log('⏭️ Skipping AI tests (--skip-ai flag provided)\n', 'yellow');
  process.exit(0);
}

runTests().catch(error => {
  log(`\n❌ Test suite error: ${error.message}`, 'red');
  console.error(error.stack);
  process.exit(1);
});
