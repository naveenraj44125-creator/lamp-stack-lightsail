import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const savedUser = localStorage.getItem('instagram_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('instagram_user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      // Simulate API call - replace with actual API call
      const mockUser = {
        id: '1',
        username: email.split('@')[0],
        email: email,
        fullName: 'Demo User',
        profilePicture: '',
        bio: 'Welcome to Instagram Clone!',
        followers: 0,
        following: 0,
        posts: 0
      };

      setUser(mockUser);
      localStorage.setItem('instagram_user', JSON.stringify(mockUser));
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      // Simulate API call - replace with actual API call
      const newUser = {
        id: Date.now().toString(),
        username: userData.username,
        email: userData.email,
        fullName: userData.fullName,
        profilePicture: '',
        bio: '',
        followers: 0,
        following: 0,
        posts: 0
      };

      setUser(newUser);
      localStorage.setItem('instagram_user', JSON.stringify(newUser));
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Registration failed' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('instagram_user');
  };

  const updateUser = (updatedData) => {
    const updatedUser = { ...user, ...updatedData };
    setUser(updatedUser);
    localStorage.setItem('instagram_user', JSON.stringify(updatedUser));
  };

  const value = {
    user,
    login,
    register,
    logout,
    updateUser,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
