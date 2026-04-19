import html
import logging
import re
from functools import lru_cache

try:
    from ..config import Config
    from .quran_foundation_client import quran_foundation
    from .virtual_quran_api import get_by_key as virtual_get_by_key
    from .virtual_quran_api import list_verses as virtual_list_verses
    from .virtual_quran_api import get_categories as virtual_get_categories
except ImportError:
    from config import Config
    from services.quran_foundation_client import quran_foundation
    from services.virtual_quran_api import get_by_key as virtual_get_by_key
    from services.virtual_quran_api import list_verses as virtual_list_verses
    from services.virtual_quran_api import get_categories as virtual_get_categories

logger = logging.getLogger(__name__)

HTML_TAG_RE = re.compile(r"<[^>]+>")

SURAH_NAMES_EN = {
    1: "Al-Fatihah",
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
    42: "Ash-Shuraa",
    57: "Al-Hadid",
    65: "At-Talaq",
    94: "Ash-Sharh",
    113: "Al-Falaq",
}

SURAH_NAMES_AR = {
    1: "الفاتحة",
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


def _clean_text(value):
    text = html.unescape(str(value or ""))
    return HTML_TAG_RE.sub("", text).strip()


def _translation_ids(translation_id):
    primary = _safe_int(Config.QURAN_DEFAULT_TRANSLATION, 131)
    requested = _safe_int(translation_id, primary)
    ids = [primary]
    if requested not in ids:
        ids.append(requested)
    return ",".join(str(item) for item in ids)


def _find_translation(translations, resource_id):
    resource_id = _safe_int(resource_id)
    if resource_id is None:
        return ""
    for item in translations or []:
        if _safe_int(item.get("resource_id")) == resource_id:
            return _clean_text(item.get("text"))
    return ""


def _first_translation(translations):
    for item in translations or []:
        text = _clean_text(item.get("text"))
        if text:
            return text
    return ""


def _audio_from_item(item, chapter, verse):
    audio = item.get("audio") or {}
    if isinstance(audio, dict):
        url = audio.get("url") or audio.get("audio_url")
        if url:
            if str(url).startswith("//"):
                return f"https:{url}"
            return str(url)
    return f"https://everyayah.com/data/Abdul_Basit_Murattal_192kbps/{chapter:03d}{verse:03d}.mp3"


def _map_verse_for_ui(item, requested_translation_id="131"):
    chapter = _safe_int(item.get("chapter_id"))
    verse = _safe_int(item.get("verse_number"))
    verse_key = str(item.get("verse_key") or "")

    if chapter is None or verse is None:
        if ":" in verse_key:
            left, right = verse_key.split(":", 1)
            chapter = _safe_int(left)
            verse = _safe_int(right)
    if chapter is None or verse is None:
        return None

    translations = item.get("translations") or []
    primary_id = _safe_int(Config.QURAN_DEFAULT_TRANSLATION, 131)
    requested_id = _safe_int(requested_translation_id, primary_id)
    primary_translation = _find_translation(translations, primary_id) or _first_translation(translations)
    secondary_translation = ""
    if requested_id != primary_id:
        secondary_translation = _find_translation(translations, requested_id)
        if secondary_translation == primary_translation:
            secondary_translation = ""

    audio_url = _audio_from_item(item, chapter, verse)

    return {
        "chapter": chapter,
        "verse": verse,
        "verse_key": verse_key or f"{chapter}:{verse}",
        "arabic": str(item.get("text_uthmani") or item.get("text_uthmani_simple") or item.get("text_imlaei") or ""),
        "translation": primary_translation,
        "secondary_translation": secondary_translation,
        "surah_name": str(item.get("chapter", {}).get("name_simple") or SURAH_NAMES_EN.get(chapter, f"Surah {chapter}")),
        "surah_name_ar": str(item.get("chapter", {}).get("name_arabic") or SURAH_NAMES_AR.get(chapter, "")),
        "audio": audio_url,
        "audio_url": audio_url,
        "success": True,
    }


def content_api_get(path, params=None):
    """Return an official Quran Foundation response when credentials exist."""
    return quran_foundation.get_or_none(path, params=params)


def _fetch_official_verse(verse_key, translation_id):
    params = {
        "language": "en",
        "words": "false",
        "translations": _translation_ids(translation_id),
        "audio": Config.QURAN_DEFAULT_RECITATION,
        "fields": ",".join(
            [
                "text_uthmani",
                "text_uthmani_simple",
                "text_imlaei",
                "chapter_id",
                "verse_number",
                "verse_key",
                "juz_number",
                "hizb_number",
                "page_number",
            ]
        ),
    }
    payload = content_api_get(f"verses/by_key/{verse_key}", params=params)
    item = (payload or {}).get("verse")
    if not item:
        return None
    return _map_verse_for_ui(item, requested_translation_id=translation_id)


def _fetch_local_verse(chapter, verse, translation_id):
    verse_key = f"{chapter}:{verse}"
    data = virtual_get_by_key(verse_key=verse_key, translations=None, words=False)
    if not data or "verse" not in data:
        logger.warning("Virtual Quran verse not found in sample dataset: %s", verse_key)
        fallback = virtual_list_verses(limit=1, randomize=True, translations=None)
        if fallback:
            data = {"verse": (fallback[0] or {}).get("verse") or {}}
        else:
            return None

    return _map_verse_for_ui(data.get("verse") or {}, requested_translation_id=translation_id)


@lru_cache(maxsize=512)
def fetch_verse(chapter, verse, translation_id="131"):
    """Fetch verse details while keeping the AyahPath UI response stable.

    With Quran Foundation credentials, this uses the official Content API.
    Without credentials, or if the upstream is unavailable, it falls back to
    the bundled local virtual dataset.
    """
    chapter_num = _safe_int(chapter)
    verse_num = _safe_int(verse)
    if chapter_num is None or verse_num is None:
        return None

    verse_key = f"{chapter_num}:{verse_num}"
    official = _fetch_official_verse(verse_key, translation_id)
    if official and official.get("translation"):
        return official

    return _fetch_local_verse(chapter_num, verse_num, translation_id)


def get_chapters():
    """Return chapter data using official API when possible, local data otherwise."""
    payload = content_api_get("chapters", params={"language": "en"})
    if payload and payload.get("chapters"):
        return payload["chapters"]

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
                    "chapter_number": chapter_id,
                    "name_simple": SURAH_NAMES_EN.get(chapter_id, f"Surah {chapter_id}"),
                    "name_arabic": SURAH_NAMES_AR.get(chapter_id, ""),
                    "verses_count": 0,
                },
            )
            item["verses_count"] += 1

    return [chapters[k] for k in sorted(chapters.keys())]


def get_tafsir(chapter, verse):
    """Return tafsir text from official API when available, else local placeholder."""
    verse_key = f"{chapter}:{verse}"
    tafsir_id = Config.QURAN_DEFAULT_TAFSIR
    candidates = [
        (f"tafsirs/{tafsir_id}", {"verse_key": verse_key}),
        (f"tafsirs/{tafsir_id}/by_ayah/{verse_key}", None),
        (f"tafsirs/by_ayah/{verse_key}", {"tafsirs": tafsir_id}),
    ]
    for path, params in candidates:
        payload = content_api_get(path, params=params)
        tafsir = (payload or {}).get("tafsir")
        if isinstance(tafsir, dict):
            text = _clean_text(tafsir.get("text") or tafsir.get("text_uthmani"))
            if text:
                return text
        tafsirs = (payload or {}).get("tafsirs") or []
        for item in tafsirs:
            text = _clean_text(item.get("text") or item.get("text_uthmani"))
            if text:
                return text

    return f"Tafsir text is not bundled in virtual mode for {verse_key}."
