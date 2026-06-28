from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Generator

import pytest


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture
def streamable_http_url() -> Generator[str, None, None]:
    port = _find_free_port()
    env = os.environ.copy()
    env["MCP_HOST"] = "127.0.0.1"
    env["MCP_PORT"] = str(port)

    proc = subprocess.Popen(
        [sys.executable, "-m", "app.server"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        deadline = time.time() + 10
        ready = False
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                    ready = True
                    break
            except Exception:
                pass
            time.sleep(0.2)

        if not ready:
            stderr_output = ""
            if proc.poll() is not None and proc.stderr is not None:
                stderr_output = proc.stderr.read()
            raise RuntimeError(f"MCP server did not become ready in time. stderr={stderr_output}")

        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
