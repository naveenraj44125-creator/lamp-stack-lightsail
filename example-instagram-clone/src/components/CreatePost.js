import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const CreatePost = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [caption, setCaption] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError('Image size must be less than 10MB');
        return;
      }

      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }

      setSelectedImage(file);
      setError('');

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedImage) {
      setError('Please select an image');
      return;
    }

    if (!caption.trim()) {
      setError('Please add a caption');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Simulate API call to create post
      // In a real app, you would upload the image to your storage service
      // and save the post data to your database
      
      const newPost = {
        id: Date.now().toString(),
        username: user.username,
        userAvatar: user.username.charAt(0).toUpperCase(),
        image: imagePreview, // In real app, this would be the uploaded image URL
        caption: caption,
        likes: 0,
        comments: [],
        createdAt: new Date(),
        liked: false
      };

      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // In a real app, you would save this to your backend
      console.log('New post created:', newPost);

      // Navigate back to feed
      navigate('/');
    } catch (err) {
      setError('Failed to create post. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-post-container">
      <div className="create-post-card">
        <h2 className="create-post-title">Create New Post</h2>
        
        <form onSubmit={handleSubmit} className="create-post-form">
          <div className="file-input-wrapper">
            {!imagePreview ? (
              <>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="file-input"
                  id="image-upload"
                />
                <label htmlFor="image-upload" className="file-input-label">
                  <Camera size={48} />
                  <div style={{ marginTop: '12px' }}>
                    Click to select an image
                  </div>
                  <div style={{ fontSize: '12px', marginTop: '4px', opacity: 0.7 }}>
                    JPG, PNG, GIF up to 10MB
                  </div>
                </label>
              </>
            ) : (
              <div style={{ position: 'relative' }}>
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="image-preview"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  style={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    background: 'rgba(0, 0, 0, 0.5)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer'
                  }}
                >
                  <X size={16} />
                </button>
              </div>
            )}
          </div>

          <textarea
            placeholder="Write a caption..."
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            className="caption-textarea"
            maxLength={2200}
          />

          <div style={{ fontSize: '12px', color: '#8e8e8e', textAlign: 'right' }}>
            {caption.length}/2200
          </div>

          {error && <div className="error">{error}</div>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !selectedImage || !caption.trim()}
          >
            {loading ? 'Sharing...' : 'Share Post'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreatePost;
