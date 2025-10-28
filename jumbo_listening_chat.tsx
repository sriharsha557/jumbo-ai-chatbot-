import React, { useState, useEffect, useRef } from 'react';
import { Heart, Cloud, Sprout, Mic, MicOff, LogOut, Settings } from 'lucide-react';

const API_URL = 'http://localhost:5000/api';

export default function JumboVoiceChat() {
  // Auth & User
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [userName, setUserName] = useState('');
  const [userLanguage, setUserLanguage] = useState('en');
  const [existingUsers, setExistingUsers] = useState([]);

  // Voice & UI State
  const [screenState, setScreenState] = useState('listening');
  const [isMicActive, setIsMicActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [soundIntensity, setSoundIntensity] = useState(0);
  const [particlePositions, setParticlePositions] = useState([]);
  const [transcript, setTranscript] = useState('');
  const [currentResponse, setCurrentResponse] = useState('');
  const [metadata, setMetadata] = useState({});
  const [conversations, setConversations] = useState([]);

  // Refs
  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = userLanguage === 'te' ? 'te-IN' : userLanguage === 'hi' ? 'hi-IN' : 'en-IN';

      recognition.onstart = () => {
        setIsMicActive(true);
        setScreenState('listening');
        setTranscript('');
        setSoundIntensity(0.8);
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const trans = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            setTranscript(prev => prev + trans + ' ');
          } else {
            interimTranscript += trans;
          }
          setSoundIntensity(event.results[i][0].confidence);
        }
      };

      recognition.onend = () => {
        setIsMicActive(false);
        if (transcript.trim()) {
          setScreenState('thinking');
          handleSendMessage(transcript);
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsMicActive(false);
      };

      recognitionRef.current = recognition;
    }
  }, [userLanguage, transcript]);

  // Initialize particles
  useEffect(() => {
    const particles = Array.from({ length: 5 }, (_, i) => ({
      id: i,
      x: Math.random() * 80 - 40,
      y: Math.random() * 60 - 30,
      duration: 3 + Math.random() * 2,
    }));
    setParticlePositions(particles);
  }, []);

  // Check current user on mount
  useEffect(() => {
    fetchCurrentUser();
    fetchExistingUsers();
  }, []);

  // ==================== API CALLS ====================

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch(`${API_URL}/users/current`);
      const data = await response.json();
      if (data.success && data.user) {
        setCurrentUser(data.user);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
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
      console.error('Error fetching users:', error);
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
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Login error:', error);
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
        fetchExistingUsers();
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim() || !currentUser) return;

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const data = await response.json();

      if (data.success) {
        setCurrentResponse(data.response);
        setMetadata(data.metadata);
        setConversations(prev => [...prev, {
          user: message,
          bot: data.response,
          mood: data.metadata.mood,
          timestamp: new Date()
        }]);

        // Speak response
        speakResponse(data.response);
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Chat error:', error);
      alert('Failed to send message');
    } finally {
      setTranscript('');
      setScreenState('listening');
    }
  };

  const speakResponse = (text) => {
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
    if (!recognitionRef.current || !currentUser) return;

    if (isMicActive) {
      recognitionRef.current.stop();
    } else {
      setIsProcessing(true);
      recognitionRef.current.start();
    }
  };

  const logout = () => {
    setCurrentUser(null);
    setConversations([]);
    setTranscript('');
  };

  // Simulate sound waves
  useEffect(() => {
    const interval = setInterval(() => {
      if (screenState === 'listening' && isMicActive) {
        setSoundIntensity(Math.random() * 0.8 + 0.2);
      }
    }, 200);
    return () => clearInterval(interval);
  }, [screenState, isMicActive]);

  const getStatusText = () => {
    switch (screenState) {
      case 'thinking':
        return 'Processing...';
      case 'responding':
        return 'Speaking...';
      default:
        return isMicActive ? 'Listening...' : 'Ready to Listen';
    }
  };

  const getStatusColor = () => {
    switch (screenState) {
      case 'thinking':
        return '#8B7F9E';
      case 'responding':
        return '#4ECDC4';
      default:
        return isMicActive ? '#DC2626' : '#3A506B';
    }
  };

  // ==================== AUTH SCREEN ====================

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
        <style>{`
          @keyframes fade-in {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in { animation: fade-in 0.5s ease-out; }
        `}</style>

        <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 animate-fade-in">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-2">
              🐘 JUMBO
            </h1>
            <p className="text-gray-600">Your Emotional Support Companion</p>
          </div>

          <div className="space-y-4">
            {/* Existing Users */}
            {existingUsers.length > 0 && (
              <>
                <p className="text-sm font-semibold text-gray-700">Select User:</p>
                <div className="grid grid-cols-2 gap-2">
                  {existingUsers.map(user => (
                    <button
                      key={user}
                      onClick={() => loginUser(user)}
                      disabled={isAuthenticating}
                      className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition disabled:opacity-50 font-medium"
                    >
                      {user}
                    </button>
                  ))}
                </div>
                <div className="border-t border-gray-200 my-4"></div>
              </>
            )}

            {/* New User */}
            <p className="text-sm font-semibold text-gray-700">New User:</p>
            <input
              type="text"
              placeholder="Enter your name"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && registerUser()}
              className="w-full px-4 py-2 border-2 border-purple-200 rounded-lg focus:outline-none focus:border-purple-600"
              disabled={isAuthenticating}
            />

            <select
              value={userLanguage}
              onChange={(e) => setUserLanguage(e.target.value)}
              className="w-full px-4 py-2 border-2 border-purple-200 rounded-lg focus:outline-none focus:border-purple-600"
              disabled={isAuthenticating}
            >
              <option value="en">English</option>
              <option value="te">Telugu</option>
              <option value="hi">Hindi</option>
            </select>

            <button
              onClick={registerUser}
              disabled={isAuthenticating || !userName.trim()}
              className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50"
            >
              {isAuthenticating ? 'Loading...' : 'Start Chatting'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==================== CHAT SCREEN ====================

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex flex-col items-center justify-center p-4">
      <style>{`
        @keyframes soundwave-pulse {
          0% { r: 0; opacity: 0.6; }
          100% { r: 100; opacity: 0; }
        }
        @keyframes particle-float {
          0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.6; }
          50% { transform: translate(var(--tx), var(--ty)) scale(1.2); opacity: 1; }
        }
        @keyframes glow-pulse {
          0%, 100% { filter: drop-shadow(0 0 16px rgba(78, 205, 196, 0.3)); }
          50% { filter: drop-shadow(0 0 24px rgba(78, 205, 196, 0.6)); }
        }
        @keyframes subtle-tilt {
          0%, 100% { transform: perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1); }
          50% { transform: perspective(1000px) rotateX(0deg) rotateY(2deg) scale(1.01); }
        }
        @keyframes zoom-in {
          from { transform: scale(1); }
          to { transform: scale(1.05); }
        }
        .jumbo-container {
          animation: ${isMicActive ? 'subtle-tilt 3s ease-in-out infinite' : screenState === 'responding' ? 'zoom-in 0.5s ease-out forwards, glow-pulse 2s ease-in-out infinite' : 'none'};
        }
        .soundwave { animation: soundwave-pulse 1.5s ease-out infinite; }
        .particle { animation: particle-float var(--duration, 3s) ease-in-out infinite; }
        @keyframes bounce {
          0%, 80%, 100% { opacity: 0.5; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1); }
        }
        .bounce-dot { animation: bounce 1.4s ease-in-out infinite; }
      `}</style>

      {/* Header */}
      <div className="absolute top-6 left-6 right-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-700">🐘 JUMBO</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">Welcome, {currentUser.name}</span>
          <button
            onClick={logout}
            className="p-2 hover:bg-red-50 rounded-full transition"
            title="Logout"
          >
            <LogOut size={20} className="text-red-500" />
          </button>
        </div>
      </div>

      <div className="mb-12 mt-16">
        <h2 className="text-4xl font-light text-center text-gray-700">
          {screenState === 'responding' ? 'Speaking...' : 'Talk with JUMBO'}
        </h2>
        <p className="text-center text-gray-500 mt-2">Click the microphone and share your thoughts</p>
      </div>

      <div className="relative w-full max-w-md">
        {/* Soundwave */}
        {screenState === 'listening' && isMicActive && (
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 300 400" style={{ pointerEvents: 'none' }}>
            {[0, 1, 2].map((i) => (
              <circle
                key={`wave-${i}`}
                cx="150"
                cy="280"
                r="20"
                fill="none"
                stroke="#DC2626"
                strokeWidth="2"
                opacity={0.3 * (1 - i * 0.2)}
                className="soundwave"
                style={{ animationDelay: `${i * 0.3}s` }}
              />
            ))}
          </svg>
        )}

        {/* Particles */}
        <div className="absolute inset-0 w-full h-full" style={{ pointerEvents: 'none' }}>
          {particlePositions.map((particle) => (
            <div
              key={particle.id}
              className="particle absolute rounded-full bg-yellow-300"
              style={{
                width: '8px',
                height: '8px',
                left: '50%',
                top: '30%',
                marginLeft: '-4px',
                marginTop: '-4px',
                '--tx': `${particle.x}px`,
                '--ty': `${particle.y}px`,
                '--duration': `${particle.duration}s`,
                opacity: isMicActive || screenState === 'thinking' ? 0.6 : 0.3,
                animation: isMicActive || screenState === 'thinking' ? `particle-float ${particle.duration}s ease-in-out infinite` : 'none',
              }}
            />
          ))}
        </div>

        {/* JUMBO */}
        <div className="flex justify-center mb-8">
          <div
            className="jumbo-container relative"
            style={{
              width: '240px',
              height: '240px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667EEA 0%, #764BA2 100%)',
              boxShadow: screenState === 'responding' ? '0 0 40px rgba(78, 205, 196, 0.4)' : '0 8px 32px rgba(0, 0, 0, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              transform: isMicActive ? 'scaleY(0.98) skewX(2deg)' : 'none',
            }}
          >
            <div className="text-8xl">
              {screenState === 'listening' && isMicActive ? '👂' : screenState === 'thinking' ? '🤔' : screenState === 'responding' ? '💬' : '🐘'}
            </div>

            {screenState === 'responding' && (
              <div
                className="absolute inset-0 rounded-full"
                style={{
                  border: '3px solid rgba(78, 205, 196, 0.3)',
                  animation: 'glow-pulse 2s ease-in-out infinite',
                }}
              />
            )}
          </div>
        </div>

        {/* Status Text */}
        <div className="text-center mt-12">
          <p
            className="text-base font-light transition-colors duration-500"
            style={{ color: getStatusColor() }}
          >
            {getStatusText()}
          </p>
          {screenState === 'thinking' && (
            <div className="flex justify-center gap-1 mt-2">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-2 h-2 rounded-full bg-gray-400 bounce-dot"
                  style={{ animationDelay: `${i * 0.2}s` }}
                />
              ))}
            </div>
          )}
          {transcript && (
            <div className="mt-4 p-3 bg-white rounded-2xl border-2 border-purple-200">
              <p className="text-sm text-gray-700 italic">"{transcript.trim()}"</p>
            </div>
          )}
        </div>

        {/* Response Box */}
        {currentResponse && (
          <div className="mt-6 p-4 bg-white rounded-2xl border-2 border-purple-200 shadow-lg">
            <p className="text-sm text-gray-700">{currentResponse}</p>
            {metadata.mood && (
              <p className="text-xs text-gray-500 mt-2">
                Mood: {metadata.mood} | Confidence: {(metadata.mood_confidence * 100).toFixed(0)}%
              </p>
            )}
          </div>
        )}

        {/* Mood Indicator */}
        {metadata.mood && (
          <div className="flex justify-center gap-4 mt-8">
            {metadata.mood === 'happy' && <Heart size={24} className="text-red-400" fill="currentColor" />}
            {metadata.mood === 'anxious' && <Cloud size={24} className="text-blue-300" />}
            {metadata.mood === 'sad' && <Sprout size={24} className="text-green-400" />}
          </div>
        )}
      </div>

      {/* Conversation History */}
      {conversations.length > 0 && (
        <div className="absolute bottom-20 left-6 right-6 max-h-32 overflow-y-auto bg-white rounded-2xl p-4 shadow-lg border-2 border-purple-200">
          <p className="text-xs font-semibold text-gray-700 mb-2">Recent Messages:</p>
          <div className="space-y-2">
            {conversations.slice(-3).map((conv, idx) => (
              <div key={idx} className="text-xs text-gray-600">
                <p className="font-semibold">You: {conv.user.substring(0, 40)}...</p>
                <p className="text-gray-500">Bot: {conv.bot.substring(0, 50)}...</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Microphone Button */}
      <div className="mt-16 flex flex-col items-center gap-4">
        <button
          onClick={toggleMic}
          disabled={isProcessing}
          className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl ${
            isMicActive
              ? 'bg-red-500 text-white scale-110 animate-pulse'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-2xl hover:scale-105'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          {isMicActive ? <MicOff size={40} /> : <Mic size={40} />}
        </button>
        <p className="text-sm text-gray-600 text-center max-w-xs">
          {isMicActive ? 'Listening to you... Click to stop' : 'Click the microphone to start talking'}
        </p>
      </div>
    </div>
  );
}