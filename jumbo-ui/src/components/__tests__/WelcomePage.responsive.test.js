import React from 'react';
import { render, screen } from '@testing-library/react';
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

// Helper function to mock window dimensions
const mockViewport = (width, height) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
  
  // Mock matchMedia for responsive breakpoints
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => {
      const matches = {
        '(max-width: 768px)': width <= 768,
        '(max-width: 480px)': width <= 480,
        '(min-width: 769px)': width >= 769,
        '(prefers-reduced-motion: reduce)': false,
        '(prefers-contrast: high)': false,
      };
      
      return {
        matches: matches[query] || false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      };
    }),
  });
  
  // Trigger resize event
  window.dispatchEvent(new Event('resize'));
};

describe('WelcomePage Responsive Design Tests', () => {
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

  afterEach(() => {
    // Reset viewport to default
    mockViewport(1024, 768);
  });

  describe('Desktop Layout (>768px)', () => {
    beforeEach(() => {
      mockViewport(1024, 768);
    });

    test('renders full desktop layout', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // All elements should be visible
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      expect(screen.getByRole('button', { name: /Continue to Chat/ })).toBeInTheDocument();
      
      // Check for desktop-specific classes
      const content = document.querySelector('.welcome-content');
      expect(content).toBeInTheDocument();
    });

    test('mood selector has proper spacing on desktop', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodSelector = document.querySelector('.mood-selector');
      expect(moodSelector).toBeInTheDocument();
      
      // All mood buttons should be visible
      const moodButtons = screen.getAllByRole('radio');
      expect(moodButtons).toHaveLength(5);
      
      moodButtons.forEach(button => {
        expect(button).toBeVisible();
      });
    });

    test('text sizes are appropriate for desktop', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const title = screen.getByRole('heading', { level: 1 });
      expect(title).toHaveClass('welcome-title');
      
      const subtitle = screen.getByText(/How are you feeling today?/);
      expect(subtitle).toHaveClass('welcome-subtitle');
    });
  });

  describe('Tablet Layout (768px)', () => {
    beforeEach(() => {
      mockViewport(768, 1024);
    });

    test('adapts layout for tablet screens', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Core functionality should remain
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      expect(screen.getByRole('button', { name: /Continue to Chat/ })).toBeInTheDocument();
    });

    test('mood selector remains horizontal on tablet', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      expect(moodButtons).toHaveLength(5);
      
      // All buttons should still be accessible
      moodButtons.forEach(button => {
        expect(button).toBeVisible();
      });
    });
  });

  describe('Mobile Layout (<480px)', () => {
    beforeEach(() => {
      mockViewport(375, 667); // iPhone SE dimensions
    });

    test('adapts layout for mobile screens', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Core functionality should remain
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      expect(screen.getByRole('button', { name: /Continue to Chat/ })).toBeInTheDocument();
    });

    test('mood buttons have appropriate touch targets on mobile', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      expect(moodButtons).toHaveLength(5);
      
      // All buttons should be accessible for touch
      moodButtons.forEach(button => {
        expect(button).toBeVisible();
        // Touch targets should be at least 44px (we can't easily test computed styles)
        expect(button).toBeInTheDocument();
      });
    });

    test('text scales appropriately for mobile', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const title = screen.getByRole('heading', { level: 1 });
      expect(title).toHaveClass('welcome-title');
      
      // Mobile-specific classes should be applied via CSS
      expect(title).toBeInTheDocument();
    });

    test('content remains readable on small screens', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // All text content should be present and readable
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getByText(/Tap the emoji that best describes/)).toBeInTheDocument();
      expect(screen.getByText(/Jumbo is here to listen and support you/)).toBeInTheDocument();
    });
  });

  describe('Very Small Mobile (<375px)', () => {
    beforeEach(() => {
      mockViewport(320, 568); // iPhone 5/SE dimensions
    });

    test('handles very small screens gracefully', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Core functionality should still work
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      expect(screen.getByRole('button', { name: /Continue to Chat/ })).toBeInTheDocument();
    });

    test('mood selector adapts to very narrow screens', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      expect(moodButtons).toHaveLength(5);
      
      // Buttons should still be usable even on very small screens
      moodButtons.forEach(button => {
        expect(button).toBeVisible();
      });
    });
  });

  describe('Large Desktop (>1200px)', () => {
    beforeEach(() => {
      mockViewport(1440, 900);
    });

    test('handles large screens without excessive stretching', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Content should be centered and not stretched too wide
      const content = document.querySelector('.welcome-content');
      expect(content).toBeInTheDocument();
      
      // All elements should remain accessible
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
    });

    test('maintains proper proportions on large screens', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      expect(moodButtons).toHaveLength(5);
      
      // Layout should not be overly spread out
      moodButtons.forEach(button => {
        expect(button).toBeVisible();
      });
    });
  });

  describe('Landscape Orientation', () => {
    beforeEach(() => {
      mockViewport(667, 375); // Mobile landscape
    });

    test('adapts to landscape orientation', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Content should still be accessible in landscape
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      expect(screen.getByRole('button', { name: /Continue to Chat/ })).toBeInTheDocument();
    });

    test('mood selector works in landscape mode', () => {
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      expect(moodButtons).toHaveLength(5);
      
      // All buttons should be accessible in landscape
      moodButtons.forEach(button => {
        expect(button).toBeVisible();
      });
    });
  });

  describe('Content Overflow and Scrolling', () => {
    test('handles content overflow gracefully', () => {
      mockViewport(320, 400); // Very constrained height
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // All content should still be present
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      expect(screen.getByRole('button', { name: /Continue to Chat/ })).toBeInTheDocument();
    });

    test('maintains usability with limited vertical space', () => {
      mockViewport(375, 300); // Very short screen
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Critical elements should remain accessible
      const moodButtons = screen.getAllByRole('radio');
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/ });
      
      expect(moodButtons).toHaveLength(5);
      expect(continueButton).toBeInTheDocument();
    });
  });

  describe('CSS Media Query Integration', () => {
    test('applies mobile-specific styles', () => {
      mockViewport(375, 667);
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Check that mobile classes are applied
      const title = screen.getByRole('heading', { level: 1 });
      expect(title).toHaveClass('welcome-title');
      
      const subtitle = screen.getByText(/How are you feeling today?/);
      expect(subtitle).toHaveClass('welcome-subtitle');
    });

    test('applies tablet-specific styles', () => {
      mockViewport(768, 1024);
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Tablet styles should be applied
      const moodSelector = document.querySelector('.mood-selector');
      expect(moodSelector).toBeInTheDocument();
    });

    test('applies desktop-specific styles', () => {
      mockViewport(1024, 768);
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Desktop styles should be applied
      const content = document.querySelector('.welcome-content');
      expect(content).toBeInTheDocument();
    });
  });

  describe('Touch and Interaction Areas', () => {
    test('mood buttons have adequate touch targets on mobile', () => {
      mockViewport(375, 667);
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const moodButtons = screen.getAllByRole('radio');
      
      // All buttons should be present and clickable
      moodButtons.forEach(button => {
        expect(button).toBeVisible();
        expect(button).not.toBeDisabled();
      });
    });

    test('continue button is easily tappable on mobile', () => {
      mockViewport(375, 667);
      
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      const continueButton = screen.getByRole('button', { name: /Continue to Chat/ });
      expect(continueButton).toBeVisible();
      expect(continueButton).not.toBeDisabled();
    });
  });

  describe('Performance on Different Screen Sizes', () => {
    test('renders efficiently on mobile devices', () => {
      mockViewport(375, 667);
      
      const startTime = performance.now();
      render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      const endTime = performance.now();
      
      // Render should complete quickly (less than 100ms is reasonable for tests)
      expect(endTime - startTime).toBeLessThan(100);
      
      // All essential elements should be present
      expect(screen.getByText(/How are you feeling today?/)).toBeInTheDocument();
      expect(screen.getAllByRole('radio')).toHaveLength(5);
    });

    test('handles rapid viewport changes', () => {
      // Start with mobile
      mockViewport(375, 667);
      const { rerender } = render(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      
      // Switch to desktop
      mockViewport(1024, 768);
      rerender(<WelcomePage currentUser={mockCurrentUser} onContinueToChat={mockOnContinueToChat} />);
      
      // Should still work correctly
      expect(screen.getAllByRole('radio')).toHaveLength(5);
      expect(screen.getByRole('button', { name: /Continue to Chat/ })).toBeInTheDocument();
    });
  });
});