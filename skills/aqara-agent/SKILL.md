---
name: aqara-agent
description: "aqara-agent is an official Aqara Home AI Agent skill. It supports natural-language home and space management, device inquiry, device control, device logs, scene management (query, execute, create, snapshot, and logs), automation management (query, detail, toggle, and logs), and energy / electricity-cost statistics (by device, room, or home). Examples: \"How many lights are at home?\", \"Switch to my other home.\", \"Turn off the living room AC.\", \"What are the temperature and humidity in the bedroom?\", \"Show device logs for this device.\", \"Run the Movie scene.\", \"Recommend a bedtime setup for the bedroom.\", \"Create a good-night scene in the bedroom.\", \"Capture a scene snapshot of how things are now.\", \"Which scenes use the kitchen lights?\", \"What automations do I have?\", \"Turn off the morning routine automation.\", \"What triggers the Leave Home automation?\", \"What was last month's electricity bill at home?\", \"How much power did the bedroom use this week?\", \"Check automation execution in the bedroom for the last three days.\", \"Show scene run history for the Movie scene.\""
---

# Aqara Smart Home AI Agent Skill

## Basics

- **Host (default):** `agent.aqara.com` - override with `AQARA_OPEN_HOST`. **Skill root:** `skills/aqara-agent/`. **Wrapper:** `scripts/aqara_open_api.py` (`AqaraOpenAPI` -> Open Platform REST, including energy).

### `aqara_open_api.py` CLI

- **Invocation:** `python3 scripts/aqara_open_api.py <method_name> [json_body]`.
- **Must:** first argument equals the **exact** public method name on `AqaraOpenAPI` (see bash examples in `references/*.md`). **Forbidden:** aliases or shortened names unless a reference documents an equivalent.
- **Dispatch:** `get_*` -> no JSON body; `post_*` -> JSON object (optional, default `{}`).
- **Energy:** `post_energy_consumption_statistic` - route from **`device_ids` only** (non-empty -> device API; else position). Fields and NL mapping: `references/energy-statistic.md`.
- **Methods (ground list):** `get_homes`, `get_rooms`, `get_home_devices`, `get_home_scenes`, `get_home_automations`, `post_current_outdoor_weather`, `post_device_base_info`, `post_device_status`, `post_device_control`, `post_device_log`, `post_execute_scene`, `post_scene_detail_query`, `post_create_scene`, `post_scene_snapshot`, `post_scene_execution_log`, `post_automation_detail_query`, `post_automation_execution_log`, `post_automation_switch`, `post_energy_consumption_statistic`. **Forbidden** call names not present on `AqaraOpenAPI` unless a reference adds them.
- **Optional env:** `AQARA_OPEN_HTTP_TIMEOUT` (default 60), `AQARA_OPEN_API_URL`.

## Skill Package Layout

Relative to `skills/aqara-agent/`. **Normative:** this file + `references/*.md` + `references/scene-workflow/*.md` where scene applies + `references/automation-workflow/*.md` where automation applies. `README.md` is a human index only.

| Path | Purpose |
|------|---------|
| `SKILL.md` | This document. |
| `README.md` | Human index; **Forbidden** treat as overriding `SKILL.md`. |
| `assets/login_reply_prompt.json` | Locales, `official_open_login_url`, `login_url_policy`. |
| `assets/user_account.example.json` | Template shape. |
| `assets/user_account.json` | Live session (sensitive). |
| `assets/device_control_action_table.csv` | Normative `attribute` / `action` / `value` mapping for control and scene slots (`devices-control.md`, scene workflows). |
| `references/*.md` | Per-domain procedures (account, home-space, devices, scenes index, automations, energy, weather). |
| `references/scene-workflow/*.md` | Scene sub-workflows; enter via `references/scene-manage.md`. **Files (scan):** `list.md` (catalog `#catalog-list` + `#scenes-by-device`), `execute.md`, `recommend.md`, `create.md`, `snapshot.md`, `execution-log.md`, `failure-response.md`, `appendices.md`. |
| `references/automation-workflow/*.md` | Automation sub-workflows; enter via `references/automation-manage.md`. **Files (scan):** `list.md` (catalog `#catalog-list` + by-device `#by-device`), `toggle.md`, `execution-log.md`, `failure-response.md`. |
| `scripts/aqara_open_api.py` | CLI + HTTP client. |
| `scripts/save_user_account.py` | Writes `aqara_api_key`. |
| `scripts/runtime_utils.py` | Shared helpers. |
| `scripts/requirements.txt` | Dependencies. |

## Core Workflow

**deps -> sign-in -> pick home -> intent -> `references/*.md` -> summarize**

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
- Locale from JSON for the user's language; unknown -> `en` (`fallback_locale` / `default_locale`). **Must** deliver the **single-line** login URL per `references/aqara-account-manage.md`.

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

- **Must** after saving `aqara_api_key` run `references/home-space-manage.md` step **0** immediately (fetch homes; one home -> write; many -> user picks). **Forbidden** reply only "send home name" without running fetch.
- **Must** run `save_user_account.py` and `aqara_open_api.py get_homes` as **two separate** invocations. **Forbidden** `&&` on one shell line (`aqara-account-manage.md` step 2, `home-space-manage.md` step 0).
- **Switch home:** **Must** re-fetch homes and let the user choose (`home-space-manage.md`). **Forbidden** default to re-login. **Must** use `aqara-account-manage.md` login only if the user demands re-login/token rotation or the API signals expired/unauthorized.

### 4. Intent

Categories: space, device query, control, scene, automation, energy. **Multiple intents:** **Must** query before control, in utterance order.

| Intent | `AqaraOpenAPI` methods (details in reference) | Reference |
|--------|-----------------------------------------------|-----------|
| Space | `get_homes`, `get_rooms` | `references/home-space-manage.md` |
| Device query | `get_home_devices`, `post_device_status`; optional `post_device_base_info`, `post_device_log` | `references/devices-inquiry.md` |
| Device control | `post_device_control` | `references/devices-control.md` + `assets/device_control_action_table.csv` |
| Scene | `get_home_scenes`, `post_execute_scene`, `post_create_scene`, `post_scene_snapshot`, `post_scene_detail_query`, `post_scene_execution_log`; **`post_current_outdoor_weather`** - **only** [Scene recommend workflow](references/scene-workflow/recommend.md) step 7 **Leaving home** before control (`references/weather-forecast.md`); **Forbidden** elsewhere. Recommend path uses `post_device_control` unless **Create scene** applies. Catalog list + `post_scene_detail_query`: [list.md](references/scene-workflow/list.md) (`#catalog-list`, `#scenes-by-device`) | `references/scene-manage.md` (index); `references/weather-forecast.md`; other steps in `references/scene-workflow/*.md` |
| Automation | `get_home_automations`, `post_automation_detail_query`, `post_automation_switch`, `post_automation_execution_log` | `references/automation-manage.md` (index); catalog + by-device: [list.md](references/automation-workflow/list.md); toggle: [toggle.md](references/automation-workflow/toggle.md); logs: [execution-log.md](references/automation-workflow/execution-log.md) |
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

### Error Handling

| Situation | Action |
|-----------|--------|
| Device not found | **Must** state no match; **allowed:** short candidate list. |
| Capability unsupported | **Must** state unsupported; **Forbidden** imply success. |
| Home/room not found | **Must** state no hit; **Must** direct next step via `references/` (re-fetch or verify home). |
| Multiple device matches | **Must** list matches; **Must** one disambiguation question (room or full name). |
| Not signed in / empty `aqara_api_key` | **Must** login + save per `references/aqara-account-manage.md`, then homes. `MissingAqaraApiKeyError` -> same. |
| No home selected | **Must** `references/home-space-manage.md`. No `home_id` -> `homes/query`; one home -> auto-write; many -> `home_selection_required`. |
| Bad token / auth | **Must** re-login / refresh (no secret leak). **Forbidden** treat **home switch** as auth failure unless home-list returns auth error. `unauthorized or insufficient permissions` (or equivalent) -> **Must** re-login per `references/aqara-account-manage.md`; **Forbidden** fake success. |
| Control path blocked | **Must** say device found, command not sent. |
| Other | **Must** short summary + retry/`references/`; **Forbidden** internal URLs or full headers. |
| Indeterminate | **Must** use `references/` + script output; confirmed bug -> **Must** file skill issue. |
| Empty API data | **Forbidden** invent entities/readings; **Must** re-run or report failure (**Ground truth**). |
| HTTP / network | **Forbidden** treat as success; **Must** retry or brief explanation; **Forbidden** raw stacks. |

## Notes

1. **Forbidden** raw IDs in user text (device, position, `home_id`, ...). **Exception:** `automation_id` **allowed** if server desensitized virtual ID.
2. After layout changes, if match fails: **Must** re-fetch space + devices (`references/home-space-manage.md`, `references/devices-inquiry.md`), retry.
3. User replies: **Must** conclusion first, then detail; **Must** <= one clarification question.
4. **Session gate:** unsigned -> **Must** end on setup; **Forbidden** imply control ran.
5. **Must** run `scripts/*.py` automatically when required (stricter host policy wins).
6. Account/home change: **Must** update `user_account.json` and re-run [`references/aqara-account-manage.md`](references/aqara-account-manage.md).
7. **Forbidden** echo tokens/headers; **Must** treat `user_account.json` and caches as sensitive.
8. Multiple fuzzy name hits: **Must** user confirm.
9. User-visible: **Forbidden** shell, paths, raw stdout, debug JSON, `references/` filenames; **Must** plain summary.
10. Control OK: **Must** brief close; **Forbidden** preemptive hedging; fix only after user reports failure.

## Out of Scope

**Fully unsupported** (no API in this skill; point users to **Aqara Home app** when relevant):

- **Cameras** - live view / playback.
- **Locks** - unlock / lock-unlock.
- **Shortcuts** (e.g. Siri lists) - **Must** point to **Aqara Home app**.
- **Weather** - general forecasts and Q&A; **exception:** `post_current_outdoor_weather` **only** in [recommend.md](references/scene-workflow/recommend.md) step 7 **Leaving home** before control - see [weather-forecast.md](references/weather-forecast.md); **Forbidden** for Create scene, snapshot, run catalog scene, logs, or any other flow.
- **Entertainment** - beyond [devices-control.md](references/devices-control.md).

**Limited to documented workflows** (no app-only or undocumented features):

- **Scenes** - **only** procedures in [scene-manage.md](references/scene-manage.md) and `references/scene-workflow/*.md` (e.g. `list.md`, `execute.md`, `recommend.md`, `create.md`, `snapshot.md`, `execution-log.md`, `failure-response.md`, `appendices.md`).
- **Automations** - **only** procedures in [automation-manage.md](references/automation-manage.md) and `references/automation-workflow/*.md` (`list.md`, `toggle.md`, `execution-log.md`, `failure-response.md`).

**When** the user asks outside the above: **Must** say unsupported (or not yet); **Must** direct to **Aqara Home app** if the app covers it.
