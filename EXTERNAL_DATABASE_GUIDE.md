# External Database Configuration Guide

This guide explains how to configure external databases (AWS Lightsail RDS) instead of installing database servers locally on your Lightsail instance.

## 🎯 **Why Use External Databases?**

### **Benefits:**
- **Separation of concerns**: Database runs on dedicated infrastructure
- **Better performance**: RDS instances are optimized for databases
- **Easier scaling**: Scale database independently from application
- **Automated backups**: Built-in backup and restore capabilities
- **High availability**: Multi-AZ deployments for production
- **No server installation**: Saves resources on your Lightsail instance

### **When to Use:**
- ✅ Production applications requiring high availability
- ✅ Applications with large databases
- ✅ When you need automated backups
- ✅ When you want to scale database independently

### **When NOT to Use:**
- ❌ Development/testing environments (local is simpler)
- ❌ Small applications with minimal database needs
- ❌ When you want to minimize costs (local is cheaper)

## 📋 **Configuration Examples**

### **Example 1: External MySQL RDS Database**

```yaml
dependencies:
  mysql:
    enabled: true
    external: true  # ✅ This tells the system to use external RDS
    rds:
      database_name: "my-rds-instance"  # Name of your Lightsail RDS instance
      region: "us-east-1"
      access_key: "${AWS_ACCESS_KEY_ID}"     # GitHub Secret
      secret_key: "${AWS_SECRET_ACCESS_KEY}" # GitHub Secret
      master_database: "app_db"  # Database name within RDS
      environment:
        DB_CONNECTION_TIMEOUT: "30"
        DB_CHARSET: "utf8mb4"
```

**What happens:**
- ✅ Only MySQL **client** is installed (not the server)
- ✅ Connection details are retrieved from AWS
- ✅ Environment variables are configured automatically
- ✅ Connectivity is tested
- ❌ MySQL server is **NOT** installed locally

### **Example 2: Local MySQL Database**

```yaml
dependencies:
  mysql:
    enabled: true
    external: false  # ✅ This installs MySQL server locally
    config:
      create_app_database: true
      database_name: "app_db"
```

**What happens:**
- ✅ MySQL **server** is installed locally
- ✅ Database is created on the instance
- ✅ Local user accounts are configured
- ✅ Service is started and enabled

### **Example 3: External PostgreSQL RDS Database**

```yaml
dependencies:
  postgresql:
    enabled: true
    external: true  # ✅ Use external RDS
    rds:
      database_name: "my-postgres-rds"
      region: "us-east-1"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
      master_database: "app_db"
```

**What happens:**
- ✅ Only PostgreSQL **client** is installed
- ✅ Connection details retrieved from AWS
- ✅ Environment variables configured
- ❌ PostgreSQL server is **NOT** installed locally

## 🔧 **How It Works**

### **External Database Flow:**

```
1. Configuration Check
   ↓
2. Check if external: true
   ↓
3. Install ONLY database client (mysql-client or postgresql-client)
   ↓
4. Retrieve RDS connection details from AWS
   ↓
5. Test connectivity to RDS
   ↓
6. Create environment file with connection details
   ↓
7. Configure application to use external database
```

### **Local Database Flow:**

```
1. Configuration Check
   ↓
2. Check if external: false (or not set)
   ↓
3. Install database SERVER (mysql-server or postgresql)
   ↓
4. Start and enable service
   ↓
5. Create local database
   ↓
6. Configure local user accounts
   ↓
7. Set up application access
```

## 📝 **Environment Variables Created**

When using external databases, these environment variables are automatically created:

### **MySQL External:**
```bash
DB_TYPE=MYSQL
DB_HOST=your-rds-instance.region.rds.amazonaws.com
DB_PORT=3306
DB_NAME=app_db
DB_USERNAME=admin
DB_PASSWORD=***
DB_EXTERNAL=true
```

### **PostgreSQL External:**
```bash
DB_TYPE=POSTGRESQL
DB_HOST=your-rds-instance.region.rds.amazonaws.com
DB_PORT=5432
DB_NAME=app_db
DB_USERNAME=postgres
DB_PASSWORD=***
DB_EXTERNAL=true
```

### **Location:**
- Primary: `/opt/app/database.env`
- Symlink: `/var/www/html/.env` (for easy application access)

## 🚀 **Setup Steps**

### **Step 1: Create Lightsail RDS Database**

1. Go to AWS Lightsail Console
2. Click "Databases" → "Create database"
3. Choose database engine (MySQL or PostgreSQL)
4. Select a plan
5. Give it a name (e.g., "my-app-db")
6. Set master password
7. Create database

### **Step 2: Configure Deployment**

Update your `deployment-generic.config.yml`:

```yaml
dependencies:
  mysql:
    enabled: true
    external: true  # ✅ Enable external database
    rds:
      database_name: "my-app-db"  # ✅ Your RDS instance name
      region: "us-east-1"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
      master_database: "app_db"
```

### **Step 3: Set GitHub Secrets**

Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### **Step 4: Deploy**

Push your changes or run the deployment workflow. The system will:
1. Install only the database client
2. Connect to your RDS instance
3. Configure environment variables
4. Test connectivity

## 🔍 **Verification**

### **Check Installation:**

```bash
# SSH to your instance
ssh ubuntu@your-instance-ip

# Check if MySQL client is installed (not server)
mysql --version  # ✅ Should work
sudo systemctl status mysql  # ❌ Should fail (no server installed)

# Check environment file
cat /opt/app/database.env

# Test connection to RDS
mysql -h your-rds-endpoint -u admin -p
```

### **Check Logs:**

Look for these messages in your deployment logs:

```
🔗 Configuring external MYSQL RDS database...
📡 Retrieving RDS connection details for my-app-db...
📦 Installing mysql client...
✅ MySQL client installation completed
🔍 Testing database connectivity...
⚙️  Configuring environment variables...
✅ External MYSQL RDS database configured successfully
   Host: my-app-db.region.rds.amazonaws.com
   Port: 3306
   Database: app_db
   Username: admin
```

## ⚠️ **Common Issues**

### **Issue 1: MySQL server still being installed**

**Problem:** You see `mysql-server` being installed even with `external: true`

**Solution:** 
- Make sure `external: true` is set in your config
- Check that you're using the latest version of the deployment scripts
- Clear old logs and redeploy

### **Issue 2: Cannot connect to RDS**

**Problem:** Connectivity test fails

**Solutions:**
- Check RDS security group allows connections from Lightsail instance
- Verify RDS is in "Available" state
- Check RDS endpoint is correct
- Verify credentials are correct

### **Issue 3: Environment variables not set**

**Problem:** Application can't find database connection details

**Solutions:**
- Check `/opt/app/database.env` exists
- Verify symlink `/var/www/html/.env` points to database.env
- Check file permissions (should be 600)
- Source the environment file in your application

## 💡 **Best Practices**

1. **Use external databases for production**
   - Better performance and reliability
   - Automated backups
   - Easy scaling

2. **Use local databases for development**
   - Simpler setup
   - Lower costs
   - Faster iteration

3. **Secure your credentials**
   - Use GitHub Secrets for AWS credentials
   - Never commit credentials to git
   - Use environment variables in application

4. **Test connectivity**
   - Always verify database connection after deployment
   - Check application logs for connection errors
   - Test with a simple query

5. **Monitor your database**
   - Set up CloudWatch alarms for RDS
   - Monitor connection pool usage
   - Track query performance

## 📚 **Additional Resources**

- [AWS Lightsail RDS Documentation](https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-databases)
- [MySQL Client Documentation](https://dev.mysql.com/doc/refman/8.0/en/mysql.html)
- [PostgreSQL Client Documentation](https://www.postgresql.org/docs/current/app-psql.html)

## 🆘 **Need Help?**

If you encounter issues:
1. Check the deployment logs for error messages
2. Verify your RDS instance is running
3. Test connectivity manually from your instance
4. Check security group rules
5. Review the configuration file syntax