import json
import logging
import requests
from collections import Counter
try:
    from ..config import Config
    from ..models.mappings import get_all_categories, get_scenario
    from .data_service import get_recent_user_context
except ImportError:
    from config import Config
    from models.mappings import get_all_categories, get_scenario
    from services.data_service import get_recent_user_context
logger = logging.getLogger(__name__)
HTTP = requests.Session()
KEYWORD_CATEGORY_MAP = {
    "stress": ("stress", "anxiety", "sad", "down", "worried", "worry", "fear", "panic", "overwhelmed", "depressed"),
    "anger": ("angry", "anger", "furious", "mad", "rage"),
    "jealousy": ("jealous", "envy", "envious", "resent"),
    "gratitude": ("grateful", "gratitude", "thankful", "blessing"),
    "forgiveness": ("forgive", "forgiveness", "grudge", "resentment"),
    "trust_in_allah": ("trust", "tawakkul", "uncertain", "future", "rely", "reliance"),
    "patience": ("patient", "patience", "sabr", "waiting", "hardship", "trial"),
    "charity": ("charity", "donate", "giving", "sadaqah", "helping"),
    "lying": ("lie", "lying", "dishonest", "truth"),
    "arrogance": ("pride", "arrogant", "ego", "boast"),
}
SUPPORTIVE_CATEGORY_MAP = {
    "stress": "trust_in_allah",
    "anger": "forgiveness",
    "jealousy": "gratitude",
    "lying": "patience",
    "arrogance": "gratitude",
    "patience": "patience",
    "gratitude": "gratitude",
    "forgiveness": "forgiveness",
    "trust_in_allah": "trust_in_allah",
    "charity": "charity",
}
def _build_memory_summary(user_id):
    """Summarize recent reflections/activity into a short memory block for prompts."""
    context = get_recent_user_context(user_id)
    reflections = context.get("reflections", [])
    activities = context.get("activities", [])
    reflection_lines = []
    for item in reflections[-4:]:
        reflection_lines.append(
            f"- {item.get('timestamp', '')}: {item.get('assigned_category', 'unknown')} | {item.get('scenario', '')[:160]}"
        )
    activity_lines = []
    for item in activities[-6:]:
        activity_lines.append(
            f"- {item.get('timestamp', '')}: {item.get('action', '')} | {item.get('details', '')[:100]}"
        )
    return "\n".join([
        "Recent reflections:",
        *(reflection_lines or ["- No saved reflections yet."]),
        "Recent activity:",
        *(activity_lines or ["- No recent activity yet."]),
    ])
def _make_openrouter_call(prompt, is_json=False):
    """Helper to call OpenRouter API with speed optimization."""
    if not Config.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY is not set.")
        return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": Config.APP_URL,
        "X-Title": "AyahPath"
    }
    
    payload = {
        "model": Config.AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }
    
    if is_json:
        payload["response_format"] = {"type": "json_object"}
    try:
        response = HTTP.post(url, headers=headers, json=payload, timeout=12)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"OpenRouter call failed: {e}")
        return None
def guess_category_from_text(scenario):
    text = str(scenario or "").lower()
    for category, keywords in KEYWORD_CATEGORY_MAP.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "stress"
def assign_category(scenario, user_id='anonymous_user'):
    """Assigns category using OpenRouter (fast)."""
    categories = get_all_categories()
    memory = _build_memory_summary(user_id)
    
    prompt = (
        f"You are categorising a user's latest reflection for an Islamic guidance app.\n"
        f"{memory}\n"
        f'Latest reflection: "{scenario}"\n'
        f"Options: {', '.join(categories)}.\n"
        f"Respond with ONLY the category name."
    )
    
    assigned = _make_openrouter_call(prompt)
    if not assigned:
        return guess_category_from_text(scenario)
        
    assigned = assigned.strip().lower().replace('"', '').replace('.', '')
    
    if assigned in categories:
        return assigned
    
    for cat in categories:
        if cat.lower() in assigned:
            return cat
            
    return guess_category_from_text(scenario)
def generate_guidance(scenario, category, verse_text, tafsir_text, user_id='anonymous_user'):
    """Generates dual-perspective guidance using OpenRouter (fast)."""
    memory = _build_memory_summary(user_id)
    prompt = f"""
    UK English. JSON output.
    Use the user's recent memory to keep continuity without repeating old advice.
    {memory}
    User reflection: "{scenario}"
    Category: "{category}"
    Verse: {verse_text.get('english', '')}
    Tafsir: {tafsir_text[:800]}
    Provide:
    1. dunya_impact: Practical worldly advice.
    2. akhirah_impact: Spiritual takeaway.
    3. better_choice: One small actionable step.
    4. why_this_verse: A short sentence explaining why this verse is relevant to the user.
    """
    
    fallback = {
        "dunya_impact": "Focus on patience and practical steps in your daily affairs.",
        "akhirah_impact": "Trust in Allah's plan and seek reward in the hereafter.",
        "better_choice": "Take a moment for prayer and reflection today.",
        "why_this_verse": "This verse reminds us of Allah's presence in all situations."
    }
    
    content = _make_openrouter_call(prompt, is_json=True)
    if not content:
        return fallback
        
    try:
        data = json.loads(content)
        result = {}
        for key in ["dunya_impact", "akhirah_impact", "better_choice", "why_this_verse"]:
            result[key] = data.get(key, fallback[key])
        return result
    except json.JSONDecodeError:
        logger.error("Failed to parse OpenRouter JSON response")
        return fallback
def recommend_personalized_category(user_id='anonymous_user'):
    """Pick a supportive category using recent history, with AI when available."""
    context = get_recent_user_context(user_id)
    reflections = context.get("reflections", [])
    if not reflections:
        return "gratitude"
    latest = reflections[-1]
    latest_category = latest.get("assigned_category") or "stress"
    if Config.OPENROUTER_API_KEY:
        memory = _build_memory_summary(user_id)
        prompt = f"""
        You are selecting one supportive Qur'anic category for today's home screen.
        Goal: choose the category most likely to make the user's day easier and lighter.
        {memory}
        Latest category: "{latest_category}"
        Allowed categories: {", ".join(get_all_categories())}
        Respond with ONLY one category.
        """
        assigned = _make_openrouter_call(prompt)
        if assigned:
            assigned = assigned.strip().lower().replace('"', '').replace('.', '')
            if assigned in get_all_categories():
                return assigned
    return SUPPORTIVE_CATEGORY_MAP.get(latest_category, "gratitude")
def get_personalized_ayah_plan(user_id='anonymous_user'):
    """Return category and explanation for the personalized main-page ayah."""
    context = get_recent_user_context(user_id)
    category = recommend_personalized_category(user_id)
    scenario = get_scenario(category) or get_scenario("gratitude")
    reflections = context.get("reflections", [])
    activities = context.get("activities", [])
    recent_categories = [r.get("assigned_category") for r in reflections if r.get("assigned_category")]
    top_category = Counter(recent_categories).most_common(1)[0][0] if recent_categories else None
    if reflections:
        latest_text = reflections[-1].get("scenario", "")
        reason = f"Picked for you based on your recent reflections and activity. Latest reflection: {latest_text[:90]}"
    elif activities:
        reason = "Picked for you from your recent activity to bring a little more ease to today."
    else:
        reason = "A gentle ayah chosen to help make today easier."
    return {
        "category": category,
        "scenario": scenario,
        "reason": reason,
        "top_category": top_category,
    }
