import React, { useState, useEffect } from 'react';

// import { auth } from '../lib/supabase'; // Uncomment when Supabase is configured

const API_URL = 'http://localhost:5000/api';

function AuthPage({ onUserLogin }) {
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [userName, setUserName] = useState('');
  const [userLanguage, setUserLanguage] = useState('en');
  const [existingUsers, setExistingUsers] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchExistingUsers();
  }, []);

  const fetchExistingUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/users/list`);
      const data = await response.json();
      if (data.success) {
        setExistingUsers(data.users);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const loginUser = async (name) => {
    setIsAuthenticating(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      const data = await response.json();
      if (data.success) {
        onUserLogin(data.user);
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError('Login failed. Please try again.');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const registerUser = async () => {
    if (!userName.trim()) {
      setError('Please enter a name');
      return;
    }

    setIsAuthenticating(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: userName, language: userLanguage })
      });
      const data = await response.json();
      if (data.success) {
        onUserLogin(data.user);
        setExistingUsers([...existingUsers, userName]);
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError('Registration failed. Please try again.');
    } finally {
      setIsAuthenticating(false);
    }
  };

  return (
    <div style={styles.container}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>

      <div style={styles.background} />

      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.logoCircle}>🐘</div>
          <h1 style={styles.title}>JUMBO</h1>
          <p style={styles.subtitle}>Your Emotional Support Companion</p>
        </div>

        {error && (
          <div style={styles.errorBox}>
            <p style={styles.errorText}>{error}</p>
          </div>
        )}

        {existingUsers.length > 0 && (
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Welcome Back</h2>
            <div style={styles.userGrid}>
              {existingUsers.map(user => (
                <button
                  key={user}
                  onClick={() => loginUser(user)}
                  disabled={isAuthenticating}
                  style={{
                    ...styles.userButton,
                    opacity: isAuthenticating ? 0.5 : 1,
                  }}
                >
                  {user}
                </button>
              ))}
            </div>
            <div style={styles.divider}>OR</div>
          </div>
        )}

        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>New User</h2>
          
          <input
            type="text"
            placeholder="Enter your name"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && registerUser()}
            disabled={isAuthenticating}
            style={styles.input}
          />

          <select
            value={userLanguage}
            onChange={(e) => setUserLanguage(e.target.value)}
            disabled={isAuthenticating}
            style={styles.select}
          >
            <option value="en">English</option>
            <option value="te">Telugu</option>
            <option value="hi">Hindi</option>
          </select>

          <button
            onClick={registerUser}
            disabled={isAuthenticating || !userName.trim()}
            style={{
              ...styles.registerButton,
              opacity: isAuthenticating || !userName.trim() ? 0.6 : 1,
              cursor: isAuthenticating || !userName.trim() ? 'not-allowed' : 'pointer',
            }}
          >
            {isAuthenticating ? 'Loading...' : 'Start Chatting'}
          </button>
        </div>

        <p style={styles.footer}>
          Jumbo is here to listen and support your emotional well-being.
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '16px',
    position: 'relative',
  },
  background: {
    position: 'absolute',
    inset: 0,
    background: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 50%, #fce7f3 100%)',
    zIndex: -1,
  },
  card: {
    width: '100%',
    maxWidth: '448px',
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '32px',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.15)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
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
    background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '40px',
  },
  title: {
    fontSize: '36px',
    fontWeight: 'bold',
    background: 'linear-gradient(to right, #9333ea, #ec4899)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '14px',
    color: '#6b7280',
    margin: 0,
  },
  section: {
    marginBottom: '24px',
  },
  sectionTitle: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
    marginBottom: '12px',
  },
  userGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '8px',
    marginBottom: '16px',
  },
  userButton: {
    padding: '8px 16px',
    background: 'linear-gradient(to right, #f3e8ff, #fce7f3)',
    color: '#7c3aed',
    border: 'none',
    borderRadius: '12px',
    fontWeight: '500',
    cursor: 'pointer',
    fontSize: '13px',
    transition: 'all 0.3s',
  },
  divider: {
    textAlign: 'center',
    color: '#d1d5db',
    fontSize: '12px',
    fontWeight: '600',
    marginBottom: '16px',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #e9d5ff',
    borderRadius: '12px',
    fontSize: '16px',
    marginBottom: '12px',
    outline: 'none',
    transition: 'all 0.3s',
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #e9d5ff',
    borderRadius: '12px',
    fontSize: '16px',
    marginBottom: '12px',
    outline: 'none',
    boxSizing: 'border-box',
    cursor: 'pointer',
  },
  registerButton: {
    width: '100%',
    padding: '12px 16px',
    background: 'linear-gradient(to right, #9333ea, #ec4899)',
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    fontWeight: '600',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  errorBox: {
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '12px',
    padding: '12px 16px',
    marginBottom: '16px',
  },
  errorText: {
    color: '#dc2626',
    fontSize: '14px',
    margin: 0,
  },
  footer: {
    textAlign: 'center',
    fontSize: '12px',
    color: '#9ca3af',
    margin: 0,
    marginTop: '24px',
  },
};

export default AuthPage;