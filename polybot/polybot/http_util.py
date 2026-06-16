"""Tiny stdlib HTTP GET helper (no `requests` dependency)."""

from __future__ import annotations

import urllib.request
import urllib.error


_UA = "polybot/0.1 (+https://github.com/crypotec/dnsconf)"


def get(url: str, timeout: float = 15.0) -> bytes:
    """HTTP GET returning raw bytes. Raises on non-2xx / network error."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def get_text(url: str, timeout: float = 15.0) -> str:
    return get(url, timeout).decode("utf-8", errors="replace")
