from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import httpx
import yaml

from ..registry import register_tool
from ..runtime.http_tool import http_call


def _load_spec(source: Union[str, Path]) -> Dict[str, Any]:
    # Support http(s) URLs and local files
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        resp = httpx.get(source, timeout=20)
        resp.raise_for_status()
        text = resp.text
        # Try JSON first, then YAML
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return yaml.safe_load(text)
    # Local path
    p = Path(source)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def _infer_args(params: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    path_params: List[str] = []
    query_params: List[str] = []
    for p in params or []:
        name = p.get("name")
        loc = p.get("in")
        if not name or not loc:
            continue
        if loc == "path":
            path_params.append(name)
        elif loc == "query":
            query_params.append(name)
    return path_params, query_params


def ingest_openapi(
    spec_path: Union[str, Path], tag: str, base_url_override: str | None = None
) -> List[str]:
    """Parse a simple OpenAPI spec and register tools for GET/POST endpoints.

    Returns a list of registered tool names.
    """
    spec = _load_spec(spec_path)
    base_url = base_url_override or spec.get("servers", [{}])[0].get("url", "")
    assert base_url, "No base URL found; provide --base-url or include servers[].url in spec"

    registered: List[str] = []
    paths: Dict[str, Any] = spec.get("paths", {})
    for path, ops in paths.items():
        if not isinstance(ops, dict):
            continue
        for method in ["get", "post"]:
            op = ops.get(method)
            if not op:
                continue
            op_id = op.get("operationId") or f"{path.strip('/').replace('/', '_')}_{method}"
            tool_name = f"{tag}.{op_id}"
            params = op.get("parameters", [])
            path_params, query_params = _infer_args(params)

            # Security: if apiKey in header, read from env TOKEN
            sec_headers: Dict[str, str] = {}
            sec = spec.get("components", {}).get("securitySchemes", {}) or {}
            api_key_name = None
            for _, sch in sec.items():
                if sch.get("type") == "apiKey" and sch.get("in") == "header":
                    api_key_name = sch.get("name")
                    break
            token = None
            if api_key_name:
                env_name = f"{tag.upper()}_TOKEN"
                token = os.getenv(env_name)
                if token:
                    sec_headers[api_key_name] = token

            def make_tool(
                _base=base_url,
                _path=path,
                _method=method.upper(),
                _path_params=path_params,
                _query_params=query_params,
                _headers=sec_headers,
            ):
                def _tool(**kwargs: Any) -> str:
                    path_vals = {k: kwargs.get(k) for k in _path_params}
                    query_vals = {k: kwargs.get(k) for k in _query_params}
                    body = kwargs.get("body") if _method == "POST" else None
                    return http_call(
                        _method,
                        _base,
                        _path,
                        headers=_headers,
                        path_params=path_vals,
                        query=query_vals,
                        json_body=body,
                    )

                return _tool

            register_tool(tool_name, make_tool())
            registered.append(tool_name)

    return registered
