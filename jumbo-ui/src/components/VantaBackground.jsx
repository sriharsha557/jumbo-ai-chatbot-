import React, { useEffect, useRef, useState } from 'react';

const VantaBackground = ({ 
  children, 
  effect = 'HALO',
  options = {},
  style = {} 
}) => {
  const vantaRef = useRef(null);
  const [vantaEffect, setVantaEffect] = useState(null);

  useEffect(() => {
    if (!vantaEffect && window.VANTA && window.THREE) {
      const defaultOptions = {
        el: vantaRef.current,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        // HALO specific options
        baseColor: 0x3b82f6,
        backgroundColor: 0x1e40af,
        amplitudeFactor: 1.0,
        xOffset: 0.0,
        yOffset: 0.0,
        size: 1.0,
        ...options
      };

      try {
        const effect = window.VANTA[effect](defaultOptions);
        setVantaEffect(effect);
      } catch (error) {
        console.warn('Vanta.js effect failed to initialize:', error);
      }
    }

    return () => {
      if (vantaEffect) {
        vantaEffect.destroy();
      }
    };
  }, [vantaEffect, effect, options]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (vantaEffect) {
        vantaEffect.destroy();
      }
    };
  }, [vantaEffect]);

  const containerStyle = {
    position: 'relative',
    width: '100%',
    height: '100%',
    minHeight: '100vh',
    ...style
  };

  const contentStyle = {
    position: 'relative',
    zIndex: 1,
    width: '100%',
    height: '100%',
  };

  return (
    <div ref={vantaRef} style={containerStyle}>
      <div style={contentStyle}>
        {children}
      </div>
    </div>
  );
};

export default VantaBackground;