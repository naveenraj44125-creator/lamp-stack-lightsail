# Nginx Static Website Example

A modern, responsive static website deployed on AWS Lightsail using Nginx.

## Features

- ⚡ Lightning-fast static content delivery with Nginx
- 📱 Fully responsive design
- 🎨 Modern UI with CSS animations
- 🚀 Automated deployment with GitHub Actions
- 🔒 OIDC authentication for secure AWS access
- 🔥 Firewall configured for security

## Project Structure

```
example-nginx-app/
├── index.html              # Main HTML file
├── assets/
│   ├── css/
│   │   └── style.css      # Styles and animations
│   ├── js/
│   │   └── app.js         # Interactive features
│   └── images/            # Image assets
└── README.md              # This file
```

## Local Development

Simply open `index.html` in your browser:

```bash
cd example-nginx-app
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or just double-click the file
```

Or use a local server:

```bash
# Python
python3 -m http.server 8000

# Node.js
npx serve

# PHP
php -S localhost:8000
```

Then visit: http://localhost:8000

## Deployment

### Automatic Deployment

Push changes to the `main` branch:

```bash
git add example-nginx-app/
git commit -m "Update nginx site"
git push origin main
```

The GitHub Actions workflow will automatically:
1. ✅ Authenticate with AWS using OIDC
2. ✅ Package the application
3. ✅ Install Nginx and dependencies
4. ✅ Deploy files to `/var/www/html`
5. ✅ Configure Nginx
6. ✅ Restart services
7. ✅ Verify deployment

### Manual Deployment

```bash
# Package the application
cd example-nginx-app
tar -czf ../nginx-app.tar.gz .
cd ..

# Deploy
python workflows/deploy-post-steps-generic.py \
  --config-file deployment-nginx.config.yml \
  --package-file nginx-app.tar.gz \
  --verify \
  --cleanup
```

## Configuration

Edit `deployment-nginx.config.yml` to customize:

```yaml
application:
  name: "nginx-static-site"
  type: "static"
  deploy_path: "/var/www/html"

dependencies:
  nginx:
    enabled: true
    config:
      document_root: "/var/www/html"
      enable_gzip: true
      enable_caching: true
```

## Nginx Configuration

The deployment automatically configures Nginx with:

- **Gzip compression** for faster loading
- **Static asset caching** (1 year for images, CSS, JS)
- **Security headers** (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- **Custom error pages**
- **Access logging**

## Features Included

### 1. Responsive Navigation
- Sticky header
- Smooth scrolling
- Mobile-friendly menu

### 2. Hero Section
- Gradient background
- Call-to-action buttons
- Fade-in animations

### 3. Features Grid
- Auto-responsive layout
- Hover effects
- Icon-based cards

### 4. About Section
- Deployment information
- Server status checker
- Dynamic content

### 5. Contact Form
- Form validation
- Submission handling
- User feedback

## Customization

### Change Colors

Edit `assets/css/style.css`:

```css
:root {
    --primary-color: #2563eb;  /* Change to your brand color */
    --secondary-color: #7c3aed;
    --dark-bg: #1e293b;
}
```

### Add Pages

Create new HTML files:

```bash
touch example-nginx-app/about.html
touch example-nginx-app/services.html
```

### Add Images

Place images in `assets/images/`:

```bash
cp logo.png example-nginx-app/assets/images/
```

Then reference in HTML:

```html
<img src="assets/images/logo.png" alt="Logo">
```

## Performance

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Lighthouse Score**: 95+

## Security

- ✅ HTTPS ready (configure SSL certificates)
- ✅ Security headers enabled
- ✅ Firewall configured (ports 22, 80, 443)
- ✅ No server information disclosure

## Monitoring

Check deployment status:

```bash
# View workflow runs
gh run list

# Check specific run
gh run view <run-id>

# Check instance connectivity
./check-instance-connectivity.sh nginx-static-demo
```

## Troubleshooting

### Site Not Loading

1. Check instance status:
```bash
aws lightsail get-instance --instance-name nginx-static-demo --region us-east-1
```

2. Check Nginx status:
```bash
# Via browser-based SSH in Lightsail console
sudo systemctl status nginx
```

3. Check firewall:
```bash
sudo ufw status
```

### Deployment Fails

See `DEPLOYMENT-TROUBLESHOOTING.md` for common issues and solutions.

## Tech Stack

- **Web Server**: Nginx
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deployment**: GitHub Actions
- **Infrastructure**: AWS Lightsail
- **Authentication**: OIDC (OpenID Connect)

## License

MIT License - See LICENSE file for details
