import React from 'react';
import { Sparkles, Heart, Mic, MessageCircle, Info, LogIn, Smartphone } from 'lucide-react';
import { theme } from '../theme/theme';

function LandingPage({ onGetStarted, onAbout, onHelp, onLogin, onHome }) {
  const [scrolled, setScrolled] = React.useState(false);
  const [videoLoaded, setVideoLoaded] = React.useState(false);
  const [videoError, setVideoError] = React.useState(false);

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
          // Video will still be visible but not playing
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
            console.log('Video can play, videoLoaded state:', videoLoaded);
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
      
      {/* Loading indicator for video */}
      {!videoLoaded && !videoError && (
        <div style={styles.videoLoading}>
          <div style={styles.loadingSpinner}></div>
        </div>
      )}
      

      <style>{`
        .contact-form input::placeholder,
        .contact-form textarea::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }
        
        .contact-form input:focus,
        .contact-form textarea:focus,
        .contact-form select:focus {
          border-color: rgba(139, 92, 246, 0.6);
          box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
        }
        
        .contact-form select option {
          background: #1e293b;
          color: white;
        }
        
        /* Force horizontal layout on desktop */
        .explainer-steps {
          display: flex !important;
          flex-direction: row !important;
          justify-content: center !important;
          gap: 32px !important;
          flex-wrap: nowrap !important;
        }
        
        .explainer-step {
          flex: 1 !important;
          max-width: 350px !important;
          min-width: 300px !important;
        }
        
        @media (max-width: 1024px) {
          .explainer-steps {
            gap: 20px !important;
            max-width: 900px !important;
          }
        }
        
        @media (max-width: 768px) {
          .landing-content {
            padding: 120px 16px 20px !important;
          }
          .about-button, .login-button {
            padding: 8px 16px !important;
            font-size: 0.9rem !important;
          }
          .background-video {
            opacity: 0.2 !important;
          }
          .landing-features {
            grid-template-columns: 1fr !important;
            gap: 20px !important;
            max-width: 400px !important;
            margin: 0 auto 60px !important;
          }

          .quick-features {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 12px !important;
          }
        }
          .landing-hero {
            margin-bottom: 40px !important;
          }
          .landing-title {
            font-size: 2.5rem !important;
            line-height: 1.2 !important;
            margin-bottom: 16px !important;
          }
          .landing-subtitle {
            font-size: 1rem !important;
            margin-bottom: 24px !important;
            padding: 0 8px !important;
          }
          .landing-logo {
            width: 80px !important;
            height: 80px !important;
            padding: 12px !important;
          }
          .landing-logo-container {
            margin-bottom: 20px !important;
          }
          .landing-cta-button {
            padding: 14px 24px !important;
            font-size: 1rem !important;
          }
          .landing-features {
            gap: 24px !important;
            margin-bottom: 40px !important;
          }
          .landing-feature {
            padding: 24px !important;
          }
          .landing-section {
            margin-bottom: 40px !important;
          }

          .landing-about-features {
            gap: 16px !important;
          }
          .landing-about-feature {
            padding: 16px !important;
          }
          .landing-contact-form {
            padding: 0 8px !important;
          }
          .trust-badges {
            gap: 8px !important;
            flex-direction: column !important;
            align-items: center !important;
          }

        }
        
        @media (max-width: 480px) {
          .landing-title {
            font-size: 2rem !important;
          }
          .landing-subtitle {
            font-size: 0.9rem !important;
          }
          .landing-content {
            padding: 120px 12px 16px !important;
          }
          .about-button, .login-button {
            padding: 6px 12px !important;
            font-size: 0.8rem !important;
          }
          .landing-features {
            gap: 16px !important;
            max-width: 300px !important;
          }
          .landing-feature {
            padding: 24px 16px !important;
            min-height: 180px !important;
          }
          .trust-badges {
            gap: 6px !important;
            flex-direction: column !important;
            align-items: center !important;
          }
          .trust-badge {
            font-size: 12px !important;
            padding: 6px 12px !important;
          }

          .step-number {
            width: 40px !important;
            height: 40px !important;
            font-size: 18px !important;
          }
          .quick-features {
            grid-template-columns: 1fr !important;
            gap: 8px !important;
          }
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        }
      `}</style>
      
      {/* Header with About | Logo (Home) | Login */}
      <div style={{
        ...styles.header,
        borderBottom: scrolled ? '1px solid rgba(255, 255, 255, 0.2)' : 'none',
        background: scrolled ? 'rgba(0, 0, 0, 0.3)' : 'transparent',
        backdropFilter: scrolled ? 'blur(20px)' : 'none',
        boxShadow: scrolled ? '0 4px 6px -1px rgba(0, 0, 0, 0.1)' : 'none',
      }}>
        {/* Left: About Button */}
        <button 
          onClick={onAbout}
          style={{
            ...styles.aboutButton,
            background: scrolled ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.05)',
            border: scrolled ? '1px solid rgba(255, 255, 255, 0.3)' : '1px solid rgba(255, 255, 255, 0.15)',
            backdropFilter: scrolled ? 'blur(10px)' : 'none',
          }}
          className="about-button"
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.25)';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = scrolled ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.1)';
          }}
        >
          <Info size={20} style={{ marginRight: '8px' }} />
          About
        </button>
        
        {/* Center: Logo (Home Button) */}
        <button 
          onClick={onHome || (() => window.scrollTo({ top: 0, behavior: 'smooth' }))}
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
        
        {/* Right: Login Button */}
        <button 
          onClick={onLogin}
          style={{
            ...styles.loginButton,
            boxShadow: scrolled ? '0 25px 50px -12px rgba(139, 92, 246, 0.4)' : '0 20px 25px -5px rgba(139, 92, 246, 0.3)',
          }}
          className="login-button"
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = scrolled ? '0 25px 50px -12px rgba(139, 92, 246, 0.4)' : '0 20px 25px -5px rgba(139, 92, 246, 0.3)';
          }}
        >
          <LogIn size={18} style={{ marginRight: '8px' }} />
          Login
        </button>
      </div>

      <div style={styles.content} className="landing-content">
        {/* Hero Section */}
        <div style={styles.hero} className="landing-hero">
          <h1 style={styles.title} className="landing-title">
            Meet Jumbo
          </h1>
          
          <p style={styles.subtitle} className="landing-subtitle">
            Your AI-powered emotional support companion with advanced conversation and memory capabilities
          </p>
          
          <div style={styles.betaMessage}>
            💛 Jumbo is growing! Join our beta and share your thoughts with us.
          </div>
          
          <button 
            onClick={onGetStarted}
            style={styles.ctaButton}
            className="landing-cta-button"
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.3)';
            }}
          >
            <Sparkles size={20} style={{ marginRight: '8px' }} />
            Start Your Journey – It's Free (Beta Access)
          </button>
          
          <div style={styles.comingSoonMessage}>
            <Smartphone size={18} style={{ marginRight: '8px' }} />
            Coming Soon to Android & iOS Devices
          </div>

          
          <div style={styles.trustBadges} className="trust-badges">
            <span style={styles.trustBadge} className="trust-badge">🔒 100% Private & Secure</span>
            <span style={styles.trustBadge} className="trust-badge">🆓 Free During Beta Period</span>
            <span style={styles.trustBadge} className="trust-badge">⚡ Subscription Plans Coming Later</span>
          </div>
        </div>

        {/* How Jumbo Works - Horizontal Steps */}
        <div style={styles.howItWorksSection}>
          <h2 style={styles.howItWorksTitle}>How Jumbo Helps You Feel Better</h2>
          <p style={styles.howItWorksSubtitle}>
            Mental wellness shouldn't be complicated. Jumbo makes emotional support accessible, 
            private, and available whenever you need it most.
          </p>
          
          <div style={styles.stepsContainer} className="steps-container">
            <div style={styles.step} className="step">
              <div style={styles.stepIcon}>1</div>
              <h3 style={styles.stepHeading}>Share Your Feelings</h3>
              <p style={styles.stepText}>Talk to Jumbo about anything. No judgment, just caring support.</p>
            </div>
            
            <div style={styles.step} className="step">
              <div style={styles.stepIcon}>2</div>
              <h3 style={styles.stepHeading}>Get Personalized Support</h3>
              <p style={styles.stepText}>Jumbo understands your emotions and provides tailored responses.</p>
            </div>
            
            <div style={styles.step} className="step">
              <div style={styles.stepIcon}>3</div>
              <h3 style={styles.stepHeading}>Build Emotional Resilience</h3>
              <p style={styles.stepText}>Jumbo learns about you and helps develop healthy coping strategies.</p>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div style={styles.features} className="landing-features">
          <div 
            style={styles.feature} 
            className="landing-feature"
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-5px)';
              e.target.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            <div style={styles.featureIcon}>
              <Heart size={24} color="#ef4444" />
            </div>
            <h3 style={styles.featureTitle}>Emotional Intelligence</h3>
            <p style={styles.featureDescription}>
              Understands and responds to your emotions with empathy and care
            </p>
          </div>

          <div 
            style={styles.feature} 
            className="landing-feature"
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-5px)';
              e.target.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            <div style={styles.featureIcon}>
              <Mic size={24} color="#8b5cf6" />
            </div>
            <h3 style={styles.featureTitle}>Voice Interaction</h3>
            <p style={styles.featureDescription}>
              Speak naturally and hear responses with advanced speech technology
            </p>
          </div>

          <div 
            style={styles.feature} 
            className="landing-feature"
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-5px)';
              e.target.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            <div style={styles.featureIcon}>
              <MessageCircle size={24} color="#06b6d4" />
            </div>
            <h3 style={styles.featureTitle}>Memory & Context</h3>
            <p style={styles.featureDescription}>
              Remembers your conversations and builds meaningful relationships
            </p>
          </div>
        </div>

        {/* Brief About Section */}
        <div style={styles.aboutSection} className="landing-section">
          <h2 style={styles.sectionTitle}>Why Choose Jumbo?</h2>
          <p style={styles.sectionDescription}>
            Jumbo combines advanced AI with evidence-based emotional support techniques to provide 
            safe, private, and effective mental wellness support whenever you need it.
          </p>
          
          <div style={styles.quickFeatures} className="quick-features">
            <div style={styles.quickFeature}>🔒 100% Private & Secure</div>
            <div style={styles.quickFeature}>🆓 Free During Beta Period</div>
            <div style={styles.quickFeature}>⚡ Subscription Plans Coming Later</div>
            <div style={styles.quickFeature}>🌍 Available 24/7</div>
          </div>
          
          <button 
            onClick={onAbout}
            style={styles.learnMoreButton}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.1)';
            }}
          >
            See Our Mission & Demo
          </button>
        </div>



        {/* Simple Contact Section */}
        <div style={styles.contactSection} className="landing-section">
          <h2 style={styles.sectionTitle}>Get in Touch</h2>
          <p style={styles.sectionDescription}>
            Have questions or want to collaborate? We'd love to hear from you.
          </p>
          
          <div style={styles.contactOptions}>
            <button 
              onClick={onAbout}
              style={styles.contactButton}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.1)';
              }}
            >
              Learn About Jumbo
            </button>
            <button 
              onClick={onHelp}
              style={styles.contactButton}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.1)';
              }}
            >
              Get Help & FAQ
            </button>
          </div>
        </div>

        {/* Footer */}
        <div style={styles.footer}>
          <p style={styles.footerText}>
            © 2025 Sriharsha Siddam. All rights reserved. This website and its content, including the design, concept, and original ideas, are the intellectual property of Sriharsha Siddam. Unauthorized reproduction or use of any part of this website is strictly prohibited.
          </p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0c1426 0%, #1e293b 50%, #0ea5e9 100%)',
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
    padding: '12px 24px',
    transition: 'all 0.3s ease',
  },
  aboutButton: {
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
    width: '100%',
    padding: '100px 24px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
    position: 'relative',
    zIndex: 10,
  },
  hero: {
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
    fontSize: '4rem',
    fontWeight: '700',
    color: 'white',
    marginBottom: '24px',
    textShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  subtitle: {
    fontSize: '1.25rem',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '24px',
    maxWidth: '600px',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  betaMessage: {
    fontSize: '1rem',
    color: 'white',
    marginBottom: '32px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    fontWeight: '500',
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
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  comingSoonMessage: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1rem',
    color: 'white',
    marginTop: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    fontWeight: '500',
  },

  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '24px',
    width: '100%',
    maxWidth: '1000px',
    marginBottom: '60px',
    justifyItems: 'center',
  },
  feature: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '32px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    transition: 'all 0.3s ease',
    width: '100%',
    maxWidth: '320px',
    minHeight: '200px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
  },
  featureIcon: {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    background: 'rgba(255, 255, 255, 0.9)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 20px',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.2)',
  },
  featureTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  featureDescription: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  footer: {
    marginTop: '40px',
  },
  footerText: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.7)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  aboutSection: {
    marginBottom: '80px',
    textAlign: 'center',
    maxWidth: '800px',
  },
  quickFeatures: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '16px',
    marginBottom: '32px',
    maxWidth: '800px',
    margin: '0 auto 32px',
  },
  quickFeature: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '12px',
    padding: '16px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    fontSize: '1rem',
    color: 'white',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  learnMoreButton: {
    padding: '12px 24px',
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

  contactSection: {
    marginBottom: '60px',
    textAlign: 'center',
    maxWidth: '600px',
  },
  contactOptions: {
    display: 'flex',
    gap: '16px',
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
  contactButton: {
    padding: '12px 24px',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '25px',
    color: 'white',
    fontSize: '1rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textDecoration: 'none',
    display: 'inline-block',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  sectionTitle: {
    fontSize: '2.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '24px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  sectionDescription: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.7',
    marginBottom: '40px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  trustBadges: {
    display: 'flex',
    gap: '16px',
    marginTop: '24px',
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  trustBadge: {
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.9)',
    background: 'rgba(255, 255, 255, 0.1)',
    padding: '8px 16px',
    borderRadius: '20px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  howItWorksSection: {
    marginBottom: '80px',
    textAlign: 'center',
    maxWidth: '1200px',
    margin: '0 auto 80px',
  },
  howItWorksTitle: {
    fontSize: '2.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  howItWorksSubtitle: {
    fontSize: '1.2rem',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '48px',
    maxWidth: '700px',
    margin: '0 auto 48px',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  stepsContainer: {
    display: 'table',
    width: '100%',
    tableLayout: 'fixed',
    borderSpacing: '20px 0',
  },
  step: {
    display: 'table-cell',
    verticalAlign: 'top',
    textAlign: 'center',
    background: 'rgba(255, 255, 255, 0.05)',
    padding: '24px 16px',
    borderRadius: '16px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    width: '33.333%',
  },
  stepIcon: {
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '20px',
    fontWeight: '600',
    margin: '0 auto 16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  stepHeading: {
    fontSize: '1.2rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '12px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  stepText: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.5',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  videoSection: {
    marginTop: '48px',
    textAlign: 'center',
  },
  videoTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '24px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  videoContainer: {
    maxWidth: '800px',
    margin: '0 auto',
  },
  video: {
    width: '100%',
    maxWidth: '600px',
    height: 'auto',
    borderRadius: '16px',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  videoPlaceholder: {
    position: 'relative',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    padding: '60px 40px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  playButton: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 20px',
    boxShadow: '0 20px 25px -5px rgba(139, 92, 246, 0.3)',
    transition: 'all 0.3s ease',
  },
  playIcon: {
    fontSize: '24px',
    color: 'white',
    marginLeft: '4px',
  },
  videoText: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.5',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  videoDescription: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.5',
    marginTop: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  videoLoading: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    zIndex: -1,
  },
  loadingSpinner: {
    width: '40px',
    height: '40px',
    border: '3px solid rgba(255, 255, 255, 0.3)',
    borderTop: '3px solid rgba(139, 92, 246, 0.8)',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },


};

export default LandingPage;