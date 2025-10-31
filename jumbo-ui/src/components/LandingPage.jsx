import React from 'react';
import { Sparkles, Heart, Mic, MessageCircle } from 'lucide-react';
import GradientBackground from './GradientBackground';
import { theme } from '../theme/theme';

function LandingPage({ onGetStarted }) {
  return (
    <GradientBackground variant="copilot" animated={true} style={styles.container}>
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
        
        @media (max-width: 768px) {
          .form-row {
            grid-template-columns: 1fr !important;
          }
          .collaborate-options {
            grid-template-columns: 1fr !important;
          }
          .landing-content {
            padding: 20px 16px !important;
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
          .landing-tech-grid {
            gap: 16px !important;
          }
          .landing-tech-category {
            padding: 16px !important;
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
        }
        
        @media (max-width: 480px) {
          .landing-title {
            font-size: 2rem !important;
          }
          .landing-subtitle {
            font-size: 0.9rem !important;
          }
          .landing-content {
            padding: 16px 12px !important;
          }
          .landing-features {
            gap: 16px !important;
          }
        }
        }
      `}</style>
      <div style={styles.content} className="landing-content">
        {/* Hero Section */}
        <div style={styles.hero} className="landing-hero">
          <div style={styles.logoContainer} className="landing-logo-container">
            <img 
              src="/jumbo-logo.png" 
              alt="Jumbo Logo" 
              style={styles.logo}
              className="landing-logo"
            />
          </div>
          
          <h1 style={styles.title} className="landing-title">
            Meet Jumbo
          </h1>
          
          <p style={styles.subtitle} className="landing-subtitle">
            Your AI-powered emotional support companion with advanced conversation and memory capabilities
          </p>
          
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
            Start Chatting with Jumbo
          </button>
        </div>

        {/* Features Section */}
        <div style={styles.features} className="landing-features">
          <div style={styles.feature} className="landing-feature">
            <div style={styles.featureIcon}>
              <Heart size={24} color="#ef4444" />
            </div>
            <h3 style={styles.featureTitle}>Emotional Intelligence</h3>
            <p style={styles.featureDescription}>
              Understands and responds to your emotions with empathy and care
            </p>
          </div>

          <div style={styles.feature} className="landing-feature">
            <div style={styles.featureIcon}>
              <Mic size={24} color="#8b5cf6" />
            </div>
            <h3 style={styles.featureTitle}>Voice Interaction</h3>
            <p style={styles.featureDescription}>
              Speak naturally and hear responses with advanced speech technology
            </p>
          </div>

          <div style={styles.feature} className="landing-feature">
            <div style={styles.featureIcon}>
              <MessageCircle size={24} color="#06b6d4" />
            </div>
            <h3 style={styles.featureTitle}>Memory & Context</h3>
            <p style={styles.featureDescription}>
              Remembers your conversations and builds meaningful relationships
            </p>
          </div>
        </div>

        {/* About Section */}
        <div style={styles.aboutSection} className="landing-section">
          <h2 style={styles.sectionTitle}>About Jumbo</h2>
          <p style={styles.sectionDescription}>
            Jumbo is your caring emotional support companion powered by advanced AI technology. 
            We understand that everyone needs someone to talk to, and Jumbo is here to listen, 
            understand, and provide meaningful support whenever you need it.
          </p>
          
          <div style={styles.aboutFeatures} className="landing-about-features">
            <div style={styles.aboutFeature} className="landing-about-feature">
              <h4 style={styles.aboutFeatureTitle}>🔒 Privacy First</h4>
              <p style={styles.aboutFeatureText}>Your conversations are private and secure. We don't share your data with anyone.</p>
            </div>
            <div style={styles.aboutFeature} className="landing-about-feature">
              <h4 style={styles.aboutFeatureTitle}>🧠 Smart Memory</h4>
              <p style={styles.aboutFeatureText}>Each conversation helps Jumbo understand you better and provide more personalized support.</p>
            </div>
            <div style={styles.aboutFeature} className="landing-about-feature">
              <h4 style={styles.aboutFeatureTitle}>🌍 Always Available</h4>
              <p style={styles.aboutFeatureText}>24/7 emotional support whenever you need someone to talk to.</p>
            </div>
          </div>
        </div>

        {/* MVP Disclaimer Section */}
        <div style={styles.mvpSection} className="landing-section">
          <div style={styles.mvpBanner}>
            <h3 style={styles.mvpTitle}>🚀 MVP Demo Version</h3>
            <p style={styles.mvpDescription}>
              This is a <strong>Minimum Viable Product (MVP)</strong> showcasing the core concept and architecture. 
              Due to free-tier hosting limitations, some advanced features are simplified or disabled.
            </p>
          </div>
          
          <div style={styles.techStackSection}>
            <h4 style={styles.techStackTitle}>🛠️ Tech Stack & Architecture</h4>
            <div style={styles.techGrid} className="landing-tech-grid">
              <div style={styles.techCategory} className="landing-tech-category">
                <h5 style={styles.techCategoryTitle}>Frontend</h5>
                <ul style={styles.techList}>
                  <li style={styles.techListItem}>React.js with modern hooks</li>
                  <li style={styles.techListItem}>Responsive design & animations</li>
                  <li style={styles.techListItem}>Real-time speech recognition</li>
                  <li style={styles.techListItem}>Progressive Web App (PWA)</li>
                </ul>
              </div>
              
              <div style={styles.techCategory} className="landing-tech-category">
                <h5 style={styles.techCategoryTitle}>Backend</h5>
                <ul style={styles.techList}>
                  <li style={styles.techListItem}>Flask API with production architecture</li>
                  <li style={styles.techListItem}>Stateless design for scalability</li>
                  <li style={styles.techListItem}>Comprehensive error handling</li>
                  <li style={styles.techListItem}>Monitoring & logging system</li>
                </ul>
              </div>
              
              <div style={styles.techCategory} className="landing-tech-category">
                <h5 style={styles.techCategoryTitle}>AI & Intelligence</h5>
                <ul style={styles.techList}>
                  <li style={styles.techListItem}>Groq LLM integration (Llama 3)</li>
                  <li style={styles.techListItem}>Emotion detection system</li>
                  <li style={styles.techListItem}>Personality-driven responses</li>
                  <li style={styles.techListItem}>Memory & context management</li>
                </ul>
              </div>
              
              <div style={styles.techCategory} className="landing-tech-category">
                <h5 style={styles.techCategoryTitle}>Infrastructure</h5>
                <ul style={styles.techList}>
                  <li style={styles.techListItem}>Supabase (PostgreSQL + Auth)</li>
                  <li style={styles.techListItem}>Vercel (Frontend hosting)</li>
                  <li style={styles.techListItem}>Render (Backend hosting)</li>
                  <li style={styles.techListItem}>Google OAuth integration</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div style={styles.limitationsSection}>
            <h4 style={styles.limitationsTitle}>⚠️ Current MVP Limitations</h4>
            <div style={styles.limitationsList}>
              <div style={styles.limitation}>
                <strong>Simplified Emotion Detection:</strong> Using keyword-based detection instead of advanced transformer models
              </div>
              <div style={styles.limitation}>
                <strong>Basic Memory System:</strong> Core functionality present, advanced semantic search disabled
              </div>
              <div style={styles.limitation}>
                <strong>Limited Concurrent Users:</strong> Free-tier hosting restricts simultaneous users
              </div>
              <div style={styles.limitation}>
                <strong>Reduced Model Complexity:</strong> Using lighter AI models for faster response times
              </div>
            </div>
          </div>
          
          <div style={styles.futureSection}>
            <h4 style={styles.futureTitle}>🔮 Planned Enhancements</h4>
            <div style={styles.futureGrid}>
              <div style={styles.futureItem}>
                <strong>Advanced Emotion AI:</strong> Transformer-based emotion detection with 95%+ accuracy
              </div>
              <div style={styles.futureItem}>
                <strong>Semantic Memory:</strong> Vector-based memory search with contextual understanding
              </div>
              <div style={styles.futureItem}>
                <strong>Multi-modal Input:</strong> Image, voice, and text processing capabilities
              </div>
              <div style={styles.futureItem}>
                <strong>Personalized Models:</strong> Fine-tuned AI models for individual users
              </div>
              <div style={styles.futureItem}>
                <strong>Real-time Analytics:</strong> Mood tracking and mental health insights
              </div>
              <div style={styles.futureItem}>
                <strong>Mobile Apps:</strong> Native iOS and Android applications
              </div>
            </div>
          </div>
        </div>

        {/* Collaborate Section */}
        <div style={styles.collaborateSection} className="landing-section">
          <h2 style={styles.sectionTitle}>Let's Collaborate</h2>
          <p style={styles.sectionDescription}>
            We're always looking to improve Jumbo and make it more helpful for everyone. 
            Whether you're a developer, researcher, or someone passionate about mental health technology, 
            we'd love to hear from you.
          </p>
          
          <div style={styles.collaborateOptions} className="collaborate-options">
            <div style={styles.collaborateOption}>
              <h4 style={styles.collaborateTitle}>🚀 Developers</h4>
              <p style={styles.collaborateText}>Help us build better AI experiences and contribute to open-source mental health technology.</p>
            </div>
            <div style={styles.collaborateOption}>
              <h4 style={styles.collaborateTitle}>🔬 Researchers</h4>
              <p style={styles.collaborateText}>Partner with us to study AI-human emotional interactions and improve mental health outcomes.</p>
            </div>
            <div style={styles.collaborateOption}>
              <h4 style={styles.collaborateTitle}>💡 Ideas & Feedback</h4>
              <p style={styles.collaborateText}>Share your thoughts on how we can make Jumbo more helpful and accessible to everyone.</p>
            </div>
          </div>

          {/* Contact Form */}
          <div style={styles.contactFormSection}>
            <h3 style={styles.contactFormTitle}>Get in Touch</h3>
            <form 
              action="https://formspree.io/f/YOUR_FORM_ID" 
              method="POST"
              style={styles.contactForm}
              className="contact-form landing-contact-form"
            >
              <div style={styles.formRow} className="form-row">
                <input
                  type="text"
                  name="name"
                  placeholder="Your Name"
                  required
                  style={styles.formInput}
                />
                <input
                  type="email"
                  name="email"
                  placeholder="Your Email"
                  required
                  style={styles.formInput}
                />
              </div>
              
              <input
                type="text"
                name="subject"
                placeholder="Subject"
                required
                style={styles.formInputFull}
              />
              
              <select
                name="collaboration_type"
                required
                style={styles.formSelect}
              >
                <option value="">Select Collaboration Type</option>
                <option value="developer">🚀 Developer Collaboration</option>
                <option value="researcher">🔬 Research Partnership</option>
                <option value="feedback">💡 Ideas & Feedback</option>
                <option value="business">💼 Business Inquiry</option>
                <option value="other">🤝 Other</option>
              </select>
              
              <textarea
                name="message"
                placeholder="Tell us about your ideas, project, or how you'd like to collaborate..."
                rows="5"
                required
                style={styles.formTextarea}
              ></textarea>
              
              <button 
                type="submit"
                style={styles.formSubmitButton}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 20px 25px -5px rgba(139, 92, 246, 0.3)';
                }}
              >
                Send Message
              </button>
            </form>
          </div>
        </div>

        {/* Footer */}
        <div style={styles.footer}>
          <p style={styles.footerText}>
            © 2025 Sriharsha Siddam. All rights reserved. This website and its content, including the design, concept, and original ideas, are the intellectual property of Sriharsha Siddam. Unauthorized reproduction or use of any part of this website is strictly prohibited.
          </p>
        </div>
      </div>
    </GradientBackground>
  );
}

const styles = {
  container: {
    // GradientBackground handles centering now
  },
  content: {
    width: '100%',
    padding: '40px 24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
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
    marginBottom: '40px',
    maxWidth: '600px',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
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
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '40px',
    width: '100%',
    marginBottom: '60px',
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
  mvpSection: {
    marginBottom: '80px',
    textAlign: 'center',
    maxWidth: '1000px',
  },
  mvpBanner: {
    background: 'rgba(255, 193, 7, 0.15)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '24px',
    border: '2px solid rgba(255, 193, 7, 0.3)',
    marginBottom: '40px',
  },
  mvpTitle: {
    fontSize: '1.8rem',
    fontWeight: '600',
    color: '#fbbf24',
    marginBottom: '12px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  mvpDescription: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.6',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  techStackSection: {
    marginBottom: '40px',
  },
  techStackTitle: {
    fontSize: '1.6rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '24px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  techGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
    marginBottom: '40px',
  },
  techCategory: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '24px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    textAlign: 'left',
  },
  techCategoryTitle: {
    fontSize: '1.2rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  techList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  techListItem: {
    padding: '8px 0',
    fontSize: '0.95rem',
    color: 'rgba(255, 255, 255, 0.9)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  limitationsSection: {
    marginBottom: '40px',
  },
  limitationsTitle: {
    fontSize: '1.4rem',
    fontWeight: '600',
    color: '#f59e0b',
    marginBottom: '20px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  limitationsList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '16px',
  },
  limitation: {
    background: 'rgba(245, 158, 11, 0.1)',
    borderRadius: '12px',
    padding: '16px',
    border: '1px solid rgba(245, 158, 11, 0.3)',
    fontSize: '0.95rem',
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'left',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  futureSection: {
    marginBottom: '40px',
  },
  futureTitle: {
    fontSize: '1.4rem',
    fontWeight: '600',
    color: '#10b981',
    marginBottom: '20px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  futureGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '16px',
  },
  futureItem: {
    background: 'rgba(16, 185, 129, 0.1)',
    borderRadius: '12px',
    padding: '16px',
    border: '1px solid rgba(16, 185, 129, 0.3)',
    fontSize: '0.95rem',
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'left',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  collaborateSection: {
    marginBottom: '60px',
    textAlign: 'center',
    maxWidth: '800px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
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
  aboutFeatures: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
  },
  aboutFeature: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '24px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  aboutFeatureTitle: {
    fontSize: '1.2rem',
    color: 'white',
    marginBottom: '12px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  aboutFeatureText: {
    fontSize: '0.95rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.5',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  collaborateOptions: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '24px',
    marginBottom: '60px',
    '@media (max-width: 768px)': {
      gridTemplateColumns: '1fr',
    },
  },
  collaborateOption: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '24px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    transition: 'all 0.3s ease',
  },
  collaborateTitle: {
    fontSize: '1.2rem',
    color: 'white',
    marginBottom: '12px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  collaborateText: {
    fontSize: '0.95rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.5',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  contactFormSection: {
    marginTop: '40px',
    maxWidth: '600px',
    width: '100%',
  },
  contactFormTitle: {
    fontSize: '1.8rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '24px',
    textAlign: 'center',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  contactForm: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  formRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
    '@media (max-width: 768px)': {
      gridTemplateColumns: '1fr',
    },
  },
  formInput: {
    padding: '14px 18px',
    borderRadius: '12px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    color: 'white',
    fontSize: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    outline: 'none',
    transition: 'all 0.3s ease',
  },
  formInputFull: {
    padding: '14px 18px',
    borderRadius: '12px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    color: 'white',
    fontSize: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    outline: 'none',
    transition: 'all 0.3s ease',
    width: '100%',
  },
  formSelect: {
    padding: '14px 18px',
    borderRadius: '12px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    color: 'white',
    fontSize: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    outline: 'none',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
  },
  formTextarea: {
    padding: '14px 18px',
    borderRadius: '12px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    color: 'white',
    fontSize: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    outline: 'none',
    transition: 'all 0.3s ease',
    resize: 'vertical',
    minHeight: '120px',
  },
  formSubmitButton: {
    padding: '16px 32px',
    borderRadius: '50px',
    border: 'none',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
    color: 'white',
    fontSize: '1.1rem',
    fontWeight: '600',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 20px 25px -5px rgba(139, 92, 246, 0.3)',
    marginTop: '10px',
  },
};

export default LandingPage;