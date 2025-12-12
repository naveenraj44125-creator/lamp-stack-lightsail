# 📸 Instagram Clone - React Social Media App

A fully functional Instagram-like social media application built with React, featuring user authentication, photo sharing, social feeds, user profiles, and real-time interactions.

> **Note**: This is a local example based on the original repository at `https://github.com/naveenraj44125-creator/instagram-clone` with added deployment configuration and GitHub Actions integration for AWS Lightsail.

## 🌟 Features

- **User Authentication**: Login and registration with mock authentication system
- **Photo Sharing**: Upload and share photos with captions
- **Social Feed**: Browse posts from other users with infinite scroll
- **User Profiles**: View user profiles with post grids and statistics
- **Interactive Features**: Like and comment on posts
- **Responsive Design**: Mobile-first design that works on all devices
- **Real-time Updates**: Dynamic like and comment interactions

## 🛠️ Tech Stack

- **Frontend**: React 18 with functional components and hooks
- **Routing**: React Router for navigation
- **State Management**: React Context API for authentication
- **Styling**: Custom CSS with Instagram-like design
- **Icons**: Lucide React for beautiful icons
- **Date Handling**: date-fns for time formatting
- **Build Tool**: Create React App

## 🚀 Quick Start

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/naveenraj44125-creator/instagram-clone.git
   cd instagram-clone
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000` (or the port shown in terminal)

### Demo Accounts

For testing, you can use these demo credentials:
- **Email**: demo@example.com
- **Password**: password123

Or register a new account with any email and password.

## 📱 Application Structure

```
src/
├── components/
│   ├── Header.js          # Navigation header
│   ├── Login.js           # Login form
│   ├── Register.js        # Registration form
│   ├── Feed.js            # Main feed with posts
│   ├── CreatePost.js      # Post creation form
│   └── Profile.js         # User profile page
├── contexts/
│   └── AuthContext.js     # Authentication context
├── App.js                 # Main app component
├── App.css                # Global styles
└── index.js               # App entry point
```

## 🎨 Key Components

### Authentication System
- Mock authentication with localStorage persistence
- Protected routes for authenticated users
- Login/Register forms with validation

### Feed Component
- Displays posts in Instagram-like cards
- Like and comment functionality
- Real-time interaction updates
- Responsive post layout

### Profile Component
- User information display
- Post grid layout
- Follow/Following functionality
- Statistics (posts, followers, following)

### Create Post Component
- Image upload with preview
- Caption input with character limit
- File validation and error handling
- Mock post creation

## 🚀 Deployment to AWS Lightsail

This project includes automated deployment to AWS Lightsail with GitHub Actions integration:

### 🏗️ Deployment Architecture

- **Infrastructure**: Ubuntu 22.04 on small instance (2GB RAM, 1 vCPU)
- **Web Server**: Nginx serving React build files
- **Storage**: S3-compatible Lightsail bucket for image uploads
- **CI/CD**: GitHub Actions for automated deployment
- **Application Type**: React SPA with Express.js server for production

### 📋 Deployment Configuration

The deployment uses `deployment-instagram-clone.config.yml` with:

```yaml
application:
  name: instagram-clone
  type: react
  
lightsail:
  instance_name: instagram-clone-instance-1
  bundle_id: small_3_0  # 2GB RAM, 1 vCPU
  blueprint_id: ubuntu_22_04
  
  bucket:
    enabled: true
    name: instagram-clone-bucket
    access_level: read_write
```

### 🔄 GitHub Actions Workflow

The deployment is automated with `.github/workflows/deploy-instagram-clone.yml`:

1. **Test Phase**: 
   - Install dependencies
   - Run React tests
   - Build production bundle
   - Verify build output

2. **Deploy Phase**:
   - Deploy to Lightsail instance
   - Configure Nginx for SPA routing
   - Set up health checks

3. **Verification**:
   - Test application endpoints
   - Verify React app loads correctly
   - Check responsive design

### 🚀 Quick Deployment

1. **Fork this repository**
2. **Configure AWS credentials** in GitHub Secrets
3. **Push to main branch** - deployment starts automatically
4. **Access your app** at the provided Lightsail URL

### 🔧 Local Development vs Production

**Development Mode** (`npm run dev`):
- React development server on port 3000
- Hot reloading enabled
- Development build with source maps

**Production Mode** (`npm start`):
- Express server serves React build
- Optimized production bundle
- API endpoints for health checks
- SPA routing support

## 🔧 Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **Styling**: Update `src/App.css` or create component-specific CSS
3. **State Management**: Use Context API or add new contexts
4. **Routing**: Update routes in `src/App.js`

### Mock Data

The app uses mock data for demonstration:
- User profiles in `Profile.js`
- Posts in `Feed.js`
- Authentication in `AuthContext.js`

For production, replace with real API calls.

## 🎯 Future Enhancements

- **Real Backend**: Replace mock data with actual API
- **Database Integration**: Add PostgreSQL or MongoDB
- **Real Authentication**: Implement JWT or OAuth
- **Image Storage**: Integrate with AWS S3 or Cloudinary
- **Push Notifications**: Real-time notifications
- **Stories Feature**: Instagram-like stories
- **Direct Messaging**: Private messaging system
- **Advanced Search**: Search users and posts
- **Content Moderation**: Automated content filtering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Instagram for design inspiration
- React team for the amazing framework
- Lucide React for beautiful icons
- Create React App for the build setup

## 📞 Support

If you have any questions or need help with deployment:

1. Check the [Issues](https://github.com/naveenraj44125-creator/instagram-clone/issues) page
2. Create a new issue with detailed description
3. Include error messages and system information

---

**Built with ❤️ using React and deployed on AWS Lightsail**
