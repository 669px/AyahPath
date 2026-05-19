import logging
import time
from urllib.parse import urljoin
import requests
from requests import RequestException
try:
    from ..config import Config
except ImportError:
    from config import Config
logger = logging.getLogger(__name__)

class QuranFoundationClient:

    def __init__(self):
        self.session = requests.Session()
        self._access_token = ''
        self._expires_at = 0
        self._public_fail_until = 0.0

    @property
    def enabled(self):
        mode = Config.QURAN_USE_OFFICIAL_API
        has_credentials = bool(Config.QURAN_CLIENT_ID and Config.QURAN_CLIENT_SECRET)
        if mode in {'0', 'false', 'no', 'local'}:
            return False
        if mode in {'1', 'true', 'yes', 'official'}:
            return has_credentials
        return has_credentials

    def _base_url(self, value):
        return str(value or '').rstrip('/') + '/'

    def _token_url(self):
        return urljoin(self._base_url(Config.QURAN_AUTH_BASE_URL), 'oauth2/token')

    def _content_url(self, path, base_url=None):
        normalized = str(path or '').lstrip('/')
        if not normalized.startswith('content/api/v4/'):
            normalized = f'content/api/v4/{normalized}'
        return urljoin(self._base_url(base_url or Config.QURAN_API_BASE_URL), normalized)

    def _get_token(self, force=False):
        now = time.time()
        if not force and self._access_token and (now < self._expires_at - 60):
            return self._access_token
        response = self.session.post(self._token_url(), auth=(Config.QURAN_CLIENT_ID, Config.QURAN_CLIENT_SECRET), headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'grant_type': 'client_credentials', 'scope': 'content'}, timeout=Config.QURAN_API_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        token = payload.get('access_token')
        if not token:
            raise RuntimeError('Quran Foundation token response did not include access_token')
        self._access_token = token
        self._expires_at = now + int(payload.get('expires_in') or 3600)
        return token

    def _get_public_content(self, path, params=None):
        base = str(Config.QURAN_MCP_BASE_URL or '').strip()
        if not base:
            return None
        if self._public_fail_until and time.time() < self._public_fail_until:
            return None
        response = self.session.get(self._content_url(path, base_url=base), params=params or {}, headers={'Accept': 'application/json'}, timeout=Config.QURAN_MCP_TIMEOUT_SECONDS)
        response.raise_for_status()
        self._public_fail_until = 0.0
        return response.json() if response.text else {}

    def get(self, path, params=None, retry=True):
        try:
            public_payload = self._get_public_content(path, params=params)
            if public_payload is not None:
                return public_payload
        except RequestException as exc:
            self._public_fail_until = time.time() + Config.QURAN_MCP_FAIL_COOLDOWN_SECONDS
            logger.warning('Public Quran MCP fallback for %s: %s', path, exc)
        except Exception as exc:
            self._public_fail_until = time.time() + Config.QURAN_MCP_FAIL_COOLDOWN_SECONDS
            logger.warning('Unexpected Quran MCP error for %s: %s', path, exc)
        if not self.enabled:
            return None
        token = self._get_token()
        response = self.session.get(self._content_url(path), params=params or {}, headers={'x-auth-token': token, 'x-client-id': Config.QURAN_CLIENT_ID, 'Accept': 'application/json'}, timeout=Config.QURAN_API_TIMEOUT_SECONDS)
        if response.status_code == 401 and retry:
            token = self._get_token(force=True)
            response = self.session.get(self._content_url(path), params=params or {}, headers={'x-auth-token': token, 'x-client-id': Config.QURAN_CLIENT_ID, 'Accept': 'application/json'}, timeout=Config.QURAN_API_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json() if response.text else {}

    def get_or_none(self, path, params=None):
        try:
            return self.get(path, params=params)
        except Exception as exc:
            logger.warning('Quran Foundation API fallback for %s: %s', path, exc)
            return None
quran_foundation = QuranFoundationClient()
