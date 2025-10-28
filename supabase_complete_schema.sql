-- ============================================
-- JUMBO EMOTIONAL AI - COMPLETE DATABASE SCHEMA
-- ============================================
-- Complete schema with onboarding system integrated
-- Use this for fresh Supabase setup or reference

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For similarity search

-- ============================================
-- 1. ENHANCED USER PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
  -- Core user fields
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  preferred_name TEXT, -- What the user wants to be called in chat
  language TEXT DEFAULT 'en' CHECK (language IN ('en', 'te', 'hi')),
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_active TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb,
  
  -- ONBOARDING SYSTEM FIELDS
  onboarding_completed BOOLEAN DEFAULT FALSE,
  onboarding_data JSONB DEFAULT '{}'::jsonb,
  
  -- Step 2: Personal Information
  display_name TEXT, -- User's chosen display name
  pronouns TEXT CHECK (pronouns IN ('he/him', 'she/her', 'they/them', 'prefer_not_to_say')),
  preferred_language TEXT DEFAULT 'en' CHECK (preferred_language IN ('en', 'hi', 'other')),
  
  -- Step 3: Emotional Baseline
  current_mood INTEGER CHECK (current_mood >= 1 AND current_mood <= 5), -- 1=😞 to 5=😄
  emotion_comfort_level TEXT CHECK (emotion_comfort_level IN ('easy', 'sometimes', 'difficult')),
  
  -- Step 4: Support Style
  support_style TEXT CHECK (support_style IN ('calm_comforting', 'honest_real', 'motivational', 'fun_distraction')),
  communication_tone TEXT CHECK (communication_tone IN ('calm', 'cheerful', 'deep', 'friendly')),
  
  -- Step 5: Focus Areas (up to 3 selections)
  focus_areas TEXT[] CHECK (array_length(focus_areas, 1) <= 3),
  
  -- Step 6: Check-in Preferences
  checkin_frequency TEXT CHECK (checkin_frequency IN ('daily', 'few_times_week', 'on_demand')),
  checkin_time TEXT CHECK (checkin_time IN ('morning', 'evening', 'custom')),
  custom_checkin_time TIME,
  
  -- Step 7: Privacy acknowledgment (stored in onboarding_data)
  
  CONSTRAINT unique_name_per_user UNIQUE(name)
);

-- ============================================
-- 2. CONVERSATIONS TABLE (Enhanced)
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  user_message TEXT NOT NULL,
  bot_response TEXT NOT NULL,
  
  -- Emotion detection data
  user_emotion TEXT, -- Detected emotion from user message
  user_emotion_confidence FLOAT DEFAULT 0.0,
  
  -- Legacy mood fields (keep for compatibility)
  mood TEXT DEFAULT 'neutral',
  mood_confidence FLOAT DEFAULT 0.0,
  
  -- AI processing metadata
  detected_language TEXT DEFAULT 'en',
  used_llm BOOLEAN DEFAULT FALSE,
  scenario TEXT,
  response_type TEXT DEFAULT 'text',
  
  -- Personalization data
  personality_enhanced BOOLEAN DEFAULT FALSE,
  support_style_used TEXT,
  communication_tone_used TEXT,
  
  -- Complete metadata
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. USER MEMORIES TABLE (Enhanced)
-- ============================================
CREATE TABLE IF NOT EXISTS user_memories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  
  -- Memory classification
  memory_type TEXT NOT NULL CHECK (memory_type IN ('person', 'preference', 'event', 'topic', 'fact', 'emotion', 'goal')),
  category TEXT, -- 'friend', 'family', 'food', 'music', 'work', 'hobby', etc.
  
  -- Memory content
  fact TEXT NOT NULL, -- The actual memory/fact to remember
  name TEXT, -- Name of person/thing (if applicable)
  relationship TEXT, -- 'friend', 'brother', 'colleague', etc.
  
  -- Memory reliability and importance
  importance_score FLOAT DEFAULT 1.0 CHECK (importance_score >= 0.1 AND importance_score <= 1.0),
  confidence_score FLOAT DEFAULT 1.0 CHECK (confidence_score >= 0.1 AND confidence_score <= 1.0),
  
  -- Memory lifecycle
  is_active BOOLEAN DEFAULT true,
  duplicate_of UUID REFERENCES user_memories(id),
  version INTEGER DEFAULT 1,
  
  -- Source tracking
  source_conversation_id UUID REFERENCES conversations(id),
  
  -- Structured data
  data JSONB NOT NULL DEFAULT '{}'::jsonb,
  
  -- Vector embeddings (for future semantic search)
  embedding vector(1536), -- OpenAI embedding size
  embedding_model TEXT DEFAULT 'text-embedding-ada-002',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 4. MOOD HISTORY TABLE (Enhanced)
-- ============================================
CREATE TABLE IF NOT EXISTS mood_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  
  -- Mood data
  mood TEXT NOT NULL,
  confidence FLOAT DEFAULT 0.0,
  intensity INTEGER CHECK (intensity >= 1 AND intensity <= 5), -- 1-5 scale
  
  -- Context
  context TEXT, -- What triggered this mood
  conversation_id UUID REFERENCES conversations(id), -- Link to conversation
  
  -- Metadata
  detection_method TEXT DEFAULT 'ml_transformer', -- How mood was detected
  metadata JSONB DEFAULT '{}'::jsonb,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 5. ONBOARDING SESSIONS TABLE (Optional)
-- ============================================
CREATE TABLE IF NOT EXISTS onboarding_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  
  -- Session tracking
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  current_step INTEGER DEFAULT 1,
  total_steps INTEGER DEFAULT 7,
  
  -- Step completion tracking
  steps_completed INTEGER[] DEFAULT '{}',
  step_data JSONB DEFAULT '{}'::jsonb,
  
  -- Session metadata
  user_agent TEXT,
  ip_address INET,
  completion_time_seconds INTEGER,
  
  CONSTRAINT valid_current_step CHECK (current_step >= 1 AND current_step <= total_steps)
);

-- ============================================
-- OPTIMIZED INDEXES FOR PERFORMANCE
-- ============================================

-- Profiles indexes
CREATE INDEX IF NOT EXISTS idx_profiles_onboarding_status ON profiles(onboarding_completed);
CREATE INDEX IF NOT EXISTS idx_profiles_last_active ON profiles(last_active DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_support_style ON profiles(support_style) WHERE support_style IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_profiles_focus_areas ON profiles USING gin(focus_areas) WHERE focus_areas IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_profiles_checkin ON profiles(checkin_frequency, checkin_time) WHERE checkin_frequency IS NOT NULL;

-- Conversations indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_date ON conversations(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_emotion ON conversations(user_id, user_emotion) WHERE user_emotion IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_conversations_personality ON conversations(user_id, personality_enhanced) WHERE personality_enhanced = true;
CREATE INDEX IF NOT EXISTS idx_conversations_metadata ON conversations USING gin(metadata);

-- Memories indexes
CREATE INDEX IF NOT EXISTS idx_memories_user_type ON user_memories(user_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_active ON user_memories(user_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_memories_importance ON user_memories(user_id, importance_score DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_memories_updated ON user_memories(user_id, updated_at DESC);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_memories_fact_search ON user_memories USING gin(to_tsvector('english', fact)) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_memories_name_search ON user_memories USING gin(to_tsvector('english', name)) WHERE is_active = true AND name IS NOT NULL;

-- Mood history indexes
CREATE INDEX IF NOT EXISTS idx_mood_history_user_date ON mood_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_mood_history_mood ON mood_history(user_id, mood);

-- Onboarding sessions indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user ON onboarding_sessions(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_completion ON onboarding_sessions(completed_at) WHERE completed_at IS NOT NULL;

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE mood_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;

-- PROFILES POLICIES
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- CONVERSATIONS POLICIES
DROP POLICY IF EXISTS "Users can view own conversations" ON conversations;
CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own conversations" ON conversations;
CREATE POLICY "Users can insert own conversations"
  ON conversations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- MEMORIES POLICIES
DROP POLICY IF EXISTS "Users can view own memories" ON user_memories;
CREATE POLICY "Users can view own memories"
  ON user_memories FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own memories" ON user_memories;
CREATE POLICY "Users can manage own memories"
  ON user_memories FOR ALL
  USING (auth.uid() = user_id);

-- MOOD HISTORY POLICIES
DROP POLICY IF EXISTS "Users can view own mood history" ON mood_history;
CREATE POLICY "Users can view own mood history"
  ON mood_history FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own mood history" ON mood_history;
CREATE POLICY "Users can insert own mood history"
  ON mood_history FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ONBOARDING SESSIONS POLICIES
DROP POLICY IF EXISTS "Users can manage own onboarding sessions" ON onboarding_sessions;
CREATE POLICY "Users can manage own onboarding sessions"
  ON onboarding_sessions FOR ALL
  USING (auth.uid() = user_id);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get user onboarding progress
CREATE OR REPLACE FUNCTION get_onboarding_progress(p_user_id UUID)
RETURNS TABLE(
  step_number INTEGER,
  step_name TEXT,
  completed BOOLEAN,
  data JSONB
) AS $$
BEGIN
  RETURN QUERY
  WITH onboarding_steps AS (
    SELECT * FROM (VALUES
      (1, 'welcome', 'welcome_seen'),
      (2, 'personal_info', 'personal_info'),
      (3, 'emotional_baseline', 'emotional_baseline'),
      (4, 'support_style', 'support_style'),
      (5, 'focus_areas', 'focus_areas'),
      (6, 'checkin_preferences', 'checkin_preferences'),
      (7, 'privacy_note', 'privacy_acknowledged')
    ) AS t(step_num, step_name, data_key)
  ),
  user_data AS (
    SELECT onboarding_data FROM profiles WHERE id = p_user_id
  )
  SELECT 
    os.step_num,
    os.step_name,
    (ud.onboarding_data ? os.data_key) as completed,
    COALESCE(ud.onboarding_data -> os.data_key, '{}'::jsonb) as data
  FROM onboarding_steps os
  CROSS JOIN user_data ud
  ORDER BY os.step_num;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to complete onboarding
CREATE OR REPLACE FUNCTION complete_user_onboarding(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  steps_completed INTEGER;
BEGIN
  -- Check if all steps are completed
  SELECT COUNT(*) INTO steps_completed
  FROM get_onboarding_progress(p_user_id)
  WHERE completed = true;
  
  -- If all 7 steps completed, mark onboarding as done
  IF steps_completed >= 7 THEN
    UPDATE profiles 
    SET onboarding_completed = true
    WHERE id = p_user_id;
    RETURN true;
  END IF;
  
  RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get personalized AI settings
CREATE OR REPLACE FUNCTION get_ai_personalization(p_user_id UUID)
RETURNS TABLE(
  display_name TEXT,
  pronouns TEXT,
  support_style TEXT,
  communication_tone TEXT,
  focus_areas TEXT[],
  emotion_comfort_level TEXT,
  current_mood INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.display_name,
    p.pronouns,
    p.support_style,
    p.communication_tone,
    p.focus_areas,
    p.emotion_comfort_level,
    p.current_mood
  FROM profiles p
  WHERE p.id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- ENHANCED VIEWS FOR MONITORING
-- ============================================

-- View: Onboarding completion stats
CREATE OR REPLACE VIEW onboarding_stats AS
SELECT 
  COUNT(*) as total_users,
  COUNT(*) FILTER (WHERE onboarding_completed = true) as completed_onboarding,
  COUNT(*) FILTER (WHERE onboarding_completed = false) as pending_onboarding,
  ROUND(
    (COUNT(*) FILTER (WHERE onboarding_completed = true)::FLOAT / COUNT(*)) * 100, 
    2
  ) as completion_rate_percent,
  
  -- Step completion breakdown
  COUNT(*) FILTER (WHERE onboarding_data ? 'welcome_seen') as step1_completed,
  COUNT(*) FILTER (WHERE onboarding_data ? 'personal_info') as step2_completed,
  COUNT(*) FILTER (WHERE onboarding_data ? 'emotional_baseline') as step3_completed,
  COUNT(*) FILTER (WHERE onboarding_data ? 'support_style') as step4_completed,
  COUNT(*) FILTER (WHERE onboarding_data ? 'focus_areas') as step5_completed,
  COUNT(*) FILTER (WHERE onboarding_data ? 'checkin_preferences') as step6_completed,
  COUNT(*) FILTER (WHERE onboarding_data ? 'privacy_acknowledged') as step7_completed
FROM profiles;

-- View: User personalization summary
CREATE OR REPLACE VIEW user_personalization AS
SELECT 
  id,
  name,
  display_name,
  pronouns,
  support_style,
  communication_tone,
  focus_areas,
  emotion_comfort_level,
  current_mood,
  onboarding_completed,
  created_at
FROM profiles
WHERE onboarding_completed = true;

-- View: Focus areas popularity
CREATE OR REPLACE VIEW focus_areas_stats AS
SELECT 
  unnest(focus_areas) as focus_area,
  COUNT(*) as user_count,
  ROUND((COUNT(*)::FLOAT / (SELECT COUNT(*) FROM profiles WHERE focus_areas IS NOT NULL)) * 100, 2) as percentage
FROM profiles 
WHERE focus_areas IS NOT NULL AND array_length(focus_areas, 1) > 0
GROUP BY unnest(focus_areas)
ORDER BY user_count DESC;

-- ============================================
-- TRIGGERS FOR AUTOMATION
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for user_memories
DROP TRIGGER IF EXISTS update_memories_updated_at ON user_memories;
CREATE TRIGGER update_memories_updated_at
  BEFORE UPDATE ON user_memories
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Function to update last_active on profile
CREATE OR REPLACE FUNCTION update_last_active()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE profiles
  SET last_active = NOW()
  WHERE id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update last_active when conversation is created
DROP TRIGGER IF EXISTS update_profile_last_active ON conversations;
CREATE TRIGGER update_profile_last_active
  AFTER INSERT ON conversations
  FOR EACH ROW
  EXECUTE FUNCTION update_last_active();

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, email, name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', SPLIT_PART(NEW.email, '@', 1))
  )
  ON CONFLICT (id) DO NOTHING; -- Prevent duplicate inserts
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile automatically
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- ============================================
-- SAMPLE DATA FOR TESTING (Optional)
-- ============================================

-- Uncomment to insert sample focus areas for testing
/*
INSERT INTO profiles (id, name, email, onboarding_completed, focus_areas, support_style, communication_tone)
VALUES 
  (uuid_generate_v4(), 'Test User 1', 'test1@example.com', true, 
   ARRAY['stress_relief', 'better_sleep', 'mindfulness'], 'calm_comforting', 'friendly'),
  (uuid_generate_v4(), 'Test User 2', 'test2@example.com', true,
   ARRAY['motivation', 'emotional_balance'], 'motivational', 'cheerful')
ON CONFLICT (name) DO NOTHING;
*/

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check table structure
-- SELECT table_name, column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns 
-- WHERE table_name IN ('profiles', 'conversations', 'user_memories', 'mood_history')
-- ORDER BY table_name, ordinal_position;

-- Check onboarding completion rate
-- SELECT * FROM onboarding_stats;

-- Check focus areas popularity
-- SELECT * FROM focus_areas_stats;

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE profiles IS 'Enhanced user profiles with complete onboarding system';
COMMENT ON TABLE conversations IS 'Chat conversations with emotion detection and personalization';
COMMENT ON TABLE user_memories IS 'User context and memories with reliability features';
COMMENT ON TABLE mood_history IS 'Mood tracking with enhanced emotion detection';
COMMENT ON TABLE onboarding_sessions IS 'Onboarding session tracking and analytics';

COMMENT ON COLUMN profiles.onboarding_completed IS 'Whether user completed the 7-step onboarding flow';
COMMENT ON COLUMN profiles.focus_areas IS 'Up to 3 emotional focus areas: stress_relief, better_sleep, self_awareness, emotional_balance, motivation, mindfulness';
COMMENT ON COLUMN profiles.support_style IS 'Preferred support approach: calm_comforting, honest_real, motivational, fun_distraction';
COMMENT ON COLUMN profiles.communication_tone IS 'Preferred AI communication tone: calm, cheerful, deep, friendly';

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
  RAISE NOTICE '✅ Jumbo Emotional AI Database Schema Complete!';
  RAISE NOTICE '📊 Tables: profiles, conversations, user_memories, mood_history, onboarding_sessions';
  RAISE NOTICE '🔒 Row Level Security: Enabled with user-specific policies';
  RAISE NOTICE '⚡ Indexes: Optimized for performance';
  RAISE NOTICE '🎯 Onboarding System: Ready for 7-step user flow';
  RAISE NOTICE '🧠 Emotional AI: Full personalization support';
END $$;