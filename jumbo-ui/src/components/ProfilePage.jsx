import React, { useState, useEffect } from 'react';
import { User, Edit3, Save, X, Settings } from 'lucide-react';
import GradientBackground from './GradientBackground';
import { theme } from '../theme/theme';

function ProfilePage({ currentUser }) {
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({});
  const [editedData, setEditedData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = () => {
    try {
      // Load user data
      const userData = localStorage.getItem('jumbo_user');
      const onboardingData = localStorage.getItem('jumbo_onboarding_data');
      
      const user = userData ? JSON.parse(userData) : {};
      const onboarding = onboardingData ? JSON.parse(onboardingData) : {};
      
      const profile = {
        // Basic info
        name: user.name || 'User',
        email: user.email || '',
        
        // Onboarding preferences
        display_name: onboarding.step_2?.display_name || '',
        pronouns: onboarding.step_2?.pronouns || '',
        preferred_language: onboarding.step_2?.preferred_language || 'en',
        
        current_mood: onboarding.step_3?.current_mood || 3,
        emotion_comfort_level: onboarding.step_3?.emotion_comfort_level || '',
        
        support_style: onboarding.step_4?.support_style || '',
        communication_tone: onboarding.step_4?.communication_tone || '',
        
        focus_areas: onboarding.step_5?.selected_areas || [],
        
        checkin_frequency: onboarding.step_6?.frequency || '',
        checkin_time: onboarding.step_6?.time || '',
        custom_checkin_time: onboarding.step_6?.custom_time || '',
        
        // Metadata
        onboarding_completed: localStorage.getItem('jumbo_onboarding_completed') === 'true',
        completed_at: onboarding.completed_at || null
      };
      
      setProfileData(profile);
      setEditedData(profile);
    } catch (error) {
      console.error('Error loading profile data:', error);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditedData({ ...profileData });
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedData({ ...profileData });
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      // Update localStorage with new data
      const userData = JSON.parse(localStorage.getItem('jumbo_user') || '{}');
      const onboardingData = JSON.parse(localStorage.getItem('jumbo_onboarding_data') || '{}');
      
      // Update user data
      userData.name = editedData.display_name || editedData.name;
      
      // Update onboarding data
      if (onboardingData.step_2) {
        onboardingData.step_2.display_name = editedData.display_name;
        onboardingData.step_2.pronouns = editedData.pronouns;
        onboardingData.step_2.preferred_language = editedData.preferred_language;
      }
      
      if (onboardingData.step_3) {
        onboardingData.step_3.current_mood = editedData.current_mood;
        onboardingData.step_3.emotion_comfort_level = editedData.emotion_comfort_level;
      }
      
      if (onboardingData.step_4) {
        onboardingData.step_4.support_style = editedData.support_style;
        onboardingData.step_4.communication_tone = editedData.communication_tone;
      }
      
      if (onboardingData.step_5) {
        onboardingData.step_5.selected_areas = editedData.focus_areas;
      }
      
      if (onboardingData.step_6) {
        onboardingData.step_6.frequency = editedData.checkin_frequency;
        onboardingData.step_6.time = editedData.checkin_time;
        onboardingData.step_6.custom_time = editedData.custom_checkin_time;
      }
      
      // Save to localStorage
      localStorage.setItem('jumbo_user', JSON.stringify(userData));
      localStorage.setItem('jumbo_onboarding_data', JSON.stringify(onboardingData));
      
      // Update state
      setProfileData(editedData);
      setIsEditing(false);
      
      console.log('Profile updated successfully');
    } catch (error) {
      console.error('Error saving profile:', error);
    }
    setLoading(false);
  };

  const handleInputChange = (field, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayChange = (field, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: Array.isArray(value) ? value : [value]
    }));
  };

  const moodLabels = ['Very Low', 'Low', 'Neutral', 'Good', 'Great'];
  const moodEmojis = ['😞', '😕', '😐', '🙂', '😄'];

  return (
    <GradientBackground variant="copilot" animated={true} style={styles.container}>
      <style>{`
        .checkbox-label:hover {
          background: rgba(255, 255, 255, 0.1) !important;
        }
        .checkbox-group::-webkit-scrollbar {
          width: 6px;
        }
        .checkbox-group::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }
        .checkbox-group::-webkit-scrollbar-thumb {
          background: rgba(139, 92, 246, 0.5);
          border-radius: 3px;
        }
        .checkbox-group::-webkit-scrollbar-thumb:hover {
          background: rgba(139, 92, 246, 0.7);
        }
        /* Fix dropdown option colors */
        select option {
          background: #1e293b !important;
          color: white !important;
        }
        select {
          color: white !important;
        }
        /* Ensure select text is visible */
        .profile-select {
          color: white !important;
          background: rgba(255, 255, 255, 0.1) !important;
        }
        .profile-select option {
          background: #1e293b !important;
          color: white !important;
        }
      `}</style>
      <div style={styles.content}>
        <div style={styles.profileCard}>
          {/* Header */}
          <div style={styles.header}>
            <div style={styles.headerLeft}>
              <div style={styles.avatarContainer}>
                <User size={32} color="white" />
              </div>
              <div>
                <h1 style={styles.title}>My Profile</h1>
                <p style={styles.subtitle}>Manage your preferences and settings</p>
              </div>
            </div>
            
            <div style={styles.headerRight}>
              {!isEditing ? (
                <button onClick={handleEdit} style={styles.editButton}>
                  <Edit3 size={18} />
                  <span>Edit Profile</span>
                </button>
              ) : (
                <div style={styles.editActions}>
                  <button onClick={handleCancel} style={styles.cancelButton}>
                    <X size={18} />
                    <span>Cancel</span>
                  </button>
                  <button 
                    onClick={handleSave} 
                    style={styles.saveButton}
                    disabled={loading}
                  >
                    <Save size={18} />
                    <span>{loading ? 'Saving...' : 'Save'}</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Profile Sections */}
          <div style={styles.sections}>
            
            {/* Basic Information */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>
                <User size={20} />
                Basic Information
              </h3>
              
              <div style={styles.fieldGrid}>
                <div style={styles.field}>
                  <label style={styles.label}>Display Name</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedData.display_name || ''}
                      onChange={(e) => handleInputChange('display_name', e.target.value)}
                      style={styles.input}
                      placeholder="Your preferred name"
                    />
                  ) : (
                    <div style={styles.value}>{profileData.display_name || 'Not set'}</div>
                  )}
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Email</label>
                  <div style={styles.value}>{profileData.email}</div>
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Pronouns</label>
                  {isEditing ? (
                    <select
                      value={editedData.pronouns || ''}
                      onChange={(e) => handleInputChange('pronouns', e.target.value)}
                      style={styles.select}
                      className="profile-select"
                    >
                      <option value="">Select pronouns</option>
                      <option value="he/him">He/Him</option>
                      <option value="she/her">She/Her</option>
                      <option value="they/them">They/Them</option>
                      <option value="prefer_not_to_say">Prefer not to say</option>
                    </select>
                  ) : (
                    <div style={styles.value}>{profileData.pronouns || 'Not set'}</div>
                  )}
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Preferred Language</label>
                  {isEditing ? (
                    <select
                      value={editedData.preferred_language || 'en'}
                      onChange={(e) => handleInputChange('preferred_language', e.target.value)}
                      style={styles.select}
                      className="profile-select"
                    >
                      <option value="en">English</option>
                      <option value="hi">Hindi</option>
                      <option value="other">Other</option>
                    </select>
                  ) : (
                    <div style={styles.value}>
                      {profileData.preferred_language === 'en' ? 'English' : 
                       profileData.preferred_language === 'hi' ? 'Hindi' : 'Other'}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Emotional Preferences */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>
                <Settings size={20} />
                Emotional Preferences
              </h3>
              
              <div style={styles.fieldGrid}>
                <div style={styles.field}>
                  <label style={styles.label}>Current Mood</label>
                  {isEditing ? (
                    <div style={styles.moodSelector}>
                      {moodEmojis.map((emoji, index) => (
                        <button
                          key={index}
                          type="button"
                          style={{
                            ...styles.moodOption,
                            ...(editedData.current_mood === index + 1 ? styles.moodOptionSelected : {})
                          }}
                          onClick={() => handleInputChange('current_mood', index + 1)}
                        >
                          <span style={styles.moodEmoji}>{emoji}</span>
                          <span style={styles.moodLabel}>{moodLabels[index]}</span>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div style={styles.value}>
                      {profileData.current_mood ? 
                        `${moodEmojis[profileData.current_mood - 1]} ${moodLabels[profileData.current_mood - 1]}` : 
                        'Not set'
                      }
                    </div>
                  )}
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Comfort with Emotions</label>
                  {isEditing ? (
                    <select
                      value={editedData.emotion_comfort_level || ''}
                      onChange={(e) => handleInputChange('emotion_comfort_level', e.target.value)}
                      style={styles.select}
                    >
                      <option value="">Select comfort level</option>
                      <option value="easy">Yes, pretty easy</option>
                      <option value="sometimes">Sometimes</option>
                      <option value="difficult">Not really</option>
                    </select>
                  ) : (
                    <div style={styles.value}>
                      {profileData.emotion_comfort_level === 'easy' ? 'Yes, pretty easy' :
                       profileData.emotion_comfort_level === 'sometimes' ? 'Sometimes' :
                       profileData.emotion_comfort_level === 'difficult' ? 'Not really' : 'Not set'}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* AI Preferences */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>
                <Settings size={20} />
                AI Support Preferences
              </h3>
              
              <div style={styles.fieldGrid}>
                <div style={styles.field}>
                  <label style={styles.label}>Support Style</label>
                  {isEditing ? (
                    <select
                      value={editedData.support_style || ''}
                      onChange={(e) => handleInputChange('support_style', e.target.value)}
                      style={styles.select}
                    >
                      <option value="">Select support style</option>
                      <option value="calm_comforting">🧘 Calm & comforting</option>
                      <option value="honest_real">💬 Honest & real</option>
                      <option value="motivational">⚡ Motivational</option>
                      <option value="fun_distraction">🎧 Fun distraction</option>
                    </select>
                  ) : (
                    <div style={styles.value}>
                      {profileData.support_style ? 
                        profileData.support_style.replace('_', ' & ').replace(/\b\w/g, l => l.toUpperCase()) : 
                        'Not set'
                      }
                    </div>
                  )}
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Communication Tone</label>
                  {isEditing ? (
                    <select
                      value={editedData.communication_tone || ''}
                      onChange={(e) => handleInputChange('communication_tone', e.target.value)}
                      style={styles.select}
                    >
                      <option value="">Select tone</option>
                      <option value="calm">Calm</option>
                      <option value="cheerful">Cheerful</option>
                      <option value="deep">Deep</option>
                      <option value="friendly">Friendly</option>
                    </select>
                  ) : (
                    <div style={styles.value}>
                      {profileData.communication_tone ? 
                        profileData.communication_tone.charAt(0).toUpperCase() + profileData.communication_tone.slice(1) : 
                        'Not set'
                      }
                    </div>
                  )}
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Focus Areas</label>
                  {isEditing ? (
                    <div style={styles.checkboxGroup} className="checkbox-group">
                      {[
                        'Anxiety Management',
                        'Depression Support', 
                        'Stress Relief',
                        'Sleep Issues',
                        'Relationship Concerns',
                        'Work-Life Balance',
                        'Self-Esteem',
                        'Grief & Loss',
                        'Anger Management',
                        'Social Anxiety',
                        'General Mental Wellness'
                      ].map(area => (
                        <label key={area} style={styles.checkboxLabel} className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={editedData.focus_areas?.includes(area) || false}
                            onChange={(e) => {
                              const currentAreas = editedData.focus_areas || [];
                              if (e.target.checked) {
                                handleArrayChange('focus_areas', [...currentAreas, area]);
                              } else {
                                handleArrayChange('focus_areas', currentAreas.filter(a => a !== area));
                              }
                            }}
                            style={styles.checkbox}
                          />
                          <span style={styles.checkboxText}>{area}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div style={styles.value}>
                      {profileData.focus_areas && profileData.focus_areas.length > 0 ? 
                        profileData.focus_areas.join(', ') : 
                        'Not set'
                      }
                    </div>
                  )}
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Check-in Frequency</label>
                  {isEditing ? (
                    <select
                      value={editedData.checkin_frequency || ''}
                      onChange={(e) => handleInputChange('checkin_frequency', e.target.value)}
                      style={styles.select}
                      className="profile-select"
                    >
                      <option value="">Select frequency</option>
                      <option value="daily">Daily</option>
                      <option value="few_times_week">A few times a week</option>
                      <option value="on_demand">Only when I open the app</option>
                    </select>
                  ) : (
                    <div style={styles.value}>
                      {profileData.checkin_frequency ? 
                        profileData.checkin_frequency.replace('_', ' ') : 
                        'Not set'
                      }
                    </div>
                  )}
                </div>
                
                <div style={styles.field}>
                  <label style={styles.label}>Preferred Check-in Time</label>
                  {isEditing ? (
                    <div style={styles.timeSelection}>
                      <select
                        value={editedData.checkin_time || ''}
                        onChange={(e) => handleInputChange('checkin_time', e.target.value)}
                        style={styles.select}
                        className="profile-select"
                      >
                        <option value="">Select time preference</option>
                        <option value="morning">Morning (8:00 AM - 12:00 PM)</option>
                        <option value="afternoon">Afternoon (12:00 PM - 5:00 PM)</option>
                        <option value="evening">Evening (5:00 PM - 9:00 PM)</option>
                        <option value="custom">Custom Time</option>
                      </select>
                      
                      {editedData.checkin_time === 'custom' && (
                        <input
                          type="time"
                          value={editedData.custom_checkin_time || ''}
                          onChange={(e) => handleInputChange('custom_checkin_time', e.target.value)}
                          style={{...styles.input, marginTop: '8px'}}
                        />
                      )}
                    </div>
                  ) : (
                    <div style={styles.value}>
                      {profileData.checkin_time ? (
                        profileData.checkin_time === 'custom' ? 
                          `Custom: ${profileData.custom_checkin_time || 'Not set'}` :
                          profileData.checkin_time.charAt(0).toUpperCase() + profileData.checkin_time.slice(1)
                      ) : 'Not set'}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Account Status */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>
                <Settings size={20} />
                Account Status
              </h3>
              
              <div style={styles.statusGrid}>
                <div style={styles.statusItem}>
                  <span style={styles.statusLabel}>Onboarding Status:</span>
                  <span style={{
                    ...styles.statusValue,
                    color: profileData.onboarding_completed ? '#10b981' : '#f59e0b'
                  }}>
                    {profileData.onboarding_completed ? '✅ Completed' : '⏳ Pending'}
                  </span>
                </div>
                
                {profileData.completed_at && (
                  <div style={styles.statusItem}>
                    <span style={styles.statusLabel}>Completed On:</span>
                    <span style={styles.statusValue}>
                      {new Date(profileData.completed_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </GradientBackground>
  );
}

const styles = {
  container: {
    padding: '20px',
  },
  content: {
    width: '100%',
    maxWidth: '800px',
    margin: '0 auto',
  },
  profileCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '32px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  avatarContainer: {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #8b5cf6, #a855f7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: '2rem',
    fontWeight: '600',
    color: 'white',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  subtitle: {
    fontSize: '1rem',
    color: 'rgba(255, 255, 255, 0.7)',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  headerRight: {
    display: 'flex',
    gap: '12px',
  },
  editButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 20px',
    background: 'linear-gradient(135deg, #8b5cf6, #a855f7)',
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    transition: 'all 0.3s ease',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  editActions: {
    display: 'flex',
    gap: '8px',
  },
  cancelButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '10px 16px',
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'white',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  saveButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '10px 16px',
    background: 'linear-gradient(135deg, #10b981, #059669)',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  sections: {
    padding: '0 32px 32px 32px',
  },
  section: {
    marginBottom: '32px',
  },
  sectionTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '20px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  fieldGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.9)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  value: {
    fontSize: '16px',
    color: 'white',
    padding: '12px 0',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  input: {
    padding: '12px 16px',
    borderRadius: '10px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'white',
    fontSize: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    outline: 'none',
    transition: 'all 0.3s ease',
  },
  select: {
    padding: '12px 16px',
    borderRadius: '10px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'white',
    fontSize: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    outline: 'none',
    cursor: 'pointer',
  },
  moodSelector: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  moodOption: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '12px 8px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    background: 'rgba(255, 255, 255, 0.05)',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    minWidth: '60px',
  },
  moodOptionSelected: {
    borderColor: '#8b5cf6',
    background: 'rgba(139, 92, 246, 0.2)',
  },
  moodEmoji: {
    fontSize: '20px',
    marginBottom: '4px',
  },
  moodLabel: {
    fontSize: '10px',
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  statusGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  statusItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '10px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  },
  statusLabel: {
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.7)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  statusValue: {
    fontSize: '14px',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  checkboxGroup: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '8px',
    maxHeight: '200px',
    overflowY: 'auto',
    padding: '8px',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '10px',
    background: 'rgba(255, 255, 255, 0.05)',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    padding: '4px',
    borderRadius: '6px',
    transition: 'background 0.2s ease',
  },
  checkbox: {
    width: '16px',
    height: '16px',
    accentColor: '#8b5cf6',
  },
  checkboxText: {
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.9)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  timeSelection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
};

export default ProfilePage;