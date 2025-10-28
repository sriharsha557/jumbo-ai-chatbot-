-- ============================================
-- JUMBO CHATBOT - SUPABASE DATABASE SCHEMA
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USER PROFILES TABLE
-- ============================================
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT,
  preferred_name TEXT, -- What the user wants to be called
  language TEXT DEFAULT 'en' CHECK (language IN ('en', 'te', 'hi')),
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_active TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb,
  
  -- ONBOARDING FIELDS
  onboarding_completed BOOLEAN DEFAULT FALSE,
  display_name TEXT, -- User's chosen display name
  pronouns TEXT CHECK (pronouns IN ('he/him', 'she/her', 'they/them', 'prefer_not_to_say')),
  preferred_language TEXT DEFAULT 'en' CHECK (preferred_language IN ('en', 'hi', 'other')),
  current_mood INTEGER CHECK (current_mood >= 1 AND current_mood <= 5), -- 1-5 scale
  emotion_comfort_level TEXT CHECK (emotion_comfort_level IN ('easy', 'sometimes', 'difficult')),
  support_style TEXT CHECK (support_style IN ('calm_comforting', 'honest_real', 'motivational', 'fun_distraction')),
  communication_tone TEXT CHECK (communication_tone IN ('calm', 'cheerful', 'deep', 'friendly')),
  focus_areas TEXT[], -- Array of focus areas
  checkin_frequency TEXT CHECK (checkin_frequency IN ('daily', 'few_times_week', 'on_demand')),
  checkin_time TEXT CHECK (checkin_time IN ('morning', 'evening', 'custom')),
  custom_checkin_time TIME,
  onboarding_data JSONB DEFAULT '{}'::jsonb -- Store complete onboarding responses
);

-- ============================================
-- 2. CONVERSATIONS TABLE
-- ============================================
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  user_message TEXT NOT NULL,
  bot_response TEXT NOT NULL,
  mood TEXT DEFAULT 'neutral',
  mood_confidence FLOAT DEFAULT 0.0,
  detected_language TEXT DEFAULT 'en',
  used_llm BOOLEAN DEFAULT FALSE,
  scenario TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. USER MEMORIES TABLE
-- ============================================
CREATE TABLE user_memories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  memory_type TEXT NOT NULL CHECK (memory_type IN ('person', 'preference', 'event', 'topic', 'fact', 'emotion')),
  category TEXT, -- 'friend', 'family', 'food', 'music', 'personal_relationship', 'work', etc.
  fact TEXT NOT NULL, -- The actual memory/fact to remember
  name TEXT, -- Name of person/thing (if applicable)
  relationship TEXT, -- 'friend', 'brother', 'colleague', etc.
  importance_score FLOAT DEFAULT 1.0, -- How important this memory is (0.1 to 1.0)
  data JSONB NOT NULL DEFAULT '{}'::jsonb, -- Additional structured data
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 4. MOOD HISTORY TABLE
-- ============================================
CREATE TABLE mood_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  mood TEXT NOT NULL,
  confidence FLOAT DEFAULT 0.0,
  context TEXT, -- What triggered this mood
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ENHANCED MEMORY SCHEMA FOR RELIABILITY
-- ============================================

-- Add vector embeddings support (requires pgvector extension)
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Enhanced user_memories table with reliability features
ALTER TABLE user_memories ADD COLUMN IF NOT EXISTS embedding vector(1536);
ALTER TABLE user_memories ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-ada-002';
ALTER TABLE user_memories ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE user_memories ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE user_memories ADD COLUMN IF NOT EXISTS duplicate_of UUID REFERENCES user_memories(id);
ALTER TABLE user_memories ADD COLUMN IF NOT EXISTS confidence_score FLOAT DEFAULT 1.0;
ALTER TABLE user_memories ADD COLUMN IF NOT EXISTS source_conversation_id UUID REFERENCES conversations(id);

-- ============================================
-- OPTIMIZED INDEXES FOR PERFORMANCE
-- ============================================

-- Conversations indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_date ON conversations(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_mood ON conversations(user_id, mood);
CREATE INDEX IF NOT EXISTS idx_conversations_language ON conversations(user_id, detected_language);
CREATE INDEX IF NOT EXISTS idx_conversations_metadata ON conversations USING gin(metadata);

-- Enhanced memory indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_memories_user_type ON user_memories(user_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_category ON user_memories(user_id, category);
CREATE INDEX IF NOT EXISTS idx_memories_updated ON user_memories(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_active ON user_memories(user_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_memories_importance ON user_memories(user_id, importance_score DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_memories_type_category ON user_memories(user_id, memory_type, category) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_memories_confidence ON user_memories(user_id, confidence_score DESC) WHERE is_active = true;

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_memories_name_search ON user_memories USING gin(to_tsvector('english', name)) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_memories_fact_search ON user_memories USING gin(to_tsvector('english', fact)) WHERE is_active = true;

-- Vector similarity index (uncomment when pgvector is available)
-- CREATE INDEX IF NOT EXISTS idx_memories_embedding ON user_memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Mood history index
CREATE INDEX idx_mood_history_user_date ON mood_history(user_id, created_at DESC);

-- Profiles index
CREATE INDEX idx_profiles_last_active ON profiles(last_active DESC);

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE mood_history ENABLE ROW LEVEL SECURITY;

-- PROFILES POLICIES
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- CONVERSATIONS POLICIES
CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations"
  ON conversations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations"
  ON conversations FOR DELETE
  USING (auth.uid() = user_id);

-- MEMORIES POLICIES
CREATE POLICY "Users can view own memories"
  ON user_memories FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own memories"
  ON user_memories FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own memories"
  ON user_memories FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own memories"
  ON user_memories FOR DELETE
  USING (auth.uid() = user_id);

-- MOOD HISTORY POLICIES
CREATE POLICY "Users can view own mood history"
  ON mood_history FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own mood history"
  ON mood_history FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for user_memories
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
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile automatically
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- ============================================
-- MEMORY RELIABILITY FUNCTIONS
-- ============================================

-- Function to find duplicate memories
CREATE OR REPLACE FUNCTION find_duplicate_memories(p_user_id UUID, p_fact TEXT, p_similarity_threshold FLOAT DEFAULT 0.85)
RETURNS TABLE(memory_id UUID, similarity_score FLOAT) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    id,
    similarity(fact, p_fact) as sim_score
  FROM user_memories 
  WHERE user_id = p_user_id 
    AND is_active = true
    AND similarity(fact, p_fact) > p_similarity_threshold
  ORDER BY sim_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to mark memory as duplicate
CREATE OR REPLACE FUNCTION mark_memory_duplicate(p_memory_id UUID, p_duplicate_of UUID)
RETURNS BOOLEAN AS $$
BEGIN
  UPDATE user_memories 
  SET is_active = false, 
      duplicate_of = p_duplicate_of,
      updated_at = NOW()
  WHERE id = p_memory_id;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to clean old inactive memories
CREATE OR REPLACE FUNCTION cleanup_old_memories(p_days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM user_memories 
  WHERE is_active = false 
    AND updated_at < NOW() - INTERVAL '%s days' % p_days_old;
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- BACKUP AND RECOVERY TABLES
-- ============================================

-- Memory backup table for point-in-time recovery
CREATE TABLE IF NOT EXISTS user_memories_backup (
  backup_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  backup_date TIMESTAMPTZ DEFAULT NOW(),
  user_id UUID NOT NULL,
  memory_data JSONB NOT NULL,
  backup_type TEXT DEFAULT 'daily' CHECK (backup_type IN ('daily', 'weekly', 'monthly', 'manual', 'pre_migration'))
);

CREATE INDEX IF NOT EXISTS idx_memory_backup_user_date ON user_memories_backup(user_id, backup_date DESC);
CREATE INDEX IF NOT EXISTS idx_memory_backup_type ON user_memories_backup(backup_type, backup_date DESC);

-- Backup records table
CREATE TABLE IF NOT EXISTS backup_records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  backup_id TEXT NOT NULL UNIQUE,
  backup_type TEXT NOT NULL,
  file_path TEXT,
  file_size BIGINT,
  table_counts JSONB,
  checksum TEXT,
  status TEXT DEFAULT 'in_progress',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_backup_records_type_date ON backup_records(backup_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backup_records_status ON backup_records(status, created_at DESC);

-- Function to create memory backup
CREATE OR REPLACE FUNCTION backup_user_memories(p_user_id UUID, p_backup_type TEXT DEFAULT 'manual')
RETURNS UUID AS $$
DECLARE
  backup_id UUID;
BEGIN
  INSERT INTO user_memories_backup (user_id, memory_data, backup_type)
  SELECT 
    p_user_id,
    jsonb_agg(to_jsonb(um.*)) as memory_data,
    p_backup_type
  FROM user_memories um
  WHERE um.user_id = p_user_id
  RETURNING backup_id INTO backup_id;
  
  RETURN backup_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ENHANCED VIEWS FOR MONITORING
-- ============================================

-- View: Memory statistics with reliability metrics
CREATE OR REPLACE VIEW memory_stats AS
SELECT 
  user_id,
  COUNT(*) as total_memories,
  COUNT(*) FILTER (WHERE is_active = true) as active_memories,
  COUNT(*) FILTER (WHERE is_active = false) as inactive_memories,
  COUNT(*) FILTER (WHERE duplicate_of IS NOT NULL) as duplicate_memories,
  AVG(importance_score) as avg_importance,
  AVG(confidence_score) as avg_confidence,
  MAX(updated_at) as last_updated,
  COUNT(DISTINCT memory_type) as memory_types_count,
  COUNT(DISTINCT category) as categories_count,
  COUNT(*) FILTER (WHERE embedding IS NOT NULL) as memories_with_embeddings
FROM user_memories
GROUP BY user_id;

-- View: Recent conversations with user info
CREATE OR REPLACE VIEW recent_conversations AS
SELECT 
  c.id,
  c.user_id,
  p.name as user_name,
  p.preferred_name,
  c.user_message,
  c.bot_response,
  c.mood,
  c.mood_confidence,
  c.used_llm,
  c.scenario,
  c.created_at
FROM conversations c
JOIN profiles p ON c.user_id = p.id
ORDER BY c.created_at DESC;

-- View: User statistics with memory metrics
CREATE OR REPLACE VIEW user_stats AS
SELECT 
  p.id,
  p.name,
  p.preferred_name,
  p.language,
  COUNT(DISTINCT c.id) as total_conversations,
  COUNT(DISTINCT DATE(c.created_at)) as days_active,
  MAX(c.created_at) as last_conversation,
  COUNT(DISTINCT m.id) FILTER (WHERE m.is_active = true) as active_memories,
  COUNT(DISTINCT m.id) as total_memories,
  AVG(m.importance_score) as avg_memory_importance,
  COUNT(DISTINCT mh.id) as mood_entries,
  p.last_active
FROM profiles p
LEFT JOIN conversations c ON p.id = c.user_id
LEFT JOIN user_memories m ON p.id = m.user_id
LEFT JOIN mood_history mh ON p.id = mh.user_id
GROUP BY p.id, p.name, p.preferred_name, p.language, p.last_active;

-- ============================================
-- SAMPLE QUERIES (For Testing)
-- ============================================

-- Test: Check if tables are created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Test: Check RLS policies
-- SELECT * FROM pg_policies WHERE schemaname = 'public';

COMMENT ON TABLE profiles IS 'User profiles linked to Supabase Auth';
COMMENT ON TABLE conversations IS 'Chat conversation history';
COMMENT ON TABLE user_memories IS 'User relationships, preferences, and context';
COMMENT ON TABLE mood_history IS 'Mood tracking for emotional patterns';