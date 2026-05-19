import json
import logging
import os
import random
from collections import defaultdict
from functools import lru_cache
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'quran_virtual_verses.json')
KEYWORD_CATEGORY_MAP = {'stress': ('stress', 'anxiety', 'worried', 'worry', 'fear', 'panic', 'overwhelmed', 'hardship'), 'anger': ('angry', 'anger', 'furious', 'mad', 'rage', 'temper'), 'jealousy': ('jealous', 'envy', 'envious', 'resent'), 'gratitude': ('grateful', 'gratitude', 'thankful', 'blessing', 'blessings'), 'forgiveness': ('forgive', 'forgiveness', 'repent', 'mercy', 'pardon'), 'trust_in_allah': ('trust', 'tawakkul', 'rely', 'future', 'uncertain', 'reliance'), 'patience': ('patient', 'patience', 'sabr', 'waiting', 'trial', 'trials'), 'charity': ('charity', 'donate', 'donation', 'sadaqah', 'giving'), 'lying': ('lie', 'lying', 'dishonest', 'false', 'truth'), 'arrogance': ('arrogant', 'arrogance', 'pride', 'ego', 'boast')}

def _to_bool(value):
    return str(value or '').strip().lower() in {'1', 'true', 'yes', 'on'}

def _parse_translation_ids(value):
    if value is None or str(value).strip() == '':
        return None
    out = []
    for part in str(value).split(','):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            continue
    return out or None

def _safe_int(value, fallback=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback

def _copy_verse(verse, translation_ids=None, include_words=False):
    item = dict(verse)
    translations = [dict(t) for t in verse.get('translations', [])]
    if translation_ids is not None:
        translations = [t for t in translations if int(t.get('resource_id', -1)) in translation_ids]
    item['translations'] = translations
    if include_words:
        item['words'] = list(verse.get('words', []))
    else:
        item['words'] = []
    item['audio'] = dict(verse.get('audio') or {})
    return item

def _verse_sort_key(verse):
    key = str(verse.get('verse_key', '0:0'))
    if ':' not in key:
        return (9999, 9999)
    left, right = key.split(':', 1)
    try:
        return (int(left), int(right))
    except ValueError:
        return (9999, 9999)

@lru_cache(maxsize=1)
def _load_index():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception as exc:
        logger.error('Failed loading virtual Quran data: %s', exc)
        payload = {'verses': [], 'metadata': {}}
    verses = payload.get('verses', [])
    by_key = {}
    by_category = defaultdict(list)
    for row in verses:
        category = str(row.get('category', '')).strip().lower()
        verse = row.get('verse') or {}
        key = str(verse.get('verse_key', '')).strip()
        if not category or not key:
            continue
        by_key[key] = verse
        by_category[category].append(verse)
    for category in by_category:
        by_category[category].sort(key=_verse_sort_key)
    metadata = dict(payload.get('metadata') or {})
    metadata['total_verses'] = sum((len(v) for v in by_category.values()))
    metadata['categories'] = {k: len(v) for k, v in sorted(by_category.items())}
    return {'by_key': by_key, 'by_category': dict(by_category), 'metadata': metadata}

def get_metadata():
    return dict(_load_index()['metadata'])

def get_categories():
    return sorted(_load_index()['by_category'].keys())

def get_by_key(verse_key, translations=None, words=False):
    normalized_key = str(verse_key or '').strip()
    if not normalized_key:
        return None
    verse = _load_index()['by_key'].get(normalized_key)
    if not verse:
        return None
    translation_ids = _parse_translation_ids(translations)
    include_words = _to_bool(words)
    return {'verse': _copy_verse(verse, translation_ids=translation_ids, include_words=include_words)}

def _category_matches_from_query(text):
    q = str(text or '').strip().lower()
    if not q:
        return []
    matches = []
    for category, keywords in KEYWORD_CATEGORY_MAP.items():
        if any((k in q for k in keywords)):
            matches.append(category)
    return matches

def list_verses(category=None, query=None, limit=20, randomize=False, translations=None, words=False, chapter_number=None, page_number=None, juz_number=None):
    idx = _load_index()
    by_category = idx['by_category']
    selected = []
    if chapter_number is not None:
        selected = [verse for rows in by_category.values() for verse in rows if _safe_int(verse.get('chapter_id'), -1) == _safe_int(chapter_number)]
    elif page_number is not None:
        selected = [verse for rows in by_category.values() for verse in rows if _safe_int(verse.get('page_number'), -1) == _safe_int(page_number)]
    elif juz_number is not None:
        selected = [verse for rows in by_category.values() for verse in rows if _safe_int(verse.get('juz_number'), -1) == _safe_int(juz_number)]
    elif category:
        selected = list(by_category.get(str(category).strip().lower(), []))
    elif query:
        categories = _category_matches_from_query(query)
        for matched in categories:
            selected.extend(by_category.get(matched, []))
    else:
        for rows in by_category.values():
            selected.extend(rows)
    if not selected:
        return []
    dedup = {}
    for verse in selected:
        dedup[verse.get('verse_key')] = verse
    selected = list(dedup.values())
    if _to_bool(randomize):
        random.shuffle(selected)
    else:
        selected.sort(key=_verse_sort_key)
    try:
        limit = max(1, min(int(limit), 100))
    except (TypeError, ValueError):
        limit = 20
    translation_ids = _parse_translation_ids(translations)
    include_words = _to_bool(words)
    result = []
    for verse in selected[:limit]:
        category_name = None
        verse_key = verse.get('verse_key')
        for cat_name, rows in by_category.items():
            if any((r.get('verse_key') == verse_key for r in rows)):
                category_name = cat_name
                break
        result.append({'category': category_name, 'verse': _copy_verse(verse, translation_ids=translation_ids, include_words=include_words)})
    return result

def paginate_verses(rows, page=1, per_page=10):
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = max(1, min(int(per_page), 50))
    except (TypeError, ValueError):
        per_page = 10
    total_records = len(rows)
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    return {'verses': rows[start:end], 'pagination': {'per_page': per_page, 'current_page': page, 'next_page': page + 1 if page < total_pages else None, 'total_pages': total_pages, 'total_records': total_records}}
