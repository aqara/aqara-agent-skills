# Scene flows: failure and user-facing response

Use together with [`scene-manage.md`](../scene-manage.md) and the specific workflow file you are executing.

## Failure

- **`unauthorized or insufficient permissions`:** **Must** `aqara-account-manage.md` - retry.
- No catalog match after **execute** workflow: **Must** tell the user no matching catalog scene was found (phrase in the user's locale as needed), then **Must** automatically continue per **[Scene execute](execute.md)** step 5 into **[Scene recommend workflow](recommend.md)** when location scope is resolved - **Forbidden** require a separate user **yes** before starting that recommendation.
- **Forbidden** claim success if call failed.

## Response

- Short; conclusion first.
- **Forbidden** script paths, shell, raw JSON, internal ids to user.
- **Must** only observed API/script output.

**Related:** [Scene execute](execute.md), [Scene recommend workflow](recommend.md), [`scene-manage.md`](../scene-manage.md).
