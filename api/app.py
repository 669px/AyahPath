import random
import json
import logging
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from config import Config
from models.mappings import SCENARIO_MAPPINGS, DAILY_AYAHS, get_all_categories, get_scenario, get_daily_ayahs, get_youtube_videos
from services.quran_service import fetch_verse, get_tafsir, get_chapters
from services.ai_service import assign_category, generate_guidance
from services.data_service import (
    save_reflection, get_reflections, delete_reflection,
    update_streak, get_streak, get_week_activity,
    record_activity, get_activity_logs,
    create_goal, get_goals, get_active_goals, get_completed_goals, update_goal_progress, delete_goal,
    clear_streak, clear_user_goals
)
from services.youtube_service import get_videos_for_scenario
from datetime import date, datetime
import time
from functools import wraps

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# In-memory request tracking: { ip: [timestamp1, timestamp2, ...] }
REQUEST_HISTORY = {}

def rate_limit(limit=5, period=60):
    """Simple in-memory rate limiter decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            
            # Initialize or clean up history
            history = REQUEST_HISTORY.get(ip, [])
            history = [t for t in history if now - t < period]
            
            if len(history) >= limit:
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return jsonify({
                    'success': False, 
                    'error': 'Too many requests. Please wait a moment.'
                }), 429
                
            history.append(now)
            REQUEST_HISTORY[ip] = history
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== SCENARIOS ENDPOINTS ====================

@app.route('/api/scenarios', methods=['GET'])
def list_scenarios():
    """Get all available scenarios."""
    scenarios = []
    for key, data in SCENARIO_MAPPINGS.items():
        scenarios.append({
            'id': key,
            'title': data['title'],
            'icon': data['icon'],
            'description': data['description'],
            'category': data['category'],
        })
    return jsonify({'success': True, 'scenarios': scenarios}), 200

@app.route('/api/scenarios/<scenario_id>', methods=['GET'])
@rate_limit(limit=5, period=60) # Prevent spamming AI guidance
def get_scenario_detail(scenario_id):
    """Get detailed information about a scenario with primary ayah and guidance."""
    scenario = get_scenario(scenario_id)
    if not scenario:
        return jsonify({'success': False, 'error': 'Scenario not found'}), 404
    
    trans = request.args.get('trans', '131')
    lang = request.args.get('lang', 'en')
    
    # Get primary ayah
    primary = scenario['ayahs'][0]
    primaryayah = fetch_verse(primary['surah'], primary['ayah'], translation_id=trans)
    if not primaryayah or not primaryayah.get('translation'):
        return jsonify({'success': False, 'error': 'Failed to fetch ayah'}), 500
    
    # Already contains 'translation' from fetch_verse
    
    # Generate guidance
    tafsir = get_tafsir(primary['surah'], primary['ayah'])
    guidance = generate_guidance(
        scenario=scenario['title'],
        category=scenario_id,
        verse_text={'english': primaryayah['translation']},
        tafsir_text=tafsir or ""
    )
    
    # Get additional ayahs
    additional_ayahs = []
    for extra in scenario['ayahs'][1:3]:
        extra_data = fetch_verse(extra['surah'], extra['ayah'], translation_id=trans)
        if extra_data and extra_data.get('translation'):
            extra_data['context'] = extra['context']
            additional_ayahs.append(extra_data)
    
    # Get YouTube videos
    videos = get_videos_for_scenario(scenario_id)
    
    record_activity('anonymous_user', 'scenario_viewed', scenario['title'])
    
    return jsonify({
        'success': True,
        'scenario': {
            'id': scenario_id,
            'title': scenario['title'],
            'description': scenario['description'],
            'category': scenario['category'],
            'icon': scenario['icon'],
        },
        'primary_ayah': primaryayah,
        'additional_ayahs': additional_ayahs,
        'insight': {**guidance, 'success': True},
        'video_embeds': videos
    }), 200

# ==================== REFLECTION ENDPOINTS ====================

@app.route('/api/reflections', methods=['POST'])
@rate_limit(limit=3, period=60) # Stricter limit for AI generation
def create_reflection():
    """Create a new custom reflection."""
    data = request.get_json() or {}
    # Accept both 'reflection' and 'situation' for flexibility
    situation = (data.get('reflection') or data.get('situation', '')).strip()
    user_id = data.get('user_id', 'anonymous_user')
    trans = data.get('trans', '131')
    lang = data.get('lang', 'en')
    
    if not situation:
        return jsonify({'success': False, 'error': 'Reflection required'}), 400
    if len(situation) < 5: # Reduced minimum context to be more forgiving
        return jsonify({'success': False, 'error': 'Provide more context'}), 400
    
    try:
        # AI dynamically assigns category
        category = assign_category(situation)
        
        # Pick a random verse from that category
        scenario = get_scenario(category)
        if not scenario:
            return jsonify({'success': False, 'error': 'Could not determine appropriate guidance'}), 500
        
        primary = scenario['ayahs'][0]
        
        # Fetch verse and tafsir
        verse_data = fetch_verse(primary['surah'], primary['ayah'], translation_id=trans)
        tafsir_text = get_tafsir(primary['surah'], primary['ayah'])
        
        if not verse_data or not verse_data.get('translation'):
            return jsonify({'success': False, 'error': 'Verse details missing'}), 404
        
        # Generate guidance
        guidance = generate_guidance(
            scenario=situation,
            category=scenario.get('title', category),
            verse_text={'english': verse_data['translation']},
            tafsir_text=tafsir_text or ""
        )
        
        # Save reflection
        saved = save_reflection(
            user_id=user_id,
            scenario=situation,
            category=category,
            chapter=primary['surah'],
            verse=primary['ayah'],
            verse_text=verse_data,
            tafsir_text=tafsir_text or "",
            ai_guidance=guidance
        )
        
        update_streak(user_id)
        record_activity(user_id, 'reflection_submitted', situation[:60])
        
        # Get videos
        videos = get_videos_for_scenario(category)
        
        return jsonify({
            'success': True,
            'reflection_id': saved['id'],
            'category': category,
            'matched_scenario': scenario.get('title', category),
            'why_this_verse': guidance.get('why_this_verse', ''),
            'quranic_reference': f"{primary['surah']}:{primary['ayah']}",
            'ayah': {**verse_data, 'success': True},
            'insight': {**guidance, 'success': True},
            'video_embeds': videos
        }), 201
    except Exception as e:
        logger.error(f"Error creating reflection: {e}")
        return jsonify({'success': False, 'error': 'Failed to process reflection'}), 500

@app.route('/api/save', methods=['POST'])
def save_existing_reflection():
    """Save an already generated reflection."""
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous_user')
    title = data.get('title', 'Reflection')
    verse_key = data.get('verse_key', '')
    situation = data.get('situation', '')
    insight_summary = data.get('insight_summary', '')
    
    # Parse verse_key (e.g., "1:1")
    chapter, verse = 1, 1
    if ':' in verse_key:
        try:
            chapter, verse = map(int, verse_key.split(':'))
        except: pass
    
    # Use existing save_reflection but with simplified data if needed
    save_reflection(
        user_id=user_id,
        scenario=situation or title,
        category='manual',
        chapter=chapter,
        verse=verse,
        verse_text={"english": "", "arabic": ""}, # Minimal
        tafsir_text="",
        ai_guidance={
            "dunya_impact": data.get('dunya_impact', ''),
            "akhirah_impact": data.get('akhirah_impact', ''),
            "better_choice": insight_summary
        }
    )
    
    record_activity(user_id, 'reflection_saved', f"{title} - {verse_key}")
    return jsonify({'success': True}), 200

@app.route('/api/reflections/<user_id>', methods=['GET'])
def get_user_reflections(user_id):
    """Get all reflections for a user."""
    reflections = get_reflections(user_id)
    return jsonify({'success': True, 'reflections': reflections}), 200

@app.route('/api/reflections/<reflection_id>', methods=['DELETE'])
def remove_reflection(reflection_id):
    """Delete a reflection."""
    delete_reflection(reflection_id)
    return jsonify({'success': True}), 200

# ==================== DAILY AYAH ENDPOINTS ====================

@app.route('/api/daily-ayah', methods=['GET'])
def get_daily_ayah():
    """Get today's daily ayah."""
    trans = request.args.get('trans', '131')
    lang = request.args.get('lang', 'en')
    
    today = date.today()
    idx = today.timetuple().tm_yday % len(DAILY_AYAHS)
    daily = DAILY_AYAHS[idx]
    
    ayah = fetch_verse(daily['surah'], daily['ayah'], translation_id=trans)
    
    if not ayah or not ayah.get('translation'):
        return jsonify({'success': False, 'error': 'Failed to fetch daily ayah'}), 500
    ayah['success'] = True
    
    record_activity('anonymous_user', 'daily_ayah_viewed')
    
    return jsonify({
        'success': True,
        'date': today.isoformat(),
        'ayah': ayah
    }), 200

# ==================== STREAK ENDPOINTS ====================

# Default streak endpoint (uses anonymous_user)
@app.route('/api/streak', methods=['GET'])
def get_default_streak():
    """Get streak information (default user)."""
    user_id = request.args.get('user_id', 'anonymous_user')
    streak = get_streak(user_id)
    week_activity = get_week_activity(user_id)
    
    return jsonify({
        'success': True,
        'current_streak': streak.get('current_streak', 0),
        'longest_streak': streak.get('longest_streak', 0),
        'total_days_active': streak.get('total_days_active', 0),
        'week_activity': week_activity
    }), 200

@app.route('/api/streak/<user_id>', methods=['GET'])
def get_user_streak(user_id):
    """Get streak information for a user."""
    streak = get_streak(user_id)
    week_activity = get_week_activity(user_id)
    
    return jsonify({
        'success': True,
        'current_streak': streak.get('current_streak', 0),
        'longest_streak': streak.get('longest_streak', 0),
        'total_days_active': streak.get('total_days_active', 0),
        'week_activity': week_activity
    }), 200

@app.route('/api/streak/<user_id>/checkin', methods=['POST'])
def checkin_streak(user_id):
    """Record a daily check-in."""
    record_activity(user_id, 'manual_checkin', 'Daily check-in')
    streak = get_streak(user_id)
    return jsonify({
        'success': True,
        'current_streak': streak.get('current_streak', 0)
    }), 200

@app.route('/api/streak/<user_id>', methods=['DELETE'])
def clear_user_streak(user_id):
    """Clear streak data."""
    clear_streak(user_id)
    return jsonify({'success': True}), 200

# ==================== GOALS ENDPOINTS ====================

@app.route('/api/goals', methods=['GET'])
def list_default_goals():
    """Get all goals (default user)."""
    user_id = request.args.get('user_id', 'anonymous_user')
    active = get_active_goals(user_id)
    completed = get_completed_goals(user_id)
    return jsonify({
        'success': True,
        'active_goals': active,
        'completed_goals': completed
    }), 200

@app.route('/api/goals/<user_id>', methods=['GET'])
def list_goals(user_id):
    """Get all goals for a user."""
    active = get_active_goals(user_id)
    completed = get_completed_goals(user_id)
    return jsonify({
        'success': True,
        'active_goals': active,
        'completed_goals': completed
    }), 200

@app.route('/api/goals', methods=['POST'])
def create_user_goal():
    """Create a new goal."""
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous_user')
    title = data.get('title', 'My Goal')
    goal_type = data.get('type', 'any')
    target = data.get('target', 5)
    period = data.get('period', 'daily')
    
    goal = create_goal(user_id, title, goal_type, target, period)
    return jsonify({'success': True, 'goal': goal}), 201

@app.route('/api/goals/<goal_id>', methods=['DELETE'])
def remove_goal(goal_id):
    """Delete a goal."""
    user_id = request.args.get('user_id', 'anonymous_user')
    delete_goal(user_id, goal_id)
    return jsonify({'success': True}), 200

@app.route('/api/goals', methods=['DELETE'])
def clear_all_goals():
    """Clear all goals."""
    user_id = request.args.get('user_id', 'anonymous_user')
    clear_user_goals(user_id)
    return jsonify({'success': True}), 200

@app.route('/api/goals/<user_id>', methods=['DELETE'])
def clear_user_goals_endpoint(user_id):
    """Clear all goals for a user."""
    clear_user_goals(user_id)
    return jsonify({'success': True}), 200

# ==================== ACTIVITY ENDPOINTS ====================

@app.route('/api/activity', methods=['GET'])
def get_default_activity():
    """Get recent activity logs (default user)."""
    user_id = request.args.get('user_id', 'anonymous_user')
    limit = request.args.get('limit', 30, type=int)
    logs = get_activity_logs(user_id, limit)
    return jsonify({'success': True, 'activities': logs}), 200

@app.route('/api/activity/<user_id>', methods=['GET'])
def get_user_activity(user_id):
    """Get recent activity logs for a user."""
    limit = request.args.get('limit', 30, type=int)
    logs = get_activity_logs(user_id, limit)
    return jsonify({'success': True, 'activities': logs}), 200

@app.route('/api/activity', methods=['POST'])
def record_user_activity():
    """Record an activity."""
    data = request.get_json()
    user_id = data.get('user_id', 'anonymous_user')
    activity_type = data.get('type', 'general')
    details = data.get('details', '')
    
    record_activity(user_id, activity_type, details)
    return jsonify({'success': True}), 201

# ==================== HISTORY ENDPOINT ====================

@app.route('/api/history', methods=['GET', 'DELETE'])
def get_history():
    """Get or clear reflection history."""
    user_id = request.args.get('user_id', 'anonymous_user')
    if request.method == 'DELETE':
        # Logic to clear history for user
        reflections = get_reflections(user_id)
        for r in reflections:
            delete_reflection(r['id'])
        return jsonify({'success': True}), 200
    
    reflections = get_reflections(user_id)
    return jsonify({'success': True, 'reflections': reflections}), 200

# ==================== QURAN DATA ENDPOINTS ====================

@app.route('/api/quran/chapters', methods=['GET'])
def list_quran_chapters():
    """Get all Qur'an chapters (surahs)."""
    chapters = get_chapters()
    return jsonify({
        'success': True,
        'chapters': chapters
    }), 200

@app.route('/api/quran/verse/<int:surah>/<int:ayah>', methods=['GET'])
def get_quran_verse(surah, ayah):
    """Get a specific verse."""
    trans = request.args.get('trans', '131')
    verse = fetch_verse(surah, ayah, translation_id=trans)
    
    if not verse or not verse.get('translation'):
        return jsonify({'success': False, 'error': 'Verse not found'}), 404
    verse['success'] = True
    
    return jsonify({'success': True, 'verse': verse}), 200

@app.route('/api/quran/tafsir/<int:surah>/<int:ayah>', methods=['GET'])
def get_verse_tafsir(surah, ayah):
    """Get tafsir (interpretation) for a verse."""
    tafsir = get_tafsir(surah, ayah)
    return jsonify({
        'success': True,
        'reference': f"{surah}:{ayah}",
        'tafsir': tafsir
    }), 200

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """API health check endpoint."""
    return jsonify({"status": "api_healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)
