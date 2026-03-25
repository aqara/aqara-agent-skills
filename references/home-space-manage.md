# Home & space management

**When this applies (mandatory)**

- Right after `aqara_api_key` is saved (see `references/aqara-account-manage.md`), **automatically** run **step 0** here and continue **1 / 2**—**do not** open with vague “please send a home name”; only if there are **multiple** homes, use **1** to ask for index or name.
- When the user says **switch / change / another home**: again run **step 0** first (**no** re-login by default; exceptions in `references/aqara-account-manage.md`: user explicitly re-logins, or API says token invalid).

**0. Fetch homes / positions**

- Infer `lang` from user input when relevant, e.g. `zh`, `en`.
- **Recommended**: from **`skills/aqara-home-skills`**, run:

```bash
python3 scripts/aqara_open_api.py homes
```

- **After saving token**: if the previous step was `save_user_account.py aqara_api_key ...`, this command **must be a new, separate invocation**—**do not** chain with `&&` on the same line as the save script (see `references/aqara-account-manage.md` step **2**).

**1. Multiple homes** (when the script shows two or more homes)

- In chat, list homes for selection, e.g. **1-xxxx, 2-xxxx** (index + home name).
- Wait for the user’s choice (`1`, `2`, or a name string).
- Write the chosen **`home_id`** and **`home_name`** to **`assets/user_account.json`** via:

```bash
python3 scripts/save_user_account.py home  '<home_id>'  '<home_name>'
```

- That home becomes the default; you do not need to ask for home info every time.

**2. Single home**

- If there is only one home, write `home_id` and `home_name` straight into **`assets/user_account.json`**—no user choice needed.

**3. Room list** — With a selected home and valid `home_id` in `user_account.json`:

```bash
python3 scripts/aqara_open_api.py rooms
```
