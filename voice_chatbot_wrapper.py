"""
Voice-Enabled Jumbo Chatbot Wrapper
Converts your existing text-based Jumbo chatbot to speech-enabled
Supports Telugu, Hindi, and English
"""

import speech_recognition as sr
import pyttsx3
import sys
import os

# Add your project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your Jumbo chatbot
from chatbot import JumboChatbot
from language_utils import Language
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================

class VoiceConfig:
    """Configuration for voice chatbot"""
    RECOGNITION_LANGUAGE = 'en-IN'  # Google Speech Recognition language
    TTS_RATE = 150  # Words per minute for text-to-speech
    TTS_VOLUME = 0.9  # Volume 0.0 to 1.0
    USE_FEMALE_VOICE = True
    TIMEOUT_SECONDS = 10
    PHRASE_TIME_LIMIT = 5

# ================== SPEECH RECOGNITION ==================

class VoiceChatbotInput:
    """Handle speech recognition with support for multiple languages"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language_map = {
            'te': 'te-IN',  # Telugu
            'hi': 'hi-IN',  # Hindi
            'en': 'en-IN',  # English
        }
    
    def recognize_speech(self, language_code='en-IN'):
        """
        Capture and recognize speech from microphone
        Returns: transcribed text or None if error
        """
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Capture audio with timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=VoiceConfig.TIMEOUT_SECONDS,
                    phrase_time_limit=VoiceConfig.PHRASE_TIME_LIMIT
                )
            
            # Recognize speech using Google Speech Recognition
            print("⏳ Processing speech...")
            text = self.recognizer.recognize_google(
                audio,
                language=language_code
            )
            print(f"👤 You: {text}")
            return text
            
        except sr.RequestError as e:
            print(f"❌ API Error: {e}")
            print("   (Check your internet connection)")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand the audio. Please speak clearly.")
            return None
        except sr.RequestError:
            print("❌ Could not reach speech recognition service.")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

# ================== TEXT-TO-SPEECH ==================

class VoiceChatbotOutput:
    """Handle text-to-speech conversion"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self._configure_engine()
    
    def _configure_engine(self):
        """Configure text-to-speech engine"""
        try:
            # Set speech rate
            self.engine.setProperty('rate', VoiceConfig.TTS_RATE)
            
            # Set volume
            self.engine.setProperty('volume', VoiceConfig.TTS_VOLUME)
            
            # Set voice (prefer female if available)
            voices = self.engine.getProperty('voices')
            if len(voices) > 0 and VoiceConfig.USE_FEMALE_VOICE:
                # Try to find female voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        return
                # Fall back to first available voice
                self.engine.setProperty('voice', voices[0].id)
        except Exception as e:
            logger.warning(f"Could not configure voice: {e}")
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"🤖 Bot: {text}\n")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ Text-to-Speech Error: {e}")
            print(f"   (Fallback text): {text}")

# ================== JUMBO CHATBOT INTERFACE ==================

class VoiceChatbotManager:
    """Manage the voice-enabled Jumbo chatbot"""
    
    def __init__(self):
        self.chatbot = JumboChatbot()
        self.voice_input = VoiceChatbotInput()
        self.voice_output = VoiceChatbotOutput()
        self.current_user = None
        self.current_language = Language.ENGLISH
        self.text_mode = False
    
    def setup_user(self):
        """Register or select a user"""
        print("\n" + "="*60)
        print("👤 USER SETUP")
        print("="*60)
        
        # Check for existing users
        existing_users = self.chatbot.get_all_users()
        
        if existing_users:
            print(f"\n📋 Existing users: {', '.join(existing_users)}")
            user_input = input("Enter your name (or 'new' for new user): ").strip()
            
            if user_input.lower() == 'new':
                return self._register_new_user()
            elif self.chatbot.user_exists(user_input):
                self.chatbot.set_current_user(user_input)
                self.current_user = self.chatbot.get_current_user()
                print(f"✅ Welcome back, {user_input}!")
                return True
            else:
                return self._register_new_user(user_input)
        else:
            return self._register_new_user()
    
    def _register_new_user(self, suggested_name=None):
        """Register a new user"""
        while True:
            if suggested_name:
                name = suggested_name
            else:
                name = input("\n📝 Enter your name: ").strip()
            
            if not name or len(name) < 2:
                print("❌ Name must be at least 2 characters long.")
                continue
            
            success, message = self.chatbot.register_new_user(name)
            print(f"{'✅' if success else '❌'} {message}")
            
            if success:
                self.current_user = self.chatbot.get_current_user()
                return True
            
            suggested_name = None
    
    def chat_voice_mode(self):
        """Run chatbot in voice mode"""
        print("\n🎤 VOICE MODE")
        print("   Say something to chat, say 'exit' to quit, 'text mode' to switch\n")
        
        # Determine language based on user preference or detection
        language_code = self.voice_input.language_map.get(
            self.current_language.value,
            'en-IN'
        )
        
        # Get user input via speech
        user_input = self.voice_input.recognize_speech(language_code)
        
        if user_input is None:
            print("   Retrying...\n")
            return True
        
        # Check for mode switches
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("\n👋 Goodbye!")
            return False
        
        if user_input.lower() == 'text mode':
            self.text_mode = True
            print("\n📝 Switched to text mode. Say 'voice mode' to switch back.")
            return True
        
        # Process with chatbot
        response, metadata = self.chatbot.process_message(user_input)
        
        # Output response
        self.voice_output.speak(response)
        
        # Print metadata for debugging
        if metadata.get('used_llm'):
            print("   [Used LLM for response]")
        else:
            print(f"   [Scenario: {metadata.get('scenario', 'unknown')}]")
        
        return True
    
    def chat_text_mode(self):
        """Run chatbot in text mode"""
        print("\n📝 TEXT MODE")
        print("   Type to chat, 'exit' to quit, 'voice mode' to switch\n")
        
        user_input = input("You: ").strip()
        
        if not user_input:
            return True
        
        # Check for mode switches
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("\n👋 Goodbye!")
            return False
        
        if user_input.lower() == 'voice mode':
            self.text_mode = False
            print("\n🎤 Switched to voice mode.")
            return True
        
        # Process with chatbot
        response, metadata = self.chatbot.process_message(user_input)
        
        # Output response
        print(f"\nBot: {response}\n")
        
        # Print metadata for debugging
        if metadata.get('used_llm'):
            print("   [Used LLM for response]")
        else:
            print(f"   [Scenario: {metadata.get('scenario', 'unknown')}]")
        
        return True
    
    def run(self):
        """Main loop"""
        try:
            print("\n" + "="*60)
            print("🐘 JUMBO VOICE-ENABLED CHATBOT")
            print("="*60)
            print("\nSupported Languages: Telugu, Hindi, English")
            print("Modes: Voice & Text")
            
            # Setup user
            if not self.setup_user():
                return
            
            # Get user stats
            stats = self.chatbot.get_user_stats()
            print(f"\n📊 User Stats:")
            print(f"   Name: {stats.get('user_name')}")
            print(f"   Language: {stats.get('language')}")
            print(f"   Total Conversations: {stats.get('total_conversations')}")
            
            print("\n" + "="*60)
            print("Starting chat... (Say or type 'exit' to quit)")
            print("="*60 + "\n")
            
            # Main conversation loop
            while True:
                try:
                    if self.text_mode:
                        if not self.chat_text_mode():
                            break
                    else:
                        if not self.chat_voice_mode():
                            break
                
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
                except Exception as e:
                    logger.error(f"Error in chat loop: {e}")
                    print(f"❌ Error: {e}")
                    print("   Retrying...\n")
                    continue
        
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            print(f"❌ Fatal Error: {e}")
            import traceback
            traceback.print_exc()

# ================== ENTRY POINT ==================

def check_dependencies():
    """Verify all dependencies are installed"""
    required = {
        'pyttsx3': 'pyttsx3',
        'speech_recognition': 'SpeechRecognition',
        'groq': 'groq',
    }
    
    missing = []
    for import_name, display_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(display_name)
    
    if missing:
        print("❌ Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\n📦 Install with:")
        print("   pip install " + " ".join(missing))
        return False
    
    return True

def main():
    """Main entry point"""
    print("\n🚀 Starting Jumbo Voice Chatbot...\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies loaded successfully\n")
    
    # Run chatbot
    try:
        manager = VoiceChatbotManager()
        manager.run()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()