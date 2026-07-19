-- EdgeFlow Database Schema — v1 Draft
-- Status: DRAFT, akan difinalisasi jadi docs/Database.md + migration Alembic di Phase 1
-- Referensi entitas: docs/PRD.md §6, docs/Architecture.md §3

-- ============================
-- Users & Auth
-- ============================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- Subscription / Entitlement (docs/Architecture.md §3.7)
-- ============================
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan VARCHAR(50) NOT NULL, -- 'free' | 'crypto_only' | 'forex_only' | 'bundle'
    markets TEXT[] NOT NULL,   -- ['crypto'] | ['forex'] | ['crypto','forex']
    strategies TEXT[],         -- opsional, granular entitlement per strategy
    status VARCHAR(20) NOT NULL DEFAULT 'trial', -- trial | active | expired
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- Exchange/Broker Connections (API key user, terenkripsi)
-- ============================
CREATE TABLE broker_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'binance' | 'bybit' | 'oanda' | dst
    market VARCHAR(20) NOT NULL,   -- 'crypto' | 'forex'
    api_key_encrypted TEXT NOT NULL,
    api_secret_encrypted TEXT NOT NULL,
    permissions VARCHAR(50) DEFAULT 'read_trade', -- tidak pernah 'withdrawal'
    environment VARCHAR(20) DEFAULT 'practice',   -- practice | live
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- Strategy Config Reference (docs/Strategy-Specification.md §7)
-- ============================
CREATE TABLE strategy_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id VARCHAR(50) NOT NULL, -- 'smc_v1', 'ema_v1'
    version VARCHAR(20) NOT NULL,
    config_json JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- User Strategy Preference (parameter custom per user, dalam batas yang diizinkan)
-- ============================
CREATE TABLE user_strategy_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    strategy_id VARCHAR(50) NOT NULL,
    market VARCHAR(20) NOT NULL,
    symbols TEXT[] NOT NULL, -- watchlist
    parameters JSONB,        -- override default parameters (lihat packages/config)
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- Signals (hasil evaluasi Strategy Engine, termasuk yang di-skip/blocked)
-- ============================
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    strategy_id VARCHAR(50) NOT NULL,
    strategy_version VARCHAR(20) NOT NULL,
    market VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL, -- BUY | SELL
    checklist JSONB NOT NULL,        -- [{ rule_id, passed, reason }]
    score INT NOT NULL,
    recommendation VARCHAR(20),      -- A+ | A | B | Reject
    entry_zone NUMERIC,
    stop_loss NUMERIC,
    take_profit NUMERIC,
    status VARCHAR(30) NOT NULL DEFAULT 'pending', -- pending | sent | blocked_by_discipline | confirmed | expired
    blocked_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- Trades (setelah user konfirmasi eksekusi)
-- ============================
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    signal_id UUID REFERENCES signals(id),
    broker_connection_id UUID REFERENCES broker_connections(id),
    market VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    strategy_id VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_price NUMERIC NOT NULL,
    stop_loss NUMERIC NOT NULL,
    take_profit NUMERIC NOT NULL,
    lot_size NUMERIC NOT NULL,
    risk_amount NUMERIC,
    rr_planned NUMERIC,
    result VARCHAR(10),      -- win | loss | breakeven | open
    r_multiple NUMERIC,
    profit_loss NUMERIC,
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    exit_reason VARCHAR(30), -- tp_hit | sl_hit | manual | time_exit | news_exit
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- Journal (data tambahan manual dari user)
-- ============================
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trade_id UUID REFERENCES trades(id) ON DELETE CASCADE,
    emotion VARCHAR(30),     -- calm | fomo | revenge | anxious | confident | dst
    notes TEXT,
    screenshot_url TEXT,
    mistake_tags TEXT[],     -- ['moved_sl', 'entered_early', 'oversized']
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================
-- Discipline State (daily limit, cooldown tracking)
-- ============================
CREATE TABLE discipline_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    trades_count INT DEFAULT 0,
    cumulative_r NUMERIC DEFAULT 0,
    loss_streak INT DEFAULT 0,
    is_locked BOOLEAN DEFAULT false,
    lock_reason TEXT,
    locked_until TIMESTAMPTZ,
    UNIQUE(user_id, date)
);

-- ============================
-- Indexes
-- ============================
CREATE INDEX idx_signals_user_created ON signals(user_id, created_at DESC);
CREATE INDEX idx_trades_user_symbol ON trades(user_id, symbol);
CREATE INDEX idx_discipline_state_user_date ON discipline_state(user_id, date);
