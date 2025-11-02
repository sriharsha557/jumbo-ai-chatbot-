/**
 * Jumbo Voice Utility
 * Implements the "Jumbo Speaks" voice concept for consistent speech synthesis
 * 
 * Voice Characteristics:
 * - Gender-neutral
 * - Soft, low-mid pitch
 * - Neutral Indian or global accent
 * - Calm pacing (140–150 words per minute)
 * - Gentle inflection at sentence ends
 * - Soothing and empathetic, like a gentle elephant companion
 */

export class JumboVoice {
  constructor() {
    this.synthesis = window.speechSynthesis;
    this.preferredVoice = null;
    this.isInitialized = false;
    
    // Initialize voice when voices are available
    this.initializeVoice();
  }

  /**
   * Initialize Jumbo's preferred voice
   */
  initializeVoice() {
    if (!this.synthesis) {
      console.warn('🐘 Speech synthesis not available');
      return;
    }

    const loadVoices = () => {
      const voices = this.synthesis.getVoices();
      
      if (voices.length === 0) return;

      // Find the best voice for Jumbo based on characteristics
      this.preferredVoice = this.selectBestVoice(voices);
      this.isInitialized = true;
      
      console.log('🐘 Jumbo voice initialized:', this.preferredVoice?.name || 'Default system voice');
    };

    // Load voices immediately if available
    loadVoices();

    // Also listen for voice changes (some browsers load voices asynchronously)
    if (this.synthesis.onvoiceschanged !== undefined) {
      this.synthesis.onvoiceschanged = loadVoices;
    }
  }

  /**
   * Select the best available voice for Jumbo
   * @param {SpeechSynthesisVoice[]} voices - Available voices
   * @returns {SpeechSynthesisVoice|null} - Best voice for Jumbo
   */
  selectBestVoice(voices) {
    // Priority order for voice selection
    const voicePreferences = [
      // Gender-neutral voices
      (voice) => voice.name.toLowerCase().includes('neutral'),
      (voice) => voice.name.toLowerCase().includes('alex'), // Often gender-neutral
      
      // Calm/gentle voices
      (voice) => voice.name.toLowerCase().includes('calm'),
      (voice) => voice.name.toLowerCase().includes('gentle'),
      (voice) => voice.name.toLowerCase().includes('soft'),
      
      // Pleasant female voices (as fallback)
      (voice) => voice.name.toLowerCase().includes('samantha'),
      (voice) => voice.name.toLowerCase().includes('karen'),
      (voice) => voice.name.toLowerCase().includes('serena'),
      
      // Pleasant male voices (as fallback)
      (voice) => voice.name.toLowerCase().includes('daniel'),
      (voice) => voice.name.toLowerCase().includes('thomas'),
      
      // Default English voices
      (voice) => voice.default && voice.lang.startsWith('en'),
      (voice) => voice.lang.startsWith('en-US'),
      (voice) => voice.lang.startsWith('en-GB'),
      (voice) => voice.lang.startsWith('en'),
    ];

    // Try each preference in order
    for (const preference of voicePreferences) {
      const matchingVoice = voices.find(preference);
      if (matchingVoice) {
        console.log('🐘 Selected Jumbo voice:', matchingVoice.name, `(${matchingVoice.lang})`);
        return matchingVoice;
      }
    }

    // Fallback to first available voice
    console.log('🐘 Using fallback voice for Jumbo:', voices[0]?.name);
    return voices[0] || null;
  }

  /**
   * Create a speech utterance with Jumbo's voice characteristics
   * @param {string} text - Text to speak
   * @returns {SpeechSynthesisUtterance} - Configured utterance
   */
  createUtterance(text) {
    if (!this.synthesis) {
      throw new Error('Speech synthesis not available');
    }

    // Process text for natural, gentle delivery
    const processedText = this.processTextForJumbo(text);
    
    const utterance = new SpeechSynthesisUtterance(processedText);
    
    // Apply Jumbo's voice characteristics
    utterance.rate = 0.75;    // Calm pacing (140-150 WPM)
    utterance.pitch = 0.8;    // Soft, low-mid pitch
    utterance.volume = 0.9;   // Gentle but clear volume
    
    // Use preferred voice if available
    if (this.preferredVoice) {
      utterance.voice = this.preferredVoice;
    }

    return utterance;
  }

  /**
   * Process text to make it more suitable for Jumbo's gentle delivery
   * @param {string} text - Original text
   * @returns {string} - Processed text
   */
  processTextForJumbo(text) {
    return text
      // Ensure gentle inflection by converting exclamations to periods
      .replace(/!/g, '.')
      // Add slight pauses for natural breathing
      .replace(/\. /g, '. ')
      .replace(/, /g, ', ')
      // Ensure questions maintain gentle tone
      .replace(/\?/g, '?')
      // Remove excessive punctuation that might sound harsh
      .replace(/\.{2,}/g, '.')
      .replace(/\?{2,}/g, '?')
      // Trim whitespace
      .trim();
  }

  /**
   * Speak text with Jumbo's voice
   * @param {string} text - Text to speak
   * @param {Object} options - Additional options
   * @returns {Promise} - Promise that resolves when speech completes
   */
  speak(text, options = {}) {
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        reject(new Error('Speech synthesis not available'));
        return;
      }

      try {
        // Cancel any ongoing speech
        this.synthesis.cancel();

        // Ensure audio context is resumed (for headphones/audio devices)
        this.ensureAudioContext();

        const utterance = this.createUtterance(text);

        // Apply any custom options
        if (options.rate !== undefined) utterance.rate = options.rate;
        if (options.pitch !== undefined) utterance.pitch = options.pitch;
        if (options.volume !== undefined) utterance.volume = options.volume;

        // Set up event handlers
        utterance.onstart = () => {
          console.log('🐘 Jumbo begins speaking:', text.substring(0, 50) + '...');
          if (options.onStart) options.onStart();
        };

        utterance.onend = () => {
          console.log('🐘 Jumbo finished speaking');
          if (options.onEnd) options.onEnd();
          resolve();
        };

        utterance.onerror = (event) => {
          console.error('🐘 Jumbo speech error:', event);
          if (options.onError) options.onError(event);
          reject(event);
        };

        // Add a brief pause before speaking for natural feel
        setTimeout(() => {
          if (this.synthesis) {
            this.synthesis.speak(utterance);
          }
        }, options.delay || 200);

      } catch (error) {
        console.error('🐘 Error creating Jumbo speech:', error);
        reject(error);
      }
    });
  }

  /**
   * Stop any ongoing speech
   */
  stop() {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }

  /**
   * Ensure audio context is active for proper audio routing (iOS-optimized)
   */
  ensureAudioContext() {
    try {
      // Create or resume audio context to ensure proper audio routing
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        if (!this.audioContext) {
          this.audioContext = new AudioContextClass();
        }
        
        // iOS-specific: Always try to resume audio context
        if (this.audioContext.state === 'suspended') {
          this.audioContext.resume().then(() => {
            console.log('🐘 Audio context resumed for speech synthesis');
          }).catch(err => {
            console.warn('🐘 Could not resume audio context:', err);
          });
        }
        
        // iOS Safari fix: Create a silent buffer to "prime" the audio system
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
          try {
            const buffer = this.audioContext.createBuffer(1, 1, 22050);
            const source = this.audioContext.createBufferSource();
            source.buffer = buffer;
            source.connect(this.audioContext.destination);
            source.start(0);
            console.log('🍎 iOS audio system primed');
          } catch (primeError) {
            console.warn('🍎 iOS audio priming failed:', primeError);
          }
        }
      }
    } catch (error) {
      console.warn('🐘 Audio context initialization failed:', error);
    }
  }

  /**
   * Check if speech synthesis is available and working
   * @returns {boolean} - True if speech is available
   */
  isAvailable() {
    return !!(this.synthesis && this.synthesis.speak);
  }

  /**
   * Get information about the current voice setup
   * @returns {Object} - Voice information
   */
  getVoiceInfo() {
    return {
      isAvailable: this.isAvailable(),
      isInitialized: this.isInitialized,
      preferredVoice: this.preferredVoice ? {
        name: this.preferredVoice.name,
        lang: this.preferredVoice.lang,
        gender: this.preferredVoice.gender || 'unknown'
      } : null,
      totalVoices: this.synthesis ? this.synthesis.getVoices().length : 0
    };
  }
}

// Create a singleton instance for consistent voice across the app
export const jumboVoice = new JumboVoice();

// Export utility functions for easy use
export const speakAsJumbo = (text, options) => jumboVoice.speak(text, options);
export const stopJumboSpeech = () => jumboVoice.stop();
export const getJumboVoiceInfo = () => jumboVoice.getVoiceInfo();