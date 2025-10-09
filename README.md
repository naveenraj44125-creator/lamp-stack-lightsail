# LAMP Stack Application

A simple LAMP (Linux, Apache, MySQL, PHP) stack application that displays "Hello Welcome!" message.

## Features

- **Welcome Message**: Displays "Hello Welcome!" with current date and time
- **System Information**: Shows PHP version, server details, and database status
- **Responsive Design**: Mobile-friendly CSS styling with animations
- **Database Integration**: Ready for MySQL/MariaDB connection
- **Modern UI**: Gradient backgrounds and clean design

## File Structure

```
lamp_stack_lightsail/
├── index.php              # Main application file
├── css/
│   └── style.css         # Stylesheet with responsive design
├── config/
│   └── database.php      # Database configuration and connection
└── README.md             # This documentation file
```

## Requirements

- **Linux** server (Ubuntu, CentOS, etc.)
- **Apache** web server
- **MySQL** or **MariaDB** database
- **PHP** 7.4 or higher with PDO extension

## Installation

1. **Copy files to web server**:
   ```bash
   cp -r lamp_stack_lightsail/ /var/www/html/
   ```

2. **Set proper permissions**:
   ```bash
   sudo chown -R www-data:www-data /var/www/html/lamp_stack_lightsail/
   sudo chmod -R 755 /var/www/html/lamp_stack_lightsail/
   ```

3. **Configure database** (optional):
   - Edit `config/database.php` with your MySQL/MariaDB credentials
   - Create database: `CREATE DATABASE lamp_app;`

4. **Access the application**:
   - Open browser and navigate to: `http://your-server-ip/lamp_stack_lightsail/`

## Configuration

### Database Settings

Edit `config/database.php` to match your database setup:

```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'lamp_app');
define('DB_USER', 'your_username');
define('DB_PASS', 'your_password');
```

### Apache Configuration

Ensure Apache is configured to serve PHP files:

```apache
<Directory /var/www/html>
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
```

## Features Explained

### Welcome Message
The main page displays a prominent "Hello Welcome!" message along with:
- Current date and time
- PHP version information
- Server details

### Database Status
The application automatically checks database connectivity and displays:
- ✅ Success message if connection works
- ❌ Error message if connection fails

### Responsive Design
The CSS includes:
- Mobile-friendly responsive layout
- Gradient backgrounds
- Smooth animations
- Clean typography

## Troubleshooting

### Common Issues

1. **PHP not working**:
   ```bash
   sudo apt update
   sudo apt install php libapache2-mod-php
   sudo systemctl restart apache2
   ```

2. **Database connection failed**:
   - Check MySQL/MariaDB is running: `sudo systemctl status mysql`
   - Verify credentials in `config/database.php`
   - Ensure database exists: `CREATE DATABASE lamp_app;`

3. **Permission errors**:
   ```bash
   sudo chown -R www-data:www-data /var/www/html/lamp_stack_lightsail/
   sudo chmod -R 755 /var/www/html/lamp_stack_lightsail/
   ```

4. **CSS not loading**:
   - Check file permissions
   - Verify Apache can serve static files
   - Check browser developer tools for 404 errors

## Development

To modify the application:

1. **Update welcome message**: Edit the PHP echo statements in `index.php`
2. **Change styling**: Modify `css/style.css`
3. **Add database features**: Use functions in `config/database.php`

## Security Notes

- Change default database credentials
- Use environment variables for sensitive data
- Enable HTTPS in production
- Keep PHP and Apache updated
- Implement proper input validation for user data

## License

This is a simple demo application for educational purposes.
