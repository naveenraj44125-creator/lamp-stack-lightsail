#!/usr/bin/env python3
"""
Test database configuration logic to identify the issue
"""
import os

def load_env_file():
    """Load .env file and return environment variables"""
    env_vars = {}
    env_file = '.env'
    
    if os.path.exists(env_file):
        print(f"✅ Found .env file: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        print(f"📋 Loaded {len(env_vars)} environment variables")
    else:
        print(f"❌ .env file not found: {env_file}")
    
    return env_vars

def test_database_logic():
    """Test the database configuration logic"""
    print("🔍 Testing Database Configuration Logic")
    print("=" * 50)
    
    # Load environment variables
    env_vars = load_env_file()
    
    print("\n📋 Environment Variables:")
    for key, value in env_vars.items():
        if 'PASSWORD' in key:
            print(f"  {key} = {'*' * len(value)}")
        else:
            print(f"  {key} = {value}")
    
    # Check the critical DB_EXTERNAL variable
    print(f"\n🔑 Critical Check - DB_EXTERNAL:")
    db_external = env_vars.get('DB_EXTERNAL', 'NOT SET')
    print(f"  DB_EXTERNAL = {db_external}")
    
    # Simulate PHP logic
    is_external_db = db_external == 'true'
    print(f"  is_external_db = {is_external_db}")
    
    if is_external_db:
        print("\n✅ Would use RDS Configuration:")
        print(f"  DB_HOST = {env_vars.get('DB_HOST', 'localhost')}")
        print(f"  DB_NAME = {env_vars.get('DB_DATABASE', 'app_db')}")
        print(f"  DB_USER = {env_vars.get('DB_USERNAME', 'root')}")
        print(f"  DB_PORT = {env_vars.get('DB_PORT', '3306')}")
        print(f"  DB_TYPE = {env_vars.get('DB_TYPE', 'MYSQL')}")
        print(f"  DB_EXTERNAL = true")
    else:
        print("\n❌ Would use Local Configuration:")
        print(f"  DB_HOST = localhost")
        print(f"  DB_NAME = app_db")
        print(f"  DB_USER = root")
        print(f"  DB_PORT = 3306")
        print(f"  DB_TYPE = MYSQL")
        print(f"  DB_EXTERNAL = false")
    
    print(f"\n🎯 ISSUE IDENTIFIED:")
    if not is_external_db:
        print(f"  The .env file is missing 'DB_EXTERNAL=true'")
        print(f"  This causes the application to use local database configuration")
        print(f"  instead of the RDS configuration.")
    else:
        print(f"  Configuration looks correct for RDS usage.")

if __name__ == "__main__":
    test_database_logic()
