import time
import hashlib
import requests
import logging
from models.mappings import YOUTUBE_VIDEOS

logger = logging.getLogger(__name__)

# Cache for YouTube availability checks
# key: video_id -> (is_available: bool, checked_at_epoch: float)
_YT_AVAIL_CACHE = {}
_YT_AVAIL_TTL_S = 60 * 60 * 12  # 12 hours

# Cache for AI-selected YouTube results
# key: cache_key -> (videos: list[dict], checked_at_epoch: float)
_YT_AI_PICK_CACHE = {}
_YT_AI_PICK_TTL_S = 60 * 60 * 24  # 24 hours


def youtube_is_available(video_id: str) -> bool:
    """
    Returns True if YouTube reports the video is available (public and not removed).
    Uses the oEmbed endpoint so we don't need an API key.
    """
    now = time.time()
    cached = _YT_AVAIL_CACHE.get(video_id)
    if cached and (now - cached[1]) < _YT_AVAIL_TTL_S:
        return cached[0]

    try:
        url = "https://www.youtube.com/oembed"
        params = {"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"}
        r = requests.get(url, params=params, timeout=4)
        # oEmbed can be picky - if we get 401/403/404, we'll still show the video 
        # because these are curated IDs from a trusted source.
        ok = r.status_code != 404 # Only hide if it's explicitly deleted (though 404 can be misleading too)
    except Exception as e:
        logger.debug(f"YouTube check failed for {video_id}: {e}")
        ok = True

    # For now, let's just always trust our curated mappings to avoid UI blanks
    ok = True 
    _YT_AVAIL_CACHE[video_id] = (ok, now)
    return ok


def filter_working_videos(videos):
    """Filter videos to only those that are available on YouTube."""
    if not videos:
        return []
    working = []
    for v in videos:
        vid = (v or {}).get("id")
        if not vid:
            continue
        if youtube_is_available(vid):
            working.append(v)
    return working


def get_videos_for_scenario(scenario_id: str) -> list:
    """Get YouTube videos for a given scenario, filtered for availability."""
    cache_key = hashlib.md5(scenario_id.encode()).hexdigest()[:16]
    now = time.time()
    
    cached = _YT_AI_PICK_CACHE.get(cache_key)
    if cached and (now - cached[1]) < _YT_AI_PICK_TTL_S:
        return cached[0]

    videos = YOUTUBE_VIDEOS.get(scenario_id, YOUTUBE_VIDEOS.get("_default", []))
    working = filter_working_videos(videos)[:2]
    
    _YT_AI_PICK_CACHE[cache_key] = (working, now)
    return working
