#!/bin/bash
set -e

# Fix any broken packages first
echo "Fixing any broken packages..."
sudo dpkg --configure -a
sudo apt-get -f install -y

# Update system
echo "Updating system packages..."
sudo apt-get update -y

# Check if Apache is already installed
if ! command -v apache2 &> /dev/null; then
    echo "Installing Apache..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y apache2
else
    echo "Apache already installed"
fi

# Check if MySQL is already installed
if ! command -v mysql &> /dev/null; then
    echo "Installing MariaDB (lighter alternative to MySQL)..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server mariadb-client
else
    echo "MySQL/MariaDB already installed"
fi

# Check if PHP is already installed
if ! command -v php &> /dev/null; then
    echo "Installing PHP and extensions..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y php php-mysql php-cli php-curl php-json php-mbstring php-xml php-zip
else
    echo "PHP already installed"
fi

# Start and enable services
echo "Starting services..."
sudo systemctl start apache2 || echo "Apache already running"
sudo systemctl enable apache2
sudo systemctl start mysql || echo "MySQL already running"
sudo systemctl enable mysql

# Configure Apache
echo "Configuring Apache..."
sudo a2enmod rewrite || echo "Rewrite module already enabled"
sudo systemctl restart apache2

# Set up web directory permissions
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

echo "✅ LAMP stack installation completed"
