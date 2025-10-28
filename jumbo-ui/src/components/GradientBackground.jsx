import React from 'react';

const GradientBackground = ({ 
  children, 
  variant = 'default',
  animated = true,
  hasNavigation = false,
  style = {} 
}) => {
  const gradientVariants = {
    default: {
      background: `
        linear-gradient(135deg, 
          #0f172a 0%,
          #1e293b 15%,
          #334155 30%,
          #0ea5e9 60%,
          #38bdf8 80%,
          #7dd3fc 100%
        )
      `,
    },
    copilot: {
      background: `
        linear-gradient(135deg, 
          #0c1426 0%,
          #1a2332 20%,
          #2d3748 40%,
          #0369a1 70%,
          #0284c7 85%,
          #0ea5e9 100%
        )
      `,
    },
    ocean: {
      background: `
        linear-gradient(135deg, 
          #1e3a8a 0%,
          #1e40af 25%,
          #3b82f6 50%,
          #60a5fa 75%,
          #93c5fd 100%
        )
      `,
    },
    deep: {
      background: `
        linear-gradient(135deg, 
          #0f172a 0%,
          #1e293b 20%,
          #0f4c75 40%,
          #3282b8 60%,
          #0f4c75 80%,
          #1e293b 100%
        )
      `,
    }
  };

  const containerStyle = {
    position: 'relative',
    width: '100%',
    minHeight: '100vh',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: hasNavigation ? '72px' : '0', // Account for fixed navigation only when needed
    boxSizing: 'border-box',
    ...gradientVariants[variant],
    backgroundSize: animated ? '400% 400%' : '100% 100%',
    animation: animated ? 'gradientShift 15s ease infinite' : 'none',
    ...style
  };

  const overlayStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `
      radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%)
    `,
    pointerEvents: 'none',
  };

  const contentStyle = {
    position: 'relative',
    zIndex: 1,
    width: '100%',
    maxWidth: '1200px', // Prevent content from being too wide
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto', // Ensure horizontal centering
  };

  return (
    <>
      <style>{`
        @keyframes gradientShift {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
        
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
          }
        }
        
        .floating-orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(40px);
          animation: float 6s ease-in-out infinite;
          pointer-events: none;
        }
        
        .orb-1 {
          width: 200px;
          height: 200px;
          background: rgba(59, 130, 246, 0.4);
          top: 10%;
          left: 10%;
          animation-delay: 0s;
        }
        
        .orb-2 {
          width: 150px;
          height: 150px;
          background: rgba(147, 197, 253, 0.3);
          top: 60%;
          right: 10%;
          animation-delay: 2s;
        }
        
        .orb-3 {
          width: 100px;
          height: 100px;
          background: rgba(14, 165, 233, 0.5);
          bottom: 20%;
          left: 50%;
          animation-delay: 4s;
        }
      `}</style>
      
      <div style={containerStyle}>
        {/* Overlay effects */}
        <div style={overlayStyle} />
        
        {/* Floating orbs for extra depth */}
        {animated && (
          <>
            <div className="floating-orb orb-1" />
            <div className="floating-orb orb-2" />
            <div className="floating-orb orb-3" />
          </>
        )}
        
        {/* Content */}
        <div style={contentStyle}>
          {children}
        </div>
      </div>
    </>
  );
};

export default GradientBackground;