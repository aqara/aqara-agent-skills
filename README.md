# Aqara Agent Skills

Official AI skills library from Aqara for agent-driven smart-home workflows.

## About `aqara-agent`

### Purpose

`aqara-agent` defines a consistent runtime for Aqara Open API: account setup, home selection, device query/control, and scenes—so assistants follow the same guardrails and never treat guessed data as fact.

### Who it is for

- Developers wiring smart-home into AI assistants
- Agent hosts and integrators (e.g. OpenClaw-style platforms)
- Operators running scripted home/device checks

### Capabilities

| Area | What it covers |
|------|----------------|
| Account / session | Login guidance, save `aqara_api_key`, re-auth on failure |
| Home / space | List homes, select or switch default home, list rooms |
| Device inquiry | Home device list, live status where supported |
| Device control | Supported attributes/actions per `references/devices-control.md` |
| Scenes | List scenes, execute by matched scene |
| Safety | Outcomes and counts must come from real API/script output only |

## Repository layout

```text
Aqara Agent Skills/
├── README.md
└── skills/
    └── aqara-agent/
        ├── SKILL.md                 # Skill entry: workflow, errors, notes
        ├── assets/
        │   ├── login_reply_prompt.json   # Locales, default_login_url
        │   ├── login_qr.png              # Optional; same URL as default_login_url (regen if URL changes)
        │   ├── user_account.example.json # Template for local user_account.json
        │   └── user_account.json         # Local only (gitignored); credentials + home
        ├── references/              # Step-by-step flows (account, home, devices, scenes)
        └── scripts/
            ├── aqara_open_api.py    # CLI: homes, rooms, home_devices, device_control, …
            ├── save_user_account.py # Persist api key / home selection
            ├── runtime_utils.py
            └── requirements.txt
```

## Quick start

1. Go to the skill root:

```bash
cd "Aqara Agent Skills/skills/aqara-agent"
```

2. Install dependencies:

```bash
python3 -m pip install -r scripts/requirements.txt
```

3. Configure environment (optional overrides):

```bash
export AQARA_OPEN_HOST=agent.aqara.com
# Optional: full REST base URL instead of host-derived default
# export AQARA_OPEN_API_URL=https://agent.aqara.com/open/api
```

4. Follow **`SKILL.md`** and **`references/`**:

   - Sign in and save `aqara_api_key` (see `references/aqara-account-manage.md`).
   - After saving the key, **in a separate shell invocation**, fetch homes and set `home_id` / `home_name` (see `references/home-space-manage.md`). Do **not** chain `save_user_account.py` and `aqara_open_api.py homes` with `&&` on one line.
   - Then run inquiry, control, or scene flows as documented.

## Script CLI (summary)

`python3 scripts/aqara_open_api.py <tool> [json_body]`

Common tools: `homes`, `rooms`, `home_devices`, `device_status`, `device_control`, `home_scenes`, `execute_scenes`.

Details and JSON shapes: see `SKILL.md` and the matching `references/*.md` files.

## Packaging

To ship the skill folder only (from `skills/`):

```bash
cd "Aqara Agent Skills/skills"
tar -czf aqara-agent.tar.gz aqara-agent
```

## Notes

- Default Open Platform host is **`agent.aqara.com`**; override with **`AQARA_OPEN_HOST`** (or **`AQARA_OPEN_API_URL`** for the full base URL).
- Do not present homes, devices, scenes, or states without a successful script/API run.
- Treat **`assets/user_account.json`** as secret.

## Git and GitHub

- **Do not commit** `skills/aqara-agent/assets/user_account.json` (contains `aqara_api_key` and `home_id`). The workspace `.gitignore` excludes it.
- After clone, copy `assets/user_account.example.json` to `assets/user_account.json` and complete login plus home selection per `references/aqara-account-manage.md` and `references/home-space-manage.md`.
- To publish: create an empty GitHub repository, then `git init`, add, commit, `git remote add origin <url>`, and `git push -u origin <branch>`.
