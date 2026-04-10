# Automation flows: failure and user-facing response

Use with [`automation-manage.md`](../automation-manage.md) and the specific workflow file you run.

## Failure

- **`unauthorized or insufficient permissions`:** **Must** `aqara-account-manage.md` -> retry.
- Empty list -> **Must** state clearly.
- API error -> brief user-safe message; **Forbidden** raw stacks.
- Tool missing -> **Must** say unsupported; fallback list or app.

## Response

- Conclusion first; factual.
- **Forbidden** script paths, shell, raw JSON; **`automation_id` allowed** if desensitized virtual ID.
- **Forbidden** invent names, counts, rooms, enabled state.

**Related:** [List](list.md), [Toggle](toggle.md).
