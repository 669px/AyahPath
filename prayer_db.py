"""
AyahPath Prayer Tracker — SQLite Database Module
Provides persistent storage for prayer tracking data.
Designed for deployment on Ubuntu KVM (SQLite, no external DB needed).
"""
import os
import sqlite3
import logging
from datetime import datetime, date, timedelta
from contextlib import contextmanager
logger = logging.getLogger(__name__)
                                                   
DB_DIR = os.environ.get('PRAYER_DB_DIR', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DB_DIR, 'prayer.db')
                                                  
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS prayer_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL DEFAULT 'anonymous_user',
    prayer_date TEXT    NOT NULL,
    prayer_id   TEXT    NOT NULL,
    completed   INTEGER NOT NULL DEFAULT 1,
    checked_at  TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, prayer_date, prayer_id)
);
CREATE INDEX IF NOT EXISTS idx_prayer_logs_user_date
    ON prayer_logs(user_id, prayer_date);
CREATE INDEX IF NOT EXISTS idx_prayer_logs_date
    ON prayer_logs(prayer_date);
CREATE TABLE IF NOT EXISTS prayer_daily_summary (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT    NOT NULL DEFAULT 'anonymous_user',
    prayer_date     TEXT    NOT NULL,
    completed_count INTEGER NOT NULL DEFAULT 0,
    total_prayers   INTEGER NOT NULL DEFAULT 5,
    is_complete     INTEGER NOT NULL DEFAULT 0,
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, prayer_date)
);
CREATE INDEX IF NOT EXISTS idx_daily_summary_user_date
    ON prayer_daily_summary(user_id, prayer_date);
CREATE TABLE IF NOT EXISTS prayer_streaks (
    user_id             TEXT PRIMARY KEY,
    current_streak      INTEGER NOT NULL DEFAULT 0,
    longest_streak      INTEGER NOT NULL DEFAULT 0,
    total_prayers_logged INTEGER NOT NULL DEFAULT 0,
    total_complete_days INTEGER NOT NULL DEFAULT 0,
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""
                          
VALID_PRAYERS = ('fajr', 'dhuhr', 'asr', 'maghrib', 'isha')
                                                                 
@contextmanager
def get_db():
    """Thread-safe database connection context manager."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")                          
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")                             
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
def init_db():
    """Initialize the database schema. Safe to call multiple times."""
    os.makedirs(DB_DIR, exist_ok=True)
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
    logger.info(f"Prayer database initialized at {DB_PATH}")
                                                       
def toggle_prayer(user_id, prayer_date_str, prayer_id):
    """
    Toggle a prayer on/off for a given user and date.
    Returns the new state: True if now checked, False if unchecked.
    """
    if prayer_id not in VALID_PRAYERS:
        raise ValueError(f"Invalid prayer_id: {prayer_id}. Must be one of {VALID_PRAYERS}")
    with get_db() as conn:
                                 
        row = conn.execute(
            "SELECT id, completed FROM prayer_logs WHERE user_id=? AND prayer_date=? AND prayer_id=?",
            (user_id, prayer_date_str, prayer_id)
        ).fetchone()
        now = datetime.utcnow().isoformat()
        if row and row['completed'] == 1:
                                                          
            conn.execute("DELETE FROM prayer_logs WHERE id=?", (row['id'],))
            new_state = False
        elif row and row['completed'] == 0:
                                             
            conn.execute(
                "UPDATE prayer_logs SET completed=1, checked_at=?, updated_at=? WHERE id=?",
                (now, now, row['id'])
            )
            new_state = True
        else:
                                                
            conn.execute(
                "INSERT INTO prayer_logs (user_id, prayer_date, prayer_id, completed, checked_at, created_at, updated_at) VALUES (?,?,?,1,?,?,?)",
                (user_id, prayer_date_str, prayer_id, now, now, now)
            )
            new_state = True
                              
        _update_daily_summary(conn, user_id, prayer_date_str)
                            
        _recalculate_streak(conn, user_id)
    return new_state
def get_prayers_for_date(user_id, prayer_date_str):
    """
    Get prayer completion status for a specific date.
    Returns dict: { 'fajr': True/False, 'dhuhr': True/False, ... }
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT prayer_id, completed FROM prayer_logs WHERE user_id=? AND prayer_date=? AND completed=1",
            (user_id, prayer_date_str)
        ).fetchall()
    result = {p: False for p in VALID_PRAYERS}
    for row in rows:
        if row['prayer_id'] in result:
            result[row['prayer_id']] = True
    return result
def get_week_summary(user_id, reference_date_str=None):
    """
    Get prayer completion for the week containing the reference date.
    Returns list of 7 dicts: [{date, day_label, completed_count, is_complete}, ...]
    """
    if reference_date_str:
        ref = date.fromisoformat(reference_date_str)
    else:
        ref = date.today()
                             
    dow = ref.weekday()            
    monday = ref - timedelta(days=dow)
    day_labels = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    dates = [(monday + timedelta(days=i)).isoformat() for i in range(7)]
    with get_db() as conn:
        placeholders = ','.join('?' * len(dates))
        rows = conn.execute(
            f"SELECT prayer_date, completed_count, is_complete FROM prayer_daily_summary WHERE user_id=? AND prayer_date IN ({placeholders})",
            [user_id] + dates
        ).fetchall()
    summary_map = {row['prayer_date']: dict(row) for row in rows}
    today_str = date.today().isoformat()
    result = []
    for i, d in enumerate(dates):
        s = summary_map.get(d, {})
        result.append({
            'date': d,
            'day_label': day_labels[i],
            'completed_count': s.get('completed_count', 0),
            'is_complete': bool(s.get('is_complete', 0)),
            'is_today': d == today_str,
        })
    return result
def get_prayer_stats(user_id):
    """
    Get aggregated prayer stats for a user.
    Returns: { current_streak, longest_streak, total_prayers, week_completion_pct }
    """
    with get_db() as conn:
                     
        streak_row = conn.execute(
            "SELECT * FROM prayer_streaks WHERE user_id=?", (user_id,)
        ).fetchone()
                                                           
        week_start = (date.today() - timedelta(days=6)).isoformat()
        week_row = conn.execute(
            "SELECT COALESCE(SUM(completed_count), 0) as week_prayed FROM prayer_daily_summary WHERE user_id=? AND prayer_date >= ?",
            (user_id, week_start)
        ).fetchone()
        week_prayed = week_row['week_prayed'] if week_row else 0
        week_total = 7 * 5                      
    return {
        'current_streak': streak_row['current_streak'] if streak_row else 0,
        'longest_streak': streak_row['longest_streak'] if streak_row else 0,
        'total_prayers': streak_row['total_prayers_logged'] if streak_row else 0,
        'total_complete_days': streak_row['total_complete_days'] if streak_row else 0,
        'week_completion_pct': round((week_prayed / week_total) * 100) if week_total > 0 else 0,
    }
def clear_prayer_data(user_id):
    """Clear all prayer data for a user."""
    with get_db() as conn:
        conn.execute("DELETE FROM prayer_logs WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM prayer_daily_summary WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM prayer_streaks WHERE user_id=?", (user_id,))
    return True
                                                            
def _update_daily_summary(conn, user_id, prayer_date_str):
    """Recalculate the daily summary row for a given date."""
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM prayer_logs WHERE user_id=? AND prayer_date=? AND completed=1",
        (user_id, prayer_date_str)
    ).fetchone()
    count = row['cnt'] if row else 0
    is_complete = 1 if count >= 5 else 0
    now = datetime.utcnow().isoformat()
    conn.execute("""
        INSERT INTO prayer_daily_summary (user_id, prayer_date, completed_count, total_prayers, is_complete, updated_at)
        VALUES (?, ?, ?, 5, ?, ?)
        ON CONFLICT(user_id, prayer_date) DO UPDATE SET
            completed_count = excluded.completed_count,
            is_complete = excluded.is_complete,
            updated_at = excluded.updated_at
    """, (user_id, prayer_date_str, count, is_complete, now))
def _recalculate_streak(conn, user_id):
    """
    Recalculate the streak for a user from scratch.
    A streak day = all 5 prayers completed on that date.
    """
                                              
    rows = conn.execute(
        "SELECT prayer_date FROM prayer_daily_summary WHERE user_id=? AND is_complete=1 ORDER BY prayer_date DESC",
        (user_id,)
    ).fetchall()
    complete_dates = set(row['prayer_date'] for row in rows)
                         
    total_row = conn.execute(
        "SELECT COUNT(*) as cnt FROM prayer_logs WHERE user_id=? AND completed=1",
        (user_id,)
    ).fetchone()
    total_prayers = total_row['cnt'] if total_row else 0
    total_complete_days = len(complete_dates)
                                                                      
    streak = 0
    check_date = date.today()
                       
    if check_date.isoformat() in complete_dates:
        streak = 1
        check_date -= timedelta(days=1)
    else:
                                                                          
        check_date -= timedelta(days=0)                               
                                                                  
        check_date = date.today() - timedelta(days=1)
                    
    for _ in range(365):
        if check_date.isoformat() in complete_dates:
            if streak == 0:
                streak = 1                           
            else:
                streak += 1
            check_date -= timedelta(days=1)
        else:
            break
                                             
    longest = 0
    current = 0
    if complete_dates:
        all_dates = sorted(complete_dates)
        current = 1
        longest = 1
        for i in range(1, len(all_dates)):
            prev = date.fromisoformat(all_dates[i - 1])
            curr = date.fromisoformat(all_dates[i])
            if (curr - prev).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
    now = datetime.utcnow().isoformat()
    conn.execute("""
        INSERT INTO prayer_streaks (user_id, current_streak, longest_streak, total_prayers_logged, total_complete_days, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            current_streak = excluded.current_streak,
            longest_streak = excluded.longest_streak,
            total_prayers_logged = excluded.total_prayers_logged,
            total_complete_days = excluded.total_complete_days,
            updated_at = excluded.updated_at
    """, (user_id, streak, longest, total_prayers, total_complete_days, now))
