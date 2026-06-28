from app.server import _configure_runtime_settings, mcp


def test_configure_runtime_settings_public_host_allows_non_local_headers(
    monkeypatch,
) -> None:
    original_settings = mcp.settings.model_copy(deep=True)
    try:
        monkeypatch.setenv("MCP_HOST", "0.0.0.0")
        monkeypatch.setenv("MCP_PORT", "8000")
        monkeypatch.delenv("MCP_ALLOWED_HOSTS", raising=False)
        monkeypatch.delenv("MCP_ALLOWED_ORIGINS", raising=False)

        _configure_runtime_settings()

        security = mcp.settings.transport_security
        assert security.allowed_hosts == ["*"]
        assert security.allowed_origins == ["*"]
    finally:
        mcp.settings = original_settings


def test_configure_runtime_settings_env_overrides_allow_lists(monkeypatch) -> None:
    original_settings = mcp.settings.model_copy(deep=True)
    try:
        monkeypatch.setenv("MCP_HOST", "0.0.0.0")
        monkeypatch.setenv("MCP_PORT", "9000")
        monkeypatch.setenv("MCP_ALLOWED_HOSTS", "api.example.com:443,api.example.com:*")
        monkeypatch.setenv(
            "MCP_ALLOWED_ORIGINS",
            "https://api.example.com,https://console.example.com",
        )

        _configure_runtime_settings()

        security = mcp.settings.transport_security
        assert mcp.settings.port == 9000
        assert security.allowed_hosts == ["api.example.com:443", "api.example.com:*"]
        assert security.allowed_origins == [
            "https://api.example.com",
            "https://console.example.com",
        ]
    finally:
        mcp.settings = original_settings