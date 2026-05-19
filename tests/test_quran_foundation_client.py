import unittest
from api.config import Config
from api.services.quran_foundation_client import QuranFoundationClient

class _NoAuthClient(QuranFoundationClient):

    @property
    def enabled(self):
        return False

class DummyResponse:

    def __init__(self, payload=None, should_raise=False):
        self._payload = payload or {}
        self._raise = should_raise
        self.text = '{}'

    def raise_for_status(self):
        if self._raise:
            raise RuntimeError('boom')

    def json(self):
        return self._payload

class QuranFoundationClientTests(unittest.TestCase):

    def setUp(self):
        self.old_base = Config.QURAN_MCP_BASE_URL
        self.old_cooldown = Config.QURAN_MCP_FAIL_COOLDOWN_SECONDS
        Config.QURAN_MCP_BASE_URL = 'https://example.test'
        Config.QURAN_MCP_FAIL_COOLDOWN_SECONDS = 300

    def tearDown(self):
        Config.QURAN_MCP_BASE_URL = self.old_base
        Config.QURAN_MCP_FAIL_COOLDOWN_SECONDS = self.old_cooldown

    def test_returns_public_payload_when_available(self):
        client = _NoAuthClient()
        client.session.get = lambda *a, **k: DummyResponse(payload={'chapters': [{'id': 1}]})
        result = client.get('chapters')
        self.assertIn('chapters', result)
        self.assertEqual(result['chapters'][0]['id'], 1)

    def test_public_failure_sets_cooldown_and_returns_none_when_no_auth_fallback(self):
        client = _NoAuthClient()
        client.session.get = lambda *a, **k: DummyResponse(should_raise=True)
        result = client.get('chapters')
        self.assertIsNone(result)
        self.assertGreater(client._public_fail_until, 0)

    def test_cooldown_skips_public_http_call(self):
        client = _NoAuthClient()
        calls = {'count': 0}

        def failing_get(*a, **k):
            calls['count'] += 1
            return DummyResponse(should_raise=True)
        client.session.get = failing_get
        _ = client.get('chapters')
        _ = client.get('chapters')
        self.assertEqual(calls['count'], 1)
if __name__ == '__main__':
    unittest.main()
