-- ============================================================================
-- COMPLETE SUPABASE SCHEMA - Project: ylcepmvbjjnwmzvevxid
-- Consolidated from all conversation artifacts
-- Run in: https://supabase.com/dashboard/project/ylcepmvbjjnwmzvevxid/sql
-- ============================================================================

-- PART 1: CORE TABLES (Self-Improving Systems)

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    system_context JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER,
    evaluated BOOLEAN DEFAULT FALSE,
    evaluation_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    prompt_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50) DEFAULT 'system',
    trigger_reason TEXT,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_type, version)
);

-- PART 2: NOVEL WRITER TABLES

CREATE TABLE IF NOT EXISTS books (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), title VARCHAR(500) NOT NULL, series_name VARCHAR(255), genre VARCHAR(100), target_word_count INTEGER DEFAULT 80000, current_word_count INTEGER DEFAULT 0, status VARCHAR(50) DEFAULT 'planning', metadata JSONB DEFAULT '{}', created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS chapters (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), book_id UUID REFERENCES books(id) ON DELETE CASCADE, chapter_number INTEGER NOT NULL, title VARCHAR(500), content TEXT, word_count INTEGER DEFAULT 0, status VARCHAR(50) DEFAULT 'draft', evaluation_scores JSONB DEFAULT '{}', revision_count INTEGER DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW(), UNIQUE(book_id, chapter_number));

CREATE TABLE IF NOT EXISTS style_profiles (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name VARCHAR(255) NOT NULL, description TEXT, pov VARCHAR(50) DEFAULT 'third_limited', tense VARCHAR(50) DEFAULT 'past', tone_keywords JSONB DEFAULT '[]', dialogue_percentage INTEGER DEFAULT 40, forbidden_phrases JSONB DEFAULT '[]', is_active BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS evaluations (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE, clarity_score DECIMAL(3,1), engagement_score DECIMAL(3,1), pacing_score DECIMAL(3,1), voice_score DECIMAL(3,1), technical_score DECIMAL(3,1), overall_score DECIMAL(3,2), feedback_text TEXT, triggered_revision BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW());

-- PART 3: VALIDATION STACK TABLES

CREATE TABLE IF NOT EXISTS chapter_manifest (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), book_id UUID REFERENCES books(id) ON DELETE CASCADE, chapter_number INTEGER NOT NULL, title VARCHAR(500), summary TEXT, key_events JSONB DEFAULT '[]', characters_present JSONB DEFAULT '[]', location VARCHAR(255), time_period VARCHAR(100), emotional_arc TEXT, required_elements JSONB DEFAULT '{}', song_required BOOLEAN DEFAULT FALSE, song_placement TEXT, created_at TIMESTAMPTZ DEFAULT NOW(), UNIQUE(book_id, chapter_number));

CREATE TABLE IF NOT EXISTS characters (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), book_id UUID REFERENCES books(id) ON DELETE CASCADE, name VARCHAR(255) NOT NULL, role VARCHAR(100), description TEXT, personality_traits JSONB DEFAULT '[]', speech_patterns TEXT, arc_summary TEXT, relationships JSONB DEFAULT '{}', created_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS world_settings (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), book_id UUID REFERENCES books(id) ON DELETE CASCADE, setting_type VARCHAR(100) NOT NULL, name VARCHAR(255), description TEXT, rules JSONB DEFAULT '[]', forbidden_elements JSONB DEFAULT '[]', created_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS phrase_tracker (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), style_profile_id UUID REFERENCES style_profiles(id) ON DELETE CASCADE, phrase TEXT NOT NULL, last_used_chapter INTEGER, usage_count INTEGER DEFAULT 1, flagged_as_llm_pattern BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS story_memory (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), book_id UUID REFERENCES books(id) ON DELETE CASCADE, chapter_number INTEGER NOT NULL, summary TEXT, key_developments JSONB DEFAULT '[]', character_states JSONB DEFAULT '{}', unresolved_threads JSONB DEFAULT '[]', created_at TIMESTAMPTZ DEFAULT NOW());

-- PART 4: ASSET VAULT TABLES

CREATE TABLE IF NOT EXISTS asset_projects (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name TEXT NOT NULL, description TEXT, style_guide JSONB DEFAULT '{}', created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS asset_characters (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), project_id UUID REFERENCES asset_projects(id) ON DELETE CASCADE, name TEXT NOT NULL, tier TEXT CHECK (tier IN ('hero', 'supporting', 'chorus')) NOT NULL DEFAULT 'supporting', description TEXT, visual_traits JSONB DEFAULT '{}', created_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS reference_images (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), character_id UUID REFERENCES asset_characters(id) ON DELETE CASCADE, storage_path TEXT NOT NULL, public_url TEXT NOT NULL, metadata JSONB DEFAULT '{}', uploaded_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS generated_assets (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), character_id UUID REFERENCES asset_characters(id) ON DELETE CASCADE, reference_image_id UUID REFERENCES reference_images(id), prompt TEXT, model_used VARCHAR(100), storage_path TEXT, public_url TEXT, generation_params JSONB DEFAULT '{}', cost_usd DECIMAL(10,6), status VARCHAR(50) DEFAULT 'pending', created_at TIMESTAMPTZ DEFAULT NOW());

CREATE TABLE IF NOT EXISTS generation_jobs (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), project_id UUID REFERENCES asset_projects(id) ON DELETE CASCADE, character_id UUID REFERENCES asset_characters(id), job_type VARCHAR(50) NOT NULL, status VARCHAR(50) DEFAULT 'queued', progress INTEGER DEFAULT 0, result JSONB, error_message TEXT, callback_url TEXT, created_at TIMESTAMPTZ DEFAULT NOW(), completed_at TIMESTAMPTZ);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_chapters_book ON chapters(book_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_chapter ON evaluations(chapter_id);
CREATE INDEX IF NOT EXISTS idx_phrase_tracker_profile ON phrase_tracker(style_profile_id);
CREATE INDEX IF NOT EXISTS idx_asset_characters_project ON asset_characters(project_id);
