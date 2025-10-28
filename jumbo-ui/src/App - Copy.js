import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, LogOut, Sparkles } from 'lucide-react';

const API_URL = 'http://localhost:5000/api';

function JumboVoiceChat() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [userName, setUserName] = useState('');
  const [userLanguage, setUserLanguage] = useState('en');
  const [existingUsers, setExistingUsers] = useState([]);
  const [screenState, setScreenState] = useState('listening');
  const [isMicActive, setIsMicActive] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentResponse, setCurrentResponse] = useState('');
  const [metadata, setMetadata] = useState({});
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [textInput, setTextInput] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [memories, setMemories] = useState({});
  const [debugLog, setDebugLog] = useState([]);

  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const isListeningRef = useRef(false);
  const silenceTimerRef = useRef(null);
  const finalTranscriptRef = useRef('');

  const addDebugLog = (message) => {
    console.log('DEBUG:', message);
    setDebugLog(prev => [...prev.slice(-9), `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const saveMemory = (key, value) => {
    setMemories(prev => ({
      ...prev,
      [key]: { value, timestamp: new Date().toISOString() }
    }));
  };

  const handleSendMessage = useCallback(async (message) => {
    if (!message.trim() || !currentUser) {
      addDebugLog('Cannot send: empty message or no user');
      return;
    }

    addDebugLog(`Sending: "${message}"`);

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message,
          conversation_context: conversationHistory 
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      addDebugLog(`Response received: ${data.success ? 'success' : 'error'}`);

      if (data.success) {
        setCurrentResponse(data.response);
        setMetadata(data.metadata || {});
        
        if (data.metadata?.detected_mood) {
          saveMemory('last_mood', data.metadata.detected_mood);
        }

        setConversationHistory(prev => [
          ...prev,
          { role: 'user', content: message },
          { role: 'assistant', content: data.response }
        ]);

        speakResponse(data.response);
      } else {
        setCurrentResponse(`Error: ${data.message}`);
        setMetadata({ mood: 'neutral' });
      }
    } catch (error) {
      addDebugLog(`Chat error: ${error.message}`);
      setCurrentResponse(`Connection error: ${error.message}`);
      setMetadata({ mood: 'neutral' });
    } finally {
      setTranscript('');
      setScreenState('listening');
    }
  }, [currentUser, conversationHistory]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSpeechSupported(false);
      addDebugLog('Speech recognition not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    
    const langMap = {
      'te': 'te-IN',
      'hi': 'hi-IN',
      'en': 'en-IN'
    };
    recognition.lang = langMap[userLanguage] || 'en-IN';

    let finalTranscript = '';

    recognition.onstart = () => {
      addDebugLog('✓ Listening started');
      finalTranscript = '';
      finalTranscriptRef.current = '';
      isListeningRef.current = true;
      setIsMicActive(true);
      setScreenState('listening');
      setTranscript('Listening... speak now!');
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        const confidence = event.results[i][0].confidence;

        addDebugLog(`Speech: "${transcript}" (confidence: ${(confidence * 100).toFixed(0)}%, final: ${event.results[i].isFinal})`);

        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
          finalTranscriptRef.current = finalTranscript;
        } else {
          interimTranscript += transcript;
        }
      }

      const displayText = finalTranscript + (interimTranscript ? `[${interimTranscript}]` : '');
      setTranscript(displayText || 'Listening...');

      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }

      if (finalTranscript.trim()) {
        silenceTimerRef.current = setTimeout(() => {
          addDebugLog('Silence detected - stopping recognition');
          recognition.stop();
        }, 2000);
      }
    };

    recognition.onspeechend = () => {
      addDebugLog('Speech ended');
    };

    recognition.onend = () => {
      addDebugLog('✓ Listening ended');
      isListeningRef.current = false;

      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }

      setIsMicActive(false);

      const transcriptFinal = finalTranscriptRef.current.trim();
      if (transcriptFinal) {
        addDebugLog(`✓ Processing: "${transcriptFinal}"`);
        setScreenState('responding');
        handleSendMessage(transcriptFinal);
        finalTranscriptRef.current = '';
      } else {
        addDebugLog('No speech detected');
        setScreenState('listening');
        setCurrentResponse('No speech detected. Please try again and speak clearly.');
      }
    };

    recognition.onerror = (event) => {
      addDebugLog(`✗ Error: ${event.error}`);
      isListeningRef.current = false;

      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
      }

      setIsMicActive(false);
      setScreenState('listening');

      const errorMessages = {
        'not-allowed': 'Microphone access denied. Click the mic icon in address bar and allow access.',
        'no-speech': 'No speech detected. Speak clearly right after clicking the mic button.',
        'audio-capture': 'No microphone found. Check your device.',
        'network': 'Network error. Speech recognition needs internet.',
        'service-not-allowed': 'Speech service not available.'
      };

      setCurrentResponse(errorMessages[event.error] || `Speech error: ${event.error}`);
    };

    recognitionRef.current = recognition;
    setIsSpeechSupported(true);

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [userLanguage, handleSendMessage]);

  useEffect(() => {
    fetchCurrentUser();
    fetchExistingUsers();
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch(`${API_URL}/users/current`);
      const data = await response.json();
      if (data.success && data.user) {
        setCurrentUser(data.user);
        addDebugLog(`User loaded: ${data.user.name}`);
      }
    } catch (error) {
      addDebugLog(`Error fetching user: ${error.message}`);
    }
  };

  const fetchExistingUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/users/list`);
      const data = await response.json();
      if (data.success) {
        setExistingUsers(data.users);
      }
    } catch (error) {
      addDebugLog(`Error fetching users: ${error.message}`);
    }
  };

  const loginUser = async (name) => {
    setIsAuthenticating(true);
    try {
      const response = await fetch(`${API_URL}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      const data = await response.json();
      if (data.success) {
        setCurrentUser(data.user);
        setUserName('');
        setConversationHistory([]);
        addDebugLog(`Logged in: ${name}`);
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Login failed');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const registerUser = async () => {
    if (!userName.trim()) {
      alert('Please enter a name');
      return;
    }

    setIsAuthenticating(true);
    try {
      const response = await fetch(`${API_URL}/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: userName, language: userLanguage })
      });
      const data = await response.json();
      if (data.success) {
        setCurrentUser(data.user);
        setUserName('');
        setConversationHistory([]);
        fetchExistingUsers();
        addDebugLog(`Registered: ${userName}`);
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Registration failed');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const speakResponse = (text) => {
    setScreenState('responding');
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.lang = userLanguage === 'te' ? 'te-IN' : userLanguage === 'hi' ? 'hi-IN' : 'en-IN';

    utterance.onend = () => {
      setScreenState('listening');
    };

    synthRef.current.speak(utterance);
  };

  const toggleMic = () => {
    if (!recognitionRef.current || !currentUser || !isSpeechSupported) return;

    if (isMicActive) {
      addDebugLog('Stopping microphone');
      recognitionRef.current.stop();
    } else {
      try {
        addDebugLog('Starting microphone...');
        setTranscript('Starting... Please wait...');
        finalTranscriptRef.current = '';
        recognitionRef.current.start();
      } catch (error) {
        addDebugLog(`Error starting: ${error.message}`);
        if (error.name === 'InvalidStateError') {
          recognitionRef.current.abort();
          setTimeout(() => {
            try {
              recognitionRef.current.start();
            } catch (e) {
              alert('Failed to start microphone');
            }
          }, 500);
        }
      }
    }
  };

  const logout = () => {
    setCurrentUser(null);
    setTranscript('');
    setCurrentResponse('');
    setConversationHistory([]);
    setMemories({});
    addDebugLog('Logged out');
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      addDebugLog(`Sending text: "${textInput}"`);
      setScreenState('responding');
      handleSendMessage(textInput.trim());
      setTextInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleTextSubmit();
    }
  };

  if (!currentUser) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 50%, #fce7f3 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '448px',
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
          borderRadius: '24px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          padding: '32px',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{
              width: '80px',
              height: '80px',
              margin: '0 auto 16px',
              background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '40px'
            }}>
              🐘
            </div>
            <h1 style={{
              fontSize: '36px',
              fontWeight: 'bold',
              background: 'linear-gradient(to right, #9333ea, #ec4899)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              marginBottom: '8px'
            }}>
              JUMBO
            </h1>
            <p style={{ color: '#6b7280' }}>Your Emotional Support Companion</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {existingUsers.length > 0 && (
              <>
                <p style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Select User:</p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                  {existingUsers.map(user => (
                    <button
                      key={user}
                      onClick={() => loginUser(user)}
                      disabled={isAuthenticating}
                      style={{
                        padding: '8px 16px',
                        background: 'linear-gradient(to right, #f3e8ff, #fce7f3)',
                        color: '#7c3aed',
                        borderRadius: '12px',
                        border: 'none',
                        fontWeight: '500',
                        cursor: isAuthenticating ? 'not-allowed' : 'pointer',
                        opacity: isAuthenticating ? 0.5 : 1,
                      }}
                    >
                      {user}
                    </button>
                  ))}
                </div>
                <div style={{ borderTop: '1px solid #e5e7eb', margin: '16px 0' }}></div>
              </>
            )}

            <p style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>New User:</p>
            <input
              type="text"
              placeholder="Enter your name"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && registerUser()}
              disabled={isAuthenticating}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e9d5ff',
                borderRadius: '12px',
                outline: 'none',
                fontSize: '16px'
              }}
            />

            <select
              value={userLanguage}
              onChange={(e) => setUserLanguage(e.target.value)}
              disabled={isAuthenticating}
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid #e9d5ff',
                borderRadius: '12px',
                outline: 'none',
                fontSize: '16px'
              }}
            >
              <option value="en">English</option>
              <option value="te">Telugu</option>
              <option value="hi">Hindi</option>
            </select>

            <button
              onClick={registerUser}
              disabled={isAuthenticating || !userName.trim()}
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'linear-gradient(to right, #9333ea, #ec4899)',
                color: 'white',
                borderRadius: '12px',
                border: 'none',
                fontWeight: '600',
                cursor: isAuthenticating || !userName.trim() ? 'not-allowed' : 'pointer',
                opacity: isAuthenticating || !userName.trim() ? 0.5 : 1,
                fontSize: '16px'
              }}
            >
              {isAuthenticating ? 'Loading...' : 'Start Chatting'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 25%, #dbeafe 50%, #fce7f3 75%, #f5f3ff 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -20px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(20px, 20px) scale(1.05); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.05); opacity: 0.8; }
        }
        @keyframes ping {
          75%, 100% { transform: scale(2); opacity: 0; }
        }
      `}</style>

      <div style={{
        position: 'absolute',
        top: '24px',
        left: '24px',
        right: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        zIndex: 10
      }}>
        <h1 style={{
          fontSize: '24px',
          fontWeight: 'bold',
          background: 'linear-gradient(to right, #9333ea, #ec4899)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          JUMBO
        </h1>
        <div style={{
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(12px)',
          padding: '8px 16px',
          borderRadius: '999px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>
            {currentUser.name}
          </span>
          <button
            onClick={logout}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: '#ef4444'
            }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

      <div style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: '672px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px', marginTop: '60px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Sparkles color="#a855f7" size={24} />
            <h2 style={{ fontSize: '24px', fontWeight: '300', color: '#374151' }}>
              {screenState === 'responding' ? "JUMBO's Response" : 'Talk with JUMBO'}
            </h2>
          </div>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>
            {isMicActive ? 'Listening... speak now!' : 'Click the microphone and share your thoughts'}
          </p>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
          <div style={{
            position: 'relative',
            width: '280px',
            height: '280px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: isMicActive ? 'scale(1.05)' : 'scale(1)',
            transition: 'transform 0.3s'
          }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.9)',
              width: '100px',
              height: '100px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '48px'
            }}>
              {isMicActive ? '🎤' : screenState === 'responding' ? '💭' : '🐘'}
            </div>
            {isMicActive && (
              <div style={{
                position: 'absolute',
                inset: 0,
                borderRadius: '50%',
                border: '4px solid #22d3ee',
                animation: 'ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite'
              }}></div>
            )}
          </div>
        </div>

        {currentResponse && (
          <div style={{ marginBottom: '32px', animation: 'fadeIn 0.5s' }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.8)',
              backdropFilter: 'blur(20px)',
              borderRadius: '24px',
              padding: '24px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <p style={{ color: '#374151', lineHeight: '1.625' }}>{currentResponse}</p>
              {metadata.mood && (
                <p style={{
                  fontSize: '12px',
                  color: '#6b7280',
                  marginTop: '12px'
                }}>
                  Mood: {metadata.mood}
                </p>
              )}
            </div>
          </div>
        )}

        {transcript && (
          <div style={{ marginBottom: '24px' }}>
            <div style={{
              background: isMicActive ? 'rgba(239, 68, 68, 0.1)' : 'rgba(243, 232, 255, 0.8)',
              borderRadius: '16px',
              padding: '16px',
              border: '2px solid ' + (isMicActive ? 'rgba(239, 68, 68, 0.5)' : 'rgba(233, 213, 255, 0.5)')
            }}>
              <p style={{ fontSize: '14px', color: '#581c87' }}>
                {transcript}
              </p>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
          <button
            onClick={toggleMic}
            disabled={!isSpeechSupported}
            style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              background: isMicActive ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 'linear-gradient(135deg, #9333ea 0%, #ec4899 100%)',
              border: 'none',
              cursor: !isSpeechSupported ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              transform: isMicActive ? 'scale(1.1)' : 'scale(1)',
              transition: 'all 0.3s',
              opacity: !isSpeechSupported ? 0.5 : 1
            }}
          >
            {isMicActive ? <MicOff size={32} /> : <Mic size={32} />}
          </button>
        </div>

        <p style={{ textAlign: 'center', fontSize: '14px', color: '#6b7280', marginBottom: '24px' }}>
          {!isSpeechSupported ? 'Speech recognition not supported' :
           isMicActive ? 'Click to stop' : 'Click to start'}
        </p>

        <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Or type your message..."
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '2px solid #e9d5ff',
              borderRadius: '12px',
              outline: 'none',
              fontSize: '14px',
              background: 'rgba(255, 255, 255, 0.8)'
            }}
          />
          <button
            onClick={handleTextSubmit}
            disabled={!textInput.trim()}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(135deg, #9333ea 0%, #ec4899 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontWeight: '600',
              cursor: !textInput.trim() ? 'not-allowed' : 'pointer',
              opacity: !textInput.trim() ? 0.5 : 1
            }}
          >
            Send
          </button>
        </div>

        <details style={{ marginTop: '24px', fontSize: '12px', color: '#6b7280' }}>
          <summary style={{ cursor: 'pointer', fontWeight: '600', marginBottom: '8px' }}>Debug Log</summary>
          <div style={{
            background: 'rgba(0, 0, 0, 0.05)',
            borderRadius: '8px',
            padding: '12px',
            maxHeight: '200px',
            overflow: 'auto',
            fontFamily: 'monospace'
          }}>
            {debugLog.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        </details>
      </div>
    </div>
  );
}

export default JumboVoiceChat;