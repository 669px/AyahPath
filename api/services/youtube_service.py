import hashlib
import logging
import time
from urllib.parse import quote_plus
import requests
try:
    from ..models.mappings import YOUTUBE_VIDEOS
except ImportError:
    from models.mappings import YOUTUBE_VIDEOS
logger = logging.getLogger(__name__)
HTTP = requests.Session()
HTTP.headers.update({"User-Agent": "AyahPath/1.0"})
_YT_AVAIL_CACHE = {}
_YT_AVAIL_TTL_S = 60 * 60 * 12
_YT_CACHE = {}
_YT_CACHE_TTL_S = 60 * 60 * 24
def youtube_is_available(video_id):
    now = time.time()
    cached = _YT_AVAIL_CACHE.get(video_id)
    if cached and (now - cached[1]) < _YT_AVAIL_TTL_S:
        return cached[0]
    try:
        response = HTTP.get(
            "https://www.youtube.com/oembed",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            timeout=4,
        )
        ok = response.status_code == 200
    except requests.RequestException as exc:
        logger.debug("YouTube availability check failed for %s: %s", video_id, exc)
        ok = False
    _YT_AVAIL_CACHE[video_id] = (ok, now)
    return ok
def normalize_video_entry(video):
    title = (video or {}).get("title", "Islamic Reminder")
    channel = (video or {}).get("channel", "YouTube")
    video_id = (video or {}).get("id", "")
    query = (video or {}).get("query") or f"{channel} {title}".strip()
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    is_working_video = bool(video_id) and youtube_is_available(video_id)
    watch_url = f"https://www.youtube.com/watch?v={video_id}" if is_working_video else search_url
    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if is_working_video else ""
    return {
        "id": video_id,
        "title": title,
        "channel": channel,
        "query": query,
        "url": watch_url,
        "search_url": search_url,
        "thumbnail_url": thumbnail_url,
        "link_type": "video" if is_working_video else "search",
    }
def get_videos_for_scenario(scenario_id):
    cache_key = hashlib.md5(scenario_id.encode()).hexdigest()[:16]
    now = time.time()
    cached = _YT_CACHE.get(cache_key)
    if cached and (now - cached[1]) < _YT_CACHE_TTL_S:
        return cached[0]
    videos = YOUTUBE_VIDEOS.get(scenario_id, YOUTUBE_VIDEOS.get("_default", []))
    prepared = [normalize_video_entry(video) for video in videos[:2]]
    _YT_CACHE[cache_key] = (prepared, now)
    return prepared
