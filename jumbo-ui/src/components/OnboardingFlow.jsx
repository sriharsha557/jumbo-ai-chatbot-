import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import GradientBackground from './GradientBackground';
import { theme } from '../theme/theme';
import { Sparkles } from 'lucide-react';

const OnboardingFlow = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [onboardingData, setOnboardingData] = useState({});
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkUser();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const checkUser = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    setUser(user);
    
    // Check localStorage for existing onboarding data
    const storedOnboardingData = localStorage.getItem('jumbo_onboarding_data');
    const storedOnboardingCompleted = localStorage.getItem('jumbo_onboarding_completed');
    
    if (storedOnboardingCompleted === 'true') {
      onComplete();
      return;
    }
    
    if (storedOnboardingData) {
      try {
        const parsedData = JSON.parse(storedOnboardingData);
        setOnboardingData(parsedData);
        
        // Determine current step based on stored data
        let step = 1;
        if (parsedData.step_1) step = 2;
        if (parsedData.step_2) step = 3;
        if (parsedData.step_3) step = 4;
        if (parsedData.step_4) step = 5;
        if (parsedData.step_5) step = 6;
        if (parsedData.step_6) step = 7;
        
        setCurrentStep(step);
      } catch (error) {
        console.error('Error parsing stored onboarding data:', error);
      }
    }
  };

  const saveStep = async (stepData) => {
    setLoading(true);
    
    // For now, save data locally instead of API call
    console.log(`Saving step ${currentStep}:`, stepData);
    
    // Update onboarding data
    setOnboardingData(prev => ({
      ...prev,
      [`step_${currentStep}`]: stepData
    }));
    
    // Store in localStorage for persistence
    const updatedData = {
      ...onboardingData,
      [`step_${currentStep}`]: stepData
    };
    localStorage.setItem('jumbo_onboarding_data', JSON.stringify(updatedData));
    
    // Move to next step or complete
    if (currentStep < 7) {
      setCurrentStep(currentStep + 1);
    } else {
      await completeOnboarding();
    }
    
    setLoading(false);
  };

  const completeOnboarding = async () => {
    try {
      // Store completion data locally
      const finalOnboardingData = {
        ...onboardingData,
        completed_at: new Date().toISOString(),
        version: '1.0'
      };
      
      console.log('🔍 Completing onboarding with data:', finalOnboardingData);
      console.log('🔍 Step 2 data (name):', finalOnboardingData.step_2);
      
      // Save to backend
      try {
        const storedUser = localStorage.getItem('jumbo_user');
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          
          // Use environment variable for production
          console.log('🔍 Environment check:', {
            NODE_ENV: process.env.NODE_ENV,
            REACT_APP_API_URL: process.env.REACT_APP_API_URL,
            allEnvVars: Object.keys(process.env).filter(key => key.startsWith('REACT_APP_'))
          });
          
          const apiUrl = process.env.REACT_APP_API_URL || (() => {
            console.warn('⚠️ REACT_APP_API_URL not found, using fallback');
            if (process.env.NODE_ENV === 'production') {
              console.error('❌ REACT_APP_API_URL not set in production!');
              throw new Error('API_URL not configured for production');
            }
            return 'http://localhost:5000/api/v1';
          })();
          console.log('🔍 API URL being used:', apiUrl);
          console.log('🔍 Full URL:', `${apiUrl}/onboarding/complete`);
          
          const response = await fetch(`${apiUrl}/onboarding/complete`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${userData.access_token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              onboarding_data: finalOnboardingData
            })
          });
          
          if (response.ok) {
            console.log('✅ Onboarding saved to backend');
          } else {
            console.warn('⚠️ Failed to save onboarding to backend, using localStorage fallback');
          }
        }
      } catch (error) {
        console.warn('⚠️ Backend save failed, using localStorage fallback:', error);
      }
      
      // Store in localStorage (fallback)
      localStorage.setItem('jumbo_onboarding_data', JSON.stringify(finalOnboardingData));
      localStorage.setItem('jumbo_onboarding_completed', 'true');
      
      // Call completion callback
      onComplete();
    } catch (error) {
      console.error('Error completing onboarding:', error);
    }
  };

  const goBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <WelcomeStep onNext={saveStep} loading={loading} />;
      case 2:
        return <PersonalInfoStep onNext={saveStep} onBack={goBack} loading={loading} />;
      case 3:
        return <EmotionalBaselineStep onNext={saveStep} onBack={goBack} loading={loading} />;
      case 4:
        return <SupportStyleStep onNext={saveStep} onBack={goBack} loading={loading} />;
      case 5:
        return <FocusAreasStep onNext={saveStep} onBack={goBack} loading={loading} />;
      case 6:
        return <CheckinPreferencesStep onNext={saveStep} onBack={goBack} loading={loading} />;
      case 7:
        return <SummaryStep onNext={saveStep} onBack={goBack} loading={loading} data={onboardingData} />;
      default:
        return <WelcomeStep onNext={saveStep} loading={loading} />;
    }
  };

  return (
    <GradientBackground variant="copilot" animated={true} style={styles.container}>
      <div style={styles.content}>
        <div style={styles.progressSection}>
          <div style={styles.progressBar}>
            <div 
              style={{ 
                ...styles.progressFill,
                width: `${(currentStep / 7) * 100}%` 
              }}
            />
          </div>
          <span style={styles.progressText}>Step {currentStep} of 7</span>
        </div>
        
        <div style={styles.onboardingCard} className="onboarding-responsive">
          {renderStep()}
        </div>
      </div>
    </GradientBackground>
  );
};

// Step 1: Welcome
const WelcomeStep = ({ onNext, loading }) => {
  const handleNext = () => {
    onNext({
      welcome_seen: true,
      timestamp: new Date().toISOString()
    });
  };

  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepContent}>
        <div style={styles.logoContainer}>
          <img 
            src="/jumbo-logo.png" 
            alt="Jumbo Logo" 
            style={styles.logo}
          />
        </div>
        
        <h1 style={styles.welcomeTitle}>Hey, I'm Jumbo</h1>
        <p style={styles.welcomeSubtitle}>Your emotional companion</p>
        <p style={styles.welcomeDescription}>
          I'll help you reflect, recharge, and grow a little calmer each day. 
          Let's set things up so I can support you better 💛
        </p>
        
        <button 
          style={styles.primaryButton}
          onClick={handleNext}
          disabled={loading}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 25px 50px -12px rgba(139, 92, 246, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 20px 25px -5px rgba(139, 92, 246, 0.3)';
          }}
        >
          <Sparkles size={20} style={{ marginRight: '8px' }} />
          {loading ? 'Starting...' : "Let's Begin"}
        </button>
      </div>
    </div>
  );
};

// Step 2: Personal Info
const PersonalInfoStep = ({ onNext, onBack, loading }) => {
  const [formData, setFormData] = useState({
    display_name: '',
    pronouns: '',
    preferred_language: 'en'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.display_name.trim()) {
      onNext(formData);
    }
  };

  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepContent}>
        <h2 style={styles.stepTitle}>Let's get to know you</h2>
        <p style={styles.stepSubtitle}>Help me personalize our conversations</p>
        
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>What should I call you?</label>
            <input
              type="text"
              value={formData.display_name}
              onChange={(e) => setFormData({...formData, display_name: e.target.value})}
              placeholder="Your name"
              required
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Pronouns</label>
            <div style={styles.radioGroup}>
              {['he/him', 'she/her', 'they/them', 'prefer_not_to_say'].map(pronoun => (
                <label key={pronoun} style={styles.radioOption}>
                  <input
                    type="radio"
                    name="pronouns"
                    value={pronoun}
                    checked={formData.pronouns === pronoun}
                    onChange={(e) => setFormData({...formData, pronouns: e.target.value})}
                    style={styles.radioInput}
                  />
                  <span style={styles.radioLabel}>
                    {pronoun === 'prefer_not_to_say' ? 'Prefer not to say' : pronoun}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Preferred Language</label>
            <select
              value={formData.preferred_language}
              onChange={(e) => setFormData({...formData, preferred_language: e.target.value})}
              style={styles.select}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div style={styles.stepNavigation}>
            <button type="button" onClick={onBack} style={styles.secondaryButton}>
              Back
            </button>
            <button 
              type="submit" 
              style={{
                ...styles.primaryButton,
                opacity: loading || !formData.display_name.trim() ? 0.6 : 1
              }}
              disabled={loading || !formData.display_name.trim()}
            >
              {loading ? 'Saving...' : 'Next'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Step 3: Emotional Baseline
const EmotionalBaselineStep = ({ onNext, onBack, loading }) => {
  const [formData, setFormData] = useState({
    current_mood: null,
    emotion_comfort_level: ''
  });

  const moodEmojis = ['😞', '😕', '😐', '🙂', '😄'];
  const moodLabels = ['Very Low', 'Low', 'Neutral', 'Good', 'Great'];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.current_mood && formData.emotion_comfort_level) {
      onNext(formData);
    }
  };

  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepContent}>
        <h2 style={styles.stepTitle}>How are you feeling today?</h2>
        <p style={styles.stepSubtitle}>This helps me understand where you're starting from</p>
        
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Current mood</label>
            <div style={styles.moodSelector} className="mood-selector">
              {moodEmojis.map((emoji, index) => (
                <button
                  key={index}
                  type="button"
                  style={{
                    ...styles.moodOption,
                    ...(formData.current_mood === index + 1 ? styles.moodOptionSelected : {})
                  }}
                  onClick={() => setFormData({...formData, current_mood: index + 1})}
                >
                  <span style={styles.moodEmoji}>{emoji}</span>
                  <span style={styles.moodLabel}>{moodLabels[index]}</span>
                </button>
              ))}
            </div>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Do you find it easy to talk about your emotions?</label>
            <div style={styles.radioGroup}>
              {[
                { value: 'easy', label: 'Yes, pretty easy' },
                { value: 'sometimes', label: 'Sometimes' },
                { value: 'difficult', label: 'Not really' }
              ].map(option => (
                <label key={option.value} style={styles.radioOption}>
                  <input
                    type="radio"
                    name="emotion_comfort"
                    value={option.value}
                    checked={formData.emotion_comfort_level === option.value}
                    onChange={(e) => setFormData({...formData, emotion_comfort_level: e.target.value})}
                    style={styles.radioInput}
                  />
                  <span style={styles.radioLabel}>{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          {formData.current_mood && (
            <div style={styles.encouragementMessage}>
              <p style={styles.encouragementText}>💛 Thanks for sharing. I'm here to support you wherever you are.</p>
            </div>
          )}

          <div style={styles.stepNavigation}>
            <button type="button" onClick={onBack} style={styles.secondaryButton}>
              Back
            </button>
            <button 
              type="submit" 
              style={{
                ...styles.primaryButton,
                opacity: loading || !formData.current_mood || !formData.emotion_comfort_level ? 0.6 : 1
              }}
              disabled={loading || !formData.current_mood || !formData.emotion_comfort_level}
            >
              {loading ? 'Saving...' : 'Next'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Step 4: Support Style
const SupportStyleStep = ({ onNext, onBack, loading }) => {
  const [formData, setFormData] = useState({
    support_style: '',
    communication_tone: ''
  });

  const supportStyles = [
    { value: 'calm_comforting', emoji: '🧘', label: 'Calm & comforting', desc: 'Gentle, soothing responses' },
    { value: 'honest_real', emoji: '💬', label: 'Honest & real', desc: 'Direct, authentic conversations' },
    { value: 'motivational', emoji: '⚡', label: 'Motivational', desc: 'Encouraging and energizing' },
    { value: 'fun_distraction', emoji: '🎧', label: 'Fun distraction', desc: 'Light-hearted and playful' }
  ];

  const tones = [
    { value: 'calm', label: 'Calm' },
    { value: 'cheerful', label: 'Cheerful' },
    { value: 'deep', label: 'Deep' },
    { value: 'friendly', label: 'Friendly' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.support_style && formData.communication_tone) {
      onNext(formData);
    }
  };

  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepContent}>
        <h2 style={styles.stepTitle}>How can I best support you?</h2>
        <p style={styles.stepSubtitle}>When you're feeling low, what kind of support helps most?</p>
        
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Support style</label>
            <div style={styles.supportGrid} className="support-grid">
              {supportStyles.map(style => (
                <button
                  key={style.value}
                  type="button"
                  style={{
                    ...styles.supportOption,
                    ...(formData.support_style === style.value ? styles.supportOptionSelected : {})
                  }}
                  onClick={() => setFormData({...formData, support_style: style.value})}
                >
                  <span style={styles.supportEmoji}>{style.emoji}</span>
                  <span style={styles.supportLabel}>{style.label}</span>
                  <span style={styles.supportDesc}>{style.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>How do you want Jumbo to sound when we chat?</label>
            <div style={styles.supportGrid} className="support-grid">
              {tones.map(tone => (
                <label 
                  key={tone.value} 
                  style={{
                    ...styles.radioOption,
                    ...(formData.communication_tone === tone.value ? { borderColor: '#8b5cf6', background: 'rgba(139, 92, 246, 0.2)' } : {})
                  }}
                >
                  <input
                    type="radio"
                    name="tone"
                    value={tone.value}
                    checked={formData.communication_tone === tone.value}
                    onChange={(e) => setFormData({...formData, communication_tone: e.target.value})}
                    style={styles.radioInput}
                  />
                  <span style={styles.radioLabel}>{tone.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div style={styles.stepNavigation}>
            <button type="button" onClick={onBack} style={styles.secondaryButton}>
              Back
            </button>
            <button 
              type="submit" 
              style={{
                ...styles.primaryButton,
                opacity: loading || !formData.support_style || !formData.communication_tone ? 0.6 : 1
              }}
              disabled={loading || !formData.support_style || !formData.communication_tone}
            >
              {loading ? 'Saving...' : 'Next'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Step 5: Focus Areas
const FocusAreasStep = ({ onNext, onBack, loading }) => {
  const [selectedAreas, setSelectedAreas] = useState([]);

  const focusAreas = [
    { value: 'sleep', emoji: '😴', label: 'Better sleep' },
    { value: 'stress', emoji: '😌', label: 'Stress relief' },
    { value: 'awareness', emoji: '💭', label: 'Self-awareness' },
    { value: 'balance', emoji: '❤️', label: 'Emotional balance' },
    { value: 'motivation', emoji: '💪', label: 'Motivation' },
    { value: 'mindfulness', emoji: '🧘', label: 'Mindfulness' }
  ];

  const toggleArea = (area) => {
    setSelectedAreas(prev => {
      if (prev.includes(area)) {
        return prev.filter(a => a !== area);
      } else if (prev.length < 3) {
        return [...prev, area];
      }
      return prev;
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedAreas.length > 0) {
      onNext({ selected_areas: selectedAreas });
    }
  };

  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepContent}>
        <h2 style={styles.stepTitle}>What would you like to work on?</h2>
        <p style={styles.stepSubtitle}>Choose up to 3 areas where you'd like Jumbo's support</p>
        
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.focusGrid}>
            {focusAreas.map(area => (
              <button
                key={area.value}
                type="button"
                style={{
                  ...styles.focusOption,
                  ...(selectedAreas.includes(area.value) ? styles.focusOptionSelected : {}),
                  ...(!selectedAreas.includes(area.value) && selectedAreas.length >= 3 ? styles.focusOptionDisabled : {})
                }}
                onClick={() => toggleArea(area.value)}
                disabled={!selectedAreas.includes(area.value) && selectedAreas.length >= 3}
              >
                <span style={styles.focusEmoji}>{area.emoji}</span>
                <span style={styles.focusLabel}>{area.label}</span>
              </button>
            ))}
          </div>
          
          <p style={styles.selectionCount}>
            {selectedAreas.length}/3 selected
          </p>

          <div style={styles.stepNavigation}>
            <button type="button" onClick={onBack} style={styles.secondaryButton}>
              Back
            </button>
            <button 
              type="submit" 
              style={{
                ...styles.primaryButton,
                opacity: loading || selectedAreas.length === 0 ? 0.6 : 1
              }}
              disabled={loading || selectedAreas.length === 0}
            >
              {loading ? 'Saving...' : 'Next'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Step 6: Check-in Preferences
const CheckinPreferencesStep = ({ onNext, onBack, loading }) => {
  const [formData, setFormData] = useState({
    frequency: '',
    time: '',
    custom_time: ''
  });

  const frequencies = [
    { value: 'daily', label: 'Daily' },
    { value: 'few_times_week', label: 'A few times a week' },
    { value: 'on_demand', label: 'Only when I open the app' }
  ];

  const times = [
    { value: 'morning', label: 'Morning' },
    { value: 'evening', label: 'Evening' },
    { value: 'custom', label: 'Custom time' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.frequency && (formData.frequency === 'on_demand' || formData.time)) {
      onNext(formData);
    }
  };

  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepContent}>
        <h2 style={styles.stepTitle}>When should I check in?</h2>
        <p style={styles.stepSubtitle}>Let's set up a rhythm that works for you</p>
        
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>How often should I check in with you?</label>
            <div style={styles.radioGroup}>
              {frequencies.map(freq => (
                <label key={freq.value} style={styles.radioOption}>
                  <input
                    type="radio"
                    name="frequency"
                    value={freq.value}
                    checked={formData.frequency === freq.value}
                    onChange={(e) => setFormData({...formData, frequency: e.target.value})}
                    style={styles.radioInput}
                  />
                  <span style={styles.radioLabel}>{freq.label}</span>
                </label>
              ))}
            </div>
          </div>

          {formData.frequency && formData.frequency !== 'on_demand' && (
            <div style={styles.formGroup}>
              <label style={styles.label}>Best time for a gentle check-in?</label>
              <div style={styles.radioGroup}>
                {times.map(time => (
                  <label key={time.value} style={styles.radioOption}>
                    <input
                      type="radio"
                      name="time"
                      value={time.value}
                      checked={formData.time === time.value}
                      onChange={(e) => setFormData({...formData, time: e.target.value})}
                      style={styles.radioInput}
                    />
                    <span style={styles.radioLabel}>{time.label}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {formData.time === 'custom' && (
            <div style={styles.formGroup}>
              <label style={styles.label}>Custom time</label>
              <input
                type="time"
                value={formData.custom_time}
                onChange={(e) => setFormData({...formData, custom_time: e.target.value})}
                style={styles.input}
              />
            </div>
          )}

          <div style={styles.stepNavigation}>
            <button type="button" onClick={onBack} style={styles.secondaryButton}>
              Back
            </button>
            <button 
              type="submit" 
              style={{
                ...styles.primaryButton,
                opacity: loading || !formData.frequency || (formData.frequency !== 'on_demand' && !formData.time) ? 0.6 : 1
              }}
              disabled={loading || !formData.frequency || (formData.frequency !== 'on_demand' && !formData.time)}
            >
              {loading ? 'Saving...' : 'Next'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Step 7: Summary
const SummaryStep = ({ onNext, onBack, loading, data }) => {
  const [privacyAccepted, setPrivacyAccepted] = useState(false);

  const handleComplete = () => {
    if (privacyAccepted) {
      onNext({
        privacy_acknowledged: true,
        terms_accepted: true
      });
    }
  };

  return (
    <div style={styles.stepContainer}>
      <div style={styles.stepContent}>
        <h2 style={styles.stepTitle}>You're all set! 🎉</h2>
        <p style={styles.stepSubtitle}>Here's what I learned about you:</p>
        
        <div style={styles.summaryCard}>
          <div style={styles.summaryItem}>
            <span style={styles.summaryItemStrong}>Name:</span> {data.step_2?.display_name}
          </div>
          <div style={styles.summaryItem}>
            <span style={styles.summaryItemStrong}>Support style:</span> {data.step_4?.support_style?.replace('_', ' ')}
          </div>
          <div style={styles.summaryItem}>
            <span style={styles.summaryItemStrong}>Communication tone:</span> {data.step_4?.communication_tone}
          </div>
          <div style={styles.summaryItem}>
            <span style={styles.summaryItemStrong}>Focus areas:</span> {data.step_5?.selected_areas?.join(', ')}
          </div>
          <div style={styles.summaryItem}>
            <span style={styles.summaryItemStrong}>Check-ins:</span> {data.step_6?.frequency?.replace('_', ' ')}
          </div>
        </div>

        <div style={styles.privacySection}>
          <label style={styles.checkboxOption}>
            <input
              type="checkbox"
              checked={privacyAccepted}
              onChange={(e) => setPrivacyAccepted(e.target.checked)}
              style={styles.checkboxInput}
            />
            <span style={styles.checkboxLabel}>
              I understand that my data will be stored securely and used only to personalize my experience with Jumbo.
            </span>
          </label>
        </div>

        <div style={styles.completionMessage}>
          <p style={styles.completionText}>Thanks, {data.step_2?.display_name}! I'm all set to support you. 💛</p>
        </div>

        <div style={styles.stepNavigation}>
          <button type="button" onClick={onBack} style={styles.secondaryButton}>
            Edit
          </button>
          <button 
            onClick={handleComplete}
            style={{
              ...styles.primaryButton,
              opacity: loading || !privacyAccepted ? 0.6 : 1
            }}
            disabled={loading || !privacyAccepted}
          >
            <Sparkles size={20} style={{ marginRight: '8px' }} />
            {loading ? 'Completing...' : "Let's Begin! 🚀"}
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    // GradientBackground handles the container
  },
  content: {
    width: '100%',
    padding: '40px 24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
  },
  progressSection: {
    width: '100%',
    maxWidth: '600px',
    marginBottom: '30px',
  },
  progressBar: {
    width: '100%',
    height: '8px',
    background: 'rgba(255, 255, 255, 0.2)',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '10px',
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #8b5cf6, #a855f7)',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
  },
  progressText: {
    color: 'white',
    fontSize: '14px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  onboardingCard: {
    width: '100%',
    maxWidth: '600px',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
    overflow: 'hidden',
  },
  stepContainer: {
    padding: '40px',
    minHeight: '500px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  stepContent: {
    textAlign: 'center',
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
    animation: 'bounce 2s infinite',
  },
  welcomeTitle: {
    fontSize: '3rem',
    fontWeight: '700',
    color: 'white',
    marginBottom: '16px',
    textShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  welcomeSubtitle: {
    fontSize: '1.5rem',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '24px',
    fontWeight: '300',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  welcomeDescription: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6',
    marginBottom: '40px',
    maxWidth: '400px',
    margin: '0 auto 40px auto',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  stepTitle: {
    fontSize: '2rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  stepSubtitle: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '32px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  form: {
    textAlign: 'left',
    maxWidth: '500px',
    margin: '0 auto',
  },
  formGroup: {
    marginBottom: '24px',
  },
  label: {
    display: 'block',
    fontSize: '1.1rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '12px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  input: {
    width: '100%',
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
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
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
    boxSizing: 'border-box',
  },
  radioGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  radioOption: {
    display: 'flex',
    alignItems: 'center',
    padding: '15px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    background: 'rgba(255, 255, 255, 0.05)',
  },
  radioInput: {
    marginRight: '12px',
    transform: 'scale(1.2)',
  },
  radioLabel: {
    color: 'white',
    fontSize: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  primaryButton: {
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
    minWidth: '120px',
    justifyContent: 'center',
  },
  secondaryButton: {
    padding: '16px 32px',
    fontSize: '1rem',
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.8)',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '50px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    minWidth: '120px',
  },
  stepNavigation: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '32px',
    gap: '20px',
  },
  moodSelector: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '10px',
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
  },
  moodOptionSelected: {
    borderColor: '#8b5cf6',
    background: 'rgba(139, 92, 246, 0.2)',
    transform: 'translateY(-2px)',
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
  },
  encouragementText: {
    margin: 0,
    color: 'white',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  supportGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '15px',
    marginBottom: '30px',
  },
  supportOption: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '25px 15px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '16px',
    background: 'rgba(255, 255, 255, 0.05)',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textAlign: 'center',
  },
  supportOptionSelected: {
    borderColor: '#8b5cf6',
    background: 'rgba(139, 92, 246, 0.2)',
    transform: 'translateY(-2px)',
  },
  supportEmoji: {
    fontSize: '32px',
    marginBottom: '10px',
  },
  supportLabel: {
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    marginBottom: '5px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  supportDesc: {
    fontSize: '12px',
    color: 'rgba(255, 255, 255, 0.7)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  focusGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '15px',
    marginBottom: '20px',
  },
  focusOption: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px 15px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '16px',
    background: 'rgba(255, 255, 255, 0.05)',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  focusOptionSelected: {
    borderColor: '#8b5cf6',
    background: 'rgba(139, 92, 246, 0.2)',
    transform: 'translateY(-2px)',
  },
  focusOptionDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  focusEmoji: {
    fontSize: '28px',
    marginBottom: '8px',
  },
  focusLabel: {
    fontSize: '14px',
    fontWeight: '500',
    color: 'white',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  selectionCount: {
    textAlign: 'center',
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '14px',
    marginBottom: '20px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  summaryCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '25px',
    margin: '30px 0',
    textAlign: 'left',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  summaryItem: {
    marginBottom: '15px',
    fontSize: '16px',
    lineHeight: '1.5',
    color: 'rgba(255, 255, 255, 0.9)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  summaryItemStrong: {
    color: 'white',
    fontWeight: '600',
  },
  privacySection: {
    margin: '30px 0',
    textAlign: 'left',
  },
  checkboxOption: {
    display: 'flex',
    alignItems: 'flex-start',
    cursor: 'pointer',
  },
  checkboxInput: {
    marginRight: '12px',
    marginTop: '4px',
    transform: 'scale(1.2)',
  },
  checkboxLabel: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '14px',
    lineHeight: '1.5',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  completionMessage: {
    background: 'linear-gradient(135deg, #8b5cf6, #a855f7)',
    color: 'white',
    padding: '20px',
    borderRadius: '16px',
    margin: '30px 0',
  },
  completionText: {
    margin: 0,
    fontSize: '18px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
};

// Add CSS animations only (remove problematic media queries)
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-10px);
    }
    60% {
      transform: translateY(-5px);
    }
  }
`;
document.head.appendChild(styleSheet);

export default OnboardingFlow;