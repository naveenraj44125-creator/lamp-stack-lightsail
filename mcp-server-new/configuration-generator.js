/**
 * Configuration Generator
 * 
 * Generates deployment configurations based on intelligent analysis:
 * - deployment-{type}.config.yml files
 * - GitHub Actions workflows
 * - Environment-specific settings
 * - Security configurations
 */

export class ConfigurationGenerator {
  constructor() {
    this.templates = {
      base_config: this.getBaseConfigTemplate(),
      workflows: this.getWorkflowTemplates(),
      security: this.getSecurityTemplates()
    };
  }

  generateDeploymentConfig(analysis, optimization, options = {}) {
    const {
      app_name,
      instance_name,
      aws_region = 'us-east-1',
      custom_overrides = {}
    } = options;

    const config = {
      // AWS Configuration
      aws: {
        region: aws_region
      },

      // Lightsail Configuration
      lightsail: {
        instance_name: instance_name || `${analysis.detected_type}-${app_name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`,
        static_ip: "",
        bundle_id: custom_overrides.bundle_id || optimization.recommended_bundle,
        blueprint_id: this.selectBlueprint(analysis)
      },

      // Application Configuration
      application: {
        name: app_name.toLowerCase().replace(/[^a-z0-9]/g, '-'),
        version: "1.0.0",
        type: analysis.detected_type,
        package_files: this.generatePackageFiles(analysis),
        package_fallback: true,
        environment_variables: this.generateEnvironmentVariables(analysis, optimization)
      },

      // Dependencies Configuration
      dependencies: this.generateDependencies(analysis, optimization),

      // Deployment Configuration
      deployment: this.generateDeploymentSettings(analysis, optimization),

      // GitHub Actions Configuration
      github_actions: this.generateGitHubActionsConfig(analysis),

      // Monitoring Configuration
      monitoring: this.generateMonitoringConfig(analysis),

      // Security Configuration
      security: this.generateSecurityConfig(analysis),

      // Backup Configuration
      backup: this.generateBackupConfig(analysis)
    };

    // Add bucket configuration if needed
    if (optimization.bucket_config) {
      config.lightsail.bucket = {
        enabled: true,
        name: `${app_name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-bucket`,
        access_level: optimization.bucket_config.access_level,
        bundle_id: optimization.bucket_config.bundle_id
      };
    }

    return config;
  }

  selectBlueprint(analysis) {
    // Default to Ubuntu 22.04 for most applications
    let blueprint = 'ubuntu_22_04';
    
    // Special cases
    if (analysis.detected_type === 'lamp' && 
        analysis.frameworks.some(f => f.name.includes('laravel') || f.name.includes('symfony'))) {
      blueprint = 'ubuntu_22_04'; // PHP works well on Ubuntu
    }
    
    return blueprint;
  }

  generatePackageFiles(analysis) {
    const appType = analysis.detected_type;
    const baseDir = `example-${appType}-app`;
    
    const packageFiles = [`${baseDir}/`];
    
    // Add specific files based on application type
    switch (appType) {
      case 'nodejs':
        packageFiles.push(
          `${baseDir}/package.json`,
          `${baseDir}/package-lock.json`,
          `${baseDir}/app.js`,
          `${baseDir}/routes/**`,
          `${baseDir}/public/**`
        );
        break;
        
      case 'python':
        packageFiles.push(
          `${baseDir}/requirements.txt`,
          `${baseDir}/app.py`,
          `${baseDir}/wsgi.py`,
          `${baseDir}/templates/**`,
          `${baseDir}/static/**`
        );
        break;
        
      case 'lamp':
        packageFiles.push(
          `${baseDir}/index.php`,
          `${baseDir}/config/**`,
          `${baseDir}/api/**`,
          `${baseDir}/assets/**`
        );
        break;
        
      case 'react':
        packageFiles.push(
          `${baseDir}/build/**`,
          `${baseDir}/package.json`
        );
        break;
        
      case 'docker':
        packageFiles.push(
          `${baseDir}/Dockerfile`,
          `${baseDir}/docker-compose.yml`,
          `${baseDir}/src/**`,
          `${baseDir}/.dockerignore`
        );
        break;
        
      case 'nginx':
        packageFiles.push(
          `${baseDir}/index.html`,
          `${baseDir}/css/**`,
          `${baseDir}/js/**`,
          `${baseDir}/images/**`
        );
        break;
    }
    
    return packageFiles;
  }

  generateEnvironmentVariables(analysis, optimization) {
    const envVars = {
      APP_ENV: 'production',
      NODE_ENV: 'production'
    };

    // Database environment variables
    if (optimization.database_config) {
      const dbConfig = optimization.database_config;
      envVars.DB_TYPE = dbConfig.type;
      envVars.DB_HOST = dbConfig.external ? 'RDS_ENDPOINT' : 'localhost';
      envVars.DB_NAME = 'app_db';
      envVars.DB_USER = 'app_user';
      envVars.DB_PASSWORD = 'CHANGE_ME_secure_password_123';
      
      if (dbConfig.external) {
        envVars.DB_RDS_NAME = `${analysis.detected_type}-${dbConfig.type}-db`;
      }
    }

    // Application-specific environment variables
    switch (analysis.detected_type) {
      case 'nodejs':
        envVars.PORT = '3000';
        break;
      case 'python':
        envVars.FLASK_ENV = 'production';
        envVars.FLASK_APP = 'app.py';
        envVars.PORT = '5000';
        break;
      case 'docker':
        envVars.COMPOSE_PROJECT_NAME = analysis.application?.name || 'docker-app';
        envVars.DOCKER_BUILDKIT = '1';
        break;
    }

    // Bucket environment variables
    if (optimization.bucket_config) {
      envVars.BUCKET_NAME = `${analysis.application?.name || 'app'}-bucket`;
      envVars.AWS_REGION = 'us-east-1';
    }

    // Security environment variables
    if (analysis.security_considerations?.needs_auth) {
      envVars.JWT_SECRET = 'CHANGE_ME_jwt_secret_key';
      envVars.SESSION_SECRET = 'CHANGE_ME_session_secret';
    }

    return envVars;
  }

  generateDependencies(analysis, optimization) {
    const dependencies = {
      git: {
        enabled: true,
        config: {
          install_lfs: false
        }
      },
      firewall: {
        enabled: true,
        config: {
          allowed_ports: ['22', '80', '443'],
          deny_all_other: true
        }
      }
    };

    // Database dependencies
    if (optimization.database_config) {
      const dbType = optimization.database_config.type;
      dependencies[dbType] = {
        enabled: !optimization.database_config.external,
        external: optimization.database_config.external,
        config: this.getDatabaseConfig(dbType, optimization.database_config)
      };
    }

    // Application-specific dependencies
    switch (analysis.detected_type) {
      case 'nodejs':
        dependencies.nodejs = {
          enabled: true,
          config: {
            version: '18',
            package_manager: 'npm'
          }
        };
        dependencies.pm2 = {
          enabled: true,
          config: {
            app_name: analysis.application?.name || 'nodejs-app',
            instances: 1,
            exec_mode: 'cluster'
          }
        };
        dependencies.firewall.config.allowed_ports.push('3000');
        break;

      case 'python':
        dependencies.python = {
          enabled: true,
          config: {
            version: '3.9',
            pip_packages: ['flask', 'gunicorn']
          }
        };
        dependencies.gunicorn = {
          enabled: true,
          config: {
            app_module: 'app:app',
            workers: 2,
            bind: '0.0.0.0:5000'
          }
        };
        dependencies.firewall.config.allowed_ports.push('5000');
        break;

      case 'lamp':
        dependencies.apache = {
          enabled: true,
          config: {
            enable_rewrite: true,
            document_root: '/var/www/html'
          }
        };
        dependencies.php = {
          enabled: true,
          config: {
            version: '8.1',
            extensions: ['curl', 'json', 'mbstring', 'mysql', 'xml', 'zip']
          }
        };
        break;

      case 'docker':
        dependencies.docker = {
          enabled: true,
          config: {
            install_compose: true
          }
        };
        break;

      case 'nginx':
      case 'react':
        dependencies.nginx = {
          enabled: true,
          config: {
            document_root: '/var/www/html',
            enable_gzip: true,
            client_max_body_size: '10M'
          }
        };
        break;
    }

    return dependencies;
  }
  getDatabaseConfig(dbType, dbConfig) {
    const config = {
      version: dbType === 'mysql' ? '8.0' : '13',
      root_password: 'CHANGE_ME_root_password_123',
      create_database: 'app_db',
      create_user: 'app_user',
      user_password: 'CHANGE_ME_secure_password_123'
    };

    if (dbConfig.external) {
      config.rds = {
        database_name: `${dbType}-db`,
        region: 'us-east-1',
        master_database: 'app_db',
        environment: {
          DB_CONNECTION_TIMEOUT: '30',
          DB_CHARSET: dbType === 'mysql' ? 'utf8mb4' : 'UTF8'
        }
      };
    }

    return config;
  }

  generateDeploymentSettings(analysis, optimization) {
    const settings = {
      timeouts: {
        ssh_connection: 120,
        command_execution: 600,
        health_check: 180
      },
      retries: {
        max_attempts: 3,
        ssh_connection: 5
      },
      steps: {
        pre_deployment: {
          common: {
            enabled: true,
            update_packages: true,
            create_directories: true,
            backup_enabled: true
          },
          dependencies: {
            enabled: true,
            install_system_deps: true,
            configure_services: true
          }
        },
        post_deployment: {
          common: {
            enabled: true,
            verify_extraction: true,
            create_env_file: true,
            cleanup_temp_files: true
          },
          dependencies: {
            enabled: true,
            configure_application: true,
            set_permissions: true,
            restart_services: true
          }
        },
        verification: {
          enabled: true,
          health_check: true,
          external_connectivity: true,
          endpoints_to_test: ['/']
        }
      }
    };

    // Add Docker-specific settings
    if (analysis.detected_type === 'docker') {
      settings.use_docker = true;
      settings.docker_app_path = `/opt/${analysis.application?.name || 'app'}`;
      settings.docker_compose_file = 'docker-compose.yml';
    }

    // Add application-specific health check endpoints
    if (analysis.detected_type === 'nodejs' || analysis.detected_type === 'python') {
      settings.steps.verification.endpoints_to_test.push('/api/health');
      if (analysis.detected_type === 'nodejs') {
        settings.steps.verification.port = 3000;
      }
    }

    return settings;
  }

  generateGitHubActionsConfig(analysis) {
    return {
      triggers: {
        push_branches: ['main', 'master'],
        pull_request_branches: ['main', 'master'],
        workflow_dispatch: true
      },
      jobs: {
        test: {
          enabled: true,
          docker_test: analysis.detected_type === 'docker',
          language_specific_tests: analysis.detected_type !== 'docker'
        },
        deployment: {
          deploy_on_push: true,
          deploy_on_pr: false,
          artifact_retention_days: 1,
          create_summary: true
        }
      }
    };
  }

  generateMonitoringConfig(analysis) {
    const config = {
      health_check: {
        endpoint: '/',
        max_attempts: 15,
        wait_between_attempts: 20,
        initial_wait: 60
      }
    };

    // Add expected content based on application type
    const expectedContent = {
      'lamp': 'LAMP Stack',
      'nodejs': 'Node.js',
      'python': 'Flask',
      'react': 'React',
      'docker': 'Docker',
      'nginx': 'Welcome'
    };

    config.health_check.expected_content = expectedContent[analysis.detected_type] || 'Welcome';

    // Add port for Node.js applications
    if (analysis.detected_type === 'nodejs') {
      config.health_check.port = 3000;
    }

    return config;
  }

  generateSecurityConfig(analysis) {
    return {
      file_permissions: {
        web_files: '644',
        directories: '755',
        config_files: '600'
      },
      ssl: {
        enabled: analysis.security_considerations?.needs_ssl !== false,
        force_https: true,
        certificate_auto_renew: true
      },
      firewall: {
        strict_mode: analysis.security_considerations?.handles_user_data || false,
        rate_limiting: analysis.detected_type === 'nodejs' || analysis.detected_type === 'python'
      }
    };
  }

  generateBackupConfig(analysis) {
    return {
      enabled: true,
      retention_days: 7,
      backup_location: `/var/backups/${analysis.application?.name || 'app'}-deployments`,
      backup_database: analysis.databases?.length > 0,
      backup_uploads: analysis.storage_needs?.file_uploads || false
    };
  }

  generateWorkflow(analysis, options = {}) {
    const { app_name, aws_region = 'us-east-1' } = options;
    const appType = analysis.detected_type;

    // Use string concatenation to avoid template literal conflicts with GitHub Actions syntax
    return 'name: ' + app_name + ' Deployment\n\n' +
      'on:\n' +
      '  push:\n' +
      '    branches: [ main, master ]\n' +
      '    paths:\n' +
      '      - \'example-' + appType + '-app/**\'\n' +
      '      - \'deployment-' + appType + '.config.yml\'\n' +
      '      - \'.github/workflows/deploy-' + appType + '.yml\'\n' +
      '  pull_request:\n' +
      '    branches: [ main, master ]\n' +
      '    paths:\n' +
      '      - \'example-' + appType + '-app/**\'\n' +
      '      - \'deployment-' + appType + '.config.yml\'\n' +
      '  workflow_dispatch:\n' +
      '    inputs:\n' +
      '      environment:\n' +
      '        description: \'Deployment environment\'\n' +
      '        required: false\n' +
      '        default: \'production\'\n' +
      '        type: choice\n' +
      '        options:\n' +
      '          - production\n' +
      '          - staging\n\n' +
      'permissions:\n' +
      '  id-token: write   # Required for OIDC authentication\n' +
      '  contents: read    # Required to checkout code\n\n' +
      'jobs:\n' +
      '  deploy:\n' +
      '    name: Deploy ' + app_name + '\n' +
      '    uses: ./.github/workflows/deploy-generic-reusable.yml\n' +
      '    with:\n' +
      '      config_file: \'deployment-' + appType + '.config.yml\'\n' +
      '      aws_region: \'' + aws_region + '\'\n' +
      '    secrets: inherit\n' +
      '  \n' +
      '  summary:\n' +
      '    name: Deployment Summary\n' +
      '    needs: deploy\n' +
      '    runs-on: ubuntu-latest\n' +
      '    if: always()\n' +
      '    steps:\n' +
      '      - name: Show Deployment Results\n' +
      '        run: |\n' +
      '          echo "## 🚀 ' + app_name + ' Deployment" >> $GITHUB_STEP_SUMMARY\n' +
      '          echo "" >> $GITHUB_STEP_SUMMARY\n' +
      '          echo "- **URL**: ${{ needs.deploy.outputs.deployment_url }}" >> $GITHUB_STEP_SUMMARY\n' +
      '          echo "- **Status**: ${{ needs.deploy.outputs.deployment_status }}" >> $GITHUB_STEP_SUMMARY\n' +
      '          echo "" >> $GITHUB_STEP_SUMMARY\n' +
      '          \n' +
      '          if [ "${{ needs.deploy.outputs.deployment_status }}" = "success" ]; then\n' +
      '            echo "✅ Application deployed successfully!" >> $GITHUB_STEP_SUMMARY\n' +
      '          else\n' +
      '            echo "❌ Deployment failed. Check logs above." >> $GITHUB_STEP_SUMMARY\n' +
      '          fi\n';
  }

  getBaseConfigTemplate() {
    return {
      // Template structure for base configuration
    };
  }

  getWorkflowTemplates() {
    return {
      // Workflow templates
    };
  }

  getSecurityTemplates() {
    return {
      // Security configuration templates
    };
  }

  formatYAML(config, indent = 0) {
    const spaces = '  '.repeat(indent);
    let yaml = '';

    for (const [key, value] of Object.entries(config)) {
      if (value === null || value === undefined) {
        continue;
      }

      if (typeof value === 'object' && !Array.isArray(value)) {
        yaml += `${spaces}${key}:\n`;
        yaml += this.formatYAML(value, indent + 1);
      } else if (Array.isArray(value)) {
        yaml += `${spaces}${key}:\n`;
        for (const item of value) {
          if (typeof item === 'object') {
            yaml += `${spaces}  -\n`;
            yaml += this.formatYAML(item, indent + 2);
          } else {
            yaml += `${spaces}  - ${item}\n`;
          }
        }
      } else {
        const valueStr = typeof value === 'string' && value.includes(':') ? `"${value}"` : value;
        yaml += `${spaces}${key}: ${valueStr}\n`;
      }
    }

    return yaml;
  }
}