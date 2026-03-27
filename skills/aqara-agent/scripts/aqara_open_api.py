#!/usr/bin/env python3
"""
Aqara Smart Home Open Platform REST API wrapper.

Base URL: ``https://<AQARA_OPEN_HOST>/open/api`` by default, or override with
``AQARA_OPEN_API_URL`` (full URL, no trailing slash required).
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests
from runtime_utils import (
    MissingAqaraApiKeyError,
    MultipleHomesMustSelectError,
    NoHomesAvailableError,
    load_api_key,
    merge_user_context_home_info,
)


def _default_open_host() -> str:
    return (os.environ.get("AQARA_OPEN_HOST") or "agent.aqara.com").strip()


def _default_api_base_url() -> str:
    return f"https://{_default_open_host()}/open/api"


def _resolve_api_base_url(explicit: Optional[str] = None) -> str:
    """Resolve Open Platform REST base URL (no trailing slash)."""
    if explicit is not None and str(explicit).strip():
        return str(explicit).strip().rstrip("/")
    env_url = (os.environ.get("AQARA_OPEN_API_URL") or "").strip()
    if env_url:
        return env_url.rstrip("/")
    return _default_api_base_url()


def _session_position_id_valid(session: requests.Session) -> bool:
    pid = session.headers.get("position_id")
    return isinstance(pid, str) and bool(pid.strip())


def _extract_homes_from_response(payload: Any) -> List[Dict[str, str]]:
    """Normalize ``homes/query`` JSON into ``[{"home_id", "home_name"}, ...]``."""
    out: List[Dict[str, str]] = []
    if not isinstance(payload, dict):
        return out
    items: Any = None
    data = payload.get("data")
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ("homes", "list", "positions", "items"):
            v = data.get(key)
            if isinstance(v, list):
                items = v
                break
    if items is None:
        for key in ("homes", "list", "positions"):
            v = payload.get(key)
            if isinstance(v, list):
                items = v
                break
    if not isinstance(items, list):
        return out
    for it in items:
        if not isinstance(it, dict):
            continue
        hid = (
            it.get("positionId")
            or it.get("homeId")
            or it.get("id")
            or it.get("position_id")
            or it.get("home_id")
        )
        if hid is None or not str(hid).strip():
            continue
        name = (
            it.get("positionName")
            or it.get("homeName")
            or it.get("name")
            or it.get("home_name")
            or ""
        )
        out.append(
            {
                "home_id": str(hid).strip(),
                "home_name": str(name).strip() if name is not None else "",
            }
        )
    return out


def _resolve_home_context_if_needed(api: Any) -> None:
    """
    If ``position_id`` is missing, call ``homes/query`` (via ``get_homes``):
    zero homes → :class:`NoHomesAvailableError`; one → persist ``home_id`` / ``home_name`` and set header;
    several → :class:`MultipleHomesMustSelectError` with ``.homes``.
    """
    if _session_position_id_valid(api.session):
        return
    raw = api.get_homes()
    entries = _extract_homes_from_response(raw)
    if not entries:
        raise NoHomesAvailableError(
            "No homes returned from homes/query; cannot set position_id. "
            "See references/home-space-manage.md."
        )
    if len(entries) == 1:
        e = entries[0]
        merge_user_context_home_info(
            home_id=e["home_id"],
            home_name=e["home_name"],
        )
        api.session.headers["position_id"] = e["home_id"]
        return
    raise MultipleHomesMustSelectError(
        "Multiple homes found. You must select a home before other operations. "
        "Run: python3 scripts/save_user_account.py home '<home_id>' '<home_name>' "
        "(see references/home-space-manage.md).",
        entries,
    )


class AqaraOpenAPI:
    """Aqara Open API client."""

    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        loaded_key, home_id = load_api_key(require_saved_api_key=False)
        key = (api_key.strip() if isinstance(api_key, str) and api_key.strip() else None) or loaded_key
        if not key:
            raise MissingAqaraApiKeyError(
                "Missing aqara_api_key. Set it in assets/user_account.json or pass api_key to AqaraOpenAPI(). "
                "Follow references/aqara-account-manage.md to sign in and save the key."
            )

        self.api_key = key
        self.base_url = _resolve_api_base_url(api_base_url)
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {key}"})
        if home_id and str(home_id).strip():
            self.session.headers.update({"position_id": str(home_id).strip()})

    def _require_position_id(self) -> None:
        if not _session_position_id_valid(self.session):
            _resolve_home_context_if_needed(self)
        raw = self.session.headers.get("position_id")
        if not (isinstance(raw, str) and raw.strip()):
            raise ValueError(
                "Missing or empty position_id (home_id). Set home_id in assets/user_account.json "
                "before calling this API (not required for homes/query only)."
            )

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    # ─── Home management ───
    def get_homes(self, lang: str = "zh") -> Any:
        """List all homes for the current user.

        Omits ``position_id`` for this request only; many Open flows require no
        home header when calling ``homes/query`` (see skill home/account docs).
        """
        lang = lang or "zh"
        self.session.headers.update({"lang": lang})
        saved_position = self.session.headers.pop("position_id", None)
        try:
            return self._get("homes/query")
        finally:
            if saved_position is not None:
                self.session.headers["position_id"] = saved_position

    def get_rooms(self) -> Any:
        """List all rooms in the current home."""
        self._require_position_id()
        return self._get("position/detail/query")

    # ─── Device info ───
    def get_home_devices(self) -> Any:
        """List device details for the current home."""
        self._require_position_id()
        return self._get("home/devices/query")

    # ─── Device status ───
    def get_devices_status(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """Query device status. `data`: request JSON body (e.g. device_ids)."""
        self._require_position_id()
        return self._post("device/status/query", data=data or {})

    # ─── Device control ───
    def devices_control(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """Send a control command to device(s) in the current home."""
        self._require_position_id()
        return self._post("device/control", data=data or {})

    # ─── Scene management ───
    def get_home_scenes(self) -> Any:
        """List scene details for the current home."""
        self._require_position_id()
        return self._get("scene/query")

    def execute_scenes(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """Execute scene(s) in the current home."""
        self._require_position_id()
        return self._post("scene/run", data=data or {})


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: aqara_open_api.py <tool> [json_body]", file=sys.stderr)
        sys.exit(1)

    try:
        api = AqaraOpenAPI()
    except MissingAqaraApiKeyError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    tool_name = sys.argv[1]
    args = sys.argv[2:]

    try:
        payload: Dict[str, Any] = json.loads(args[0]) if args else {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    tools = {
        "homes": lambda: api.get_homes(),
        "rooms": lambda: api.get_rooms(),
        "home_devices": lambda: api.get_home_devices(),
        "home_scenes": lambda: api.get_home_scenes(),
        "device_status": lambda: api.get_devices_status(payload),
        "device_control": lambda: api.devices_control(payload),
        "execute_scenes": lambda: api.execute_scenes(payload),
    }

    runner = tools.get(tool_name)
    if runner is None:
        print(f"Unknown tool: {tool_name}", file=sys.stderr)
        sys.exit(1)

    try:
        out = runner()
    except NoHomesAvailableError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except MultipleHomesMustSelectError as e:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "home_selection_required",
                    "message": str(e),
                    "homes": e.homes,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        print(
            "Multiple homes: select one home, then run save_user_account.py home "
            "'<home_id>' '<home_name>' before other operations.",
            file=sys.stderr,
        )
        sys.exit(2)
    else:
        _print_json(out)


if __name__ == "__main__":
    main()
