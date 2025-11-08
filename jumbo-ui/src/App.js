import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import Navigation from './components/Navigation';
import ChatPage from './components/ChatPage';
import AuthPage from './components/AuthPageSupabase';
import LandingPage from './components/LandingPage';
import AboutPage from './components/AboutPage';
import HelpPage from './components/HelpPage';
import OnboardingFlow from './components/OnboardingFlow';
import WelcomePage from './components/WelcomePage';
import ProfilePage from './components/ProfilePage';
import './App.css';

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [needsOnboarding, setNeedsOnboarding] = useState(() => {
    // Initialize from localStorage to prevent flashing
    const storedStatus = localStorage.getItem('jumbo_onboarding_completed');
    return storedStatus !== 'true'; // Need onboarding if not completed
  });
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false);
  
  const [welcomeShownThisSession, setWelcomeShownThisSession] = useState(() => {
    // Check if welcome was shown in this session
    const welcomeShown = sessionStorage.getItem('jumbo_welcome_shown') === 'true';
    const welcomeTimestamp = sessionStorage.getItem('jumbo_welcome_timestamp');
    
    // If welcome was shown and has a timestamp, consider it valid
    // This prevents re-showing welcome on tab switch
    if (welcomeShown && welcomeTimestamp) {
      const timeSinceWelcome = Date.now() - parseInt(welcomeTimestamp);
      // If less than 1 hour, consider welcome still valid
      if (timeSinceWelcome < 3600000) {
        return true;
      }
    }
    
    return welcomeShown;
  });
  const [isScrolled, setIsScrolled] = useState(false);

  const checkOnboardingStatus = async (userData) => {
    // First check localStorage for quick response (no loading state)
    const storedOnboardingStatus = localStorage.getItem('jumbo_onboarding_completed');
    
    if (storedOnboardingStatus === 'true') {
      console.log('✅ Onboarding completed (from localStorage)');
      setNeedsOnboarding(false);
      return; // Exit early, no need to check API
    }
    
    // Only set loading state if we need to check API
    setIsCheckingOnboarding(true);
    
    try {
      
      // If not in localStorage, check with API
      const apiUrl = process.env.REACT_APP_API_URL || (() => {
        if (process.env.NODE_ENV === 'production') {
          console.error('❌ REACT_APP_API_URL not set in production!');
          throw new Error('API_URL not configured for production');
        }
        return 'http://localhost:5000/api/v1';
      })();
      
      console.log('🔍 Checking onboarding status with API:', apiUrl);
      
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
          console.log('✅ Onboarding completed (from API)');
          localStorage.setItem('jumbo_onboarding_completed', 'true');
          setNeedsOnboarding(false);
        } else {
          console.log('⏳ Onboarding needed');
          setNeedsOnboarding(true);
        }
      } else {
        console.log('⚠️ API check failed, assuming onboarding needed');
        setNeedsOnboarding(true);
      }
    } catch (error) {
      console.log('❌ Onboarding status check error:', error);
      // Check localStorage as fallback
      const storedOnboardingStatus = localStorage.getItem('jumbo_onboarding_completed');
      if (storedOnboardingStatus === 'true') {
        console.log('✅ Using localStorage fallback - onboarding completed');
        setNeedsOnboarding(false);
      } else {
        console.log('⏳ Using localStorage fallback - onboarding needed');
        setNeedsOnboarding(true);
      }
    } finally {
      setIsCheckingOnboarding(false);
    }
  };

  const handleOnboardingComplete = () => {
    console.log('✅ Onboarding completed successfully');
    
    // Store onboarding completion status immediately
    localStorage.setItem('jumbo_onboarding_completed', 'true');
    
    // Update state
    setNeedsOnboarding(false);
    // After onboarding, go to welcome page
    navigate('/welcome');
    setIsCheckingOnboarding(false);
  };

  const handleWelcomeComplete = (moodData) => {
    console.log('✅ Welcome page completed', moodData ? 'with mood data' : 'without mood data');
    
    // Mark welcome as shown for this session - use a timestamp to make it more reliable
    setWelcomeShownThisSession(true);
    sessionStorage.setItem('jumbo_welcome_shown', 'true');
    sessionStorage.setItem('jumbo_welcome_timestamp', Date.now().toString());
    
    // Store mood data if provided
    if (moodData) {
      localStorage.setItem('jumbo_current_session_mood', JSON.stringify(moodData));
    }
    
    // Navigate to chat
    navigate('/chat');
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
    localStorage.removeItem('jumbo_current_session_mood');
    localStorage.removeItem('jumbo_mood_history');
    
    setCurrentUser(null);
    navigate('/');
    setNeedsOnboarding(false);
    setWelcomeShownThisSession(false);
  };

  // Add scroll detection for navigation styling
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      setIsScrolled(scrollTop > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Scroll to top when location changes
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

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
          
          // Only handle actual sign-in events, not session refreshes or initial sessions
          if (event === 'SIGNED_IN' && session?.user) {
            const userData = {
              id: session.user.id,
              email: session.user.email,
              name: session.user.user_metadata?.full_name || 
                    session.user.user_metadata?.name || 
                    session.user.email?.split('@')[0] || 'User',
              access_token: session.access_token
            };
            
            // Check if this is a NEW login or just a session refresh
            const existingUser = localStorage.getItem('jumbo_user');
            const isNewLogin = !existingUser || !currentUser;
            
            // Store user in localStorage
            localStorage.setItem('jumbo_user', JSON.stringify(userData));
            
            setCurrentUser(userData);
            
            // Only redirect to onboarding for NEW logins, not session refreshes
            if (isNewLogin) {
              console.log('🆕 New login detected - checking onboarding status');
              // Check if they've completed onboarding before
              const hasCompletedOnboarding = localStorage.getItem('jumbo_onboarding_completed') === 'true';
              
              if (!hasCompletedOnboarding) {
                setNeedsOnboarding(true);
                navigate('/onboarding');
              } else {
                // They've already completed onboarding, go to welcome or chat
                const welcomeShown = sessionStorage.getItem('jumbo_welcome_shown') === 'true';
                if (!welcomeShown) {
                  navigate('/welcome');
                } else {
                  navigate('/chat');
                }
              }
            } else {
              console.log('🔄 Session refresh detected - maintaining current page');
              // Don't navigate, just update the user data
            }
          }
          
          // Handle INITIAL_SESSION - this fires when page loads with existing session
          if (event === 'INITIAL_SESSION' && session?.user) {
            console.log('🔄 Initial session detected - maintaining state');
            // Don't do anything - let the initial useEffect handle this
            // This prevents unnecessary redirects on page load
          }
          
          if (event === 'SIGNED_OUT') {
            localStorage.removeItem('jumbo_user');
            localStorage.removeItem('jumbo_onboarding_completed');
            localStorage.removeItem('jumbo_current_session_mood');
            localStorage.removeItem('jumbo_mood_history');
            sessionStorage.removeItem('jumbo_welcome_shown');
            sessionStorage.removeItem('jumbo_welcome_timestamp');
            setCurrentUser(null);
            navigate('/');
            setNeedsOnboarding(false);
            setWelcomeShownThisSession(false);
          }
        });

        setIsLoading(false);

        // Add window focus listener to prevent unnecessary re-checks
        const handleWindowFocus = () => {
          // Only log focus events, don't re-trigger onboarding checks
          console.log('🔍 Window focused - maintaining current state');
        };

        window.addEventListener('focus', handleWindowFocus);

        // Cleanup subscription and event listeners on unmount
        return () => {
          subscription.unsubscribe();
          window.removeEventListener('focus', handleWindowFocus);
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
    navigate('/onboarding');
    setNeedsOnboarding(true);
    
    // Temporarily comment out the API call until Flask auth is fixed
    // checkOnboardingStatus(user);
  };

  const handleGetStarted = () => {
    navigate('/auth');
  };

  const handleAbout = () => {
    navigate('/about');
  };

  const handleHelp = () => {
    navigate('/help');
  };

  const handleLogin = () => {
    navigate('/auth');
  };

  const handleBackToLanding = () => {
    navigate('/');
  };

  const handleHome = () => {
    navigate('/');
  };

  // Show loading state while checking for existing session or onboarding status
  if (isLoading || isCheckingOnboarding) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(135deg, #0c1426 0%, #0ea5e9 100%)',
        color: 'white',
        fontSize: '18px',
        gap: '16px'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '3px solid rgba(255, 255, 255, 0.3)',
          borderTop: '3px solid white',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
        {isLoading ? 'Loading Jumbo...' : 'Verifying your progress...'}
      </div>
    );
  }

  // Handle routing based on authentication and onboarding status
  if (!currentUser) {
    return (
      <Routes>
        <Route path="/" element={
          <LandingPage 
            onGetStarted={handleGetStarted} 
            onAbout={handleAbout} 
            onHelp={handleHelp} 
            onLogin={handleLogin} 
          />
        } />
        <Route path="/about" element={
          <AboutPage 
            onBack={handleBackToLanding} 
            onHelp={handleHelp} 
            onLogin={handleLogin} 
          />
        } />
        <Route path="/help" element={
          <HelpPage 
            onBack={handleBackToLanding} 
            onLogin={handleLogin} 
          />
        } />
        <Route path="/auth" element={
          <AuthPage onUserLogin={handleUserLogin} />
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  // If user needs onboarding
  if (needsOnboarding) {
    return (
      <Routes>
        <Route path="/onboarding" element={
          <OnboardingFlow onComplete={handleOnboardingComplete} />
        } />
        <Route path="*" element={<Navigate to="/onboarding" replace />} />
      </Routes>
    );
  }

  // If user is explicitly on welcome page, show it
  if (location.pathname === '/welcome') {
    return (
      <Routes>
        <Route path="/welcome" element={
          <WelcomePage 
            currentUser={currentUser} 
            onContinueToChat={handleWelcomeComplete} 
          />
        } />
        <Route path="*" element={<Navigate to="/welcome" replace />} />
      </Routes>
    );
  }
  
  // Only redirect to welcome if user is on root path AND hasn't seen welcome
  // Don't redirect if user is already on /chat or /profile
  const isOnProtectedRoute = location.pathname === '/chat' || location.pathname === '/profile';
  
  if (!welcomeShownThisSession && location.pathname === '/' && !isOnProtectedRoute) {
    return <Navigate to="/welcome" replace />;
  }
  
  // If user is on chat or profile without seeing welcome, mark welcome as shown
  // This handles the case where user navigates directly to /chat
  if (!welcomeShownThisSession && isOnProtectedRoute) {
    console.log('📍 User on protected route without welcome - marking welcome as shown');
    setWelcomeShownThisSession(true);
    sessionStorage.setItem('jumbo_welcome_shown', 'true');
    sessionStorage.setItem('jumbo_welcome_timestamp', Date.now().toString());
  }

  // Authenticated user with main app
  return (
    <>
      <Navigation 
        currentPage={location.pathname.slice(1) || 'chat'} 
        onNavigate={(page) => navigate(`/${page}`)}
        userName={currentUser.name}
        onLogout={handleLogout}
        scrolled={isScrolled}
      />
      
      <main style={{ paddingTop: '80px' }}>
        <Routes>
          <Route path="/chat" element={
            <ChatPage 
              currentUser={currentUser} 
              sessionMoodData={JSON.parse(localStorage.getItem('jumbo_current_session_mood') || 'null')}
            />
          } />
          <Route path="/profile" element={
            <ProfilePage currentUser={currentUser} />
          } />
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
      </main>
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;