import React, { useState } from 'react';
import { LogOut, Menu, X } from 'lucide-react';
import { theme } from '../theme/theme';

function Navigation({ currentPage, onNavigate, userName, onLogout }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'chat', label: 'Chat' },
    { id: 'profile', label: 'Profile' }
  ];

  const handleNavClick = (pageId) => {
    onNavigate(pageId);
    setMobileMenuOpen(false);
  };

  return (
    <nav style={styles.navbar}>
      <div style={styles.navContainer}>
        {/* Logo and Title */}
        <div style={styles.logo}>
          <div style={styles.logoCircle}>
            <img src="/jumbo-logo.png" alt="Jumbo" style={styles.logoImage} />
          </div>
          <img src="/logotext.png" alt="JUMBO" style={styles.logoText} />
        </div>

        {/* Desktop Navigation */}
        <div style={styles.desktopNav}>
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              style={{
                ...styles.navLink,
                ...(currentPage === item.id ? styles.navLinkActive : {})
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* User Info and Logout */}
        <div style={styles.userSection}>
          <span style={styles.userName}>{userName}</span>
          <button
            onClick={onLogout}
            style={styles.logoutBtn}
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          style={styles.mobileMenuToggle}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div style={styles.mobileNav}>
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              style={{
                ...styles.mobileNavLink,
                ...(currentPage === item.id ? styles.mobileNavLinkActive : {})
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </nav>
  );
}

const styles = {
  navbar: {
    background: 'rgba(255, 255, 255, 0.08)',
    backdropFilter: 'blur(24px)',
    WebkitBackdropFilter: 'blur(24px)', // Safari support
    border: '1px solid rgba(255, 255, 255, 0.15)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
  },
  navContainer: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '16px 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    cursor: 'pointer',
  },
  logoCircle: {
    width: '40px',
    height: '40px',
    background: 'rgba(255, 255, 255, 0.9)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
    overflow: 'hidden',
  },
  logoImage: {
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    objectFit: 'cover',
  },
  logoText: {
    height: '32px',
    width: 'auto',
    objectFit: 'contain',
    filter: 'brightness(0) invert(1)', // Makes the logo white
  },
  desktopNav: {
    display: 'flex',
    gap: '24px',
    '@media (maxWidth: 768px)': {
      display: 'none',
    },
  },
  navLink: {
    background: 'none',
    border: 'none',
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '16px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    cursor: 'pointer',
    padding: '8px 16px',
    borderRadius: '8px',
    transition: 'all 0.3s',
  },
  navLinkActive: {
    background: 'rgba(255, 255, 255, 0.2)',
    color: 'white',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
  },
  userSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userName: {
    color: 'white',
    fontSize: '14px',
    fontWeight: '600',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  logoutBtn: {
    background: 'rgba(255, 255, 255, 0.2)',
    border: 'none',
    color: 'white',
    padding: '8px 12px',
    borderRadius: '8px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.3s',
  },
  mobileMenuToggle: {
    display: 'none',
    background: 'none',
    border: 'none',
    color: 'white',
    cursor: 'pointer',
    '@media (maxWidth: 768px)': {
      display: 'block',
    },
  },
  mobileNav: {
    background: 'rgba(0, 0, 0, 0.1)',
    padding: '12px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  mobileNavLink: {
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    color: 'white',
    padding: '12px 16px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    textAlign: 'left',
  },
  mobileNavLinkActive: {
    background: 'rgba(255, 255, 255, 0.3)',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
  },
};

export default Navigation;