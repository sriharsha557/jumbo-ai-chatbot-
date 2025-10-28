import React, { useState, useEffect } from 'react';
import { auth, supabase } from '../lib/supabase';
import { theme } from '../theme/theme';
import GradientBackground from './GradientBackground';
import OAuthLoadingOverlay from './OAuthLoadingOverlay';

function AuthPageSupabase({ onUserLogin }) {
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [showOAuthLoading, setShowOAuthLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState('');

  // Removed checkUser function - using Flask API authentication instead



  const handleEmailAuth = async (e) => {
    e.preventDefault();
    setIsAuthenticating(true);
    setError('');
    
    try {
      const endpoint = isSignUp ? '/api/auth/signup' : '/api/auth/signin';
      const payload = isSignUp 
        ? { email, password, name }
        : { email, password };
      
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        credentials: 'include' // Important for session cookies
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Successfully authenticated
        console.log('Login successful, calling onUserLogin with:', data);
        const userData = {
          id: data.user.user_id,
          email: data.user.email,
          name: data.profile?.name || data.user.email?.split('@')[0] || 'User',
          access_token: data.user.access_token
        };
        
        // Store user in localStorage for session persistence
        localStorage.setItem('jumbo_user', JSON.stringify(userData));
        
        onUserLogin(userData);
      } else {
        console.log('Login failed:', data);
        setError(data.message || 'Authentication failed');
      }
    } catch (error) {
      console.error('Auth error:', error);
      setError('Authentication failed. Please try again.');
    }
    
    setIsAuthenticating(false);
  };

  const handleGoogleSignIn = async () => {
    setIsAuthenticating(true);
    setShowOAuthLoading(true);
    setError('');
    
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin
        }
      });
      
      if (error) throw error;
      
      // Keep loading overlay visible during redirect
      // It will be hidden when the page reloads after OAuth
    } catch (error) {
      console.error('Google sign in error:', error);
      setError(error.message);
      setIsAuthenticating(false);
      setShowOAuthLoading(false);
    }
  };

  // Removed old handleEmailAuth - using the new one above

  return (
    <GradientBackground variant="copilot" animated={true} style={styles.container}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        
        .auth-input::placeholder {
          color: rgba(30, 64, 175, 0.6);
        }
        
        .auth-input:focus {
          border-color: rgba(139, 92, 246, 0.6);
          box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
        }
        
        .google-button:hover {
          background: rgba(255, 255, 255, 1);
          border-color: rgba(139, 92, 246, 0.3);
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .email-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
      `}</style>

      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.logoCircle}></div>
          <h1 style={styles.title}>JUMBO</h1>
          <p style={styles.subtitle}>Your Emotional Support Companion</p>
        </div>

        {error && (
          <div style={styles.errorBox}>
            <p style={styles.errorText}>{error}</p>
          </div>
        )}

        {/* Google Sign In */}
        <div style={styles.section}>
          <button
            onClick={handleGoogleSignIn}
            disabled={isAuthenticating}
            className="google-button"
            style={{
              ...styles.googleButton,
              opacity: isAuthenticating ? 0.6 : 1,
              cursor: isAuthenticating ? 'not-allowed' : 'pointer',
            }}
          >
            <svg style={styles.googleIcon} viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            {isAuthenticating ? 'Signing in...' : 'Continue with Google'}
          </button>
        </div>

        <div style={styles.divider}>
          <span style={styles.dividerText}>OR</span>
        </div>

        {/* Email/Password Form */}
        <div style={styles.section}>
          <div style={styles.toggleSection}>
            <button
              onClick={() => setIsSignUp(false)}
              style={{
                ...styles.toggleButton,
                ...(isSignUp ? {} : styles.toggleButtonActive)
              }}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsSignUp(true)}
              style={{
                ...styles.toggleButton,
                ...(isSignUp ? styles.toggleButtonActive : {})
              }}
            >
              Sign Up
            </button>
          </div>

          {isSignUp && (
            <input
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isAuthenticating}
              className="auth-input"
              style={styles.input}
            />
          )}

          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isAuthenticating}
            className="auth-input"
            style={styles.input}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleEmailAuth()}
            disabled={isAuthenticating}
            className="auth-input"
            style={styles.input}
          />

          <button
            onClick={handleEmailAuth}
            disabled={isAuthenticating || !email || !password || (isSignUp && !name)}
            className="email-button"
            style={{
              ...styles.emailButton,
              opacity: isAuthenticating || !email || !password || (isSignUp && !name) ? 0.6 : 1,
              cursor: isAuthenticating || !email || !password || (isSignUp && !name) ? 'not-allowed' : 'pointer',
            }}
          >
            {isAuthenticating ? 'Loading...' : (isSignUp ? 'Create Account' : 'Sign In')}
          </button>
        </div>

        <p style={styles.footer}>
          Jumbo is here to listen and support your emotional well-being.
        </p>
      </div>
      
      {/* OAuth Loading Overlay */}
      <OAuthLoadingOverlay show={showOAuthLoading} />
    </GradientBackground>
  );
}

const styles = {
  container: {
    padding: '16px',
    position: 'relative',
    // GradientBackground handles centering now
  },

  card: {
    width: '100%',
    maxWidth: '448px',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '32px',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.3)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    animation: 'slideIn 0.5s ease-out',
  },
  header: {
    textAlign: 'center',
    marginBottom: '32px',
  },
  logoCircle: {
    width: '80px',
    height: '80px',
    margin: '0 auto 16px',
    background: `linear-gradient(135deg, ${theme.colors.primary[500]} 0%, ${theme.colors.primary[600]} 100%)`,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '40px',
    backgroundImage: 'url(/jumbo-logo.png)',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  },
  title: {
    fontSize: '36px',
    fontWeight: 'bold',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    color: 'white',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '14px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    color: 'rgba(255, 255, 255, 0.8)',
    margin: 0,
  },
  section: {
    marginBottom: '24px',
  },
  googleButton: {
    width: '100%',
    padding: '12px 16px',
    background: 'rgba(255, 255, 255, 0.9)',
    color: '#374151',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '12px',
    fontWeight: '500',
    fontSize: '16px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    transition: 'all 0.3s',
  },
  googleIcon: {
    width: '20px',
    height: '20px',
  },
  divider: {
    display: 'flex',
    alignItems: 'center',
    margin: '24px 0',
  },
  dividerText: {
    flex: 1,
    textAlign: 'center',
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: '12px',
    fontWeight: '600',
    position: 'relative',
  },
  toggleSection: {
    display: 'flex',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '12px',
    padding: '4px',
    marginBottom: '16px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  toggleButton: {
    flex: 1,
    padding: '8px 16px',
    background: 'transparent',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    color: 'rgba(255, 255, 255, 0.8)',
    transition: 'all 0.3s',
  },
  toggleButtonActive: {
    background: 'rgba(255, 255, 255, 0.9)',
    color: '#1e40af',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    fontSize: '16px',
    marginBottom: '12px',
    outline: 'none',
    transition: 'all 0.3s',
    boxSizing: 'border-box',
    background: 'rgba(255, 255, 255, 0.9)',
    color: '#1e40af',
  },
  emailButton: {
    width: '100%',
    padding: '12px 16px',
    background: `linear-gradient(to right, ${theme.colors.primary[600]}, ${theme.colors.primary[500]})`,
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    fontWeight: '600',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  errorBox: {
    background: 'rgba(239, 68, 68, 0.2)',
    border: '1px solid rgba(239, 68, 68, 0.4)',
    borderRadius: '12px',
    padding: '12px 16px',
    marginBottom: '16px',
    backdropFilter: 'blur(10px)',
  },
  errorText: {
    color: '#fca5a5',
    fontSize: '14px',
    margin: 0,
    fontWeight: '500',
  },
  footer: {
    textAlign: 'center',
    fontSize: '12px',
    color: 'rgba(255, 255, 255, 0.6)',
    margin: 0,
    marginTop: '24px',
  },
};

export default AuthPageSupabase;