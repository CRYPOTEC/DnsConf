"""Thin client for the Composio v3 REST API.

We talk to Composio over plain HTTP (verified contract) so the code does not
depend on a particular SDK version:

    POST https://backend.composio.dev/api/v3/tools/execute/{TOOL_SLUG}
    header: x-api-key: <ak_...>
    body:   {"user_id": "...", "arguments": { ... }}
"""
from __future__ import annotations

import requests

BASE = "https://backend.composio.dev/api/v3"


class ComposioError(RuntimeError):
    pass


class ComposioClient:
    def __init__(self, api_key: str, user_id: str, timeout: int = 30):
        self.api_key = api_key
        self.user_id = user_id
        self.timeout = timeout

    def _headers(self) -> dict:
        return {"x-api-key": self.api_key, "content-type": "application/json"}

    def execute(self, tool_slug: str, arguments: dict) -> dict:
        """Run a single Composio tool for the configured user/entity."""
        resp = requests.post(
            f"{BASE}/tools/execute/{tool_slug}",
            headers=self._headers(),
            json={"user_id": self.user_id, "arguments": arguments},
            timeout=self.timeout,
        )
        try:
            data = resp.json()
        except ValueError:
            raise ComposioError(f"Composio вернул не-JSON ответ (HTTP {resp.status_code})")
        if resp.status_code >= 400 or data.get("error"):
            err = data.get("error") or {}
            msg = err.get("message") if isinstance(err, dict) else str(err)
            raise ComposioError(msg or f"HTTP {resp.status_code}")
        return data

    def append_sheet_row(self, spreadsheet_id: str, sheet_name: str, row: list[str]) -> dict:
        """Append one row of values to the end of a Google Sheet.

        GOOGLESHEETS_BATCH_UPDATE appends new rows when first_cell_location is omitted.
        """
        return self.execute(
            "GOOGLESHEETS_BATCH_UPDATE",
            {
                "spreadsheet_id": spreadsheet_id,
                "sheet_name": sheet_name,
                "values": [row],
            },
        )

    def is_toolkit_connected(self, toolkit_slug: str) -> bool:
        """Return True if there is an active connected account for the toolkit/user."""
        resp = requests.get(
            f"{BASE}/connected_accounts",
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code >= 400:
            return False
        items = resp.json().get("items", [])
        for acc in items:
            toolkit = (acc.get("toolkit") or {})
            slug = toolkit.get("slug") if isinstance(toolkit, dict) else toolkit
            if slug == toolkit_slug:
                return True
        return False
