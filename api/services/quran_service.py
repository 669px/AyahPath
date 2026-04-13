import logging
from functools import lru_cache

try:
    from .virtual_quran_api import get_by_key as virtual_get_by_key
    from .virtual_quran_api import list_verses as virtual_list_verses
    from .virtual_quran_api import get_categories as virtual_get_categories
except ImportError:
    from virtual_quran_api import get_by_key as virtual_get_by_key
    from virtual_quran_api import list_verses as virtual_list_verses
    from virtual_quran_api import get_categories as virtual_get_categories

logger = logging.getLogger(__name__)

SURAH_NAMES_EN = {
    2: "Al-Baqarah",
    3: "Ali 'Imran",
    4: "An-Nisa",
    8: "Al-Anfal",
    9: "At-Tawbah",
    13: "Ar-Ra'd",
    14: "Ibrahim",
    16: "An-Nahl",
    17: "Al-Isra",
    31: "Luqman",
    39: "Az-Zumar",
    41: "Fussilat",
    42: "Ash-Shura",
    57: "Al-Hadid",
    65: "At-Talaq",
    94: "Ash-Sharh",
    113: "Al-Falaq",
}

SURAH_NAMES_AR = {
    2: "البقرة",
    3: "آل عمران",
    4: "النساء",
    8: "الأنفال",
    9: "التوبة",
    13: "الرعد",
    14: "إبراهيم",
    16: "النحل",
    17: "الإسراء",
    31: "لقمان",
    39: "الزمر",
    41: "فصلت",
    42: "الشورى",
    57: "الحديد",
    65: "الطلاق",
    94: "الشرح",
    113: "الفلق",
}


def _safe_int(value, fallback=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


@lru_cache(maxsize=512)
def fetch_verse(chapter, verse, translation_id="131"):
    """Fetch verse details from the local virtual Quran dataset (no external API call)."""
    chapter_num = _safe_int(chapter)
    verse_num = _safe_int(verse)
    if chapter_num is None or verse_num is None:
        return None

    verse_key = f"{chapter_num}:{verse_num}"
    data = virtual_get_by_key(verse_key=verse_key, translations=translation_id, words=False)
    if not data or "verse" not in data:
        logger.warning("Virtual Quran verse not found in sample dataset: %s", verse_key)
        fallback = virtual_list_verses(limit=1, randomize=True, translations=translation_id)
        if fallback:
            data = {"verse": (fallback[0] or {}).get("verse") or {}}
        else:
            return None

    item = data.get("verse") or {}
    translations = item.get("translations") or []

    requested_translation_id = _safe_int(translation_id)
    primary_translation = ""
    secondary_translation = ""

    if translations:
        selected = translations[0]
        if requested_translation_id is not None:
            for tr in translations:
                if _safe_int(tr.get("resource_id")) == requested_translation_id:
                    selected = tr
                    break
        primary_translation = str(selected.get("text") or "")

        if requested_translation_id is not None:
            for tr in translations:
                if _safe_int(tr.get("resource_id")) != requested_translation_id:
                    secondary_translation = str(tr.get("text") or "")
                    break

    audio_url = str((item.get("audio") or {}).get("url") or "")

    resolved_chapter = _safe_int(item.get("chapter_id"), chapter_num)
    resolved_verse = _safe_int(item.get("verse_number"), verse_num)
    resolved_key = str(item.get("verse_key") or f"{resolved_chapter}:{resolved_verse}")

    return {
        "chapter": resolved_chapter,
        "verse": resolved_verse,
        "verse_key": resolved_key,
        "arabic": str(item.get("text_uthmani") or ""),
        "translation": primary_translation,
        "secondary_translation": secondary_translation,
        "surah_name": SURAH_NAMES_EN.get(resolved_chapter, f"Surah {resolved_chapter}"),
        "surah_name_ar": SURAH_NAMES_AR.get(resolved_chapter, ""),
        "audio": audio_url,
        "audio_url": audio_url,
        "success": True,
    }


def get_chapters():
    """Build chapter list from the local virtual Quran dataset."""
    chapters = {}

    for category in virtual_get_categories():
        rows = virtual_list_verses(category=category, limit=1000)
        for row in rows:
            verse = (row or {}).get("verse") or {}
            chapter_id = _safe_int(verse.get("chapter_id"))
            if chapter_id is None:
                continue

            item = chapters.setdefault(
                chapter_id,
                {
                    "id": chapter_id,
                    "name_simple": SURAH_NAMES_EN.get(chapter_id, f"Surah {chapter_id}"),
                    "name_arabic": SURAH_NAMES_AR.get(chapter_id, ""),
                    "verses_count": 0,
                },
            )
            item["verses_count"] += 1

    return [chapters[k] for k in sorted(chapters.keys())]


def get_tafsir(chapter, verse):
    """Return a local tafsir placeholder for virtual mode."""
    return f"Tafsir text is not bundled in virtual mode for {chapter}:{verse}."
