import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';
import GradientBackground from './GradientBackground';
import MoodTrend from './MoodTrend';
import { theme } from '../theme/theme';

// Inspirational messages pool (20 messages as per requirements)
const INSPIRATIONAL_MESSAGES = [
  "You've got this. One small step at a time.",
  "Your feelings are valid, always.",
  "Breathe in calm, breathe out doubt.",
  "It's okay not to be okay.",
  "You've made progress simply by showing up today.",
  "Every sunrise brings another chance.",
  "You're stronger than you think.",
  "Small joys build big strength.",
  "Healing is a process, not a race.",
  "Today's a new page — write it with kindness.",
  "Your journey matters, and so do you.",
  "Progress isn't always visible, but it's always happening.",
  "Be gentle with yourself today.",
  "You have survived 100% of your difficult days so far.",
  "This moment is temporary, your strength is permanent.",
  "You are worthy of love and support.",
  "Every feeling you have is teaching you something.",
  "Your courage to continue is inspiring.",
  "You don't have to be perfect to be amazing.",
  "Tomorrow is a fresh start waiting for you."
];

// Mood configuration matching design specifications
const MOOD_OPTIONS = [
  { type: 'very_sad', emoji: '😢', label: 'Very Sad', color: '#ef4444' },
  { type: 'sad', emoji: '🙁', label: 'Sad', color: '#f97316' },
  { type: 'neutral', emoji: '😐', label: 'Neutral', color: '#eab308' },
  { type: 'happy', emoji: '🙂', label: 'Happy', color: '#84cc16' },
  { type: 'very_happy', emoji: '😀', label: 'Very Happy', color: '#10b981' }
];

const WelcomePage = ({ currentUser, onContinueToChat }) => {
  const [selectedMood, setSelectedMood] = useState(null);
  const [inspirationalMessage, setInspirationalMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [preferredName, setPreferredName] = useState('');
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  
  // Cache the name to avoid flickering on tab switches
  const [cachedName, setCachedName] = useState(() => {
    return localStorage.getItem('jumbo_cached_display_name') || '';
  });
  const [showMoodTrend, setShowMoodTrend] = useState(false);

  // Initialize inspirational message, check for existing mood data, and fetch user profile
  useEffect(() => {
    const randomIndex = Math.floor(Math.random() * INSPIRATIONAL_MESSAGES.length);
    setInspirationalMessage(INSPIRATIONAL_MESSAGES[randomIndex]);
    
    // Always show mood trend section - it will handle empty state gracefully
    setShowMoodTrend(true);
    
    // Fetch user's preferred name from profile
    fetchUserProfile();
    
    // iOS Audio Context Fix - Initialize audio on first user interaction
    const initializeAudioForIOS = () => {
      if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        console.log('🍎 iOS detected - initializing audio context');
        // Create a silent audio context to enable audio
        try {
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          if (audioContext.state === 'suspended') {
            audioContext.resume().then(() => {
              console.log('🍎 iOS audio context resumed');
            });
          }
        } catch (error) {
          console.warn('🍎 iOS audio context initialization failed:', error);
        }
      }
    };
    
    // Add listeners for iOS audio initialization
    document.addEventListener('click', initializeAudioForIOS, { once: true });
    document.addEventListener('touchstart', initializeAudioForIOS, { once: true });
    
    return () => {
      document.removeEventListener('click', initializeAudioForIOS);
      document.removeEventListener('touchstart', initializeAudioForIOS);
    };
  }, []);

  const fetchUserProfile = async () => {
    // Only show loading if we don't have cached name
    if (!cachedName) {
      setIsLoadingProfile(true);
    }
    try {
      const apiUrl = process.env.REACT_APP_API_URL || (() => {
        if (process.env.NODE_ENV === 'production') {
          console.error('❌ REACT_APP_API_URL not set in production!');
          throw new Error('API_URL not configured for production');
        }
        return 'http://localhost:5000/api/v1';
      })();
      
      const headers = { 'Content-Type': 'application/json' };
      
      // Add Authorization header if we have access token
      if (currentUser.access_token) {
        headers['Authorization'] = `Bearer ${currentUser.access_token}`;
        console.log('🔑 Using access token for preferences API');
      } else {
        console.warn('⚠️ No access token available for preferences API');
      }
      
      console.log('🌐 Fetching preferences from:', `${apiUrl}/onboarding/preferences`);
      
      const response = await fetch(`${apiUrl}/onboarding/preferences`, {
        method: 'GET',
        headers
      });
      
      console.log('📡 Preferences API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.preferences) {
          // Use display_name from onboarding preferences
          const displayName = data.preferences.display_name || 
                             currentUser.name || 
                             currentUser.email?.split('@')[0] || 
                             'there';
          setPreferredName(displayName);
          setCachedName(displayName);
          localStorage.setItem('jumbo_cached_display_name', displayName);
          console.log('✅ User preferences loaded:', { 
            displayName, 
            preferences: data.preferences,
            fullApiResponse: data 
          });
        } else {
          // Fallback to current user name
          console.log('⚠️ No preferences found, using fallback name');
          const fallbackName = getDefaultName();
          setPreferredName(fallbackName);
          setCachedName(fallbackName);
          localStorage.setItem('jumbo_cached_display_name', fallbackName);
        }
      } else {
        console.warn('⚠️ Failed to fetch user profile, using fallback name');
        const fallbackName = getDefaultName();
        setPreferredName(fallbackName);
        setCachedName(fallbackName);
        localStorage.setItem('jumbo_cached_display_name', fallbackName);
      }
    } catch (error) {
      console.warn('⚠️ Error fetching user profile:', error);
      const fallbackName = getDefaultName();
      setPreferredName(fallbackName);
      setCachedName(fallbackName);
      localStorage.setItem('jumbo_cached_display_name', fallbackName);
    } finally {
      setIsLoadingProfile(false);
    }
  };

  const getDefaultName = () => {
    // Fallback logic: use current name, then extract from email, then 'there'
    return currentUser.name ? 
           currentUser.name.split(' ')[0] : 
           currentUser.email?.split('@')[0] || 
           'there';
  };

  // Handle mood selection
  const handleMoodSelect = async (moodType) => {
    setSelectedMood(moodType);
    setError(null);
    
    // Store mood data locally for immediate feedback
    const moodEntry = {
      id: Date.now().toString(),
      user_id: currentUser.id,
      mood_type: moodType,
      timestamp: new Date().toISOString(),
      session_id: `session_${Date.now()}`
    };
    
    // Store in localStorage for persistence (fallback)
    try {
      const existingMoods = JSON.parse(localStorage.getItem('jumbo_mood_history') || '[]');
      const updatedMoods = [...existingMoods, moodEntry];
      localStorage.setItem('jumbo_mood_history', JSON.stringify(updatedMoods));
      localStorage.setItem('jumbo_last_mood', JSON.stringify(moodEntry));
    } catch (error) {
      console.error('Error storing mood data locally:', error);
    }
    
    // Send to API
    try {
      const apiUrl = process.env.REACT_APP_API_URL || (() => {
        if (process.env.NODE_ENV === 'production') {
          console.error('❌ REACT_APP_API_URL not set in production!');
          throw new Error('API_URL not configured for production');
        }
        return 'http://localhost:5000/api/v1';
      })();
      
      const headers = { 'Content-Type': 'application/json' };
      
      // Add Authorization header if we have access token
      if (currentUser.access_token) {
        headers['Authorization'] = `Bearer ${currentUser.access_token}`;
      }
      
      const response = await fetch(`${apiUrl}/mood/entry`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          mood_type: moodType,
          timestamp: moodEntry.timestamp,
          session_id: moodEntry.session_id,
          notes: ''
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Mood entry saved to API:', data);
      } else {
        const errorData = await response.text();
        console.warn('⚠️ Failed to save mood to API:', errorData);
        // Don't show error to user since localStorage fallback worked
      }
    } catch (apiError) {
      console.warn('⚠️ API call failed, using localStorage fallback:', apiError);
      // Don't show error to user since localStorage fallback worked
    }
  };

  // Handle continue to chat
  const handleContinueToChat = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Prepare mood data to pass to chat interface
      const moodData = selectedMood ? {
        mood_type: selectedMood,
        timestamp: new Date().toISOString(),
        user_id: currentUser.id
      } : null;

      // TODO: Send mood data to API endpoint when implemented
      // For now, we'll pass it directly to the chat interface
      
      // Call the navigation callback with mood data
      onContinueToChat(moodData);
    } catch (error) {
      console.error('Error continuing to chat:', error);
      setError('Failed to continue. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Use preferred name from profile, cached name while loading, or fallback to default
  const displayName = preferredName || (isLoadingProfile ? cachedName : '') || getDefaultName();

  return (
    <GradientBackground variant="copilot" animated={true} style={styles.container}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes moodHover {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-3px); }
        }
        .mood-option:hover {
          animation: moodHover 0.3s ease;
        }
        @media (max-width: 768px) {
          .welcome-content {
            padding: 20px 16px !important;
          }
          .welcome-title {
            font-size: 2.5rem !important;
          }
          .welcome-subtitle {
            font-size: 1rem !important;
          }
          .mood-selector {
            gap: 8px !important;
          }
          .mood-option {
            min-width: 70px !important;
            padding: 15px 8px !important;
          }
          .mood-emoji {
            font-size: 28px !important;
          }
          .mood-label {
            font-size: 11px !important;
          }
        }
        @media (max-width: 480px) {
          .welcome-title {
            font-size: 2rem !important;
          }
          .welcome-subtitle {
            font-size: 0.9rem !important;
          }
          .mood-selector {
            gap: 6px !important;
          }
          .mood-option {
            min-width: 60px !important;
            padding: 12px 6px !important;
          }
          .mood-emoji {
            font-size: 24px !important;
          }
        }
        
        /* Screen reader only text */
        .sr-only {
          position: absolute;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          overflow: hidden;
          clip: rect(0, 0, 0, 0);
          white-space: nowrap;
          border: 0;
        }
        
        /* High contrast mode support */
        @media (prefers-contrast: high) {
          .mood-option {
            border-width: 3px !important;
          }
          .mood-option:focus {
            outline: 3px solid currentColor !important;
            outline-offset: 2px !important;
          }
        }
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          .mood-option {
            transition: none !important;
          }
          .mood-option:hover {
            animation: none !important;
          }
        }
        
        /* Focus styles for better keyboard navigation */
        .mood-option:focus {
          outline: 2px solid #ffffff;
          outline-offset: 2px;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
        }
      `}</style>
      
      <div style={styles.content} className="welcome-content">
        {/* Skip link for keyboard users */}
        <a 
          href="#main-content" 
          style={styles.skipLink}
          className="skip-link"
          onFocus={(e) => e.target.style.transform = 'translateY(0)'}
          onBlur={(e) => e.target.style.transform = 'translateY(-100%)'}
        >
          Skip to main content
        </a>
        
        {/* Personal Greeting */}
        <header style={styles.greetingSection} role="banner">
          <div style={styles.logoContainer}>
            <img 
              src="/jumbo-logo.png" 
              alt="Jumbo Logo" 
              style={styles.logo}
            />
          </div>
          
          <h1 style={styles.title} className="welcome-title">
            {isLoadingProfile && !cachedName ? 'Hey! 🌼' : `Hey ${displayName}! 🌼`}
          </h1>
          

          
          <p style={styles.subtitle} className="welcome-subtitle">
            How are you feeling today?
          </p>
        </header>

        {/* Main Content */}
        <main id="main-content" style={styles.mainContent}>
          {/* Mood Selector */}
          <section style={styles.moodSection} role="group" aria-labelledby="mood-instructions">
          <p id="mood-instructions" style={styles.moodInstructions}>
            Tap the emoji that best describes how you feel right now
          </p>
          
          <div 
            style={styles.moodSelector} 
            className="mood-selector"
            role="radiogroup"
            aria-labelledby="mood-instructions"
            aria-required="false"
          >
            {MOOD_OPTIONS.map((mood, index) => (
              <button
                key={mood.type}
                type="button"
                role="radio"
                aria-checked={selectedMood === mood.type}
                aria-describedby={selectedMood === mood.type ? 'mood-feedback' : undefined}
                style={{
                  ...styles.moodOption,
                  ...(selectedMood === mood.type ? styles.moodOptionSelected : {}),
                  borderColor: selectedMood === mood.type ? mood.color : 'rgba(255, 255, 255, 0.2)'
                }}
                onClick={() => handleMoodSelect(mood.type)}
                onKeyDown={(e) => {
                  // Handle keyboard navigation
                  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prevIndex = index > 0 ? index - 1 : MOOD_OPTIONS.length - 1;
                    const prevButton = document.querySelector(`[data-mood-index="${prevIndex}"]`);
                    prevButton?.focus();
                  } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                    e.preventDefault();
                    const nextIndex = index < MOOD_OPTIONS.length - 1 ? index + 1 : 0;
                    const nextButton = document.querySelector(`[data-mood-index="${nextIndex}"]`);
                    nextButton?.focus();
                  } else if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleMoodSelect(mood.type);
                  }
                }}
                className="mood-option"
                aria-label={`${mood.label} mood. ${mood.emoji}`}
                data-mood-index={index}
                tabIndex={selectedMood === mood.type ? 0 : -1}
              >
                <span style={styles.moodEmoji} className="mood-emoji" aria-hidden="true">
                  {mood.emoji}
                </span>
                <span style={styles.moodLabel} className="mood-label">
                  {mood.label}
                </span>
              </button>
            ))}
          </div>

          {selectedMood && (
            <div 
              id="mood-feedback"
              style={styles.encouragementMessage}
              role="status"
              aria-live="polite"
              aria-atomic="true"
            >
              <p style={styles.encouragementText}>
                <span aria-hidden="true">💛</span>
                <span className="sr-only">Heart emoji. </span>
                Thanks for sharing that you're feeling {selectedMood.replace('_', ' ')}. I'm here to support you wherever you are.
              </p>
            </div>
          )}
          </section>

          {/* Mood Trend Visualization (Optional) */}
          {showMoodTrend && (
            <section style={styles.moodTrendSection} aria-labelledby="trend-heading">
              <h2 id="trend-heading" className="sr-only">Mood Trend</h2>
              <MoodTrend currentUser={currentUser} days={7} />
            </section>
          )}

          {/* Inspirational Message */}
          <section style={styles.inspirationalSection} aria-labelledby="inspiration-heading">
            <h2 id="inspiration-heading" className="sr-only">Daily Inspiration</h2>
            <div style={styles.inspirationalCard}>
              <p style={styles.inspirationalText}>
                "{inspirationalMessage}"
              </p>
            </div>
          </section>

          {/* Navigation CTA */}
          <section style={styles.navigationSection} aria-labelledby="navigation-heading">
            <h2 id="navigation-heading" className="sr-only">Continue to Chat</h2>
            <button 
            onClick={handleContinueToChat}
            disabled={isLoading}
            style={{
              ...styles.continueButton,
              opacity: isLoading ? 0.6 : 1,
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 20px 25px -5px rgba(139, 92, 246, 0.3)';
              }
            }}
            aria-describedby="continue-description"
            aria-live="polite"
          >
            <Sparkles size={20} style={{ marginRight: '8px' }} aria-hidden="true" />
            {isLoading ? 'Loading...' : 'Continue to Chat'}
          </button>
          
            <p id="continue-description" style={styles.supportText}>
              Jumbo is here to listen and support you.
            </p>
          </section>
        </main>

        {/* Error Message */}
        {error && (
          <div style={styles.errorMessage}>
            <p style={styles.errorText}>{error}</p>
          </div>
        )}
      </div>
    </GradientBackground>
  );
};

const styles = {
  container: {
    // GradientBackground handles the container
  },
  content: {
    width: '100%',
    maxWidth: '672px',
    padding: '40px 24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
    margin: '0 auto',
    animation: 'fadeIn 0.6s ease-out',
  },
  skipLink: {
    position: 'absolute',
    top: '-40px',
    left: '6px',
    background: '#000',
    color: '#fff',
    padding: '8px',
    textDecoration: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    fontWeight: '600',
    zIndex: 1000,
    transform: 'translateY(-100%)',
    transition: 'transform 0.3s',
  },
  mainContent: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  greetingSection: {
    marginBottom: '40px',
  },
  logoContainer: {
    marginBottom: '24px',
  },
  logo: {
    width: '100px',
    height: '100px',
    borderRadius: '50%',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
    background: 'rgba(255, 255, 255, 0.9)',
    padding: '16px',
  },
  title: {
    fontSize: '3rem',
    fontWeight: '700',
    color: 'white',
    marginBottom: '16px',
    textShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  subtitle: {
    fontSize: '1.25rem',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '0',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    fontWeight: '400',
  },
  moodSection: {
    marginBottom: '40px',
    width: '100%',
  },
  moodInstructions: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '24px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  moodSelector: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '12px',
    marginBottom: '20px',
    flexWrap: 'wrap',
  },
  moodOption: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px 10px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '16px',
    background: 'rgba(255, 255, 255, 0.05)',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    minWidth: '80px',
    outline: 'none',
  },
  moodOptionSelected: {
    background: 'rgba(139, 92, 246, 0.2)',
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 25px -5px rgba(139, 92, 246, 0.3)',
  },
  moodEmoji: {
    fontSize: '32px',
    marginBottom: '8px',
  },
  moodLabel: {
    fontSize: '12px',
    color: 'rgba(255, 255, 255, 0.8)',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  encouragementMessage: {
    background: 'rgba(139, 92, 246, 0.2)',
    border: '1px solid rgba(139, 92, 246, 0.3)',
    padding: '15px 20px',
    borderRadius: '12px',
    margin: '20px 0',
    animation: 'fadeIn 0.5s ease-out',
  },
  encouragementText: {
    margin: 0,
    color: 'white',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  moodTrendSection: {
    marginBottom: '32px',
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
  },
  inspirationalSection: {
    marginBottom: '40px',
    width: '100%',
  },
  inspirationalCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '24px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
  },
  inspirationalText: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.95)',
    lineHeight: '1.6',
    fontStyle: 'italic',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    fontWeight: '400',
  },
  navigationSection: {
    marginBottom: '20px',
  },
  continueButton: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '16px 32px',
    fontSize: '1.1rem',
    fontWeight: '600',
    color: 'white',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
    border: 'none',
    borderRadius: '50px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 20px 25px -5px rgba(139, 92, 246, 0.3)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    marginBottom: '16px',
    outline: 'none',
  },
  supportText: {
    fontSize: '0.95rem',
    color: 'rgba(255, 255, 255, 0.7)',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  errorMessage: {
    background: 'rgba(239, 68, 68, 0.2)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    padding: '12px 20px',
    borderRadius: '12px',
    marginTop: '20px',
  },
  errorText: {
    margin: 0,
    color: '#fca5a5',
    fontSize: '14px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
};

export default WelcomePage;