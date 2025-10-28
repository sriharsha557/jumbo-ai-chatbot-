-- ============================================
-- JUMBO ONBOARDING - SAFE MIGRATION SCRIPT
-- ============================================
-- Run this in Supabase SQL Editor to add onboarding fields
-- Uses ALTER TABLE to safely add columns to existing tables

-- ============================================
-- ADD ONBOARDING COLUMNS TO PROFILES TABLE
-- ============================================

-- Core onboarding tracking
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS onboarding_data JSONB DEFAULT '{}'::jsonb;

-- Personal information from Step 2
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS display_name TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS pronouns TEXT CHECK (pronouns IN ('he/him', 'she/her', 'they/them', 'prefer_not_to_say'));
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS preferred_language TEXT DEFAULT 'en' CHECK (preferred_language IN ('en', 'hi', 'other'));

-- Emotional baseline from Step 3
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS current_mood INTEGER CHECK (current_mood >= 1 AND current_mood <= 5);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS emotion_comfort_level TEXT CHECK (emotion_comfort_level IN ('easy', 'sometimes', 'difficult'));

-- Support style from Step 4
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS support_style TEXT CHECK (support_style IN ('calm_comforting', 'honest_real', 'motivational', 'fun_distraction'));
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS communication_tone TEXT CHECK (communication_tone IN ('calm', 'cheerful', 'deep', 'friendly'));

-- Focus areas from Step 5
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS focus_areas TEXT[];

-- Check-in preferences from Step 6
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS checkin_frequency TEXT CHECK (checkin_frequency IN ('daily', 'few_times_week', 'on_demand'));
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS checkin_time TEXT CHECK (checkin_time IN ('morning', 'evening', 'custom'));
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS custom_checkin_time TIME;

-- ============================================
-- ADD INDEXES FOR ONBOARDING FIELDS
-- ============================================

-- Index for onboarding status queries
CREATE INDEX IF NOT EXISTS idx_profiles_onboarding_status ON profiles(onboarding_completed);

-- Index for user preferences queries
CREATE INDEX IF NOT EXISTS idx_profiles_support_style ON profiles(support_style) WHERE support_style IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_profiles_communication_tone ON profiles(communication_tone) WHERE communication_tone IS NOT NULL;

-- Index for check-in scheduling
CREATE INDEX IF NOT EXISTS idx_profiles_checkin ON profiles(checkin_frequency, checkin_time) WHERE checkin_frequency IS NOT NULL;

-- ============================================
-- UPDATE EXISTING USERS (OPTIONAL)
-- ============================================

-- Set default values for existing users who haven't completed onboarding
UPDATE profiles 
SET 
  onboarding_completed = FALSE,
  onboarding_data = '{}'::jsonb
WHERE onboarding_completed IS NULL;

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON COLUMN profiles.onboarding_completed IS 'Whether user has completed the onboarding flow';
COMMENT ON COLUMN profiles.onboarding_data IS 'Complete onboarding responses stored as JSON';
COMMENT ON COLUMN profiles.display_name IS 'User chosen display name from onboarding';
COMMENT ON COLUMN profiles.pronouns IS 'User preferred pronouns';
COMMENT ON COLUMN profiles.preferred_language IS 'User preferred language for communication';
COMMENT ON COLUMN profiles.current_mood IS 'User current mood on 1-5 scale from onboarding';
COMMENT ON COLUMN profiles.emotion_comfort_level IS 'How comfortable user is discussing emotions';
COMMENT ON COLUMN profiles.support_style IS 'User preferred support approach';
COMMENT ON COLUMN profiles.communication_tone IS 'User preferred communication tone';
COMMENT ON COLUMN profiles.focus_areas IS 'Array of emotional focus areas user wants to work on';
COMMENT ON COLUMN profiles.checkin_frequency IS 'How often user wants check-ins';
COMMENT ON COLUMN profiles.checkin_time IS 'Preferred time for check-ins';
COMMENT ON COLUMN profiles.custom_checkin_time IS 'Custom check-in time if user chose custom';

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check if all columns were added successfully
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'profiles' 
-- AND column_name IN ('onboarding_completed', 'display_name', 'pronouns', 'support_style', 'focus_areas')
-- ORDER BY column_name;

-- Check existing users onboarding status
-- SELECT 
--   id, 
--   name, 
--   email, 
--   onboarding_completed, 
--   display_name, 
--   support_style,
--   focus_areas
-- FROM profiles 
-- LIMIT 5;