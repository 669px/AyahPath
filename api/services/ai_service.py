import json
import logging
import requests
from config import Config
from models.mappings import get_all_categories

logger = logging.getLogger(__name__)

def _make_openrouter_call(prompt, is_json=False):
    """Helper to call OpenRouter API with speed optimization."""
    if not Config.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY is not set.")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
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
        response = requests.post(url, headers=headers, json=payload, timeout=12) # Fast timeout
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"OpenRouter call failed: {e}")
        return None

def assign_category(scenario):
    """Assigns category using OpenRouter (fast)."""
    categories = get_all_categories()
    
    prompt = f"Categorise this reflection: \"{scenario}\". Options: {', '.join(categories)}. Respond with ONLY the category name."
    
    assigned = _make_openrouter_call(prompt)
    if not assigned:
        return categories[0]
        
    assigned = assigned.strip().lower().replace('"', '').replace('.', '')
    
    if assigned in categories:
        return assigned
    
    for cat in categories:
        if cat.lower() in assigned:
            return cat
            
    return categories[0]

def generate_guidance(scenario, category, verse_text, tafsir_text):
    """Generates dual-perspective guidance using OpenRouter (fast)."""
    
    prompt = f"""
    UK English. JSON output.
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
        # Ensure only expected keys are returned to avoid frontend bloat
        result = {}
        for key in ["dunya_impact", "akhirah_impact", "better_choice", "why_this_verse"]:
            result[key] = data.get(key, fallback[key])
        return result
    except json.JSONDecodeError:
        logger.error("Failed to parse OpenRouter JSON response")
        return fallback
