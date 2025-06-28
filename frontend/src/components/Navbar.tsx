import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Auth.css';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogout = () => {
    logout();
  };

  if (!user) {
    return null;
  }

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          🌟 멘토링 커넥트
        </Link>
        <ul className="navbar-nav">
          <li>
            <Link 
              to="/profile" 
              className={`nav-link ${isActive('/profile') ? 'active' : ''}`}
            >
              👤 프로필
            </Link>
          </li>
          {user.role === 'mentee' && (
            <li>
              <Link 
                to="/mentors" 
                className={`nav-link ${isActive('/mentors') ? 'active' : ''}`}
              >
                🎯 멘토 찾기
              </Link>
            </li>
          )}
          <li>
            <Link 
              to="/requests" 
              className={`nav-link ${isActive('/requests') ? 'active' : ''}`}
            >
              📋 요청 관리
            </Link>
          </li>
          <li>
            <span className="nav-link" style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
              {user.role === 'mentor' ? '👨‍🏫' : '👨‍🎓'} {user.profile?.name || user.email}
            </span>
          </li>
          <li>
            <button onClick={handleLogout} className="logout-btn">
              🚪 로그아웃
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
