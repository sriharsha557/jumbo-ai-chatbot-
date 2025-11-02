import React, { useState, useEffect } from 'react';
import { theme } from '../theme/theme';

const MoodTrend = ({ currentUser, days = 7 }) => {
  // Add CSS for animations
  React.useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);
  const [moodData, setMoodData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Mood type to color mapping
  const moodColors = {
    very_sad: '#ef4444',
    sad: '#f97316',
    neutral: '#eab308',
    happy: '#84cc16',
    very_happy: '#10b981'
  };

  // Mood type to emoji mapping
  const moodEmojis = {
    very_sad: '😢',
    sad: '🙁',
    neutral: '😐',
    happy: '🙂',
    very_happy: '😀'
  };

  // Mood type to numeric value
  const moodToNumeric = {
    very_sad: 1,
    sad: 2,
    neutral: 3,
    happy: 4,
    very_happy: 5
  };

  useEffect(() => {
    fetchMoodHistory();
  }, [currentUser, days]);

  const fetchMoodHistory = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // First try to get data from API
      const apiUrl = process.env.REACT_APP_API_URL || (() => {
        if (process.env.NODE_ENV === 'production') {
          console.error('❌ REACT_APP_API_URL not set in production!');
          throw new Error('API_URL not configured for production');
        }
        return 'http://localhost:5000/api/v1';
      })();

      const headers = { 'Content-Type': 'application/json' };
      
      // Add Authorization header if available
      if (currentUser.access_token) {
        headers['Authorization'] = `Bearer ${currentUser.access_token}`;
        console.log('🔑 Using access token for mood history API');
      } else {
        console.warn('⚠️ No access token available for mood history API');
      }
      
      console.log('🌐 Fetching mood history from:', `${apiUrl}/mood/history?days=${days}&limit=50`);

      const response = await fetch(`${apiUrl}/mood/history?days=${days}&limit=50`, {
        method: 'GET',
        headers
      });
      
      console.log('📡 Mood history API response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          processMoodData(data.mood_history);
          return;
        }
      }
      
      // Fallback to localStorage if API fails
      console.warn('API failed, using localStorage fallback');
      const localMoodHistory = JSON.parse(localStorage.getItem('jumbo_mood_history') || '[]');
      processMoodData(localMoodHistory);

    } catch (error) {
      console.warn('Error fetching mood history:', error);
      // Fallback to localStorage
      try {
        const localMoodHistory = JSON.parse(localStorage.getItem('jumbo_mood_history') || '[]');
        processMoodData(localMoodHistory);
      } catch (localError) {
        console.error('Error reading local mood history:', localError);
        setError('Unable to load mood history');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const processMoodData = (rawMoodData) => {
    // Create array of last N days
    const today = new Date();
    const daysArray = [];
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      daysArray.push({
        date: date.toISOString().split('T')[0],
        dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
        moods: [],
        averageMood: null,
        dominantMood: null
      });
    }

    // Group mood entries by date
    rawMoodData.forEach(entry => {
      const entryDate = new Date(entry.timestamp).toISOString().split('T')[0];
      const dayData = daysArray.find(day => day.date === entryDate);
      
      if (dayData) {
        dayData.moods.push({
          mood_type: entry.mood_type,
          mood_numeric: entry.mood_numeric || moodToNumeric[entry.mood_type],
          timestamp: entry.timestamp
        });
      }
    });

    // Calculate averages and dominant moods
    daysArray.forEach(day => {
      if (day.moods.length > 0) {
        // Calculate average mood
        const sum = day.moods.reduce((acc, mood) => acc + mood.mood_numeric, 0);
        day.averageMood = sum / day.moods.length;

        // Find dominant mood (most frequent)
        const moodCounts = {};
        day.moods.forEach(mood => {
          moodCounts[mood.mood_type] = (moodCounts[mood.mood_type] || 0) + 1;
        });
        
        day.dominantMood = Object.keys(moodCounts).reduce((a, b) => 
          moodCounts[a] > moodCounts[b] ? a : b
        );
      }
    });

    setMoodData(daysArray);
  };

  const getBarHeight = (averageMood) => {
    if (!averageMood) return 0;
    return (averageMood / 5) * 100; // Convert to percentage
  };

  const getBarColor = (averageMood) => {
    if (!averageMood) return '#e5e7eb';
    
    // Color based on mood level
    if (averageMood >= 4.5) return moodColors.very_happy;
    if (averageMood >= 3.5) return moodColors.happy;
    if (averageMood >= 2.5) return moodColors.neutral;
    if (averageMood >= 1.5) return moodColors.sad;
    return moodColors.very_sad;
  };

  if (isLoading) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h3 style={styles.title}>Your Mood This Week</h3>
        </div>
        <div style={styles.loadingContainer}>
          <div style={styles.loadingSpinner}></div>
          <p style={styles.loadingText}>Loading mood history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h3 style={styles.title}>Your Mood This Week</h3>
        </div>
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
        </div>
      </div>
    );
  }

  const hasAnyMoodData = moodData.some(day => day.moods.length > 0);

  if (!hasAnyMoodData) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h3 style={styles.title}>Your Mood This Week</h3>
        </div>
        <div style={styles.emptyContainer}>
          <p style={styles.emptyText}>Start tracking your mood to see trends here! 📊</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Your Mood This Week</h3>
        <p style={styles.subtitle}>Track your emotional journey</p>
      </div>
      
      <div style={styles.chartContainer}>
        <div style={styles.chart}>
          {moodData.map((day, index) => (
            <div key={day.date} style={styles.dayColumn}>
              <div style={styles.barContainer}>
                <div
                  style={{
                    ...styles.bar,
                    height: `${getBarHeight(day.averageMood)}%`,
                    backgroundColor: getBarColor(day.averageMood),
                  }}
                  title={day.averageMood ? 
                    `${day.dayName}: ${day.averageMood.toFixed(1)}/5 (${day.moods.length} entries)` : 
                    `${day.dayName}: No data`
                  }
                />
              </div>
              
              <div style={styles.dayLabel}>
                <span style={styles.dayName}>{day.dayName}</span>
                {day.dominantMood && (
                  <span style={styles.dayEmoji}>
                    {moodEmojis[day.dominantMood]}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div style={styles.yAxis}>
          <span style={styles.yAxisLabel}>😀</span>
          <span style={styles.yAxisLabel}>😐</span>
          <span style={styles.yAxisLabel}>😢</span>
        </div>
      </div>

      <div style={styles.legend}>
        <div style={styles.legendItem}>
          <div style={{...styles.legendColor, backgroundColor: moodColors.very_happy}}></div>
          <span style={styles.legendText}>Very Happy</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendColor, backgroundColor: moodColors.happy}}></div>
          <span style={styles.legendText}>Happy</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendColor, backgroundColor: moodColors.neutral}}></div>
          <span style={styles.legendText}>Neutral</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendColor, backgroundColor: moodColors.sad}}></div>
          <span style={styles.legendText}>Sad</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{...styles.legendColor, backgroundColor: moodColors.very_sad}}></div>
          <span style={styles.legendText}>Very Sad</span>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    borderRadius: '20px',
    padding: '24px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
    width: '100%',
    maxWidth: '500px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'white',
    margin: '0 0 8px 0',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  subtitle: {
    fontSize: '0.9rem',
    color: 'rgba(255, 255, 255, 0.7)',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  chartContainer: {
    position: 'relative',
    display: 'flex',
    alignItems: 'flex-end',
    marginBottom: '20px',
  },
  chart: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    height: '120px',
    flex: 1,
    padding: '0 10px',
  },
  dayColumn: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    flex: 1,
    maxWidth: '50px',
  },
  barContainer: {
    height: '80px',
    width: '24px',
    display: 'flex',
    alignItems: 'flex-end',
    marginBottom: '8px',
  },
  bar: {
    width: '100%',
    minHeight: '2px',
    borderRadius: '12px 12px 0 0',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
  },
  dayLabel: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
  },
  dayName: {
    fontSize: '0.75rem',
    color: 'rgba(255, 255, 255, 0.8)',
    fontWeight: '500',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  dayEmoji: {
    fontSize: '0.9rem',
  },
  yAxis: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    height: '80px',
    marginLeft: '10px',
    paddingBottom: '8px',
  },
  yAxisLabel: {
    fontSize: '0.8rem',
    color: 'rgba(255, 255, 255, 0.6)',
  },
  legend: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '12px',
    justifyContent: 'center',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  legendColor: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
  },
  legendText: {
    fontSize: '0.75rem',
    color: 'rgba(255, 255, 255, 0.8)',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '40px 20px',
  },
  loadingSpinner: {
    width: '32px',
    height: '32px',
    border: '3px solid rgba(255, 255, 255, 0.3)',
    borderTop: '3px solid white',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px',
  },
  loadingText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '0.9rem',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  errorContainer: {
    padding: '20px',
    textAlign: 'center',
  },
  errorText: {
    color: '#fca5a5',
    fontSize: '0.9rem',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  emptyContainer: {
    padding: '40px 20px',
    textAlign: 'center',
  },
  emptyText: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '0.95rem',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
};

export default MoodTrend;