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
        /* Clean glass morphism navigation */
        .jumbo-nav {
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .jumbo-nav-link {
          transition: all 0.2s ease;
          border-radius: 12px;
        }
        
        .jumbo-nav-link:hover {
          transform: translateY(-1px);
          background: rgba(255, 255, 255, 0.1) !important;
        }
        
        .jumbo-nav-link-active {
          background: rgba(59, 130, 246, 0.25) !important;
          box-shadow: 0 0 20px rgba(59, 130, 246, 0.15) !important;
          border: 1px solid rgba(59, 130, 246, 0.3) !important;
        }
        
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          .mobile-toggle { display: flex !important; }
          .user-name { display: none !important; }
        }
        
        @media (min-width: 769px) {
          .mobile-toggle { display: none !important; }
        }
      `}</style>
      
      <nav className="jumbo-nav" style={scrolled ? styles.navScrolled : styles.navTransparent}>
        <div style={styles.container}>
          {/* Logo */}
          <div style={styles.logo}>
            <div style={styles.logoCircle}>
              <img src="/jumbo-logo.png" alt="Jumbo" style={styles.logoImg} />
            </div>
            <img src="/logotext.png" alt="JUMBO" style={styles.logoText} />
          </div>

          {/* Desktop Navigation */}
          <div style={styles.navLinks} className="desktop-nav">
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`jumbo-nav-link ${currentPage === item.id ? 'jumbo-nav-link-active' : ''}`}
                style={{
                  ...styles.navLink,
                  ...(currentPage === item.id ? styles.navLinkActive : {})
                }}
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* User Section */}
          <div style={styles.userSection}>
            <span style={styles.userName} className="user-name">{userName}</span>
            <button onClick={onLogout} style={styles.logoutButton} title="Logout">
              <LogOut size={18} />
            </button>
          </div>

          {/* Mobile Toggle */}
          <button
            style={styles.mobileToggle}
            className="mobile-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div style={styles.mobileMenu}>
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                style={{
                  ...styles.mobileLink,
                  ...(currentPage === item.id ? styles.mobileLinkActive : {})
                }}
              >
                {item.label}
              </button>
            ))}
            <button onClick={() => { onLogout(); setMobileMenuOpen(false); }} style={styles.mobileLogout}>
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
  // Base navigation styles
  navTransparent: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    background: 'transparent',
    border: 'none',
    boxShadow: 'none',
  },
  navScrolled: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '16px 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  
  // Logo section
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  logoCircle: {
    width: '40px',
    height: '40px',
    background: 'rgba(255, 255, 255, 0.9)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  logoImg: {
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    objectFit: 'cover',
  },
  logoText: {
    height: '32px',
    width: 'auto',
    objectFit: 'contain',
    filter: 'brightness(0) invert(1)',
  },
  
  // Desktop navigation
  navLinks: {
    display: 'flex',
    gap: '20px',
  },
  navLink: {
    background: 'none',
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'sans-serif',
    cursor: 'pointer',
    padding: '10px 18px',
    borderRadius: '12px',
    transition: 'all 0.2s ease',
  },
  navLinkActive: {
    background: 'rgba(59, 130, 246, 0.25)', // Blue instead of purple
    color: 'white',
    boxShadow: '0 0 20px rgba(59, 130, 246, 0.15)',
    border: '1px solid rgba(59, 130, 246, 0.3)',
  },
  
  // User section
  userSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userName: {
    color: 'rgba(255, 255, 255, 0.95)',
    fontSize: '14px',
    fontWeight: '600',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'sans-serif',
  },
  logoutButton: {
    background: 'rgba(239, 68, 68, 0.2)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: 'white',
    padding: '8px 12px',
    borderRadius: '8px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    transition: 'all 0.2s ease',
  },
  
  // Mobile navigation
  mobileToggle: {
    display: 'none',
    background: 'none',
    border: 'none',
    color: 'white',
    cursor: 'pointer',
    alignItems: 'center',
    justifyContent: 'center',
  },
  mobileMenu: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    padding: '16px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  mobileLink: {
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    color: 'white',
    padding: '12px 16px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'sans-serif',
  },
  mobileLinkActive: {
    background: 'rgba(59, 130, 246, 0.3)',
    boxShadow: '0 0 15px rgba(59, 130, 246, 0.2)',
  },
  mobileLogout: {
    background: 'rgba(239, 68, 68, 0.2)',
    border: 'none',
    color: '#fca5a5',
    padding: '12px 16px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    justifyContent: 'center',
  },
};

export default Navigation;