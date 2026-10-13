import unittest
from email.message import Message
from unittest.mock import patch

from tree_nation_connector import TreeNationConnector, _parse_key_values


class FakeResponse:
    def __init__(self, body: str, content_type: str = "application/json") -> None:
        self._body = body.encode("utf-8")
        self.headers = Message()
        self.headers.add_header("Content-Type", content_type)

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TreeNationConnectorTests(unittest.TestCase):
    @patch("tree_nation_connector.request.urlopen")
    def test_get_request_parses_json_and_sets_headers(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse('{"ok": true}')

        connector = TreeNationConnector(api_key="token123")
        result = connector.request("get", "/v1/projects", params={"page": "1"})

        self.assertEqual(result, {"ok": True})
        req = mock_urlopen.call_args.args[0]
        self.assertEqual(req.get_method(), "GET")
        self.assertEqual(req.full_url, "https://api.tree-nation.com/v1/projects?page=1")
        self.assertEqual(req.headers["Authorization"], " ".join(["Bearer", "token123"]))

    @patch("tree_nation_connector.request.urlopen")
    def test_post_request_encodes_json_payload(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse('{"created": true}')

        connector = TreeNationConnector(api_key="token123")
        connector.request("post", "/v1/projects", payload={"name": "x"})

        req = mock_urlopen.call_args.args[0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.data, b'{"name": "x"}')
        self.assertEqual(req.headers["Content-type"], "application/json")


class ParseKeyValuesTests(unittest.TestCase):
    def test_parse_key_values(self):
        self.assertEqual(_parse_key_values(["a=1", "b=2"]), {"a": "1", "b": "2"})

    def test_parse_key_values_invalid_entry(self):
        with self.assertRaises(ValueError):
            _parse_key_values(["invalid"])


if __name__ == "__main__":
    unittest.main()
