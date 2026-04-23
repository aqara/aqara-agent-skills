# Home & Space Management

## When This Applies

- After `aqara_api_key` save (`aqara-account-manage.md`): **Must** run **step 0** immediately, then **1** or **2**. **Forbidden** open with vague "send home name" only; **Must** use step **1** only when **multiple** homes — and **Must** show the **entire** fetched list plus a **choose one** prompt before waiting for the user's pick.
- User says switch/change/another home: **Must** step **0** first. **Forbidden** default re-login (exceptions: user demands re-login or API auth failure  -  `aqara-account-manage.md`).

### Step 0: Fetch Homes

- Infer `lang` when relevant (`zh`, `en`, ...).
- **Must** run from skill root:

```bash
python3 scripts/aqara_open_api.py get_homes
```

- After `save_user_account.py ...`: **Must** new shell invocation for `get_homes`; **Forbidden** `&&` on same line as save (`aqara-account-manage.md` step 2).
- **After a successful homes query (multiple homes):** **Must** in the **same user-facing reply** present the **full** home list — **every** home as its own readable row (at minimum **home_name** and **home_id**; numbered `1. …`, `2. …` is recommended). **Must** add an explicit reminder that the user **must choose one** home (by number, name, or id). **Forbidden** only saying "there are multiple homes" / "please send a home name" without showing the complete list; **Forbidden** truncating or hiding ids when the user still needs them to disambiguate.

### Step 1: Multiple Homes

- **Must** keep the same requirement as Step 0: user sees **all** homes before choosing; **Must** accept selection by index, name, or `home_id` (then run `save_user_account.py home` as below). If the list was already shown in the immediately prior turn, **May** repeat the full list once for clarity when the user returns after a long gap.
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
