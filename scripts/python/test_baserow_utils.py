import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch

import requests


config = types.ModuleType("config")
config.BASEROW_URL = ""
config.BASEROW_TOKEN = None
config.br_client = Mock()
with patch.dict(sys.modules, {"config": config}):
    baserow_utils = importlib.import_module("baserow_utils")


class LoadTableRowsTests(unittest.TestCase):
    def test_retries_transient_request_error(self):
        rows = [{"id": 1}]
        with (
            patch.object(baserow_utils.br_client, "yield_rows",
                         side_effect=[requests.exceptions.SSLError(), rows]),
            patch.object(baserow_utils, "sleep") as sleep,
        ):
            self.assertEqual(baserow_utils._load_table_rows("1499"), rows)

        sleep.assert_called_once_with(1)

    def test_raises_after_retry_limit(self):
        error = requests.exceptions.SSLError()
        with (
            patch.object(baserow_utils.br_client, "yield_rows", side_effect=error) as yield_rows,
            patch.object(baserow_utils, "sleep") as sleep,
        ):
            with self.assertRaises(requests.exceptions.SSLError):
                baserow_utils._load_table_rows("1499")

        self.assertEqual(yield_rows.call_count, 3)
        self.assertEqual(sleep.call_count, 2)


if __name__ == "__main__":
    unittest.main()
