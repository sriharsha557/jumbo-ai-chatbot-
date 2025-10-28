import React, { useState } from 'react';
import { Mail, Github, Linkedin, Twitter, Send, Users, Lightbulb, Code } from 'lucide-react';
import { theme } from '../theme/theme';

function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'developer',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.name && formData.email && formData.message) {
      setSubmitted(true);
      setFormData({ name: '', email: '', role: 'developer', message: '' });
      setTimeout(() => setSubmitted(false), 5000);
    }
  };

  return (
    <div style={styles.container}>
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}</style>

      <div style={styles.content}>
        {/* Hero Section */}
        <div style={styles.heroSection}>
          <h1 style={styles.heroTitle}>Let's Build Together</h1>
          <p style={styles.heroSubtitle}>
            Jumbo is an open collaboration. I welcome developers, designers, 
            mental health professionals, and visionaries who share our mission.
          </p>
        </div>

        <div style={styles.mainGrid}>
          {/* How You Can Help */}
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>How You Can Help</h2>
            <div style={styles.rolesGrid}>
              <RoleCard
                icon={<Code size={32} />}
                role="Developers"
                description="Help us build better AI, improve speech recognition, add new languages, or optimize the platform."
                color="#3b82f6"
              />
              <RoleCard
                icon={<Users size={32} />}
                role="Designers"
                description="Create beautiful UI/UX, improve accessibility, design marketing materials, and enhance user experience."
                color="#ec4899"
              />
              <RoleCard
                icon={<Lightbulb size={32} />}
                role="Mental Health Experts"
                description="Guide our AI responses, ensure cultural sensitivity, improve emotional intelligence, and validate approaches."
                color="#f59e0b"
              />
              <RoleCard
                icon={<Users size={32} />}
                role="Community Advocates"
                description="Help spread awareness, gather feedback from users, conduct research, and build communities."
                color="#10b981"
              />
            </div>
          </section>

          {/* Contact Form */}
          <section style={styles.formSection}>
            <h2 style={styles.sectionTitle}>Get in Touch</h2>
            
            {submitted && (
              <div style={styles.successMessage}>
                <p style={styles.successText}>
                  ✓ Thanks for reaching out! We'll be in touch soon.
                </p>
              </div>
            )}

            <form onSubmit={handleSubmit} style={styles.form}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Your Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Enter your name"
                  required
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Email Address</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="aivisionaryforfuture@gmail.com"
                  required
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>I'm a...</label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  style={styles.select}
                >
                  <option value="developer">Developer</option>
                  <option value="designer">Designer</option>
                  <option value="mental_health">Mental Health Professional</option>
                  <option value="researcher">Researcher</option>
                  <option value="advocate">Community Advocate</option>
                  <option value="investor">Investor / Supporter</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Your Message</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  placeholder="Tell us about your idea, expertise, or how you'd like to collaborate..."
                  required
                  style={styles.textarea}
                  rows={6}
                />
              </div>

              <button type="submit" style={styles.submitButton}>
                <Send size={18} />
                Send Message
              </button>
            </form>
          </section>
        </div>

        {/* Direct Contact & Social */}
        <section style={styles.contactSection}>
          <h2 style={styles.sectionTitle}>Other Ways to Connect</h2>
          
          <div style={styles.contactGrid}>
            <ContactMethod
              icon={<Mail size={24} />}
              title="Email"
              description="hello@jumbo.ai"
              link="mailto:hello@jumbo.ai"
            />
            <ContactMethod
              icon={<Github size={24} />}
              title="GitHub"
              description="github.com/hellojumbo"
              link="https://github.com"
            />
            <ContactMethod
              icon={<Linkedin size={24} />}
              title="LinkedIn"
              description="linkedin.com/company/jumbo"
              link="https://linkedin.com"
            />
            <ContactMethod
              icon={<Twitter size={24} />}
              title="Twitter"
              description="@jumpoacompanion"
              link="https://twitter.com"
            />
          </div>
        </section>

        {/* FAQ Section */}
        <section style={styles.faqSection}>
          <h2 style={styles.sectionTitle}>Frequently Asked Questions</h2>
          
          <FAQ
            question="Is Jumbo open source?"
            answer="We're working on opening up parts of Jumbo. Right now, we welcome contributions and collaborations. Reach out to discuss."
          />
          <FAQ
            question="Do I need experience to contribute?"
            answer="Not at all! We welcome everyone from beginners to experts. We believe in learning together as a community."
          />
          <FAQ
            question="What's the development roadmap?"
            answer="We're focusing on: multi-language support, improved emotional intelligence, integration with mental health resources, and Android/iOS apps."
          />
          <FAQ
            question="How is user data handled?"
            answer="User privacy is paramount. Data is encrypted, stored securely, and never shared. Users have full control over their data."
          />
          <FAQ
            question="Can I use Jumbo commercially?"
            answer="We're open to partnerships and commercial use cases. Let's discuss your idea!"
          />
        </section>

        {/* CTA */}
        <section style={styles.ctaSection}>
          <h2 style={styles.ctaTitle}>Ready to Make a Difference?</h2>
          <p style={styles.ctaText}>
            Every contribution, big or small, helps us build a better emotional support system for everyone.
          </p>
          <a href="mailto:aivisionaryforfuture@gmail.com" style={styles.ctaButton}>
            Start Collaborating Today
          </a>
        </section>
      </div>
    </div>
  );
}

function RoleCard({ icon, role, description, color }) {
  return (
    <div style={styles.roleCard}>
      <div style={{ ...styles.roleIcon, color }}>{icon}</div>
      <h3 style={styles.roleTitle}>{role}</h3>
      <p style={styles.roleDescription}>{description}</p>
    </div>
  );
}

function ContactMethod({ icon, title, description, link }) {
  return (
    <a href={link} target="_blank" rel="noopener noreferrer" style={styles.contactMethod}>
      <div style={styles.contactIcon}>{icon}</div>
      <h3 style={styles.contactTitle}>{title}</h3>
      <p style={styles.contactDescription}>{description}</p>
    </a>
  );
}

function FAQ({ question, answer }) {
  const [open, setOpen] = React.useState(false);

  return (
    <div style={styles.faqItem}>
      <button
        onClick={() => setOpen(!open)}
        style={styles.faqQuestion}
      >
        <span>{question}</span>
        <span style={{ transform: open ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.3s' }}>
          ▼
        </span>
      </button>
      {open && <p style={styles.faqAnswer}>{answer}</p>}
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: `linear-gradient(135deg, ${theme.colors.primary[50]} 0%, ${theme.colors.primary[100]} 50%, ${theme.colors.secondary[50]} 100%)`,
    padding: '40px 24px',
  },
  content: {
    maxWidth: '1000px',
    margin: '0 auto',
  },
  heroSection: {
    textAlign: 'center',
    marginBottom: '60px',
  },
  heroTitle: {
    fontSize: '44px',
    fontWeight: 'bold',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '16px',
  },
  heroSubtitle: {
    fontSize: '18px',
    color: '#6b7280',
    maxWidth: '600px',
    margin: '0 auto',
    lineHeight: '1.6',
  },
  mainGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '32px',
    marginBottom: '60px',
  },
  section: {
    background: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '40px',
    border: '1px solid rgba(255, 255, 255, 0.3)',
  },
  formSection: {
    background: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '40px',
    border: '1px solid rgba(255, 255, 255, 0.3)',
  },
  sectionTitle: {
    fontSize: '28px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '24px',
  },
  rolesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '16px',
  },
  roleCard: {
    background: `linear-gradient(135deg, ${theme.colors.primary[50]} 0%, ${theme.colors.secondary[50]} 100%)`,
    padding: '24px',
    borderRadius: '16px',
    textAlign: 'center',
    border: `1px solid ${theme.colors.primary[200]}`,
    transition: 'all 0.3s',
  },
  roleIcon: {
    marginBottom: '12px',
    display: 'flex',
    justifyContent: 'center',
  },
  roleTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '8px',
  },
  roleDescription: {
    fontSize: '13px',
    color: '#6b7280',
    lineHeight: '1.6',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
  },
  input: {
    padding: '12px 16px',
    border: `2px solid ${theme.colors.primary[200]}`,
    borderRadius: '12px',
    fontSize: '14px',
    outline: 'none',
    transition: 'all 0.3s',
    boxSizing: 'border-box',
  },
  select: {
    padding: '12px 16px',
    border: `2px solid ${theme.colors.primary[200]}`,
    borderRadius: '12px',
    fontSize: '14px',
    outline: 'none',
    boxSizing: 'border-box',
    cursor: 'pointer',
  },
  textarea: {
    padding: '12px 16px',
    border: `2px solid ${theme.colors.primary[200]}`,
    borderRadius: '12px',
    fontSize: '14px',
    outline: 'none',
    resize: 'vertical',
    fontFamily: 'inherit',
    boxSizing: 'border-box',
  },
  submitButton: {
    padding: '12px 24px',
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    fontWeight: '600',
    fontSize: '16px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    transition: 'all 0.3s',
  },
  successMessage: {
    background: 'rgba(16, 185, 129, 0.1)',
    border: '2px solid rgba(16, 185, 129, 0.3)',
    borderRadius: '12px',
    padding: '16px',
    marginBottom: '16px',
    animation: 'fadeIn 0.3s',
  },
  successText: {
    color: '#059669',
    fontSize: '14px',
    margin: 0,
    fontWeight: '500',
  },
  contactSection: {
    marginBottom: '60px',
  },
  contactGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
  },
  contactMethod: {
    background: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '24px',
    textAlign: 'center',
    textDecoration: 'none',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    transition: 'all 0.3s',
    cursor: 'pointer',
  },
  contactIcon: {
    color: theme.colors.primary[600],
    marginBottom: '12px',
    display: 'flex',
    justifyContent: 'center',
  },
  contactTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '8px',
  },
  contactDescription: {
    fontSize: '14px',
    color: '#6b7280',
  },
  faqSection: {
    background: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '40px',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    marginBottom: '60px',
  },
  faqItem: {
    borderBottom: '1px solid #e5e7eb',
    paddingBottom: '16px',
    marginBottom: '16px',
  },
  faqQuestion: {
    width: '100%',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 0',
    background: 'none',
    border: 'none',
    fontSize: '15px',
    fontWeight: '600',
    color: '#1f2937',
    cursor: 'pointer',
    textAlign: 'left',
  },
  faqAnswer: {
    fontSize: '14px',
    color: '#6b7280',
    lineHeight: '1.6',
    marginTop: '12px',
  },
  ctaSection: {
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    color: 'white',
    padding: '48px 40px',
    borderRadius: '20px',
    textAlign: 'center',
  },
  ctaTitle: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '16px',
  },
  ctaText: {
    fontSize: '16px',
    lineHeight: '1.6',
    marginBottom: '24px',
    opacity: 0.95,
  },
  ctaButton: {
    display: 'inline-block',
    padding: '12px 32px',
    background: 'rgba(255, 255, 255, 0.2)',
    color: 'white',
    border: '2px solid rgba(255, 255, 255, 0.5)',
    borderRadius: '12px',
    fontWeight: '600',
    textDecoration: 'none',
    transition: 'all 0.3s',
    cursor: 'pointer',
  },
};
export default ContactPage;