import React from 'react';

const OAuthLoadingOverlay = ({ show }) => {
  if (!show) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.content}>
        <div style={styles.logoContainer}>
          <img src="/jumbo-logo.png" alt="Jumbo" style={styles.logo} />
        </div>
        <h2 style={styles.title}>Connecting to Google</h2>
        <p style={styles.subtitle}>Securely authenticating with your Google account...</p>
        <div style={styles.spinner}></div>
        <p style={styles.note}>
          🔒 Your data is protected by enterprise-grade security
        </p>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(12, 20, 38, 0.95)',
    backdropFilter: 'blur(10px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
  },
  content: {
    textAlign: 'center',
    color: 'white',
    maxWidth: '400px',
    padding: '40px',
  },
  logoContainer: {
    marginBottom: '20px',
  },
  logo: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
  },
  title: {
    fontSize: '24px',
    fontWeight: '600',
    marginBottom: '10px',
    background: 'linear-gradient(135deg, #0ea5e9, #3b82f6)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    fontSize: '16px',
    opacity: 0.8,
    marginBottom: '30px',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid rgba(255,255,255,0.3)',
    borderTop: '4px solid #0ea5e9',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 20px',
  },
  note: {
    fontSize: '14px',
    opacity: 0.7,
    marginTop: '20px',
  },
};

// Add CSS animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

export default OAuthLoadingOverlay;