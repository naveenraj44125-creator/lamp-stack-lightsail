#!/bin/bash

# Test Suite for Smart Recommendations
# Tests project analysis and intelligent recommendations

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Smart Recommendations Test Suite                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Source modules
source setup/00-variables.sh
source setup/01-utils.sh
source setup/03-project-analysis.sh

# Helper function
verify() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"
    
    if [[ "$actual" == "$expected" ]]; then
        echo -e "  ${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗${NC} $test_name"
        echo -e "    Expected: $expected"
        echo -e "    Got: $actual"
        ((TESTS_FAILED++))
    fi
}

# Create test projects
mkdir -p test-projects/fullstack
mkdir -p test-projects/python-api
mkdir -p test-projects/php-app
mkdir -p test-projects/docker-app

# Test 1: Fullstack Node.js + React with MySQL and file uploads
echo -e "${CYAN}Test 1: Fullstack Node.js + React${NC}"
cat > test-projects/fullstack/package.json << 'EOF'
{
  "dependencies": {
    "react": "^18.0.0",
    "express": "^4.18.0",
    "mysql2": "^3.0.0",
    "multer": "^1.4.5"
  }
}
EOF

cat > test-projects/fullstack/server.js << 'EOF'
const express = require('express');
const app = express();

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(3000);
EOF

cd test-projects/fullstack
analyze_project_for_recommendations . > /dev/null 2>&1
verify "App type detected" "nodejs" "$RECOMMENDED_APP_TYPE"
verify "Database detected" "mysql" "$RECOMMENDED_DATABASE"
verify "Bucket recommended" "true" "$RECOMMENDED_BUCKET"
verify "Health endpoint detected" "/api/health" "$RECOMMENDED_HEALTH_ENDPOINT"
verify "Instance size" "small_3_0" "$RECOMMENDED_BUNDLE"
cd ../..
echo ""

# Test 2: Python Flask with PostgreSQL
echo -e "${CYAN}Test 2: Python Flask API${NC}"
cat > test-projects/python-api/requirements.txt << 'EOF'
Flask==2.3.0
psycopg2-binary==2.9.0
Pillow==10.0.0
EOF

cat > test-projects/python-api/app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'ok'}
EOF

cd test-projects/python-api
analyze_project_for_recommendations . > /dev/null 2>&1
verify "App type detected" "python" "$RECOMMENDED_APP_TYPE"
verify "Database detected" "postgresql" "$RECOMMENDED_DATABASE"
verify "Bucket recommended" "true" "$RECOMMENDED_BUCKET"
verify "Health endpoint detected" "/health" "$RECOMMENDED_HEALTH_ENDPOINT"
cd ../..
echo ""

# Test 3: PHP Laravel
echo -e "${CYAN}Test 3: PHP Laravel${NC}"
cat > test-projects/php-app/composer.json << 'EOF'
{
  "require": {
    "laravel/framework": "^10.0",
    "intervention/image": "^2.7"
  }
}
EOF

cat > test-projects/php-app/health.php << 'EOF'
<?php
echo json_encode(['status' => 'ok']);
?>
EOF

cd test-projects/php-app
analyze_project_for_recommendations . > /dev/null 2>&1
verify "App type detected" "lamp" "$RECOMMENDED_APP_TYPE"
verify "Database detected" "mysql" "$RECOMMENDED_DATABASE"
verify "Bucket recommended" "true" "$RECOMMENDED_BUCKET"
verify "Health endpoint detected" "/health.php" "$RECOMMENDED_HEALTH_ENDPOINT"
cd ../..
echo ""

# Test 4: Docker with MySQL
echo -e "${CYAN}Test 4: Docker Application${NC}"
cat > test-projects/docker-app/docker-compose.yml << 'EOF'
version: '3'
services:
  app:
    build: .
  db:
    image: mysql:8.0
  volumes:
    - ./uploads:/app/uploads
EOF

cat > test-projects/docker-app/Dockerfile << 'EOF'
FROM node:18
WORKDIR /app
HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000/healthcheck || exit 1
CMD ["node", "server.js"]
EOF

cd test-projects/docker-app
analyze_project_for_recommendations . > /dev/null 2>&1
verify "App type detected" "docker" "$RECOMMENDED_APP_TYPE"
verify "Database detected" "mysql" "$RECOMMENDED_DATABASE"
verify "Bucket recommended" "true" "$RECOMMENDED_BUCKET"
verify "Health endpoint detected" "/healthcheck" "$RECOMMENDED_HEALTH_ENDPOINT"
verify "Instance size" "medium_3_0" "$RECOMMENDED_BUNDLE"
cd ../..
echo ""

# Cleanup
rm -rf test-projects

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Results Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "  Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ ALL TESTS PASSED                                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ✗ SOME TESTS FAILED                                      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
