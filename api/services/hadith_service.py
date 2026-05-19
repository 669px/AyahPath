import logging
import random
import time
from urllib.parse import quote_plus
import requests

try:
    from ..config import Config
except ImportError:
    from config import Config

logger = logging.getLogger(__name__)

HTTP = requests.Session()
HTTP.headers.update({'User-Agent': 'AyahPath/1.0', 'Accept': 'application/json'})

HADITH_API_BASE = 'https://www.hadithapi.com/api'
HADITH_TIMEOUT_S = 8
_HADITH_CACHE = {}
_HADITH_CACHE_TTL_S = 60 * 60 * 12

SCENARIO_HADITH_KEYWORDS = {
    'lying': ['lie', 'truthful'],
    'patience': ['patience'],
    'anger': ['anger'],
    'charity': ['charity'],
    'forgiveness': ['forgive'],
    'gratitude': ['grateful'],
    'trust_in_allah': ['trust'],
    'jealousy': ['envy'],
    'stress': ['anxious', 'worry'],
    'arrogance': ['pride', 'arrogant'],
}

PREFERRED_BOOK_SLUGS = ['sahih-bukhari', 'sahih-muslim', 'al-tirmidhi', 'abu-dawood']


def _cache_get(key):
    entry = _HADITH_CACHE.get(key)
    if not entry:
        return None
    if time.time() - entry[1] > _HADITH_CACHE_TTL_S:
        _HADITH_CACHE.pop(key, None)
        return None
    return entry[0]


def _cache_set(key, value):
    _HADITH_CACHE[key] = (value, time.time())


def _clean(text):
    return str(text or '').strip()


def _is_meaningful(value, min_len=20):
    text = _clean(value)
    return len(text) >= min_len


def _slugify(text):
    text = _clean(text).lower()
    if not text:
        return ''
    out = []
    prev_dash = False
    for ch in text:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif ch in {' ', '-', '_', '/', '\\', "'", '`'}:
            if not prev_dash:
                out.append('-')
                prev_dash = True
    slug = ''.join(out).strip('-')
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug


def _book_to_collection_slug(book_slug, book_name):
    seeds = [_slugify(book_slug), _slugify(book_name)]
    prefixes = ('sahih-', 'sunan-', 'jami-', 'al-', 'as-', 'an-', 'at-')
    candidates = []
    for seed in seeds:
        if not seed:
            continue
        variants = {seed, seed.replace('-', '')}
        for prefix in prefixes:
            if seed.startswith(prefix) and len(seed) > len(prefix):
                trimmed = seed[len(prefix):]
                variants.add(trimmed)
                variants.add(trimmed.replace('-', ''))
        tokenized = [tok for tok in seed.split('-') if tok and tok not in {'al', 'as', 'an', 'at'}]
        if tokenized:
            variants.add(''.join(tokenized))
        for item in variants:
            if item and item not in candidates:
                candidates.append(item)
    # Prefer short canonical-looking candidates first (e.g. bukhari, muslim, tirmidhi).
    candidates.sort(key=len)
    return candidates[0] if candidates else ''


def _sunnah_source_url(book_slug, book_name, hadith_number):
    collection = _book_to_collection_slug(book_slug, book_name)
    number = _clean(hadith_number)
    if not collection or not number:
        # Always return a navigable Sunnah search URL when a canonical path cannot be inferred.
        query = ' '.join(part for part in (book_name, f'hadith {number}') if _clean(part))
        return f'https://sunnah.com/search?q={quote_plus(query)}' if query else ''
    return f'https://sunnah.com/{collection}:{number}'


def _normalize_hadith(item):
    if not isinstance(item, dict):
        return None
    arabic = _clean(item.get('hadithArabic'))
    english = _clean(item.get('hadithEnglish'))
    urdu = _clean(item.get('hadithUrdu'))
    if not _is_meaningful(english) and not _is_meaningful(arabic):
        return None
    book_info = item.get('book') or {}
    chapter_info = item.get('chapter') or {}
    book_name = _clean(book_info.get('bookName') or item.get('bookName'))
    book_slug = _clean(book_info.get('bookSlug') or item.get('bookSlug'))
    chapter_number = _clean(chapter_info.get('chapterNumber') or item.get('chapterId'))
    chapter_en = _clean(chapter_info.get('chapterEnglish'))
    chapter_ar = _clean(chapter_info.get('chapterArabic'))
    hadith_number = _clean(item.get('hadithNumber'))
    status = _clean(item.get('status'))
    narrator_en = _clean(item.get('englishNarrator'))
    narrator_ur = _clean(item.get('urduNarrator'))
    heading_en = _clean(item.get('headingEnglish'))
    heading_ar = _clean(item.get('headingArabic'))
    reference_parts = []
    if book_name:
        reference_parts.append(book_name)
    if chapter_en:
        reference_parts.append(chapter_en)
    elif chapter_number:
        reference_parts.append(f'Chapter {chapter_number}')
    if hadith_number:
        reference_parts.append(f'Hadith {hadith_number}')
    return {
        'id': _clean(item.get('id')),
        'hadith_number': hadith_number,
        'status': status,
        'book_name': book_name,
        'book_slug': book_slug,
        'chapter_number': chapter_number,
        'chapter_en': chapter_en,
        'chapter_ar': chapter_ar,
        'heading_en': heading_en,
        'heading_ar': heading_ar,
        'narrator_en': narrator_en,
        'narrator_ur': narrator_ur,
        'arabic': arabic,
        'english': english,
        'urdu': urdu,
        'reference': ' • '.join(reference_parts),
        'source_url': (
            _sunnah_source_url(book_slug, book_name, hadith_number)
            or (f'https://www.hadithapi.com/hadiths/{item.get("id")}' if item.get('id') else '')
        ),
    }


def _request_hadiths(params):
    if not Config.HADITH_API_KEY:
        logger.debug('HADITH_API_KEY not set; skipping live request')
        return []
    query = {'apiKey': Config.HADITH_API_KEY, **{k: v for k, v in params.items() if v is not None and v != ''}}
    try:
        response = HTTP.get(f'{HADITH_API_BASE}/hadiths', params=query, timeout=HADITH_TIMEOUT_S)
    except requests.RequestException as exc:
        logger.warning('Hadith API request failed: %s', exc)
        return []
    if response.status_code != 200:
        logger.warning('Hadith API non-200 (%s): %s', response.status_code, response.text[:160])
        return []
    try:
        payload = response.json() or {}
    except ValueError:
        logger.warning('Hadith API returned non-JSON payload')
        return []
    container = payload.get('hadiths')
    if isinstance(container, dict):
        rows = container.get('data') or []
    elif isinstance(container, list):
        rows = container
    else:
        rows = []
    normalized = []
    for row in rows:
        mapped = _normalize_hadith(row)
        if mapped:
            normalized.append(mapped)
    return normalized


def _search_with_fallback(keywords, paginate=10):
    for keyword in keywords:
        items = _request_hadiths({'hadithEnglish': keyword, 'status': 'Sahih', 'paginate': paginate})
        if items:
            return items
        items = _request_hadiths({'hadithEnglish': keyword, 'paginate': paginate})
        if items:
            return items
    return []


def get_hadiths_for_scenario(scenario_id, limit=2):
    if not scenario_id:
        return []
    cache_key = f'scenario::{scenario_id}::{limit}'
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    keywords = SCENARIO_HADITH_KEYWORDS.get(scenario_id) or [scenario_id.replace('_', ' ')]
    items = _search_with_fallback(keywords)
    if not items:
        _cache_set(cache_key, [])
        return []
    preferred = [h for h in items if h.get('book_slug') in PREFERRED_BOOK_SLUGS]
    pool = preferred or items
    pool = [h for h in pool if _is_meaningful(h.get('english'), min_len=30)] or pool
    sample = random.sample(pool, min(limit, len(pool)))
    _cache_set(cache_key, sample)
    return sample


