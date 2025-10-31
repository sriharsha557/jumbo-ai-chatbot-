import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import WelcomePage from '../WelcomePage';

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock console methods to avoid noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

describe('WelcomePage Component', () => {
  const mockCurrentUser = {
    id: 'test-user-id',
    name: 'John Doe',
    email: 'john.doe@example.com',
    access_token: 'mock-access-token'
  };

  const mockOnContinueToChat = jest.fn();

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    fetch.mockClear();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    
    // Mock successful profile fetch by default
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        preferences: {
          display_name: 'Johnny'
        }
      })
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    test('renders welcome page with basic elements', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Check for main elements
      expect(screen.getByText(/How are you feeling today?/i)).toBeInTheDocument();
      expect(screen.getByText(/Tap the emoji that best describes how you feel right now/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Continue to Chat/i })).toBeInTheDocument();
      expect(screen.getByText(/Jumbo is here to listen and support you/i)).toBeInTheDocument();
    });

    test('renders all mood selector options', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Check for all mood options
      expect(screen.getByRole('button', { name: /Select Very Sad mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Sad mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Neutral mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Happy mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Very Happy mood/i })).toBeInTheDocument();
    });

    test('displays inspirational message', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Should display one of the inspirational messages
      const inspirationalSection = screen.getByText(/"/);
      expect(inspirationalSection).toBeInTheDocument();
    });

    test('shows loading state initially for name', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Should show loading state initially
      expect(screen.getByText('Hey! 🌼')).toBeInTheDocument();
    });
  });

  describe('Personalized Greeting', () => {
    test('displays preferred name from profile after loading', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Wait for profile to load and name to update
      await waitFor(() => {
        expect(screen.getByText('Hey Johnny! 🌼')).toBeInTheDocument();
      });
    });

    test('falls back to current user name when profile fetch fails', async () => {
      // Mock failed profile fetch
      fetch.mockRejectedValueOnce(new Error('API Error'));
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      await waitFor(() => {
        expect(screen.getByText('Hey John! 🌼')).toBeInTheDocument();
      });
    });

    test('falls back to email username when no name available', async () => {
      // Mock failed profile fetch
      fetch.mockRejectedValueOnce(new Error('API Error'));
      
      const userWithoutName = {
        ...mockCurrentUser,
        name: null
      };
      
      render(<WelcomePage currentUser={userWithoutName} onContinueToChat={mockOnContinueToChat} />);
      
      await waitFor(() => {
        expect(screen.getByText('Hey john.doe! 🌼')).toBeInTheDocument();
      });
    });

    test('falls back to "there" when no name or email available', async () => {
      // Mock failed profile fetch
      fetch.mockRejectedValueOnce(new Error('API Error'));
      
      const userWithoutNameOrEmail = {
        ...mockCurrentUser,
        name: null,
        email: null
      };
      
      render(<WelcomePage currentUser={userWithoutNameOrEmail} onContinueToChat={mockOnContinueToChat} />);
      
      await waitFor(() => {
        expect(screen.getByText('Hey there! 🌼')).toBeInTheDocument();
      });
    });
  });

  describe('Mood Selection Functionality', () => {
    test('allows mood selection and shows encouragement message', async () => {
      // Mock successful mood API call
      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, preferences: { display_name: 'Johnny' } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, mood_entry: { id: '123' } })
        });

      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Click on happy mood
      const happyMoodButton = screen.getByRole('button', { name: /Select Happy mood/i });
      fireEvent.click(happyMoodButton);
      
      // Should show encouragement message
      await waitFor(() => {
        expect(screen.getByText(/Thanks for sharing. I'm here to support you wherever you are/i)).toBeInTheDocument();
      });
    });

    test('stores mood data in localStorage', async () => {
      // Mock successful API calls
      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, preferences: { display_name: 'Johnny' } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, mood_entry: { id: '123' } })
        });

      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Click on neutral mood
      const neutralMoodButton = screen.getByRole('button', { name: /Select Neutral mood/i });
      fireEvent.click(neutralMoodButton);
      
      // Should store mood in localStorage
      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'jumbo_mood_history',
          expect.stringContaining('neutral')
        );
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'jumbo_last_mood',
          expect.stringContaining('neutral')
        );
      });
    });

    test('handles API failure gracefully', async () => {
      // Mock profile success but mood API failure
      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, preferences: { display_name: 'Johnny' } })
        })
        .mockRejectedValueOnce(new Error('Network error'));

      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Click on sad mood
      const sadMoodButton = screen.getByRole('button', { name: /Select Sad mood/i });
      fireEvent.click(sadMoodButton);
      
      // Should still show encouragement message (localStorage fallback worked)
      await waitFor(() => {
        expect(screen.getByText(/Thanks for sharing. I'm here to support you wherever you are/i)).toBeInTheDocument();
      });
      
      // Should still store in localStorage
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    test('visual feedback for selected mood', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const veryHappyButton = screen.getByRole('button', { name: /Select Very Happy mood/i });
      fireEvent.click(veryHappyButton);
      
      // The button should have selected styling (we can't easily test CSS, but we can test the click worked)
      await waitFor(() => {
        expect(screen.getByText(/Thanks for sharing/i)).toBeInTheDocument();
      });
    });
  });

  describe('Navigation and Continue Functionality', () => {
    test('continue button calls onContinueToChat with mood data', async () => {
      // Mock API calls
      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, preferences: { display_name: 'Johnny' } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, mood_entry: { id: '123' } })
        });

      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Select a mood first
      const happyMoodButton = screen.getByRole('button', { name: /Select Happy mood/i });
      fireEvent.click(happyMoodButton);
      
      // Click continue button
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/i });
      fireEvent.click(continueButton);
      
      await waitFor(() => {
        expect(mockOnContinueToChat).toHaveBeenCalledWith(
          expect.objectContaining({
            mood_type: 'happy',
            user_id: 'test-user-id'
          })
        );
      });
    });

    test('continue button works without mood selection', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Click continue button without selecting mood
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/i });
      fireEvent.click(continueButton);
      
      await waitFor(() => {
        expect(mockOnContinueToChat).toHaveBeenCalledWith(null);
      });
    });

    test('shows loading state when continuing', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/i });
      fireEvent.click(continueButton);
      
      // Should show loading text briefly
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('displays error message when continue fails', async () => {
      // Mock onContinueToChat to throw error
      mockOnContinueToChat.mockRejectedValueOnce(new Error('Navigation failed'));
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/i });
      fireEvent.click(continueButton);
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to continue. Please try again/i)).toBeInTheDocument();
      });
    });

    test('handles localStorage errors gracefully', async () => {
      // Mock localStorage to throw error
      localStorageMock.setItem.mockImplementationOnce(() => {
        throw new Error('Storage full');
      });

      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const neutralMoodButton = screen.getByRole('button', { name: /Select Neutral mood/i });
      fireEvent.click(neutralMoodButton);
      
      // Should still show encouragement message despite storage error
      await waitFor(() => {
        expect(screen.getByText(/Thanks for sharing/i)).toBeInTheDocument();
      });
    });
  });

  describe('API Integration', () => {
    test('makes correct API call for profile preferences', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/onboarding/preferences'),
          expect.objectContaining({
            method: 'GET',
            headers: expect.objectContaining({
              'Authorization': 'Bearer mock-access-token',
              'Content-Type': 'application/json'
            })
          })
        );
      });
    });

    test('makes correct API call for mood entry', async () => {
      // Mock profile fetch
      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, preferences: { display_name: 'Johnny' } })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, mood_entry: { id: '123' } })
        });

      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const happyMoodButton = screen.getByRole('button', { name: /Select Happy mood/i });
      fireEvent.click(happyMoodButton);
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/mood/entry'),
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Authorization': 'Bearer mock-access-token',
              'Content-Type': 'application/json'
            }),
            body: expect.stringContaining('happy')
          })
        );
      });
    });

    test('handles missing access token', async () => {
      const userWithoutToken = {
        ...mockCurrentUser,
        access_token: null
      };

      render(<WelcomePage currentUser={userWithoutToken} onContinueToChat={mockOnContinueToChat} />);
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/onboarding/preferences'),
          expect.objectContaining({
            headers: expect.not.objectContaining({
              'Authorization': expect.anything()
            })
          })
        );
      });
    });
  });

  describe('Inspirational Messages', () => {
    test('displays random inspirational message', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Should contain quotes around the message
      const messageElement = screen.getByText(/"/);
      expect(messageElement).toBeInTheDocument();
      
      // Message should be one of the predefined ones (we can't test randomness easily, but we can test format)
      expect(messageElement.textContent).toMatch(/^".*"$/);
    });
  });

  describe('Accessibility', () => {
    test('mood buttons have proper ARIA labels', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      expect(screen.getByRole('button', { name: /Select Very Sad mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Sad mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Neutral mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Happy mood/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Select Very Happy mood/i })).toBeInTheDocument();
    });

    test('continue button is accessible', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/i });
      expect(continueButton).toBeInTheDocument();
      expect(continueButton).not.toBeDisabled();
    });
  });
});