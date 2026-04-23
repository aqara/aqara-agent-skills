# List automations

**Must** follow [`automation-manage.md`](../automation-manage.md) for session, execution order, and cross-domain rules. This file covers **listing the automation catalog** and **automations linked to devices** (`post_device_related_automation_query`).

## Catalog list

Use **`get_home_automations`** for automations in the current home.

```bash
python3 scripts/aqara_open_api.py get_home_automations
```

Related methods: `post_device_related_automation_query`, `post_automation_switch`, `post_automation_execution_log` (see sibling files in this folder).

- Reply: conclusion then detail; stable order room -> name when possible.
- No exact name -> 2-5 candidates + one question.

## List by device

Use **`post_device_related_automation_query`** when the user cares which automations involve specific device endpoint(s).

1. **Must** resolve `device_ids` from `get_home_devices` (`devices-inquiry.md`).
2. Path `automation/detail/query`.

```bash
python3 scripts/aqara_open_api.py post_device_related_automation_query '{"device_ids":["<endpoint_id>"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_related_automation_query '{"device_ids":["<endpoint_id_1>","<endpoint_id_2>"]}'
```

**Related:** [Toggle](toggle.md), [Execution log](execution-log.md), [`automation-manage.md`](../automation-manage.md).
