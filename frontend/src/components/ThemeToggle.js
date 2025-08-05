import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`theme-toggle ${className}`}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      <div className="theme-toggle-track">
        <div className="theme-toggle-thumb">
          <div className="theme-icon">
            {theme === 'light' ? '☀️' : '🌙'}
          </div>
        </div>
        <div className="theme-toggle-icons">
          <span className="sun-icon">☀️</span>
          <span className="moon-icon">🌙</span>
        </div>
      </div>
    </button>
  );
};

export default ThemeToggle;