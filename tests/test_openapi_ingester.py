from pathlib import Path
from typing import Any

import httpx

from agentlab.tools.openapi.ingest import ingest_openapi
from agentlab.tools.registry import get_tool


class MockTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/pets" and request.method == "GET":
            return httpx.Response(200, json={"items": ["a", "b"]})
        if request.url.path.startswith("/pets/") and request.method == "GET":
            pid = request.url.path.split("/")[-1]
            return httpx.Response(200, json={"id": pid, "name": "x"})
        if request.url.path == "/pets" and request.method == "POST":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(404, text="not found")


def test_ingest_registers_tools(tmp_path: Path, monkeypatch):
    spec = Path("tests/fixtures/petstore.yaml")
    names = ingest_openapi(spec, tag="pet", base_url_override="https://example.com")
    assert any(n.endswith("listPets") for n in names)
    assert get_tool("pet.listPets") is not None

    # Exercise the tool call with mock transport
    import agentlab.tools.openapi.ingest as ing
    import agentlab.tools.runtime.http_tool as rt

    client = httpx.Client(transport=MockTransport())
    monkeypatch.setattr(rt, "httpx", httpx)

    def http_call_with_client(method: str, base_url: str, path: str, **kwargs: Any) -> str:
        return rt.http_call(method, base_url, path, client=client, **kwargs)

    # Patch where the closure resolves from (ingest module)
    monkeypatch.setattr(ing, "http_call", http_call_with_client)

    tool = get_tool("pet.listPets")
    assert tool is not None
    out = tool(limit=2)
    assert "items" in out
