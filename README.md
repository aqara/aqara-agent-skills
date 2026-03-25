# aqara-home-skills

An **AI Agent** skill (e.g. for Cursor) for Aqara smart homes. It uses the **Aqara Open API** for natural-language queries about homes, rooms, and devices, plus limited hardware control.

- **Aqara site**: https://www.aqara.com/cn/
- **Canonical agent spec**: [`SKILL.md`](SKILL.md) in this folder (workflow, errors, guardrails)

## Capabilities

| Area | What it covers |
|------|----------------|
| Account & homes | Login guidance, save access token, fetch home list, select/switch home |
| Space | List rooms in the current home |
| Devices | List devices and read state (attributes) |
| Control | Send control commands to supported devices (see `references/devices-control.md`) |

**Explicitly not supported** (use the Aqara Home app): camera/video, lock unlock, scenes & automations, energy & weather, etc. Full list: “Out of scope” in [`SKILL.md`](SKILL.md).

## Layout

```
aqara-home-skills/
├── README.md                 # This file (human quick start)
├── SKILL.md                  # Main agent playbook
├── assets/
│   └── user_account.json     # Local credentials & current home (gitignored)
├── references/               # Topic-specific playbooks
│   ├── aqara-account-manage.md
│   ├── home-space-manage.md
│   ├── devices-inquiry.md
│   └── devices-control.md
└── scripts/
    ├── requirements.txt
    ├── runtime_utils.py      # Config & user_account helpers
    ├── aqara_open_api.py     # Thin Open API wrapper + CLI
    └── save_user_account.py  # Persist token & home fields
```

## Requirements

- Python 3 (3.10+ recommended)
- Network access to the Aqara Open Platform gateway (default base URL in `scripts/aqara_open_api.py`, or `assets/api_path_config.json` if present)

## Install

From the **skill root**:

```bash
cd skills/aqara-home-skills
pip install -r scripts/requirements.txt
```

Scripts read `aqara_api_key` and `home_id` from `assets/user_account.json` (`home_id` is sent as header `position_id`).

## Quick start

1. **Account** — Follow [`references/aqara-account-manage.md`](references/aqara-account-manage.md): browser login, obtain access token (`aqara_api_key`), save locally (never leak the token in chat or commits).

2. **Save token (example)** — From `skills/aqara-home-skills`:

   ```bash
   python3 scripts/save_user_account.py aqara_api_key '<你的访问令牌>'
   ```

3. **Fetch homes & select** — **Important**: saving the token and `aqara_open_api.py homes` must be **two separate** runs; **do not** chain with `&&` on one line. See [`references/aqara-account-manage.md`](references/aqara-account-manage.md) and [`references/home-space-manage.md`](references/home-space-manage.md).

4. **Rooms / devices** — With a valid `home_id`, run the CLI subcommands below from the `scripts` context.

## CLI (`aqara_open_api.py`)

Run from **`skills/aqara-home-skills/scripts`**:

| Subcommand | Purpose |
|------------|---------|
| `homes` | List homes for the account |
| `rooms` | List rooms for current `home_id` |
| `home_devices` | Device details for current home |
| `device_status` | Device status (optional JSON args; see script) |
| `device_control` | Send control (JSON required; see `references/devices-control.md`) |

Examples:

```bash
cd skills/aqara-home-skills/scripts
python3 aqara_open_api.py homes
python3 aqara_open_api.py rooms
python3 aqara_open_api.py home_devices
```

Write current home:

```bash
python3 scripts/save_user_account.py home '<home_id>' '<home_name>'
```

## `user_account.json` fields

```json
{
  "aqara_api_key": "",
  "updated_at": "",
  "home_id": "",
  "home_name": ""
}
```

- `aqara_api_key`: platform access token  
- `home_id` / `home_name`: selected home (maps to position/home ids in the API)

Sensitive — **do not commit**; `.gitignore` ignores `assets/user_account.json` and related local files.

## Using in Cursor

- Open a workspace that contains `skills/aqara-home-skills`; if `.cursor/rules/` includes Aqara rules, the agent should verify account/home before query/control.
- You can also copy this skill to a personal skills path (e.g. `~/.cursor/skills/aqara-home-skills/`) for reuse across projects—follow your Cursor version’s skill loading behavior.

## Reference index (`references/`)

| Doc | Topic |
|-----|--------|
| [`aqara-account-manage.md`](references/aqara-account-manage.md) | Login, token save, auth failures |
| [`home-space-manage.md`](references/home-space-manage.md) | Home list, selection, rooms |
| [`devices-inquiry.md`](references/devices-inquiry.md) | Device & status queries |
| [`devices-control.md`](references/devices-control.md) | Control & safety bounds |

## Legal

Using this skill with Aqara’s Open Platform is subject to [Aqara](https://www.aqara.com/cn/) and the platform’s terms.
# aqara-home-skills
