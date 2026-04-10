# Home & Space Management

## When This Applies

- After `aqara_api_key` save (`aqara-account-manage.md`): **Must** run **step 0** immediately, then **1** or **2**. **Forbidden** open with vague "send home name" only; **Must** use step **1** only when **multiple** homes.
- User says switch/change/another home: **Must** step **0** first. **Forbidden** default re-login (exceptions: user demands re-login or API auth failure  -  `aqara-account-manage.md`).

### Step 0: Fetch Homes

- Infer `lang` when relevant (`zh`, `en`, ...).
- **Must** run from skill root:

```bash
python3 scripts/aqara_open_api.py get_homes
```

- After `save_user_account.py ...`: **Must** new shell invocation for `get_homes`; **Forbidden** `&&` on same line as save (`aqara-account-manage.md` step 2).

### Step 1: Multiple Homes

- **Must** list `1 - name, 2 - name`, wait for index or name.
- **Must** persist choice:

```bash
python3 scripts/save_user_account.py home '<home_id>' '<home_name>'
```

### Step 2: Single Home

- **Must** write `home_id` / `home_name` to `user_account.json` without asking.

### Step 3: Rooms

With valid `home_id`:

```bash
python3 scripts/aqara_open_api.py get_rooms
```

## Switch Home vs Re-Login

- Switch/another home + valid key: **Must** step **0** -> **1** or **2** here; **Forbidden** jump to login.
- Re-login: **Must** only if user explicitly re-logins/rotates token or API returns invalid/unauthorized  -  then `aqara-account-manage.md`.
- **`unauthorized or insufficient permissions`** (or equivalent): **Must** treat as auth failure -> login flow in `aqara-account-manage.md` -> refresh homes here -> re-select `home_id` if needed -> continue original intent.
