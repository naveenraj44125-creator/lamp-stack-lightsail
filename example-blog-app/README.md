# Modern Blog Application

A full-stack blog application built with Node.js, Express, and vanilla JavaScript with a modern UI.

## Features

- 📝 Create, read, update, and delete blog posts
- 🎨 Modern, responsive design
- 💾 JSON file-based storage (easily upgradeable to database)
- 🔍 Search functionality
- 📱 Mobile-friendly interface
- 🚀 Easy deployment to AWS Lightsail

## Technology Stack

- **Backend**: Node.js with Express
- **Frontend**: Vanilla JavaScript with modern CSS
- **Storage**: JSON files (can be upgraded to MongoDB/MySQL)
- **Deployment**: AWS Lightsail with GitHub Actions

## Local Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open your browser to `http://localhost:3000`

## API Endpoints

- `GET /api/posts` - Get all blog posts
- `GET /api/posts/:id` - Get a specific post
- `POST /api/posts` - Create a new post
- `PUT /api/posts/:id` - Update a post
- `DELETE /api/posts/:id` - Delete a post

## Deployment

This application is configured for automatic deployment to AWS Lightsail using GitHub Actions. The deployment includes:

- Node.js runtime setup
- PM2 process manager for production
- Nginx reverse proxy
- SSL certificate (optional)
- Automatic health checks

## Project Structure

```
example-blog-app/
├── public/           # Static files (HTML, CSS, JS)
├── data/            # JSON data storage
├── routes/          # Express routes
├── middleware/      # Custom middleware
├── package.json     # Dependencies and scripts
├── server.js        # Main application file
└── README.md        # This file
```

## Environment Variables

- `PORT` - Server port (default: 3000)
- `NODE_ENV` - Environment (development/production)
- `DATA_DIR` - Directory for data storage (default: ./data)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details