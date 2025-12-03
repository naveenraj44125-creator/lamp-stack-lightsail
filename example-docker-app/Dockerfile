FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Apache + PHP
RUN apt-get update && apt-get install -y \
    apache2 \
    php8.1 \
    php8.1-apache2 \
    php8.1-mysql \
    php8.1-pgsql \
    php8.1-redis \
    php8.1-curl \
    php8.1-json \
    php8.1-mbstring \
    php8.1-xml \
    php8.1-zip \
    php8.1-gd \
    php8.1-intl \
    php8.1-bcmath \
    curl \
    wget \
    unzip \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite ssl headers proxy proxy_http

# Configure Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY src/ /var/www/html/

# Create necessary directories
RUN mkdir -p /var/www/html/uploads /var/www/html/cache /var/www/html/logs

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html \
    && chmod -R 775 /var/www/html/uploads \
    && chmod -R 775 /var/www/html/cache \
    && chmod -R 775 /var/www/html/logs

# Configure PHP
RUN echo "upload_max_filesize = 50M" >> /etc/php/8.1/apache2/php.ini \
    && echo "post_max_size = 50M" >> /etc/php/8.1/apache2/php.ini \
    && echo "memory_limit = 256M" >> /etc/php/8.1/apache2/php.ini \
    && echo "max_execution_time = 300" >> /etc/php/8.1/apache2/php.ini \
    && echo "display_errors = Off" >> /etc/php/8.1/apache2/php.ini \
    && echo "log_errors = On" >> /etc/php/8.1/apache2/php.ini \
    && echo "error_log = /var/www/html/logs/php_errors.log" >> /etc/php/8.1/apache2/php.ini

# Create Apache virtual host configuration
RUN echo '<VirtualHost *:80>' > /etc/apache2/sites-available/000-default.conf && \
    echo '    ServerAdmin webmaster@localhost' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    DocumentRoot /var/www/html' >> /etc/apache2/sites-available/000-default.conf && \
    echo '' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    <Directory /var/www/html>' >> /etc/apache2/sites-available/000-default.conf && \
    echo '        Options Indexes FollowSymLinks' >> /etc/apache2/sites-available/000-default.conf && \
    echo '        AllowOverride All' >> /etc/apache2/sites-available/000-default.conf && \
    echo '        Require all granted' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    </Directory>' >> /etc/apache2/sites-available/000-default.conf && \
    echo '' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    ErrorLog ${APACHE_LOG_DIR}/error.log' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    CustomLog ${APACHE_LOG_DIR}/access.log combined' >> /etc/apache2/sites-available/000-default.conf && \
    echo '</VirtualHost>' >> /etc/apache2/sites-available/000-default.conf

# Health check script
RUN echo '<?php http_response_code(200); echo "OK"; ?>' > /var/www/html/health.php

# Expose ports
EXPOSE 80 443

# Start Apache in foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]
