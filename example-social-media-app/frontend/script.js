// Global variables
let currentUser = null;
let authToken = null;
let currentPage = 'feed';
let currentPostId = null;

// API Base URL
const API_BASE = '/api';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check if user is logged in
    authToken = localStorage.getItem('authToken');
    currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    
    if (authToken && currentUser) {
        showMainApp();
        loadFeed();
    } else {
        showAuthPage();
    }
    
    setupEventListeners();
}

function setupEventListeners() {
    // Auth form listeners
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
    });
    
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });
    
    document.getElementById('login-form-element').addEventListener('submit', handleLogin);
    document.getElementById('register-form-element').addEventListener('submit', handleRegister);
    
    // Navigation listeners
    document.querySelectorAll('.nav-link[data-page]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = e.target.closest('.nav-link').dataset.page;
            navigateToPage(page);
        });
    });
    
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Post form listeners
    document.getElementById('create-post-form').addEventListener('submit', handleCreatePost);
    
    // Post type change listener
    document.querySelectorAll('input[name="postType"]').forEach(radio => {
        radio.addEventListener('change', handlePostTypeChange);
    });
    
    // Feed filter listeners
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const filter = e.target.dataset.filter;
            setActiveFilter(e.target);
            loadFeed(filter);
        });
    });
    
    // Friends tab listeners
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            setActiveTab(e.target, tab);
        });
    });
    
    // Friend search
    document.getElementById('search-friends-btn').addEventListener('click', searchFriends);
    document.getElementById('friend-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchFriends();
        }
    });
    
    // Profile form
    document.getElementById('profile-form').addEventListener('submit', handleUpdateProfile);
    document.getElementById('profile-image-container').addEventListener('click', () => {
        document.getElementById('profile-picture-input').click();
    });
    document.getElementById('profile-picture-input').addEventListener('change', handleProfileImageChange);
    
    // Comments modal
    document.getElementById('close-comments-modal').addEventListener('click', closeCommentsModal);
    document.getElementById('add-comment-form').addEventListener('submit', handleAddComment);
    
    // Modal backdrop click
    document.getElementById('comments-modal').addEventListener('click', (e) => {
        if (e.target.id === 'comments-modal') {
            closeCommentsModal();
        }
    });
}

// Authentication functions
function showAuthPage() {
    document.getElementById('navbar').classList.add('hidden');
    document.getElementById('auth-page').classList.remove('hidden');
    hideAllPages();
}

function showMainApp() {
    document.getElementById('navbar').classList.remove('hidden');
    document.getElementById('auth-page').classList.add('hidden');
    navigateToPage('feed');
}

function showLoginForm() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
}

function showRegisterForm() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            showToast('Login successful!', 'success');
            showMainApp();
            loadFeed();
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('username', document.getElementById('register-username').value);
    formData.append('email', document.getElementById('register-email').value);
    formData.append('password', document.getElementById('register-password').value);
    formData.append('fullName', document.getElementById('register-fullname').value);
    formData.append('department', document.getElementById('register-department').value);
    formData.append('bio', document.getElementById('register-bio').value);
    
    const profilePic = document.getElementById('register-profile-pic').files[0];
    if (profilePic) {
        formData.append('profilePicture', profilePic);
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            showToast('Registration successful!', 'success');
            showMainApp();
            loadFeed();
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    showAuthPage();
    showToast('Logged out successfully', 'success');
}

// Navigation functions
function navigateToPage(page) {
    currentPage = page;
    hideAllPages();
    document.getElementById(`${page}-page`).classList.remove('hidden');
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    
    // Load page content
    switch (page) {
        case 'feed':
            loadFeed();
            break;
        case 'anomalies':
            loadAnomalies();
            break;
        case 'friends':
            loadFriends();
            break;
        case 'profile':
            loadProfile();
            break;
    }
}

function hideAllPages() {
    document.querySelectorAll('.page').forEach(page => {
        if (page.id !== 'auth-page') {
            page.classList.add('hidden');
        }
    });
}

// Post functions
async function handleCreatePost(e) {
    e.preventDefault();
    
    const content = document.getElementById('post-content').value;
    const postType = document.querySelector('input[name="postType"]:checked').value;
    const visibility = document.querySelector('input[name="visibility"]:checked').value;
    const imageFile = document.getElementById('post-image').files[0];
    
    const formData = new FormData();
    formData.append('content', content);
    formData.append('postType', postType);
    formData.append('visibility', visibility);
    
    if (imageFile) {
        formData.append('image', imageFile);
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/posts`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Post created successfully!', 'success');
            document.getElementById('create-post-form').reset();
            loadFeed();
        } else {
            showToast(data.error || 'Failed to create post', 'error');
        }
    } catch (error) {
        console.error('Create post error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function handlePostTypeChange() {
    const postType = document.querySelector('input[name="postType"]:checked').value;
    const visibilityGroup = document.getElementById('visibility-group');
    
    if (postType === 'anomaly') {
        visibilityGroup.style.display = 'none';
        document.querySelector('input[name="visibility"][value="public"]').checked = true;
    } else {
        visibilityGroup.style.display = 'flex';
    }
}

async function loadFeed(filter = 'all') {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/posts/feed?type=${filter}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayPosts(data.posts, 'posts-container');
        } else {
            showToast(data.error || 'Failed to load feed', 'error');
        }
    } catch (error) {
        console.error('Load feed error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function loadAnomalies() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/posts/feed?type=anomaly`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayPosts(data.posts, 'anomalies-container');
        } else {
            showToast(data.error || 'Failed to load anomalies', 'error');
        }
    } catch (error) {
        console.error('Load anomalies error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displayPosts(posts, containerId) {
    const container = document.getElementById(containerId);
    
    if (posts.length === 0) {
        container.innerHTML = '<div class="no-content">No posts to display</div>';
        return;
    }
    
    container.innerHTML = posts.map(post => createPostHTML(post)).join('');
    
    // Add event listeners to post buttons
    container.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', () => toggleLike(btn.dataset.postId));
    });
    
    container.querySelectorAll('.comment-btn').forEach(btn => {
        btn.addEventListener('click', () => openCommentsModal(btn.dataset.postId));
    });
}

function createPostHTML(post) {
    const timeAgo = getTimeAgo(post.created_at);
    const avatarSrc = post.profile_picture_url || 'https://via.placeholder.com/50x50?text=User';
    
    return `
        <div class="post-card">
            <div class="post-header">
                <img src="${avatarSrc}" alt="${post.full_name}" class="post-avatar">
                <div class="post-user-info">
                    <h4>${post.full_name}</h4>
                    <p>@${post.username} • ${post.department || 'Employee'} • ${timeAgo}</p>
                </div>
                <span class="post-type-badge ${post.post_type}">
                    ${post.post_type === 'anomaly' ? 'Anomaly Report' : 'Regular Post'}
                </span>
            </div>
            
            <div class="post-content">
                ${post.content}
            </div>
            
            ${post.image_url ? `<img src="${post.image_url}" alt="Post image" class="post-image">` : ''}
            
            <div class="post-actions">
                <div class="post-stats">
                    <span>${post.like_count} likes</span>
                    <span>${post.comment_count} comments</span>
                </div>
                <div class="post-buttons">
                    <button class="post-btn like-btn ${post.user_liked ? 'liked' : ''}" data-post-id="${post.id}">
                        <i class="fas fa-heart"></i> ${post.user_liked ? 'Liked' : 'Like'}
                    </button>
                    <button class="post-btn comment-btn" data-post-id="${post.id}">
                        <i class="fas fa-comment"></i> Comment
                    </button>
                </div>
            </div>
        </div>
    `;
}

async function toggleLike(postId) {
    try {
        const response = await fetch(`${API_BASE}/posts/${postId}/like`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Reload current page to update like counts
            if (currentPage === 'feed') {
                const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
                loadFeed(activeFilter);
            } else if (currentPage === 'anomalies') {
                loadAnomalies();
            }
        } else {
            showToast(data.error || 'Failed to toggle like', 'error');
        }
    } catch (error) {
        console.error('Toggle like error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// Comments functions
async function openCommentsModal(postId) {
    currentPostId = postId;
    document.getElementById('comments-modal').classList.remove('hidden');
    await loadComments(postId);
}

function closeCommentsModal() {
    document.getElementById('comments-modal').classList.add('hidden');
    currentPostId = null;
}

async function loadComments(postId) {
    try {
        const response = await fetch(`${API_BASE}/comments/post/${postId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayComments(data.comments);
        } else {
            showToast(data.error || 'Failed to load comments', 'error');
        }
    } catch (error) {
        console.error('Load comments error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

function displayComments(comments) {
    const container = document.getElementById('comments-container');
    
    if (comments.length === 0) {
        container.innerHTML = '<div class="no-content">No comments yet</div>';
        return;
    }
    
    container.innerHTML = comments.map(comment => createCommentHTML(comment)).join('');
}

function createCommentHTML(comment) {
    const timeAgo = getTimeAgo(comment.created_at);
    const avatarSrc = comment.profile_picture_url || 'https://via.placeholder.com/40x40?text=User';
    
    return `
        <div class="comment-card">
            <img src="${avatarSrc}" alt="${comment.full_name}" class="comment-avatar">
            <div class="comment-content">
                <div class="comment-header">
                    <span class="comment-author">${comment.full_name}</span>
                    <span class="comment-time">${timeAgo}</span>
                </div>
                <p>${comment.content}</p>
            </div>
        </div>
    `;
}

async function handleAddComment(e) {
    e.preventDefault();
    
    const content = document.getElementById('comment-content').value;
    
    try {
        const response = await fetch(`${API_BASE}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                postId: currentPostId,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('comment-content').value = '';
            await loadComments(currentPostId);
            showToast('Comment added successfully!', 'success');
        } else {
            showToast(data.error || 'Failed to add comment', 'error');
        }
    } catch (error) {
        console.error('Add comment error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// Friends functions
async function loadFriends() {
    await loadFriendsList();
    await loadFriendRequests();
}

async function loadFriendsList() {
    try {
        const response = await fetch(`${API_BASE}/friends`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayFriends(data.friends);
        } else {
            showToast(data.error || 'Failed to load friends', 'error');
        }
    } catch (error) {
        console.error('Load friends error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

function displayFriends(friends) {
    const container = document.getElementById('friends-container');
    
    if (friends.length === 0) {
        container.innerHTML = '<div class="no-content">No friends yet</div>';
        return;
    }
    
    container.innerHTML = friends.map(friend => createFriendHTML(friend)).join('');
    
    // Add event listeners
    container.querySelectorAll('.remove-friend-btn').forEach(btn => {
        btn.addEventListener('click', () => removeFriend(btn.dataset.friendId));
    });
}

function createFriendHTML(friend) {
    const avatarSrc = friend.profile_picture_url || 'https://via.placeholder.com/60x60?text=User';
    
    return `
        <div class="friend-card">
            <div class="friend-info">
                <img src="${avatarSrc}" alt="${friend.full_name}" class="friend-avatar">
                <div class="friend-details">
                    <h4>${friend.full_name}</h4>
                    <p>@${friend.username} • ${friend.department || 'Employee'}</p>
                </div>
            </div>
            <div class="friend-actions">
                <button class="btn btn-danger remove-friend-btn" data-friend-id="${friend.friend_id}">
                    Remove Friend
                </button>
            </div>
        </div>
    `;
}

async function loadFriendRequests() {
    try {
        const [receivedResponse, sentResponse] = await Promise.all([
            fetch(`${API_BASE}/friends/requests/received`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            }),
            fetch(`${API_BASE}/friends/requests/sent`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            })
        ]);
        
        const receivedData = await receivedResponse.json();
        const sentData = await sentResponse.json();
        
        if (receivedResponse.ok && sentResponse.ok) {
            displayReceivedRequests(receivedData.requests);
            displaySentRequests(sentData.requests);
        }
    } catch (error) {
        console.error('Load friend requests error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

function displayReceivedRequests(requests) {
    const container = document.getElementById('received-requests-container');
    
    if (requests.length === 0) {
        container.innerHTML = '<div class="no-content">No pending requests</div>';
        return;
    }
    
    container.innerHTML = requests.map(request => createReceivedRequestHTML(request)).join('');
    
    // Add event listeners
    container.querySelectorAll('.accept-request-btn').forEach(btn => {
        btn.addEventListener('click', () => respondToFriendRequest(btn.dataset.requestId, 'accept'));
    });
    
    container.querySelectorAll('.decline-request-btn').forEach(btn => {
        btn.addEventListener('click', () => respondToFriendRequest(btn.dataset.requestId, 'decline'));
    });
}

function createReceivedRequestHTML(request) {
    const avatarSrc = request.profile_picture_url || 'https://via.placeholder.com/60x60?text=User';
    
    return `
        <div class="request-card">
            <div class="friend-info">
                <img src="${avatarSrc}" alt="${request.full_name}" class="friend-avatar">
                <div class="friend-details">
                    <h4>${request.full_name}</h4>
                    <p>@${request.username} • ${request.department || 'Employee'}</p>
                </div>
            </div>
            <div class="friend-actions">
                <button class="btn btn-success accept-request-btn" data-request-id="${request.id}">
                    Accept
                </button>
                <button class="btn btn-danger decline-request-btn" data-request-id="${request.id}">
                    Decline
                </button>
            </div>
        </div>
    `;
}

function displaySentRequests(requests) {
    const container = document.getElementById('sent-requests-container');
    
    if (requests.length === 0) {
        container.innerHTML = '<div class="no-content">No sent requests</div>';
        return;
    }
    
    container.innerHTML = requests.map(request => createSentRequestHTML(request)).join('');
}

function createSentRequestHTML(request) {
    const avatarSrc = request.profile_picture_url || 'https://via.placeholder.com/60x60?text=User';
    
    return `
        <div class="request-card">
            <div class="friend-info">
                <img src="${avatarSrc}" alt="${request.full_name}" class="friend-avatar">
                <div class="friend-details">
                    <h4>${request.full_name}</h4>
                    <p>@${request.username} • ${request.department || 'Employee'}</p>
                </div>
            </div>
            <div class="friend-actions">
                <span class="status-text">Request Sent</span>
            </div>
        </div>
    `;
}

async function searchFriends() {
    const query = document.getElementById('friend-search').value.trim();
    
    if (query.length < 2) {
        showToast('Please enter at least 2 characters', 'warning');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/friends/search?q=${encodeURIComponent(query)}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySearchResults(data.users);
        } else {
            showToast(data.error || 'Search failed', 'error');
        }
    } catch (error) {
        console.error('Search friends error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displaySearchResults(users) {
    const container = document.getElementById('search-results-container');
    
    if (users.length === 0) {
        container.innerHTML = '<div class="no-content">No users found</div>';
        return;
    }
    
    container.innerHTML = users.map(user => createSearchResultHTML(user)).join('');
    
    // Add event listeners
    container.querySelectorAll('.send-request-btn').forEach(btn => {
        btn.addEventListener('click', () => sendFriendRequest(btn.dataset.userId));
    });
}

function createSearchResultHTML(user) {
    const avatarSrc = user.profile_picture_url || 'https://via.placeholder.com/60x60?text=User';
    let actionButton = '';
    
    if (user.friendship_status === 'accepted') {
        actionButton = '<span class="status-text">Already Friends</span>';
    } else if (user.friendship_status === 'pending') {
        actionButton = '<span class="status-text">Request Pending</span>';
    } else {
        actionButton = `<button class="btn btn-primary send-request-btn" data-user-id="${user.id}">Send Request</button>`;
    }
    
    return `
        <div class="request-card">
            <div class="friend-info">
                <img src="${avatarSrc}" alt="${user.full_name}" class="friend-avatar">
                <div class="friend-details">
                    <h4>${user.full_name}</h4>
                    <p>@${user.username} • ${user.department || 'Employee'}</p>
                </div>
            </div>
            <div class="friend-actions">
                ${actionButton}
            </div>
        </div>
    `;
}

async function sendFriendRequest(userId) {
    try {
        const response = await fetch(`${API_BASE}/friends/request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ userId: parseInt(userId) })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Friend request sent!', 'success');
            searchFriends(); // Refresh search results
        } else {
            showToast(data.error || 'Failed to send friend request', 'error');
        }
    } catch (error) {
        console.error('Send friend request error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

async function respondToFriendRequest(requestId, action) {
    try {
        const response = await fetch(`${API_BASE}/friends/request/${requestId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ action })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`Friend request ${action}ed!`, 'success');
            loadFriendRequests(); // Refresh requests
            if (action === 'accept') {
                loadFriendsList(); // Refresh friends list
            }
        } else {
            showToast(data.error || `Failed to ${action} friend request`, 'error');
        }
    } catch (error) {
        console.error('Respond to friend request error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

async function removeFriend(friendId) {
    if (!confirm('Are you sure you want to remove this friend?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/friends/${friendId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Friend removed successfully', 'success');
            loadFriendsList(); // Refresh friends list
        } else {
            showToast(data.error || 'Failed to remove friend', 'error');
        }
    } catch (error) {
        console.error('Remove friend error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// Profile functions
async function loadProfile() {
    try {
        const response = await fetch(`${API_BASE}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            populateProfileForm(data.user);
        } else {
            showToast(data.error || 'Failed to load profile', 'error');
        }
    } catch (error) {
        console.error('Load profile error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

function populateProfileForm(user) {
    document.getElementById('profile-fullname').value = user.full_name || '';
    document.getElementById('profile-username').value = user.username || '';
    document.getElementById('profile-email').value = user.email || '';
    document.getElementById('profile-department').value = user.department || '';
    document.getElementById('profile-bio').value = user.bio || '';
    
    const profileImage = document.getElementById('profile-image');
    if (user.profile_picture_url) {
        profileImage.src = user.profile_picture_url;
    } else {
        profileImage.src = 'https://via.placeholder.com/150x150?text=User';
    }
}

function handleProfileImageChange(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profile-image').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

async function handleUpdateProfile(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('fullName', document.getElementById('profile-fullname').value);
    formData.append('department', document.getElementById('profile-department').value);
    formData.append('bio', document.getElementById('profile-bio').value);
    
    const profilePicture = document.getElementById('profile-picture-input').files[0];
    if (profilePicture) {
        formData.append('profilePicture', profilePicture);
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/auth/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showToast('Profile updated successfully!', 'success');
        } else {
            showToast(data.error || 'Failed to update profile', 'error');
        }
    } catch (error) {
        console.error('Update profile error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Utility functions
function setActiveFilter(activeBtn) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    activeBtn.classList.add('active');
}

function setActiveTab(activeBtn, tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    activeBtn.classList.add('active');
    
    // Show/hide tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    document.getElementById(`${tab}-tab`).classList.remove('hidden');
    
    // Load tab content
    switch (tab) {
        case 'friends':
            loadFriendsList();
            break;
        case 'requests':
            loadFriendRequests();
            break;
        case 'search':
            // Search tab is always visible, no need to load
            break;
    }
}

function showLoading() {
    // Create loading overlay if it doesn't exist
    let loadingOverlay = document.getElementById('loading-overlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Loading...</p>
            </div>
        `;
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
        document.body.appendChild(loadingOverlay);
    }
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
        `;
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close">&times;</button>
        </div>
    `;
    
    // Toast styles
    toast.style.cssText = `
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : '#2196F3'};
        color: white;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;
    
    // Add close functionality
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        margin-left: 10px;
        padding: 0;
    `;
    
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

function getTimeAgo(dateString) {
    const now = new Date();
    const date = new Date(dateString);
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 2592000) {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 31536000) {
        const months = Math.floor(diffInSeconds / 2592000);
        return `${months} month${months > 1 ? 's' : ''} ago`;
    } else {
        const years = Math.floor(diffInSeconds / 31536000);
        return `${years} year${years > 1 ? 's' : ''} ago`;
    }
}

// Add CSS for animations and loading spinner
const additionalStyles = `
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #007bff;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 10px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-spinner {
    text-align: center;
    color: white;
}

.loading-spinner p {
    margin: 0;
    font-size: 16px;
}

.toast-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.toast-message {
    flex: 1;
}
`;

// Add the additional styles to the document
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
