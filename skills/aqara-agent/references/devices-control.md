# Device Control

## Not Control (Routing)

**Firmware / OTA / device software upgrade** is **device configuration**, not `post_device_control`. **Must** use `references/devices-config.md` — **Forbidden** use `assets/device_control_action_table.csv` for upgrade intents.

**Scheduled device control** and **delayed device control** (as opposed to **immediate** `post_device_control`): whenever NL / intent falls in this category (time or clock as the trigger premise, then control devices or spatial targets such as lights / AC / curtains), semantically this is equivalent to **adding an automation** in Aqara Home (executed by cloud / gateway), **Must** **go straight into** the full [`automation-create.md`](automation-create.md) flow: `get_home_devices` and other grounding → Steps 01–03 → **`post_create_automation`** (time and condition splits: **`automation-create-workflow/`**). **Forbidden** to replace that business path with host-side `sleep` / timers / cron, or ad hoc "call `post_device_control` later" schemes as the primary approach (when the API is unavailable, only explain the blocker; **forbidden** to pretend an automation was created).

## Goal

**Must** locate devices before control. **Must** user-facing: outcome first; zh users: success = affirmative + location + device + outcome; failure = short `{location}{device} control failed` (or omit location if unknown). **Must** add auth/next steps only when required (`Auth failure`, end of reply patterns).

## Control slots (`attribute` / `action` / `value`)

The former **Action Table** and per-`device_type` hints are **merged** into one file: **`assets/device_control_action_table.csv`**.

**Must** read that CSV before mapping user intent to slots (after devices are located). Columns: `device_type`, `attribute`, `action`, `value_range`, `default_value`, `unit`, `category_name_zh`, `category_name_en`. **Must** extend **only** the CSV when adding attributes or device families - **do not** reintroduce a separate Action Table in this doc.

**Row match (same as CSV semantics):** For each endpoint, take `device_type` from `get_home_devices`. A CSV row applies if its **`device_type`** cell is **`Any`** (use that row for every endpoint for that **`attribute`**) **or** the cell is a **substring** of `device_type`. If a cell contains **`/`** (legacy compact form), **either** side matching as substring applies. **Current CSV** lists `WindowCovering`, `ClotheDryingMachine`, `Speaker`, and `VideoDoorbell` as **separate** rows (no combined `Speaker/VideoDoorbell` cell). Hints are not a substitute for live API behavior - tenant may differ.

## Workflow

1. **Split** multi-device/action utterances; semantic order; **Must** query before control if both in one sub-request.
2. **Locate:** `home-space-manage.md` + `devices-inquiry.md` list. Generic categories ("all lights", AC, curtains): **Must** filter `get_home_devices` by `device_type` substring (`devices-inquiry.md` table). Multi-match -> `endpoint_id` -> `device_ids`.
3. **Map** user intent -> `attribute` / `action` / `value`: **Must** use **`assets/device_control_action_table.csv`** only. Unsupported capability -> **Must** say unsupported.
4. **Send:**

```bash
python3 scripts/aqara_open_api.py post_device_control '{"device_ids":["device_id_1","device_id_2"],"attribute":"brightness","action":"set","value":"30"}'
```

5. **Reply** per patterns below.

## User-Facing Patterns

**Forbidden** `endpoint_id` or other raw ids in user message.

### Success

| Case   | Shape                                                   |
| ------ | ------------------------------------------------------- |
| On     | `[Affirmative], [location] [device] [opened].`          |
| Off    | `[Affirmative], [location] [device] [closed].`          |
| Adjust | `[Affirmative], [location] [device] [set to] {target}.` |

Localize. Multi-step: one sentence per step or summary + lines.

### Failure (Non-Auth)

**Must** one short line: `{location}{device} control failed` (e.g. `Living room light control failed.`).

### Auth

**`unauthorized or insufficient permissions`:** **Must** `aqara-account-manage.md` (re-login); **Forbidden** only generic failure line without guidance; **Allowed:** add localized "sign in again and retry" with failure pattern.

## Auth Failure

**`unauthorized or insufficient permissions`:** **Must** re-login per `aqara-account-manage.md`; **Forbidden** claim control succeeded.
