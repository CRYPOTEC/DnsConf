"""Optional push source over a websocket.

A background thread holds the connection and pushes parsed NewsItem objects
into a thread-safe queue; the engine drains the queue each cycle via fetch(),
so a streaming feed fits the existing poll loop.

Requires the optional `websockets` package. Expected message shape (JSON):
  {"title": "...", "summary": "...", "link": "...", "source": "...",
   "published": <epoch seconds, optional>}
Non-JSON text messages are accepted too (used as the title).
"""

from __future__ import annotations

import json
import queue
import threading
import time

from ..models import NewsItem


def _to_item(raw: str) -> NewsItem | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        d = json.loads(raw)
    except ValueError:
        return NewsItem(source="ws", title=raw[:200], link="")
    title = (d.get("title") or "").strip()
    if not title:
        return None
    return NewsItem(
        source=d.get("source") or "ws",
        title=title,
        link=d.get("link") or "",
        summary=(d.get("summary") or "").strip(),
        published=float(d.get("published", time.time())),
    )


class WebSocketSource:
    def __init__(self, url: str, max_buffer: int = 1000):
        try:
            import websockets  # noqa: F401
        except ImportError as exc:  # pragma: no cover - depends on optional dep
            raise ImportError(
                "websocket_url is set but the `websockets` package is not "
                "installed. Run: pip install websockets"
            ) from exc
        self.url = url
        self.name = "websocket"
        self._q: "queue.Queue[NewsItem]" = queue.Queue(maxsize=max_buffer)
        self._started = False

    def _run(self) -> None:  # pragma: no cover - requires a live socket
        import asyncio

        import websockets

        async def loop() -> None:
            while True:
                try:
                    async with websockets.connect(self.url) as ws:
                        async for message in ws:
                            item = _to_item(message if isinstance(message, str)
                                             else message.decode("utf-8", "replace"))
                            if item is not None:
                                try:
                                    self._q.put_nowait(item)
                                except queue.Full:
                                    pass  # drop oldest-style: just skip when full
                except Exception:  # noqa: BLE001 - reconnect on any failure
                    await asyncio.sleep(3)

        asyncio.new_event_loop().run_until_complete(loop())

    def _ensure_started(self) -> None:
        if not self._started:
            threading.Thread(target=self._run, daemon=True).start()
            self._started = True

    def fetch(self) -> list[NewsItem]:
        self._ensure_started()
        items = []
        while True:
            try:
                items.append(self._q.get_nowait())
            except queue.Empty:
                break
        return items
