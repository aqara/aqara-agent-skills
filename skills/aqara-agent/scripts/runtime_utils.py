#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for local aqara skill scripts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_ROOT / "assets"
USER_ACCOUNT_PATH = ASSETS_DIR / "user_account.json"
_LEGACY_USER_CONTEXT_PATH = ASSETS_DIR / "user_context.json"


class MissingAqaraApiKeyError(RuntimeError):
    """No usable ``aqara_api_key`` on disk. Run the login flow in ``references/aqara-account-manage.md`` and save the key."""


class NoHomesAvailableError(RuntimeError):
    """``homes/query`` returned no homes; cannot set ``position_id``. See ``references/home-space-manage.md``."""


class MultipleHomesMustSelectError(RuntimeError):
    """
    More than one home exists; the user must choose before home-scoped APIs run.
    ``homes`` is a list of ``{"home_id", "home_name"}`` dicts.
    """

    def __init__(self, message: str, homes: List[Dict[str, str]]):
        super().__init__(message)
        self.homes = homes


def _fresh_user_account_template() -> Dict[str, Any]:
    """Canonical empty ``user_account.json`` used when the file is missing or cannot be parsed."""
    return {
        "aqara_api_key": "",
        "updated_at": "",
        "home_id": "",
        "home_name": "",
    }


def _load_user_account_dict_or_template() -> Dict[str, Any]:
    """
    Load existing ``user_account.json`` if it is valid JSON with a root object.
    If the file is missing, invalid JSON, or the root is not an object, return a
    fresh template (empty strings for the four core fields).
    """
    if not USER_ACCOUNT_PATH.exists():
        return _fresh_user_account_template()
    try:
        parsed = json.loads(USER_ACCOUNT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _fresh_user_account_template()
    if not isinstance(parsed, dict):
        return _fresh_user_account_template()
    return parsed


def _migrate_legacy_user_context_file() -> None:
    """If only the legacy file user_context.json exists, rename it to user_account.json (one-time migration)."""
    if USER_ACCOUNT_PATH.exists():
        return
    if not _LEGACY_USER_CONTEXT_PATH.exists():
        return
    try:
        _LEGACY_USER_CONTEXT_PATH.rename(USER_ACCOUNT_PATH)
    except OSError:
        pass


def _unlink_legacy_pairing_artifacts() -> None:
    """Remove legacy local pairing screenshots under assets (login_*_latest.png); this skill no longer creates them."""
    try:
        for p in ASSETS_DIR.glob("login_*_latest.png"):
            try:
                p.unlink()
            except OSError:
                pass
    except OSError:
        pass


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _read_stored_credentials() -> tuple[Optional[str], Optional[str]]:
    """Read ``aqara_api_key`` (and legacy ``aqara_access_token``) plus ``home_id`` without raising."""
    _migrate_legacy_user_context_file()
    if not USER_ACCOUNT_PATH.exists():
        return None, None
    try:
        data = json.loads(USER_ACCOUNT_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None, None
        t = data.get("aqara_api_key")
        if not (isinstance(t, str) and t.strip()):
            legacy = data.get("aqara_access_token")
            t = legacy if isinstance(legacy, str) else None
        h = data.get("home_id") or data.get("position_id")
        token = t.strip() if isinstance(t, str) and t.strip() else None
        home_id = str(h).strip() if h and str(h).strip() else None
        return token, home_id
    except Exception:
        return None, None


def load_api_key(*, require_saved_api_key: bool = True) -> tuple[Optional[str], Optional[str]]:
    """
    Read ``aqara_api_key`` and ``home_id`` from ``user_account.json``.

    By default (``require_saved_api_key=True``), raises :class:`MissingAqaraApiKeyError`
    if the saved key is missing or empty so callers can route to the account login flow.

    Pass ``require_saved_api_key=False`` when the caller may supply a key another way
    (e.g. ``AqaraOpenAPI(api_key=...)``) but still needs ``home_id`` from disk.
    """
    token, home_id = _read_stored_credentials()
    if require_saved_api_key:
        if not token or not str(token).strip():
            raise MissingAqaraApiKeyError(
                "Missing or empty aqara_api_key in assets/user_account.json. "
                "Follow references/aqara-account-manage.md to sign in and save the key."
            )
        return str(token).strip(), home_id
    return token, home_id


def set_aqara_api_key(api_key: str) -> None:
    """
    Merge-write aqara_api_key and updated_at; keep other keys in user_account.json.
    Remove legacy keys aqara_access_token and region; after success, delete legacy pairing images under assets if any.
    """
    _migrate_legacy_user_context_file()
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("aqara_api_key must be non-empty")
    data = _load_user_account_dict_or_template()
    data.pop("region", None)
    data.pop("aqara_access_token", None)
    data["aqara_api_key"] = api_key
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    USER_ACCOUNT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _unlink_legacy_pairing_artifacts()


def merge_user_context_home_info(
    homes: Optional[List[Dict[str, Any]]] = None,
    position_ids: Optional[Dict[str, str]] = None,
    home_id: Optional[str] = None,
    home_name: Optional[str] = None,
) -> None:
    """
    Merge home fields into user_account.json; preserve existing aqara_api_key and other keys.
    Drops obsolete region (region is derived from the token on the server; this skill no longer persists region).
    """
    _migrate_legacy_user_context_file()
    data = _load_user_account_dict_or_template()
    if homes is not None:
        data["homes"] = homes
    if position_ids is not None:
        data["position_ids"] = position_ids
    if home_id is not None:
        data["home_id"] = str(home_id).strip()
    if home_name is not None:
        data["home_name"] = str(home_name).strip()
    if home_id is not None or home_name is not None:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data.pop("region", None)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    USER_ACCOUNT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
