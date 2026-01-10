-- JESSE NOVEL FACTORY - COMPLETE DATABASE SCHEMA
-- Deploy to Supabase: ylcepmvbjjnwmzvevxid
-- Created: 2024-12-24

-- ============================================================
-- SCHEMA: jesse_factory
-- ============================================================
CREATE SCHEMA IF NOT EXISTS jesse_factory;

-- ============================================================
-- TABLE: projects (Book-level tracking)
-- ============================================================
CREATE TABLE jesse_factory.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_number INTEGER NOT NULL UNIQUE,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'Planning' CHECK (status IN ('Planning', 'Outlining', 'Drafting', 'Editing', 'Final', 'Published')),
    premise TEXT,
    target_words INTEGER DEFAULT 35000,
    current_words INTEGER DEFAULT 0,
    chapters_planned INTEGER DEFAULT 12,
    chapters_complete INTEGER DEFAULT 0,
    songs_planned INTEGER DEFAULT 4,
    songs_complete INTEGER DEFAULT 0,
    fairy_tale_source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: characters (Character registry with voice/rules)
-- ============================================================
CREATE TABLE jesse_factory.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    species TEXT NOT NULL,
    role TEXT NOT NULL,
    voice_notes TEXT,
    dialogue_markers TEXT[],
    hard_rules TEXT[],
    running_jokes TEXT[],
    relationships JSONB DEFAULT '[]'::jsonb,
    first_appearance INTEGER,
    arc_summary TEXT,
    elevenlabs_voice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: canon_ledger (Single source of truth for facts)
-- ============================================================
CREATE TABLE jesse_factory.canon_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Magic Rule', 'Character Trait', 'World Building', 'Timeline', 'Artifact', 'Relationship', 'Running Joke')),
    confidence TEXT DEFAULT 'High' CHECK (confidence IN ('High', 'Medium', 'Low')),
    source_book INTEGER,
    source_chapter INTEGER,
    evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by TEXT DEFAULT 'System',
    UNIQUE(fact, category)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: scenes (Chapter/scene level content)
-- ============================================================
CREATE TABLE jesse_factory.scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    scene_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    scene_number INTEGER DEFAULT 1,
    title TEXT,
    goal TEXT,
    conflict TEXT,
    turn TEXT,
    humour_device TEXT,
    draft_status TEXT DEFAULT 'Outline' CHECK (draft_status IN ('Outline', 'Draft', 'Revised', 'Punched', 'Final')),
    draft_text TEXT,
    word_count INTEGER DEFAULT 0,
    continuity_issues JSONB DEFAULT '[]'::jsonb,
    editor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, scene_id)
);

-- ============================================================
-- TABLE: songs (Musical numbers tracking)
-- ============================================================
CREATE TABLE jesse_factory.songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    song_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    performer TEXT NOT NULL,
    song_type TEXT CHECK (song_type IN ('Opening', 'I Want', 'Comedy', 'Villain', 'Ensemble', 'Finale', 'Reprise', 'Duet')),
    placement TEXT,
    lyrics TEXT,
    suno_prompt TEXT,
    suno_style TEXT,
    suno_output_urls TEXT[],
    status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Draft Lyrics', 'Final Lyrics', 'Generated', 'Approved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, song_number)
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- TABLE: tasks (Punch list / work items)
-- ============================================================
CREATE TABLE jesse_factory.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id) ON DELETE CASCADE,
    task TEXT NOT NULL,
    task_type TEXT CHECK (task_type IN ('Continuity Fix', 'Voice Fix', 'Structural Edit', 'Canon Update', 'Song Write', 'QA Review', 'Human Review')),
    severity TEXT DEFAULT 'Medium' CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done', 'Blocked', 'Rejected')),
    owner_agent TEXT,
    source_scene_id TEXT,
    quote TEXT,
    suggested_fix TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: prompts_library (Reusable agent prompts)
-- ============================================================
CREATE TABLE jesse_factory.prompts_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_name TEXT NOT NULL UNIQUE,
    agent_role TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    input_variables TEXT[],
    output_format TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    performance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: style_contract / agent_runs / quality_reviews
-- ============================================================
CREATE TABLE jesse_factory.style_contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL UNIQUE,
    rule_category TEXT CHECK (rule_category IN ('Tone', 'Dialogue', 'Magic', 'Family', 'Humour', 'Structure')),
    rule_text TEXT NOT NULL,
    examples TEXT[],
    anti_examples TEXT[],
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    project_id UUID REFERENCES jesse_factory.projects(id),
    input_summary TEXT,
    output_summary TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    status TEXT CHECK (status IN ('Success', 'Partial', 'Failed', 'Halted')),
    error_message TEXT,
    quality_score DECIMAL(3,2),
    improvements_noted TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jesse_factory.quality_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES jesse_factory.projects(id),
    review_type TEXT CHECK (review_type IN ('Continuity', 'Voice', 'Structure', 'Canon', 'Final')),
    reviewer_agent TEXT NOT NULL,
    items_checked INTEGER,
    issues_found INTEGER,
    issues_resolved INTEGER,
    pass_rate DECIMAL(5,2),
    detailed_report JSONB,
    recommendations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_scenes_project ON jesse_factory.scenes(project_id);
CREATE INDEX idx_scenes_status ON jesse_factory.scenes(draft_status);
CREATE INDEX idx_songs_project ON jesse_factory.songs(project_id);
CREATE INDEX idx_tasks_status ON jesse_factory.tasks(status);
CREATE INDEX idx_tasks_severity ON jesse_factory.tasks(severity);
CREATE INDEX idx_canon_category ON jesse_factory.canon_ledger(category);
CREATE INDEX idx_agent_runs_agent ON jesse_factory.agent_runs(agent_name);
CREATE INDEX idx_agent_runs_project ON jesse_factory.agent_runs(project_id);

-- ============================================================
-- FUNCTIONS: Auto-update timestamps
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON jesse_factory.projects
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_characters_timestamp BEFORE UPDATE ON jesse_factory.characters
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();
CREATE TRIGGER update_scenes_timestamp BEFORE UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.update_timestamp();

-- ============================================================
-- FUNCTION: Calculate word count on scene update
-- ============================================================
CREATE OR REPLACE FUNCTION jesse_factory.calculate_word_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.draft_text IS NOT NULL THEN
        NEW.word_count = array_length(regexp_split_to_array(trim(NEW.draft_text), '\s+'), 1);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calc_scene_words BEFORE INSERT OR UPDATE ON jesse_factory.scenes
    FOR EACH ROW EXECUTE FUNCTION jesse_factory.calculate_word_count();


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';


-- ============================================================
-- VIEW: Active tasks dashboard
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.active_tasks_dashboard AS
SELECT 
    t.id,
    p.title as book_title,
    t.task,
    t.task_type,
    t.severity,
    t.status,
    t.owner_agent,
    t.created_at,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/3600 as hours_open
FROM jesse_factory.tasks t
LEFT JOIN jesse_factory.projects p ON t.project_id = p.id
WHERE t.status NOT IN ('Done', 'Rejected')
ORDER BY 
    CASE t.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
    t.created_at;

-- ============================================================
-- VIEW: Project progress summary
-- ============================================================
CREATE OR REPLACE VIEW jesse_factory.project_progress AS
SELECT 
    p.id, p.book_number, p.title, p.status,
    p.current_words, p.target_words,
    ROUND((p.current_words::decimal / NULLIF(p.target_words, 0)) * 100, 1) as word_progress_pct,
    p.chapters_complete, p.chapters_planned,
    (SELECT COUNT(*) FROM jesse_factory.tasks WHERE project_id = p.id AND status = 'Open') as open_tasks
FROM jesse_factory.projects p
ORDER BY p.book_number;

COMMENT ON SCHEMA jesse_factory IS 'Jesse Novel Factory - Automated book production system';
