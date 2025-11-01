import React, { useState } from 'react';
import { ArrowLeft, ChevronDown, ChevronRight, LogIn } from 'lucide-react';
import GradientBackground from './GradientBackground';
import { theme } from '../theme/theme';

function HelpPage({ onBack, onLogin }) {
  const [expandedSection, setExpandedSection] = useState(null);

  const toggleSection = (sectionId) => {
    setExpandedSection(expandedSection === sectionId ? null : sectionId);
  };

  const helpSections = [
    {
      id: 'common-questions',
      title: '❓ Common Questions',
      questions: [
        {
          q: 'What is Jumbo?',
          a: 'Jumbo is an AI-powered emotional support companion designed to provide empathetic conversations and mental wellness support. It uses advanced AI to understand your emotions and provide personalized responses.'
        },
        {
          q: 'Is Jumbo free to use?',
          a: 'Yes! Jumbo is completely free to use and will always remain free. We believe mental health support should be accessible to everyone.'
        },
        {
          q: 'How does Jumbo work?',
          a: 'Simply start a conversation with Jumbo by typing or speaking. Jumbo will listen to your concerns, understand your emotions, and provide supportive responses tailored to your needs.'
        },
        {
          q: 'Can Jumbo replace therapy or professional help?',
          a: 'No, Jumbo is not a replacement for professional mental health care. While it provides valuable emotional support, it cannot diagnose or treat mental health conditions. For serious concerns, please consult a mental health professional.'
        },
        {
          q: 'What makes Jumbo different from other chatbots?',
          a: 'Jumbo is specifically designed for emotional support with advanced emotion detection, memory capabilities, and responses grounded in evidence-based therapeutic techniques like CBT and mindfulness.'
        }
      ]
    },
    {
      id: 'moods',
      title: '😊 Understanding Moods',
      questions: [
        {
          q: 'How does Jumbo detect my emotions?',
          a: 'Jumbo analyzes your messages using advanced emotion detection algorithms that look for emotional cues, keywords, and context to understand how you\'re feeling.'
        },
        {
          q: 'What emotions can Jumbo recognize?',
          a: 'Jumbo can recognize a wide range of emotions including happiness, sadness, anxiety, anger, confusion, excitement, frustration, and many others with varying levels of intensity.'
        },
        {
          q: 'Can I tell Jumbo how I\'m feeling directly?',
          a: 'Absolutely! You can directly tell Jumbo about your emotions by saying things like "I\'m feeling anxious" or "I\'m really happy today." This helps Jumbo provide more targeted support.'
        },
        {
          q: 'Does Jumbo track my mood over time?',
          a: 'Yes, Jumbo can track your emotional patterns over time to provide insights and help you understand your emotional journey better.'
        },
        {
          q: 'What if Jumbo misunderstands my emotion?',
          a: 'You can always correct Jumbo by explaining how you actually feel. This helps improve the conversation and Jumbo\'s understanding of your emotional state.'
        }
      ]
    },
    {
      id: 'conversation',
      title: '💬 Conversation & Memory',
      questions: [
        {
          q: 'Does Jumbo remember our previous conversations?',
          a: 'Yes! Jumbo has memory capabilities and can remember important details from your conversations to provide more personalized and contextual support over time.'
        },
        {
          q: 'What kind of information does Jumbo remember?',
          a: 'Jumbo remembers important personal details you share, your preferences, significant events, relationships, and emotional patterns to provide better support.'
        },
        {
          q: 'Can I ask Jumbo to forget something?',
          a: 'While Jumbo doesn\'t have a specific "forget" command, you can always clarify or update information. Your privacy is important, and you control what you share.'
        },
        {
          q: 'How long does Jumbo remember things?',
          a: 'Jumbo maintains memory of your conversations to provide consistent support. Important information is retained to help build a meaningful relationship over time.'
        },
        {
          q: 'Can I have voice conversations with Jumbo?',
          a: 'Yes! Jumbo supports voice interaction. You can speak to Jumbo naturally and hear responses using advanced speech technology.'
        },
        {
          q: 'What should I talk to Jumbo about?',
          a: 'You can talk to Jumbo about anything on your mind - your feelings, daily experiences, concerns, achievements, relationships, or just casual conversation. Jumbo is here to listen and support you.'
        }
      ]
    },
    {
      id: 'privacy-safety',
      title: '🔒 Privacy & Safety',
      questions: [
        {
          q: 'Is my data safe with Jumbo?',
          a: 'Yes! Your conversations are protected with end-to-end encryption. We never share, sell, or analyze your personal data for advertising purposes.'
        },
        {
          q: 'Who can see my conversations?',
          a: 'Only you can see your conversations with Jumbo. Your data is private and secure, stored with industry-standard encryption.'
        },
        {
          q: 'Does Jumbo share my information with third parties?',
          a: 'No, we never share your personal information or conversation data with third parties. Your privacy is our top priority.'
        },
        {
          q: 'What if I\'m having thoughts of self-harm?',
          a: 'If you\'re experiencing thoughts of self-harm or are in crisis, please contact emergency services immediately (112) or reach out to crisis helplines like AASRA (91-9820466726). Jumbo can provide support, but professional help is essential for crisis situations.'
        },
        {
          q: 'Is Jumbo suitable for children?',
          a: 'Jumbo is designed for general audiences, but parental guidance is recommended for younger users. For children with mental health concerns, professional guidance is always recommended.'
        },
        {
          q: 'How do I report inappropriate responses?',
          a: 'If Jumbo provides an inappropriate response, please let us know through the contact form. We continuously work to improve Jumbo\'s responses and ensure they\'re helpful and appropriate.'
        }
      ]
    },
    {
      id: 'login-activity',
      title: '👤 Login & Activity',
      questions: [
        {
          q: 'How do I create an account?',
          a: 'Simply click "Get Started" on the main page and sign up with Google. The process is quick and secure, requiring no additional setup.'
        },
        {
          q: 'Can I use Jumbo without creating an account?',
          a: 'Currently, an account is required to use Jumbo. This allows us to remember your conversations and provide personalized support over time.'
        },
        {
          q: 'I forgot my password. How do I reset it?',
          a: 'If you signed up with Google, you can simply sign in with Google again. For other login methods, use the password reset option on the login page.'
        },
        {
          q: 'Can I delete my account?',
          a: 'Yes, you can delete your account and all associated data. Contact us through the support form, and we\'ll help you with account deletion.'
        },
        {
          q: 'Why do I need to complete onboarding?',
          a: 'Onboarding helps Jumbo understand your preferences and communication style, enabling more personalized and effective emotional support from the start.'
        },
        {
          q: 'Can I change my profile information?',
          a: 'Yes, you can update your profile information, including your preferred name and other details, through the profile page once you\'re logged in.'
        },
        {
          q: 'Is my account secure?',
          a: 'Yes, we use industry-standard security measures including secure authentication, encrypted data storage, and regular security updates to protect your account.'
        }
      ]
    }
  ];

  return (
    <GradientBackground variant="copilot" animated={true} style={styles.container}>
      <style>{`
        .contact-form input::placeholder,
        .contact-form textarea::placeholder,
        .contact-form select::placeholder {
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
          .help-content {
            padding: 20px 16px !important;
          }
          .form-row {
            grid-template-columns: 1fr !important;
          }
          .help-header {
            margin-bottom: 30px !important;
          }
          .help-title {
            font-size: 2rem !important;
          }
          .help-subtitle {
            font-size: 1rem !important;
          }
          .help-section {
            margin-bottom: 20px !important;
          }
          .section-header {
            padding: 16px !important;
          }
          .section-title {
            font-size: 1.1rem !important;
          }
          .question-item {
            padding: 16px !important;
          }
          .question-text {
            font-size: 0.95rem !important;
          }
          .answer-text {
            font-size: 0.9rem !important;
          }
        }
        
        @media (max-width: 480px) {
          .help-title {
            font-size: 1.8rem !important;
          }
          .help-subtitle {
            font-size: 0.9rem !important;
          }
          .back-button {
            padding: 8px 16px !important;
            font-size: 0.9rem !important;
          }
          .login-button {
            padding: 8px 16px !important;
            font-size: 0.9rem !important;
          }
        }
        
        .contact-form input::placeholder,
        .contact-form textarea::placeholder,
        .contact-form select::placeholder {
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
      `}</style>
      
      {/* Header with Back Button and Login */}
      <div style={styles.header}>
        <button 
          onClick={onBack}
          style={styles.backButton}
          className="back-button"
          onMouseEnter={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.target.style.background = 'rgba(255, 255, 255, 0.1)';
          }}
        >
          <ArrowLeft size={20} style={{ marginRight: '8px' }} />
          Back to Home
        </button>
        
        <button 
          onClick={onLogin}
          style={styles.loginButton}
          className="login-button"
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 20px 25px -5px rgba(139, 92, 246, 0.3)';
          }}
        >
          <LogIn size={18} style={{ marginRight: '8px' }} />
          Login
        </button>
      </div>

      <div style={styles.content} className="help-content">
        {/* Hero Section */}
        <div style={styles.heroSection} className="help-header">
          <h1 style={styles.title} className="help-title">
            Help & Support
          </h1>
          <p style={styles.subtitle} className="help-subtitle">
            Find answers to common questions about using Jumbo for emotional support and mental wellness
          </p>
        </div>

        {/* Help Sections */}
        <div style={styles.sectionsContainer}>
          {helpSections.map((section) => (
            <div key={section.id} style={styles.section} className="help-section">
              <div 
                style={styles.sectionHeader}
                className="section-header"
                onClick={() => toggleSection(section.id)}
              >
                <h2 style={styles.sectionTitle} className="section-title">
                  {section.title}
                </h2>
                <div style={styles.expandIcon}>
                  {expandedSection === section.id ? (
                    <ChevronDown size={24} color="white" />
                  ) : (
                    <ChevronRight size={24} color="white" />
                  )}
                </div>
              </div>
              
              {expandedSection === section.id && (
                <div style={styles.questionsContainer}>
                  {section.questions.map((item, index) => (
                    <div key={index} style={styles.questionItem} className="question-item">
                      <h3 style={styles.questionText} className="question-text">
                        {item.q}
                      </h3>
                      <p style={styles.answerText} className="answer-text">
                        {item.a}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Emergency Resources */}
        <div style={styles.emergencySection}>
          <h2 style={styles.emergencyTitle}>🚨 Crisis Resources</h2>
          <div style={styles.emergencyBox}>
            <p style={styles.emergencyText}>
              <strong>If you're in immediate danger or having thoughts of self-harm, please contact emergency services immediately.</strong>
            </p>
            <div style={styles.emergencyContacts}>
              <p style={styles.emergencyContactTitle}>Crisis Helplines:</p>
              <p style={styles.contactText}>
                • <strong>AASRA Helpline (Pan India):</strong> 📞 91-9820466726<br/>
                • <strong>Snehi Helpline:</strong> 📞 91-9582208181 (10 AM – 10 PM)<br/>
                • <strong>Local emergency services:</strong> 112
              </p>
            </div>
          </div>
        </div>

        {/* Contact Section with Formspree */}
        <div style={styles.contactSection}>
          <h2 style={styles.contactTitle}>Still Need Help?</h2>
          <p style={styles.contactDescription}>
            If you couldn't find the answer to your question, we're here to help! 
            Fill out the form below and we'll get back to you as soon as possible.
          </p>
          
          {/* Contact Form */}
          <div style={styles.contactFormSection}>
            <form 
              action="https://formspree.io/f/manlqopz" 
              method="POST"
              style={styles.contactForm}
              className="contact-form"
            >
              <div style={styles.formRow}>
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
                name="help_category"
                required
                style={styles.formSelect}
              >
                <option value="">What do you need help with?</option>
                <option value="account">👤 Account & Login Issues</option>
                <option value="conversation">💬 Conversation & Memory</option>
                <option value="mood">😊 Mood & Emotion Detection</option>
                <option value="privacy">🔒 Privacy & Safety</option>
                <option value="technical">⚙️ Technical Issues</option>
                <option value="feedback">💡 Feedback & Suggestions</option>
                <option value="collaboration">🤝 Collaboration Inquiry</option>
                <option value="other">❓ Other</option>
              </select>
              
              <textarea
                name="message"
                placeholder="Please describe your question or issue in detail..."
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
      </div>
    </GradientBackground>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
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
    background: 'rgba(0, 0, 0, 0.1)',
    backdropFilter: 'blur(20px)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
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
    maxWidth: '900px',
    margin: '0 auto',
    padding: '100px 24px 40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  heroSection: {
    textAlign: 'center',
    marginBottom: '60px',
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
    fontSize: '1.2rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.6',
    maxWidth: '600px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  sectionsContainer: {
    width: '100%',
    marginBottom: '60px',
  },
  section: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    marginBottom: '24px',
    overflow: 'hidden',
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  sectionTitle: {
    fontSize: '1.3rem',
    fontWeight: '600',
    color: 'white',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  expandIcon: {
    transition: 'transform 0.3s ease',
  },
  questionsContainer: {
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
  },
  questionItem: {
    padding: '20px 24px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  },
  questionText: {
    fontSize: '1.1rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '12px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  answerText: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  emergencySection: {
    width: '100%',
    marginBottom: '40px',
  },
  emergencyTitle: {
    fontSize: '1.8rem',
    fontWeight: '600',
    color: '#ef4444',
    marginBottom: '20px',
    textAlign: 'center',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  emergencyBox: {
    background: 'rgba(239, 68, 68, 0.1)',
    border: '2px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '16px',
    padding: '24px',
  },
  emergencyText: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.6',
    marginBottom: '16px',
    textAlign: 'center',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  emergencyContacts: {
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '12px',
    padding: '16px',
  },
  emergencyContactTitle: {
    fontSize: '1.1rem',
    fontWeight: '600',
    color: '#fca5a5',
    marginBottom: '8px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  contactText: {
    fontSize: '0.95rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.5',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  contactSection: {
    textAlign: 'center',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  contactTitle: {
    fontSize: '1.8rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  contactDescription: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.9)',
    lineHeight: '1.6',
    marginBottom: '24px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  contactFormSection: {
    marginTop: '40px',
    maxWidth: '600px',
    width: '100%',
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

export default HelpPage;