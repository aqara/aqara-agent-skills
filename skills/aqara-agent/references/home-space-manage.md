# Home & Space Management

## When This Applies (Mandatory)

- Right after `aqara_api_key` is saved (see `references/aqara-account-manage.md`), **automatically** run **step 0** here and continue **1 / 2** - **do not** open with vague "please send a home name"; only if there are **multiple** homes, use **1** to ask for index or name.
- When the user says **switch / change / another home**: again run **step 0** first (**no** re-login by default; exceptions in `references/aqara-account-manage.md`: user explicitly re-logins, or API says token invalid).

### Step 0: Fetch Homes / Positions

- Infer `lang` from user input when relevant, e.g. `zh`, `en`.
- **Recommended**: from **`skills/aqara-agent`**, run:

```bash
python3 scripts/aqara_open_api.py homes
```

- **After saving token**: if the previous step was `save_user_account.py aqara_api_key ...`, this command **must be a new, separate invocation** - **do not** chain with `&&` on the same line as the save script (see `references/aqara-account-manage.md` step **2**).

### Step 1: Multiple Homes (When the Script Shows Two or More Homes)

- In chat, list homes for selection, e.g. **1 - xxxx, 2 - xxxx** (index + home name).
- Wait for the user's choice (`1`, `2`, or a name string).
- Write the chosen **`home_id`** and **`home_name`** to **`assets/user_account.json`** via:

```bash
python3 scripts/save_user_account.py home '<home_id>' '<home_name>'
```

- That home becomes the default; you do not need to ask for home info every time.

### Step 2: Single Home

- If there is only one home, write `home_id` and `home_name` straight into **`assets/user_account.json`** - no user choice needed.

### Step 3: Room List

With a selected home and valid `home_id` in `user_account.json`:

```bash
python3 scripts/aqara_open_api.py rooms
```

## Notes: Switching Home vs Re-Login

**Switching home** is not the same as **re-login**:

- If the user says they want to switch home, use another home, or similar: **do not** default to re-login. When a valid `aqara_api_key` is already present, go straight to **step 0** in this file (fetch homes). If there are multiple homes, **step 1** (user picks by index or name; write `home_id` / `home_name`). If there is only one home, **step 2** (auto-write).
- **Only** if the user **explicitly** asks to re-login or rotate the token, or the API clearly returns token invalid / unauthorized / auth failure, follow the flow to log in and save `aqara_api_key` in `references/aqara-account-manage.md`.
- **Strong signal**: if any response contains **`unauthorized or insufficient permissions`** (or an equivalent unauthorized / insufficient-permission message), treat it as auth failure - **you must** run the log-in-and-save-`aqara_api_key` flow there; then refresh homes per this file and re-select `home_id` if needed, then continue the original query or control intent.
