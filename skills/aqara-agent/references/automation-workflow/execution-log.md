# Automation execution log

1. Resolve targets from `get_home_automations`.
2. Valid JSON time window.
3. Call if wrapper exists.

```bash
python3 scripts/aqara_open_api.py post_automation_execution_log '{"automation_ids":["automation_id_1"],"time_range":["2026-01-15 00:00:00","2026-01-15 23:59:59"]}'
```

- Empty records -> **Must** say so. **Forbidden** fabricate fields.

**Related:** [List](list.md), [`automation-manage.md`](../automation-manage.md).
