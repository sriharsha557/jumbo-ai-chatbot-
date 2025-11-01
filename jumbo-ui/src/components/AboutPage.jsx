import React from 'react';
import { ArrowLeft, Heart, Users, Map, Shield, Smartphone } from 'lucide-react';
import { theme } from '../theme/theme';

function AboutPage({ onBack, onHelp, onHome, onLogin }) {
  const [videoLoaded, setVideoLoaded] = React.useState(false);
  const [videoError, setVideoError] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 100;
      setScrolled(isScrolled);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Attempt to play video manually if autoplay fails
  React.useEffect(() => {
    const video = document.querySelector('video');
    if (video) {
      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.catch(error => {
          console.log('Autoplay prevented:', error);
        });
      }
    }
  }, [videoLoaded]);

  return (
    <div style={styles.container}>
      {/* Background Video */}
      {!videoError && (
        <video
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          style={{
            ...styles.backgroundVideo,
            opacity: videoLoaded ? 0.6 : 0.2,
            transition: 'opacity 1s ease-in-out'
          }}
          onError={(e) => {
            console.log('Video failed to load:', e);
            setVideoError(true);
          }}
          onLoadedData={() => {
            console.log('Video loaded successfully');
            setVideoLoaded(true);
          }}
          onCanPlay={() => {
            console.log('Video can play');
            setVideoLoaded(true);
          }}
          onPlay={() => {
            console.log('Video is playing');
          }}
        >
          <source src="/Jumbo_Preview.mp4" type="video/mp4" />
          <source src="/jumbo-demo.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      )}
      
      {/* Video Overlay for better text readability */}
      <div style={{
        ...styles.videoOverlay,
        background: videoError || !videoLoaded 
          ? 'linear-gradient(135deg, rgba(12, 20, 38, 0.8) 0%, rgba(30, 41, 59, 0.7) 50%, rgba(14, 165, 233, 0.6) 100%)'
          : 'linear-gradient(135deg, rgba(12, 20, 38, 0.4) 0%, rgba(30, 41, 59, 0.3) 50%, rgba(14, 165, 233, 0.2) 100%)'
      }}></div>
      {/* Header with Back | Logo (Home) | Get Started */}
      <div style={{
        ...styles.header,
        borderBottom: scrolled ? '1px solid rgba(255, 255, 255, 0.2)' : 'none',
        background: scrolled ? 'rgba(0, 0, 0, 0.3)' : 'transparent',
        backdropFilter: scrolled ? 'blur(20px)' : 'none',
        boxShadow: scrolled ? '0 4px 6px -1px rgba(0, 0, 0, 0.1)' : 'none',
      }}>
        {/* Left: Back Button */}
        <button 
          onClick={onBack} 
          style={{
            ...styles.backButton,
            background: scrolled ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.05)',
            border: scrolled ? '1px solid rgba(255, 255, 255, 0.3)' : '1px solid rgba(255, 255, 255, 0.15)',
            backdropFilter: scrolled ? 'blur(10px)' : 'none',
          }}
        >
          <ArrowLeft size={20} style={{ marginRight: '8px' }} />
          Back
        </button>
        
        {/* Center: Logo (Home Button) */}
        <button 
          onClick={onHome || onBack}
          style={styles.homeLogoButton}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
          }}
        >
          <img 
            src="/jumbo-logo.png" 
            alt="Jumbo Home" 
            style={styles.navLogo}
          />
        </button>
        
        {/* Right: Get Started Button */}
        <button 
          onClick={onLogin}
          style={styles.loginButton}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 20px 25px -5px rgba(139, 92, 246, 0.3)';
          }}
        >
          Get Started
        </button>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .about-content {
            padding: 120px 16px 20px !important;
          }
          .about-features {
            grid-template-columns: 1fr !important;
            gap: 20px !important;
          }
          .about-bottom-section {
            grid-template-columns: 1fr !important;
            gap: 20px !important;
          }
          .about-cta-buttons {
            flex-direction: column !important;
            gap: 12px !important;
          }
        }
        
        @media (max-width: 480px) {
          .about-content {
            padding: 120px 12px 16px !important;
          }
          .about-title {
            font-size: 2.5rem !important;
          }
          .about-video {
            max-width: 100% !important;
          }
          .about-features {
            gap: 16px !important;
          }
          .about-bottom-section {
            gap: 16px !important;
          }
          .about-cta-buttons {
            gap: 8px !important;
          }
        }
      `}</style>

      <div style={styles.content} className="about-content">
        {/* Hero Section */}
        <div style={styles.hero}>
          <div style={styles.logoContainer}>
            <img 
              src="/jumbo-logo.png" 
              alt="Jumbo Logo" 
              style={styles.logo}
            />
          </div>
          
          <h1 style={styles.title} className="about-title">What is Jumbo?</h1>
          
          <p style={styles.mission}>
            🐘 <strong>Mission:</strong> Jumbo aims to make emotional check-ins as natural as checking the weather, 
            fostering genuine human connection in a digital world with your elephant mascot as a gentle, supportive companion.
          </p>
        </div>

        {/* Demo Video Section */}
        <div style={styles.videoSection}>
          <h2 style={styles.videoTitle}>See Jumbo in Action</h2>
          <div style={styles.videoContainer}>
            <video 
              controls 
              style={styles.video}
              className="about-video"
              poster="/jumbo-logo.png"
            >
              <source src="/jumbo-demo.mp4" type="video/mp4" />
              Your browser doesn't support video playback. 
              <a href="/jumbo-demo.mp4" style={{color: '#8b5cf6'}}>Download the video</a>
            </video>
            <p style={styles.videoDescription}>
              Discover how Jumbo creates meaningful, empathetic conversations and supports emotional well-being
            </p>
          </div>
        </div>

        {/* Core Concept */}
        <div style={styles.conceptSection}>
          <h2 style={styles.sectionTitle}>Core Concept</h2>
          <p style={styles.conceptDescription}>
            An emotional well-being app that helps users express their mood, check on friends, 
            and understand the emotional vibe of their community through gentle, non-intrusive connections.
          </p>
        </div>

        {/* Key Features */}
        <div style={styles.featuresSection}>
          <h2 style={styles.sectionTitle}>Key Features</h2>
          
          <div style={styles.features} className="about-features">
            <div style={styles.feature}>
              <div style={styles.featureIcon}>
                <Heart size={24} color="#ef4444" />
              </div>
              <h3 style={styles.featureTitle}>🌱 Self Check-In</h3>
              <ul style={styles.featureList}>
                <li>Daily mood selection with emoji interface</li>
                <li>Track special moments and conversations</li>
                <li>Optional text sharing for deeper expression</li>
              </ul>
            </div>

            <div style={styles.feature}>
              <div style={styles.featureIcon}>
                <Users size={24} color="#8b5cf6" />
              </div>
              <h3 style={styles.featureTitle}>👥 Friend Wellbeing</h3>
              <ul style={styles.featureList}>
                <li>Real-time friend mood status</li>
                <li>Visual support indicators</li>
                <li>Easy "Check In" buttons to reach out</li>
              </ul>
            </div>

            <div style={styles.feature}>
              <div style={styles.featureIcon}>
                <Map size={24} color="#06b6d4" />
              </div>
              <h3 style={styles.featureTitle}>🗺️ Community Mood Mapping</h3>
              <ul style={styles.featureList}>
                <li>Local (10km radius) mood insights</li>
                <li>City-wide and country-level trends</li>
                <li>Global emotional patterns - all anonymous</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Why It Matters */}
        <div style={styles.whySection}>
          <h2 style={styles.sectionTitle}>Why This App Matters Today</h2>
          <div style={styles.whyContent}>
            <div style={styles.problemSolution}>
              <div style={styles.problem}>
                <h3 style={styles.problemTitle}>The Challenge</h3>
                <ul style={styles.problemList}>
                  <li>People are feeling more isolated and emotionally disconnected</li>
                  <li>Existing social platforms lack emotional depth</li>
                  <li>Mental health support is often reactive, not proactive</li>
                </ul>
              </div>
              
              <div style={styles.solution}>
                <h3 style={styles.solutionTitle}>Our Solution</h3>
                <ul style={styles.solutionList}>
                  <li>Creates a gentle daily habit of emotional check-ins</li>
                  <li>Enables communities to support each other non-intrusively</li>
                  <li>Promotes emotional literacy and mindfulness</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Privacy & Target Audience */}
        <div style={styles.bottomSection} className="about-bottom-section">
          <div style={styles.privacySection}>
            <div style={styles.privacyIcon}>
              <Shield size={32} color="#10b981" />
            </div>
            <h3 style={styles.privacyTitle}>Privacy-First Approach</h3>
            <ul style={styles.privacyList}>
              <li>🔒 Local/anonymized data storage</li>
              <li>👤 User-controlled sharing</li>
              <li>📍 No GPS tracking (only approximate radius)</li>
              <li>🚫 No invasive monitoring</li>
            </ul>
          </div>

          <div style={styles.audienceSection}>
            <div style={styles.audienceIcon}>
              <Smartphone size={32} color="#8b5cf6" />
            </div>
            <h3 style={styles.audienceTitle}>Built For</h3>
            <p style={styles.audienceDescription}>
              Young adults 18-35, college students, remote workers, and empathetic communities 
              who value genuine connection and emotional well-being.
            </p>
          </div>
        </div>

        {/* Call to Action */}
        <div style={styles.ctaSection}>
          <h2 style={styles.ctaTitle}>Ready to Start Your Emotional Wellness Journey?</h2>
          <div style={styles.ctaButtons} className="about-cta-buttons">
            <button 
              onClick={onLogin}
              style={styles.ctaButton}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 20px 25px -5px rgba(139, 92, 246, 0.3)';
              }}
            >
              Join Jumbo Today - It's Free
            </button>
            
            <button 
              onClick={onHelp}
              style={styles.helpButton}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.1)';
              }}
            >
              Need Help? Visit FAQ
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0c1426 0%, #1e293b 50%, #0ea5e9 100%)',
    color: 'white',
    position: 'relative',
    overflow: 'hidden',
  },
  backgroundVideo: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    zIndex: 1,
    pointerEvents: 'none',
    transform: 'translateZ(0)', // Force hardware acceleration
  },
  videoOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'linear-gradient(135deg, rgba(12, 20, 38, 0.7) 0%, rgba(30, 41, 59, 0.6) 50%, rgba(14, 165, 233, 0.5) 100%)',
    zIndex: 2,
  },
  header: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 24px',
    transition: 'all 0.3s ease',
  },
  backButton: {
    display: 'flex',
    alignItems: 'center',
    padding: '10px 20px',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '25px',
    color: 'white',
    fontSize: '1rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  homeLogoButton: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    borderRadius: '50%',
    padding: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 5px 15px rgba(0, 0, 0, 0.1)',
  },
  navLogo: {
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    background: 'rgba(255, 255, 255, 0.9)',
    padding: '8px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
  },
  loginButton: {
    display: 'flex',
    alignItems: 'center',
    padding: '10px 20px',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
    border: 'none',
    borderRadius: '25px',
    color: 'white',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 20px 25px -5px rgba(139, 92, 246, 0.3)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  content: {
    padding: '100px 24px 40px',
    maxWidth: '1200px',
    margin: '0 auto',
    position: 'relative',
    zIndex: 10,
  },
  hero: {
    textAlign: 'center',
    marginBottom: '80px',
  },
  logoContainer: {
    marginBottom: '32px',
  },
  logo: {
    width: '120px',
    height: '120px',
    borderRadius: '50%',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
    background: 'rgba(255, 255, 255, 0.9)',
    padding: '20px',
  },
  title: {
    fontSize: '3.5rem',
    fontWeight: '700',
    color: 'white',
    marginBottom: '32px',
    textShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  mission: {
    fontSize: '1.3rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.7',
    maxWidth: '800px',
    margin: '0 auto',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  videoSection: {
    textAlign: 'center',
    marginBottom: '80px',
  },
  videoTitle: {
    fontSize: '2.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '32px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  videoContainer: {
    maxWidth: '800px',
    margin: '0 auto',
  },
  video: {
    width: '100%',
    maxWidth: '700px',
    height: 'auto',
    borderRadius: '16px',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  videoDescription: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6',
    marginTop: '24px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  conceptSection: {
    textAlign: 'center',
    marginBottom: '80px',
    maxWidth: '800px',
    margin: '0 auto 80px',
  },
  sectionTitle: {
    fontSize: '2.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '24px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  conceptDescription: {
    fontSize: '1.2rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.7',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  featuresSection: {
    marginBottom: '80px',
  },
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
    gap: '32px',
    marginTop: '40px',
  },
  feature: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '32px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    transition: 'all 0.3s ease',
  },
  featureIcon: {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    background: 'rgba(255, 255, 255, 0.9)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '20px',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.2)',
  },
  featureTitle: {
    fontSize: '1.4rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  whySection: {
    marginBottom: '80px',
  },
  whyContent: {
    marginTop: '40px',
  },
  problemSolution: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '40px',
  },
  problem: {
    background: 'rgba(239, 68, 68, 0.1)',
    borderRadius: '20px',
    padding: '32px',
    border: '1px solid rgba(239, 68, 68, 0.3)',
  },
  solution: {
    background: 'rgba(16, 185, 129, 0.1)',
    borderRadius: '20px',
    padding: '32px',
    border: '1px solid rgba(16, 185, 129, 0.3)',
  },
  problemTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#fca5a5',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  solutionTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#6ee7b7',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  problemList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  solutionList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  bottomSection: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '40px',
    marginBottom: '80px',
  },
  privacySection: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '20px',
    padding: '32px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    textAlign: 'center',
  },
  audienceSection: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '20px',
    padding: '32px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    textAlign: 'center',
  },
  privacyIcon: {
    marginBottom: '16px',
  },
  audienceIcon: {
    marginBottom: '16px',
  },
  privacyTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  audienceTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  privacyList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    textAlign: 'left',
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  audienceDescription: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  ctaSection: {
    textAlign: 'center',
    marginBottom: '40px',
  },
  ctaTitle: {
    fontSize: '2rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '32px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  ctaButtons: {
    display: 'flex',
    gap: '16px',
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
  ctaButton: {
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
  },
  helpButton: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '16px 32px',
    fontSize: '1.1rem',
    fontWeight: '500',
    color: 'white',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '50px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
};

export default AboutPage;