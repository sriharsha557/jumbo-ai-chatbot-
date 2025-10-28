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
        }
      `}</style>
      <div style={styles.content}>
        {/* Hero Section */}
        <div style={styles.hero}>
          <div style={styles.logoContainer}>
            <img 
              src="/jumbo-logo.png" 
              alt="Jumbo Logo" 
              style={styles.logo}
            />
          </div>
          
          <h1 style={styles.title}>
            Meet Jumbo
          </h1>
          
          <p style={styles.subtitle}>
            Your AI-powered emotional support companion with advanced conversation and memory capabilities
          </p>
          
          <button 
            onClick={onGetStarted}
            style={styles.ctaButton}
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
        <div style={styles.features}>
          <div style={styles.feature}>
            <div style={styles.featureIcon}>
              <Heart size={24} color="#ef4444" />
            </div>
            <h3 style={styles.featureTitle}>Emotional Intelligence</h3>
            <p style={styles.featureDescription}>
              Understands and responds to your emotions with empathy and care
            </p>
          </div>

          <div style={styles.feature}>
            <div style={styles.featureIcon}>
              <Mic size={24} color="#8b5cf6" />
            </div>
            <h3 style={styles.featureTitle}>Voice Interaction</h3>
            <p style={styles.featureDescription}>
              Speak naturally and hear responses with advanced speech technology
            </p>
          </div>

          <div style={styles.feature}>
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
        <div style={styles.aboutSection}>
          <h2 style={styles.sectionTitle}>About Jumbo</h2>
          <p style={styles.sectionDescription}>
            Jumbo is your caring emotional support companion powered by advanced AI technology. 
            We understand that everyone needs someone to talk to, and Jumbo is here to listen, 
            understand, and provide meaningful support whenever you need it.
          </p>
          
          <div style={styles.aboutFeatures}>
            <div style={styles.aboutFeature}>
              <h4 style={styles.aboutFeatureTitle}>🔒 Privacy First</h4>
              <p style={styles.aboutFeatureText}>Your conversations are private and secure. We don't share your data with anyone.</p>
            </div>
            <div style={styles.aboutFeature}>
              <h4 style={styles.aboutFeatureTitle}>🧠 Smart Memory</h4>
              <p style={styles.aboutFeatureText}>Each conversation helps Jumbo understand you better and provide more personalized support.</p>
            </div>
            <div style={styles.aboutFeature}>
              <h4 style={styles.aboutFeatureTitle}>🌍 Always Available</h4>
              <p style={styles.aboutFeatureText}>24/7 emotional support whenever you need someone to talk to.</p>
            </div>
          </div>
        </div>

        {/* Collaborate Section */}
        <div style={styles.collaborateSection}>
          <h2 style={styles.sectionTitle}>Let's Collaborate</h2>
          <p style={styles.sectionDescription}>
            We're always looking to improve Jumbo and make it more helpful for everyone. 
            Whether you're a developer, researcher, or someone passionate about mental health technology, 
            we'd love to hear from you.
          </p>
          
          <div style={styles.collaborateOptions}>
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
              className="contact-form"
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
            Experience the future of AI companionship
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
  collaborateSection: {
    marginBottom: '60px',
    textAlign: 'center',
    maxWidth: '800px',
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
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '24px',
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
    marginTop: '60px',
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