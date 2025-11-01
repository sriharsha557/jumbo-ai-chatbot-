import React, { useState } from 'react';
import { LogOut, Menu, X } from 'lucide-react';
import { theme } from '../theme/theme';

function Navigation({ currentPage, onNavigate, userName, onLogout, scrolled = false }) {
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
    <>
      <style>{`
        @media (max-width: 768px) {
          .desktop-nav {
            display: none !important;
          }
          .mobile-menu-toggle {
            display: block !important;
          }
          .user-name {
            display: none !important;
          }
          .user-section {
            gap: 8px !important;
          }
        }
        @media (min-width: 769px) {
          .mobile-menu-toggle {
            display: none !important;
          }
        }
      `}</style>
      <nav style={{
        ...styles.navbar,
        ...(scrolled ? styles.navbarScrolled : styles.navbarTop)
      }}>
      <div style={styles.navContainer}>
        {/* Logo and Title */}
        <div style={styles.logo}>
          <div style={styles.logoCircle}>
            <img src="/jumbo-logo.png" alt="Jumbo" style={styles.logoImage} />
          </div>
          <img src="/logotext.png" alt="JUMBO" style={styles.logoText} />
        </div>

        {/* Desktop Navigation */}
        <div style={styles.desktopNav} className="desktop-nav">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => handleNavClick(item.id)}
              style={{
                ...styles.navLink,
                ...(currentPage === item.id ? styles.navLinkActive : {})
              }}
              onMouseEnter={(e) => {
                if (currentPage !== item.id) {
                  e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentPage !== item.id) {
                  e.target.style.background = 'none';
                }
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* User Info and Logout */}
        <div style={styles.userSection} className="user-section">
          <span style={styles.userName} className="user-name">{userName}</span>
          <button
            onClick={onLogout}
            style={styles.logoutBtn}
            title="Logout"
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(239, 68, 68, 0.4)';
              e.target.style.borderColor = 'rgba(239, 68, 68, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(239, 68, 68, 0.2)';
              e.target.style.borderColor = 'rgba(239, 68, 68, 0.3)';
            }}
          >
            <LogOut size={18} />
          </button>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          style={styles.mobileMenuToggle}
          className="mobile-menu-toggle"
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
          <button
            onClick={() => {
              onLogout();
              setMobileMenuOpen(false);
            }}
            style={{
              ...styles.mobileNavLink,
              background: 'rgba(239, 68, 68, 0.2)',
              color: '#fca5a5',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              justifyContent: 'center',
            }}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      )}
    </nav>
    </>
  );
}

const styles = {
  navbar: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    transition: 'all 0.3s ease',
  },
  navbarTop: {
    background: 'transparent',
    backdropFilter: 'none',
    WebkitBackdropFilter: 'none',
    border: 'none',
    borderBottom: 'none',
    boxShadow: 'none',
  },
  navbarScrolled: {
    background: 'rgba(15, 23, 42, 0.85)',
    backdropFilter: 'blur(24px)',
    WebkitBackdropFilter: 'blur(24px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
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
  },
  navLink: {
    background: 'none',
    border: 'none',
    color: 'rgba(255, 255, 255, 0.9)', // Brighter text
    fontSize: '16px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    cursor: 'pointer',
    padding: '8px 16px',
    borderRadius: '8px',
    transition: 'all 0.3s',
  },
  navLinkActive: {
    background: 'rgba(59, 130, 246, 0.3)', // Blue active background
    color: 'white',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
  },
  userSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userName: {
    color: 'rgba(255, 255, 255, 0.95)', // Brighter username
    fontSize: '14px',
    fontWeight: '600',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    textShadow: '0 1px 2px rgba(0, 0, 0, 0.5)', // Add text shadow for better visibility
  },
  logoutBtn: {
    background: 'rgba(239, 68, 68, 0.2)', // Red logout button
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: 'rgba(255, 255, 255, 0.95)',
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