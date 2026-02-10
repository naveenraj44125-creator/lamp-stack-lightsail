#!/bin/bash

################################################################################
# Module: 03-project-analysis.sh
# Purpose: Project analysis and detection functions
# Dependencies: 00-variables.sh, 01-utils.sh
#
# This module provides functions for:
# - Analyzing project structure and providing AI recommendations
# - Detecting fullstack React + Node.js applications
# - Auto-detecting Node.js ports
# - Detecting health check endpoints
# - Building React clients
# - Showing deployment warnings
################################################################################

# Function to analyze project and provide intelligent recommendations
# This provides intelligent recommendations for deployment configuration
analyze_project_for_recommendations() {
    local project_path="${1:-.}"
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  🔍 Analyzing Your Project...${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Initialize recommendations
    RECOMMENDED_APP_TYPE=""
    RECOMMENDED_DATABASE="none"
    RECOMMENDED_BUNDLE="micro_3_0"
    RECOMMENDED_BUCKET="false"
    ANALYSIS_CONFIDENCE=0
    
    local detected_frameworks=()
    local detected_databases=()
    local needs_storage=false
    
    # Detect application type
    if [[ -f "package.json" ]]; then
        local pkg_content=$(cat package.json 2>/dev/null)
        
        # Check for React
        if echo "$pkg_content" | grep -q '"react"'; then
            detected_frameworks+=("react")
            RECOMMENDED_APP_TYPE="react"
            ANALYSIS_CONFIDENCE=80
        fi
        
        # Check for Express
        if echo "$pkg_content" | grep -q '"express"'; then
            detected_frameworks+=("express")
            RECOMMENDED_APP_TYPE="nodejs"
            ANALYSIS_CONFIDENCE=80
        fi
        
        # Check for database drivers
        if echo "$pkg_content" | grep -q '"mysql\|mysql2"'; then
            detected_databases+=("mysql")
            RECOMMENDED_DATABASE="mysql"
        fi
        
        if echo "$pkg_content" | grep -q '"pg\|postgres"'; then
            detected_databases+=("postgresql")
            RECOMMENDED_DATABASE="postgresql"
        fi
        
        if echo "$pkg_content" | grep -q '"mongodb\|mongoose"'; then
            detected_databases+=("mongodb")
            RECOMMENDED_DATABASE="none"  # MongoDB not directly supported
        fi
        
        # Check for file upload/storage libraries (Node.js)
        if echo "$pkg_content" | grep -qi '"multer"\|"formidable"\|"busboy"\|"aws-sdk"\|"@aws-sdk/client-s3"\|"sharp"\|"jimp"'; then
            needs_storage=true
            RECOMMENDED_BUCKET="true"
        fi
    fi
    
    # Check for Python
    if [[ -f "requirements.txt" ]] || [[ -f "app.py" ]]; then
        local req_content=""
        [[ -f "requirements.txt" ]] && req_content=$(cat requirements.txt 2>/dev/null)
        
        if echo "$req_content" | grep -qi "flask"; then
            detected_frameworks+=("flask")
            RECOMMENDED_APP_TYPE="python"
            ANALYSIS_CONFIDENCE=80
        fi
        
        if echo "$req_content" | grep -qi "django"; then
            detected_frameworks+=("django")
            RECOMMENDED_APP_TYPE="python"
            ANALYSIS_CONFIDENCE=80
        fi
        
        # Check for database drivers
        if echo "$req_content" | grep -qi "psycopg2\|postgresql"; then
            detected_databases+=("postgresql")
            RECOMMENDED_DATABASE="postgresql"
        fi
        
        if echo "$req_content" | grep -qi "mysql\|pymysql\|mysqlclient"; then
            detected_databases+=("mysql")
            RECOMMENDED_DATABASE="mysql"
        fi
        
        # Check for file upload/storage libraries (Python)
        if echo "$req_content" | grep -qi "pillow\|boto3\|flask-uploads\|django-storages\|werkzeug"; then
            needs_storage=true
            RECOMMENDED_BUCKET="true"
        fi
    fi
    
    # Check for PHP
    if [[ -f "composer.json" ]] || [[ -f "index.php" ]]; then
        local composer_content=""
        [[ -f "composer.json" ]] && composer_content=$(cat composer.json 2>/dev/null)
        
        if echo "$composer_content" | grep -qi "laravel"; then
            detected_frameworks+=("laravel")
            RECOMMENDED_APP_TYPE="lamp"
            ANALYSIS_CONFIDENCE=80
        else
            RECOMMENDED_APP_TYPE="lamp"
            ANALYSIS_CONFIDENCE=70
        fi
        
        # Check for database in PHP
        if echo "$composer_content" | grep -qi "doctrine/dbal\|illuminate/database"; then
            # Laravel typically uses MySQL
            detected_databases+=("mysql")
            RECOMMENDED_DATABASE="mysql"
        fi
        
        # Check for file upload libraries (PHP)
        if echo "$composer_content" | grep -qi "intervention/image\|league/flysystem\|aws/aws-sdk-php"; then
            needs_storage=true
            RECOMMENDED_BUCKET="true"
        fi
        
        # Check for common PHP upload patterns in code
        if [[ -f "index.php" ]] && grep -qi "move_uploaded_file\|\$_FILES" index.php 2>/dev/null; then
            needs_storage=true
            RECOMMENDED_BUCKET="true"
        fi
    fi
    
    # Check for Docker
    if [[ -f "Dockerfile" ]] || [[ -f "docker-compose.yml" ]]; then
        detected_frameworks+=("docker")
        RECOMMENDED_APP_TYPE="docker"
        ANALYSIS_CONFIDENCE=90
        RECOMMENDED_BUNDLE="medium_3_0"
        
        # Check docker-compose for database services
        if [[ -f "docker-compose.yml" ]]; then
            local compose_content=$(cat docker-compose.yml 2>/dev/null)
            
            if echo "$compose_content" | grep -qi "image:.*mysql\|mysql:"; then
                detected_databases+=("mysql")
                RECOMMENDED_DATABASE="mysql"
            fi
            
            if echo "$compose_content" | grep -qi "image:.*postgres\|postgres:"; then
                detected_databases+=("postgresql")
                RECOMMENDED_DATABASE="postgresql"
            fi
            
            # Check for volume mounts (indicates file storage needs)
            if echo "$compose_content" | grep -qi "volumes:\|/uploads\|/media\|/storage"; then
                needs_storage=true
                RECOMMENDED_BUCKET="true"
            fi
        fi
    fi
    
    # Determine bundle size based on complexity
    if [[ ${#detected_frameworks[@]} -gt 1 ]] || [[ -n "$RECOMMENDED_DATABASE" && "$RECOMMENDED_DATABASE" != "none" ]]; then
        RECOMMENDED_BUNDLE="small_3_0"
    fi
    
    echo -e "${GREEN}✓ Analysis complete!${NC}"
    echo ""
    
    # Display recommendations if any were found
    if [[ -n "$RECOMMENDED_APP_TYPE" ]]; then
        echo -e "┌─────────────────────────────────────────────────────────────┐"
        echo -e "│ ${CYAN}🤖 Smart Recommendations${NC} (${ANALYSIS_CONFIDENCE}% confidence)"
        echo -e "├─────────────────────────────────────────────────────────────┤"
        
        if [[ ${#detected_frameworks[@]} -gt 0 ]]; then
            echo -e "│   ${BLUE}Detected:${NC} ${detected_frameworks[*]}                             │"
        fi
        
        echo -e "│   ${BLUE}App Type:${NC} ${RECOMMENDED_APP_TYPE}                             │"
        
        if [[ -n "$RECOMMENDED_DATABASE" && "$RECOMMENDED_DATABASE" != "none" ]]; then
            echo -e "│   ${BLUE}Database:${NC} ${RECOMMENDED_DATABASE}                         │"
        fi
        
        echo -e "│   ${BLUE}Instance Size:${NC} ${RECOMMENDED_BUNDLE}                          │"
        
        if [[ "$RECOMMENDED_BUCKET" == "true" ]]; then
            echo -e "│   ${BLUE}Storage:${NC} Recommended (file uploads detected)      │"
        fi
        
        echo -e "└─────────────────────────────────────────────────────────────┘"
        echo ""
        echo -e "${YELLOW}★ Recommended options will be highlighted in the menus${NC}"
        echo ""
    fi
}

# Function to detect fullstack React + Node.js application
detect_fullstack_react() {
    # Check for various fullstack structures:
    # 1. server.js + client/ (traditional)
    # 2. server/ + client/ (organized)
    # 3. package.json with both react and express
    
    if [[ -f "server.js" && -d "client" ]] || [[ -d "server" && -d "client" ]]; then
        return 0
    fi
    
    return 1
}

# Function to auto-detect Node.js port from server.js or server/index.js
detect_node_port() {
    local server_file=""
    
    # Check multiple possible locations
    if [[ -f "server/server.js" ]]; then
        server_file="server/server.js"
    elif [[ -f "server/index.js" ]]; then
        server_file="server/index.js"
    elif [[ -f "server.js" ]]; then
        server_file="server.js"
    elif [[ -f "app.js" ]]; then
        server_file="app.js"
    elif [[ -f "index.js" ]]; then
        server_file="index.js"
    fi
    
    if [[ -n "$server_file" ]]; then
        # Try to extract port from common patterns (macOS compatible)
        local port=$(grep -o 'PORT.*=[^0-9]*[0-9]\{4\}' "$server_file" | grep -o '[0-9]\{4\}' | head -1)
        if [[ -z "$port" ]]; then
            port=$(grep -o 'listen([^0-9]*[0-9]\{4\}' "$server_file" | grep -o '[0-9]\{4\}' | head -1)
        fi
        
        if [[ -n "$port" ]]; then
            echo "$port"
            return 0
        fi
    fi
    
    # Default to 3000 if not found
    echo "3000"
}

# Function to detect health check endpoints in existing code
detect_health_endpoints() {
    local app_type="$1"
    local detected_endpoints=()
    
    case $app_type in
        "nodejs")
            # Check multiple possible server file locations
            local server_files=("server/server.js" "server/index.js" "server.js" "app.js" "index.js" "src/server.js" "src/index.js" "src/app.js" "src/index.ts" "src/server.ts")
            
            for file in "${server_files[@]}"; do
                if [[ -f "$file" ]]; then
                    # Look for common health endpoint patterns
                    if grep -q "'/health'\|'/api/health'\|'/healthcheck'\|'/status'\|'/ping'" "$file" 2>/dev/null; then
                        local endpoint=$(grep -o "'/[^']*health[^']*'\|'/[^']*status[^']*'\|'/ping'" "$file" | head -1 | tr -d "'")
                        if [[ -n "$endpoint" ]]; then
                            detected_endpoints+=("$endpoint")
                        fi
                    fi
                fi
            done
            ;;
        
        "python")
            # Check Python files
            local python_files=("app.py" "main.py" "server.py" "src/app.py" "src/main.py")
            
            for file in "${python_files[@]}"; do
                if [[ -f "$file" ]]; then
                    if grep -q "'/health'\|'/api/health'\|'/healthcheck'\|'/status'\|'/ping'" "$file" 2>/dev/null; then
                        local endpoint=$(grep -o "'/[^']*health[^']*'\|'/[^']*status[^']*'\|'/ping'" "$file" | head -1 | tr -d "'")
                        if [[ -n "$endpoint" ]]; then
                            detected_endpoints+=("$endpoint")
                        fi
                    fi
                fi
            done
            ;;
        
        "lamp")
            # Check PHP files
            if [[ -f "health.php" ]]; then
                detected_endpoints+=("/health.php")
            elif [[ -f "api/health.php" ]]; then
                detected_endpoints+=("/api/health.php")
            elif [[ -f "status.php" ]]; then
                detected_endpoints+=("/status.php")
            fi
            ;;
    esac
    
    # Return the first detected endpoint, or empty if none found
    if [[ ${#detected_endpoints[@]} -gt 0 ]]; then
        echo "${detected_endpoints[0]}"
    fi
}

# Function to build React client if detected
build_react_client_if_needed() {
    local app_type="$1"

    if [[ "$app_type" == "nodejs" ]] && [ -d "client" ] && [ -f "client/package.json" ]; then
        echo -e "${BLUE}Detected fullstack React + Node.js application${NC}"
        
        # Get detected port for consistency
        local DETECTED_PORT=$(detect_node_port)
        
        # Fix package.json scripts if needed
        if [ -f "package.json" ]; then
            local needs_fix=false
            
            # Check for missing scripts
            if ! grep -q '"build"' package.json 2>/dev/null; then
                needs_fix=true
            fi
            if ! grep -q '"start"' package.json 2>/dev/null; then
                needs_fix=true
            fi
            
            if [[ "$needs_fix" == "true" ]]; then
                echo -e "${YELLOW}⚠️  Root package.json missing required scripts for deployment${NC}"
                
                local FIX_PACKAGE="true"
                if [[ "$FULLY_AUTOMATED" != "true" ]]; then
                    FIX_PACKAGE=$(get_yes_no "Add missing 'build' and 'start' scripts to package.json?" "true")
                fi
                
                if [[ "$FIX_PACKAGE" == "true" ]]; then
                    echo -e "${BLUE}Updating package.json with deployment scripts...${NC}"
                    
                    # Determine the server entry point (check server/ subdirectory first)
                    local server_entry=""
                    if [ -f "server/server.js" ]; then
                        server_entry="cd server && npm install && NODE_ENV=production node server.js"
                    elif [ -f "server/index.js" ]; then
                        server_entry="cd server && npm install && NODE_ENV=production node index.js"
                    elif [ -f "server.js" ]; then
                        server_entry="node server.js"
                    elif [ -f "app.js" ]; then
                        server_entry="node app.js"
                    else
                        server_entry="cd server && npm install && NODE_ENV=production node server.js"
                    fi
                    
                    # Use node to safely update package.json
                    node -e "
                        const fs = require('fs');
                        const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
                        pkg.scripts = pkg.scripts || {};
                        if (!pkg.scripts.build) {
                            pkg.scripts.build = 'cd client && npm install && npm run build';
                        }
                        if (!pkg.scripts.start) {
                            pkg.scripts.start = '$server_entry';
                        }
                        if (!pkg.scripts.test) {
                            pkg.scripts.test = 'echo \"Error: no test specified\" && exit 1';
                        }
                        fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
                        console.log('Updated package.json scripts');
                    " 2>/dev/null || {
                        echo -e "${YELLOW}⚠️  Could not auto-update package.json - please add scripts manually${NC}"
                    }
                    
                    echo -e "${GREEN}✓ Updated package.json with build and start scripts${NC}"
                fi
            fi
            
            # Also check if start script points to non-existent file and fix it
            local current_start=$(grep -o '"start"[[:space:]]*:[[:space:]]*"[^"]*"' package.json 2>/dev/null | head -1)
            if echo "$current_start" | grep -q "node app.js" && [[ ! -f "app.js" ]]; then
                echo -e "${YELLOW}⚠️  Start script points to non-existent app.js, fixing...${NC}"
                
                # Determine correct start command
                local correct_start=""
                if [ -f "server/server.js" ]; then
                    correct_start="cd server && npm install && NODE_ENV=production node server.js"
                elif [ -f "server/index.js" ]; then
                    correct_start="cd server && npm install && NODE_ENV=production node index.js"
                elif [ -f "server.js" ]; then
                    correct_start="node server.js"
                fi
                
                if [ -n "$correct_start" ]; then
                    node -e "
                        const fs = require('fs');
                        const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
                        pkg.scripts = pkg.scripts || {};
                        pkg.scripts.start = '$correct_start';
                        fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
                        console.log('Fixed package.json start script');
                    " 2>/dev/null || {
                        echo -e "${RED}❌ Could not auto-fix package.json${NC}"
                    }
                    echo -e "${GREEN}✓ Fixed package.json start script${NC}"
                fi
            fi
        fi
        
        # Check and fix server file for production static serving
        local server_file=""
        if [ -f "server/server.js" ]; then
            server_file="server/server.js"
        elif [ -f "server/index.js" ]; then
            server_file="server/index.js"
        elif [ -f "server.js" ]; then
            server_file="server.js"
        fi
        
        if [ -n "$server_file" ] && [ -d "client" ]; then
            local needs_static_fix=false
            
            # Check if express.static for client/build is missing
            if ! grep -q "express.static.*client/build\|express.static.*client.*build" "$server_file" 2>/dev/null; then
                if ! grep -q "express.static.*build" "$server_file" 2>/dev/null; then
                    needs_static_fix=true
                fi
            fi
            
            # Check if SPA catch-all is missing
            if ! grep -q "sendFile.*index.html" "$server_file" 2>/dev/null; then
                needs_static_fix=true
            fi
            
            if [[ "$needs_static_fix" == "true" ]]; then
                echo -e "${YELLOW}⚠️  Server file missing production static file serving${NC}"
                echo -e "${YELLOW}   Your server needs to serve the React build in production:${NC}"
                echo ""
                echo -e "${BLUE}   Add this BEFORE your routes:${NC}"
                echo "   if (process.env.NODE_ENV === 'production') {"
                echo "     app.use(express.static(path.join(__dirname, '../client/build')));"
                echo "   }"
                echo ""
                echo -e "${BLUE}   Add this AFTER your API routes:${NC}"
                echo "   if (process.env.NODE_ENV === 'production') {"
                echo "     app.get('*', (req, res) => {"
                echo "       res.sendFile(path.join(__dirname, '../client/build/index.html'));"
                echo "     });"
                echo "   }"
                echo ""
                echo -e "${YELLOW}   Without these, your React frontend won't load in production!${NC}"
                echo ""
            fi
        fi

        # Check if client/build already exists
        if [ -d "client/build" ]; then
            echo -e "${YELLOW}⚠️ client/build directory already exists${NC}"
            if [[ "$FULLY_AUTOMATED" != "true" ]]; then
                BUILD_CLIENT=$(get_yes_no "Rebuild React client?" "true")
            else
                BUILD_CLIENT="true"
            fi
        else
            if [[ "$FULLY_AUTOMATED" != "true" ]]; then
                BUILD_CLIENT=$(get_yes_no "Build React client locally before deployment?" "true")
            else
                BUILD_CLIENT="true"
            fi
        fi

        if [[ "$BUILD_CLIENT" == "true" ]]; then
            echo -e "${BLUE}Building React client...${NC}"
            cd client
            if [ -f "package-lock.json" ]; then
                npm ci
            elif [ -f "yarn.lock" ]; then
                yarn install --frozen-lockfile
            else
                npm install
            fi
            npm run build
            cd ..

            if [ -d "client/build" ]; then
                echo -e "${GREEN}✓ React client built successfully${NC}"
                git add client/build/
                return 0
            else
                echo -e "${RED}❌ Failed to build React client${NC}"
                return 1
            fi
        fi
    fi

    return 0
}

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
    
    # Check for common issues in current directory
    local issues_found=false
    
    # Check for health endpoint in Node.js apps
    if [[ "$app_type" == "nodejs" ]]; then
        # Check multiple possible server file locations (including server/ subdirectory)
        local server_file=""
        if [ -f "server/server.js" ]; then
            server_file="server/server.js"
        elif [ -f "server/index.js" ]; then
            server_file="server/index.js"
        elif [ -f "server.js" ]; then
            server_file="server.js"
        elif [ -f "app.js" ]; then
            server_file="app.js"
        fi
        
        if [ -n "$server_file" ]; then
            if ! grep -q "/api/health\|/health" "$server_file" 2>/dev/null; then
                echo -e "${RED}⚠️  WARNING: No /api/health endpoint found in $server_file${NC}"
                issues_found=true
            fi
            if ! grep -q "express.static" "$server_file" 2>/dev/null; then
                if [ -d "client" ]; then
                    echo -e "${RED}⚠️  WARNING: No express.static() found in $server_file - frontend won't be served${NC}"
                    issues_found=true
                fi
            fi
            # Check for SPA catch-all route
            if [ -d "client" ]; then
                if ! grep -q "sendFile.*index.html\|sendFile.*build" "$server_file" 2>/dev/null; then
                    echo -e "${RED}⚠️  WARNING: No SPA catch-all route found - React routing won't work${NC}"
                    issues_found=true
                fi
            fi
        fi
        
        # Check for build script
        if [ -f "package.json" ] && [ -d "client" ]; then
            if ! grep -q '"build"' package.json 2>/dev/null; then
                echo -e "${RED}⚠️  WARNING: No 'build' script in package.json - frontend won't be built${NC}"
                issues_found=true
            fi
        fi
        
        # Check for start script
        if [ -f "package.json" ]; then
            if ! grep -q '"start"' package.json 2>/dev/null; then
                echo -e "${RED}⚠️  WARNING: No 'start' script in package.json - PM2 won't know how to start the app${NC}"
                issues_found=true
            fi
        fi
    fi
    
    if [[ "$issues_found" == "true" ]]; then
        echo ""
        echo -e "${YELLOW}Please fix the above issues before deployment to avoid failures.${NC}"
        echo -e "${YELLOW}The deployment workflow expects these to be in place.${NC}"
    else
        echo -e "${GREEN}✓ No obvious issues detected in your application code.${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}
