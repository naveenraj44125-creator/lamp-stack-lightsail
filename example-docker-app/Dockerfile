# Use official PHP Apache image - pre-built and optimized
FROM php:8.1-apache

# Install only required PHP extensions (much faster than Ubuntu base)
RUN docker-php-ext-install pdo pdo_mysql mysqli \
    && pecl install redis \
    && docker-php-ext-enable redis

# Enable Apache modules
RUN a2enmod rewrite headers

# Configure PHP (use php.ini-production as base)
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" \
    && echo "upload_max_filesize = 50M" >> "$PHP_INI_DIR/php.ini" \
    && echo "post_max_size = 50M" >> "$PHP_INI_DIR/php.ini" \
    && echo "memory_limit = 256M" >> "$PHP_INI_DIR/php.ini"

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY src/ /var/www/html/

# Create directories and set permissions in one layer
RUN mkdir -p uploads cache logs \
    && chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Expose port
EXPOSE 80

# Apache is already configured to run in foreground in base image
