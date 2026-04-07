"""
AyahPath Frontend Application
Delegates all data operations to the backend API
"""
import os
import sys
import subprocess
import time
import signal
import atexit
import requests
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
import logging
from prayer_db import init_db, toggle_prayer, get_prayers_for_date, get_week_summary, get_prayer_stats, clear_prayer_data

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize prayer database on module load
try:
    init_db()
    logger.info("Prayer database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize prayer database: {e}")

# Backend API configuration
API_HOST = os.environ.get("API_HOST", "localhost")
API_PORT = int(os.environ.get("API_PORT", 5001))
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

def api_call(endpoint, method='GET', data=None):
    """Helper to make API requests."""
    url = f"{API_BASE_URL}{endpoint}"
    logger.debug(f"Calling {method} {url} with data={data}")
    try:
        if method == 'GET':
            resp = requests.get(url, params=data, timeout=30)
        elif method == 'POST':
            resp = requests.post(url, json=data, timeout=30)
        elif method == 'DELETE':
            resp = requests.delete(url, params=data, timeout=30)
        else:
            return {'success': False, 'error': 'Invalid method'}
        
        if resp.status_code >= 200 and resp.status_code < 300:
            return resp.json() if resp.text else {'success': True}
        
        # Try to extract error message from JSON for 4xx/5xx errors
        error_msg = f'API error: {resp.status_code}'
        try:
            err_data = resp.json()
            if 'error' in err_data:
                error_msg = err_data['error']
        except:
            pass
            
        return {'success': False, 'error': error_msg, 'details': resp.text}
    except requests.exceptions.Timeout:
        logger.debug(f"Timeout calling {url}")
        return {'success': False, 'error': 'API timeout', 'backend_unavailable': True}
    except requests.exceptions.ConnectionError as e:
        logger.debug(f"Connection error calling {url}: {e}")
        return {'success': False, 'error': 'Cannot connect to backend API', 'backend_unavailable': True}
    except Exception as e:
        logger.error(f"API call error: {e}")
        return {'success': False, 'error': str(e)}

# ==================== STATIC PAGES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(_err):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(_err):
    return render_template('500.html'), 500

@app.errorhandler(503)
def service_unavailable(_err):
    return render_template('503.html'), 503

@app.route('/service-unavailable')
def service_unavailable_test():
    abort(503)

# ==================== API PROXY ROUTES ====================

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Get all scenarios."""
    result = api_call('/api/scenarios')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/scenarios/<scenario_id>', methods=['GET'])
def get_scenario(scenario_id):
    """Get scenario details."""
    params = {
        'trans': request.args.get('trans', '131'),
        'lang': request.args.get('lang', 'en')
    }
    result = api_call(f'/api/scenarios/{scenario_id}', data=params)
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/daily-ayah', methods=['GET'])
def get_daily_ayah():
    """Get daily ayah."""
    params = {
        'trans': request.args.get('trans', '131'),
        'lang': request.args.get('lang', 'en')
    }
    result = api_call('/api/daily-ayah', data=params)
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/reflections', methods=['POST'])
def create_reflection():
    """Create a reflection."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    result = api_call('/api/reflections', method='POST', data=data)
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 201 if result.get('success') else 400

@app.route('/api/reflections/<user_id>', methods=['GET'])
def get_reflections(user_id):
    """Get user reflections."""
    result = api_call(f'/api/reflections/{user_id}')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/reflections/<reflection_id>', methods=['DELETE'])
def delete_reflection(reflection_id):
    """Delete a reflection."""
    result = api_call(f'/api/reflections/{reflection_id}', method='DELETE')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/streak', methods=['GET'])
def get_default_streak():
    """Get streak (default user)."""
    user_id = request.args.get('user_id', 'anonymous_user')
    result = api_call(f'/api/streak/{user_id}')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/streak/<user_id>', methods=['GET'])
def get_streak(user_id):
    """Get user streak."""
    result = api_call(f'/api/streak/{user_id}')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/streak/<user_id>/checkin', methods=['POST'])
def checkin_streak(user_id):
    """Check in to streak."""
    result = api_call(f'/api/streak/{user_id}/checkin', method='POST', data={})
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/streak/<user_id>', methods=['DELETE'])
def clear_streak(user_id):
    """Clear user streak."""
    result = api_call(f'/api/streak/{user_id}', method='DELETE')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/goals/<user_id>', methods=['GET'])
def get_goals(user_id):
    """Get user goals."""
    result = api_call(f'/api/goals/{user_id}')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/goals', methods=['POST'])
def create_goal():
    """Create a goal."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    result = api_call('/api/goals', method='POST', data=data)
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 201 if result.get('success') else 400

@app.route('/api/goals/<goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    """Delete a goal."""
    user_id = request.args.get('user_id', 'anonymous_user')
    result = api_call(f'/api/goals/{goal_id}', method='DELETE', data={'user_id': user_id})
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/goals', methods=['DELETE'])
def clear_goals():
    """Clear all goals."""
    user_id = request.args.get('user_id', 'anonymous_user')
    result = api_call(f'/api/goals', method='DELETE', data={'user_id': user_id})
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/activity', methods=['GET'])
def get_default_activity():
    """Get activity (default user)."""
    user_id = request.args.get('user_id', 'anonymous_user')
    limit = request.args.get('limit', 30, type=int)
    result = api_call(f'/api/activity/{user_id}', data={'limit': limit})
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/activity/<user_id>', methods=['GET'])
def get_activity(user_id):
    """Get user activity."""
    limit = request.args.get('limit', 30, type=int)
    result = api_call(f'/api/activity/{user_id}', data={'limit': limit})
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/goals', methods=['GET'])
def get_default_goals():
    """Get goals (default user)."""
    user_id = request.args.get('user_id', 'anonymous_user')
    result = api_call(f'/api/goals/{user_id}')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/history', methods=['GET', 'DELETE'])
def get_history():
    """Get or delete reflection history (default user)."""
    user_id = request.args.get('user_id', 'anonymous_user')
    if request.method == 'DELETE':
        result = api_call(f'/api/history', method='DELETE', data={'user_id': user_id})
        if result.get('backend_unavailable'):
            return jsonify({'success': False, 'error': 'Backend not available'}), 503
        return jsonify(result), 200 if result.get('success') else 400

    result = api_call(f'/api/history', data={'user_id': user_id})
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400


@app.route('/api/save', methods=['POST'])
def save_reflection_manual():
    """Save an existing reflection."""
    data = request.get_json()
    result = api_call('/api/save', method='POST', data=data)
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/activity', methods=['POST'])
def record_activity():
    """Record activity."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    result = api_call('/api/activity', method='POST', data=data)
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 201 if result.get('success') else 400

@app.route('/api/quran/chapters', methods=['GET'])
def get_chapters():
    """Get Quran chapters."""
    result = api_call('/api/quran/chapters')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/quran/verse/<int:surah>/<int:ayah>', methods=['GET'])
def get_verse(surah, ayah):
    """Get a specific verse."""
    trans = request.args.get('trans', '131')
    result = api_call(f'/api/quran/verse/{surah}/{ayah}', data={'trans': trans})
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

@app.route('/api/quran/tafsir/<int:surah>/<int:ayah>', methods=['GET'])
def get_tafsir(surah, ayah):
    """Get verse tafsir."""
    result = api_call(f'/api/quran/tafsir/{surah}/{ayah}')
    if result.get('backend_unavailable'):
        return jsonify({'success': False, 'error': 'Backend not available'}), 503
    return jsonify(result), 200 if result.get('success') else 400

# ==================== PRAYER TRACKER API (SQLite, no backend needed) ====================

@app.route('/api/prayers/week', methods=['GET'])
def get_prayer_week():
    """Get prayer summary for the week containing the given date."""
    user_id = request.args.get('user_id', 'anonymous_user')
    ref_date = request.args.get('date')  # optional, defaults to today
    try:
        week = get_week_summary(user_id, ref_date)
        return jsonify({'success': True, 'week': week}), 200
    except Exception as e:
        logger.error(f"Error getting week summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prayers/stats', methods=['GET'])
def get_prayer_stats_route():
    """Get aggregated prayer statistics."""
    user_id = request.args.get('user_id', 'anonymous_user')
    try:
        stats = get_prayer_stats(user_id)
        return jsonify({'success': True, **stats}), 200
    except Exception as e:
        logger.error(f"Error getting prayer stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prayers/clear', methods=['DELETE'])
def clear_prayers():
    """Clear all prayer data for a user."""
    user_id = request.args.get('user_id', 'anonymous_user')
    try:
        clear_prayer_data(user_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error clearing prayer data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prayers/<prayer_date>', methods=['GET'])
def get_prayers(prayer_date):
    """Get prayer completion status for a specific date."""
    user_id = request.args.get('user_id', 'anonymous_user')
    try:
        prayers = get_prayers_for_date(user_id, prayer_date)
        return jsonify({'success': True, 'date': prayer_date, 'prayers': prayers}), 200
    except Exception as e:
        logger.error(f"Error getting prayers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prayers/<prayer_date>/<prayer_id>', methods=['POST'])
def toggle_prayer_route(prayer_date, prayer_id):
    """Toggle a prayer on/off."""
    data = request.get_json() or {}
    user_id = data.get('user_id', 'anonymous_user')
    try:
        new_state = toggle_prayer(user_id, prayer_date, prayer_id)
        prayers = get_prayers_for_date(user_id, prayer_date)
        stats = get_prayer_stats(user_id)
        return jsonify({
            'success': True,
            'prayer_id': prayer_id,
            'checked': new_state,
            'prayers': prayers,
            'stats': stats,
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error toggling prayer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Frontend health check."""
    # Check if backend is healthy too
    api_result = api_call('/api/health')
    backend_healthy = api_result.get('success', False) or api_result.get('status') == 'api_healthy'
    
    return jsonify({
        'status': 'healthy',
        'frontend': 'running',
        'backend': 'running' if backend_healthy else 'unavailable'
    }), 200 if backend_healthy else 503

if __name__ == '__main__':
    port = int(os.environ.get('FRONTEND_PORT', 5000))
    api_port = int(os.environ.get('API_PORT', 5001))
    
    print("\n" + "="*60)
    print(" 🌙 AyahPath Integrated Launcher")
    print("="*60)
    
    # Check if we should start the backend
    api_script = os.path.join(os.path.dirname(__file__), 'api', 'app.py')
    backend_proc = None
    
    if os.path.exists(api_script):
        print(f" ▶ Starting Backend API on port {api_port}...")
        try:
            # We use sys.executable to ensure we use the same Python environment
            backend_proc = subprocess.Popen(
                [sys.executable, api_script],
                env={**os.environ, 'API_PORT': str(api_port)},
                cwd=os.path.join(os.path.dirname(__file__), 'api')
            )
            
            # Ensure backend is killed when frontend exits
            def cleanup():
                if backend_proc:
                    print(f"\n ✗ Shutting down Backend API (PID: {backend_proc.pid})...")
                    backend_proc.terminate()
            
            atexit.register(cleanup)
            signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
            signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
            
            # Give it a second to start
            time.sleep(1.5)
        except Exception as e:
            print(f" ✗ Failed to start backend: {e}")
    else:
        print(" ✗ api/app.py not found. Running frontend only.")

    print(f" ▶ Starting Frontend on port {port}...")
    print(f" 🌐 http://localhost:{port}\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)
