#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for local aqara skill scripts."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_ROOT / "assets"
USER_ACCOUNT_PATH = ASSETS_DIR / "user_account.json"
_LEGACY_USER_CONTEXT_PATH = ASSETS_DIR / "user_context.json"
CONFIG_PATH = ASSETS_DIR / "api_path_config.json"


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

_DEFAULT_LOGIN_PATH = "/login"
_DEFAULT_API_PATH = "/open/api"
_DEFAULT_MCP_PATH = "/open/mcp"


def load_config() -> Dict[str, str]:
    """Load settings from assets/api_path_config.json; derive login_url, api_base_url, mcp_url from aqara_base_url + *_path."""
    out: Dict[str, str] = {
        "aqara_base_url": "",
        "login_path": "",
        "api_path": "",
        "mcp_path": "",
        "homes_query_path": "",
        "homes_query_url": "",
        "login_url": "",
        "api_base_url": "",
        "mcp_url": "",
    }
    if not CONFIG_PATH.exists():
        return out
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return out
        base = (data.get("aqara_base_url") or "").strip().rstrip("/")
        login_p = (data.get("login_path") or "").strip() or _DEFAULT_LOGIN_PATH
        api_p = (data.get("api_path") or "").strip() or _DEFAULT_API_PATH
        mcp_p = (data.get("mcp_path") or "").strip() or _DEFAULT_MCP_PATH
        if not login_p.startswith("/"):
            login_p = "/" + login_p
        if not api_p.startswith("/"):
            api_p = "/" + api_p
        if not mcp_p.startswith("/"):
            mcp_p = "/" + mcp_p
        if base:
            if not base.startswith("http"):
                base = "https://" + base
            out["aqara_base_url"] = base
            out["login_path"] = login_p
            out["api_path"] = api_p
            out["mcp_path"] = mcp_p
            out["login_url"] = out["login_url"] or (base.rstrip("/") + login_p)
            out["api_base_url"] = out["api_base_url"] or (base.rstrip("/") + api_p)
            out["mcp_url"] = out["mcp_url"] or (base.rstrip("/") + mcp_p)
        hq = (data.get("homes_query_path") or "").strip().lstrip("/")
        if hq:
            out["homes_query_path"] = hq
        hqu = data.get("homes_query_url")
        if isinstance(hqu, str) and hqu.strip():
            out["homes_query_url"] = hqu.strip()
        for k in ("login_url", "api_base_url", "mcp_url"):
            v = data.get(k)
            if isinstance(v, str) and v.strip():
                out[k] = v.strip()
    except (json.JSONDecodeError, OSError):
        pass
    return out


def build_open_api_headers(
    access_token: str,
    *,
    with_position_id: bool = False,
    position_id: Optional[str] = None,
) -> Dict[str, str]:
    """
    Open API business calls use only the token header; the server derives region and other metadata from the token.
    After a home is selected, calls may add position_id; do not send position_id before listing homes
    (e.g. get_user_info_by_token, homes/query, user/positions/query).
    """
    h: Dict[str, str] = {"token": (access_token or "").strip()}
    if with_position_id:
        pid = (position_id or "").strip()
        if pid:
            h["position_id"] = pid
    return h


def build_mcp_headers(access_token: str, position_id: str) -> Dict[str, str]:
    """MCP calls must include token and position_id (home positionId, same as home_id in user_account.json); region comes from the token on the server."""
    pid = (position_id or "").strip()
    if not pid:
        raise ValueError(
            "MCP requests require position_id: select a home and set home_id in user_account.json (step 2), "
            "or pass position_id in script headers."
        )
    return {
        "token": (access_token or "").strip(),
        "position_id": pid,
    }


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

# skill_locale values allowed in user_account.json (optional; main SKILL flow does not depend on this)
ALLOWED_SKILL_LOCALES: tuple[str, ...] = (
    "en",
    "en-US",
    "zh",
    "zh-CN",
    "ko",
    "ja",
    "fr",
    "de",
    "tr",
    "pl",
    "es",
    "ru",
    "it",
    "nl",
    "hu",
    "pt",
    "sk",
    "sv",
    "zh-TW",
    "zh-HK",
    "cs",
    "ar",
    "nn",
    "th",
    "el",
    "vi",
    "ms",
    "he",
    "id",
    "ro",
)

# Compact keys (lowercase, no separators) → canonical tags; used for aliases and langdetect mapping
_SKILL_LOCALE_COMPACT: Dict[str, str] = {
    "en": "en",
    "enus": "en-US",
    "en-us": "en-US",
    "zh": "zh",
    "zhcn": "zh-CN",
    "zh-cn": "zh-CN",
    "zhtw": "zh-TW",
    "zh-tw": "zh-TW",
    "zhhk": "zh-HK",
    "zh-hk": "zh-HK",
    "ko": "ko",
    "ja": "ja",
    "fr": "fr",
    "de": "de",
    "tr": "tr",
    "pl": "pl",
    "es": "es",
    "ru": "ru",
    "it": "it",
    "nl": "nl",
    "hu": "hu",
    "pt": "pt",
    "sk": "sk",
    "sv": "sv",
    "cs": "cs",
    "ar": "ar",
    "nn": "nn",
    "nb": "nn",
    "no": "nn",
    "th": "th",
    "el": "el",
    "vi": "vi",
    "ms": "ms",
    "he": "he",
    "iw": "he",
    "id": "id",
    "in": "id",
    "ro": "ro",
}

# Lowercase codes from langdetect → canonical tags (must be in the allowed list)
_LANGDETECT_TO_SKILL_LOCALE: Dict[str, str] = {
    "en": "en",
    "zh-cn": "zh-CN",
    "zh-tw": "zh-TW",
    "ko": "ko",
    "ja": "ja",
    "fr": "fr",
    "de": "de",
    "tr": "tr",
    "pl": "pl",
    "es": "es",
    "ru": "ru",
    "it": "it",
    "nl": "nl",
    "hu": "hu",
    "pt": "pt",
    "sk": "sk",
    "sv": "sv",
    "cs": "cs",
    "ar": "ar",
    "no": "nn",
    "nb": "nn",
    "nn": "nn",
    "th": "th",
    "el": "el",
    "vi": "vi",
    "ms": "ms",
    "he": "he",
    "iw": "he",
    "id": "id",
    "ro": "ro",
}


def read_user_context_dict() -> Dict[str, Any]:
    _migrate_legacy_user_context_file()
    if not USER_ACCOUNT_PATH.exists():
        return {}
    try:
        data = json.loads(USER_ACCOUNT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def normalize_skill_locale(tag: Optional[str]) -> Optional[str]:
    """
    Normalize a user-, agent-, or detector-provided tag to a string in ALLOWED_SKILL_LOCALES.
    Returns None if unrecognized.
    """
    if tag is None:
        return None
    t = str(tag).strip()
    if not t:
        return None
    t = t.replace("_", "-")
    for allowed in ALLOWED_SKILL_LOCALES:
        if t.lower() == allowed.lower():
            return allowed
    compact = re.sub(r"[\s-]", "", t.lower())
    return _SKILL_LOCALE_COMPACT.get(compact)


def load_skill_locale() -> Optional[str]:
    """Read skill_locale from user_account.json and normalize it."""
    raw = read_user_context_dict().get("skill_locale")
    if not isinstance(raw, str) or not raw.strip():
        return None
    return normalize_skill_locale(raw.strip())


def set_skill_locale(locale_tag: str) -> str:
    """Merge-write skill_locale and skill_locale_updated_at."""
    canon = normalize_skill_locale(locale_tag)
    if not canon:
        raise ValueError(f"unsupported skill_locale: {locale_tag!r}")
    data = read_user_context_dict()
    data["skill_locale"] = canon
    data["skill_locale_updated_at"] = datetime.now(timezone.utc).isoformat()
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    USER_ACCOUNT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return canon


def skill_locale_from_env() -> Optional[str]:
    """Infer skill_locale from LANG / LANGUAGE / LC_ALL (None if unmappable)."""
    for key in ("LANG", "LANGUAGE", "LC_ALL"):
        raw = (os.environ.get(key) or "").strip()
        if not raw:
            continue
        part = raw.split(".")[0].strip().replace("_", "-")
        c = normalize_skill_locale(part)
        if c:
            return c
        compact = re.sub(r"[\s-]", "", part.lower())
        c = _SKILL_LOCALE_COMPACT.get(compact)
        if c:
            return c
    return None


def infer_skill_locale_from_text(text: str) -> Optional[str]:
    """
    Infer skill_locale from natural language using langdetect (requires the langdetect package).
    Returns None on failure.
    """
    text = (text or "").strip()
    if len(text) < 8:
        return None
    try:
        from langdetect import detect  # type: ignore
    except ImportError:
        return None
    try:
        code = detect(text).lower()
    except Exception:
        return None
    mapped = _LANGDETECT_TO_SKILL_LOCALE.get(code)
    if mapped:
        return mapped
    if "-" in code:
        mapped = _LANGDETECT_TO_SKILL_LOCALE.get(code.split("-", 1)[0])
        if mapped:
            return mapped
    return normalize_skill_locale(code)
USER_POSITIONS_CACHE_JSON_PATH = ASSETS_DIR / "user_positions_cache.json"
DEVICES_CACHE_PATH = ASSETS_DIR / "devices_cache.md"


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def mcp_result_is_business_error(payload: Any) -> bool:
    """Return True if the parsed MCP call_tool result (dict or odd-shaped value) indicates a business error."""
    if isinstance(payload, str):
        return "Business error occurred." in payload or "InvalidParameterErrorForHeader" in payload
    if not isinstance(payload, dict):
        return "Business error occurred." in str(payload) or "InvalidParameterErrorForHeader" in str(payload)
    outputs = payload.get("outputs")
    if not isinstance(outputs, dict):
        return False
    code = str(outputs.get("code", ""))
    return code.startswith("ERROR.")


def mcp_result_to_storable_text(payload: Any) -> str:
    """Turn an MCP response body into text suitable for devices_cache.md (markdown or JSON string)."""
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, dict):
        for key in ("text", "markdown", "content"):
            if isinstance(payload.get(key), str):
                return str(payload[key]).strip()
        return json.dumps(payload, ensure_ascii=False, indent=2)
    if isinstance(payload, list):
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return str(payload).strip()


def load_api_key() -> tuple[Optional[str], Optional[str]]:
    """Read aqara_api_key (legacy: aqara_access_token) and home_id from user_account.json. Returns (credential, home_id)."""
    _migrate_legacy_user_context_file()
    if not USER_ACCOUNT_PATH.exists():
        return None, None
    try:
        data = json.loads(USER_ACCOUNT_PATH.read_text(encoding="utf-8"))
        t = data.get("aqara_api_key")
        if not (isinstance(t, str) and t.strip()):
            legacy = data.get("aqara_access_token")
            t = legacy if isinstance(legacy, str) else None
        h = data.get("home_id") or data.get("position_id")
        token = t.strip() if isinstance(t, str) and t.strip() else None
        home_id = str(h).strip() if h and str(h).strip() else None
        return token, home_id
    except Exception:
        pass
    return None, None


def set_aqara_api_key(api_key: str) -> None:
    """
    Merge-write aqara_api_key and updated_at; keep other keys in user_account.json.
    Remove legacy keys aqara_access_token and region; after success, delete legacy pairing images under assets if any.
    """
    _migrate_legacy_user_context_file()
    api_key = (api_key or "").strip()
    if not api_key:
        raise ValueError("aqara_api_key must be non-empty")
    data: Dict[str, Any] = {}
    if USER_ACCOUNT_PATH.exists():
        try:
            data = json.loads(USER_ACCOUNT_PATH.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
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
    data: Dict[str, Any] = {}
    if USER_ACCOUNT_PATH.exists():
        try:
            data = json.loads(USER_ACCOUNT_PATH.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
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


def _try_parse_json_text(text: str) -> Any:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _parse_markdown_table(text: str) -> List[Dict[str, str]]:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    table_lines = [ln for ln in lines if ln.startswith("|") and ln.endswith("|")]
    if len(table_lines) < 2:
        return []

    header = [c.strip() for c in table_lines[0].strip("|").split("|")]
    rows: List[Dict[str, str]] = []
    for ln in table_lines[1:]:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if not cells:
            continue
        if all(c.startswith("-") for c in cells):
            continue
        if len(cells) < len(header):
            cells.extend([""] * (len(header) - len(cells)))
        row = {header[idx]: cells[idx] for idx in range(len(header))}
        rows.append(row)
    return rows


def _extract_rows_from_payload(payload: Any) -> List[Dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "list", "devices", "positions"):
            v = payload.get(key)
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
        return [payload]
    if isinstance(payload, str):
        j = _try_parse_json_text(payload)
        if j is not None:
            return _extract_rows_from_payload(j)
        return _parse_markdown_table(payload)
    return []


def _read_cache_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    direct_json = _try_parse_json_text(text)
    if direct_json is not None:
        rows = _extract_rows_from_payload(direct_json)
        if rows:
            return rows
    rows = _parse_markdown_table(text)
    if rows:
        return rows
    # Some cached outputs may be wrapped in "Root(... outputs={...})"
    # Fallback: try to extract JSON-looking body.
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if m:
        try_json = _try_parse_json_text(m.group(0))
        if try_json is not None:
            return _extract_rows_from_payload(try_json)
    return []


def write_user_positions_cache_json(
    *,
    source: str,
    rows: List[Dict[str, str]],
    homes: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Write assets/user_positions_cache.json: source, timestamp, flattened rows (one row per room), optional home tree (with rooms).
    Intended as the preferred input for load_positions().
    """
    payload: Dict[str, Any] = {
        "source": source,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    if homes is not None:
        payload["homes"] = homes
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    USER_POSITIONS_CACHE_JSON_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _normalize_position_rows_for_load(rows: List[Any]) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = (
            row.get("position_name")
            or row.get("name")
            or row.get("room")
            or row.get("room_name")
            or ""
        )
        position_id = row.get("position_id") or row.get("id") or ""
        if not str(name).strip():
            continue
        normalized.append(
            {
                "position_id": str(position_id).strip(),
                "position_name": str(name).strip(),
            }
        )
    return normalized


def load_positions() -> List[Dict[str, str]]:
    if not USER_POSITIONS_CACHE_JSON_PATH.exists():
        return []
    try:
        data = json.loads(USER_POSITIONS_CACHE_JSON_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            jr = data.get("rows")
            if isinstance(jr, list) and jr:
                return _normalize_position_rows_for_load(jr)
    except Exception:
        pass
    return []


def load_devices() -> List[Dict[str, str]]:
    rows = _read_cache_rows(DEVICES_CACHE_PATH)
    normalized: List[Dict[str, str]] = []
    for row in rows:
        name = (
            row.get("device_name")
            or row.get("name")
            or row.get("endpoint_name")
            or row.get("label")
            or ""
        )
        endpoint_id = row.get("endpoint_id") or row.get("device_id") or row.get("id") or ""
        position_name = row.get("position_name") or row.get("room_name") or row.get("room") or ""
        device_type = row.get("device_type") or row.get("type") or ""
        online_raw = str(row.get("online_status") or row.get("online") or row.get("is_online") or "").strip().lower()
        if online_raw in {"1", "true", "online", "on"}:
            online_status = "online"
        elif online_raw in {"0", "false", "offline", "off"}:
            online_status = "offline"
        else:
            online_status = str(row.get("online_status") or row.get("online") or "unknown").strip() or "unknown"

        if not name:
            continue
        normalized.append(
            {
                "endpoint_id": str(endpoint_id).strip(),
                "device_name": str(name).strip(),
                "position_name": str(position_name).strip(),
                "device_type": str(device_type).strip(),
                "online_status": online_status,
            }
        )
    return normalized
