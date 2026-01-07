/**
 * Infrastructure Optimizer
 * 
 * Optimizes infrastructure configurations based on:
 * - Application requirements
 * - Budget constraints
 * - Performance needs
 * - Cost efficiency
 */

export class InfrastructureOptimizer {
  constructor() {
    this.bundleSpecs = {
      'nano_3_0': { vcpu: 1, ram: 0.5, storage: 20, cost: 3.5 },
      'micro_3_0': { vcpu: 1, ram: 1, storage: 40, cost: 5 },
      'small_3_0': { vcpu: 1, ram: 2, storage: 60, cost: 10 },
      'medium_3_0': { vcpu: 2, ram: 4, storage: 80, cost: 20 },
      'large_3_0': { vcpu: 2, ram: 8, storage: 160, cost: 40 },
      'xlarge_3_0': { vcpu: 4, ram: 16, storage: 320, cost: 80 }
    };
    
    this.databaseCosts = {
      'mysql': { small: 15, medium: 30, large: 60 },
      'postgresql': { small: 15, medium: 30, large: 60 }
    };
    
    this.bucketCosts = {
      'small_1_0': 1,
      'medium_1_0': 5,
      'large_1_0': 10
    };
  }

  optimizeInfrastructure(analysis, preferences = {}) {
    const {
      budget = 'standard',
      scale = 'small',
      environment = 'production',
      priority = 'balanced' // cost, performance, balanced
    } = preferences;

    let optimization = {
      recommended_bundle: 'micro_3_0',
      database_config: null,
      bucket_config: null,
      optimizations: [],
      cost_breakdown: {
        instance: 0,
        database: 0,
        storage: 0,
        total: 0
      },
      performance_score: 0,
      cost_efficiency_score: 0
    };

    // Optimize instance size
    optimization.recommended_bundle = this.optimizeInstanceSize(analysis, scale, priority);
    
    // Optimize database configuration
    if (analysis.databases && analysis.databases.length > 0) {
      optimization.database_config = this.optimizeDatabaseConfig(analysis, scale, priority);
    }
    
    // Optimize storage configuration
    if (analysis.storage_needs && analysis.storage_needs.needs_bucket) {
      optimization.bucket_config = this.optimizeBucketConfig(analysis, scale);
    }
    
    // Calculate costs
    this.calculateOptimizedCosts(optimization);
    
    // Generate optimization recommendations
    this.generateOptimizationRecommendations(optimization, analysis, preferences);
    
    // Calculate scores
    this.calculatePerformanceScore(optimization, analysis);
    this.calculateCostEfficiencyScore(optimization, analysis);
    
    return optimization;
  }

  optimizeInstanceSize(analysis, scale, priority) {
    let baseBundle = 'micro_3_0';
    
    // Application type requirements
    const typeRequirements = {
      'docker': 'medium_3_0', // Docker needs more resources
      'nodejs': 'micro_3_0',
      'python': 'micro_3_0',
      'lamp': 'micro_3_0',
      'react': 'nano_3_0', // Static builds need less
      'nginx': 'nano_3_0'
    };
    
    if (analysis.detected_type && typeRequirements[analysis.detected_type]) {
      baseBundle = typeRequirements[analysis.detected_type];
    }
    
    // Scale adjustments
    const scaleAdjustments = {
      'small': 0,
      'medium': 1,
      'large': 2
    };
    
    const bundles = Object.keys(this.bundleSpecs);
    let currentIndex = bundles.indexOf(baseBundle);
    currentIndex = Math.min(currentIndex + (scaleAdjustments[scale] || 0), bundles.length - 1);
    
    // Performance requirements adjustments
    if (analysis.infrastructure_needs) {
      if (analysis.infrastructure_needs.memory_intensive) {
        currentIndex = Math.min(currentIndex + 1, bundles.length - 1);
      }
      if (analysis.infrastructure_needs.cpu_intensive) {
        currentIndex = Math.min(currentIndex + 1, bundles.length - 1);
      }
    }
    
    // Priority adjustments
    if (priority === 'cost' && currentIndex > 0) {
      currentIndex = Math.max(currentIndex - 1, 0);
    } else if (priority === 'performance') {
      currentIndex = Math.min(currentIndex + 1, bundles.length - 1);
    }
    
    return bundles[currentIndex];
  }

  optimizeDatabaseConfig(analysis, scale, priority) {
    const primaryDb = analysis.databases[0];
    if (!primaryDb) return null;
    
    let dbSize = 'small';
    if (scale === 'medium') dbSize = 'medium';
    else if (scale === 'large') dbSize = 'large';
    
    // Adjust based on priority
    if (priority === 'cost' && dbSize !== 'small') {
      dbSize = 'small';
    } else if (priority === 'performance' && dbSize === 'small') {
      dbSize = 'medium';
    }
    
    return {
      type: primaryDb.type,
      size: dbSize,
      external: scale !== 'small', // Use RDS for medium/large
      backup_enabled: true,
      multi_az: scale === 'large'
    };
  }

  optimizeBucketConfig(analysis, scale) {
    let bucketSize = 'small_1_0';
    
    if (analysis.storage_needs.image_processing || scale === 'medium') {
      bucketSize = 'medium_1_0';
    } else if (scale === 'large') {
      bucketSize = 'large_1_0';
    }
    
    return {
      bundle_id: bucketSize,
      access_level: 'read_write',
      versioning: scale !== 'small',
      lifecycle_rules: true
    };
  }

  calculateOptimizedCosts(optimization) {
    // Instance cost
    const bundleSpec = this.bundleSpecs[optimization.recommended_bundle];
    optimization.cost_breakdown.instance = bundleSpec.cost;
    
    // Database cost
    if (optimization.database_config) {
      const dbCost = this.databaseCosts[optimization.database_config.type];
      if (dbCost) {
        optimization.cost_breakdown.database = dbCost[optimization.database_config.size] || 0;
      } else {
        // MongoDB and other NoSQL databases run on the instance (no separate cost)
        optimization.cost_breakdown.database = 0;
      }
    }
    
    // Storage cost
    if (optimization.bucket_config) {
      optimization.cost_breakdown.storage = this.bucketCosts[optimization.bucket_config.bundle_id];
    }
    
    // Total cost
    optimization.cost_breakdown.total = 
      optimization.cost_breakdown.instance + 
      optimization.cost_breakdown.database + 
      optimization.cost_breakdown.storage;
  }

  generateOptimizationRecommendations(optimization, analysis, preferences) {
    const recommendations = [];
    
    // Instance optimization recommendations
    const bundleSpec = this.bundleSpecs[optimization.recommended_bundle];
    if (bundleSpec.ram < 2 && analysis.infrastructure_needs?.memory_intensive) {
      recommendations.push({
        type: 'performance',
        priority: 'medium',
        message: 'Consider upgrading to a larger instance for memory-intensive operations',
        impact: 'May improve application performance significantly'
      });
    }
    
    // Database recommendations
    if (analysis.databases?.length > 0 && !optimization.database_config?.external) {
      recommendations.push({
        type: 'reliability',
        priority: 'medium',
        message: 'Consider using external RDS database for production workloads',
        impact: 'Improves reliability, backup, and maintenance'
      });
    }
    
    // Security recommendations
    if (analysis.security_considerations?.handles_user_data) {
      recommendations.push({
        type: 'security',
        priority: 'high',
        message: 'Enable SSL/TLS and implement proper authentication',
        impact: 'Essential for protecting user data'
      });
    }
    
    // Cost optimization recommendations
    if (optimization.cost_breakdown.total > 50) {
      recommendations.push({
        type: 'cost',
        priority: 'low',
        message: 'Consider using reserved instances for long-term deployments',
        impact: 'Can reduce costs by up to 30%'
      });
    }
    
    optimization.optimizations = recommendations;
  }

  calculatePerformanceScore(optimization, analysis) {
    let score = 50; // Base score
    
    const bundleSpec = this.bundleSpecs[optimization.recommended_bundle];
    
    // RAM adequacy
    const ramNeeds = this.estimateRamNeeds(analysis);
    if (bundleSpec.ram >= ramNeeds) score += 20;
    else if (bundleSpec.ram >= ramNeeds * 0.7) score += 10;
    
    // CPU adequacy
    const cpuNeeds = this.estimateCpuNeeds(analysis);
    if (bundleSpec.vcpu >= cpuNeeds) score += 15;
    else if (bundleSpec.vcpu >= cpuNeeds * 0.7) score += 7;
    
    // Database performance
    if (optimization.database_config?.external) score += 10;
    if (optimization.database_config?.multi_az) score += 5;
    
    optimization.performance_score = Math.min(score, 100);
  }

  calculateCostEfficiencyScore(optimization, analysis) {
    let score = 50; // Base score
    
    const totalCost = optimization.cost_breakdown.total;
    
    // Cost vs performance ratio
    if (totalCost < 20) score += 30;
    else if (totalCost < 50) score += 20;
    else if (totalCost < 100) score += 10;
    
    // Right-sizing bonus
    const bundleSpec = this.bundleSpecs[optimization.recommended_bundle];
    const estimatedRam = this.estimateRamNeeds(analysis);
    
    if (bundleSpec.ram >= estimatedRam && bundleSpec.ram <= estimatedRam * 1.5) {
      score += 20; // Well-sized
    }
    
    optimization.cost_efficiency_score = Math.min(score, 100);
  }

  estimateRamNeeds(analysis) {
    let baseRam = 0.5; // GB
    
    const typeRam = {
      'docker': 2,
      'nodejs': 1,
      'python': 1,
      'lamp': 0.5,
      'react': 0.25,
      'nginx': 0.25
    };
    
    if (analysis.detected_type && typeRam[analysis.detected_type]) {
      baseRam = typeRam[analysis.detected_type];
    }
    
    // Add for databases
    if (analysis.databases?.length > 0) {
      baseRam += 0.5;
    }
    
    // Add for memory-intensive operations
    if (analysis.infrastructure_needs?.memory_intensive) {
      baseRam *= 2;
    }
    
    return baseRam;
  }

  estimateCpuNeeds(analysis) {
    let baseCpu = 1;
    
    // CPU-intensive operations
    if (analysis.infrastructure_needs?.cpu_intensive) {
      baseCpu = 2;
    }
    
    // Docker typically needs more CPU
    if (analysis.detected_type === 'docker') {
      baseCpu = Math.max(baseCpu, 2);
    }
    
    return baseCpu;
  }
}