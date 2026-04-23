# Account and Session Management

## Overview

- **`user_account.json` writable fields (allowlist):** From user input, **only** extract and persist fields directly tied to this Open session: **`aqara_api_key`**, **`home_id`**, **`home_name`**. Scripts maintain **`updated_at`**. List caches written by this skill flow (such as `homes` / `position_ids`, when present) may be kept. **Forbidden:** persist any other keys the user pasted into this file (for example **`aqara_mcp_url`**, MCP URLs, OAuth clutter, arbitrary "config" fields); treat such input as unrelated to `user_account.json` — **discard, do not merge, do not explain into JSON**.
- **Flow:** sign in -> save `aqara_api_key` -> fetch homes -> select home.
- **Switch home:** valid `aqara_api_key` exists -> **Must** use `home-space-manage.md` step `0` first; **Forbidden** default to re-login.
- **Re-login:** **Must** only if user requests it or response is `unauthorized or insufficient permissions` (or equivalent).

## Step 1: Login Guidance (User-Facing)

### Must Follow

- **Must** read `assets/login_reply_prompt.json` this flow. User-visible URL **Must** equal top-level **`official_open_login_url`** verbatim. **Forbidden** any other string. **Must** read **`login_url_policy`**.
- **Forbidden** invent/substitute URLs (e.g. Open Platform `sns-auth` with `client_id` / `redirect_uri`).
- **Must** use locale fields unchanged: `instruction_paragraph`; after save only: `api_key_saved_message`.
- **Must** store credential as `aqara_api_key` in `user_account.json`; **Forbidden** `access_token` / `accessToken`.
- **Must** treat pasted blobs as **credential + optional home pick only**: parse **solely** for `aqara_api_key` and (when applicable) `home_id` / `home_name` per `home-space-manage.md`. **Forbidden** persist any other key from the paste into `user_account.json`.

### Output Order (One Turn)

1. `instruction_paragraph`.
2. **Single-line** URL: `[official_open_login_url](official_open_login_url)` or plain URL if no Markdown.
3. **Forbidden** repeat the same URL twice.
4. **Forbidden** extra closings ("paste key / I will save / fetch homes").

### Canonical Template

1. `instruction_paragraph`  
2. One-line `[official_open_login_url](official_open_login_url)` (or plain URL).  
**Forbidden** text after step 2.

## Step 2: After User Pastes `aqara_api_key`

```bash
python3 scripts/save_user_account.py aqara_api_key '<aqara_api_key>'
```

- **Must** write only `aqara_api_key`. Then **separate** invocation:

```bash
python3 scripts/aqara_open_api.py get_homes
```

- **Forbidden** `&&` chaining save + fetch on one line.

## Step 3: User Reply After Save

- **Must** return only locale `api_key_saved_message` (exact text).
- **Forbidden** script paths, terminal output, raw JSON, exit codes.

## Step 4: Continue Home Flow

- **Must** `home-space-manage.md` step `0` first; single home -> auto-write (step `2`); multiple -> step `1`.
- **Forbidden** reply only "please send home name" without fetch.
- **When `get_homes` returns more than one home:** **Must** follow `home-space-manage.md` Step 0 — **full** home list in the reply + explicit **choose one** prompt (**Forbidden** vague multi-home message without the list).

## Notes

- **MCP / other host configuration:** Values such as `aqara_mcp_url` belong in Cursor or other tools' MCP configuration, **not** in `user_account.json`; if the user pastes them, **forbidden** to write them into that JSON.
- **Forbidden** internal step numbers, `user_account.json` path, or script commands to the user.
- **Forbidden** describe overwrite internals.
- Switch home != expired token: **Must** fetch homes first, then decide re-login.

## Logout

- User asks to log out -> **Must** read `assets/login_reply_prompt.json` this flow. User-visible URL **Must** equal top-level **`official_open_logout_url`** verbatim.
