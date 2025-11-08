import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, Sparkles, Send, Volume2, VolumeX } from 'lucide-react';
import { theme } from '../theme/theme';
import GradientBackground from './GradientBackground';
import { jumboVoice, speakAsJumbo } from '../utils/jumboVoice';

import { supabase } from '../supabaseClient';

const API_URL = process.env.REACT_APP_API_URL || (() => {
  if (process.env.NODE_ENV === 'production') {
    console.error('❌ REACT_APP_API_URL not set in production! Check Vercel environment variables.');
    throw new Error('API_URL not configured for production');
  }
  console.warn('⚠️ Using localhost fallback for development');
  return 'http://localhost:5000/api/v1';
})();

function ChatPage({ currentUser, sessionMoodData }) {
  const [screenState, setScreenState] = useState('listening');
  const [isMicActive, setIsMicActive] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentResponse, setCurrentResponse] = useState('');
  const [metadata, setMetadata] = useState({});
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [textInput, setTextInput] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [isSpeechEnabled, setIsSpeechEnabled] = useState(() => {
    // Load saved preference from localStorage, default to false (disabled)
    const saved = localStorage.getItem('jumbo_speech_enabled');
    return saved !== null ? JSON.parse(saved) : false;
  });
  const [messageCount, setMessageCount] = useState(0);
  const [showFeedbackPrompt, setShowFeedbackPrompt] = useState(false);
  const [feedbackDismissed, setFeedbackDismissed] = useState(() => {
    return localStorage.getItem('jumbo_feedback_dismissed') === 'true';
  });

  // Google Form link for user feedback
  const FEEDBACK_FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSfxefcAGmvA7X2ROcdCDmwrobS1OJgmDQreav0C_BMlkHhrew/viewform?usp=sharing&ouid=103846069431803692273';

  const openFeedbackForm = () => {
    window.open(FEEDBACK_FORM_URL, '_blank');
  };

  const recognitionRef = useRef(null);
  const isListeningRef = useRef(false);
  const silenceTimerRef = useRef(null);
  const finalTranscriptRef = useRef('');

  // Save speech preference to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('jumbo_speech_enabled', JSON.stringify(isSpeechEnabled));
  }, [isSpeechEnabled]);

  // Initialize Jumbo's voice when component mounts
  useEffect(() => {
    // Log Jumbo voice information for debugging
    const voiceInfo = jumboVoice.getVoiceInfo();
    console.log('🐘 Jumbo Voice System:', voiceInfo);
    
    // Initialize voice if not already done
    if (!voiceInfo.isInitialized) {
      jumboVoice.initializeVoice();
    }
  }, []);

  // Load conversation history when component mounts
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (!currentUser) return;

      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (!session?.access_token) {
          console.warn('No session token available for loading conversation history');
          return;
        }

        const response = await fetch(`${API_URL}/chat/history?limit=20`, {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.conversations) {
            // Convert backend format to chat format
            const history = data.conversations.flatMap(conv => [
              { role: 'user', content: conv.message },
              { role: 'assistant', content: conv.response }
            ]);
            setConversationHistory(history);
            console.log('✅ Loaded conversation history:', history.length, 'messages');
          }
        } else {
          console.warn('Failed to load conversation history:', response.status);
        }
      } catch (error) {
        console.error('Error loading conversation history:', error);
      }
    };

    loadConversationHistory();
  }, [currentUser]);

  const handleSendMessage = useCallback(async (message) => {
    if (!message.trim() || !currentUser) return;

    try {
      // Get Supabase session for proper authentication
      const { data: { session } } = await supabase.auth.getSession();

      const headers = { 'Content-Type': 'application/json' };

      // Add Authorization header if we have a session
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`;
      }

      // Prepare request body with mood context
      const requestBody = {
        message,
        conversation_context: conversationHistory,
        user: currentUser,
        // Include mood data for context-aware responses
        mood_context: sessionMoodData ? {
          current_mood: sessionMoodData.mood_type,
          mood_timestamp: sessionMoodData.timestamp,
          session_id: sessionMoodData.session_id
        } : null
      };

      // Debug logging
      console.log('🔍 Sending chat request:', {
        url: `${API_URL}/chat/message`,
        headers,
        body: requestBody,
        mood_context: requestBody.mood_context ? 'included' : 'none'
      });

      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Chat API Error:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();

      if (data.success) {
        setCurrentResponse(data.response);
        setMetadata(data.metadata || {});

        setConversationHistory(prev => [
          ...prev,
          { role: 'user', content: message },
          { role: 'assistant', content: data.response }
        ]);

        // Increment message count and check for feedback prompt
        const newCount = messageCount + 1;
        setMessageCount(newCount);
        
        // Show feedback prompt after 5-6 exchanges (10-12 messages total)
        if (newCount >= 10 && !feedbackDismissed && !showFeedbackPrompt) {
          setShowFeedbackPrompt(true);
        }

        speakResponse(data.response);
      } else {
        setCurrentResponse(`Error: ${data.message}`);
      }
    } catch (error) {
      setCurrentResponse(`Connection error: ${error.message}`);
    } finally {
      setTranscript('');
      setScreenState('listening');
    }
  }, [currentUser, conversationHistory]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setIsSpeechSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    const langMap = { 'te': 'te-IN', 'hi': 'hi-IN', 'en': 'en-IN' };
    recognition.lang = langMap[currentUser?.language || 'en'] || 'en-IN';

    let finalTranscript = '';

    recognition.onstart = () => {
      finalTranscript = '';
      finalTranscriptRef.current = '';
      isListeningRef.current = true;
      setIsMicActive(true);
      setScreenState('listening');
      setTranscript('Listening... speak now!');
      console.log('🎤 Speech recognition started');
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
          finalTranscriptRef.current = finalTranscript;
        } else {
          interimTranscript += transcript;
        }
      }

      const displayText = finalTranscript + (interimTranscript ? `[${interimTranscript}]` : '');
      setTranscript(displayText || 'Listening...');
      console.log('🗣️ Speech detected:', displayText);

      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

      if (finalTranscript.trim()) {
        silenceTimerRef.current = setTimeout(() => {
          recognition.stop();
        }, 2000);
      }
    };

    recognition.onend = () => {
      isListeningRef.current = false;
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      setIsMicActive(false);

      const transcriptFinal = finalTranscriptRef.current.trim();
      if (transcriptFinal) {
        setScreenState('responding');
        handleSendMessage(transcriptFinal);
        finalTranscriptRef.current = '';
      } else {
        setScreenState('listening');
        setCurrentResponse('No speech detected. Please try again.');
      }
    };

    recognition.onerror = (event) => {
      isListeningRef.current = false;
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      setIsMicActive(false);
      setScreenState('listening');

      const errorMessages = {
        'not-allowed': 'Microphone access denied.',
        'no-speech': 'No speech detected. Speak clearly.',
        'audio-capture': 'No microphone found.',
        'network': 'Network error. Check internet.',
        'service-not-allowed': 'Speech service not available.'
      };

      setCurrentResponse(errorMessages[event.error] || `Speech error: ${event.error}`);
    };

    recognitionRef.current = recognition;
    setIsSpeechSupported(true);

    return () => {
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, [currentUser, handleSendMessage]);

  const speakResponse = async (text) => {
    console.log('🔊 Speech enabled:', isSpeechEnabled);
    console.log('🎧 Audio devices check - please ensure headphones are set as default audio device');
    
    // Always set screen state back to listening if speech is disabled
    if (!isSpeechEnabled) {
      console.log('🔇 Speech disabled - showing text only');
      setScreenState('listening');
      return;
    }
    
    // Check if Jumbo's voice is available
    if (!jumboVoice.isAvailable()) {
      console.warn('⚠️ Jumbo voice not available');
      setScreenState('listening');
      return;
    }

    try {
      console.log('🐘 Preparing to speak response:', text.substring(0, 50) + '...');
      console.log('🎵 Speech synthesis info:', jumboVoice.getVoiceInfo());
      
      setScreenState('responding');
      
      // Use Jumbo's gentle voice to speak the response
      await speakAsJumbo(text, {
        volume: 1.0, // Maximum volume for better headphone output
        onStart: () => {
          console.log('🐘 Jumbo begins speaking with gentle voice');
          console.log('🎧 If you can\'t hear audio, check your system\'s default audio device');
        },
        onEnd: () => {
          console.log('🐘 Jumbo finished speaking');
          setScreenState('listening');
        },
        onError: (event) => {
          console.error('❌ Jumbo speech synthesis error:', event);
          console.log('🎧 Speech error - this might be due to audio device routing');
          setScreenState('listening');
        }
      });

    } catch (error) {
      console.error('❌ Error in Jumbo speech synthesis:', error);
      setScreenState('listening');
    }
  };

  const toggleMic = () => {
    if (!recognitionRef.current || !isSpeechSupported) return;

    if (isMicActive) {
      recognitionRef.current.stop();
    } else {
      try {
        finalTranscriptRef.current = '';
        recognitionRef.current.start();
      } catch (error) {
        if (error.name === 'InvalidStateError') {
          recognitionRef.current.abort();
          setTimeout(() => {
            try {
              recognitionRef.current.start();
            } catch (e) {
              console.error('Failed to start microphone:', e);
            }
          }, 500);
        }
      }
    }
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      setScreenState('responding');
      handleSendMessage(textInput.trim());
      setTextInput('');
    }
  };

  return (
    <GradientBackground variant="copilot" animated={true} hasNavigation={true} style={styles.container}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
        @keyframes ping {
          75%, 100% { transform: scale(2); opacity: 0; }
        }
        @keyframes speechDisabled {
          0%, 100% { opacity: 0.8; }
          50% { opacity: 0.5; }
        }
        @keyframes volumeLevel {
          0%, 100% { 
            height: 4px; 
            opacity: 0.6; 
          }
          50% { 
            height: 12px; 
            opacity: 1; 
          }
        }
        .volume-bar {
          animation: volumeLevel 0.8s ease-in-out infinite;
        }
        .text-input::placeholder {
          color: rgba(30, 64, 175, 0.6) !important;
        }
        .text-input:focus {
          border-color: rgba(30, 64, 175, 0.6) !important;
          box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.2) !important;
        }
      `}</style>

      <div style={styles.content}>
        <div style={styles.header}>
          <div style={styles.headerIcon}>
            <Sparkles color="#a855f7" size={24} />
            <h2 style={styles.headerTitle}>
              {screenState === 'responding' ? "Jumbo's Response" : 'Talk with Jumbo'}
            </h2>
          </div>
          <p style={styles.headerSubtitle}>
            {isMicActive ? 'Listening... speak now!' : 'Click the microphone and share your thoughts'}
          </p>
          {sessionMoodData && (
            <div style={styles.moodIndicator}>
              <span style={styles.moodEmoji}>
                {sessionMoodData.mood_type === 'very_happy' ? '😀' :
                 sessionMoodData.mood_type === 'happy' ? '🙂' :
                 sessionMoodData.mood_type === 'neutral' ? '😐' :
                 sessionMoodData.mood_type === 'sad' ? '🙁' : '😢'}
              </span>
              <span style={styles.moodText}>
                Current mood: {sessionMoodData.mood_type.replace('_', ' ')}
              </span>
            </div>
          )}
        </div>

        <div style={styles.avatarSection}>
          <div style={{
            ...styles.avatar,
            transform: isMicActive ? 'scale(1.05)' : 'scale(1)',
            transition: 'transform 0.3s',
          }}>
            <div style={styles.avatarInner}>
              {isMicActive ? (
                <img src="/jumbo-animated.gif" alt="Listening" style={{ width: '80px', height: '80px', borderRadius: '50%' }} />
              ) : screenState === 'responding' ? (
                <img src="/jumbo-animated.gif" alt="Speaking" style={{ width: '80px', height: '80px', borderRadius: '50%' }} />
              ) : (
                <img src="/jumbo-logo.png" alt="Jumbo" style={{ width: '80px', height: '80px', borderRadius: '50%' }} />
              )}
            </div>
            {isMicActive && (
              <div style={{
                ...styles.ping,
                animation: 'ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite'
              }} />
            )}
          </div>
        </div>

        {currentResponse && (
          <div style={{ ...styles.responseBox, animation: 'fadeIn 0.5s' }}>
            <div style={styles.responseHeader}>
              <p style={styles.responseText}>{currentResponse}</p>
              {screenState === 'responding' && isSpeechEnabled && (
                <div style={styles.speakingIndicator}>
                  🔊 Speaking...
                </div>
              )}
            </div>
            {metadata.mood && (
              <p style={styles.moodLabel}>Mood: {metadata.mood}</p>
            )}
          </div>
        )}

        {/* Feedback Prompt */}
        {showFeedbackPrompt && (
          <div style={styles.feedbackPrompt}>
            <p style={styles.feedbackText}>
              🧡 Thanks for chatting with Jumbo! We'd love to hear how your experience has been so far.
            </p>
            <div style={styles.feedbackActions}>
              <button 
                onClick={openFeedbackForm}
                style={styles.feedbackButton}
              >
                Give Feedback
              </button>
              <button 
                onClick={() => {
                  setShowFeedbackPrompt(false);
                  setFeedbackDismissed(true);
                  localStorage.setItem('jumbo_feedback_dismissed', 'true');
                }}
                style={styles.dismissButton}
              >
                Maybe Later
              </button>
            </div>
          </div>
        )}

        {transcript && (
          <div style={styles.transcriptBox}>
            <p style={styles.transcriptText}>{transcript}</p>
          </div>
        )}

        <div style={styles.micButtonSection}>
          <button
            onClick={toggleMic}
            disabled={!isSpeechSupported}
            style={{
              ...styles.micButton,
              transform: isMicActive ? 'scale(1.1)' : 'scale(1)',
              transition: 'all 0.3s',
              opacity: !isSpeechSupported ? 0.5 : 1,
              cursor: !isSpeechSupported ? 'not-allowed' : 'pointer',
              background: isMicActive
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
              boxShadow: isMicActive 
                ? '0 0 20px rgba(16, 185, 129, 0.4), 0 25px 50px -12px rgba(0, 0, 0, 0.25)'
                : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            }}
          >
            <div style={styles.micIconContainer}>
              <Mic size={32} />
              {isMicActive && (
                <div style={styles.volumeLevels}>
                  <div style={{...styles.volumeBar, animationDelay: '0s'}} className="volume-bar"></div>
                  <div style={{...styles.volumeBar, animationDelay: '0.1s'}} className="volume-bar"></div>
                  <div style={{...styles.volumeBar, animationDelay: '0.2s'}} className="volume-bar"></div>
                </div>
              )}
            </div>
          </button>
          
          <button
            onClick={() => {
              const newState = !isSpeechEnabled;
              setIsSpeechEnabled(newState);
              console.log('🐘 Jumbo speech toggle:', newState ? 'enabled' : 'disabled');
              
              // Stop any current speech when disabling
              if (!newState) {
                jumboVoice.stop();
                setScreenState('listening');
              }
            }}
            style={{
              ...styles.speechToggleButton,
              background: isSpeechEnabled
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              transform: isSpeechEnabled ? 'scale(1)' : 'scale(0.95)',
              opacity: isSpeechEnabled ? 1 : 0.8,
            }}
            title={isSpeechEnabled ? 'Click to disable speech output' : 'Click to enable speech output'}
            aria-label={isSpeechEnabled ? 'Disable speech output' : 'Enable speech output'}
            aria-pressed={isSpeechEnabled}
          >
            {isSpeechEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
          </button>
        </div>

        <p style={styles.micStatus}>
          {!isSpeechSupported ? 'Speech recognition not supported' :
            isMicActive ? '🎤 Listening... Speak now!' : 'Click microphone to speak'} • 
          Audio: {isSpeechEnabled ? '🔊 ON' : '🔇 OFF'}
          {/iPad|iPhone|iPod/.test(navigator.userAgent) && (
            <span style={{ display: 'block', fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
              🍎 iOS: Tap screen first to enable audio
            </span>
          )}
        </p>


        <div style={styles.textInputSection}>
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
            placeholder="Or type your message..."
            style={styles.textInput}
            className="text-input"
          />
          <button
            onClick={handleTextSubmit}
            disabled={!textInput.trim()}
            style={{
              ...styles.sendButton,
              opacity: !textInput.trim() ? 0.5 : 1,
              cursor: !textInput.trim() ? 'not-allowed' : 'pointer',
            }}
          >
            <Send size={20} />
          </button>
        </div>

        {/* Footer Feedback Link */}
        {!showFeedbackPrompt && !feedbackDismissed && (
          <div style={styles.feedbackFooter}>
            Have feedback? 
            <button 
              onClick={openFeedbackForm}
              style={styles.feedbackFooterLink}
            >
              Share it here 💬
            </button>
          </div>
        )}
      </div>
    </GradientBackground>
  );
}

const styles = {
  container: {
    padding: '24px',
    // GradientBackground handles centering now
  },
  content: {
    width: '100%',
    maxWidth: '672px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    margin: '0 auto',
  },
  header: {
    textAlign: 'center',
    marginBottom: '32px',
    marginTop: '20px',
  },
  headerIcon: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '16px',
  },
  headerTitle: {
    fontSize: '24px',
    fontWeight: '400',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Briskey, sans-serif',
    color: 'white',
    margin: 0,
  },
  headerSubtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '14px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    margin: '8px 0 0 0',
  },
  moodIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginTop: '12px',
    padding: '8px 12px',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '20px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
  moodEmoji: {
    fontSize: '16px',
  },
  moodText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '12px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    textTransform: 'capitalize',
  },
  avatarSection: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '32px',
  },
  avatar: {
    position: 'relative',
    width: '280px',
    height: '280px',
    borderRadius: '50%',
    background: `linear-gradient(135deg, ${theme.colors.primary[500]} 0%, ${theme.colors.primary[600]} 100%)`,
    boxShadow: theme.shadows.xl,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarInner: {
    background: 'rgba(255, 255, 255, 0.9)',
    width: '100px',
    height: '100px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '48px',
  },
  ping: {
    position: 'absolute',
    inset: 0,
    borderRadius: '50%',
    border: '4px solid #22d3ee',
  },
  responseBox: {
    background: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(20px)',
    borderRadius: '24px',
    padding: '24px',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
    border: '2px solid rgba(30, 64, 175, 0.2)',
    marginBottom: '32px',
  },
  responseHeader: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  responseText: {
    color: '#1e40af', // Blue color for better visibility
    lineHeight: '1.625',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    margin: 0,
    fontSize: '16px',
    fontWeight: '500',
  },
  speakingIndicator: {
    fontSize: '12px',
    color: '#10b981',
    fontWeight: '600',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    alignSelf: 'flex-end',
    animation: 'pulse 1.5s infinite',
  },
  moodLabel: {
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '12px',
    margin: '12px 0 0 0',
  },
  transcriptBox: {
    background: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(10px)',
    borderRadius: '16px',
    padding: '16px',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    marginBottom: '24px',
    width: '100%',
  },
  transcriptText: {
    fontSize: '14px',
    color: 'rgba(30, 64, 175, 0.8)', // Dark blue for readability on light transcript background
    margin: 0,
  },
  micButtonSection: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '16px',
    marginBottom: '24px',
  },
  micButton: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    position: 'relative',
    overflow: 'visible',
  },
  micIconContainer: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  volumeLevels: {
    position: 'absolute',
    right: '-25px',
    top: '50%',
    transform: 'translateY(-50%)',
    display: 'flex',
    alignItems: 'end',
    gap: '2px',
    height: '16px',
  },
  volumeBar: {
    width: '3px',
    height: '4px',
    background: 'rgba(255, 255, 255, 0.8)',
    borderRadius: '2px',
    animation: 'volumeLevel 0.8s ease-in-out infinite',
  },
  speechToggleButton: {
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.2)',
    position: 'relative',
    overflow: 'hidden',
  },
  feedbackPrompt: {
    background: 'rgba(251, 146, 60, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    padding: '20px',
    border: '2px solid rgba(251, 146, 60, 0.3)',
    marginBottom: '24px',
    animation: 'fadeIn 0.5s ease',
  },
  feedbackText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '16px',
    lineHeight: '1.5',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  feedbackActions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
  },
  feedbackButton: {
    background: 'linear-gradient(135deg, #fb923c 0%, #f97316 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  dismissButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'rgba(255, 255, 255, 0.8)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  feedbackFooter: {
    textAlign: 'center',
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.6)',
    marginTop: '16px',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  feedbackFooterLink: {
    background: 'none',
    border: 'none',
    color: '#fb923c',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    marginLeft: '4px',
    textDecoration: 'underline',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  micStatus: {
    textAlign: 'center',
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '24px',
    margin: '0 0 24px 0',
  },
  textInputSection: {
    display: 'flex',
    gap: '8px',
    width: '100%',
    marginBottom: '24px',
  },
  textInput: {
    flex: 1,
    padding: '12px 16px',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '12px',
    fontSize: '14px',
    background: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(10px)',
    color: '#1e40af', // Blue text for visibility
    outline: 'none',
    transition: 'all 0.3s',
    boxSizing: 'border-box',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  sendButton: {
    padding: '12px 24px',
    background: `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    fontWeight: '600',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.3s',
  },
};

export default ChatPage;