// Modern Blog JavaScript
class BlogApp {
    constructor() {
        this.posts = [];
        this.currentOffset = 0;
        this.limit = 10;
        this.hasMore = true;
        this.isLoading = false;
        this.currentSearch = '';
        this.editingPostId = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadPosts();
    }
    
    initializeElements() {
        // Main elements
        this.postsContainer = document.getElementById('postsContainer');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.newPostBtn = document.getElementById('newPostBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        
        // Modal elements
        this.modal = document.getElementById('postModal');
        this.modalTitle = document.getElementById('modalTitle');
        this.postForm = document.getElementById('postForm');
        this.closeModal = document.getElementById('closeModal');
        this.cancelBtn = document.getElementById('cancelBtn');
        this.saveBtn = document.getElementById('saveBtn');
        
        // Form elements
        this.postTitle = document.getElementById('postTitle');
        this.postAuthor = document.getElementById('postAuthor');
        this.postTags = document.getElementById('postTags');
        this.postContent = document.getElementById('postContent');
        
        // Toast container
        this.toastContainer = document.getElementById('toastContainer');
    }
    
    bindEvents() {
        // Search functionality
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        
        // New post button
        this.newPostBtn.addEventListener('click', () => this.openModal());
        
        // Modal events
        this.closeModal.addEventListener('click', () => this.closeModalHandler());
        this.cancelBtn.addEventListener('click', () => this.closeModalHandler());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModalHandler();
        });
        
        // Form submission
        this.postForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Load more button
        this.loadMoreBtn.addEventListener('click', () => this.loadMorePosts());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                this.closeModalHandler();
            }
        });
    }
    
    async loadPosts(reset = false) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        
        if (reset) {
            this.currentOffset = 0;
            this.posts = [];
            this.hasMore = true;
        }
        
        try {
            const params = new URLSearchParams({
                limit: this.limit,
                offset: this.currentOffset,
                ...(this.currentSearch && { search: this.currentSearch })
            });
            
            const response = await fetch(`/api/posts?${params}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load posts');
            }
            
            if (reset) {
                this.posts = data.posts;
            } else {
                this.posts.push(...data.posts);
            }
            
            this.hasMore = data.hasMore;
            this.currentOffset += data.posts.length;
            
            this.renderPosts();
            this.updateLoadMoreButton();
            
        } catch (error) {
            console.error('Error loading posts:', error);
            this.showToast('Failed to load posts', 'error');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    renderPosts() {
        if (this.posts.length === 0) {
            this.postsContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No posts found</h3>
                    <p>Be the first to create a blog post!</p>
                </div>
            `;
            return;
        }
        
        const postsHTML = this.posts.map(post => this.createPostHTML(post)).join('');
        this.postsContainer.innerHTML = postsHTML;
        
        // Bind post action events
        this.bindPostEvents();
    }
    
    createPostHTML(post) {
        const createdDate = new Date(post.createdAt).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        const updatedDate = new Date(post.updatedAt).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        const isUpdated = post.createdAt !== post.updatedAt;
        
        const tagsHTML = post.tags && post.tags.length > 0 
            ? `<div class="post-tags">
                ${post.tags.map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`).join('')}
               </div>`
            : '';
        
        return `
            <article class="post-card" data-post-id="${post.id}">
                <div class="post-header">
                    <div>
                        <h2 class="post-title">${this.escapeHtml(post.title)}</h2>
                        <div class="post-meta">
                            <span class="post-author">By ${this.escapeHtml(post.author)}</span>
                            <span class="post-date">
                                ${createdDate}${isUpdated ? ` (updated ${updatedDate})` : ''}
                            </span>
                        </div>
                    </div>
                    <div class="post-actions">
                        <button class="btn btn-secondary btn-small edit-btn" data-post-id="${post.id}">
                            Edit
                        </button>
                        <button class="btn btn-danger btn-small delete-btn" data-post-id="${post.id}">
                            Delete
                        </button>
                    </div>
                </div>
                ${tagsHTML}
                <div class="post-content">${this.escapeHtml(post.content)}</div>
            </article>
        `;
    }
    
    bindPostEvents() {
        // Edit buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const postId = e.target.dataset.postId;
                this.editPost(postId);
            });
        });
        
        // Delete buttons
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const postId = e.target.dataset.postId;
                this.deletePost(postId);
            });
        });
    }
    
    handleSearch() {
        const searchTerm = this.searchInput.value.trim();
        this.currentSearch = searchTerm;
        this.loadPosts(true);
    }
    
    loadMorePosts() {
        this.loadPosts(false);
    }
    
    updateLoadMoreButton() {
        if (this.hasMore && this.posts.length > 0) {
            this.loadMoreBtn.style.display = 'block';
        } else {
            this.loadMoreBtn.style.display = 'none';
        }
    }
    
    hideLoading() {
        this.loadingSpinner.style.display = 'none';
    }
    
    openModal(post = null) {
        this.editingPostId = post ? post.id : null;
        
        if (post) {
            this.modalTitle.textContent = 'Edit Post';
            this.postTitle.value = post.title;
            this.postAuthor.value = post.author;
            this.postTags.value = post.tags ? post.tags.join(', ') : '';
            this.postContent.value = post.content;
        } else {
            this.modalTitle.textContent = 'Create New Post';
            this.postForm.reset();
        }
        
        this.modal.classList.add('show');
        this.postTitle.focus();
    }
    
    closeModalHandler() {
        this.modal.classList.remove('show');
        this.editingPostId = null;
        this.postForm.reset();
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const title = this.postTitle.value.trim();
        const author = this.postAuthor.value.trim() || 'Anonymous';
        const content = this.postContent.value.trim();
        const tags = this.postTags.value.split(',').map(tag => tag.trim()).filter(tag => tag);
        
        if (!title || !content) {
            this.showToast('Title and content are required', 'error');
            return;
        }
        
        const postData = { title, author, content, tags };
        
        try {
            this.setSaveButtonLoading(true);
            
            let response;
            if (this.editingPostId) {
                response = await fetch(`/api/posts/${this.editingPostId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(postData)
                });
            } else {
                response = await fetch('/api/posts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(postData)
                });
            }
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to save post');
            }
            
            this.showToast(
                this.editingPostId ? 'Post updated successfully!' : 'Post created successfully!',
                'success'
            );
            
            this.closeModalHandler();
            this.loadPosts(true); // Reload all posts
            
        } catch (error) {
            console.error('Error saving post:', error);
            this.showToast(error.message, 'error');
        } finally {
            this.setSaveButtonLoading(false);
        }
    }
    
    setSaveButtonLoading(loading) {
        const btnText = this.saveBtn.querySelector('.btn-text');
        const btnLoading = this.saveBtn.querySelector('.btn-loading');
        
        if (loading) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            this.saveBtn.disabled = true;
        } else {
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
            this.saveBtn.disabled = false;
        }
    }
    
    async editPost(postId) {
        const post = this.posts.find(p => p.id === postId);
        if (post) {
            this.openModal(post);
        } else {
            // Fetch post if not in current list
            try {
                const response = await fetch(`/api/posts/${postId}`);
                const post = await response.json();
                
                if (response.ok) {
                    this.openModal(post);
                } else {
                    this.showToast('Post not found', 'error');
                }
            } catch (error) {
                console.error('Error fetching post:', error);
                this.showToast('Failed to load post', 'error');
            }
        }
    }
    
    async deletePost(postId) {
        const post = this.posts.find(p => p.id === postId);
        const postTitle = post ? post.title : 'this post';
        
        if (!confirm(`Are you sure you want to delete "${postTitle}"? This action cannot be undone.`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/posts/${postId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to delete post');
            }
            
            this.showToast('Post deleted successfully!', 'success');
            this.loadPosts(true); // Reload all posts
            
        } catch (error) {
            console.error('Error deleting post:', error);
            this.showToast(error.message, 'error');
        }
    }
    
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
        
        // Allow manual removal by clicking
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BlogApp();
});