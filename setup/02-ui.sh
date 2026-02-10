#!/bin/bash

# Function to get user input with default value (enhanced styling)
get_input() {
    local prompt="$1"
    local default="$2"
    local value
    
    # Use /dev/tty for direct terminal interaction
    if [[ -n "$default" ]]; then
        echo -e "${BLUE}${prompt}${NC} ${YELLOW}[${default}]${NC}: " >&2
        read -r value < /dev/tty
        echo "${value:-$default}"
    else
        echo -e "${BLUE}${prompt}${NC}: " >&2
        read -r value < /dev/tty
        echo "$value"
    fi
}

# Function to get yes/no input (enhanced styling)
get_yes_no() {
    local prompt="$1"
    local default="$2"
    local value
    
    # Use /dev/tty for direct terminal interaction
    if [[ "$default" == "true" ]]; then
        echo -e "${BLUE}${prompt}${NC} ${YELLOW}[Y/n]${NC}: " >&2
        read -r value < /dev/tty
        value=$(to_lowercase "${value:-y}")
        [[ "$value" == "y" || "$value" == "yes" ]] && echo "true" || echo "false"
    else
        echo -e "${BLUE}${prompt}${NC} ${YELLOW}[y/N]${NC}: " >&2
        read -r value < /dev/tty
        value=$(to_lowercase "${value:-n}")
        [[ "$value" == "y" || "$value" == "yes" ]] && echo "true" || echo "false"
    fi
}

# Function to select from options with enhanced dropdown-style menu
# Now includes AI recommendation highlighting
select_option() {
    local prompt="$1"
    local default="$2"
    local recommendation_type="$3"  # "app_type", "database", "bundle", etc.
    shift 3
    local options=("$@")
    
    # Determine AI recommended option based on type
    local ai_recommended=""
    case $recommendation_type in
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
    
    echo "" >&2
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
    echo -e "${BLUE}${prompt}${NC}" >&2
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
    echo "" >&2
    
    local i=1
    for option in "${options[@]}"; do
        local marker="  "
        local color="${NC}"
        
        # Highlight AI recommendation
        if [[ -n "$ai_recommended" && "$option" == "$ai_recommended" ]]; then
            marker="★ "
            color="${GREEN}"
            echo -e "${color}${marker}${i}) ${option} ${YELLOW}(AI Recommended)${NC}" >&2
        elif [[ "$option" == "$default" ]]; then
            marker="→ "
            echo -e "${CYAN}${marker}${i}) ${option} ${YELLOW}(default)${NC}" >&2
        else
            echo -e "  ${i}) ${option}" >&2
        fi
        ((i++))
    done
    
    echo "" >&2
    echo -e "${BLUE}Enter choice [1-${#options[@]}]${NC} ${YELLOW}[default: $(for j in "${!options[@]}"; do [[ "${options[$j]}" == "$default" ]] && echo $((j+1)); done)]${NC}: " >&2
    
    local choice
    read -r choice < /dev/tty
    
    if [[ -z "$choice" ]]; then
        echo "$default"
        return
    fi
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
        echo "${options[$((choice-1))]}"
    else
        echo -e "${RED}Invalid choice. Using default: $default${NC}" >&2
        echo "$default"
    fi
}

# Function to get description for known options
get_option_description() {
    local option="$1"
    
    case $option in
        "lamp")
            echo "Linux, Apache, MySQL, PHP stack"
            ;;
        "nodejs")
            echo "Node.js with Express framework"
            ;;
        "python")
            echo "Python with Flask/Django"
            ;;
        "docker")
            echo "Containerized application"
            ;;
        "react")
            echo "React frontend application"
            ;;
        "mysql")
            echo "MySQL relational database"
            ;;
        "postgresql")
            echo "PostgreSQL relational database"
            ;;
        "none")
            echo "No database required"
            ;;
        *)
            echo "$option"
            ;;
    esac
}
