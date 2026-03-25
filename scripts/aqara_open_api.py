#!/usr/bin/env python3
"""
Aqara Smart Home Open Platform API wrapper.
"""

import json
import sys
from typing import Optional

import requests
from runtime_utils import load_api_key, load_config

# Used when api_path_config.json is missing or api_base_url is unset.
DEFAULT_API_BASE_URL = "https://agent.aqara.com/open/api"


def _resolve_open_api_base_url(explicit: Optional[str]) -> str:
    if explicit is not None:
        u = str(explicit).strip()
        if u:
            return u.rstrip("/")
    cfg_url = (load_config().get("api_base_url") or "").strip()
    if cfg_url:
        return cfg_url.rstrip("/")
    return DEFAULT_API_BASE_URL


class AqaraOpenAPI:
    """Aqara Open API client."""

    def __init__(self, api_key: str = None, base_url: str = None):
        api_key, home_id = load_api_key()
        if not api_key:
            raise ValueError(
                "Missing API key. Set environment variable AQARA_API_KEY, "
                "or pass api_key argument."
            )

        self.api_key = api_key
        self.base_url = _resolve_open_api_base_url(base_url)
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        if home_id:
            self.session.headers.update({"position_id": f"{home_id}"})

    # ─── HTTP helpers ───

    def _get(self, path: str, params: dict = None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params)
        return resp.json()

    def _post(self, path: str, data: dict = None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.post(url, json=data)
        return resp.json()

    # ─── Home management ───
    def get_homes(self, lang: str = "zh"):
        """List all homes for the current user."""
        if not lang:
            lang = "zh"
        self.session.headers.update({"lang": lang})
        return self._get("homes/query")

    def get_rooms(self):
        """List all rooms in the current home."""
        if not self.session.headers.get("position_id"):
            raise ValueError("Missing home_id. Set position_id in headers or load from API key.")
        return self._get("position/detail/query")

    # ─── Device info ───

    def get_home_devices(self):
        """List device details for the current home."""
        if not self.session.headers.get("position_id"):
            raise ValueError("Missing home_id. Set position_id in headers or load from API key.")
        return self._post("device/detail/query",data={})



    # ─── Device status ───
    def get_devices_status(self, data={}):
        """
        Query device status.

        data: request JSON body (e.g. device_ids); defaults to {}.
        """
        if not self.session.headers.get("position_id"):
            raise ValueError("Missing home_id. Set position_id in headers or load from API key.")
        return self._post("device/status/query",data=data)


    # ─── Device control ───
    def devices_control(self, data={}):
        """Send a control command to device(s) in the current home."""
        if not self.session.headers.get("position_id"):
            raise ValueError("Missing home_id. Set position_id in headers or load from API key.")
        return self._post("device/control",data=data)

 

def _print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    api = AqaraOpenAPI()
    tool_name = sys.argv[1]
    args = sys.argv[2:]
    tools = {
        "homes": lambda: api.get_homes(),
        "rooms": lambda: api.get_rooms(),
        "home_devices": lambda: api.get_home_devices(),
        "device_status": lambda: api.get_devices_status(
            json.loads(args[0]) if args else {}
        ),
        "device_control": lambda: api.devices_control(json.loads(args[0])),
    }

    if tool_name not in tools:
        print(f"Unknown tool: {tool_name}")
        sys.exit(1)

    _print_json(tools[tool_name]())


if __name__ == "__main__":
    main()
