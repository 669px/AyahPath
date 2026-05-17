import os
import unittest

from api import config


class ConfigParsingTests(unittest.TestCase):
    def test_env_float_fallbacks_on_invalid(self):
        os.environ['TMP_BAD_FLOAT'] = 'abc'
        self.assertEqual(config._env_float('TMP_BAD_FLOAT', 6), 6.0)

    def test_env_int_fallbacks_on_invalid(self):
        os.environ['TMP_BAD_INT'] = 'abc'
        self.assertEqual(config._env_int('TMP_BAD_INT', 300), 300)


if __name__ == '__main__':
    unittest.main()
