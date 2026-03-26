# Account and Session Management

**Overall flow**: sign in -> save `aqara_api_key` -> fetch home list -> select home.  
**Switch home**: when a valid `aqara_api_key` already exists, go directly to step `0` in `home-space-manage.md`; do not default to re-login.  
**Re-login**: only when the user explicitly requests it, or when the response contains `unauthorized or insufficient permissions` (or an equivalent auth error).

---

## 1) Login Guidance (User-facing)

### Must follow

- For the login URL, use only the top-level `default_login_url` in `assets/login_reply_prompt.json`; do not replace it with other "open platform" links.
- User-facing copy must come only from the current locale JSON fields, unchanged: `instruction_paragraph`, `qr_fallback_line` (and `api_key_saved_message`, which is used only after successful save).
- In `user_account.json`, the credential key name must be `aqara_api_key` only (do not use `access_token` / `accessToken`).

### Output order (within the same reply turn)

1. Output `instruction_paragraph`
2. Output a **single-line** login URL: `[default_login_url](default_login_url)`  
   - If Markdown links are unavailable, fall back to a single-line plain URL  
   - Do not repeat the same URL twice in the same turn
3. In the same turn, display `assets/login_qr.png` via image/file-read rendering (do not only write `![](...)`)
4. Output `qr_fallback_line` after one blank line
5. End the response here; do not append extra closings like "paste key / I will save it / then fetch homes"

> If `assets/login_qr.png` is missing: send only the single-line URL + `qr_fallback_line`, and restore the image file.  
> If `default_login_url` changes: regenerate `assets/login_qr.png` accordingly.

---

## 2) After User Pastes `aqara_api_key` (Internal execution)

```bash
python3 scripts/save_user_account.py aqara_api_key '<aqara_api_key>'
```

- Write only `aqara_api_key` into `user_account.json`
- After saving, run a **separate command invocation**:

```bash
python3 scripts/aqara_open_api.py homes
```

- Do not chain save + fetch in one line with `&&`; ensure config is written first

---

## 3) User Reply After Save

- Return only the current locale's `api_key_saved_message` (exact original text)
- Do not expose script paths, terminal output, raw JSON, or exit codes

---

## 4) Continue Home Flow (Required)

- Follow `home-space-manage.md`: first run step `0` to fetch the home list
- Single home: auto-write it (step `2`)
- Multiple homes: ask the user to choose in step `1`
- Do not reply with only "please send the home name"

---

## Notes

- Do not output internal step numbers, the `user_account.json` path, or script commands to the user
- Do not describe backend overwrite details (such as whether an old key was replaced)
- Switching home does not mean the token is expired: fetch home list first, then decide whether re-login is needed


## Logout
- If the user explicitly asks to log out of the Aqara account, provide this logout URL: `https://agent.aqara.com/logout`.