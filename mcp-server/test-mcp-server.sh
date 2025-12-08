#!/bin/bash

# Test script for MCP Server deployed on Lightsail
# Server URL: http://52.202.252.239:3000

SERVER_URL="http://52.202.252.239:3000"

echo "🧪 Testing MCP Server on Lightsail"
echo "=================================="
echo ""

# Test 1: Health Check
echo "1️⃣  Health Check:"
curl -s "$SERVER_URL/health" | jq '.'
echo ""
echo ""

# Test 2: List Available Tools
echo "2️⃣  Listing Available MCP Tools:"
curl -s -X POST "$SERVER_URL/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' | jq '.'
echo ""
echo ""

# Test 3: Get Server Info
echo "3️⃣  Getting Server Information:"
curl -s -X POST "$SERVER_URL/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }' | jq '.'
echo ""
echo ""

echo "✅ Testing complete!"
echo ""
echo "📝 To use this MCP server in your application:"
echo "   Server URL: $SERVER_URL"
echo "   SSE Endpoint: $SERVER_URL/sse"
echo "   Message Endpoint: $SERVER_URL/message"
