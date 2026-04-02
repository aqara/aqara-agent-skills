---
name: aqara-agent
description: "aqara-agent is an official Aqara Home AI Agent skill. It supports natural-language home and space management, device inquiry, device control, device logs, scene management (query, execute, and logs), automation management (query, detail, toggle, and logs), and energy / electricity-cost statistics (by device, room, or home). Examples: \"How many lights are at home?\", \"Turn off the living room AC.\", \"What are the temperature and humidity in the bedroom?\", \"Run the Movie scene.\", \"What automations do I have?\", \"How much the electricity bill for the past month is at home?\", \"Check automation execution in the bedroom for the last three days.\""
---

# Aqara Smart Home AI Agent Skill

## Basics

- **Host (default):** `agent.aqara.com` — override with `AQARA_OPEN_HOST`. **Skill root:** `skills/aqara-agent/`. **Wrapper:** `scripts/aqara_open_api.py` (`AqaraOpenAPI` → Open Platform REST, including energy).

### `aqara_open_api.py` CLI

- **Invocation:** `python3 scripts/aqara_open_api.py <method_name> [json_body]`.
- **Must:** first argument equals the **exact** public method name on `AqaraOpenAPI` (see bash examples in `references/*.md`). **Forbidden:** aliases or shortened names unless a reference documents an equivalent.
- **Dispatch:** `get_*` → no JSON body; `post_*` → JSON object (optional, default `{}`).
- **Energy:** `post_energy_consumption_statistic` — route from **`device_ids` only** (non-empty → device API; else position). Fields and NL mapping: `references/energy-statistic.md`.
- **Optional env:** `AQARA_OPEN_HTTP_TIMEOUT` (default 60), `AQARA_OPEN_API_URL`.

## Skill Package Layout

Relative to `skills/aqara-agent/`. **Normative:** this file + `references/*.md`. `README.md` is a human index only.

| Path | Purpose |
|------|---------|
| `SKILL.md` | This document. |
| `README.md` | Human index; **Forbidden** treat as overriding `SKILL.md`. |
| `assets/login_reply_prompt.json` | Locales, `official_open_login_url`, `login_url_policy`. |
| `assets/user_account.example.json` | Template shape. |
| `assets/user_account.json` | Live session (sensitive). |
| `references/*.md` | Per-domain procedures (account, home-space, devices, scenes, automations, energy). |
| `scripts/aqara_open_api.py` | CLI + HTTP client. |
| `scripts/save_user_account.py` | Writes `aqara_api_key`. |
| `scripts/runtime_utils.py` | Shared helpers. |
| `scripts/requirements.txt` | Dependencies. |

## Core Workflow

**deps → sign-in → pick home → intent → `references/*.md` → summarize**

## Ground Truth (Binding)

**Forbidden** stating or implying as factual: homes, rooms, devices, capabilities, attributes, counts, logs, or control outcomes, except from **executed** skill scripts + real API responses or skill-accepted user input (e.g. pasted `aqara_api_key`). If that flow **has not** succeeded, **Forbidden** any factual claim about those entities.

**Forbidden** demo-style lists, guessed layouts, synthetic values, fake success after errors/timeouts/missing auth, or prose/JSON mimicking API output without a real response.

**Must** state missing data and cause (e.g. not signed in, API error), then auth/retry/`references/`. **Forbidden** imagined padding.

---

Execute in order:

### 1. Environment

```bash
export AQARA_OPEN_HOST=agent.aqara.com   # test; omit or set prod host as required
```

```bash
cd skills/aqara-agent
pip install -r scripts/requirements.txt
```

### 2. Auth

- **Must** confirm `user_account.json` readable/writable before features; host/project rules may require reading it first.
- **Must** follow `references/aqara-account-manage.md` (switch-home vs re-login, token save, Step 1 login copy).
- **Must** read `assets/login_reply_prompt.json` on every login guidance turn. **Must** set the user-facing login link to the **exact** `official_open_login_url` string (`login_url_policy`). **Forbidden** invent Open Platform / `sns-auth` / `client_id` / `redirect_uri` URLs from memory.
- Locale from JSON for the user’s language; unknown → `en` (`fallback_locale` / `default_locale`). **Must** deliver the **single-line** login URL per `references/aqara-account-manage.md`.

`user_account.json`:

```json
{
  "aqara_api_key": "",
  "updated_at": "",
  "home_id": "",
  "home_name": ""
}
```

### 3. Home Management

- **Must** after saving `aqara_api_key` run `references/home-space-manage.md` step **0** immediately (fetch homes; one home → write; many → user picks). **Forbidden** reply only “send home name” without running fetch.
- **Must** run `save_user_account.py` and `aqara_open_api.py get_homes` as **two separate** invocations. **Forbidden** `&&` on one shell line (`aqara-account-manage.md` step 2, `home-space-manage.md` step 0).
- **Switch home:** **Must** re-fetch homes and let the user choose (`home-space-manage.md`). **Forbidden** default to re-login. **Must** use `aqara-account-manage.md` login only if the user demands re-login/token rotation or the API signals expired/unauthorized.

### 4. Intent

Categories: space, device query, control, scene, automation, energy. **Multiple intents:** **Must** query before control, in utterance order.

| Intent | `AqaraOpenAPI` methods (details in reference) | Reference |
|--------|-----------------------------------------------|-----------|
| Space | `get_homes`, `get_rooms` | `references/home-space-manage.md` |
| Device query | `get_home_devices`, `post_device_status`; optional `post_device_base_info`, `post_device_log` | `references/devices-inquiry.md` |
| Device control | `post_device_control` | `references/devices-control.md` |
| Scene | `get_home_scenes`, `post_execute_scene`, `post_scene_detail_query`, `post_scene_execution_log` | `references/scene-manage.md` |
| Automation | `get_home_automations`, `post_automation_detail_query`, `post_automation_switch`, `post_automation_execution_log` | `references/automation-manage.md` |
| Energy | `post_energy_consumption_statistic` | `references/energy-statistic.md` |

### 5. Route and Summarize

**Must** open the matching `references/` doc, run scripts, summarize from **actual** output only. **Forbidden** fabricate success or any home/room/device/state not in script/API output (**Ground truth**).

### Illustrative CLI JSON (Agents Only)

**Forbidden** paste these raw blocks to end users.

REST shape (skeleton):

```json
{
  "code": 0,
  "message": "",
  "data": {}
}
```

Bad params / parse error (skeleton):

```json
{
  "ok": false,
  "error": "..."
}
```

### Error Handling

| Situation | Action |
|-----------|--------|
| Device not found | **Must** state no match; **allowed:** short candidate list. |
| Capability unsupported | **Must** state unsupported; **Forbidden** imply success. |
| Home/room not found | **Must** state no hit; **Must** direct next step via `references/` (re-fetch or verify home). |
| Multiple device matches | **Must** list matches; **Must** one disambiguation question (room or full name). |
| Not signed in / empty `aqara_api_key` | **Must** login + save per `aqara-account-manage.md`, then homes. `MissingAqaraApiKeyError` → same. |
| No home selected | **Must** `home-space-manage.md`. No `home_id` → `homes/query`; one home → auto-write; many → `home_selection_required`. |
| Bad token / auth | **Must** re-login / refresh (no secret leak). **Forbidden** treat **home switch** as auth failure unless home-list returns auth error. `unauthorized or insufficient permissions` (or equivalent) → **Must** re-login per `aqara-account-manage.md`; **Forbidden** fake success. |
| Control path blocked | **Must** say device found, command not sent. |
| Other | **Must** short summary + retry/`references/`; **Forbidden** internal URLs or full headers. |
| Indeterminate | **Must** use `references/` + script output; confirmed bug → **Must** file skill issue. |
| Empty API data | **Forbidden** invent entities/readings; **Must** re-run or report failure (**Ground truth**). |
| HTTP / network | **Forbidden** treat as success; **Must** retry or brief explanation; **Forbidden** raw stacks. |

## Notes

1. **Forbidden** raw IDs in user text (device, position, `home_id`, …). **Exception:** `automation_id` **allowed** if server desensitized virtual ID.
2. After layout changes, if match fails: **Must** re-fetch space + devices (`home-space-manage.md`, `devices-inquiry.md`), retry.
3. User replies: **Must** conclusion first, then detail; **Must** ≤ one clarification question.
4. **Session gate:** unsigned → **Must** end on setup; **Forbidden** imply control ran.
5. **Must** run `scripts/*.py` automatically when required (stricter host policy wins).
6. Account/home change: **Must** update `user_account.json` and re-run [`aqara-account-manage.md`](references/aqara-account-manage.md).
7. **Forbidden** echo tokens/headers; **Must** treat `user_account.json` and caches as sensitive.
8. Multiple fuzzy name hits: **Must** user confirm.
9. User-visible: **Forbidden** shell, paths, raw stdout, debug JSON, `references/` filenames; **Must** plain summary.
10. Control OK: **Must** brief close; **Forbidden** preemptive hedging; fix only after user reports failure.

## Out of Scope

**Unsupported** (no create/edit in this wrapper):

- **Cameras** — live / playback.
- **Locks** — unlock / lock-unlock.
- **Scene authoring** — only ops in `references/scene-manage.md`.
- **Automation authoring** — only ops in `references/automation-manage.md`.
- **Shortcuts** (e.g. Siri lists) — **Must** point to **Aqara Home app**.
- **Weather** — outside this API.
- **Entertainment** — beyond `references/devices-control.md`.

**When** user asks for unsupported: **Must** say unsupported (or not yet); **Must** direct to **Aqara Home app** if the app covers it.
