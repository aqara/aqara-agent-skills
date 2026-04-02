# Aqara Agent Skills

Agent **skills** for Aqara Home: natural-language home control and queries via the Aqara Open API, packaged for hosts that load skills from a `skills/` tree (e.g. Cursor, Claude).

## Layout

| Path | Description |
|------|-------------|
| [`skills/aqara-agent/`](skills/aqara-agent/) | **aqara-agent** — devices, scenes, automations, energy stats, account & home setup. |

## Where to read first

| File | Role |
|------|------|
| [`skills/aqara-agent/SKILL.md`](skills/aqara-agent/SKILL.md) | Normative workflow, **Must** / **Forbidden**, intent routing, errors, out-of-scope. |
| [`skills/aqara-agent/README.md`](skills/aqara-agent/README.md) | Human overview, directory map, setup, CLI summary. |
| [`skills/aqara-agent/references/`](skills/aqara-agent/references/) | Per-topic procedures and `aqara_open_api.py` bash examples. |

## Quick setup

From the skill root:

```bash
cd skills/aqara-agent
pip install -r scripts/requirements.txt
```

Session and login: copy [`skills/aqara-agent/assets/user_account.example.json`](skills/aqara-agent/assets/user_account.example.json) to `user_account.json` if needed, then follow [`skills/aqara-agent/references/aqara-account-manage.md`](skills/aqara-agent/references/aqara-account-manage.md). **Do not** commit real `user_account.json` or API keys.

## Archives under `skills/`

If present (e.g. `aqara-agent.zip`), they are snapshots of `skills/aqara-agent/`. For public sharing, rebuild without secrets or strip `assets/user_account.json` first.
