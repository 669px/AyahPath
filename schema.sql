-- =====================================================================
-- AyahPath Prayer Tracker — Database Schema
-- SQLite 3.x | Compatible with Ubuntu KVM deployment
-- =====================================================================
--
-- Usage:
--   sqlite3 prayer.db < schema.sql
--
-- This schema is also applied automatically by prayer_db.py on startup.
-- Running this file manually is optional (useful for inspection/reset).
-- =====================================================================

-- Prayer log: one row per prayer per user per day
-- This is the source of truth for all prayer tracking data.
CREATE TABLE IF NOT EXISTS prayer_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL DEFAULT 'anonymous_user',
    prayer_date TEXT    NOT NULL,   -- ISO date: YYYY-MM-DD
    prayer_id   TEXT    NOT NULL,   -- fajr | dhuhr | asr | maghrib | isha
    completed   INTEGER NOT NULL DEFAULT 1,  -- 1 = prayed, 0 = unmarked
    checked_at  TEXT    NOT NULL,   -- ISO timestamp of when user checked the prayer
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    -- Enforce: each user can only have one entry per prayer per day
    UNIQUE(user_id, prayer_date, prayer_id)
);

-- Fast lookups for "show me all prayers for this user on this date"
CREATE INDEX IF NOT EXISTS idx_prayer_logs_user_date
    ON prayer_logs(user_id, prayer_date);

-- Fast lookups for admin/analytics queries by date range
CREATE INDEX IF NOT EXISTS idx_prayer_logs_date
    ON prayer_logs(prayer_date);


-- Daily summary: cached aggregate per user per day
-- Automatically updated on every prayer toggle to avoid expensive real-time aggregation.
CREATE TABLE IF NOT EXISTS prayer_daily_summary (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT    NOT NULL DEFAULT 'anonymous_user',
    prayer_date     TEXT    NOT NULL,   -- ISO date: YYYY-MM-DD
    completed_count INTEGER NOT NULL DEFAULT 0,   -- 0 to 5
    total_prayers   INTEGER NOT NULL DEFAULT 5,   -- always 5 (Fajr+Dhuhr+Asr+Maghrib+Isha)
    is_complete     INTEGER NOT NULL DEFAULT 0,   -- 1 if all 5 prayers done
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),

    UNIQUE(user_id, prayer_date)
);

CREATE INDEX IF NOT EXISTS idx_daily_summary_user_date
    ON prayer_daily_summary(user_id, prayer_date);


-- Prayer streak cache: running statistics per user
-- Recalculated from source data (prayer_logs + daily_summary) on each toggle.
-- This avoids expensive streak computation on every page load.
CREATE TABLE IF NOT EXISTS prayer_streaks (
    user_id              TEXT PRIMARY KEY,
    current_streak       INTEGER NOT NULL DEFAULT 0,   -- consecutive complete days ending today/yesterday
    longest_streak       INTEGER NOT NULL DEFAULT 0,   -- all-time longest consecutive complete days
    total_prayers_logged INTEGER NOT NULL DEFAULT 0,   -- total individual prayer check-ins
    total_complete_days  INTEGER NOT NULL DEFAULT 0,   -- days where all 5 prayers were completed
    updated_at           TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- =====================================================================
-- Example Queries
-- =====================================================================

-- Get all prayers for a user on a specific date:
-- SELECT prayer_id, completed FROM prayer_logs
-- WHERE user_id = 'anonymous_user' AND prayer_date = '2026-04-07' AND completed = 1;

-- Get weekly summary for a user:
-- SELECT prayer_date, completed_count, is_complete FROM prayer_daily_summary
-- WHERE user_id = 'anonymous_user' AND prayer_date BETWEEN '2026-04-01' AND '2026-04-07';

-- Get streak data:
-- SELECT * FROM prayer_streaks WHERE user_id = 'anonymous_user';

-- Count total prayers in last 30 days:
-- SELECT COUNT(*) FROM prayer_logs
-- WHERE user_id = 'anonymous_user' AND completed = 1
--   AND prayer_date >= date('now', '-30 days');
