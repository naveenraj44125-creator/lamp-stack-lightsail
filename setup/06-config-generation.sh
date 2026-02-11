#!/bin/bash

################################################################################
# Config Generation Module (06-config-generation.sh)
################################################################################
#
# Purpose: Generate deployment configuration files, GitHub Actions workflows,
#          and example application files for various application types
#
# Dependencies:
#   - 00-variables.sh (color codes, configuration variables)
#   - 01-utils.sh (to_lowercase, to_uppercase utility functions)
#   - 03-project-analysis.sh (detect_node_port, detect_fullstack_react,
#                             show_app_deployment_warnings)
#
# Functions:
#   - create_deployment_config()  : Generate deployment-{type}.config.yml (~500 lines)
#   - create_github_workflow()    : Generate GitHub Actions workflow files
#   - create_example_app()        : Generate example application files (~800 lines)
#
# App Types Supported:
#   - lamp (Linux, Apache, MySQL, PHP)
#   - nodejs (Node.js with Express)
#   - python (Python with Flask)
#   - react (React SPA)
#   - docker (Docker Compose)
#   - nginx (Static site with Nginx)
#
################################################################################

# Function to create deployment configuration based on existing examples
create_deployment_config() {
    local app_type="$1"
    local app_name="$2"
    local instance_name="$3"
    local aws_region="$4"
    local blueprint_id="$5"
    local bundle_id="$6"
    local db_type="$7"
    local db_external="$8"
    local db_rds_name="$9"
    local db_name="${10}"
    local bucket_name="${11}"
    local bucket_access="${12}"
    local bucket_bundle="${13}"
    local enable_bucket="${14}"
    
    echo -e "${BLUE}Creating deployment configuration for $app_type...${NC}"
    
    # Ensure we're in the working directory
    cd "$SCRIPT_START_DIR" || {
        echo -e "${RED}❌ Error: Cannot access working directory: $SCRIPT_START_DIR${NC}"
        exit 1
    }
    
    # Base configuration that matches our existing examples
    cat > "deployment-${app_type}.config.yml" << EOF
# ${app_name} Deployment Configuration

aws:
  region: ${aws_region}

lightsail:
  instance_name: ${instance_name}
  static_ip: ""
  
  # Instance size configuration (optional)
  # If not specified, defaults are: small_3_0 (2GB) for traditional apps, medium_3_0 (4GB) for Docker apps
  bundle_id: "${bundle_id}"
  
  # Operating system blueprint configuration (optional)
  # If not specified, defaults to ubuntu_22_04
  blueprint_id: "${blueprint_id}"

EOF

    # Add bucket configuration if enabled
    if [[ "$enable_bucket" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
  # Lightsail bucket configuration
  bucket:
    enabled: true
    name: "${bucket_name}"
    access_level: "${bucket_access}"
    bundle_id: "${bucket_bundle}"

EOF
    fi

    # Application configuration based on type
    cat >> "deployment-${app_type}.config.yml" << EOF
application:
  name: $(echo "${app_name}" | tr '[:upper:]' '[:lower:]')
  version: "1.0.0"
  type: ${app_type}
  
  package_files:
    - "./"
  
  package_fallback: true
  
  environment_variables:
    APP_ENV: production
EOF

    # Add database environment variables (available for all application types)
    if [[ "$db_type" != "none" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    # Database Configuration
    DB_TYPE: ${db_type}
    DB_HOST: $([ "$db_external" = "true" ] && echo "RDS_ENDPOINT" || echo "localhost")
    DB_NAME: ${db_name:-app_db}
    DB_USER: app_user
    DB_PASSWORD: CHANGE_ME_secure_password_123
EOF
        if [[ "$db_external" == "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
    DB_RDS_NAME: ${db_rds_name:-${app_type}-${db_type}-db}
EOF
        fi
        # MongoDB-specific connection string (no auth - MongoDB installed without authentication)
        if [[ "$db_type" == "mongodb" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
    # MongoDB specific (no authentication - local MongoDB)
    MONGODB_URI: mongodb://localhost:27017/${db_name:-app_db}
    MONGODB_PORT: "27017"
EOF
        fi
    fi

    # Add type-specific environment variables
    case $app_type in
        "lamp")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # LAMP Stack specific
    APACHE_DOCUMENT_ROOT: /var/www/html
EOF
            ;;
        "nodejs")
            # Detect actual port from server.js if it exists
            DETECTED_PORT=$(detect_node_port)
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Node.js specific
    NODE_ENV: production
    PORT: "${DETECTED_PORT}"
EOF
            ;;
        "python")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Python/Flask specific
    FLASK_ENV: production
    FLASK_APP: app.py
    PORT: "5000"
EOF
            ;;
        "react")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # React specific
    REACT_APP_ENV: production
    BUILD_PATH: build
EOF
            ;;
        "docker")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Docker specific
    COMPOSE_PROJECT_NAME: $(to_lowercase "${app_name}")
    DOCKER_BUILDKIT: "1"
EOF
            ;;
        "nginx")
            cat >> "deployment-${app_type}.config.yml" << EOF
    # Nginx specific
    NGINX_DOCUMENT_ROOT: /var/www/html
EOF
            ;;
    esac

    # Add bucket environment variables if enabled
    if [[ "$enable_bucket" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    BUCKET_NAME: ${bucket_name}
    AWS_REGION: ${aws_region}
EOF
    fi

    # Dependencies configuration based on app type
    cat >> "deployment-${app_type}.config.yml" << EOF

dependencies:
EOF

    # Database configuration (available for all application types)
    cat >> "deployment-${app_type}.config.yml" << EOF
  # Database Dependencies
  mysql:
    enabled: $([ "$db_type" = "mysql" ] && [ "$db_external" = "false" ] && echo "true" || echo "false")
    external: $([ "$db_external" = "true" ] && echo "true" || echo "false")
    config:
      version: "8.0"
      root_password: "CHANGE_ME_root_password_123"
      create_database: "${db_name:-app_db}"
      create_user: "app_user"
      user_password: "CHANGE_ME_secure_password_123"
EOF

    if [[ "$db_external" == "true" && "$db_type" == "mysql" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    rds:
      database_name: "${db_rds_name:-${app_type}-mysql-db}"
      region: "${aws_region}"
      master_database: "${db_name:-app_db}"
      environment:
        DB_CONNECTION_TIMEOUT: "30"
        DB_CHARSET: "utf8mb4"
EOF
    fi

    cat >> "deployment-${app_type}.config.yml" << EOF
  
  postgresql:
    enabled: $([ "$db_type" = "postgresql" ] && [ "$db_external" = "false" ] && echo "true" || echo "false")
    external: $([ "$db_external" = "true" ] && echo "true" || echo "false")
    config:
      version: "13"
      postgres_password: "CHANGE_ME_postgres_password_123"
      create_database: "${db_name:-app_db}"
      create_user: "app_user"
      user_password: "CHANGE_ME_secure_password_123"
EOF

    if [[ "$db_external" == "true" && "$db_type" == "postgresql" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    rds:
      database_name: "${db_rds_name:-${app_type}-postgres-db}"
      region: "${aws_region}"
      master_database: "${db_name:-app_db}"
      environment:
        DB_CONNECTION_TIMEOUT: "30"
EOF
    fi

    # MongoDB configuration (local only - no RDS support)
    cat >> "deployment-${app_type}.config.yml" << EOF
  
  mongodb:
    enabled: $([ "$db_type" = "mongodb" ] && echo "true" || echo "false")
    external: false
    config:
      version: "7.0"
      database: "${db_name:-app_db}"
      auth_enabled: true
      admin_user: "admin"
      admin_password: "CHANGE_ME_admin_password_123"
      app_user: "app_user"
      app_password: "CHANGE_ME_app_password_123"
      bind_ip: "127.0.0.1"
      port: 27017
EOF

    case $app_type in
        "lamp")
            cat >> "deployment-${app_type}.config.yml" << EOF
  
  php:
    enabled: true
    config:
      version: "8.1"
      extensions:
        - curl
        - json
        - mbstring
        - mysql
        - xml
        - zip
      
  apache:
    enabled: true
    config:
      enable_rewrite: true
      document_root: "/var/www/html"
EOF
            ;;
        "nodejs")
            cat >> "deployment-${app_type}.config.yml" << EOF
  
  nodejs:
    enabled: true
    config:
      version: "18"
      package_manager: "npm"
      
  pm2:
    enabled: true
    config:
      app_name: "$(to_lowercase "${app_name}")"
      instances: 1
      exec_mode: "cluster"
EOF
            ;;
        "python")
            cat >> "deployment-${app_type}.config.yml" << EOF
  
  python:
    enabled: true
    config:
      version: "3.9"
      pip_packages:
        - flask
        - gunicorn
        
  gunicorn:
    enabled: true
    config:
      app_module: "app:app"
      workers: 2
      bind: "0.0.0.0:5000"
EOF
            ;;
        "nginx")
            cat >> "deployment-${app_type}.config.yml" << EOF
  nginx:
    enabled: true
    config:
      document_root: "/var/www/html"
      enable_gzip: true
      client_max_body_size: "10M"
EOF
            ;;
        "docker")
            cat >> "deployment-${app_type}.config.yml" << EOF
  docker:
    enabled: true
    config:
      install_compose: true
EOF
            ;;
    esac

    # Common dependencies
    cat >> "deployment-${app_type}.config.yml" << EOF
  
  git:
    enabled: true
    config:
      install_lfs: false
  
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"    # SSH
        - "80"    # HTTP
        - "443"   # HTTPS
EOF

    # Add type-specific ports
    case $app_type in
        "nodejs")
            # Use detected port for firewall configuration
            DETECTED_PORT=$(detect_node_port)
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "${DETECTED_PORT}"  # Node.js
EOF
            ;;
        "python")
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "5000"  # Flask
EOF
            ;;
        "lamp")
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "8080"  # phpMyAdmin
EOF
            ;;
    esac

    cat >> "deployment-${app_type}.config.yml" << EOF
      deny_all_other: true

deployment:
EOF

    # Add Docker-specific deployment config
    if [[ "$app_type" == "docker" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
  use_docker: true
  docker_app_path: "/opt/$(to_lowercase "${app_name}")-app"
  docker_compose_file: "docker-compose.yml"
EOF
    fi

    # Common deployment configuration
    cat >> "deployment-${app_type}.config.yml" << EOF
  
  timeouts:
    ssh_connection: 120
    command_execution: 600
    health_check: 180
  
  retries:
    max_attempts: 3
    ssh_connection: 5
  
  steps:
    pre_deployment:
      common:
        enabled: true
        update_packages: true
        create_directories: true
        backup_enabled: true
      dependencies:
        enabled: true
        install_system_deps: true
        configure_services: true
    
    post_deployment:
      common:
        enabled: true
        verify_extraction: true
        create_env_file: true
        cleanup_temp_files: true
      dependencies:
        enabled: true
        configure_application: true
        set_permissions: true
        restart_services: true
    
    verification:
      enabled: true
      health_check: true
      external_connectivity: true
      endpoints_to_test:
EOF

    # Use custom endpoint if provided, otherwise use defaults
    if [[ -n "$VERIFICATION_ENDPOINT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
        - "${VERIFICATION_ENDPOINT}"
EOF
    elif [[ "$API_ONLY_APP" == "true" ]]; then
        # API-only apps don't have a root route
        cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/posts"
EOF
    else
        cat >> "deployment-${app_type}.config.yml" << EOF
        - "/"
EOF
    fi

    # Add type-specific endpoints and port configuration
    case $app_type in
        "nodejs")
            # Only add /api/health if not using custom endpoint and not API-only
            if [[ -z "$VERIFICATION_ENDPOINT" && "$API_ONLY_APP" != "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/health"
EOF
            fi
            # Use detected port for verification
            DETECTED_PORT=$(detect_node_port)
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: ${DETECTED_PORT}  # Node.js applications run on port ${DETECTED_PORT}
EOF
            ;;
        "python")
            if [[ -z "$VERIFICATION_ENDPOINT" && "$API_ONLY_APP" != "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/health"
EOF
            fi
            # Python/Flask apps typically run on port 5000
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 5000  # Flask applications run on port 5000
EOF
            ;;
        "lamp")
            if [[ -z "$VERIFICATION_ENDPOINT" && "$API_ONLY_APP" != "true" ]]; then
            cat >> "deployment-${app_type}.config.yml" << EOF
        - "/api/test.php"
EOF
            fi
            # LAMP apps run on port 80 (Apache)
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # Apache serves on port 80
EOF
            ;;
        "nginx")
            # Nginx apps run on port 80
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # Nginx serves on port 80
EOF
            ;;
        "react")
            # React apps are served via nginx on port 80
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # React build served via nginx on port 80
EOF
            ;;
        "docker")
            # Docker apps typically expose port 80
            cat >> "deployment-${app_type}.config.yml" << EOF
      port: 80  # Docker container exposes port 80
EOF
            ;;
    esac

    # GitHub Actions configuration
    cat >> "deployment-${app_type}.config.yml" << EOF

github_actions:
  triggers:
    push_branches:
      - main
      - master
    pull_request_branches:
      - main
      - master
    workflow_dispatch: true
  
  jobs:
    test:
      enabled: true
EOF

    # Add type-specific test configuration
    case $app_type in
        "docker")
            cat >> "deployment-${app_type}.config.yml" << EOF
      docker_test: true
EOF
            ;;
        *)
            cat >> "deployment-${app_type}.config.yml" << EOF
      language_specific_tests: true
EOF
            ;;
    esac

    cat >> "deployment-${app_type}.config.yml" << EOF
    
    deployment:
      deploy_on_push: true
      deploy_on_pr: false
      artifact_retention_days: 1
      create_summary: true

monitoring:
  health_check:
EOF

    # Use custom health check endpoint if provided
    if [[ -n "$HEALTH_CHECK_ENDPOINT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "${HEALTH_CHECK_ENDPOINT}"
EOF
    elif [[ -n "$VERIFICATION_ENDPOINT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "${VERIFICATION_ENDPOINT}"
EOF
    elif [[ "$API_ONLY_APP" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "/api/posts"
EOF
    else
        cat >> "deployment-${app_type}.config.yml" << EOF
    endpoint: "/"
EOF
    fi

    # Add type-specific expected content
    if [[ -n "$EXPECTED_CONTENT" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "${EXPECTED_CONTENT}"
EOF
    elif [[ "$API_ONLY_APP" == "true" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "["
EOF
    else
        case $app_type in
            "lamp")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "LAMP Stack"
EOF
                ;;
            "nodejs")
                # For fullstack React + Node.js apps, look for React-specific content
                if [ -d "client" ] && [ -f "client/package.json" ]; then
                    cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "root"
EOF
                else
                    cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "Node.js"
EOF
                fi
                ;;
            "python")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "Flask"
EOF
                ;;
            "react")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "root"
EOF
                ;;
            "docker")
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "Docker"
EOF
                ;;
            *)
                cat >> "deployment-${app_type}.config.yml" << EOF
    expected_content: "${app_name}"
EOF
                ;;
        esac
    fi

    # Add nodejs port if applicable
    if [[ "$app_type" == "nodejs" ]]; then
        DETECTED_PORT=$(detect_node_port)
        cat >> "deployment-${app_type}.config.yml" << EOF
    port: ${DETECTED_PORT}  # Node.js applications run on port ${DETECTED_PORT}
EOF
    fi

    cat >> "deployment-${app_type}.config.yml" << EOF
    max_attempts: 15
    wait_between_attempts: 20
    initial_wait: 60

security:
  file_permissions:
    web_files: "644"
    directories: "755"
    config_files: "600"

backup:
  enabled: true
  retention_days: 7
  backup_location: "/var/backups/$(to_lowercase "${app_name}")-deployments"
EOF

    # Add Docker-specific monitoring
    if [[ "$app_type" == "docker" ]]; then
        cat >> "deployment-${app_type}.config.yml" << EOF
  
  docker_health:
    check_containers: true
    required_containers:
      - "$(to_lowercase "${app_name}")-web"
EOF
    fi

    # Verify file was created successfully
    if [[ ! -f "deployment-${app_type}.config.yml" ]]; then
        echo -e "${RED}❌ Error: Failed to create deployment-${app_type}.config.yml${NC}"
        echo -e "${YELLOW}Expected location: $(realpath "$SCRIPT_START_DIR")/deployment-${app_type}.config.yml${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Created: $(realpath "deployment-${app_type}.config.yml")${NC}"
    
    # Show deployment warnings and checks
    show_app_deployment_warnings "$app_type"
}


# Function to create GitHub Actions workflow that matches existing examples
create_github_workflow() {
    local app_type="$1"
    local app_name="$2"
    local aws_region="$3"
    
    echo -e "${BLUE}Creating GitHub Actions workflow...${NC}"
    
    # Ensure we're in the working directory
    cd "$SCRIPT_START_DIR" || {
        echo -e "${RED}❌ Error: Cannot access working directory: $SCRIPT_START_DIR${NC}"
        exit 1
    }
    
    mkdir -p .github/workflows
    
    # Create workflow that calls the reusable workflow from the source repo
    # This ensures new repos always use the latest workflow code
    
    # Determine file patterns based on app type
    local file_patterns=""
    case $app_type in
        "lamp")
            file_patterns="      - '**/*.php'
      - '**/*.html'
      - '**/*.css'
      - '**/*.js'"
            ;;
        "nodejs")
            file_patterns="      - '**/*.js'
      - '**/*.json'
      - '**/*.html'
      - '**/*.css'"
            ;;
        "python")
            file_patterns="      - '**/*.py'
      - 'requirements.txt'
      - '**/*.html'
      - '**/*.css'"
            ;;
        "react")
            file_patterns="      - 'src/**'
      - 'public/**'
      - 'package.json'"
            ;;
        "docker")
            file_patterns="      - 'Dockerfile*'
      - 'docker-compose*.yml'
      - '**/*.php'
      - '**/*.js'"
            ;;
        "nginx")
            file_patterns="      - '**/*.html'
      - '**/*.css'
      - '**/*.js'"
            ;;
    esac
    
    cat > ".github/workflows/deploy-${app_type}.yml" << EOF
name: ${app_name} Deployment

on:
  push:
    branches: [ main, master ]
    paths:
${file_patterns}
      - 'deployment-${app_type}.config.yml'
      - '.github/workflows/deploy-${app_type}.yml'
  pull_request:
    branches: [ main, master ]
    paths:
${file_patterns}
      - 'deployment-${app_type}.config.yml'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: false
        default: 'production'
        type: choice
        options:
          - production
          - staging

permissions:
  id-token: write   # Required for OIDC authentication
  contents: read    # Required to checkout code

jobs:
  deploy:
    name: Deploy ${app_name}
    # Use reusable workflow from source repo - always gets latest fixes
    uses: naveenraj44125-creator/lamp-stack-lightsail/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-${app_type}.config.yml'
      aws_region: '${aws_region}'
    secrets: inherit
  
  summary:
    name: Deployment Summary
    needs: deploy
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Show Deployment Results
        run: |
          echo "## 🚀 ${app_name} Deployment" >> \$GITHUB_STEP_SUMMARY
          echo "" >> \$GITHUB_STEP_SUMMARY
          echo "- **URL**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
          echo "- **Status**: \${{ needs.deploy.outputs.deployment_status }}" >> \$GITHUB_STEP_SUMMARY
          echo "" >> \$GITHUB_STEP_SUMMARY
          
          if [ "\${{ needs.deploy.outputs.deployment_status }}" = "success" ]; then
            echo "✅ Application deployed successfully!" >> \$GITHUB_STEP_SUMMARY
            echo "" >> \$GITHUB_STEP_SUMMARY
EOF

    # Add type-specific summary information
    case $app_type in
        "lamp")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🔧 LAMP Stack" >> \$GITHUB_STEP_SUMMARY
            echo "- **Linux**: Ubuntu 22.04" >> \$GITHUB_STEP_SUMMARY
            echo "- **Apache**: Web Server" >> \$GITHUB_STEP_SUMMARY
            echo "- **MySQL**: Database" >> \$GITHUB_STEP_SUMMARY
            echo "- **PHP**: Application Runtime" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "nodejs")
            # Check if this is a fullstack React + Node.js app
            if [ -d "client" ] && [ -f "client/package.json" ]; then
                # Fullstack React + Node.js app
                cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### ⚛️ Fullstack React + Node.js" >> \$GITHUB_STEP_SUMMARY
            echo "- **Web App**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **API Health**: \${{ needs.deploy.outputs.deployment_url }}api/health" >> \$GITHUB_STEP_SUMMARY
            echo "- **Frontend**: React (production build)" >> \$GITHUB_STEP_SUMMARY
            echo "- **Backend**: Node.js + Express" >> \$GITHUB_STEP_SUMMARY
EOF
            else
                # Regular Node.js API
                cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 📡 Endpoints" >> \$GITHUB_STEP_SUMMARY
            echo "- **Home**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **Health**: \${{ needs.deploy.outputs.deployment_url }}api/health" >> \$GITHUB_STEP_SUMMARY
            echo "- **Info**: \${{ needs.deploy.outputs.deployment_url }}api/info" >> \$GITHUB_STEP_SUMMARY
EOF
            fi
            ;;
        "python")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🐍 Flask API" >> \$GITHUB_STEP_SUMMARY
            echo "- **Home**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **Health**: \${{ needs.deploy.outputs.deployment_url }}api/health" >> \$GITHUB_STEP_SUMMARY
            echo "- **API**: \${{ needs.deploy.outputs.deployment_url }}api/" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "react")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### ⚛️ React Dashboard" >> \$GITHUB_STEP_SUMMARY
            echo "- **Dashboard**: \${{ needs.deploy.outputs.deployment_url }}" >> \$GITHUB_STEP_SUMMARY
            echo "- **Build**: Production optimized" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "docker")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🐳 Docker Application" >> \$GITHUB_STEP_SUMMARY
            echo "- **Containers**: Multi-container setup" >> \$GITHUB_STEP_SUMMARY
            echo "- **Compose**: Docker Compose orchestration" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
        "nginx")
            cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
            echo "### 🌐 Static Site" >> \$GITHUB_STEP_SUMMARY
            echo "- **Server**: Nginx" >> \$GITHUB_STEP_SUMMARY
            echo "- **Content**: Static files" >> \$GITHUB_STEP_SUMMARY
EOF
            ;;
    esac

    cat >> ".github/workflows/deploy-${app_type}.yml" << EOF
          else
            echo "❌ Deployment failed. Check logs above." >> \$GITHUB_STEP_SUMMARY
          fi
EOF

    # Verify file was created successfully
    if [[ ! -f ".github/workflows/deploy-${app_type}.yml" ]]; then
        echo -e "${RED}❌ Error: Failed to create .github/workflows/deploy-${app_type}.yml${NC}"
        echo -e "${YELLOW}Expected location: $(realpath "$SCRIPT_START_DIR")/.github/workflows/deploy-${app_type}.yml${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Created: $(realpath ".github/workflows/deploy-${app_type}.yml")${NC}"
}


# Function to create example application that matches existing examples
create_example_app() {
    local app_type="$1"
    local app_name="$2"
    local custom_entry="${3:-}"  # Optional custom entry point from user
    
    echo -e "${BLUE}Creating example ${app_type} application in root directory...${NC}"
    echo -e "${YELLOW}Note: Existing files will NOT be overwritten${NC}"
    
    # Helper function to create file only if it doesn't exist
    create_file_if_not_exists() {
        local filepath="$1"
        if [[ -f "$filepath" ]]; then
            echo -e "${YELLOW}  ⚠ Skipping $filepath (already exists)${NC}"
            return 1
        fi
        return 0
    }
    
    case $app_type in
        "lamp")
            # Create PHP application similar to existing examples
            
            # Check for custom entry point first, then detect existing
            local detected_entry=""
            if [[ -n "$custom_entry" ]]; then
                detected_entry="$custom_entry"
                echo -e "${GREEN}  ✓ Using custom entry point: $detected_entry${NC}"
            else
                detected_entry=$(detect_entry_point "lamp")
            fi
            
            if [[ -n "$detected_entry" ]]; then
                if [[ -f "$detected_entry" ]]; then
                    echo -e "${GREEN}  ✓ Entry point exists: $detected_entry${NC}"
                    echo -e "${BLUE}  Skipping template file creation${NC}"
                    echo ""
                    return 0
                else
                    echo -e "${YELLOW}  ⚠️  Custom entry point specified but file doesn't exist: $detected_entry${NC}"
                    echo -e "${BLUE}  You'll need to create this file manually${NC}"
                    echo ""
                    return 0
                fi
            fi
            
            # No existing entry point found - create template files
            if create_file_if_not_exists "index.php"; then
            cat > "index.php" << 'PHP_EOF'
<?php
header('Content-Type: text/html; charset=UTF-8');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LAMP Stack Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 LAMP Stack Application</h1>
            <p>Successfully deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>PHP Version:</strong> <?php echo phpversion(); ?></p>
            <p><strong>Server:</strong> <?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?></p>
            <p><strong>Timestamp:</strong> <?php echo date('Y-m-d H:i:s T'); ?></p>
        </div>
        
        <div class="info">
            <h3>Database Connection</h3>
            <?php
            try {
                $host = $_ENV['DB_HOST'] ?? 'localhost';
                $dbname = $_ENV['DB_NAME'] ?? 'app_db';
                $username = $_ENV['DB_USER'] ?? 'app_user';
                $password = $_ENV['DB_PASSWORD'] ?? '';
                
                if ($password) {
                    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
                    echo "<p>✅ Database connection successful</p>";
                } else {
                    echo "<p>⚠️ Database credentials not configured</p>";
                }
            } catch (PDOException $e) {
                echo "<p>⚠️ Database connection failed: " . $e->getMessage() . "</p>";
            }
            ?>
        </div>
    </div>
</body>
</html>
PHP_EOF
            fi

            # Create API test endpoint
            mkdir -p "api"
            if create_file_if_not_exists "api/test.php"; then
            cat > "api/test.php" << 'PHP_EOF'
<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

echo json_encode([
    'status' => 'success',
    'message' => 'LAMP Stack API is working',
    'php_version' => phpversion(),
    'timestamp' => date('c'),
    'server' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'
]);
?>
PHP_EOF
            fi
            ;;
        
        "nodejs")
            # Create Node.js application similar to existing examples
            local app_name_lower=$(to_lowercase "${app_name}")
            
            # Check for custom entry point first, then detect existing
            local detected_entry=""
            if [[ -n "$custom_entry" ]]; then
                detected_entry="$custom_entry"
                echo -e "${GREEN}  ✓ Using custom entry point: $detected_entry${NC}"
            else
                detected_entry=$(detect_entry_point "nodejs")
            fi
            
            if [[ -n "$detected_entry" ]]; then
                if [[ -f "$detected_entry" ]]; then
                    echo -e "${GREEN}  ✓ Entry point exists: $detected_entry${NC}"
                    echo -e "${BLUE}  Skipping template file creation${NC}"
                    echo ""
                else
                    echo -e "${YELLOW}  ⚠️  Custom entry point specified but file doesn't exist: $detected_entry${NC}"
                    echo -e "${BLUE}  You'll need to create this file manually${NC}"
                    echo ""
                fi
                
                # Determine the correct start command based on entry point location
                local start_command=""
                if [[ "$detected_entry" == server/* ]]; then
                    # For server in subdirectory, need to handle npm install in server dir too
                    start_command="cd server && npm install && NODE_ENV=production node $(basename $detected_entry)"
                else
                    start_command="node ${detected_entry}"
                fi
                
                # Only create package.json if it doesn't exist
                if create_file_if_not_exists "package.json"; then
                cat > "package.json" << EOF
{
  "name": "${app_name_lower}",
  "version": "1.0.0",
  "description": "${app_name} Node.js application deployed via GitHub Actions",
  "main": "${detected_entry}",
  "scripts": {
    "start": "${start_command}",
    "dev": "nodemon ${detected_entry}",
    "test": "echo \\"No tests specified\\" && exit 0"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF
                fi
                
                # Check if existing package.json has incorrect start script
                if [[ -f "package.json" ]] && [[ "$detected_entry" == server/* ]]; then
                    local current_start=$(grep -o '"start"[[:space:]]*:[[:space:]]*"[^"]*"' package.json 2>/dev/null | head -1)
                    if echo "$current_start" | grep -q "node app.js\|node index.js" && [[ ! -f "app.js" ]] && [[ ! -f "index.js" ]]; then
                        echo -e "${YELLOW}  ⚠ Fixing package.json start script for server/ structure${NC}"
                        
                        # Use node to safely update package.json
                        node -e "
                            const fs = require('fs');
                            const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
                            pkg.scripts = pkg.scripts || {};
                            pkg.scripts.start = '${start_command}';
                            pkg.main = '${detected_entry}';
                            fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
                            console.log('Fixed package.json start script');
                        " 2>/dev/null || {
                            echo -e "${RED}  ❌ Could not auto-fix package.json - please update start script manually${NC}"
                        }
                        echo -e "${GREEN}  ✓ Updated package.json start script${NC}"
                    fi
                fi
                
                # Return early - skip template creation
                return 0
            fi
            
            # No existing entry point found - create template files
            if create_file_if_not_exists "package.json"; then
            cat > "package.json" << EOF
{
  "name": "${app_name_lower}",
  "version": "1.0.0",
  "description": "${app_name} Node.js application deployed via GitHub Actions",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "echo \\"No tests specified\\" && exit 0"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF
            fi
            
            if create_file_if_not_exists "app.js"; then
                cat > "app.js" << EOF
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {
    res.send(\`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${app_name}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #333; margin-bottom: 30px; }
                .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 ${app_name}</h1>
                    <p>Node.js Application deployed via GitHub Actions</p>
                </div>
                
                <div class="success">
                    ✅ Application is running successfully!
                </div>
                
                <div class="info">
                    <h3>System Information</h3>
                    <p><strong>Node.js Version:</strong> \${process.version}</p>
                    <p><strong>Environment:</strong> \${process.env.NODE_ENV || 'development'}</p>
                    <p><strong>Timestamp:</strong> \${new Date().toISOString()}</p>
                </div>
                
                <div class="info">
                    <h3>API Endpoints</h3>
                    <p><a href="/api/health">Health Check</a></p>
                    <p><a href="/api/info">System Info</a></p>
                </div>
            </div>
        </body>
        </html>
    \`);
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

app.get('/api/info', (req, res) => {
    res.json({
        status: 'success',
        message: '${app_name} Node.js Application',
        version: '1.0.0',
        node_version: process.version,
        environment: process.env.NODE_ENV || 'development',
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(\`🚀 ${app_name} server running on port \${PORT}\`);
    console.log(\`📍 Environment: \${process.env.NODE_ENV || 'development'}\`);
});
EOF
            fi
            ;;
        
        "python")
            # Create Python Flask application similar to existing examples
            
            # Check for custom entry point first, then detect existing
            local detected_entry=""
            if [[ -n "$custom_entry" ]]; then
                detected_entry="$custom_entry"
                echo -e "${GREEN}  ✓ Using custom entry point: $detected_entry${NC}"
            else
                detected_entry=$(detect_entry_point "python")
            fi
            
            if [[ -n "$detected_entry" ]]; then
                if [[ -f "$detected_entry" ]]; then
                    echo -e "${GREEN}  ✓ Entry point exists: $detected_entry${NC}"
                    echo -e "${BLUE}  Skipping template file creation${NC}"
                    echo ""
                    return 0
                else
                    echo -e "${YELLOW}  ⚠️  Custom entry point specified but file doesn't exist: $detected_entry${NC}"
                    echo -e "${BLUE}  You'll need to create this file manually${NC}"
                    echo ""
                    return 0
                fi
            fi
            
            # No existing entry point found - create template files
            if create_file_if_not_exists "requirements.txt"; then
            cat > "requirements.txt" << 'REQ_EOF'
Flask==3.0.0
gunicorn==21.2.0
flask-cors==4.0.0
REQ_EOF
            fi
            
            if create_file_if_not_exists "app.py"; then
            cat > "app.py" << EOF
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${app_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ${app_name}</h1>
            <p>Python Flask Application deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Python Version:</strong> {{ python_version }}</p>
            <p><strong>Flask Version:</strong> {{ flask_version }}</p>
            <p><strong>Environment:</strong> {{ environment }}</p>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
        </div>
        
        <div class="info">
            <h3>API Endpoints</h3>
            <p><a href="/api/health">Health Check</a></p>
            <p><a href="/api/info">System Info</a></p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    import sys
    import flask
    return render_template_string(HTML_TEMPLATE,
        python_version=sys.version.split()[0],
        flask_version=flask.__version__,
        environment=os.environ.get('FLASK_ENV', 'development'),
        timestamp=datetime.now().isoformat()
    )

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/info')
def info():
    import sys
    return jsonify({
        'status': 'success',
        'message': '${app_name} Python Flask Application',
        'version': '1.0.0',
        'python_version': sys.version.split()[0],
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
EOF
            fi
            ;;
        
        "react")
            # Create React application similar to existing examples
            local app_name_lower=$(to_lowercase "${app_name}")
            if create_file_if_not_exists "package.json"; then
            cat > "package.json" << EOF
{
  "name": "${app_name_lower}",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test --passWithNoTests",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF
            fi
            
            mkdir -p "public"
            mkdir -p "src"
            
            if create_file_if_not_exists "public/index.html"; then
            cat > "public/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="${app_name} React Application" />
    <title>${app_name}</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>
EOF
            fi
            
            if create_file_if_not_exists "src/index.js"; then
            cat > "src/index.js" << 'JS_EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
JS_EOF
            fi
            
            if create_file_if_not_exists "src/App.js"; then
            cat > "src/App.js" << EOF
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 ${app_name}</h1>
        <p>React Application deployed via GitHub Actions</p>
        
        <div className="success-message">
          ✅ Application is running successfully!
        </div>
        
        <div className="info-section">
          <h3>System Information</h3>
          <p><strong>React Version:</strong> {React.version}</p>
          <p><strong>Environment:</strong> {process.env.NODE_ENV}</p>
          <p><strong>Build Time:</strong> {process.env.REACT_APP_BUILD_TIME || 'Not set'}</p>
          <p><strong>Current Time:</strong> {currentTime.toLocaleString()}</p>
        </div>
        
        <div className="info-section">
          <h3>Features</h3>
          <ul>
            <li>Single Page Application (SPA)</li>
            <li>Production Build Optimization</li>
            <li>Static File Serving</li>
            <li>Responsive Design</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
EOF
            fi

            if create_file_if_not_exists "src/App.css"; then
            cat > "src/App.css" << 'CSS_EOF'
.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 40px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 15px;
  border-radius: 5px;
  margin: 20px 0;
  font-size: 16px;
}

.info-section {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 10px;
  margin: 20px 0;
  max-width: 600px;
}

.info-section h3 {
  margin-top: 0;
  color: #61dafb;
}

.info-section p, .info-section li {
  font-size: 14px;
  text-align: left;
}

.info-section ul {
  text-align: left;
}
CSS_EOF
            fi

            if create_file_if_not_exists "src/index.css"; then
            cat > "src/index.css" << 'CSS_EOF'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
CSS_EOF
            fi
            ;;
        
        "nginx")
            # Create static site similar to existing examples
            if create_file_if_not_exists "index.html"; then
            cat > "index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${app_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .feature-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ${app_name}</h1>
            <p>Nginx Static Site deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Server:</strong> Nginx</p>
            <p><strong>Content Type:</strong> Static HTML/CSS/JS</p>
            <p><strong>Timestamp:</strong> <span id="timestamp"></span></p>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card">
                <h4>🌐 Static Content</h4>
                <p>Fast, efficient static file serving with Nginx</p>
            </div>
            <div class="feature-card">
                <h4>📱 Responsive Design</h4>
                <p>Mobile-friendly responsive layout</p>
            </div>
            <div class="feature-card">
                <h4>⚡ High Performance</h4>
                <p>Optimized for speed and reliability</p>
            </div>
            <div class="feature-card">
                <h4>🔒 Secure</h4>
                <p>HTTPS ready with security headers</p>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
        
        // Update timestamp every second
        setInterval(() => {
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }, 1000);
    </script>
</body>
</html>
EOF
            fi
            ;;
        
        "docker")
            # Create Docker application similar to existing examples
            if create_file_if_not_exists "docker-compose.yml"; then
            cat > "docker-compose.yml" << EOF
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:80"
    environment:
      - APP_NAME=${app_name}
      - APP_ENV=production
    volumes:
      - ./html:/usr/share/nginx/html:ro
    restart: unless-stopped
    
  app:
    build:
      context: .
      dockerfile: Dockerfile.app
    environment:
      - APP_NAME=${app_name}
      - NODE_ENV=production
    restart: unless-stopped
    depends_on:
      - web

networks:
  default:
    name: $(to_lowercase "${app_name}")_network
EOF
            fi
            
            if create_file_if_not_exists "Dockerfile"; then
            cat > "Dockerfile" << 'DOCKER_EOF'
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static files
COPY html/ /usr/share/nginx/html/

# Create directory for logs
RUN mkdir -p /var/log/nginx

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
DOCKER_EOF
            fi

            if create_file_if_not_exists "Dockerfile.app"; then
            cat > "Dockerfile.app" << 'DOCKER_EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY app/ ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose port
EXPOSE 3000

# Start application
CMD ["node", "index.js"]
DOCKER_EOF
            fi

            mkdir -p "html"
            if create_file_if_not_exists "html/index.html"; then
            cat > "html/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${app_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .docker-info { background: #0db7ed; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ${app_name}</h1>
            <p>Docker Application deployed via GitHub Actions</p>
        </div>
        
        <div class="success">
            ✅ Application is running successfully!
        </div>
        
        <div class="docker-info">
            <h3>🐳 Docker Configuration</h3>
            <p><strong>Container:</strong> Multi-container setup with Docker Compose</p>
            <p><strong>Web Server:</strong> Nginx (Alpine Linux)</p>
            <p><strong>Application:</strong> Node.js backend service</p>
            <p><strong>Network:</strong> Custom Docker network</p>
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Deployment:</strong> Docker Compose</p>
            <p><strong>Environment:</strong> Production</p>
            <p><strong>Timestamp:</strong> <span id="timestamp"></span></p>
        </div>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
        setInterval(() => {
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }, 1000);
    </script>
</body>
</html>
EOF
            fi

            if create_file_if_not_exists "nginx.conf"; then
            cat > "nginx.conf" << 'NGINX_EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    server {
        listen       80;
        server_name  localhost;
        
        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
    }
}
NGINX_EOF
            fi

            mkdir -p "app"
            local app_name_lower=$(to_lowercase "${app_name}")
            if create_file_if_not_exists "package.json"; then
            cat > "package.json" << EOF
{
  "name": "${app_name_lower}-backend",
  "version": "1.0.0",
  "description": "${app_name} Docker backend service",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF
            fi

            if create_file_if_not_exists "app/index.js"; then
            cat > "app/index.js" << EOF
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: '${app_name} Backend',
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(\`🚀 ${app_name} backend service running on port \${PORT}\`);
});
EOF
            fi
            ;;
    esac
    
    echo -e "${GREEN}✓ Created ${app_type} application files in root directory${NC}"
}
