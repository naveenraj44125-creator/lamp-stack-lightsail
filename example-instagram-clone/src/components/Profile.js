import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Settings, Grid, Bookmark, UserPlus, MessageCircle } from 'lucide-react';

const Profile = () => {
  const { username } = useParams();
  const { user } = useAuth();
  const [profileUser, setProfileUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [activeTab, setActiveTab] = useState('posts');
  const [isFollowing, setIsFollowing] = useState(false);
  const [loading, setLoading] = useState(true);

  // Mock user data
  const mockUsers = {
    'john_doe': {
      id: 1,
      username: 'john_doe',
      fullName: 'John Doe',
      bio: 'Photography enthusiast 📸\nTravel lover ✈️\nCoffee addict ☕',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
      followers: 1234,
      following: 567,
      postsCount: 89,
      isVerified: false
    },
    'jane_smith': {
      id: 2,
      username: 'jane_smith',
      fullName: 'Jane Smith',
      bio: 'Digital artist 🎨\nNature lover 🌿\nDog mom 🐕',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
      followers: 2345,
      following: 432,
      postsCount: 156,
      isVerified: true
    }
  };

  // Mock posts data
  const mockPosts = [
    {
      id: 1,
      image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop',
      likes: 234,
      comments: 12
    },
    {
      id: 2,
      image: 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=400&fit=crop',
      likes: 189,
      comments: 8
    },
    {
      id: 3,
      image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=400&fit=crop',
      likes: 567,
      comments: 23
    },
    {
      id: 4,
      image: 'https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=400&h=400&fit=crop',
      likes: 345,
      comments: 15
    },
    {
      id: 5,
      image: 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=400&h=400&fit=crop',
      likes: 678,
      comments: 34
    },
    {
      id: 6,
      image: 'https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=400&h=400&fit=crop',
      likes: 123,
      comments: 7
    }
  ];

  useEffect(() => {
    // Simulate loading profile data
    setLoading(true);
    setTimeout(() => {
      const profile = mockUsers[username] || {
        id: 999,
        username: username,
        fullName: username.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        bio: 'Welcome to my profile!',
        avatar: `https://ui-avatars.com/api/?name=${username}&size=150&background=0095f6&color=fff`,
        followers: Math.floor(Math.random() * 1000),
        following: Math.floor(Math.random() * 500),
        postsCount: mockPosts.length,
        isVerified: false
      };
      
      setProfileUser(profile);
      setPosts(mockPosts);
      setIsFollowing(Math.random() > 0.5);
      setLoading(false);
    }, 500);
  }, [username]);

  const handleFollow = () => {
    setIsFollowing(!isFollowing);
    // In a real app, this would make an API call
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (loading) {
    return (
      <div className="profile-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!profileUser) {
    return (
      <div className="profile-not-found">
        <h2>User not found</h2>
        <p>The user you're looking for doesn't exist.</p>
      </div>
    );
  }

  const isOwnProfile = user && user.username === username;

  return (
    <div className="profile">
      <div className="profile-header">
        <div className="profile-avatar">
          <img src={profileUser.avatar} alt={profileUser.fullName} />
        </div>
        
        <div className="profile-info">
          <div className="profile-username">
            <h1>{profileUser.username}</h1>
            {profileUser.isVerified && <span className="verified-badge">✓</span>}
            {isOwnProfile ? (
              <button className="profile-edit-btn">
                <Settings size={16} />
              </button>
            ) : (
              <div className="profile-actions">
                <button 
                  className={`follow-btn ${isFollowing ? 'following' : ''}`}
                  onClick={handleFollow}
                >
                  {isFollowing ? 'Following' : 'Follow'}
                </button>
                <button className="message-btn">
                  <MessageCircle size={16} />
                </button>
                <button className="more-btn">
                  <UserPlus size={16} />
                </button>
              </div>
            )}
          </div>
          
          <div className="profile-stats">
            <div className="stat">
              <span className="stat-number">{formatNumber(profileUser.postsCount)}</span>
              <span className="stat-label">posts</span>
            </div>
            <div className="stat">
              <span className="stat-number">{formatNumber(profileUser.followers)}</span>
              <span className="stat-label">followers</span>
            </div>
            <div className="stat">
              <span className="stat-number">{formatNumber(profileUser.following)}</span>
              <span className="stat-label">following</span>
            </div>
          </div>
          
          <div className="profile-bio">
            <div className="profile-name">{profileUser.fullName}</div>
            <div className="profile-description">
              {profileUser.bio.split('\n').map((line, index) => (
                <div key={index}>{line}</div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="profile-tabs">
        <button 
          className={`tab ${activeTab === 'posts' ? 'active' : ''}`}
          onClick={() => setActiveTab('posts')}
        >
          <Grid size={12} />
          <span>POSTS</span>
        </button>
        <button 
          className={`tab ${activeTab === 'saved' ? 'active' : ''}`}
          onClick={() => setActiveTab('saved')}
        >
          <Bookmark size={12} />
          <span>SAVED</span>
        </button>
      </div>

      <div className="profile-content">
        {activeTab === 'posts' && (
          <div className="posts-grid">
            {posts.length > 0 ? (
              posts.map(post => (
                <div key={post.id} className="post-thumbnail">
                  <img src={post.image} alt="Post" />
                  <div className="post-overlay">
                    <div className="post-stats">
                      <span>❤️ {formatNumber(post.likes)}</span>
                      <span>💬 {formatNumber(post.comments)}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-posts">
                <div className="no-posts-icon">📷</div>
                <h3>No Posts Yet</h3>
                <p>When {isOwnProfile ? 'you' : profileUser.username} shares photos, they'll appear here.</p>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'saved' && (
          <div className="saved-posts">
            <div className="no-posts">
              <div className="no-posts-icon">🔖</div>
              <h3>No Saved Posts</h3>
              <p>Save posts to see them here.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
