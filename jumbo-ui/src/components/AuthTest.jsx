import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

function AuthTest() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      console.log('Initial session:', session);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('Auth event:', event, session);
        setUser(session?.user ?? null);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    setLoading(true);
    try {
      console.log('Starting Google OAuth...');
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: 'http://localhost:3000',
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      });
      console.log('Google sign in result:', { data, error });
      if (error) {
        console.error('OAuth error:', error);
        throw error;
      }
    } catch (error) {
      console.error('Error:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) console.error('Error signing out:', error);
  };

  if (user) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>✅ Logged in!</h2>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Name:</strong> {user.user_metadata?.full_name || 'No name'}</p>
        <p><strong>ID:</strong> {user.id}</p>
        <button onClick={signOut}>Sign Out</button>
        <pre>{JSON.stringify(user, null, 2)}</pre>
      </div>
    );
  }

  const testEmailSignUp = async () => {
    setLoading(true);
    try {
      // Use a more realistic email for testing
      const testEmail = `test${Date.now()}@gmail.com`;
      const { data, error } = await supabase.auth.signUp({
        email: testEmail,
        password: 'password123',
        options: {
          data: {
            full_name: 'Test User'
          }
        }
      });
      console.log('Email signup result:', { data, error });
      if (error) throw error;
      alert('Check your email for verification!');
    } catch (error) {
      console.error('Email signup error:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>🔐 Auth Test</h2>
      
      <div style={{ marginBottom: '10px' }}>
        <button 
          onClick={signInWithGoogle} 
          disabled={loading}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#4285f4',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginRight: '10px'
          }}
        >
          {loading ? 'Loading...' : 'Sign in with Google'}
        </button>
        
        <button 
          onClick={testEmailSignUp} 
          disabled={loading}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          Test Email Signup
        </button>
      </div>
      
      <p><strong>Supabase URL:</strong> {process.env.REACT_APP_SUPABASE_URL}</p>
      <p><strong>Has Anon Key:</strong> {process.env.REACT_APP_SUPABASE_ANON_KEY ? 'Yes' : 'No'}</p>
    </div>
  );
}

export default AuthTest;