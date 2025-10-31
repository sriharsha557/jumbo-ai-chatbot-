import { JumboVoice, jumboVoice, speakAsJumbo, stopJumboSpeech, getJumboVoiceInfo } from '../jumboVoice';

// Mock Speech Synthesis API
const mockSpeechSynthesis = {
  speak: jest.fn(),
  cancel: jest.fn(),
  getVoices: jest.fn(() => [
    { name: 'Alex', lang: 'en-US', default: false },
    { name: 'Samantha', lang: 'en-US', default: false },
    { name: 'Google US English', lang: 'en-US', default: true },
    { name: 'Microsoft David', lang: 'en-US', default: false }
  ]),
  onvoiceschanged: null
};

const mockSpeechSynthesisUtterance = jest.fn().mockImplementation((text) => ({
  text,
  rate: 1,
  pitch: 1,
  volume: 1,
  voice: null,
  onstart: null,
  onend: null,
  onerror: null
}));

// Mock global objects
global.window = {
  speechSynthesis: mockSpeechSynthesis,
  SpeechSynthesisUtterance: mockSpeechSynthesisUtterance
};

global.SpeechSynthesisUtterance = mockSpeechSynthesisUtterance;

describe('JumboVoice', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('JumboVoice Class', () => {
    test('initializes correctly', () => {
      const voice = new JumboVoice();
      expect(voice.synthesis).toBe(mockSpeechSynthesis);
      expect(voice.isAvailable()).toBe(true);
    });

    test('selects best voice from available options', () => {
      const voice = new JumboVoice();
      const voices = mockSpeechSynthesis.getVoices();
      const selectedVoice = voice.selectBestVoice(voices);
      
      // Should prefer Alex (gender-neutral) over others
      expect(selectedVoice.name).toBe('Alex');
    });

    test('processes text for gentle delivery', () => {
      const voice = new JumboVoice();
      const originalText = "Hello! How are you? I'm excited to help!!!";
      const processedText = voice.processTextForJumbo(originalText);
      
      // Should convert exclamations to periods for gentler tone
      expect(processedText).toBe("Hello. How are you? I'm excited to help.");
    });

    test('creates utterance with correct Jumbo characteristics', () => {
      const voice = new JumboVoice();
      const utterance = voice.createUtterance("Hello there");
      
      expect(utterance.rate).toBe(0.75); // Calm pacing
      expect(utterance.pitch).toBe(0.8); // Soft, low-mid pitch
      expect(utterance.volume).toBe(0.9); // Gentle volume
    });
  });

  describe('Speech Functionality', () => {
    test('speaks text with Jumbo voice characteristics', async () => {
      const voice = new JumboVoice();
      
      // Mock the speak method to resolve immediately
      mockSpeechSynthesis.speak.mockImplementation((utterance) => {
        setTimeout(() => utterance.onend && utterance.onend(), 0);
      });

      await voice.speak("Hello, I'm Jumbo");
      
      expect(mockSpeechSynthesis.cancel).toHaveBeenCalled();
      expect(mockSpeechSynthesis.speak).toHaveBeenCalled();
    });

    test('handles speech errors gracefully', async () => {
      const voice = new JumboVoice();
      
      // Mock the speak method to trigger an error
      mockSpeechSynthesis.speak.mockImplementation((utterance) => {
        setTimeout(() => utterance.onerror && utterance.onerror(new Error('Speech failed')), 0);
      });

      await expect(voice.speak("Hello")).rejects.toThrow();
    });

    test('stops ongoing speech', () => {
      const voice = new JumboVoice();
      voice.stop();
      
      expect(mockSpeechSynthesis.cancel).toHaveBeenCalled();
    });
  });

  describe('Utility Functions', () => {
    test('speakAsJumbo function works', async () => {
      mockSpeechSynthesis.speak.mockImplementation((utterance) => {
        setTimeout(() => utterance.onend && utterance.onend(), 0);
      });

      await speakAsJumbo("Hello from utility function");
      
      expect(mockSpeechSynthesis.speak).toHaveBeenCalled();
    });

    test('stopJumboSpeech function works', () => {
      stopJumboSpeech();
      
      expect(mockSpeechSynthesis.cancel).toHaveBeenCalled();
    });

    test('getJumboVoiceInfo returns correct information', () => {
      const info = getJumboVoiceInfo();
      
      expect(info).toHaveProperty('isAvailable');
      expect(info).toHaveProperty('isInitialized');
      expect(info).toHaveProperty('totalVoices');
      expect(info.isAvailable).toBe(true);
    });
  });

  describe('Voice Selection Logic', () => {
    test('prefers gender-neutral voices', () => {
      const voice = new JumboVoice();
      const voices = [
        { name: 'Microsoft David', lang: 'en-US' },
        { name: 'Alex', lang: 'en-US' }, // Gender-neutral
        { name: 'Microsoft Zira', lang: 'en-US' }
      ];
      
      const selected = voice.selectBestVoice(voices);
      expect(selected.name).toBe('Alex');
    });

    test('falls back to calm voices when no gender-neutral available', () => {
      const voice = new JumboVoice();
      const voices = [
        { name: 'Microsoft David', lang: 'en-US' },
        { name: 'Calm Voice', lang: 'en-US' },
        { name: 'Microsoft Zira', lang: 'en-US' }
      ];
      
      const selected = voice.selectBestVoice(voices);
      expect(selected.name).toBe('Calm Voice');
    });

    test('uses default voice as final fallback', () => {
      const voice = new JumboVoice();
      const voices = [
        { name: 'Microsoft David', lang: 'en-US', default: false },
        { name: 'Google US English', lang: 'en-US', default: true }
      ];
      
      const selected = voice.selectBestVoice(voices);
      expect(selected.name).toBe('Google US English');
    });
  });

  describe('Error Handling', () => {
    test('handles missing speech synthesis gracefully', () => {
      // Temporarily remove speech synthesis
      const originalSynthesis = global.window.speechSynthesis;
      global.window.speechSynthesis = null;
      
      const voice = new JumboVoice();
      expect(voice.isAvailable()).toBe(false);
      
      // Restore
      global.window.speechSynthesis = originalSynthesis;
    });

    test('handles empty voice list', () => {
      mockSpeechSynthesis.getVoices.mockReturnValue([]);
      
      const voice = new JumboVoice();
      const selected = voice.selectBestVoice([]);
      
      expect(selected).toBeNull();
    });
  });

  describe('Singleton Instance', () => {
    test('jumboVoice is a singleton instance', () => {
      expect(jumboVoice).toBeInstanceOf(JumboVoice);
      expect(jumboVoice.isAvailable()).toBe(true);
    });

    test('singleton maintains state across calls', () => {
      const info1 = jumboVoice.getVoiceInfo();
      const info2 = jumboVoice.getVoiceInfo();
      
      expect(info1).toEqual(info2);
    });
  });
});