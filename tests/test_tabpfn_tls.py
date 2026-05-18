from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_script_module(filename: str, module_name: str):
    path = PROJECT_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCRIPT_09 = load_script_module("09_train_tabpfn_priorlabs.py", "script_09_tabpfn")


class DummyResponse:
    def __init__(self) -> None:
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return {"ok": True}


class DummyClient:
    def __init__(self, *args, **kwargs) -> None:
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def request(self, *args, **kwargs):
        return DummyResponse()

    def put(self, *args, **kwargs):
        return DummyResponse()


class TabPFNTLSTests(unittest.TestCase):
    def test_request_json_uses_resolved_verify_bundle(self) -> None:
        created: list[DummyClient] = []

        def client_factory(*args, **kwargs):
            dummy = DummyClient(*args, **kwargs)
            created.append(dummy)
            return dummy

        with (
            patch.object(SCRIPT_09, "resolve_requests_verify", return_value="C:\\temp\\bundle.pem"),
            patch.object(SCRIPT_09.httpx, "Client", side_effect=client_factory),
        ):
            SCRIPT_09.request_json("GET", "https://example.com", headers={})

        self.assertEqual(created[0].kwargs["verify"], "C:\\temp\\bundle.pem")

    def test_upload_to_signed_url_uses_resolved_verify_bundle(self) -> None:
        created: list[DummyClient] = []

        def client_factory(*args, **kwargs):
            dummy = DummyClient(*args, **kwargs)
            created.append(dummy)
            return dummy

        upload_path = PROJECT_ROOT / "data" / "interim" / "priorlabs" / "tls_test_upload.csv"
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        upload_path.write_text("a,b\n1,2\n", encoding="utf-8")
        try:
            with (
                patch.object(SCRIPT_09, "resolve_requests_verify", return_value="C:\\temp\\bundle.pem"),
                patch.object(SCRIPT_09.httpx, "Client", side_effect=client_factory),
            ):
                SCRIPT_09.upload_to_signed_url(
                    upload_path,
                    {"signed_urls": ["https://example.com/upload"], "required_headers": {"x-test": "1"}},
                )
        finally:
            upload_path.unlink(missing_ok=True)

        self.assertEqual(created[0].kwargs["verify"], "C:\\temp\\bundle.pem")


if __name__ == "__main__":
    unittest.main()
