import argparse
import json
import os
from typing import Any
from urllib import error, parse, request


class TreeNationConnector:
    def __init__(self, api_key: str, base_url: str = "https://api.tree-nation.com") -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        timeout: int = 30,
    ) -> Any:
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        query = f"?{parse.urlencode(params)}" if params else ""
        url = f"{self.base_url}{endpoint}{query}"

        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = request.Request(url=url, method=method.upper(), data=body)
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", "Bearer " + self.api_key)
        if body is not None:
            req.add_header("Content-Type", "application/json")

        try:
            with request.urlopen(req, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                raw = response.read().decode(charset)
                if not raw:
                    return None
                content_type = response.headers.get("Content-Type", "")
                return json.loads(raw) if "application/json" in content_type else raw
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API request failed with status {exc.code}: {detail}") from exc


def _parse_key_values(values: list[str] | None) -> dict[str, str] | None:
    if not values:
        return None

    output: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Expected key=value format, got '{item}'")
        key, value = item.split("=", 1)
        output[key] = value
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Call Tree-Nation API endpoints from the Postman documentation.",
    )
    parser.add_argument("endpoint", help="API endpoint path, e.g. /v1/projects")
    parser.add_argument("--method", default="GET", help="HTTP method (GET, POST, etc.)")
    parser.add_argument(
        "--param",
        action="append",
        help="Query param in key=value format (repeatable)",
    )
    parser.add_argument(
        "--data",
        help="JSON payload for request body, e.g. '{\"name\":\"my-project\"}'",
    )

    args = parser.parse_args()

    api_key = os.environ.get("TREE_NATION_API_KEY")
    if not api_key:
        raise SystemExit("TREE_NATION_API_KEY environment variable is required")

    params = _parse_key_values(args.param)
    payload = json.loads(args.data) if args.data else None

    connector = TreeNationConnector(api_key=api_key)
    result = connector.request(
        args.method,
        args.endpoint,
        params=params,
        payload=payload,
    )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
