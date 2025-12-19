# Fix Node.js Application Override Issue - Add Custom Deployment Support

## 🚨 **Critical Problem Solved**

The deployment system was creating **generic Node.js applications that completely override custom applications**, causing:

1. **Custom applications get replaced** - Reddit Clone's custom interface gets overwritten with generic HTML
2. **API endpoints stop working** - `/api/subreddits`, `/health` return "Cannot GET" errors  
3. **PM2 configurations ignored** - systemd services override PM2 process management
4. **No customization possible** - all Node.js apps get the same generic treatment

## 🔧 **Solution Overview**

This PR adds **conditional Node.js configuration** that allows applications to:
- ✅ Skip automatic systemd service creation
- ✅ Install Node.js dependencies only (minimal mode)
- ✅ Run custom post-deployment scripts
- ✅ Use PM2 or other process managers without conflicts
- ✅ Maintain backward compatibility with existing deployments

## 📋 **Changes Made**

### 1. **Config Loader Enhancement** (`workflows/config_loader.py`)
Added methods to support custom deployment configurations:
- `should_skip_nodejs_configurator()` - Check if Node.js configurator should be skipped
- `get_pm2_post_setup_script()` - Get custom PM2 post-setup script path
- `should_create_generic_files()` - Check if generic files should be created

### 2. **Configurator Factory Update** (`workflows/app_configurators/configurator_factory.py`)
Added conditional logic to use minimal Node.js configurator when requested:
- Checks `skip_configurator` flag in configuration
- Uses `NodeJSMinimalConfigurator` for custom applications
- Maintains full backward compatibility

### 3. **Minimal Node.js Configurator** (`workflows/app_configurators/nodejs_configurator.py`)
Added `NodeJSMinimalConfigurator` class that:
- Installs Node.js dependencies (`npm install`)
- Sets proper file permissions
- Creates log directories
- **Skips systemd service creation** to prevent PM2 conflicts

### 4. **Post-Deployment Script Support** (`workflows/deploy-post-steps-generic.py`)
Added PM2 post-setup script execution:
- `_run_pm2_post_setup_script()` method executes custom scripts
- Integrated into deployment workflow after application configuration
- Proper error handling and timeout protection

## 🧪 **Configuration Example**

Applications can now use this configuration to enable custom deployment:

```yaml
application:
  name: "Reddit Clone"
  type: nodejs
  skip_generic_files: true

dependencies:
  nodejs:
    enabled: true
    config:
      skip_configurator: true
  pm2:
    enabled: true
    config:
      post_setup_script: "./reddit-post-deploy.sh"
```

## ✅ **Benefits**

1. **Fixes Reddit Clone deployment** - Custom interface preserved, API endpoints work
2. **Enables PM2 management** - No more systemd conflicts
3. **Supports custom scripts** - Applications can configure themselves properly
4. **Backward compatible** - Existing deployments continue to work unchanged
5. **Flexible deployment** - Applications choose minimal or full configuration

## 🔄 **Backward Compatibility**

- All existing configurations continue to work exactly as before
- `skip_configurator` defaults to `False` (full configuration)
- No breaking changes to existing deployment workflows
- Generic applications still get full systemd service setup

## 🎯 **Impact**

This change enables proper deployment of complex Node.js applications like:
- Reddit Clone with custom API endpoints
- Applications using PM2 process management
- Custom applications with their own startup scripts
- Applications that need specific configuration sequences

The deployment system now supports both **generic applications** (with automatic configuration) and **custom applications** (with manual configuration control).