#!/bin/bash

################################################################################
# Module: 02-ui.sh
# Purpose: Handle all user interaction and input collection
#
# Dependencies: 00-variables.sh, 01-utils.sh
#
# Exports:
#   - get_input(prompt, default): Get text input from user
#   - get_yes_no(prompt, default): Get yes/no input from user
#   - select_option(prompt, default, recommendation_type, options...): Display menu and get selection
#   - get_option_description(option): Get description for known options
#
# Usage: Source this module after 00-variables.sh and 01-utils.sh
#        All functions respect AUTO_MODE for automated execution
################################################################################

# Function to get user input with default value (enhanced styling)
get_input() {
    local prompt="$1"
    local default="$2"
    local value
    
    if [[ "$AUTO_MODE" == "true" ]]; then
        echo "$default"
        return
    fi
    
    echo "" >&2
    echo -ne "${YELLOW}➤ $prompt${NC}" >&2
    if [[ -n "$default" ]]; then
        echo -ne " [${GREEN}$default${NC}]" >&2
    fi
    echo -n ": " >&2
    read -r value
    
    # Use default if no value entered
    if [[ -z "$value" ]]; then
        value="$default"
        if [[ -n "$value" ]]; then
            echo -e "${GREEN}✓ Using default: $value${NC}" >&2
        fi
    else
        echo -e "${GREEN}✓ Set: $value${NC}" >&2
    fi
    
    echo "$value"
}

# Function to get yes/no input (enhanced styling)
get_yes_no() {
    local prompt="$1"
    local default="$2"
    local value
    local default_display
    
    if [[ "$AUTO_MODE" == "true" ]]; then
        echo "$default"
        return
    fi
    
    # Format default display
    if [[ "$default" == "true" ]]; then
        default_display="${GREEN}Y${NC}/n"
    else
        default_display="y/${GREEN}N${NC}"
    fi
    
    while true; do
        echo -ne "${YELLOW}$prompt${NC} ($default_display): " >&2
        read -r value
        value="${value:-$default}"
        case $value in
            [Yy]* | true ) 
                echo -e "${GREEN}✓ Yes${NC}" >&2
                echo "true"
                break
                ;;
            [Nn]* | false ) 
                echo -e "${BLUE}✓ No${NC}" >&2
                echo "false"
                break
                ;;
            * ) 
                echo -e "${RED}Please answer yes (y) or no (n).${NC}" >&2
                ;;
        esac
    done
}

# Function to select from options with enhanced dropdown-style menu
# Now includes AI recommendation highlighting
select_option() {
    local prompt="$1"
    local default="$2"
    local recommendation_type="${3:-}"  # Optional: app_type, database, bundle, bucket
    shift 3 2>/dev/null || shift 2
    local options=("$@")
    
    if [[ "$AUTO_MODE" == "true" ]]; then
        # Return the actual option value at the default index (1-based)
        # Convert default index to 0-based and return the option
        local default_index=$((default - 1))
        if [ "$default_index" -ge 0 ] && [ "$default_index" -lt "${#options[@]}" ]; then
            echo "${options[$default_index]}"
        else
            echo "${options[0]}"
        fi
        return
    fi
    
    # Determine the AI-recommended option based on type
    local ai_recommended=""
    case "$recommendation_type" in
        "app_type")
            ai_recommended="$RECOMMENDED_APP_TYPE"
            ;;
        "database")
            ai_recommended="$RECOMMENDED_DATABASE"
            ;;
        "bundle")
            ai_recommended="$RECOMMENDED_BUNDLE"
            ;;
    esac
    
    # Use /dev/tty for direct terminal interaction
    exec 3</dev/tty
    
    # Display enhanced menu to terminal
    echo "" > /dev/tty
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────┐${NC}" > /dev/tty
    echo -e "${BLUE}│${NC} ${YELLOW}$prompt${NC}" > /dev/tty
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────┤${NC}" > /dev/tty
    
    for i in "${!options[@]}"; do
        local option="${options[i]}"
        local marker="  "
        local color=""
        local ai_marker=""
        
        # Check if this is the AI-recommended option
        if [ -n "$ai_recommended" ] && [ "$option" == "$ai_recommended" ]; then
            ai_marker=" ${YELLOW}★ AI${NC}"
            # Update default to AI recommendation
            default=$((i+1))
        fi
        
        # Mark default option (which may now be the AI recommendation)
        if [ "$((i+1))" -eq "$default" ]; then
            marker="→ "
            color="${GREEN}"
        fi
        
        # Get description for known options
        local desc=""
        desc=$(get_option_description "$option")
        
        if [ -n "$desc" ]; then
            if [ -n "$ai_marker" ]; then
                printf "${BLUE}│${NC} %s${color}%2d. %-12s${NC} │ %-27s${ai_marker} ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" "$desc" > /dev/tty
            else
                printf "${BLUE}│${NC} %s${color}%2d. %-12s${NC} │ %-35s ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" "$desc" > /dev/tty
            fi
        else
            if [ -n "$ai_marker" ]; then
                printf "${BLUE}│${NC} %s${color}%2d. %-44s${NC}${ai_marker} ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" > /dev/tty
            else
                printf "${BLUE}│${NC} %s${color}%2d. %-52s${NC} ${BLUE}│${NC}\n" "$marker" "$((i+1))" "$option" > /dev/tty
            fi
        fi
    done
    
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────┘${NC}" > /dev/tty
    echo "" > /dev/tty
    
    while true; do
        echo -ne "${YELLOW}Select option [1-${#options[@]}]${NC} (default: ${GREEN}$default${NC}): " > /dev/tty
        read -u 3 choice
        choice="${choice:-$default}"
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
            local selected="${options[$((choice-1))]}"
            echo -e "${GREEN}✓ Selected: $selected${NC}" > /dev/tty
            echo "$selected"
            break
        else
            echo -e "${RED}Invalid choice. Please select 1-${#options[@]}.${NC}" > /dev/tty
        fi
    done
    
    exec 3<&-
}

# Function to get description for known options
get_option_description() {
    local option="$1"
    
    case "$option" in
        # Application types
        "lamp")
            echo "Linux, Apache, MySQL, PHP stack"
            ;;
        "nodejs")
            echo "Node.js with Express.js"
            ;;
        "python")
            echo "Python with Flask framework"
            ;;
        "react")
            echo "React single-page application"
            ;;
        "docker")
            echo "Multi-container Docker app"
            ;;
        "nginx")
            echo "Static site with Nginx server"
            ;;
        
        # Database types
        "mysql")
            echo "MySQL relational database"
            ;;
        "postgresql")
            echo "PostgreSQL advanced database"
            ;;
        "mongodb")
            echo "MongoDB NoSQL database (local)"
            ;;
        "none")
            echo "No database required"
            ;;
        
        # Instance bundles
        "nano_3_0")
            echo "512MB RAM, 0.25 vCPU - \$3.50/mo"
            ;;
        "micro_3_0")
            echo "1GB RAM, 0.5 vCPU - \$5/mo"
            ;;
        "small_3_0")
            echo "2GB RAM, 1 vCPU - \$10/mo"
            ;;
        "medium_3_0")
            echo "4GB RAM, 2 vCPU - \$20/mo"
            ;;
        "large_3_0")
            echo "8GB RAM, 2 vCPU - \$40/mo"
            ;;
        
        # OS blueprints
        "ubuntu_22_04")
            echo "Ubuntu 22.04 LTS (Recommended)"
            ;;
        "ubuntu_24_04")
            echo "Ubuntu 24.04 LTS (Newest)"
            ;;
        "amazon_linux_2023")
            echo "Amazon Linux 2023"
            ;;
        
        # Bucket access levels
        "read_only")
            echo "Read-only access to bucket"
            ;;
        "read_write")
            echo "Full read/write access"
            ;;
        
        # Bucket bundles
        "small_1_0")
            echo "5GB storage - \$1/mo"
            ;;
        "medium_1_0")
            echo "100GB storage - \$3/mo"
            ;;
        "large_1_0")
            echo "250GB storage - \$5/mo"
            ;;
        
        *)
            echo ""
            ;;
    esac
}
