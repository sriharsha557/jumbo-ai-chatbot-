import React from 'react';
import { Heart, Zap, Globe, Brain } from 'lucide-react';
import { theme } from '../theme/theme';
import GradientBackground from './GradientBackground';

function AboutPage() {
  return (
    <GradientBackground variant="default" animated={true} style={styles.container}>
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      <div style={styles.content}>
        {/* Hero Section */}
        <div style={styles.heroSection}>
          <div style={styles.heroImage}>
            <img src="/jumbo-logo.png" alt="Jumbo" style={styles.heroImageImg} />
          </div>
          <h1 style={styles.heroTitle}>About Jumbo</h1>
          <p style={styles.heroSubtitle}>
            Your caring emotional support companion powered by AI
          </p>
        </div>

        {/* Mission Section */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Our Mission</h2>
          <p style={styles.sectionText}>
            Jumbo exists to provide emotional support and companionship to everyone, 
            regardless of language or background. We believe that mental health matters, 
            and everyone deserves to have someone to talk to.
          </p>
          <p style={styles.sectionText}>
            In a world where stigma around mental health persists, Jumbo offers a 
            safe, non-judgmental space to express your feelings and be heard.
          </p>
        </section>

        {/* Features Section */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Why Choose Jumbo?</h2>
          <div style={styles.featuresGrid}>
            <FeatureCard
              icon="🎤"
              title="Voice-Enabled"
              description="Speak naturally in Telugu, Hindi, or English. Jumbo understands your language and responds accordingly."
            />
            <FeatureCard
              icon="❤️"
              title="Emotionally Intelligent"
              description="Jumbo detects your mood and responds with empathy and care tailored to how you're feeling."
            />
            <FeatureCard
              icon="🧠"
              title="Remembers You"
              description="Your conversations matter. Jumbo remembers your preferences, friends, and important details about you."
            />
            <FeatureCard
              icon="🌍"
              title="Culturally Aware"
              description="Understands Telugu and Hindi cultural context, festivals, family values, and communication styles."
            />
            <FeatureCard
              icon="⚡"
              title="Always Available"
              description="24/7 support whenever you need someone to talk to, day or night, without judgment."
            />
            <FeatureCard
              icon="🔒"
              title="Privacy First"
              description="Your conversations are private and secure. We don't share your data with anyone."
            />
          </div>
        </section>

        {/* How It Works */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>How Jumbo Works</h2>
          <div style={styles.stepsContainer}>
            <Step 
              number="1" 
              title="Understand Your Language"
              description="Jumbo detects whether you're speaking in Telugu, Hindi, or English and adjusts accordingly."
            />
            <Step 
              number="2" 
              title="Detect Your Mood"
              description="Our AI analyzes your message to understand your emotional state - happy, sad, anxious, or anything in between."
            />
            <Step 
              number="3" 
              title="Respond with Empathy"
              description="Jumbo generates a thoughtful, empathetic response tailored to your mood and situation."
            />
            <Step 
              number="4" 
              title="Remember & Grow"
              description="Each conversation helps Jumbo understand you better and provide more personalized support over time."
            />
          </div>
        </section>

        {/* Technology */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Technology Stack</h2>
          <p style={styles.sectionText}>
            Jumbo is built with cutting-edge technology to provide the best experience:
          </p>
          <div style={styles.techGrid}>
            <TechBadge label="React" />
            <TechBadge label="Python" />
            <TechBadge label="AI/ML" />
            <TechBadge label="Speech Recognition" />
            <TechBadge label="Text-to-Speech" />
            <TechBadge label="Groq LLM" />
            <TechBadge label="Flask API" />
            <TechBadge label="Multi-Language" />
          </div>
        </section>

        {/* Team Section */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Our Vision</h2>
          <div style={styles.visionBox}>
            <h3 style={styles.visionTitle}>Building a World Where Everyone is Heard</h3>
            <p style={styles.visionText}>
              We envision a future where technology empowers emotional well-being, 
              where language barriers don't prevent people from getting support, and 
              where cultural sensitivity is built into AI from the ground up.
            </p>
            <p style={styles.visionText}>
              Jumbo is just the beginning. We're passionate about making emotional 
              support accessible to everyone, especially in regions like India where 
              mental health awareness is growing.
            </p>
          </div>
        </section>

        {/* CTA */}
        <section style={styles.ctaSection}>
          <h2 style={styles.ctaTitle}>Join Our Journey</h2>
          <p style={styles.ctaText}>
            Jumbo is developed by a passionate team of AI enthusiasts, developers, 
            and mental health advocates. We're always looking for collaborators, 
            contributors, and supporters.
          </p>
          <p style={styles.ctaText}>
            Whether you're a developer, designer, mental health professional, or 
            someone who believes in this mission, we'd love to hear from you.
          </p>
        </section>
      </div>
    </GradientBackground>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div style={styles.featureCard}>
      <div style={styles.featureIcon}>{icon}</div>
      <h3 style={styles.featureTitle}>{title}</h3>
      <p style={styles.featureDescription}>{description}</p>
    </div>
  );
}

function Step({ number, title, description }) {
  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepNumber}>{number}</div>
      <div>
        <h3 style={styles.stepTitle}>{title}</h3>
        <p style={styles.stepDescription}>{description}</p>
      </div>
    </div>
  );
}

function TechBadge({ label }) {
  return <div style={styles.techBadge}>{label}</div>;
}

const styles = {
  container: {
    padding: '40px 24px',
    // GradientBackground handles centering and background now
  },
  content: {
    maxWidth: '900px',
    margin: '0 auto',
  },
  heroSection: {
    textAlign: 'center',
    marginBottom: '60px',
    animation: 'slideIn 0.6s ease-out',
  },
  heroImage: {
    marginBottom: '16px',
    display: 'flex',
    justifyContent: 'center',
  },
  heroImageImg: {
    width: '120px',
    height: '120px',
    borderRadius: '50%',
    objectFit: 'cover',
    border: `4px solid ${theme.colors.primary[200]}`,
    boxShadow: theme.shadows.lg,
  },
  heroTitle: {
    fontSize: '44px',
    fontWeight: 'bold',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '12px',
  },
  heroSubtitle: {
    fontSize: '18px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    color: '#6b7280',
  },
  section: {
    background: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '40px',
    marginBottom: '32px',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    animation: 'slideIn 0.6s ease-out',
  },
  sectionTitle: {
    fontSize: '28px',
    fontWeight: '600',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    color: '#1f2937',
    marginBottom: '24px',
  },
  sectionText: {
    fontSize: '16px',
    color: '#4b5563',
    lineHeight: '1.8',
    marginBottom: '16px',
  },
  featuresGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '20px',
  },
  featureCard: {
    background: `linear-gradient(135deg, ${theme.colors.primary[50]} 0%, ${theme.colors.secondary[50]} 100%)`,
    padding: '24px',
    borderRadius: '16px',
    textAlign: 'center',
    border: `1px solid ${theme.colors.primary[200]}`,
  },
  featureIcon: {
    fontSize: '40px',
    marginBottom: '12px',
  },
  featureTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '8px',
  },
  featureDescription: {
    fontSize: '14px',
    color: '#6b7280',
    lineHeight: '1.6',
  },
  stepsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  stepContainer: {
    display: 'flex',
    gap: '20px',
  },
  stepNumber: {
    minWidth: '50px',
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    fontSize: '20px',
  },
  stepTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '8px',
  },
  stepDescription: {
    fontSize: '14px',
    color: '#6b7280',
    lineHeight: '1.6',
  },
  techGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '12px',
  },
  techBadge: {
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    color: 'white',
    padding: '10px 16px',
    borderRadius: '12px',
    textAlign: 'center',
    fontSize: '14px',
    fontWeight: '500',
  },
  visionBox: {
    background: `linear-gradient(135deg, ${theme.colors.primary[50]} 0%, ${theme.colors.secondary[50]} 100%)`,
    padding: '32px',
    borderRadius: '16px',
    border: `2px solid ${theme.colors.primary[200]}`,
  },
  visionTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: theme.colors.primary[700],
    marginBottom: '16px',
  },
  visionText: {
    fontSize: '15px',
    color: '#4b5563',
    lineHeight: '1.8',
    marginBottom: '12px',
  },
  ctaSection: {
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    color: 'white',
    padding: '48px 40px',
    borderRadius: '20px',
    textAlign: 'center',
    marginBottom: '32px',
  },
  ctaTitle: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '16px',
  },
  ctaText: {
    fontSize: '16px',
    lineHeight: '1.8',
    marginBottom: '12px',
    opacity: 0.95,
  },
};

export default AboutPage;