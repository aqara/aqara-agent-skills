#!/usr/bin/env python3
"""
Aqara Smart Home Open Platform REST API wrapper.

Base URL: ``https://<AQARA_OPEN_HOST>/open/api`` by default, or override with
``AQARA_OPEN_API_URL`` (full URL, no trailing slash required).

HTTP timeout (seconds): ``AQARA_OPEN_HTTP_TIMEOUT`` (default 60) for ``_get`` / ``_post``.
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
    configure_stdio_utf8,
    load_api_key,
    merge_user_context_home_info,
)

_DEFAULT_OPEN_TIMEOUT = float(os.environ.get("AQARA_OPEN_HTTP_TIMEOUT") or "60")


def _default_open_host() -> str:
    # return (os.environ.get("AQARA_OPEN_HOST") or "agent.aqara.com").strip()
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
        self.session.headers.update({"application_id": "AqaqaAgentSkills"})
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
        resp = self.session.get(url, params=params, timeout=_DEFAULT_OPEN_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.post(url, json=data, timeout=_DEFAULT_OPEN_TIMEOUT)
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
        """GET home/positions/query (rooms / positions in current home)."""
        self._require_position_id()
        return self._get("home/positions/query")

    def post_current_outdoor_weather(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        GET current outdoor weather for the home context
        """
        self._require_position_id()
        path =  "current/weather/query"
        return self._post(path, data=data or {})

    # ─── Device info ───
    def get_home_devices(self) -> Any:
        """List device details for the current home."""
        self._require_position_id()
        return self._get("home/devices/query")

    def post_device_base_info(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST device/base/info (JSON body per Open API)."""
        self._require_position_id()
        return self._post("device/base/info", data=data or {})

    # ─── Device status ───
    def post_device_status(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST device/status/query. `data`: request JSON body (e.g. device_ids)."""
        self._require_position_id()
        return self._post("device/status/query", data=data or {})

    # ─── Device control ───
    def post_device_control(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST device/control."""
        self._require_position_id()
        return self._post("device/control", data=data or {})


    # ─── Device _log ───
    def post_device_log(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST device/status/log/query."""
        self._require_position_id()
        return self._post("device/status/log/query", data=data or {})
    

    # ─── Scene management ───
    def get_home_scenes(self) -> Any:
        """GET home/scenes/query."""
        self._require_position_id()
        return self._get("home/scenes/query")

    def post_execute_scene(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST scene/run."""
        self._require_position_id()
        return self._post("scene/run", data=data or {})

    def post_scene_detail_query(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST scene/detail/query (device_ids in body)."""
        self._require_position_id()
        return self._post("scene/detail/query", data=data or {})

    def post_create_scene(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST scene/create.

        JSON body (skill contract; tenant may alias keys — align with live API if needed):

        - ``scene_name`` (str): required, non-empty.
        - ``position_id`` (str): required, non-empty — room position id from ``get_rooms``.
        - ``scene_data`` (list): required, non-empty. Each element: ``device_ids`` (non-empty
          list of str), ``slots`` (list of objects with ``attribute``, ``action``, ``value``).
          Default ``action`` is ``set`` when omitted. Lighting effects: ``attribute``
          ``lighting_effect``, ``action`` ``set``, ``value`` = effect name. For ``color``,
          ``value`` should be English lowercase.

        See ``references/scene-workflow/create.md``.
        """
        self._require_position_id()
        body: Dict[str, Any] = dict(data or {})
        sn = body.get("scene_name")
        if not isinstance(sn, str) or not sn.strip():
            raise ValueError(
                "post_create_scene requires non-empty scene_name (see references/scene-workflow/create.md)."
            )
        body["scene_name"] = sn.strip()
        pid = body.get("position_id")
        if not isinstance(pid, str) or not pid.strip():
            raise ValueError(
                "post_create_scene requires non-empty position_id (room id from get_rooms)."
            )
        body["position_id"] = pid.strip()
        sd = body.get("scene_data")
        if not isinstance(sd, list) or len(sd) == 0:
            raise ValueError(
                "post_create_scene requires non-empty scene_data (see references/scene-workflow/create.md)."
            )
        for i, block in enumerate(sd):
            if not isinstance(block, dict):
                raise ValueError(f"scene_data[{i}] must be a JSON object.")
            dids = block.get("device_ids")
            if not isinstance(dids, list) or len(dids) == 0:
                raise ValueError(
                    f"scene_data[{i}].device_ids must be a non-empty list of strings."
                )
            norm_ids: List[str] = []
            for k, d in enumerate(dids):
                if not isinstance(d, str) or not d.strip():
                    raise ValueError(
                        f"scene_data[{i}].device_ids[{k}] must be a non-empty string."
                    )
                norm_ids.append(d.strip())
            block["device_ids"] = norm_ids
            slots = block.get("slots")
            if not isinstance(slots, list):
                raise ValueError(f"scene_data[{i}].slots must be a list.")
            for j, slot in enumerate(slots):
                if not isinstance(slot, dict):
                    raise ValueError(f"scene_data[{i}].slots[{j}] must be a JSON object.")
                attr = slot.get("attribute")
                if attr == "lighting_effect":
                    slot["action"] = "set"
                elif not slot.get("action"):
                    slot["action"] = "set"
                if attr == "color" and isinstance(slot.get("value"), str):
                    slot["value"] = str(slot["value"]).strip().lower()
        return self._post("scene/create", data=body)

    def post_scene_snapshot(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST scene/snapshot.
        JSON body (after normalization):

        - ``snap_name`` (str): Snapshot display name. If missing or whitespace-only,
          defaults to ``场景快照`` when ``AQARA_DEFAULT_LOCALE`` is unset or starts
          with ``zh``, otherwise ``scene snapshot``.
        - ``position_ids`` (list[str]): Room position IDs (**required**, non-empty).
        """
        self._require_position_id()
        body: Dict[str, Any] = dict(data or {})
        snap = body.get("snap_name")
        if not (isinstance(snap, str) and snap.strip()):
            loc = (os.environ.get("AQARA_DEFAULT_LOCALE") or "").strip().lower()
            if not loc or loc.startswith("zh"):
                body["snap_name"] = "场景快照"
            else:
                body["snap_name"] = "scene snapshot"
        else:
            body["snap_name"] = str(snap).strip()
        pids = body.get("position_ids")
        if not isinstance(pids, list) or len(pids) == 0:
            raise ValueError(
                "post_scene_snapshot requires non-empty position_ids (list of room position id strings). "
                "Resolve rooms via get_rooms first (see references/scene-workflow/snapshot.md)."
            )
        normalized: List[str] = []
        for x in pids:
            if not isinstance(x, str) or not x.strip():
                raise ValueError("position_ids must be a list of non-empty strings.")
            normalized.append(x.strip())
        body["position_ids"] = normalized
        return self._post("scene/snapshot", data=body)
    
    def post_scene_execution_log(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST scene/execution/log/query."""
        self._require_position_id()
        return self._post("scene/execution/log/query", data=data or {})

    # ─── Automation management ───
    def get_home_automations(self) -> Any:
        """List automations for the current home."""
        self._require_position_id()
        return self._get("home/automations/query")

    def post_automation_detail_query(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST automation/detail/query."""
        self._require_position_id()
        return self._post("automation/detail/query", data=data or {})

    def post_automation_execution_log(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST automation/execution/log/query."""
        self._require_position_id()
        return self._post("automation/execution/log/query", data=data or {})

    def post_automation_switch(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST automation/switch."""
        self._require_position_id()
        return self._post("automation/switch", data=data or {})

    # ─── Energy ───
    def post_energy_consumption_statistic(self, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        POST device or position energy consumption query.

        Route is chosen only from ``device_ids``:

        - Non-empty ``device_ids`` list → ``device/energy/consumption/query``.
        - Otherwise (including empty or missing ``device_ids``) → ``position/energy/consumption/query``.
        """
        self._require_position_id()
        body: Dict[str, Any] = data if isinstance(data, dict) else {}
        dids = body.get("device_ids")
        if isinstance(dids, list) and len(dids) > 0:
            path = "device/energy/consumption/query"
        else:
            path = "position/energy/consumption/query"
        return self._post(path, data=body)


# CLI: first argv must match a public method name on :class:`AqaraOpenAPI` (see references/*.md).
# Dispatch: ``get_*`` → ``meth()``; ``post_*`` → ``meth(payload)``.
def _print_json(data: Any) -> None:
    configure_stdio_utf8()
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _cli_invoke(api: AqaraOpenAPI, method_name: str, payload: Dict[str, Any]) -> Any:
    """Call ``api.<method_name>()`` or ``(..., payload)`` based on the ``get_`` / ``post_`` prefix."""
    if method_name.startswith("_"):
        print(f"Unknown tool: {method_name}", file=sys.stderr)
        sys.exit(1)
    meth = getattr(api, method_name, None)
    if not callable(meth):
        print(f"Unknown tool: {method_name}", file=sys.stderr)
        sys.exit(1)
    if method_name.startswith("get_"):
        return meth()
    if method_name.startswith("post_"):
        return meth(payload)
    print(
        f"Tool name must start with get_ or post_: {method_name}",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    configure_stdio_utf8()
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
        raw_payload: Any = json.loads(args[0]) if args else {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    payload: Dict[str, Any] = raw_payload if isinstance(raw_payload, dict) else {}
    if args and not isinstance(raw_payload, dict):
        print(
            "Warning: JSON body must be a JSON object; using empty object instead.",
            file=sys.stderr,
        )

    try:
        out = _cli_invoke(api, tool_name, payload)
    except json.JSONDecodeError as e:
        print(f"Response was not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)
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
