from __future__ import annotations

from typing import Any, Dict, Mapping, Optional
from urllib.parse import urlencode

import httpx


def build_url(
    base_url: str, path: str, path_params: Mapping[str, Any] | None, query: Mapping[str, Any] | None
) -> str:
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    # Path templating: replace {param} with value
    if path_params:
        for k, v in path_params.items():
            url = url.replace("{" + str(k) + "}", str(v))
    if query:
        # Remove None values
        q = {k: v for k, v in query.items() if v is not None}
        if q:
            url = url + ("&" if ("?" in url) else "?") + urlencode(q, doseq=True)
    return url


def http_call(
    method: str,
    base_url: str,
    path: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    path_params: Optional[Mapping[str, Any]] = None,
    query: Optional[Mapping[str, Any]] = None,
    json_body: Optional[Any] = None,
    timeout: float = 20.0,
    client: Optional[httpx.Client] = None,
) -> str:
    url = build_url(base_url, path, path_params, query)
    _headers = dict(headers or {})
    _client = client or httpx.Client(timeout=timeout)
    try:
        resp = _client.request(method.upper(), url, headers=_headers, json=json_body)
        resp.raise_for_status()
        try:
            data = resp.json()
            return httpx.Response(200, json=data).text  # stable JSON serialization
        except ValueError:
            return resp.text
    finally:
        if client is None:
            _client.close()
