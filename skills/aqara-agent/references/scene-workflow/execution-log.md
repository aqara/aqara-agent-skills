# Scene execution log

**Must** match scenes first per **[Scene name matching (shared)](../scene-manage.md#scene-name-matching-shared)** when resolving names to `scene_ids`; JSON per live API.

```bash
python3 scripts/aqara_open_api.py post_scene_execution_log '{"scene_ids":["scene_id_1","scene_id_2"],"time_range":["2026-01-15 00:00:00","2026-01-15 23:59:59"]}'
```

**Related:** [List scenes](list.md), [Scene execute](execute.md), [`scene-manage.md`](../scene-manage.md).
