import React, { useState, useEffect } from 'react';

const BackendStatus = ({ children }) => {
  const [backendStatus, setBackendStatus] = useState('checking');
  const [retryCount, setRetryCount] = useState(0);

  const checkBackend = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/health`, {
        timeout: 10000 // 10 second timeout
      });
      
      if (response.ok) {
        setBackendStatus('online');
      } else {
        throw new Error('Backend not responding');
      }
    } catch (error) {
      if (retryCount < 3) {
        setBackendStatus('waking');
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          checkBackend();
        }, 5000); // Retry every 5 seconds
      } else {
        setBackendStatus('offline');
      }
    }
  };

  useEffect(() => {
    checkBackend();
  }, []);

  if (backendStatus === 'checking') {
    return (
      <div style={styles.statusContainer}>
        <div style={styles.spinner}></div>
        <p>Connecting to Jumbo...</p>
      </div>
    );
  }

  if (backendStatus === 'waking') {
    return (
      <div style={styles.statusContainer}>
        <div style={styles.spinner}></div>
        <p>Waking up Jumbo's brain... This may take up to 60 seconds.</p>
        <p style={styles.subText}>First visit after inactivity requires a moment to start up.</p>
      </div>
    );
  }

  if (backendStatus === 'offline') {
    return (
      <div style={styles.statusContainer}>
        <p>❌ Unable to connect to Jumbo's backend.</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    );
  }

  return children;
};

const styles = {
  statusContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    background: 'linear-gradient(135deg, #0c1426 0%, #0ea5e9 100%)',
    color: 'white',
    textAlign: 'center',
    padding: '20px'
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid rgba(255,255,255,0.3)',
    borderTop: '4px solid white',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '20px'
  },
  subText: {
    fontSize: '14px',
    opacity: 0.8,
    marginTop: '10px'
  }
};

export default BackendStatus;