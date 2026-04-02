# Scene Management

## Intents

- List/discover scenes.
- Scenes involving a device (“which scenes use Light 1?”).
- Run scene.
- Execution history / log.

## Execution Order

1. **Session:** **Must** `aqara_api_key` + `home_id` (`aqara-account-manage.md`, `home-space-manage.md`).
2. **Must** list (`get_home_scenes`) before run; **Must** match run target against latest list.
3. Multi-intent: utterance order; query + execute → **Must** query first.
4. Device → scenes: **Must** `get_home_devices` → `device_ids` → `post_scene_detail_query`; **Forbidden** invent/paste ids without list step.
5. **Forbidden** create/edit/delete scenes here → **Must** direct to **Aqara Home app**.

## List Scenes

```bash
python3 scripts/aqara_open_api.py get_home_scenes
```

## Scenes by Device (`post_scene_detail_query`)

1. **Must** resolve `device_ids` from `get_home_devices` (`devices-inquiry.md`).
2. **Must** POST body with `device_ids`; path `scene/detail/query`.

```bash
python3 scripts/aqara_open_api.py post_scene_detail_query '{"device_ids":["<endpoint_id>"]}'
```

```bash
python3 scripts/aqara_open_api.py post_scene_detail_query '{"device_ids":["<endpoint_id_1>","<endpoint_id_2>"]}'
```

- **Must** summarize only real response; **Forbidden** guess.
- **Forbidden** raw `scene_id`, `position_id` to user; no match → 2–5 candidate names + one confirm question.

## Run Scene

**Must** match name + room vs `get_home_scenes`, then:

```bash
python3 scripts/aqara_open_api.py post_execute_scene '{"scene_ids":["scene_id_1","scene_id_2"]}'
```

- **Must** one unambiguous target unless user wants several.
- Collisions → **Must** one clarification; **Forbidden** guess and execute.

## Execution Log

**Must** match scenes first; JSON per live API:

```bash
python3 scripts/aqara_open_api.py post_scene_execution_log '{"scene_ids":["scene_id_1","scene_id_2"],"time_range":["2026-01-15 00:00:00","2026-01-15 23:59:59"]}'
```

## Failure

- **`unauthorized or insufficient permissions`:** **Must** `aqara-account-manage.md` → retry.
- No match: **Must** say so + candidates from last `get_home_scenes`.
- **Forbidden** claim success if call failed.

## Response

- Short; conclusion first.
- **Forbidden** script paths, shell, raw JSON, internal ids to user.
- **Must** only observed API/script output.
