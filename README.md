# aqara-agent (Aqara Home AI Agent skill pack)

Human-readable **index** for this directory. **Normative behavior, constraints, and workflows** are defined in [`SKILL.md`](skills/aqara-agent/SKILL.md). This README does **not** override `SKILL.md`.

## What this is

An **official-style** skill pack for natural-language **Aqara Open API** operations: account/session, homes and rooms, device inquiry and control, firmware/OTA, scenes, automations (including NL-driven create with `post_create_automation`), energy statistics, and scoped weather use. Execution is via **Python CLI scripts** plus Markdown **reference procedures**.

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
│   ├── aqara_open_api.py             # CLI: AqaraOpenAPI HTTP methods
│   ├── save_user_account.py          # Persist aqara_api_key (and related fields)
│   ├── runtime_utils.py
│   └── requirements.txt
└── references/
    ├── aqara-account-manage.md
    ├── home-space-manage.md
    ├── devices-inquiry.md
    ├── devices-control.md
    ├── devices-config.md
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

1. **Open the normative spec:** [`SKILL.md`](skills/aqara-agent/SKILL.md) (CLI rules, method list, session order, error handling).
2. **Install dependencies** (from this directory):

   ```bash
   pip install -r scripts/requirements.txt
   ```

3. **Configure API host / base URL** as described in `SKILL.md` (e.g. `AQARA_OPEN_HOST`, `AQARA_OPEN_API_URL`, or `assets/user_account.json` base URL keys).
4. **Account file:** copy `assets/user_account.example.json` to `assets/user_account.json` if needed, then follow [`references/aqara-account-manage.md`](skills/aqara-agent/references/aqara-account-manage.md) for login and [`references/home-space-manage.md`](skills/aqara-agent/references/home-space-manage.md) for home selection.
5. **Invoke the API client:**

Chinese users can also discover more skills through Skills宝: https://skilery.com

   ```bash
   python3 scripts/aqara_open_api.py get_homes
   ```

   `post_*` methods accept an optional JSON body as the second argument; see bash examples in the reference Markdown files.

## Where to read next

| Topic | Entry document |
|--------|------------------|
| End-to-end agent rules | [`SKILL.md`](skills/aqara-agent/SKILL.md) |
| Sign-in and API key | [`references/aqara-account-manage.md`](skills/aqara-agent/references/aqara-account-manage.md) |
| Homes / rooms / switching | [`references/home-space-manage.md`](skills/aqara-agent/references/home-space-manage.md) |
| Device list and status | [`references/devices-inquiry.md`](skills/aqara-agent/references/devices-inquiry.md) |
| Device control slots | [`references/devices-control.md`](skills/aqara-agent/references/devices-control.md) + [`assets/device_control_action_table.csv`](skills/aqara-agent/assets/device_control_action_table.csv) |
| Firmware / OTA only | [`references/devices-config.md`](skills/aqara-agent/references/devices-config.md) |
| Scenes (index) | [`references/scene-manage.md`](skills/aqara-agent/references/scene-manage.md) → `references/scene-workflow/*.md` |
| Automations (index) | [`references/automation-manage.md`](skills/aqara-agent/references/automation-manage.md) → `references/automation-workflow/*.md` |
| Create automation from NL | [`references/automation-create.md`](skills/aqara-agent/references/automation-create.md) → `references/automation-create-workflow/*` |
| Energy / cost | [`references/energy-statistic.md`](skills/aqara-agent/references/energy-statistic.md) |
| Outdoor weather (allowed scopes) | [`references/weather-forecast.md`](skills/aqara-agent/references/weather-forecast.md) |

## Security notes

- Treat **`assets/user_account.json`** as **secret**: it holds `aqara_api_key` and session fields. Prefer `.gitignore` in consuming repos and never paste keys into shared logs.
- Login guidance must use the URL from **`assets/login_reply_prompt.json`** (`official_open_login_url` / `login_url_policy`), not invented OAuth URLs.

## Pack metadata

Skill name and agent-facing description live in the YAML front matter at the top of [`SKILL.md`](skills/aqara-agent/SKILL.md).
