"""HTTP and WebSocket client for the SwarmSRE Control Plane API."""

import os

import httpx

DEFAULT_SERVER = "http://localhost:8000"


def _get_base_url() -> str:
    """Resolve the control plane server URL from env or default."""
    return os.environ.get("SWARMSRE_SERVER", DEFAULT_SERVER)


class SwarmSREClient:
    """Synchronous client for the SwarmSRE Control Plane REST API."""

    def __init__(self, server: str | None = None):
        self.base_url = server or _get_base_url()
        self._client = httpx.Client(base_url=self.base_url, timeout=15.0)

    # ── Health ──────────────────────────────────────────────────────────
    def health(self) -> dict:
        resp = self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    # ── Incidents ───────────────────────────────────────────────────────
    def list_incidents(self) -> list[dict]:
        resp = self._client.get("/api/incidents")
        resp.raise_for_status()
        return resp.json()

    def get_incident(self, incident_id: str) -> dict:
        resp = self._client.get(f"/api/incidents/{incident_id}")
        resp.raise_for_status()
        return resp.json()

    def approve_incident(self, incident_id: str) -> dict:
        resp = self._client.post(f"/api/incidents/{incident_id}/approve")
        resp.raise_for_status()
        return resp.json()

    def reject_incident(self, incident_id: str) -> dict:
        resp = self._client.post(f"/api/incidents/{incident_id}/reject")
        resp.raise_for_status()
        return resp.json()

    # ── Audit ──────────────────────────────────────────────────────────
    def list_audit(self) -> list[dict]:
        resp = self._client.get("/api/audit/")
        resp.raise_for_status()
        return resp.json()

    def get_audit(self, incident_id: str) -> list[dict]:
        resp = self._client.get(f"/api/audit/{incident_id}")
        resp.raise_for_status()
        return resp.json()

    # ── Metrics ────────────────────────────────────────────────────────
    def get_dora_metrics(self) -> dict:
        resp = self._client.get("/api/metrics/dora")
        resp.raise_for_status()
        return resp.json()

    # ── Cleanup ────────────────────────────────────────────────────────
    def close(self):
        self._client.close()

    def ws_url(self) -> str:
        """Return the WebSocket URL for the live event stream."""
        base = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        return f"{base}/ws"
