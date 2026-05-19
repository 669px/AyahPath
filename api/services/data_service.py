import os
import json
import logging
import hashlib
from datetime import datetime, date, timedelta, timezone
import tempfile
import shutil
import re
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.getenv('DATA_DIR', os.path.join(BASE_DIR, 'data'))
if not os.path.isabs(DATA_DIR):
    DATA_DIR = os.path.join(BASE_DIR, DATA_DIR)
logger = logging.getLogger(__name__)
SAFE_USER_ID = re.compile('[^a-zA-Z0-9_.-]')

def normalize_user_id(user_id):
    cleaned = SAFE_USER_ID.sub('_', str(user_id or 'anonymous_user')).strip('._')
    return cleaned[:64] or 'anonymous_user'

def sanitize_text(value, max_len=1000):
    return str(value or '').replace('\x00', '').strip()[:max_len]

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def _read_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return [] if filename != 'streak_data.json' else {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f'Error reading {filename}: {e}')
        return [] if filename != 'streak_data.json' else {}

def _write_json(filename, data):
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)
    try:
        fd, temp_path = tempfile.mkstemp(dir=DATA_DIR, prefix=f'{filename}.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            os.replace(temp_path, filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
    except Exception as e:
        logger.error(f'Error writing {filename}: {e}')

def save_reflection(user_id, scenario, category, chapter, verse, verse_text, tafsir_text, ai_guidance):
    user_id = normalize_user_id(user_id)
    scenario = sanitize_text(scenario, max_len=500)
    category = sanitize_text(category, max_len=64)
    reflections = _read_json('saved_reflections.json')
    new_entry = {'id': hashlib.md5(f'{datetime.now(timezone.utc).isoformat()}{scenario}'.encode()).hexdigest()[:12], 'user_id': user_id, 'timestamp': datetime.now(timezone.utc).isoformat(), 'scenario': scenario, 'assigned_category': category, 'reference': f'{chapter}:{verse}', 'verse_text': verse_text, 'tafsir_snippet': tafsir_text[:500] + '...' if tafsir_text and len(tafsir_text) > 500 else tafsir_text, 'guidance': ai_guidance}
    reflections.append(new_entry)
    _write_json('saved_reflections.json', reflections)
    _log_activity(user_id, 'reflection_saved', f'Saved reflection for {chapter}:{verse}')
    return new_entry

def get_reflections(user_id):
    user_id = normalize_user_id(user_id)
    reflections = _read_json('saved_reflections.json')
    user_reflections = [r for r in reflections if r.get('user_id') == user_id]
    return sorted(user_reflections, key=lambda x: x.get('timestamp', ''), reverse=True)

def delete_reflection(reflection_id):
    reflections = _read_json('saved_reflections.json')
    updated = [r for r in reflections if r.get('id') != reflection_id]
    _write_json('saved_reflections.json', updated)
    return True

def update_streak(user_id):
    user_id = normalize_user_id(user_id)
    streaks = _read_json('streak_data.json')
    if not isinstance(streaks, dict):
        streaks = {}
    user_streak = streaks.get(user_id, {})
    today = date.today().isoformat()
    if not user_streak:
        user_streak = {'user_id': user_id, 'current_streak': 1, 'longest_streak': 1, 'last_active': today, 'total_days_active': 1, 'activity_dates': [today]}
    else:
        last_active = user_streak.get('last_active')
        if last_active != today:
            last_date = date.fromisoformat(last_active)
            today_date = date.today()
            diff = (today_date - last_date).days
            if diff == 1:
                user_streak['current_streak'] += 1
            elif diff > 1:
                user_streak['current_streak'] = 1
            user_streak['last_active'] = today
            if today not in user_streak.get('activity_dates', []):
                user_streak.setdefault('activity_dates', []).append(today)
                user_streak['total_days_active'] = user_streak.get('total_days_active', 0) + 1
        if user_streak['current_streak'] > user_streak.get('longest_streak', 0):
            user_streak['longest_streak'] = user_streak['current_streak']
    streaks[user_id] = user_streak
    _write_json('streak_data.json', streaks)
    return user_streak

def get_streak(user_id):
    user_id = normalize_user_id(user_id)
    streaks = _read_json('streak_data.json')
    if isinstance(streaks, dict):
        return streaks.get(user_id, {})
    return {}

def clear_streak(user_id):
    user_id = normalize_user_id(user_id)
    streaks = _read_json('streak_data.json')
    if isinstance(streaks, dict) and user_id in streaks:
        del streaks[user_id]
        _write_json('streak_data.json', streaks)
    return True

def get_week_activity(user_id):
    user_id = normalize_user_id(user_id)
    streak = get_streak(user_id)
    activity_dates = set(streak.get('activity_dates', []))
    week_activity = []
    for i in range(6, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        week_activity.append({'date': d, 'day': (date.today() - timedelta(days=i)).strftime('%a'), 'active': d in activity_dates})
    return week_activity

def _log_activity(user_id, action, details):
    user_id = normalize_user_id(user_id)
    action = sanitize_text(action, max_len=64)
    details = sanitize_text(details, max_len=280)
    logs = _read_json('activity_log.json')
    logs.append({'user_id': user_id, 'timestamp': datetime.now(timezone.utc).isoformat(), 'action': action, 'details': details})
    _write_json('activity_log.json', logs)

def get_activity_logs(user_id, limit=30):
    user_id = normalize_user_id(user_id)
    logs = _read_json('activity_log.json')
    user_logs = [l for l in logs if l.get('user_id') == user_id]
    return user_logs[-limit:]

def get_recent_user_context(user_id, reflection_limit=6, activity_limit=12):
    user_id = normalize_user_id(user_id)
    reflections = get_reflections(user_id)[-reflection_limit:]
    activities = get_activity_logs(user_id, activity_limit)
    return {'user_id': user_id, 'reflections': reflections, 'activities': activities}

def progress_user_goals(user_id, activity_type):
    user_id = normalize_user_id(user_id)
    goals = _read_json('goals_data.json')
    type_map = {'scenario_viewed': 'scenarios', 'reflection_submitted': 'reflections', 'ayah_listened': 'listening', 'daily_ayah_viewed': 'daily_ayah'}
    target_type = type_map.get(activity_type)
    for goal in goals:
        if goal.get('user_id') == user_id and (not goal.get('completed')):
            if goal.get('type') == 'any' or goal.get('type') == target_type:
                goal['current'] = min(goal['current'] + 1, goal['target'])
                if goal['current'] >= goal['target']:
                    goal['completed'] = True
                    goal['completed_date'] = datetime.now(timezone.utc).isoformat()
    _write_json('goals_data.json', goals)

def record_activity(user_id, activity_type, details=''):
    user_id = normalize_user_id(user_id)
    _log_activity(user_id, activity_type, details)
    update_streak(user_id)
    progress_user_goals(user_id, activity_type)

def create_goal(user_id, title, goal_type, target, period='daily'):
    user_id = normalize_user_id(user_id)
    title = sanitize_text(title, max_len=120)
    goal_type = sanitize_text(goal_type, max_len=40)
    period = sanitize_text(period, max_len=24)
    goals = _read_json('goals_data.json')
    new_goal = {'id': hashlib.md5(f'{datetime.now(timezone.utc).isoformat()}{title}'.encode()).hexdigest()[:12], 'user_id': user_id, 'title': title, 'type': goal_type, 'target': target, 'current': 0, 'completed': False, 'created_date': datetime.now(timezone.utc).isoformat(), 'completed_date': None, 'period': period}
    goals.append(new_goal)
    _write_json('goals_data.json', goals)
    return new_goal

def get_goals(user_id):
    user_id = normalize_user_id(user_id)
    goals = _read_json('goals_data.json')
    return [g for g in goals if g.get('user_id') == user_id]

def get_active_goals(user_id):
    goals = get_goals(user_id)
    return [g for g in goals if not g.get('completed')]

def get_completed_goals(user_id):
    goals = get_goals(user_id)
    return [g for g in goals if g.get('completed')]

def update_goal_progress(user_id, goal_id, increment=1):
    user_id = normalize_user_id(user_id)
    goals = _read_json('goals_data.json')
    for goal in goals:
        if goal.get('id') == goal_id and goal.get('user_id') == user_id:
            goal['current'] = min(goal['current'] + increment, goal['target'])
            if goal['current'] >= goal['target'] and (not goal.get('completed')):
                goal['completed'] = True
                goal['completed_date'] = datetime.now(timezone.utc).isoformat()
    _write_json('goals_data.json', goals)
    return goals

def delete_goal(user_id, goal_id):
    user_id = normalize_user_id(user_id)
    goals = _read_json('goals_data.json')
    updated = [g for g in goals if not (g.get('id') == goal_id and g.get('user_id') == user_id)]
    _write_json('goals_data.json', updated)
    return True

def clear_user_goals(user_id):
    user_id = normalize_user_id(user_id)
    goals = _read_json('goals_data.json')
    updated = [g for g in goals if g.get('user_id') != user_id]
    _write_json('goals_data.json', updated)
    return True
