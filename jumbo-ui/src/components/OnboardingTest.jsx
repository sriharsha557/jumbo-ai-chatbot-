import React, { useState } from 'react';
import { supabase } from '../supabaseClient';

const OnboardingTest = () => {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const checkUser = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    setUser(user);
    return user;
  };

  const resetOnboarding = async () => {
    setLoading(true);
    try {
      // Clear localStorage onboarding data
      localStorage.removeItem('jumbo_onboarding_data');
      localStorage.removeItem('jumbo_onboarding_completed');
      
      setStatus('✅ Onboarding reset successfully! Refresh the page to see onboarding flow.');
    } catch (error) {
      setStatus(`❌ Error: ${error.message}`);
    }
    setLoading(false);
  };

  const checkOnboardingStatus = async () => {
    setLoading(true);
    try {
      // Check localStorage for onboarding data
      const onboardingData = localStorage.getItem('jumbo_onboarding_data');
      const onboardingCompleted = localStorage.getItem('jumbo_onboarding_completed');
      const userData = localStorage.getItem('jumbo_user');
      
      const status = {
        completed: onboardingCompleted === 'true',
        onboarding_data: onboardingData ? JSON.parse(onboardingData) : {},
        user: userData ? JSON.parse(userData) : null
      };
      
      setStatus(`📊 Onboarding Status: ${JSON.stringify(status, null, 2)}`);
    } catch (error) {
      setStatus(`❌ Error: ${error.message}`);
    }
    setLoading(false);
  };

  return (
    <div style={{ 
      padding: '40px', 
      maxWidth: '600px', 
      margin: '0 auto',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h2>🧪 Onboarding Test Panel</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <p><strong>Current User:</strong> {user?.email || 'Not logged in'}</p>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button 
          onClick={checkOnboardingStatus}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Checking...' : 'Check Status'}
        </button>

        <button 
          onClick={resetOnboarding}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Resetting...' : 'Reset Onboarding'}
        </button>
      </div>

      {status && (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '5px',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '14px'
        }}>
          {status}
        </div>
      )}

      <div style={{ marginTop: '30px', fontSize: '14px', color: '#666' }}>
        <h3>Instructions:</h3>
        <ol>
          <li>Make sure you're logged in</li>
          <li>Click "Check Status" to see current onboarding state</li>
          <li>Click "Reset Onboarding" to clear onboarding data</li>
          <li>Refresh the page to trigger onboarding flow</li>
        </ol>
      </div>
    </div>
  );
};

export default OnboardingTest;