# Scene Management

## Trigger Intents

- Scene query: e.g. "What scenes do I have at home?" or "List Home/Away modes."
- Scene execution: e.g. "Run Home mode" or "Turn on Movie scene."

## Execution Order

1. First confirm session gate: `aqara_api_key` and `home_id` are ready (see `references/aqara-account-manage.md` and `references/home-space-manage.md`).
2. Query scenes first, then execute scenes (even if the user directly asks to execute, do matching confirmation first).
3. For multi-intent input, process in semantic order; in the same sentence, `query + execute` should query first, then execute.

## Scene Query

Query scenes for the current home (the response usually includes `scene_id`, `scene_name`, and `position_name`):

```bash
python3 scripts/aqara_open_api.py home_scenes
```

When replying to the user:

- Put conclusion first, then details.
- Do not expose raw IDs such as `scene_id`.
- If no scene matches, provide 2-5 closest names for user confirmation.

## Scene Execution

Match the target scene from `home_scenes` results by "name + room" before execution:

```bash
python3 scripts/aqara_open_api.py execute_scenes '{"scene_ids":["scene_id_1", "scene_id_2"]}'
```

Notes:

- Be cautious even when multiple scenes are supported; by default, execute only one most certain match at a time.
- If there are duplicate names or multiple matches, ask one clarification question first (one question only); do not guess and execute.

## Failure and Fallback

- `unauthorized or insufficient permissions`: treat as auth failure; route to `references/aqara-account-manage.md` to re-login and update `aqara_api_key`, then retry.
- Scene does not exist / matching failed: clearly state no match and provide candidate names.
- For any failure, never fabricate an "execution succeeded" result.

## Response Guidelines

- Conclusion first, concise and clear.
- Do not output script paths, commands, raw JSON, or internal IDs.
- Reply only based on real script/API results; do not fill in imagined data.
