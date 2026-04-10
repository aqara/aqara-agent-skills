# Toggle (`post_automation_switch`)

1. **Must** `get_home_automations` -> resolve by name + room.
2. **Must** map user intent to enable/disable.
3. **Must** send switch; reply from real output only.
4. **Forbidden** toggle if ambiguous.

```bash
python3 scripts/aqara_open_api.py post_automation_switch '{"automation_ids":["automation_id_1"],"switch":"off"}'
```

```bash
python3 scripts/aqara_open_api.py post_automation_switch '{"automation_ids":["automation_id_1"],"operation":"on"}'
```

(Adjust keys to live API.) **`automation_id` allowed** in user text when server returns desensitized virtual IDs. If switch missing in wrapper -> **Must** say unsupported + suggest app.

**Related:** [List](list.md), [`automation-manage.md`](../automation-manage.md).
