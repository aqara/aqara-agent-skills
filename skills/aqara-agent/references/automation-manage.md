# Automation Management (index)

This file is the **entry point** for automation-related agent behavior. **Normative detail** is split under **`references/automation-workflow/`**; open the file that matches the user's intent. **Must** satisfy **`SKILL.md`** ground truth (scripts + real API output only).

Scenes are **not** automations -> use [`scene-manage.md`](scene-manage.md) (and [`scene-workflow/`](scene-workflow/) as needed).

---

## Contents (split references)

| Topic | File |
| --- | --- |
| List / discover automations | [automation-workflow/list.md#catalog-list](automation-workflow/list.md#catalog-list) |
| Automations tied to devices | [automation-workflow/list.md#by-device](automation-workflow/list.md#by-device) |
| Enable / disable (toggle) | [automation-workflow/toggle.md](automation-workflow/toggle.md) |
| Execution history / logs | [automation-workflow/execution-log.md](automation-workflow/execution-log.md) |
| Failure + user-facing response | [automation-workflow/failure-response.md](automation-workflow/failure-response.md) |

---

## Intents (routing)

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
5. Automations != scenes -> `scene-manage.md` for scenes. **Forbidden** create/edit/delete automations in this skill -> **Must** **Aqara Home app** for authoring.
6. Toggle: **Must** resolve target from `get_home_automations` first; ambiguous -> **Must** one question before switch. See [toggle.md](automation-workflow/toggle.md).

---

## Intent routing (quick)

| User goal | Read | Primary tool(s) |
| --- | --- | --- |
| List catalog automations | [list.md#catalog-list](automation-workflow/list.md#catalog-list) | `get_home_automations` |
| Automations for device(s) | [list.md#by-device](automation-workflow/list.md#by-device) | `get_home_devices`, `post_automation_detail_query` |
| Turn automation on/off | [toggle.md](automation-workflow/toggle.md) | `get_home_automations`, `post_automation_switch` |
| Automation run history | [execution-log.md](automation-workflow/execution-log.md) | `get_home_automations`, `post_automation_execution_log` |

---

## After you pick a workflow

1. Open the linked **`automation-workflow/*.md`** file.
2. Run `scripts/aqara_open_api.py` as documented there.
3. On errors or reply style, see [failure-response.md](automation-workflow/failure-response.md) and **`SKILL.md`**.
