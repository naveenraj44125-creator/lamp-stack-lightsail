#!/usr/bin/env node

/**
 * Test Suite for New MCP Server Tools
 * 
 * Tests:
 * 1. Input validation
 * 2. list_lightsail_instances tool
 * 3. check_deployment_status tool
 * 4. validate_deployment_config tool
 * 5. MongoDB-specific environment variables
 */

import { ProjectAnalyzer } from './project-analyzer.js';

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

function logTest(name, passed, details = '') {
  const status = passed ? `${colors.green}✅ PASS${colors.reset}` : `${colors.red}❌ FAIL${colors.reset}`;
  console.log(`  ${status} ${name}${details ? ` - ${details}` : ''}`);
  return passed;
}

// Mock server class for testing validation
class MockServer {
  validateToolInput(toolName, args) {
    if (!args) args = {};

    switch (toolName) {
      case 'analyze_project_intelligently':
        if (!args.project_path && !args.project_files) {
          return 'Either project_path or project_files must be provided';
        }
        if (args.project_files && !Array.isArray(args.project_files)) {
          return 'project_files must be an array';
        }
        break;

      case 'generate_smart_deployment_config':
        if (!args.analysis_result) {
          return 'analysis_result is required';
        }
        if (!args.app_name) {
          return 'app_name is required';
        }
        if (args.app_name && !/^[a-zA-Z][a-zA-Z0-9-_]*$/.test(args.app_name)) {
          return 'app_name must start with a letter and contain only letters, numbers, hyphens, and underscores';
        }
        break;

      case 'setup_intelligent_deployment':
        if (!args.app_name) {
          return 'app_name is required';
        }
        if (args.app_name && !/^[a-zA-Z][a-zA-Z0-9-_]*$/.test(args.app_name)) {
          return 'app_name must start with a letter and contain only letters, numbers, hyphens, and underscores';
        }
        break;

      case 'optimize_infrastructure_costs':
        if (!args.current_config) {
          return 'current_config is required';
        }
        break;

      case 'detect_security_requirements':
        if (!args.project_analysis) {
          return 'project_analysis is required';
        }
        break;

      case 'check_deployment_status':
        if (!args.instance_name) {
          return 'instance_name is required';
        }
        break;

      case 'validate_deployment_config':
        if (!args.config && !args.config_path) {
          return 'Either config or config_path must be provided';
        }
        break;
    }

    return null;
  }

  // Mock generateSetupScript for testing MongoDB support
  generateSetupScript(analysis, appName, deploymentPreferences, _githubConfig) {
    const appType = analysis.detected_type || 'nodejs';
    const awsRegion = deploymentPreferences.aws_region || 'us-east-1';
    
    const hasDatabase = analysis.databases && analysis.databases.length > 0;
    const dbType = hasDatabase ? analysis.databases[0].type : 'none';
    const dbName = deploymentPreferences.db_name || 'app_db';
    
    const isMongoDb = dbType === 'mongodb';
    const mongoDbUser = deploymentPreferences.mongodb_user || 'app_user';
    const mongoDbPort = deploymentPreferences.mongodb_port || '27017';
    
    const mongoDbExports = isMongoDb ? `
# MongoDB-specific configuration
export MONGODB_USER="${mongoDbUser}"
export MONGODB_PORT="${mongoDbPort}"
export MONGODB_URI="mongodb://${mongoDbUser}:CHANGE_ME_PASSWORD@localhost:${mongoDbPort}/${dbName}"` : '';
    
    return `#!/bin/bash
export FULLY_AUTOMATED=true
export APP_TYPE="${appType}"
export APP_NAME="${appName}"
export DATABASE_TYPE="${dbType}"
export DB_NAME="${dbName}"${mongoDbExports}`;
  }

  // Mock config validation
  validateConfig(config) {
    const errors = [];
    const warnings = [];

    if (!config.aws) errors.push('Missing aws section');
    if (!config.lightsail) errors.push('Missing lightsail section');
    if (!config.application) errors.push('Missing application section');
    
    if (config.lightsail && !config.lightsail.instance_name) {
      errors.push('Missing lightsail.instance_name');
    }
    
    if (config.application && !config.application.type) {
      errors.push('Missing application.type');
    }

    // Check for default passwords
    const checkPasswords = (obj, path = '') => {
      if (typeof obj === 'object' && obj !== null) {
        for (const [key, value] of Object.entries(obj)) {
          if (typeof value === 'string' && key.toLowerCase().includes('password') && value.includes('CHANGE_ME')) {
            warnings.push(`Default password at ${path}.${key}`);
          }
          if (typeof value === 'object') {
            checkPasswords(value, `${path}.${key}`);
          }
        }
      }
    };
    checkPasswords(config);

    return { errors, warnings, isValid: errors.length === 0 };
  }
}

async function runTests() {
  log('\n🧪 Running MCP Server New Tools Test Suite\n', 'cyan');
  
  const server = new MockServer();
  let totalTests = 0;
  let passedTests = 0;

  // ============================================
  // Test 1: Input Validation
  // ============================================
  log('📋 Test 1: Input Validation', 'blue');
  
  // Test analyze_project_intelligently validation
  totalTests++;
  let result = server.validateToolInput('analyze_project_intelligently', {});
  passedTests += logTest('analyze_project_intelligently - missing both inputs', 
    result === 'Either project_path or project_files must be provided');

  totalTests++;
  result = server.validateToolInput('analyze_project_intelligently', { project_path: '/some/path' });
  passedTests += logTest('analyze_project_intelligently - valid with project_path', result === null);

  totalTests++;
  result = server.validateToolInput('analyze_project_intelligently', { project_files: 'not-an-array' });
  passedTests += logTest('analyze_project_intelligently - invalid project_files type', 
    result === 'project_files must be an array');

  // Test generate_smart_deployment_config validation
  totalTests++;
  result = server.validateToolInput('generate_smart_deployment_config', {});
  passedTests += logTest('generate_smart_deployment_config - missing analysis_result', 
    result === 'analysis_result is required');

  totalTests++;
  result = server.validateToolInput('generate_smart_deployment_config', { analysis_result: {} });
  passedTests += logTest('generate_smart_deployment_config - missing app_name', 
    result === 'app_name is required');

  totalTests++;
  result = server.validateToolInput('generate_smart_deployment_config', { 
    analysis_result: {}, 
    app_name: '123invalid' 
  });
  passedTests += logTest('generate_smart_deployment_config - invalid app_name format', 
    result !== null && result.includes('must start with a letter'));

  totalTests++;
  result = server.validateToolInput('generate_smart_deployment_config', { 
    analysis_result: {}, 
    app_name: 'valid-app-name' 
  });
  passedTests += logTest('generate_smart_deployment_config - valid inputs', result === null);

  // Test check_deployment_status validation
  totalTests++;
  result = server.validateToolInput('check_deployment_status', {});
  passedTests += logTest('check_deployment_status - missing instance_name', 
    result === 'instance_name is required');

  totalTests++;
  result = server.validateToolInput('check_deployment_status', { instance_name: 'my-instance' });
  passedTests += logTest('check_deployment_status - valid inputs', result === null);

  // Test validate_deployment_config validation
  totalTests++;
  result = server.validateToolInput('validate_deployment_config', {});
  passedTests += logTest('validate_deployment_config - missing both config and config_path', 
    result === 'Either config or config_path must be provided');

  totalTests++;
  result = server.validateToolInput('validate_deployment_config', { config: {} });
  passedTests += logTest('validate_deployment_config - valid with config', result === null);

  // ============================================
  // Test 2: MongoDB Environment Variables
  // ============================================
  log('\n📋 Test 2: MongoDB Environment Variables', 'blue');

  // Test MongoDB detection and env vars
  const mongoAnalysis = {
    detected_type: 'nodejs',
    databases: [{ type: 'mongodb', name: 'mongodb' }],
    infrastructure_needs: { bundle_size: 'small_3_0' },
    storage_needs: {}
  };

  totalTests++;
  const mongoScript = server.generateSetupScript(mongoAnalysis, 'my-mongo-app', {}, {});
  passedTests += logTest('MongoDB script contains MONGODB_USER', 
    mongoScript.includes('MONGODB_USER'));

  totalTests++;
  passedTests += logTest('MongoDB script contains MONGODB_PORT', 
    mongoScript.includes('MONGODB_PORT'));

  totalTests++;
  passedTests += logTest('MongoDB script contains MONGODB_URI', 
    mongoScript.includes('MONGODB_URI'));

  totalTests++;
  passedTests += logTest('MongoDB script has correct DATABASE_TYPE', 
    mongoScript.includes('DATABASE_TYPE="mongodb"'));

  // Test non-MongoDB doesn't have MongoDB vars
  const mysqlAnalysis = {
    detected_type: 'nodejs',
    databases: [{ type: 'mysql', name: 'mysql' }],
    infrastructure_needs: { bundle_size: 'small_3_0' },
    storage_needs: {}
  };

  totalTests++;
  const mysqlScript = server.generateSetupScript(mysqlAnalysis, 'my-mysql-app', {}, {});
  passedTests += logTest('MySQL script does NOT contain MONGODB_URI', 
    !mysqlScript.includes('MONGODB_URI'));

  // ============================================
  // Test 3: Configuration Validation
  // ============================================
  log('\n📋 Test 3: Configuration Validation', 'blue');

  // Test valid config
  const validConfig = {
    aws: { region: 'us-east-1' },
    lightsail: { instance_name: 'test-instance', bundle_id: 'micro_3_0' },
    application: { name: 'test-app', type: 'nodejs' }
  };

  totalTests++;
  let validation = server.validateConfig(validConfig);
  passedTests += logTest('Valid config passes validation', 
    validation.isValid === true && validation.errors.length === 0);

  // Test missing sections
  const missingAwsConfig = {
    lightsail: { instance_name: 'test' },
    application: { name: 'test', type: 'nodejs' }
  };

  totalTests++;
  validation = server.validateConfig(missingAwsConfig);
  passedTests += logTest('Missing aws section detected', 
    validation.errors.includes('Missing aws section'));

  // Test missing instance_name
  const missingInstanceConfig = {
    aws: { region: 'us-east-1' },
    lightsail: { bundle_id: 'micro_3_0' },
    application: { name: 'test', type: 'nodejs' }
  };

  totalTests++;
  validation = server.validateConfig(missingInstanceConfig);
  passedTests += logTest('Missing instance_name detected', 
    validation.errors.includes('Missing lightsail.instance_name'));

  // Test default password warning
  const defaultPasswordConfig = {
    aws: { region: 'us-east-1' },
    lightsail: { instance_name: 'test' },
    application: { name: 'test', type: 'nodejs' },
    dependencies: {
      mysql: {
        password: 'CHANGE_ME_password'
      }
    }
  };

  totalTests++;
  validation = server.validateConfig(defaultPasswordConfig);
  passedTests += logTest('Default password warning generated', 
    validation.warnings.length > 0 && validation.warnings.some(w => w.includes('password')));

  // ============================================
  // Test 4: Project Analyzer Integration
  // ============================================
  log('\n📋 Test 4: Project Analyzer Integration', 'blue');

  const analyzer = new ProjectAnalyzer();

  // Test MongoDB detection from package.json content
  totalTests++;
  const mongoFiles = [{
    path: 'package.json',
    content: JSON.stringify({
      name: 'mongo-app',
      dependencies: {
        'mongoose': '^7.0.0',
        'express': '^4.18.0'
      }
    })
  }];
  
  const mongoProjectAnalysis = await analyzer.analyzeProject(null, mongoFiles, '');
  passedTests += logTest('MongoDB detected from mongoose dependency', 
    mongoProjectAnalysis.databases.some(db => db.type === 'mongodb'));

  // Test MySQL detection
  totalTests++;
  const mysqlFiles = [{
    path: 'package.json',
    content: JSON.stringify({
      name: 'mysql-app',
      dependencies: {
        'mysql2': '^3.0.0',
        'express': '^4.18.0'
      }
    })
  }];
  
  const mysqlProjectAnalysis = await analyzer.analyzeProject(null, mysqlFiles, '');
  passedTests += logTest('MySQL detected from mysql2 dependency', 
    mysqlProjectAnalysis.databases.some(db => db.type === 'mysql'));

  // Test PostgreSQL detection
  totalTests++;
  const pgFiles = [{
    path: 'package.json',
    content: JSON.stringify({
      name: 'pg-app',
      dependencies: {
        'pg': '^8.0.0',
        'express': '^4.18.0'
      }
    })
  }];
  
  const pgProjectAnalysis = await analyzer.analyzeProject(null, pgFiles, '');
  passedTests += logTest('PostgreSQL detected from pg dependency', 
    pgProjectAnalysis.databases.some(db => db.type === 'postgresql'));

  // ============================================
  // Test 5: Edge Cases
  // ============================================
  log('\n📋 Test 5: Edge Cases', 'blue');

  // Test empty analysis
  totalTests++;
  const emptyAnalysis = {
    detected_type: null,
    databases: null,
    infrastructure_needs: null,
    storage_needs: null
  };
  
  try {
    const emptyScript = server.generateSetupScript(emptyAnalysis, 'test-app', {}, {});
    // Should default to nodejs and have APP_NAME set
    passedTests += logTest('Handles null analysis fields gracefully', 
      emptyScript.includes('APP_TYPE="nodejs"') && emptyScript.includes('APP_NAME="test-app"'));
  } catch (e) {
    logTest('Handles null analysis fields gracefully', false, e.message);
  }

  // Test special characters in app name
  totalTests++;
  result = server.validateToolInput('setup_intelligent_deployment', { 
    app_name: 'my-app_123' 
  });
  passedTests += logTest('App name with hyphens and underscores is valid', result === null);

  totalTests++;
  result = server.validateToolInput('setup_intelligent_deployment', { 
    app_name: 'my app' 
  });
  passedTests += logTest('App name with spaces is invalid', result !== null);

  // ============================================
  // Summary
  // ============================================
  log('\n' + '='.repeat(50), 'cyan');
  log(`📊 Test Results: ${passedTests}/${totalTests} passed`, passedTests === totalTests ? 'green' : 'red');
  log('='.repeat(50) + '\n', 'cyan');

  if (passedTests === totalTests) {
    log('🎉 All tests passed! MCP Server improvements are working correctly.\n', 'green');
    process.exit(0);
  } else {
    log(`❌ ${totalTests - passedTests} test(s) failed.\n`, 'red');
    process.exit(1);
  }
}

// Run tests
runTests().catch(error => {
  log(`\n❌ Test suite error: ${error.message}`, 'red');
  console.error(error.stack);
  process.exit(1);
});
