# aqara-agent (Aqara Home AI Agent skill pack)

Human-readable **index** for this directory. **Normative behavior, constraints, and workflows** are defined in [`SKILL.md`](skills/aqara-agent/SKILL.md). This README does **not** override `SKILL.md`.

## What this is

An **official-style** skill pack for natural-language **Aqara Open API** operations: account and session, homes and rooms, device inquiry and control, **ambience / mood creation** (`ambience_create`: scene match, composite lights-off then device control, optional music, named lighting effects), lighting-preset inquiry and thin apply, firmware/OTA only, device logs, scenes (list, execute, create, snapshot, logs, recommend), automations (list, toggle, logs, recommend-then-create, **NL-driven** `post_create_automation`), energy statistics, and **scoped** outdoor weather. Execution is via **Python CLI scripts** plus Markdown **reference procedures**.

**Skill root:** this folder (`Aqara Agent Skills/skills/aqara-agent/`). The same layout may also live under `.cursor/skills/aqara-agent/` in Cursor projects; paths in docs are always relative to the skill root.

## Directory layout (scanned)

```text
aqara-agent/
├── SKILL.md                          # Authoritative skill spec (agents must follow this)
├── README.md                         # This file (index only)
├── assets/
│   ├── login_reply_prompt.json       # Login URL policy, locales, official_open_login_url
│   ├── device_control_action_table.csv
│   ├── user_account.example.json     # Shape template for user_account.json
│   └── user_account.json             # Live credentials + home selection (sensitive; do not commit)
├── scripts/
│   ├── aqara_open_api.py             # CLI: AqaraOpenAPI HTTP methods (get_* / post_*)
│   ├── save_user_account.py          # Persist aqara_api_key and home fields
│   ├── runtime_utils.py              # user_account load, optional base URL, UTF-8 stdio
│   └── requirements.txt
└── references/
    ├── aqara-account-manage.md
    ├── home-space-manage.md
    ├── devices-inquiry.md
    ├── devices-control.md
    ├── devices-config.md
    ├── ambience.md                   # ambience_create, LightingEffectAgent, save-scene payload, fast path
    ├── scene-manage.md
    ├── weather-forecast.md
    ├── energy-statistic.md
    ├── automation-manage.md
    ├── automation-create.md
    ├── scene-workflow/
    │   ├── list.md
    │   ├── execute.md
    │   ├── recommend.md
    │   ├── create.md
    │   ├── snapshot.md
    │   ├── execution-log.md
    │   ├── failure-response.md
    │   └── appendices.md
    ├── automation-workflow/
    │   ├── list.md
    │   ├── toggle.md
    │   ├── recommend.md
    │   ├── execution-log.md
    │   └── failure-response.md
    └── automation-create-workflow/
        ├── manifest.json
        ├── step-01-conditions-actions-extract.md
        ├── step-02-cell-info-fill.md
        └── step-03-parse-config-prompt.md
```

## Quick start (developers / operators)

1. **Open the normative spec:** [`SKILL.md`](skills/aqara-agent/SKILL.md) (CLI rules, method list, session order, intent table, error handling).
2. **Install dependencies** (from this directory):

   ```bash
   pip install -r scripts/requirements.txt
   ```

3. **Configure API host / base URL** as described in `SKILL.md` (e.g. `AQARA_OPEN_HOST`, `AQARA_OPEN_API_URL`, or `assets/user_account.json` keys such as `aqara_open_api_url`).
4. **Account file:** copy `assets/user_account.example.json` to `assets/user_account.json` if needed, then follow [`references/aqara-account-manage.md`](skills/aqara-agent/references/aqara-account-manage.md) for login and [`references/home-space-manage.md`](skills/aqara-agent/references/home-space-manage.md) for home selection.
5. **Invoke the API client** (from the skill root):

   ```bash
   python3 scripts/aqara_open_api.py get_homes
   ```

   `get_*` methods need no body (optional `{}`); `post_*` methods take a JSON object as the second argument. See bash examples in each `references/*.md` file.

## Where to read next

| Topic | Entry document |
|--------|----------------|
| End-to-end agent rules | [`SKILL.md`](skills/aqara-agent/SKILL.md) |
| Sign-in and API key | [`references/aqara-account-manage.md`](skills/aqara-agent/references/aqara-account-manage.md) |
| Homes / rooms / switching | [`references/home-space-manage.md`](skills/aqara-agent/references/home-space-manage.md) |
| Device list and status | [`references/devices-inquiry.md`](skills/aqara-agent/references/devices-inquiry.md) |
| Device control slots | [`references/devices-control.md`](skills/aqara-agent/references/devices-control.md) + [`assets/device_control_action_table.csv`](skills/aqara-agent/assets/device_control_action_table.csv) |
| **Ambience / mood (`ambience_create`)** | [`references/ambience.md`](skills/aqara-agent/references/ambience.md) (workflow, LightingEffectAgent, **save scene payload**, fast path for presets) |
| Firmware / OTA only | [`references/devices-config.md`](skills/aqara-agent/references/devices-config.md) |
| Scenes (index) | [`references/scene-manage.md`](skills/aqara-agent/references/scene-manage.md) → `references/scene-workflow/*.md` |
| Automations (index) | [`references/automation-manage.md`](skills/aqara-agent/references/automation-manage.md) → `references/automation-workflow/*.md` |
| Create automation from NL | [`references/automation-create.md`](skills/aqara-agent/references/automation-create.md) → `references/automation-create-workflow/*` |
| Energy / cost | [`references/energy-statistic.md`](skills/aqara-agent/references/energy-statistic.md) |
| Outdoor weather (allowed scopes) | [`references/weather-forecast.md`](skills/aqara-agent/references/weather-forecast.md) |

**Note:** Persisted **lighting ambience** scene saves are specified in [`references/ambience.md#save-scene-payload`](skills/aqara-agent/references/ambience.md#save-scene-payload) and tied to create-scene APIs per [`SKILL.md`](skills/aqara-agent/SKILL.md) intent routing; follow `SKILL.md` for when **not** to use `scene-workflow/create.md`.

## Security notes

- Treat **`assets/user_account.json`** as **secret**: it holds `aqara_api_key` and home selection. Prefer `.gitignore` in consuming repos and never paste keys into shared logs.
- Login guidance must use the URL from **`assets/login_reply_prompt.json`** (`official_open_login_url` / `login_url_policy`), not invented OAuth URLs.

## Pack metadata

Skill name and agent-facing description live in the YAML front matter at the top of [`SKILL.md`](skills/aqara-agent/SKILL.md).
