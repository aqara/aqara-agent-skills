# List scenes

Normative rules live in [`scene-manage.md`](../scene-manage.md) (intents, execution order). This file covers **catalog listing** and **scenes linked to devices** (`post_scene_detail_query`).

## Catalog list

Use **`get_home_scenes`** for the saved scene catalog in the current home.

```bash
python3 scripts/aqara_open_api.py get_home_scenes
```

## Scenes by device

Use **`post_scene_detail_query`** when the user cares which catalog scenes involve specific device endpoint(s).

1. **Must** resolve `device_ids` from `get_home_devices` (`devices-inquiry.md`).
2. **Must** POST body with `device_ids`; path `scene/detail/query`.

```bash
python3 scripts/aqara_open_api.py post_scene_detail_query '{"device_ids":["<endpoint_id>"]}'
```

```bash
python3 scripts/aqara_open_api.py post_scene_detail_query '{"device_ids":["<endpoint_id_1>","<endpoint_id_2>"]}'
```

- **Must** summarize only real response; **Forbidden** guess.
- **Forbidden** raw `scene_id`, `position_id` to user; empty or no usable rows: **Must** say so from API output only. If the user's goal is **running a catalog scene** and none match after `get_home_scenes`, follow **[Scene execute](execute.md)** step 5 (state **no matching scene** in the user's locale if needed, then auto **[Scene recommend workflow](recommend.md)** when scope is clear).

**Related:** [Scene execute](execute.md), [Scene name matching (shared)](../scene-manage.md#scene-name-matching-shared), [Execution log](execution-log.md), [`scene-manage.md`](../scene-manage.md).
