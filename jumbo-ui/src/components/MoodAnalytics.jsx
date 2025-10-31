import React, { useState, useEffect } from 'react';
import { TrendingUp, Calendar, Heart, BarChart3 } from 'lucide-react';
import { theme } from '../theme/theme';

const MoodAnalytics = ({ currentUser }) => {
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  const periodOptions = [
    { value: 7, label: '7 Days' },
    { value: 30, label: '30 Days' },
    { value: 90, label: '90 Days' }
  ];

  useEffect(() => {
    fetchMoodAnalytics();
  }, [currentUser, selectedPeriod]);

  const fetchMoodAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || (() => {
        if (process.env.NODE_ENV === 'production') {
          console.error('❌ REACT_APP_API_URL not set in production!');
          throw new Error('API_URL not configured for production');
        }
        return 'http://localhost:5000/api/v1';
      })();

      const headers = { 'Content-Type': 'application/json' };
      
      if (currentUser.access_token) {
        headers['Authorization'] = `Bearer ${currentUser.access_token}`;
      }

      const response = await fetch(`${apiUrl}/mood/trends?days=${selectedPeriod}`, {
        method: 'GET',
        headers
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAnalytics(data.trends);
          return;
        }
      }
      
      // Fallback to basic analytics from localStorage
      generateBasicAnalytics();

    } catch (error) {
      console.warn('Error fetching mood analytics:', error);
      generateBasicAnalytics();
    } finally {
      setIsLoading(false);
    }
  };

  const generateBasicAnalytics = () => {
    try {
      const localMoodHistory = JSON.parse(localStorage.getItem('jumbo_mood_history') || '[]');
      
      if (localMoodHistory.length === 0) {
        setAnalytics({
          daily_averages: [],
          weekly_summary: { average_mood: 3.0, total_entries: 0 },
          mood_patterns: {},
          insights: ['Start tracking your mood to see insights here!']
        });
        return;
      }

      // Filter by selected period
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - selectedPeriod);
      
      const filteredMoods = localMoodHistory.filter(entry => 
        new Date(entry.timestamp) >= cutoffDate
      );

      // Calculate basic analytics
      const moodCounts = {};
      let totalMood = 0;
      
      filteredMoods.forEach(entry => {
        const moodType = entry.mood_type;
        moodCounts[moodType] = (moodCounts[moodType] || 0) + 1;
        totalMood += entry.mood_numeric || getMoodNumeric(moodType);
      });

      const averageMood = filteredMoods.length > 0 ? totalMood / filteredMoods.length : 3.0;

      setAnalytics({
        daily_averages: [], // Could implement if needed
        weekly_summary: {
          average_mood: averageMood,
          total_entries: filteredMoods.length
        },
        mood_patterns: moodCounts,
        insights: generateInsights(averageMood, filteredMoods.length, moodCounts),
        analysis_period: {
          days: selectedPeriod,
          total_entries: filteredMoods.length
        }
      });

    } catch (error) {
      console.error('Error generating basic analytics:', error);
      setError('Unable to generate mood analytics');
    }
  };

  const getMoodNumeric = (moodType) => {
    const mapping = { very_sad: 1, sad: 2, neutral: 3, happy: 4, very_happy: 5 };
    return mapping[moodType] || 3;
  };

  const generateInsights = (averageMood, totalEntries, moodCounts) => {
    const insights = [];

    if (totalEntries === 0) {
      return ['Start tracking your mood to see personalized insights!'];
    }

    if (averageMood >= 4) {
      insights.push('🌟 You\'ve been feeling quite positive lately!');
    } else if (averageMood <= 2) {
      insights.push('💙 You\'ve had some challenging days. Remember, it\'s okay to not be okay.');
    } else {
      insights.push('⚖️ Your mood has been fairly balanced recently.');
    }

    // Most common mood
    const mostCommonMood = Object.keys(moodCounts).reduce((a, b) => 
      moodCounts[a] > moodCounts[b] ? a : b
    );
    
    const moodLabels = {
      very_happy: 'very happy',
      happy: 'happy',
      neutral: 'neutral',
      sad: 'sad',
      very_sad: 'very sad'
    };

    insights.push(`📊 You've felt ${moodLabels[mostCommonMood]} most often this period.`);

    if (totalEntries >= 7) {
      insights.push('🎯 Great job staying consistent with mood tracking!');
    }

    return insights;
  };

  const getMoodColor = (moodType) => {
    const colors = {
      very_sad: '#ef4444',
      sad: '#f97316',
      neutral: '#eab308',
      happy: '#84cc16',
      very_happy: '#10b981'
    };
    return colors[moodType] || '#6b7280';
  };

  const getMoodEmoji = (moodType) => {
    const emojis = {
      very_sad: '😢',
      sad: '🙁',
      neutral: '😐',
      happy: '🙂',
      very_happy: '😀'
    };
    return emojis[moodType] || '😐';
  };

  if (isLoading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.loadingSpinner}></div>
          <p style={styles.loadingText}>Loading mood analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorContainer}>
          <p style={styles.errorText}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>
          <BarChart3 size={24} style={{ marginRight: '8px' }} />
          Mood Analytics
        </h2>
        
        <div style={styles.periodSelector}>
          {periodOptions.map(option => (
            <button
              key={option.value}
              onClick={() => setSelectedPeriod(option.value)}
              style={{
                ...styles.periodButton,
                ...(selectedPeriod === option.value ? styles.periodButtonActive : {})
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>
            <TrendingUp size={20} color="#10b981" />
          </div>
          <div style={styles.statContent}>
            <h3 style={styles.statValue}>
              {analytics.weekly_summary.average_mood.toFixed(1)}/5
            </h3>
            <p style={styles.statLabel}>Average Mood</p>
          </div>
        </div>

        <div style={styles.statCard}>
          <div style={styles.statIcon}>
            <Calendar size={20} color="#3b82f6" />
          </div>
          <div style={styles.statContent}>
            <h3 style={styles.statValue}>
              {analytics.weekly_summary.total_entries}
            </h3>
            <p style={styles.statLabel}>Total Entries</p>
          </div>
        </div>

        <div style={styles.statCard}>
          <div style={styles.statIcon}>
            <Heart size={20} color="#ef4444" />
          </div>
          <div style={styles.statContent}>
            <h3 style={styles.statValue}>
              {selectedPeriod} Days
            </h3>
            <p style={styles.statLabel}>Analysis Period</p>
          </div>
        </div>
      </div>

      {Object.keys(analytics.mood_patterns).length > 0 && (
        <div style={styles.patternsSection}>
          <h3 style={styles.sectionTitle}>Mood Distribution</h3>
          <div style={styles.moodPatterns}>
            {Object.entries(analytics.mood_patterns).map(([moodType, count]) => (
              <div key={moodType} style={styles.moodPattern}>
                <div style={styles.moodPatternHeader}>
                  <span style={styles.moodPatternEmoji}>
                    {getMoodEmoji(moodType)}
                  </span>
                  <span style={styles.moodPatternLabel}>
                    {moodType.replace('_', ' ')}
                  </span>
                </div>
                <div style={styles.moodPatternBar}>
                  <div
                    style={{
                      ...styles.moodPatternFill,
                      width: `${(count / analytics.weekly_summary.total_entries) * 100}%`,
                      backgroundColor: getMoodColor(moodType)
                    }}
                  />
                </div>
                <span style={styles.moodPatternCount}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={styles.insightsSection}>
        <h3 style={styles.sectionTitle}>Insights</h3>
        <div style={styles.insights}>
          {analytics.insights.map((insight, index) => (
            <div key={index} style={styles.insight}>
              <p style={styles.insightText}>{insight}</p>
            </div>
          ))}
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
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
    flexWrap: 'wrap',
    gap: '16px',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'white',
    margin: 0,
    display: 'flex',
    alignItems: 'center',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  periodSelector: {
    display: 'flex',
    gap: '8px',
  },
  periodButton: {
    padding: '6px 12px',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '8px',
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '0.8rem',
    cursor: 'pointer',
    transition: 'all 0.3s',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  periodButtonActive: {
    background: 'rgba(59, 130, 246, 0.3)',
    borderColor: 'rgba(59, 130, 246, 0.5)',
    color: 'white',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '16px',
    marginBottom: '24px',
  },
  statCard: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '12px',
    padding: '16px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  statIcon: {
    width: '40px',
    height: '40px',
    borderRadius: '8px',
    background: 'rgba(255, 255, 255, 0.1)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  statContent: {
    flex: 1,
  },
  statValue: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'white',
    margin: '0 0 4px 0',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  statLabel: {
    fontSize: '0.8rem',
    color: 'rgba(255, 255, 255, 0.7)',
    margin: 0,
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  patternsSection: {
    marginBottom: '24px',
  },
  sectionTitle: {
    fontSize: '1.1rem',
    fontWeight: '600',
    color: 'white',
    marginBottom: '16px',
    fontFamily: theme.typography?.fontFamily?.briskey?.join(', ') || 'Bricolage Grotesque, sans-serif',
  },
  moodPatterns: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  moodPattern: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  moodPatternHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    minWidth: '120px',
  },
  moodPatternEmoji: {
    fontSize: '1.1rem',
  },
  moodPatternLabel: {
    fontSize: '0.9rem',
    color: 'rgba(255, 255, 255, 0.8)',
    textTransform: 'capitalize',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  moodPatternBar: {
    flex: 1,
    height: '8px',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  moodPatternFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.5s ease',
  },
  moodPatternCount: {
    fontSize: '0.8rem',
    color: 'rgba(255, 255, 255, 0.7)',
    minWidth: '20px',
    textAlign: 'right',
    fontFamily: theme.typography?.fontFamily?.humanistic?.join(', ') || 'Comfortaa, sans-serif',
  },
  insightsSection: {
    marginBottom: '0',
  },
  insights: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  insight: {
    background: 'rgba(59, 130, 246, 0.1)',
    border: '1px solid rgba(59, 130, 246, 0.2)',
    borderRadius: '12px',
    padding: '16px',
  },
  insightText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '0.9rem',
    margin: 0,
    lineHeight: '1.5',
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
};

export default MoodAnalytics;