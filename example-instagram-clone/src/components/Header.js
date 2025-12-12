import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Home, PlusSquare, User, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          Instagram
        </Link>
        
        <nav className="header-nav">
          <Link to="/" className="nav-link" title="Home">
            <Home size={24} />
          </Link>
          <Link to="/create" className="nav-link" title="Create Post">
            <PlusSquare size={24} />
          </Link>
          <Link to={`/profile/${user?.username}`} className="nav-link" title="Profile">
            <User size={24} />
          </Link>
          <button onClick={handleLogout} className="nav-link nav-button" title="Logout">
            <LogOut size={24} />
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
