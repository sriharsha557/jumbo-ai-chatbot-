import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Sparkles, Send, Volume2, VolumeX } from 'lucide-react';
import { theme } from '../theme/theme';
import GradientBackground from './GradientBackground';

import { auth, db, supabase } from '../lib/supabase';

const API_URL = process.env.REACT_APP_API_URL || (() => {
  if (process.env.NODE_ENV === 'production') {
    console.error('❌ REACT_APP_API_URL not set in production! Check Vercel environment variables.');
    throw new Error('API_URL not configured for production');
  }
  console.warn('⚠️ Using localhost fallback for development');
  return 'http://localhost:5000/api/v1';
})();

function ChatPage({ currentUser }) {
  const [screenState, setScreenState] = useState('listening');
  const [isMicActive, setIsMicActive] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentResponse, setCurrentResponse] = useState('');
  const [metadata, setMetadata] = useState({});
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [textInput, setTextInput] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [isSpeechEnabled, setIsSpeechEnabled] = useState(true);

  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const isListeningRef = useRef(false);
  const silenceTimerRef = useRef(null);
  const finalTranscriptRef = useRef('');

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

      // Debug logging
      console.log('🔍 Sending chat request:', {
        url: `${API_URL}/chat/message`,
        headers,
        body: {
          message,
          conversation_context: conversationHistory,
          user: currentUser
        }
      });

      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message,
          conversation_context: conversationHistory,
          user: currentUser // Fallback user data
        })
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

  const speakResponse = (text) => {
    if (!isSpeechEnabled) {
      setScreenState('listening');
      return;
    }
    
    setScreenState('responding');
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onend = () => {
      setScreenState('listening');
    };

    synthRef.current.speak(utterance);
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
            <p style={styles.responseText}>{currentResponse}</p>
            {metadata.mood && (
              <p style={styles.moodLabel}>Mood: {metadata.mood}</p>
            )}
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
                ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                : `linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[500]} 100%)`,
            }}
          >
            {isMicActive ? <MicOff size={32} /> : <Mic size={32} />}
          </button>
          
          <button
            onClick={() => setIsSpeechEnabled(!isSpeechEnabled)}
            style={{
              ...styles.speechToggleButton,
              background: isSpeechEnabled
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
            }}
            title={isSpeechEnabled ? 'Disable text-to-speech' : 'Enable text-to-speech'}
          >
            {isSpeechEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
          </button>
        </div>

        <p style={styles.micStatus}>
          {!isSpeechSupported ? 'Speech recognition not supported' :
            isMicActive ? 'Click to stop' : 'Click to start'} • 
          Speech: {isSpeechEnabled ? 'ON' : 'OFF'}
        </p>

        <div style={styles.textInputSection}>
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
            placeholder="Or type your message..."
            style={styles.textInput}
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
  responseText: {
    color: '#1e40af', // Blue color for better visibility
    lineHeight: '1.625',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
    margin: 0,
    fontSize: '16px',
    fontWeight: '500',
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
    outline: 'none',
    transition: 'all 0.3s',
    boxSizing: 'border-box',
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