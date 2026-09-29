"""PyPI update detection with a lazy, cached policy.

No repository data is transmitted; only the package name is queried.
Policy (implementation plan section 19): first two launches make no request,
the third launch checks, afterwards at most once per 24h. Set
LLIKI_NO_UPDATE_CHECK=1 to disable entirely.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

CACHE_FILENAME = ".lliki-update-check.json"
PYPI_URL = "https://pypi.org/pypi/lliki/json"
CHECK_INTERVAL_SECONDS = 24 * 3600
FREE_LAUNCHES = 2


def cache_path() -> Path:
    base = os.environ.get("LOCALAPPDATA") if sys.platform == "win32" else os.environ.get("XDG_CACHE_HOME")
    root = Path(base) if base else Path.home() / ".cache"
    return root / "lliki" / CACHE_FILENAME


def _load(cache: Path) -> dict:
    try:
        return json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"launches": 0, "last_check": 0, "latest": None, "checked_version": None}


def _save(cache: Path, data: dict) -> None:
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass


def fetch_latest(timeout: float = 2.0) -> Optional[str]:
    """Return the newest version string from PyPI, or None on any failure."""
    try:
        request = urllib.request.Request(PYPI_URL, headers={"User-Agent": "lliki-update-check"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))["info"]["version"]
    except Exception:
        return None


def _version_tuple(text: str) -> tuple:
    parts = []
    for chunk in text.split(".")[:3]:
        digits = "".join(character for character in chunk if character.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def newer(latest: str, current: str) -> bool:
    return _version_tuple(latest) > _version_tuple(current)


def update_notice(current_version: str) -> Optional[str]:
    """Called at CLI launch. Returns a one-line notice or None; never raises."""
    if os.environ.get("LLIKI_NO_UPDATE_CHECK", "").strip().lower() in {"1", "true", "yes"}:
        return None
    cache = cache_path()
    data = _load(cache)
    data["launches"] = int(data.get("launches", 0)) + 1
    due = data["launches"] > FREE_LAUNCHES and (time.time() - float(data.get("last_check", 0))) > CHECK_INTERVAL_SECONDS
    if not due:
        # Serve a cached notice without any request.
        latest = data.get("latest")
        if latest and data.get("checked_version") == current_version and newer(latest, current_version):
            _save(cache, data)
            return f"lliki {current_version} is installed; {latest} is available. Run: pip install -U lliki"
        _save(cache, data)
        return None
    latest = fetch_latest()
    data["last_check"] = time.time()
    if latest:
        data["latest"] = latest
        data["checked_version"] = current_version
    _save(cache, data)
    if latest and newer(latest, current_version):
        return f"lliki {current_version} is installed; {latest} is available. Run: pip install -U lliki"
    return None


def force_check(current_version: str) -> dict:
    latest = fetch_latest()
    if latest is None:
        return {"ok": False, "current": current_version, "latest": None, "detail": "PyPI query failed or offline"}
    cache = cache_path()
    data = _load(cache)
    data.update({"latest": latest, "last_check": time.time(), "checked_version": current_version, "launches": 0})
    _save(cache, data)
    return {"ok": True, "current": current_version, "latest": latest, "update_available": newer(latest, current_version)}
