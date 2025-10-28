// Jumbo UI Theme System - Blue Gradient Theme
// Comprehensive styling for a modern chatbot interface

export const theme = {
    // ==================== COLOR PALETTE ====================
    colors: {
        // Primary blue gradient theme
        primary: {
            50: '#eff6ff',
            100: '#dbeafe',
            200: '#bfdbfe',
            300: '#93c5fd',
            400: '#60a5fa',
            500: '#3b82f6',
            600: '#2563eb',
            700: '#1d4ed8',
            800: '#1e40af',
            900: '#1e3a8a',
            950: '#172554'
        },

        // Secondary colors
        secondary: {
            50: '#f8fafc',
            100: '#f1f5f9',
            200: '#e2e8f0',
            300: '#cbd5e1',
            400: '#94a3b8',
            500: '#64748b',
            600: '#475569',
            700: '#334155',
            800: '#1e293b',
            900: '#0f172a'
        },

        // Accent colors for mood states
        accent: {
            happy: '#10b981',
            excited: '#f59e0b',
            calm: '#6366f1',
            sad: '#8b5cf6',
            angry: '#ef4444',
            neutral: '#6b7280'
        },

        // Semantic colors
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',

        // Background variations
        background: {
            primary: '#ffffff',
            secondary: '#f8fafc',
            tertiary: '#f1f5f9',
            dark: '#0f172a',
            gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        },

        // Text colors
        text: {
            primary: '#1e293b',
            secondary: '#475569',
            tertiary: '#64748b',
            inverse: '#ffffff',
            muted: '#94a3b8'
        },

        // Border colors
        border: {
            light: '#e2e8f0',
            medium: '#cbd5e1',
            dark: '#94a3b8'
        }
    },

    // ==================== TYPOGRAPHY ====================
    typography: {
        fontFamily: {
            sans: ['Inter', 'system-ui', 'sans-serif'],
            mono: ['JetBrains Mono', 'Consolas', 'monospace'],
            display: ['Poppins', 'Inter', 'sans-serif'],
            briskey: ['Briskey', 'Bricolage Grotesque', 'Kalam', 'sans-serif'],
            humanistic: ['Comfortaa', 'Nunito', 'Quicksand', 'Poppins', 'sans-serif']
        },

        fontSize: {
            xs: '0.75rem',     // 12px
            sm: '0.875rem',    // 14px
            base: '1rem',      // 16px
            lg: '1.125rem',    // 18px
            xl: '1.25rem',     // 20px
            '2xl': '1.5rem',   // 24px
            '3xl': '1.875rem', // 30px
            '4xl': '2.25rem',  // 36px
            '5xl': '3rem',     // 48px
        },

        fontWeight: {
            light: '300',
            normal: '400',
            medium: '500',
            semibold: '600',
            bold: '700',
            extrabold: '800'
        },

        lineHeight: {
            tight: '1.25',
            normal: '1.5',
            relaxed: '1.75'
        }
    },

    // ==================== SPACING ====================
    spacing: {
        0: '0',
        1: '0.25rem',   // 4px
        2: '0.5rem',    // 8px
        3: '0.75rem',   // 12px
        4: '1rem',      // 16px
        5: '1.25rem',   // 20px
        6: '1.5rem',    // 24px
        8: '2rem',      // 32px
        10: '2.5rem',   // 40px
        12: '3rem',     // 48px
        16: '4rem',     // 64px
        20: '5rem',     // 80px
        24: '6rem',     // 96px
        32: '8rem',     // 128px
    },

    // ==================== BORDER RADIUS ====================
    borderRadius: {
        none: '0',
        sm: '0.125rem',   // 2px
        base: '0.25rem',  // 4px
        md: '0.375rem',   // 6px
        lg: '0.5rem',     // 8px
        xl: '0.75rem',    // 12px
        '2xl': '1rem',    // 16px
        '3xl': '1.5rem',  // 24px
        full: '9999px'
    },

    // ==================== SHADOWS ====================
    shadows: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        glow: '0 0 20px rgb(59 130 246 / 0.3)'
    },

    // ==================== ANIMATIONS ====================
    animations: {
        duration: {
            fast: '150ms',
            normal: '300ms',
            slow: '500ms'
        },

        easing: {
            linear: 'linear',
            easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
            easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
            easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)'
        },

        keyframes: {
            fadeIn: {
                from: { opacity: 0 },
                to: { opacity: 1 }
            },
            slideUp: {
                from: { transform: 'translateY(10px)', opacity: 0 },
                to: { transform: 'translateY(0)', opacity: 1 }
            },
            pulse: {
                '0%, 100%': { opacity: 1 },
                '50%': { opacity: 0.5 }
            },
            bounce: {
                '0%, 100%': { transform: 'translateY(-25%)', animationTimingFunction: 'cubic-bezier(0.8, 0, 1, 1)' },
                '50%': { transform: 'translateY(0)', animationTimingFunction: 'cubic-bezier(0, 0, 0.2, 1)' }
            }
        }
    },

    // ==================== COMPONENT STYLES ====================
    components: {
        // Button variants
        button: {
            primary: {
                backgroundColor: '#3b82f6',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0.5rem',
                padding: '0.75rem 1.5rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 150ms ease',
                boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                ':hover': {
                    backgroundColor: '#2563eb',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                },
                ':active': {
                    backgroundColor: '#1d4ed8',
                    transform: 'translateY(1px)'
                },
                ':disabled': {
                    backgroundColor: '#94a3b8',
                    cursor: 'not-allowed'
                }
            },

            secondary: {
                backgroundColor: 'transparent',
                color: '#3b82f6',
                border: '1px solid #3b82f6',
                borderRadius: '0.5rem',
                padding: '0.75rem 1.5rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 150ms ease',
                ':hover': {
                    backgroundColor: '#3b82f6',
                    color: '#ffffff'
                }
            },

            ghost: {
                backgroundColor: 'transparent',
                color: '#64748b',
                border: 'none',
                borderRadius: '0.5rem',
                padding: '0.75rem 1.5rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 150ms ease',
                ':hover': {
                    backgroundColor: '#f1f5f9',
                    color: '#1e293b'
                }
            }
        },

        // Input styles
        input: {
            base: {
                width: '100%',
                padding: '0.75rem 1rem',
                border: '1px solid #e2e8f0',
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
                backgroundColor: '#ffffff',
                transition: 'all 150ms ease',
                ':focus': {
                    outline: 'none',
                    borderColor: '#3b82f6',
                    boxShadow: '0 0 0 3px rgb(59 130 246 / 0.1)'
                },
                ':disabled': {
                    backgroundColor: '#f8fafc',
                    color: '#94a3b8',
                    cursor: 'not-allowed'
                }
            }
        },

        // Card styles
        card: {
            base: {
                backgroundColor: '#ffffff',
                borderRadius: '0.75rem',
                padding: '1.5rem',
                boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
                border: '1px solid #f1f5f9'
            },

            elevated: {
                backgroundColor: '#ffffff',
                borderRadius: '0.75rem',
                padding: '1.5rem',
                boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                border: 'none'
            }
        },

        // Chat message styles
        message: {
            user: {
                backgroundColor: '#3b82f6',
                color: '#ffffff',
                borderRadius: '1rem 1rem 0.25rem 1rem',
                padding: '0.75rem 1rem',
                marginLeft: 'auto',
                maxWidth: '80%',
                fontSize: '0.875rem',
                lineHeight: '1.5'
            },

            bot: {
                backgroundColor: '#f1f5f9',
                color: '#1e293b',
                borderRadius: '1rem 1rem 1rem 0.25rem',
                padding: '0.75rem 1rem',
                marginRight: 'auto',
                maxWidth: '80%',
                fontSize: '0.875rem',
                lineHeight: '1.5'
            }
        },

        // Mood indicator styles
        mood: {
            happy: {
                backgroundColor: '#dcfce7',
                color: '#166534',
                borderLeft: '4px solid #10b981'
            },
            sad: {
                backgroundColor: '#fdf4ff',
                color: '#7c2d12',
                borderLeft: '4px solid #8b5cf6'
            },
            excited: {
                backgroundColor: '#fefbeb',
                color: '#92400e',
                borderLeft: '4px solid #f59e0b'
            },
            calm: {
                backgroundColor: '#eef2ff',
                color: '#3730a3',
                borderLeft: '4px solid #6366f1'
            },
            neutral: {
                backgroundColor: '#f8fafc',
                color: '#475569',
                borderLeft: '4px solid #6b7280'
            }
        }
    },

    // ==================== BREAKPOINTS ====================
    breakpoints: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px'
    },

    // ==================== Z-INDEX SCALE ====================
    zIndex: {
        hide: -1,
        auto: 'auto',
        base: 0,
        docked: 10,
        dropdown: 1000,
        sticky: 1100,
        banner: 1200,
        overlay: 1300,
        modal: 1400,
        popover: 1500,
        skipLink: 1600,
        toast: 1700,
        tooltip: 1800
    }
}

// ==================== THEME UTILITIES ====================

// Helper function to get nested theme values
export const getThemeValue = (path, fallback = null) => {
    return path.split('.').reduce((obj, key) => obj?.[key], theme) || fallback
}

// CSS-in-JS helper for styled components
export const css = (strings, ...values) => {
    return strings.reduce((result, string, i) => {
        const value = values[i] ? values[i] : ''
        return result + string + value
    }, '')
}

// Responsive helper
export const responsive = (styles) => {
    return Object.entries(styles).map(([breakpoint, style]) => {
        if (breakpoint === 'base') return style
        return `@media (min-width: ${theme.breakpoints[breakpoint]}) { ${style} }`
    }).join(' ')
}

// Color opacity helper
export const withOpacity = (color, opacity) => {
    return `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`
}

export default theme