import React, { useState } from 'react';
import GradientBackground from './GradientBackground';
import { theme } from '../theme/theme';

function GradientDemo() {
  const [currentVariant, setCurrentVariant] = useState('copilot');
  const [isAnimated, setIsAnimated] = useState(true);

  const variants = [
    { key: 'copilot', name: 'Copilot Style', description: 'Deep blue gradient inspired by GitHub Copilot' },
    { key: 'default', name: 'Default', description: 'Balanced blue gradient with light accents' },
    { key: 'ocean', name: 'Ocean', description: 'Bright ocean blue gradient' },
    { key: 'deep', name: 'Deep Sea', description: 'Dark mysterious blue gradient' },
  ];

  return (
    <GradientBackground variant={currentVariant} animated={isAnimated} hasNavigation={true} style={styles.container}>
      <div style={styles.content}>
        <div style={styles.header}>
          <h1 style={styles.title}>Beautiful Blue Gradients</h1>
          <p style={styles.subtitle}>
            Choose your perfect blue gradient background
          </p>
        </div>

        <div style={styles.controls}>
          <div style={styles.controlGroup}>
            <h3 style={styles.controlTitle}>Gradient Variants</h3>
            <div style={styles.buttonGrid}>
              {variants.map((variant) => (
                <button
                  key={variant.key}
                  onClick={() => setCurrentVariant(variant.key)}
                  style={{
                    ...styles.variantButton,
                    ...(currentVariant === variant.key ? styles.variantButtonActive : {})
                  }}
                >
                  <div style={styles.variantName}>{variant.name}</div>
                  <div style={styles.variantDescription}>{variant.description}</div>
                </button>
              ))}
            </div>
          </div>

          <div style={styles.controlGroup}>
            <h3 style={styles.controlTitle}>Animation</h3>
            <button
              onClick={() => setIsAnimated(!isAnimated)}
              style={{
                ...styles.animationButton,
                ...(isAnimated ? styles.animationButtonActive : {})
              }}
            >
              {isAnimated ? '🌊 Animated' : '🏔️ Static'}
            </button>
          </div>
        </div>

        <div style={styles.preview}>
          <div style={styles.previewCard}>
            <h2 style={styles.previewTitle}>Current: {variants.find(v => v.key === currentVariant)?.name}</h2>
            <p style={styles.previewDescription}>
              {variants.find(v => v.key === currentVariant)?.description}
            </p>
            <div style={styles.features}>
              <div style={styles.feature}>✨ Smooth animations</div>
              <div style={styles.feature}>🎨 Beautiful gradients</div>
              <div style={styles.feature}>📱 Responsive design</div>
              <div style={styles.feature}>⚡ High performance</div>
            </div>
          </div>
        </div>
      </div>
    </GradientBackground>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
  },
  content: {
    width: '100%',
    maxWidth: '1000px',
    textAlign: 'center',
  },
  header: {
    marginBottom: '40px',
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
    color: 'rgba(255, 255, 255, 0.8)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  controls: {
    marginBottom: '40px',
  },
  controlGroup: {
    marginBottom: '30px',
  },
  controlTitle: {
    fontSize: '1.5rem',
    color: 'white',
    marginBottom: '20px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  buttonGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px',
    marginBottom: '20px',
  },
  variantButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '16px',
    padding: '20px',
    color: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textAlign: 'left',
  },
  variantButtonActive: {
    background: 'rgba(255, 255, 255, 0.2)',
    border: '2px solid rgba(255, 255, 255, 0.4)',
    transform: 'translateY(-2px)',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
  },
  variantName: {
    fontSize: '1.1rem',
    fontWeight: '600',
    marginBottom: '8px',
  },
  variantDescription: {
    fontSize: '0.9rem',
    opacity: 0.8,
    lineHeight: '1.4',
  },
  animationButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '50px',
    padding: '12px 24px',
    color: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    fontSize: '1.1rem',
    fontWeight: '600',
  },
  animationButtonActive: {
    background: 'rgba(255, 255, 255, 0.2)',
    border: '2px solid rgba(255, 255, 255, 0.4)',
    transform: 'translateY(-2px)',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
  },
  preview: {
    display: 'flex',
    justifyContent: 'center',
  },
  previewCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '40px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    maxWidth: '500px',
    textAlign: 'center',
  },
  previewTitle: {
    fontSize: '1.8rem',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  previewDescription: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '30px',
    lineHeight: '1.6',
  },
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '12px',
  },
  feature: {
    fontSize: '0.9rem',
    color: 'rgba(255, 255, 255, 0.9)',
    padding: '8px',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
  },
};

export default GradientDemo;