-- PairLingua Database Initialization
-- This script creates the initial database structure

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create custom types
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'cefr_level') THEN
        CREATE TYPE cefr_level AS ENUM ('A1', 'A2', 'B1', 'B2', 'C1', 'C2');
    END IF;
END $$;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) UNIQUE,
    locale VARCHAR(10) DEFAULT 'ru',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    deleted_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false
);

-- User profiles table
CREATE TABLE IF NOT EXISTS profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    avatar_url TEXT,
    bio TEXT,
    daily_goal VARCHAR(20) DEFAULT '10',
    difficulty_preference VARCHAR(10) DEFAULT 'adaptive',
    notification_enabled BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}'::jsonb
);

-- Word pairs table
CREATE TABLE IF NOT EXISTS word_pairs (
    id BIGSERIAL PRIMARY KEY,
    spanish_word VARCHAR(200) NOT NULL,
    russian_word VARCHAR(200) NOT NULL,
    audio_url TEXT,
    cefr_level VARCHAR(2),
    frequency_rank INTEGER,
    tags TEXT[] DEFAULT '{}',
    examples JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User cards table (SM-2 algorithm)
CREATE TABLE IF NOT EXISTS user_cards (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_pair_id BIGINT NOT NULL REFERENCES word_pairs(id) ON DELETE CASCADE,
    ease_factor NUMERIC(4,2) DEFAULT 2.50,
    repetition_count INTEGER DEFAULT 0,
    interval_days INTEGER DEFAULT 0,
    due_date TIMESTAMP,
    last_quality SMALLINT,
    last_reviewed_at TIMESTAMP,
    total_reviews INTEGER DEFAULT 0,
    correct_reviews INTEGER DEFAULT 0,
    accuracy NUMERIC(4,2) DEFAULT 0.0,
    average_response_time INTEGER,
    is_learning BOOLEAN DEFAULT true,
    is_suspended BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, word_pair_id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_pair_id BIGINT NOT NULL REFERENCES word_pairs(id) ON DELETE CASCADE,
    user_card_id BIGINT NOT NULL REFERENCES user_cards(id) ON DELETE CASCADE,
    quality SMALLINT NOT NULL CHECK (quality >= 0 AND quality <= 5),
    response_time_ms INTEGER,
    source VARCHAR(50) DEFAULT 'web',
    session_id UUID,
    ease_factor_before INTEGER,
    ease_factor_after INTEGER,
    interval_before INTEGER,
    interval_after INTEGER,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Study sessions table
CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    active_pair_ids INTEGER[] DEFAULT '{}',
    session_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Achievements table
CREATE TABLE IF NOT EXISTS achievements (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    requirement_type VARCHAR(50),
    requirement_value INTEGER,
    category VARCHAR(50) DEFAULT 'general',
    difficulty VARCHAR(20) DEFAULT 'medium',
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- User achievements table
CREATE TABLE IF NOT EXISTS user_achievements (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id BIGINT NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_data TEXT,
    UNIQUE(user_id, achievement_id)
);

-- Token blacklist table
CREATE TABLE IF NOT EXISTS tokens_blacklist (
    jti UUID PRIMARY KEY,
    user_id UUID,
    token_type VARCHAR(20) DEFAULT 'access',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(100) DEFAULT 'logout'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_nickname ON users(nickname);
CREATE INDEX IF NOT EXISTS ix_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS ix_word_pairs_spanish ON word_pairs(spanish_word);
CREATE INDEX IF NOT EXISTS ix_word_pairs_russian ON word_pairs(russian_word);
CREATE INDEX IF NOT EXISTS ix_word_pairs_cefr_level ON word_pairs(cefr_level);
CREATE INDEX IF NOT EXISTS ix_word_pairs_frequency_rank ON word_pairs(frequency_rank);
CREATE INDEX IF NOT EXISTS ix_word_pairs_is_active ON word_pairs(is_active);
CREATE INDEX IF NOT EXISTS ix_word_pairs_tags ON word_pairs USING GIN(tags);

CREATE INDEX IF NOT EXISTS ix_user_cards_user_id ON user_cards(user_id);
CREATE INDEX IF NOT EXISTS ix_user_cards_due_date ON user_cards(due_date);
CREATE INDEX IF NOT EXISTS ix_user_cards_user_due ON user_cards(user_id, due_date);

CREATE INDEX IF NOT EXISTS ix_reviews_user_id ON reviews(user_id);
CREATE INDEX IF NOT EXISTS ix_reviews_reviewed_at ON reviews(reviewed_at);
CREATE INDEX IF NOT EXISTS ix_reviews_user_date ON reviews(user_id, reviewed_at);

CREATE INDEX IF NOT EXISTS ix_tokens_blacklist_expires ON tokens_blacklist(expires_at);
CREATE INDEX IF NOT EXISTS ix_tokens_blacklist_jti ON tokens_blacklist(jti);

CREATE INDEX IF NOT EXISTS ix_achievements_code ON achievements(code);
CREATE INDEX IF NOT EXISTS ix_user_achievements_user ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS ix_user_achievements_earned ON user_achievements(user_id, earned_at);

-- Create partial index for due cards (performance optimization)
CREATE INDEX IF NOT EXISTS ix_user_cards_due_now 
ON user_cards(user_id, due_date) 
WHERE due_date <= CURRENT_TIMESTAMP AND is_suspended = false;

-- Update triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_word_pairs_updated_at BEFORE UPDATE ON word_pairs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_cards_updated_at BEFORE UPDATE ON user_cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_sessions_updated_at BEFORE UPDATE ON study_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'PairLingua database initialization completed successfully!';
END $$;
