# MongoDB Task Manager

A simple task management application demonstrating MongoDB integration with Node.js and Express.

## Features

- ✅ Create, read, update, delete tasks
- 📊 Task statistics dashboard
- 🎨 Modern responsive UI
- 🔄 Real-time updates
- 🏷️ Priority levels (low, medium, high)
- ✓ Task completion tracking

## Tech Stack

- **Backend**: Node.js + Express
- **Database**: MongoDB
- **Frontend**: Vanilla JavaScript + CSS

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks |
| POST | `/api/tasks` | Create a new task |
| PUT | `/api/tasks/:id` | Update a task |
| DELETE | `/api/tasks/:id` | Delete a task |
| GET | `/api/stats` | Get task statistics |
| GET | `/api/health` | Health check |

## Environment Variables

```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/taskdb
```

## Local Development

```bash
# Install dependencies
npm install

# Start MongoDB (if not running)
sudo systemctl start mongod

# Run the app
npm start
```

## Deployment

This app is configured for deployment to AWS Lightsail using GitHub Actions.
The deployment will automatically:
1. Create a Lightsail instance
2. Install MongoDB locally on the instance
3. Deploy the application
4. Configure the database connection

## License

MIT
