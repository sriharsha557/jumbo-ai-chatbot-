-- ============================================
-- MOOD ENTRIES TABLE MIGRATION
-- ============================================
-- This creates a new mood_entries table for the Welcome Page mood tracking feature
-- It's separate from the existing mood_history table which is used for AI mood detection

CREATE TABLE IF NOT EXISTS mood_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  
  -- Mood data (standardized for Welcome Page)
  mood_type TEXT NOT NULL CHECK (mood_type IN ('very_sad', 'sad', 'neutral', 'happy', 'very_happy')),
  mood_numeric INTEGER NOT NULL CHECK (mood_numeric >= 1 AND mood_numeric <= 5),
  
  -- Timing and context
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  session_id TEXT, -- Optional session identifier
  notes TEXT DEFAULT '', -- Optional user notes
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_mood_entries_user_id ON mood_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_entries_timestamp ON mood_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_mood_entries_user_timestamp ON mood_entries(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_mood_entries_session ON mood_entries(session_id) WHERE session_id IS NOT NULL;

-- Add RLS (Row Level Security) policies
ALTER TABLE mood_entries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own mood entries
CREATE POLICY "Users can view own mood entries" ON mood_entries
  FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own mood entries
CREATE POLICY "Users can insert own mood entries" ON mood_entries
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own mood entries
CREATE POLICY "Users can update own mood entries" ON mood_entries
  FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can delete their own mood entries
CREATE POLICY "Users can delete own mood entries" ON mood_entries
  FOR DELETE USING (auth.uid() = user_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_mood_entries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER mood_entries_updated_at
  BEFORE UPDATE ON mood_entries
  FOR EACH ROW
  EXECUTE FUNCTION update_mood_entries_updated_at();

-- Add some helpful views for analytics
CREATE OR REPLACE VIEW mood_entries_daily_summary AS
SELECT 
  user_id,
  DATE(timestamp) as date,
  COUNT(*) as entry_count,
  AVG(mood_numeric) as average_mood,
  MIN(mood_numeric) as min_mood,
  MAX(mood_numeric) as max_mood,
  ARRAY_AGG(mood_type ORDER BY timestamp) as mood_types
FROM mood_entries
GROUP BY user_id, DATE(timestamp)
ORDER BY user_id, date DESC;

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON mood_entries TO authenticated;
GRANT SELECT ON mood_entries_daily_summary TO authenticated;