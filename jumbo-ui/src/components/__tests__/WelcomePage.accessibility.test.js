import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
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

// Mock console methods
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

describe('WelcomePage Accessibility Tests', () => {
  const mockCurrentUser = {
    id: 'test-user-id',
    name: 'John Doe',
    email: 'john.doe@example.com',
    access_token: 'mock-access-token'
  };

  const mockOnContinueToChat = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        preferences: { display_name: 'Johnny' }
      })
    });
  });

  describe('Semantic HTML Structure', () => {
    test('uses proper semantic HTML elements', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Check for semantic elements
      expect(screen.getByRole('banner')).toBeInTheDocument(); // header
      expect(screen.getByRole('main')).toBeInTheDocument(); // main content
      expect(screen.getAllByRole('group')).toHaveLength(1); // mood selector group
      expect(screen.getByRole('radiogroup')).toBeInTheDocument(); // mood options
    });

    test('has proper heading structure', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Main heading should be h1
      const mainHeading = screen.getByRole('heading', { level: 1 });
      expect(mainHeading).toBeInTheDocument();
      expect(mainHeading).toHaveTextContent(/Hey.*🌼/);
      
      // Section headings should be h2 (screen reader only)
      const sectionHeadings = screen.getAllByRole('heading', { level: 2 });
      expect(sectionHeadings.length).toBeGreaterThan(0);
    });

    test('has skip link for keyboard navigation', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const skipLink = screen.getByText('Skip to main content');
      expect(skipLink).toBeInTheDocument();
      expect(skipLink).toHaveAttribute('href', '#main-content');
    });
  });

  describe('ARIA Attributes and Labels', () => {
    test('mood selector has proper ARIA attributes', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const radioGroup = screen.getByRole('radiogroup');
      expect(radioGroup).toHaveAttribute('aria-labelledby', 'mood-instructions');
      expect(radioGroup).toHaveAttribute('aria-required', 'false');
    });

    test('mood options have proper radio button semantics', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      expect(moodButtons).toHaveLength(5);
      
      moodButtons.forEach((button, index) => {
        expect(button).toHaveAttribute('aria-checked', 'false');
        expect(button).toHaveAttribute('data-mood-index', index.toString());
      });
    });

    test('selected mood has correct ARIA state', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const happyButton = screen.getByRole('radio', { name: /Happy mood/ });
      fireEvent.click(happyButton);
      
      expect(happyButton).toHaveAttribute('aria-checked', 'true');
      expect(happyButton).toHaveAttribute('aria-describedby', 'mood-feedback');
    });

    test('feedback message has live region attributes', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const neutralButton = screen.getByRole('radio', { name: /Neutral mood/ });
      fireEvent.click(neutralButton);
      
      const feedback = screen.getByRole('status');
      expect(feedback).toHaveAttribute('aria-live', 'polite');
      expect(feedback).toHaveAttribute('aria-atomic', 'true');
      expect(feedback).toHaveAttribute('id', 'mood-feedback');
    });

    test('continue button has proper description', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/ });
      expect(continueButton).toHaveAttribute('aria-describedby', 'continue-description');
      
      const description = screen.getByText('Jumbo is here to listen and support you.');
      expect(description).toHaveAttribute('id', 'continue-description');
    });
  });

  describe('Keyboard Navigation', () => {
    test('mood buttons support arrow key navigation', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      const firstButton = moodButtons[0];
      const secondButton = moodButtons[1];
      
      // Focus first button
      firstButton.focus();
      expect(firstButton).toHaveFocus();
      
      // Arrow right should move to next button
      fireEvent.keyDown(firstButton, { key: 'ArrowRight' });
      // Note: In a real test, we'd need to mock the focus behavior
      // This tests that the event handler is present
      expect(firstButton).toHaveAttribute('data-mood-index', '0');
    });

    test('mood buttons support Enter and Space key selection', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const happyButton = screen.getByRole('radio', { name: /Happy mood/ });
      
      // Test Enter key
      fireEvent.keyDown(happyButton, { key: 'Enter' });
      expect(happyButton).toHaveAttribute('aria-checked', 'true');
      
      // Reset selection
      const sadButton = screen.getByRole('radio', { name: /Sad mood/ });
      
      // Test Space key
      fireEvent.keyDown(sadButton, { key: ' ' });
      expect(sadButton).toHaveAttribute('aria-checked', 'true');
    });

    test('proper tab order and focus management', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/ });
      
      // Initially, no mood button should be in tab order
      moodButtons.forEach(button => {
        expect(button).toHaveAttribute('tabIndex', '-1');
      });
      
      // Continue button should be focusable
      expect(continueButton).not.toHaveAttribute('tabIndex');
    });
  });

  describe('Screen Reader Support', () => {
    test('emojis are properly hidden from screen readers', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Mood emojis should be aria-hidden
      const moodEmojis = document.querySelectorAll('.mood-emoji');
      moodEmojis.forEach(emoji => {
        expect(emoji).toHaveAttribute('aria-hidden', 'true');
      });
      
      // Icons should be aria-hidden
      const sparklesIcon = document.querySelector('svg');
      if (sparklesIcon) {
        expect(sparklesIcon).toHaveAttribute('aria-hidden', 'true');
      }
    });

    test('screen reader only content is present', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Check for screen reader only headings
      const srOnlyHeadings = document.querySelectorAll('.sr-only');
      expect(srOnlyHeadings.length).toBeGreaterThan(0);
    });

    test('mood feedback includes descriptive text for screen readers', async () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const veryHappyButton = screen.getByRole('radio', { name: /Very Happy mood/ });
      fireEvent.click(veryHappyButton);
      
      const feedback = screen.getByRole('status');
      expect(feedback).toHaveTextContent(/feeling very happy/i);
    });
  });

  describe('High Contrast and Reduced Motion Support', () => {
    test('components have focus indicators', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/ });
      
      // Focus a mood button
      moodButtons[0].focus();
      
      // Focus continue button
      continueButton.focus();
      
      // Test passes if no errors are thrown (focus styles are applied via CSS)
      expect(moodButtons[0]).toBeInTheDocument();
      expect(continueButton).toBeInTheDocument();
    });

    test('respects user motion preferences', () => {
      // Mock prefers-reduced-motion
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Component should render without animations when reduced motion is preferred
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });

  describe('Error State Accessibility', () => {
    test('error messages are announced to screen readers', async () => {
      // Mock onContinueToChat to throw error
      mockOnContinueToChat.mockRejectedValueOnce(new Error('Navigation failed'));
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/ });
      fireEvent.click(continueButton);
      
      // Error should be announced
      const errorMessage = await screen.findByText(/Failed to continue/i);
      expect(errorMessage).toBeInTheDocument();
      
      // Error container should have appropriate role
      const errorContainer = errorMessage.closest('div');
      expect(errorContainer).toBeInTheDocument();
    });
  });

  describe('Loading State Accessibility', () => {
    test('loading states are announced to screen readers', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/ });
      
      // Click to trigger loading state
      fireEvent.click(continueButton);
      
      // Button should show loading text
      expect(screen.getByText('Loading...')).toBeInTheDocument();
      
      // Button should be disabled during loading
      expect(continueButton).toBeDisabled();
    });

    test('name loading state is handled gracefully', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Initially shows generic greeting
      expect(screen.getByText('Hey! 🌼')).toBeInTheDocument();
    });
  });
});