from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.data import who_client


class WHOClientTLSTests(unittest.TestCase):
    def setUp(self) -> None:
        who_client.resolve_requests_verify.cache_clear()
        who_client.build_windows_ca_bundle.cache_clear()

    def test_resolve_requests_verify_uses_explicit_bundle_env_var(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as handle:
            bundle_path = Path(handle.name)

        try:
            with patch.dict(os.environ, {"WHO_GHO_CA_BUNDLE": str(bundle_path)}, clear=False):
                self.assertEqual(who_client.resolve_requests_verify(), str(bundle_path))
        finally:
            bundle_path.unlink(missing_ok=True)

    def test_resolve_requests_verify_can_disable_verification_explicitly(self) -> None:
        with patch.dict(os.environ, {"WHO_GHO_SSL_VERIFY": "false"}, clear=False):
            self.assertFalse(who_client.resolve_requests_verify())

    def test_resolve_requests_verify_builds_windows_bundle_when_needed(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("src.data.who_client.platform.system", return_value="Windows"),
            patch("src.data.who_client.build_windows_ca_bundle", return_value="C:\\temp\\who-gho.pem") as bundle_builder,
        ):
            self.assertEqual(who_client.resolve_requests_verify(), "C:\\temp\\who-gho.pem")
            bundle_builder.assert_called_once()


if __name__ == "__main__":
    unittest.main()
