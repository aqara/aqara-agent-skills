#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_ROOT = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from runtime_utils import merge_user_context_home_info, print_json, set_aqara_api_key

# When argv[0] is already a subcommand, do not prepend api-key
_SUBCOMMAND_PREFIXES = frozenset({"api-key", "aqara_api_key", "home"})


def _cmd_api_key(args: argparse.Namespace) -> int:
    if args.file is not None:
        raw = args.file.read_text(encoding="utf-8")
    elif args.api_key is not None:
        raw = args.api_key
    else:
        raw = sys.stdin.read()

    api_key = (raw or "").strip()
    if not api_key:
        print_json({"ok": False, "message": "api_key is empty"})
        return 2

    if args.dry_run:
        print_json({"ok": True, "dry_run": True, "aqara_api_key_length": len(api_key)})
        return 0

    try:
        set_aqara_api_key(api_key)
    except ValueError as e:
        print_json({"ok": False, "message": str(e)})
        return 2

    written = {"ok": True, "message": "Written aqara_api_key and updated_at to assets/user_account.json"}
    if args.continue_chain:
        get_user_info = _SCRIPT_DIR / "call_get_user_info.py"
        if not get_user_info.is_file():
            print_json({"ok": False, "message": f"missing {get_user_info} (drop --continue or add script)"})
            return 1
        written["next"] = "call_get_user_info.py"
        print(json.dumps(written, ensure_ascii=False, indent=2), file=sys.stderr)
        r = subprocess.run(
            [sys.executable, str(get_user_info)],
            cwd=str(_SKILL_ROOT),
        )
        return r.returncode if r.returncode != 0 else 0

    print_json(written)
    return 0


def _cmd_home(args: argparse.Namespace) -> int:
    home_id = (args.home_id or "").strip()
    if not home_id:
        print_json({"ok": False, "message": "home_id is empty"})
        return 2

    # If the second arg is omitted, leave the existing home_name in JSON unchanged
    home_name: str | None
    if args.home_name is None:
        home_name = None
    else:
        home_name = str(args.home_name).strip()

    if args.dry_run:
        print_json(
            {
                "ok": True,
                "dry_run": True,
                "home_id": home_id,
                "home_name": home_name if home_name is not None else None,
            }
        )
        return 0

    try:
        merge_user_context_home_info(
            home_id=home_id,
            home_name=home_name,
        )
    except ValueError as e:
        print_json({"ok": False, "message": str(e)})
        return 2

    print_json(
        {
            "ok": True,
            "message": "Written home fields and updated_at to assets/user_account.json",
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write credentials / home fields to assets/user_account.json",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pk = sub.add_parser(
        "api-key",
        aliases=["aqara_api_key"],
        help="Write aqara_api_key and updated_at",
    )
    pk.add_argument(
        "api_key",
        nargs="?",
        default=None,
        help="API key; omit to read from stdin (stripped)",
    )
    pk.add_argument("-f", "--file", type=Path, help="Read key from UTF-8 file (stripped)")
    pk.add_argument("--dry-run", action="store_true", help="Validate only; do not write")
    pk.add_argument(
        "--continue",
        dest="continue_chain",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="After write, run call_get_user_info.py if present (default: false)",
    )
    pk.set_defaults(handler=_cmd_api_key)

    ph = sub.add_parser("home", help="Write home_id, optional home_name, and updated_at")
    ph.add_argument("home_id", help="Selected home id (e.g. positionId from API)")
    ph.add_argument(
        "home_name",
        nargs="?",
        default=None,
        help="Display name; omit to keep existing home_name in JSON",
    )
    ph.add_argument("--dry-run", action="store_true", help="Validate only; do not write")
    ph.set_defaults(handler=_cmd_home)

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        argv = ["api-key"]
    elif argv[0] not in _SUBCOMMAND_PREFIXES:
        argv = ["api-key", *argv]
    args = build_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
