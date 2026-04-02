# Automation Management

## Intents

- List/discover; filter by room/name; enabled count/status.
- Enable/disable toggle.
- Execution history / logs.

## Execution Order

1. **Session:** **Must** `aqara_api_key` + `home_id` (`aqara-account-manage.md`, `home-space-manage.md`).
2. **Must** query from API before claims; answers only from script output.
3. Mixed intent: semantic order; query + control wording → **Must** query first.
4. **Must** match names/rooms from retrieved list; **Forbidden** guess missing automations.
5. Automations ≠ scenes → `scene-manage.md` for scenes. **Forbidden** create/edit/delete automations here → **Must** **Aqara Home app** for authoring.
6. Toggle: **Must** resolve target from `get_home_automations` first; ambiguous → **Must** one question before switch.

## List Automations

```bash
python3 scripts/aqara_open_api.py get_home_automations
```

Related methods: `post_automation_detail_query`, `post_automation_switch`, `post_automation_execution_log`.

- Reply: conclusion then detail; stable order room → name when possible.
- No exact name → 2–5 candidates + one question.

## Automations by Device (`post_automation_detail_query`)

1. **Must** `device_ids` from `get_home_devices` (`devices-inquiry.md`).
2. Path `automation/detail/query`.

```bash
python3 scripts/aqara_open_api.py post_automation_detail_query '{"device_ids":["<endpoint_id>"]}'
```

```bash
python3 scripts/aqara_open_api.py post_automation_detail_query '{"device_ids":["<endpoint_id_1>","<endpoint_id_2>"]}'
```

## Enable / Disable

1. **Must** `get_home_automations` → resolve by name + room.
2. **Must** map user intent to enable/disable.
3. **Must** send switch; reply from real output only.
4. **Forbidden** toggle if ambiguous.

```bash
python3 scripts/aqara_open_api.py post_automation_switch '{"automation_ids":["automation_id_1"],"switch":"off"}'
```

```bash
python3 scripts/aqara_open_api.py post_automation_switch '{"automation_ids":["automation_id_1"],"operation":"on"}'
```

(Adjust keys to live API.) **`automation_id` allowed** in user text when server returns desensitized virtual IDs. If switch missing in wrapper → **Must** say unsupported + suggest app.

## Execution Log

1. Resolve targets from `get_home_automations`.
2. Valid JSON time window.
3. Call if wrapper exists.

```bash
python3 scripts/aqara_open_api.py post_automation_execution_log '{"automation_ids":["automation_id_1"],"time_range":["2026-01-15 00:00:00","2026-01-15 23:59:59"]}'
```

- Empty records → **Must** say so. **Forbidden** fabricate fields.

## Failure

- **`unauthorized or insufficient permissions`:** **Must** `aqara-account-manage.md` → retry.
- Empty list → **Must** state clearly.
- API error → brief user-safe message; **Forbidden** raw stacks.
- Tool missing → **Must** say unsupported; fallback list or app.

## Response

- Conclusion first; factual.
- **Forbidden** script paths, shell, raw JSON; **`automation_id` allowed** if desensitized virtual ID.
- **Forbidden** invent names, counts, rooms, enabled state.
