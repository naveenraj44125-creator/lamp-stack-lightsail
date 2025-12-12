import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Share, Bookmark } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useAuth } from '../contexts/AuthContext';

const Feed = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    // Simulate loading posts
    const loadPosts = () => {
      const mockPosts = [
        {
          id: '1',
          username: 'john_doe',
          userAvatar: 'JD',
          image: 'https://picsum.photos/600/600?random=1',
          caption: 'Beautiful sunset at the beach! 🌅 #sunset #beach #nature',
          likes: 42,
          comments: [
            { id: '1', username: 'jane_smith', text: 'Amazing shot!' },
            { id: '2', username: 'mike_wilson', text: 'Love the colors 🎨' }
          ],
          createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
          liked: false
        },
        {
          id: '2',
          username: 'travel_lover',
          userAvatar: 'TL',
          image: 'https://picsum.photos/600/600?random=2',
          caption: 'Exploring the mountains today! The view is incredible 🏔️ #mountains #hiking #adventure',
          likes: 128,
          comments: [
            { id: '3', username: 'outdoor_enthusiast', text: 'Which trail is this?' },
            { id: '4', username: 'nature_photographer', text: 'Perfect composition!' }
          ],
          createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 hours ago
          liked: true
        },
        {
          id: '3',
          username: 'foodie_adventures',
          userAvatar: 'FA',
          image: 'https://picsum.photos/600/600?random=3',
          caption: 'Homemade pasta night! 🍝 Recipe in my bio #pasta #cooking #homemade',
          likes: 89,
          comments: [
            { id: '5', username: 'chef_maria', text: 'Looks delicious!' },
            { id: '6', username: 'pasta_lover', text: 'Recipe please! 🙏' }
          ],
          createdAt: new Date(Date.now() - 8 * 60 * 60 * 1000), // 8 hours ago
          liked: false
        }
      ];
      
      setPosts(mockPosts);
      setLoading(false);
    };

    setTimeout(loadPosts, 1000); // Simulate loading delay
  }, []);

  const handleLike = (postId) => {
    setPosts(posts.map(post => {
      if (post.id === postId) {
        return {
          ...post,
          liked: !post.liked,
          likes: post.liked ? post.likes - 1 : post.likes + 1
        };
      }
      return post;
    }));
  };

  const handleComment = (postId, commentText) => {
    if (!commentText.trim()) return;

    setPosts(posts.map(post => {
      if (post.id === postId) {
        const newComment = {
          id: Date.now().toString(),
          username: user.username,
          text: commentText
        };
        return {
          ...post,
          comments: [...post.comments, newComment]
        };
      }
      return post;
    }));
  };

  if (loading) {
    return (
      <div className="feed-container">
        <div className="loading">Loading posts...</div>
      </div>
    );
  }

  return (
    <div className="feed-container">
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#8e8e8e' }}>
          <h3>No posts yet</h3>
          <p>Follow some users or create your first post!</p>
        </div>
      ) : (
        posts.map(post => (
          <PostCard
            key={post.id}
            post={post}
            onLike={handleLike}
            onComment={handleComment}
            currentUser={user}
          />
        ))
      )}
    </div>
  );
};

const PostCard = ({ post, onLike, onComment, currentUser }) => {
  const [commentText, setCommentText] = useState('');

  const handleCommentSubmit = (e) => {
    e.preventDefault();
    onComment(post.id, commentText);
    setCommentText('');
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <div className="post-avatar">
          {post.userAvatar}
        </div>
        <div className="post-user-info">
          <div className="post-username">{post.username}</div>
          <div className="post-time">
            {formatDistanceToNow(post.createdAt, { addSuffix: true })}
          </div>
        </div>
      </div>

      <img src={post.image} alt="Post" className="post-image" />

      <div className="post-actions">
        <div className="post-buttons">
          <button
            className={`post-button ${post.liked ? 'liked' : ''}`}
            onClick={() => onLike(post.id)}
          >
            <Heart size={24} fill={post.liked ? '#ed4956' : 'none'} />
          </button>
          <button className="post-button">
            <MessageCircle size={24} />
          </button>
          <button className="post-button">
            <Share size={24} />
          </button>
          <button className="post-button" style={{ marginLeft: 'auto' }}>
            <Bookmark size={24} />
          </button>
        </div>

        <div className="post-likes">
          {post.likes} {post.likes === 1 ? 'like' : 'likes'}
        </div>

        <div className="post-caption">
          <span className="username">{post.username}</span>
          {post.caption}
        </div>

        {post.comments.length > 0 && (
          <div className="post-comments">
            {post.comments.map(comment => (
              <div key={comment.id} className="post-comment">
                <span className="username">{comment.username}</span>
                {comment.text}
              </div>
            ))}
          </div>
        )}
      </div>

      <form onSubmit={handleCommentSubmit} className="comment-form">
        <input
          type="text"
          placeholder="Add a comment..."
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          className="comment-input"
        />
        <button
          type="submit"
          className="comment-submit"
          disabled={!commentText.trim()}
        >
          Post
        </button>
      </form>
    </div>
  );
};

export default Feed;
