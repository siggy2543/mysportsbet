-- Sports Betting Database Initialization Script
-- This script sets up the initial database schema and configuration

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO sports_user;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO sports_user;
GRANT ALL PRIVILEGES ON SCHEMA audit TO sports_user;

-- Create custom types
DO $$ BEGIN
    CREATE TYPE bet_status AS ENUM (
        'pending',
        'placed',
        'won',
        'lost',
        'cancelled',
        'void'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE bet_type AS ENUM (
        'moneyline',
        'spread',
        'over_under',
        'prop',
        'parlay',
        'teaser'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE game_status AS ENUM (
        'scheduled',
        'live',
        'completed',
        'postponed',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email CITEXT UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.00 CHECK (balance >= 0),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}',
    
    CONSTRAINT users_username_length CHECK (length(username) >= 3),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;

-- Sports and leagues
CREATE TABLE IF NOT EXISTS sports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leagues (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER REFERENCES sports(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(sport_id, slug)
);

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    league_id INTEGER REFERENCES leagues(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    abbreviation VARCHAR(10),
    logo_url TEXT,
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(league_id, name)
);

-- Games/Events
CREATE TABLE IF NOT EXISTS sport_events (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    sport VARCHAR(100) NOT NULL,
    league VARCHAR(100) NOT NULL,
    home_team VARCHAR(200) NOT NULL,
    away_team VARCHAR(200) NOT NULL,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status game_status DEFAULT 'scheduled',
    odds_data JSONB DEFAULT '{}',
    final_score JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sport_events_external_id ON sport_events(external_id);
CREATE INDEX IF NOT EXISTS idx_sport_events_date ON sport_events(event_date);
CREATE INDEX IF NOT EXISTS idx_sport_events_status ON sport_events(status);
CREATE INDEX IF NOT EXISTS idx_sport_events_sport ON sport_events(sport);
CREATE INDEX IF NOT EXISTS idx_sport_events_league ON sport_events(league);

-- Bets
CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    event_id INTEGER REFERENCES sport_events(id),
    bet_type bet_type NOT NULL,
    selection VARCHAR(100) NOT NULL,
    odds DECIMAL(8, 3) NOT NULL CHECK (odds > 0),
    stake DECIMAL(10, 2) NOT NULL CHECK (stake > 0),
    potential_payout DECIMAL(12, 2) NOT NULL,
    actual_payout DECIMAL(12, 2) DEFAULT 0,
    status bet_status DEFAULT 'pending',
    external_bet_id VARCHAR(100),
    placed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    settled_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_bets_user_id ON bets(user_id);
CREATE INDEX IF NOT EXISTS idx_bets_event_id ON bets(event_id);
CREATE INDEX IF NOT EXISTS idx_bets_status ON bets(status);
CREATE INDEX IF NOT EXISTS idx_bets_placed_at ON bets(placed_at);

-- Predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES sport_events(id),
    prediction_type VARCHAR(50) NOT NULL,
    predicted_outcome VARCHAR(100) NOT NULL,
    confidence DECIMAL(5, 4) CHECK (confidence BETWEEN 0 AND 1),
    expected_value DECIMAL(8, 4),
    kelly_criterion DECIMAL(8, 4),
    model_version VARCHAR(50),
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_event_id ON predictions(event_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);

-- Functions and Triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sport_events_updated_at BEFORE UPDATE ON sport_events 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default sports
INSERT INTO sports (name, slug, display_name) VALUES 
    ('football', 'football', 'Football'),
    ('basketball', 'basketball', 'Basketball'),
    ('baseball', 'baseball', 'Baseball'),
    ('hockey', 'hockey', 'Hockey'),
    ('soccer', 'soccer', 'Soccer')
ON CONFLICT (slug) DO NOTHING;

-- Grant final permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sports_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO sports_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO sports_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sports_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO sports_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA audit TO sports_user;