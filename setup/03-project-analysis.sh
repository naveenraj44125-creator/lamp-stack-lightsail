#!/bin/bash

# Function to analyze project using MCP server's project analyzer
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
        
        if echo "$req_content" | grep -qi "mysql\|pymysql"; then
            detected_databases+=("mysql")
            RECOMMENDED_DATABASE="mysql"
        fi
        
        # Check for file upload libraries
        if echo "$req_content" | grep -qi "pillow\|boto3"; then
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
    fi
    
    # Check for Docker
    if [[ -f "Dockerfile" ]] || [[ -f "docker-compose.yml" ]]; then
        detected_frameworks+=("docker")
        RECOMMENDED_APP_TYPE="docker"
        ANALYSIS_CONFIDENCE=90
        RECOMMENDED_BUNDLE="medium_3_0"
    fi
    
    # Determine bundle size based on complexity
    if [[ ${#detected_frameworks[@]} -gt 1 ]] || [[ -n "$RECOMMENDED_DATABASE" && "$RECOMMENDED_DATABASE" != "none" ]]; then
        RECOMMENDED_BUNDLE="small_3_0"
    fi
    
    echo -e "${GREEN}✓ Scanning complete!${NC}                    "
    echo ""
    
    # Display recommendations if any were found
    if [[ -n "$RECOMMENDED_APP_TYPE" ]]; then
        echo -e "${GREEN}✓ Project Analysis Complete!${NC}"
        echo ""
        echo -e "┌─────────────────────────────────────────────────────────────┐"
        echo -e "│ ${CYAN}🤖 AI Recommendations${NC} (${ANALYSIS_CONFIDENCE}% confidence)"
        echo -e "├─────────────────────────────────────────────────────────────┤"
        
        if [[ ${#detected_frameworks[@]} -gt 0 ]]; then
            echo -e "│   ${BLUE}Detected Frameworks:${NC} ${detected_frameworks[*]}                             │"
        fi
        
        echo -e "│   ${BLUE}Recommended App Type:${NC} ${RECOMMENDED_APP_TYPE}                             │"
        
        if [[ -n "$RECOMMENDED_DATABASE" ]]; then
            echo -e "│   ${BLUE}Recommended Database:${NC} ${RECOMMENDED_DATABASE}                         │"
        fi
        
        echo -e "│   ${BLUE}Recommended Instance:${NC} ${RECOMMENDED_BUNDLE}                          │"
        
        if [[ "$RECOMMENDED_BUCKET" == "true" ]]; then
            echo -e "│   ${BLUE}Storage Bucket:${NC} Recommended (file uploads detected)      │"
        fi
        
        echo -e "└─────────────────────────────────────────────────────────────┘"
        echo ""
        echo -e "${YELLOW}★ Recommended options will be highlighted in the menus below${NC}"
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
