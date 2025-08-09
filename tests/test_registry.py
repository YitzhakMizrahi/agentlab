from agentlab.tools.registry import register_tool, get_tool, list_tools


def sample_tool(x: int) -> int:
    return x + 1


def test_register_and_get_tool():
    register_tool("sample", sample_tool)
    fn = get_tool("sample")
    assert fn is sample_tool
    assert "sample" in list_tools()


