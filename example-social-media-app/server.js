#!/usr/bin/env node

/**
 * Main entry point for Employee Social App
 * This file serves as the root entry point that the deployment system expects
 * and delegates to the actual server implementation in the backend directory
 */

console.log('🚀 Starting Employee Social App...');
console.log('📁 Entry point: server.js -> backend/server.js');
console.log('🌍 Environment:', process.env.NODE_ENV || 'development');
console.log('🔌 Port:', process.env.PORT || 3000);

// Require the actual server implementation
require('./backend/server.js');