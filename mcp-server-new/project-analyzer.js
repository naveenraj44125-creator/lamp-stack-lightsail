/**
 * Intelligent Project Analyzer
 * 
 * Analyzes project structure, dependencies, and code to determine:
 * - Application type and framework
 * - Database requirements
 * - Storage needs
 * - Infrastructure requirements
 * - Security considerations
 */

import fs from 'fs';
import path from 'path';

export class ProjectAnalyzer {
  constructor() {
    this.patterns = {
      // Framework detection patterns
      frameworks: {
        'express': { files: ['package.json'], content: ['"express"'], type: 'nodejs' },
        'fastify': { files: ['package.json'], content: ['"fastify"'], type: 'nodejs' },
        'koa': { files: ['package.json'], content: ['"koa"'], type: 'nodejs' },
        'flask': { files: ['requirements.txt', 'app.py'], content: ['Flask', 'from flask'], type: 'python' },
        'django': { files: ['requirements.txt', 'manage.py'], content: ['Django', 'django'], type: 'python' },
        'laravel': { files: ['composer.json'], content: ['laravel/framework'], type: 'lamp' },
        'symfony': { files: ['composer.json'], content: ['symfony/'], type: 'lamp' },
        'react': { files: ['package.json'], content: ['"react"'], type: 'react' },
        'vue': { files: ['package.json'], content: ['"vue"'], type: 'react' },
        'angular': { files: ['package.json'], content: ['"@angular/'], type: 'react' },
        'next': { files: ['package.json'], content: ['"next"'], type: 'react' },
        'nuxt': { files: ['package.json'], content: ['"nuxt"'], type: 'react' }
      },
      
      // Database detection patterns
      databases: {
        'mysql': { 
          files: ['package.json', 'requirements.txt', 'composer.json'], 
          content: ['mysql', 'mysql2', 'PyMySQL', 'mysqlclient', 'doctrine/dbal'],
          type: 'mysql'
        },
        'postgresql': { 
          files: ['package.json', 'requirements.txt', 'composer.json'], 
          content: ['pg', 'postgres', 'psycopg2', 'postgresql'],
          type: 'postgresql'
        },
        'mongodb': { 
          files: ['package.json', 'requirements.txt'], 
          content: ['mongodb', 'mongoose', 'pymongo'],
          type: 'mongodb'
        },
        'redis': { 
          files: ['package.json', 'requirements.txt'], 
          content: ['redis', 'ioredis'],
          type: 'redis'
        }
      },
      
      // File upload/storage patterns
      storage: {
        'file_uploads': {
          files: ['*.js', '*.py', '*.php'],
          content: ['multer', 'upload', 'FileField', 'move_uploaded_file', 'FormData'],
          needs_bucket: true
        },
        'image_processing': {
          files: ['package.json', 'requirements.txt'],
          content: ['sharp', 'jimp', 'Pillow', 'PIL', 'imagemagick'],
          needs_bucket: true
        }
      },
      
      // Docker detection
      docker: {
        files: ['Dockerfile', 'docker-compose.yml', '.dockerignore'],
        type: 'docker'
      }
    };
  }

  async analyzeProject(projectPath, projectFiles = null, userDescription = '') {
    let analysis = {
      detected_type: 'unknown',
      confidence: 0,
      frameworks: [],
      databases: [],
      storage_needs: {
        file_uploads: false,
        image_processing: false,
        needs_bucket: false
      },
      infrastructure_needs: {
        bundle_size: 'micro_3_0',
        memory_intensive: false,
        cpu_intensive: false,
        network_intensive: false
      },
      security_considerations: {
        handles_user_data: false,
        needs_ssl: true,
        needs_auth: false,
        file_uploads: false
      },
      deployment_complexity: 'simple', // simple, moderate, complex
      estimated_costs: {
        monthly_min: 5,
        monthly_max: 20
      }
    };

    try {
      // Use provided files or scan directory
      const files = projectFiles || await this.scanProjectDirectory(projectPath);
      
      // Analyze each file
      for (const file of files) {
        await this.analyzeFile(file, analysis);
      }
      
      // Enhance analysis with user description
      if (userDescription) {
        this.enhanceWithUserDescription(analysis, userDescription);
      }
      
      // Determine final application type and confidence
      this.determineApplicationType(analysis);
      
      // Calculate infrastructure requirements
      this.calculateInfrastructureNeeds(analysis);
      
      // Assess security requirements
      this.assessSecurityRequirements(analysis);
      
      // Estimate costs
      this.estimateCosts(analysis);
      
      return analysis;
      
    } catch (error) {
      console.error('Project analysis error:', error);
      return {
        ...analysis,
        error: error.message,
        detected_type: 'unknown',
        confidence: 0
      };
    }
  }

  async scanProjectDirectory(projectPath) {
    const files = [];
    
    if (!fs.existsSync(projectPath)) {
      throw new Error(`Project path does not exist: ${projectPath}`);
    }
    
    const scanDir = (dir, maxDepth = 3, currentDepth = 0) => {
      if (currentDepth >= maxDepth) return;
      
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        // Skip common directories that don't need analysis
        if (['node_modules', '.git', 'vendor', '__pycache__', '.venv', 'venv'].includes(item)) {
          continue;
        }
        
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          scanDir(fullPath, maxDepth, currentDepth + 1);
        } else if (this.shouldAnalyzeFile(item)) {
          try {
            const content = fs.readFileSync(fullPath, 'utf8').substring(0, 2000); // First 2000 chars
            files.push({
              path: path.relative(projectPath, fullPath),
              content: content
            });
          } catch (err) {
            // Skip files that can't be read
            console.warn(`Could not read file: ${fullPath}`);
          }
        }
      }
    };
    
    scanDir(projectPath);
    return files;
  }

  shouldAnalyzeFile(filename) {
    const importantFiles = [
      'package.json', 'requirements.txt', 'composer.json', 'Gemfile',
      'Dockerfile', 'docker-compose.yml', '.dockerignore',
      'app.js', 'server.js', 'index.js', 'main.js',
      'app.py', 'main.py', 'wsgi.py', 'manage.py',
      'index.php', 'app.php', 'config.php',
      'pom.xml', 'build.gradle', 'Cargo.toml',
      'README.md', 'README.txt'
    ];
    
    const extensions = ['.js', '.py', '.php', '.json', '.yml', '.yaml', '.md', '.txt'];
    
    return importantFiles.includes(filename) || 
           extensions.some(ext => filename.endsWith(ext));
  }
  async analyzeFile(file, analysis) {
    const { path: filePath, content } = file;
    const filename = path.basename(filePath);
    
    // Framework detection
    for (const [framework, pattern] of Object.entries(this.patterns.frameworks)) {
      if (pattern.files.some(f => f === filename || filePath.includes(f))) {
        if (pattern.content.some(c => content.includes(c))) {
          analysis.frameworks.push({
            name: framework,
            type: pattern.type,
            confidence: 0.8
          });
        }
      }
    }
    
    // Database detection
    for (const [db, pattern] of Object.entries(this.patterns.databases)) {
      if (pattern.files.some(f => f === filename || filePath.includes(f))) {
        if (pattern.content.some(c => content.toLowerCase().includes(c.toLowerCase()))) {
          analysis.databases.push({
            name: db,
            type: pattern.type,
            confidence: 0.7
          });
        }
      }
    }
    
    // Storage needs detection
    for (const [feature, pattern] of Object.entries(this.patterns.storage)) {
      if (pattern.content.some(c => content.toLowerCase().includes(c.toLowerCase()))) {
        analysis.storage_needs[feature] = true;
        if (pattern.needs_bucket) {
          analysis.storage_needs.needs_bucket = true;
        }
      }
    }
    
    // Docker detection
    if (this.patterns.docker.files.includes(filename)) {
      analysis.frameworks.push({
        name: 'docker',
        type: 'docker',
        confidence: 0.9
      });
    }
    
    // Security considerations
    this.analyzeSecurityPatterns(content, analysis);
    
    // Performance patterns
    this.analyzePerformancePatterns(content, analysis);
  }

  analyzeSecurityPatterns(content, analysis) {
    const securityPatterns = {
      auth: ['passport', 'jwt', 'session', 'login', 'authentication', 'auth'],
      user_data: ['user', 'profile', 'account', 'personal', 'email', 'password'],
      file_uploads: ['upload', 'file', 'multipart', 'FormData'],
      database: ['INSERT', 'UPDATE', 'DELETE', 'SELECT', 'query']
    };
    
    const lowerContent = content.toLowerCase();
    
    if (securityPatterns.auth.some(p => lowerContent.includes(p))) {
      analysis.security_considerations.needs_auth = true;
    }
    
    if (securityPatterns.user_data.some(p => lowerContent.includes(p))) {
      analysis.security_considerations.handles_user_data = true;
    }
    
    if (securityPatterns.file_uploads.some(p => lowerContent.includes(p))) {
      analysis.security_considerations.file_uploads = true;
    }
  }

  analyzePerformancePatterns(content, analysis) {
    const performancePatterns = {
      memory_intensive: ['image', 'video', 'large', 'buffer', 'stream', 'cache'],
      cpu_intensive: ['crypto', 'hash', 'compress', 'resize', 'process', 'compute'],
      network_intensive: ['api', 'request', 'fetch', 'http', 'websocket', 'socket']
    };
    
    const lowerContent = content.toLowerCase();
    
    for (const [type, patterns] of Object.entries(performancePatterns)) {
      if (patterns.some(p => lowerContent.includes(p))) {
        analysis.infrastructure_needs[type] = true;
      }
    }
  }

  enhanceWithUserDescription(analysis, userDescription) {
    const description = userDescription.toLowerCase();
    
    // Extract application type hints
    const typeHints = {
      'api': 'nodejs',
      'rest': 'nodejs',
      'backend': 'nodejs',
      'web app': 'nodejs',
      'website': 'nginx',
      'static': 'nginx',
      'blog': 'lamp',
      'cms': 'lamp',
      'dashboard': 'react',
      'admin': 'react',
      'spa': 'react',
      'microservice': 'docker',
      'container': 'docker'
    };
    
    for (const [hint, type] of Object.entries(typeHints)) {
      if (description.includes(hint)) {
        analysis.frameworks.push({
          name: hint,
          type: type,
          confidence: 0.6,
          source: 'user_description'
        });
      }
    }
    
    // Extract scale hints
    const scaleHints = {
      'small': 'micro_3_0',
      'simple': 'micro_3_0',
      'medium': 'small_3_0',
      'large': 'medium_3_0',
      'enterprise': 'large_3_0',
      'high traffic': 'medium_3_0',
      'production': 'small_3_0'
    };
    
    for (const [hint, bundle] of Object.entries(scaleHints)) {
      if (description.includes(hint)) {
        analysis.infrastructure_needs.bundle_size = bundle;
        break;
      }
    }
    
    // Extract database hints
    if (description.includes('database') || description.includes('data')) {
      if (!analysis.databases.length) {
        analysis.databases.push({
          name: 'mysql',
          type: 'mysql',
          confidence: 0.5,
          source: 'user_description'
        });
      }
    }
  }

  determineApplicationType(analysis) {
    const typeScores = {};
    
    // Score based on detected frameworks
    for (const framework of analysis.frameworks) {
      const type = framework.type;
      if (!typeScores[type]) typeScores[type] = 0;
      typeScores[type] += framework.confidence;
    }
    
    // Find highest scoring type
    let maxScore = 0;
    let detectedType = 'unknown';
    
    for (const [type, score] of Object.entries(typeScores)) {
      if (score > maxScore) {
        maxScore = score;
        detectedType = type;
      }
    }
    
    analysis.detected_type = detectedType;
    analysis.confidence = Math.min(maxScore, 1.0);
    
    // If confidence is low, make educated guesses
    if (analysis.confidence < 0.5) {
      if (analysis.frameworks.some(f => f.name === 'docker')) {
        analysis.detected_type = 'docker';
        analysis.confidence = 0.7;
      } else if (analysis.databases.length > 0) {
        analysis.detected_type = 'lamp'; // Default for database apps
        analysis.confidence = 0.6;
      }
    }
  }

  calculateInfrastructureNeeds(analysis) {
    let recommendedBundle = 'micro_3_0';
    
    // Upgrade based on detected patterns
    if (analysis.detected_type === 'docker') {
      recommendedBundle = 'medium_3_0'; // Docker needs more resources
    } else if (analysis.infrastructure_needs.memory_intensive) {
      recommendedBundle = 'small_3_0';
    } else if (analysis.infrastructure_needs.cpu_intensive) {
      recommendedBundle = 'small_3_0';
    } else if (analysis.databases.length > 1) {
      recommendedBundle = 'small_3_0'; // Multiple databases need more resources
    }
    
    analysis.infrastructure_needs.bundle_size = recommendedBundle;
    
    // Determine deployment complexity
    let complexity = 'simple';
    if (analysis.detected_type === 'docker') complexity = 'complex';
    else if (analysis.databases.length > 0 || analysis.storage_needs.needs_bucket) complexity = 'moderate';
    
    analysis.deployment_complexity = complexity;
  }

  assessSecurityRequirements(analysis) {
    // SSL is always recommended
    analysis.security_considerations.needs_ssl = true;
    
    // Additional security based on detected patterns
    if (analysis.security_considerations.handles_user_data) {
      analysis.security_considerations.needs_auth = true;
    }
    
    if (analysis.security_considerations.file_uploads) {
      analysis.storage_needs.needs_bucket = true;
    }
  }

  estimateCosts(analysis) {
    const bundleCosts = {
      'nano_3_0': { min: 3.5, max: 5 },
      'micro_3_0': { min: 5, max: 10 },
      'small_3_0': { min: 10, max: 20 },
      'medium_3_0': { min: 20, max: 40 },
      'large_3_0': { min: 40, max: 80 }
    };
    
    const baseCost = bundleCosts[analysis.infrastructure_needs.bundle_size] || bundleCosts['micro_3_0'];
    
    let minCost = baseCost.min;
    let maxCost = baseCost.max;
    
    // Add database costs
    if (analysis.databases.length > 0) {
      minCost += 15; // RDS minimum
      maxCost += 50;
    }
    
    // Add bucket costs
    if (analysis.storage_needs.needs_bucket) {
      minCost += 1;
      maxCost += 10;
    }
    
    analysis.estimated_costs = {
      monthly_min: Math.round(minCost),
      monthly_max: Math.round(maxCost)
    };
  }
}