#!/bin/bash

# Function to create GitHub repository if needed
create_github_repo_if_needed() {
    local repo_name="$1"
    local repo_desc="$2"
    local visibility="$3"
    
    echo -e "${BLUE}Checking GitHub repository...${NC}"
    
    if gh repo view "$repo_name" &> /dev/null; then
        echo -e "${GREEN}✓ Repository already exists${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}Creating GitHub repository: $repo_name${NC}"
    gh repo create "$repo_name" --"$visibility" --description "$repo_desc" --source=. --remote=origin
    
    echo -e "${GREEN}✓ GitHub repository created${NC}"
}

# Function to setup workflow files
setup_workflow_files() {
    echo -e "${BLUE}Setting up workflow directory...${NC}"
    
    mkdir -p .github/workflows
    
    echo -e "${GREEN}✓ Workflow directory created${NC}"
}

# Function to commit and push changes
commit_and_push() {
    local app_type="$1"
    local app_name="$2"
    
    echo -e "${BLUE}Committing and pushing changes...${NC}"
    
    git add .
    git commit -m "Initial deployment setup for $app_name ($app_type)" || true
    git push -u origin main || git push -u origin master
    
    echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"
}

# Function to create .gitignore file
create_gitignore() {
    echo -e "${BLUE}Creating .gitignore file...${NC}"
    
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
vendor/
venv/
__pycache__/
*.pyc

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.egg-info/

# AWS
.aws-sam/

# Temporary files
*.tmp
*.temp
EOF
    
    echo -e "${GREEN}✓ .gitignore created${NC}"
}
