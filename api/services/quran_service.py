import requests
import logging

BASE_URL = "http://api.alquran.cloud/v1"
ARABIC_EDITION = "quran-uthmani"
AUDIO_EDITION = "ar.alafasy"

# Mapping numeric frontend IDs to alquran.cloud edition strings
TRANSLATION_EDITIONS = {
    "131": "en.asad",        # Asad English
    "97": "ur.ahmedali",    # Urdu
    "84": "en.hilali",      # Hilali & Khan English
    "136": "fr.hamidullah", # French
    "33": "id.indonesian",  # Indonesian
    "20": "bn.bengali",     # Bengali
    "77": "tr.diyanet",     # Turkish
    "54": "hi.hindi",       # Hindi
}

def fetch_verse(chapter, verse, translation_id="131"):
    """Fetch verse details including Arabic text, translation, and audio."""
    primary_edition = "en.asad"
    secondary_edition = TRANSLATION_EDITIONS.get(str(translation_id), primary_edition)
    
    # If the user requested English, we only need one translation edition
    if secondary_edition == primary_edition:
        editions_str = primary_edition
    else:
        editions_str = f"{primary_edition},{secondary_edition}"

    url = f"{BASE_URL}/ayah/{chapter}:{verse}/editions/{ARABIC_EDITION},{editions_str},{AUDIO_EDITION}"
    
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        
        if not data.get('data') or len(data['data']) < 2:
            logging.error(f"Incomplete data returned for {chapter}:{verse}")
            return None
            
        results = data['data']
        # mapping: 0=arabic, 1=primary(en), 2=secondary(optional), last=audio
        arabic_text = results[0]['text']
        primary_trans = results[1]['text']
        # If we have 4 items, results[2] is the secondary trans.
        # If we have 3 items, the user requested English (so editions_str was just "en.asad")
        secondary_trans = results[2]['text'] if len(results) > 3 else ""
        audio_url = results[-1]['audio']
        
        surah = results[0]['surah']
        
        return {
            "chapter": chapter,
            "verse": verse,
            "verse_key": f"{chapter}:{verse}",
            "arabic": arabic_text,
            "translation": primary_trans,
            "secondary_translation": secondary_trans,
            "surah_name": surah['englishName'],
            "audio": audio_url,
            "success": True
        }
    except Exception as e:
        logging.error(f"Error fetching verse {chapter}:{verse}: {e}")
        return None

def get_chapters():
    """Fetches the list of all surahs (chapters) from the Quran."""
    try:
        response = requests.get(f"{BASE_URL}/surah", timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        logging.error(f"Error fetching chapters: {e}")
        return []

def get_tafsir(chapter, verse):
    """Fetches tafsir for the given verse."""
    try:
        # Using a simple tafsir endpoint if available, otherwise return placeholder
        # alquran.cloud doesn't have tafsir, so return a placeholder
        return "Tafsir available through Quran.com for detailed explanations."
    except Exception as e:
        logging.error(f"Error fetching tafsir for {chapter}:{verse} - {e}")
        return "Tafsir unavailable at the moment."
