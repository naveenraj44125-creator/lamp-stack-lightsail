#!/bin/bash

# Config Generation Module
# Generates deployment configuration files and GitHub Actions workflows

# Function to show application-specific warnings for common deployment issues
show_app_deployment_warnings() {
    local app_type="$1"
    
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Pre-Deployment Checklist${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Common warnings for all app types
    echo -e "${BLUE}1. Health Check Endpoint:${NC}"
    echo -e "   Your app needs a PUBLIC endpoint (no auth) for health checks."
    echo -e "   The deployment will fail if the health endpoint returns 401/403."
    echo -e "   ${GREEN}Recommended:${NC} Add GET /api/health returning {\"status\": \"ok\"}"
    echo ""
    
    # Node.js specific warnings
    if [[ "$app_type" == "nodejs" ]]; then
        echo -e "${BLUE}2. Frontend Serving (Node.js):${NC}"
        echo -e "   If you have a React/Vue/Angular frontend in /client:"
        echo -e "   - Add 'npm run build' script to build the frontend"
        echo -e "   - Server must serve static files: app.use(express.static('client/build'))"
        echo -e "   - Add catch-all route for SPA: app.get('*', (req,res) => res.sendFile(...))"
        echo ""
        
        echo -e "${BLUE}3. Build Script:${NC}"
        echo -e "   Ensure package.json has a 'build' script if frontend needs building"
        echo -e "   ${GREEN}Example:${NC} \"build\": \"cd client && npm install && npm run build\""
        echo ""
        
        echo -e "${BLUE}4. Start Script:${NC}"
        echo -e "   Root package.json needs a 'start' script for production"
        echo -e "   ${GREEN}Example:${NC} \"start\": \"cd server && npm start\" or \"start\": \"node app.js\""
        echo ""
    fi
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

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

    echo -e "${GREEN}✓ Created deployment-${app_type}.config.yml${NC}"
    
    # Show deployment warnings and checks
    show_app_deployment_warnings "$app_type"
}

# Function to create GitHub Actions workflow that matches existing examples
create_github_workflow() {
    local app_type="$1"
    local app_name="$2"
    local aws_region="$3"
    
    echo -e "${BLUE}Creating GitHub Actions workflow...${NC}"
    
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

    echo -e "${GREEN}✓ Created .github/workflows/deploy-${app_type}.yml${NC}"
}
