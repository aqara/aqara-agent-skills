# Account and Session Management

## Overview

- **Overall flow**: sign in -> save `aqara_api_key` -> fetch home list -> select home.
- **Switch home**: when a valid `aqara_api_key` already exists, go directly to step `0` in `home-space-manage.md`; do not default to re-login.
- **Re-login**: only when the user explicitly requests it, or when the response contains `unauthorized or insufficient permissions` (or an equivalent auth error).

## Step 1: Login Guidance (User-facing)

### Must Follow

- For the login URL, use only the top-level `default_login_url` in `assets/login_reply_prompt.json`; do not replace it with other "open platform" links.
- User-facing copy must come only from the current locale JSON fields, unchanged: `instruction_paragraph`, `qr_fallback_line` (and `api_key_saved_message`, which is used only after successful save).
- In `user_account.json`, the credential key name must be `aqara_api_key` only (do not use `access_token` / `accessToken`).

### Output Order (Within the Same Reply Turn)

**Primary path is always the link**; the QR image is optional convenience when the file exists and the client can render it.

1. Output `instruction_paragraph`.
2. Output a **single-line** login URL: `[default_login_url](default_login_url)`.
   - If Markdown links are unavailable, fall back to a single-line plain URL.
   - Do not repeat the same URL twice in the same turn.
3. **Optional — QR:** If `assets/login_qr.png` exists and you can show an image to the user (e.g. file-read / attachment rendering), you may display it after the URL. If the file is missing, image rendering fails, or the environment cannot show binaries, **omit the QR**; login is still complete via the link alone.
4. Output `qr_fallback_line` after one blank line (it reinforces that the link is sufficient).
5. End the response here; do not append extra closings like "paste key / I will save it / then fetch homes".

> If `default_login_url` changes: update `assets/login_qr.png` when you want to keep scan-and-open aligned with the link; until then, rely on the link only.

### Canonical Login Reply Template (Copy and Reuse)

Use this structure every time login starts:

1. `instruction_paragraph`
2. One-line URL: `[default_login_url](default_login_url)` (or plain URL if Markdown link is unavailable).
3. *(Optional)* Show `assets/login_qr.png` only when available and displayable; otherwise skip.
4. Blank line.
5. `qr_fallback_line`

Do not add any extra sentence after step 5.

## Step 2: After User Pastes `aqara_api_key` (Internal Execution)

```bash
python3 scripts/save_user_account.py aqara_api_key '<aqara_api_key>'
```

- Write only `aqara_api_key` into `user_account.json`.
- After saving, run a **separate command invocation**:

```bash
python3 scripts/aqara_open_api.py homes
```

- Do not chain save + fetch in one line with `&&`; ensure config is written first.

## Step 3: User Reply After Save

- Return only the current locale's `api_key_saved_message` (exact original text).
- Do not expose script paths, terminal output, raw JSON, or exit codes.

## Step 4: Continue Home Flow (Required)

- Follow `home-space-manage.md`: first run step `0` to fetch the home list.
- Single home: auto-write it (step `2`).
- Multiple homes: ask the user to choose in step `1`.
- Do not reply with only "please send the home name".

## Notes

- Do not output internal step numbers, the `user_account.json` path, or script commands to the user.
- Do not describe backend overwrite details (such as whether an old key was replaced).
- Switching home does not mean the token is expired: fetch home list first, then decide whether re-login is needed.

## Logout

- If the user explicitly asks to log out of the Aqara account, provide this logout URL: `https://agent.aqara.com/logout`.
