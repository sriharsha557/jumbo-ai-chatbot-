import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import ChatPage from './components/ChatPage';
import AuthPage from './components/AuthPageSupabase';
import LandingPage from './components/LandingPage';

import OnboardingFlow from './components/OnboardingFlow';

import ProfilePage from './components/ProfilePage';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('landing'); // Always start with landing
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);

  const checkOnboardingStatus = async (userData) => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || (() => {
        if (process.env.NODE_ENV === 'production') {
          console.error('❌ REACT_APP_API_URL not set in production!');
          throw new Error('API_URL not configured for production');
        }
        return 'http://localhost:5000/api/v1';
      })();
      console.log('🔍 API URL being used:', apiUrl);
      
      const response = await fetch(`${apiUrl}/onboarding/status`, {
        headers: {
          'Authorization': `Bearer ${userData.access_token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.completed) {
          setCurrentPage('chat');
          setNeedsOnboarding(false);
        } else {
          setCurrentPage('onboarding');
          setNeedsOnboarding(true);
        }
      } else {
        // If onboarding API fails, assume onboarding needed
        setCurrentPage('onboarding');
        setNeedsOnboarding(true);
      }
    } catch (error) {
      console.log('Onboarding status check error:', error);
      // Default to onboarding if check fails
      setCurrentPage('onboarding');
      setNeedsOnboarding(true);
    }
  };

  const handleOnboardingComplete = () => {
    setNeedsOnboarding(false);
    setCurrentPage('chat');
    
    // Store onboarding completion status
    localStorage.setItem('jumbo_onboarding_completed', 'true');
  };

  const handleLogout = async () => {
    try {
      // Use Supabase signOut for Google OAuth
      const { supabase } = await import('./supabaseClient');
      await supabase.auth.signOut();
    } catch (error) {
      console.log('Logout error:', error);
    }
    
    // Clear localStorage
    localStorage.removeItem('jumbo_user');
    localStorage.removeItem('jumbo_onboarding_completed');
    
    setCurrentUser(null);
    setCurrentPage('landing');
    setNeedsOnboarding(false);
  };

  // Initialize app - check for Supabase session and stored user
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const { supabase } = await import('./supabaseClient');
        
        // Check for Supabase session (for Google OAuth)
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          console.log('Found Supabase session:', session.user);
          const userData = {
            id: session.user.id,
            email: session.user.email,
            name: session.user.user_metadata?.full_name || 
                  session.user.user_metadata?.name || 
                  session.user.email?.split('@')[0] || 'User',
            access_token: session.access_token
          };
          
          // Store user in localStorage
          localStorage.setItem('jumbo_user', JSON.stringify(userData));
          
          setCurrentUser(userData);
          
          // Check onboarding status from backend
          await checkOnboardingStatus(userData);
        } else {
          // Check if user is stored in localStorage (fallback)
          const storedUser = localStorage.getItem('jumbo_user');
          const storedOnboardingStatus = localStorage.getItem('jumbo_onboarding_completed');
          
          if (storedUser) {
            const userData = JSON.parse(storedUser);
            setCurrentUser(userData);
            
            // Check onboarding status from backend
            await checkOnboardingStatus(userData);
          }
        }

        // Listen for auth state changes (for Google OAuth callback)
        const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
          console.log('Auth state changed:', event, session);
          
          if (event === 'SIGNED_IN' && session?.user) {
            const userData = {
              id: session.user.id,
              email: session.user.email,
              name: session.user.user_metadata?.full_name || 
                    session.user.user_metadata?.name || 
                    session.user.email?.split('@')[0] || 'User',
              access_token: session.access_token
            };
            
            // Store user in localStorage
            localStorage.setItem('jumbo_user', JSON.stringify(userData));
            
            setCurrentUser(userData);
            
            // For new Google login, go to onboarding
            setCurrentPage('onboarding');
            setNeedsOnboarding(true);
          }
          
          if (event === 'SIGNED_OUT') {
            localStorage.removeItem('jumbo_user');
            localStorage.removeItem('jumbo_onboarding_completed');
            setCurrentUser(null);
            setCurrentPage('landing');
            setNeedsOnboarding(false);
          }
        });

        setIsLoading(false);

        // Cleanup subscription on unmount
        return () => {
          subscription.unsubscribe();
        };
      } catch (error) {
        console.log('Auth initialization error:', error);
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const handleUserLogin = (user) => {
    console.log('App received user login:', user);
    setCurrentUser(user);
    
    // For now, assume new users need onboarding
    // TODO: Fix Flask API authentication to properly check onboarding status
    console.log('Setting up onboarding for new user');
    setCurrentPage('onboarding');
    setNeedsOnboarding(true);
    
    // Temporarily comment out the API call until Flask auth is fixed
    // checkOnboardingStatus(user);
  };

  const handleGetStarted = () => {
    setCurrentPage('auth');
  };

  // Show loading state while checking for existing session
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(135deg, #0c1426 0%, #0ea5e9 100%)',
        color: 'white',
        fontSize: '18px'
      }}>
        Loading Jumbo...
      </div>
    );
  }

  // If no user, show landing or auth page
  if (!currentUser) {
    if (currentPage === 'auth') {
      return <AuthPage onUserLogin={handleUserLogin} />;
    }
    return <LandingPage onGetStarted={handleGetStarted} />;
  }

  // If user needs onboarding, show onboarding flow
  if (needsOnboarding && currentPage === 'onboarding') {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  // If user logged in, show main app with navigation
  return (
    <>
      <Navigation 
        currentPage={currentPage} 
        onNavigate={setCurrentPage}
        userName={currentUser.name}
        onLogout={handleLogout}
      />
      
      <main style={{ paddingTop: '0' }}>
        {currentPage === 'chat' && <ChatPage currentUser={currentUser} />}
        {currentPage === 'profile' && <ProfilePage currentUser={currentUser} />}
      </main>
    </>
  );
}

export default App;