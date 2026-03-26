# Aqara Agent Skills

This directory is a distributable package for Aqara smart home agent skills.

## About `aqara-agent`

### Purpose

`aqara-agent` provides a standardized runtime flow for smart-home operations through Aqara Open API, so an AI agent can complete account setup, home selection, device query, device control, and scene execution with consistent guardrails.

### Target Users

- AI application developers who need smart-home capability in their assistants
- Agent platform integrators (for example OpenClaw-like hosts)
- Internal operators or solution engineers who run scripted home/device workflows

### Core Functions

- Account/session management: login guidance, save `aqara_api_key`, auth retry handling
- Home/space management: list homes, select/switch home, list rooms
- Device inquiry: list devices and query live status
- Device control: send supported control commands to matched devices
- Scene management: list scenes and execute selected scene IDs
- Safety guardrails: require real API/script outputs and forbid fabricated results

## Structure

```text
Aqara Agent Skills/
├── README.md
└── skills/
    └── aqara-agent/
        ├── SKILL.md
        ├── README.md
        ├── assets/
        ├── references/
        └── scripts/
```

## Quick Use

1. Enter the skill root:

```bash
cd "Aqara Agent Skills/skills/aqara-agent"
```

2. Install dependencies:

```bash
python3 -m pip install -r scripts/requirements.txt
```

3. Follow the runtime flow in `SKILL.md`:
- Sign in and save `aqara_api_key`
- Fetch/select home
- Run inquiry/control/scene actions

## Notes

- Default Aqara host is `agent.aqara.com` (override with `AQARA_OPEN_HOST`).
- Never fabricate home/device/scene data; only use real API/script outputs.
- Treat `assets/user_account.json` as sensitive.
