# Automation Management (index)

This file is the **entry point** for automation-related agent behavior. **Normative detail** is split under **`references/automation-workflow/`**; open the file that matches the user's intent. **Must** satisfy **`SKILL.md`** ground truth (scripts + real API output only).

**Recommend automation** (example NL first, then create) -> [`automation-workflow/recommend.md`](automation-workflow/recommend.md) only; **Must not** duplicate that workflow here.

Scenes are **not** automations -> use [`scene-manage.md`](scene-manage.md) (and [`scene-workflow/`](scene-workflow/) as needed).

---

## Contents (split references)

| Topic | File |
| --- | --- |
| Create new automation (NL → `raw_config` → API + optional `auxiliary_config`) | [automation-create.md](automation-create.md) |
| Recommend automation (example NL first, then create) | [automation-workflow/recommend.md](automation-workflow/recommend.md) |
| List / discover automations | [automation-workflow/list.md#catalog-list](automation-workflow/list.md#catalog-list) |
| Automations tied to devices | [automation-workflow/list.md#by-device](automation-workflow/list.md#by-device) |
| Enable / disable (toggle) | [automation-workflow/toggle.md](automation-workflow/toggle.md) |
| Execution history / logs | [automation-workflow/execution-log.md](automation-workflow/execution-log.md) |
| Failure + user-facing response | [automation-workflow/failure-response.md](automation-workflow/failure-response.md) |

---

## Intents (routing)

- **Scheduled / delayed device control** (time or clock condition + device or spatial-side actions, and **not** plain immediate `post_device_control`), and **scheduled / delayed scene control** (time or clock condition + run a **catalog scene**, and **not** immediate `post_execute_scene`): the user goal in each case is **to create an automation**, **Must** **go straight to** [automation-create.md](automation-create.md) (`post_create_automation`); scene-side grounding must use `get_home_scenes` etc. and match **`automation-create-workflow`** action intent **3**. **Forbidden** to discuss or implement host-only timers or "later call `post_execute_scene` / `post_device_control`" as the primary approach; only when `automation/create` is unavailable, explain why and point to the **Aqara Home app** (see `automation-create.md` failure handling). Wording is not limited to fixed example sentences; classify by whether NL / intent falls in the above categories.
- List/discover; filter by room/name; enabled count/status -> [list.md#catalog-list](automation-workflow/list.md#catalog-list).
- Automations involving specific devices -> [list.md#by-device](automation-workflow/list.md#by-device).
- Enable/disable toggle -> [toggle.md](automation-workflow/toggle.md).
- Execution history / logs -> [execution-log.md](automation-workflow/execution-log.md).

---

## Execution order

1. **Session:** **Must** `aqara_api_key` + `home_id` (`aqara-account-manage.md`, `home-space-manage.md`).
2. **Must** query from API before claims; answers only from script output.
3. Mixed intent: semantic order; query + control wording -> **Must** query first.
4. **Must** match names/rooms from retrieved list; **Forbidden** guess missing automations.
5. Automations != scenes -> `scene-manage.md` for scenes. **Flows not documented** under `automation-workflow/` (including editing or removing automations in ways this skill does not specify) -> **Must** **Aqara Home app** unless a future workflow is added to this skill.
6. Toggle: **Must** resolve target from `get_home_automations` first; ambiguous -> **Must** one question before switch. See [toggle.md](automation-workflow/toggle.md).

---

## Intent routing (quick)

| User goal | Read | Primary tool(s) |
| --- | --- | --- |
| **Create** automation (NL classified as **scheduled / delayed device control** or **scheduled / delayed scene control**) | [automation-create.md](automation-create.md) | Devices / rooms: `get_home_devices`, `get_rooms`, etc.; scenes: `get_home_scenes`, etc. → **`post_create_automation`** |
| **Recommend** automation (example sentences first, then create) | [recommend.md](automation-workflow/recommend.md) (**user-visible reply** in **§5**: on success, **recommend.md §5.2 lead-in (localized to user input language)** + numbered lines `1`–`10`; on error, error detail only and **forbidden** to output real **ids** for home / device / position / scene / automation — names may appear) | `get_rooms`, `get_home_devices`, `get_home_scenes` (optional `get_home_automations`) → after user picks → **`post_create_automation`** (see `automation-create.md`) |
| List catalog automations | [list.md#catalog-list](automation-workflow/list.md#catalog-list) | `get_home_automations` |
| Automations for device(s) | [list.md#by-device](automation-workflow/list.md#by-device) | `get_home_devices`, `post_device_related_automation_query` |
| Turn automation on/off | [toggle.md](automation-workflow/toggle.md) | `get_home_automations`, `post_automation_switch` |
| Automation run history | [execution-log.md](automation-workflow/execution-log.md) | `get_home_automations`, `post_automation_execution_log` |

---

## After you pick a workflow

1. If the path is **recommend automation** (example NL first): open [`automation-workflow/recommend.md`](automation-workflow/recommend.md) and follow it end-to-end; **Must not** use only this file’s `automation-workflow/` list as the sole guide.
2. Else: open the linked **`automation-workflow/*.md`** file.
3. Run `scripts/aqara_open_api.py` as documented in the opened workflow.
4. On errors or reply style, see [failure-response.md](automation-workflow/failure-response.md) and **`SKILL.md`**.
