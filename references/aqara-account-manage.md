# Account & session management

Flow: sign in → save token → fetch homes → multi-home selection.

**Switching homes** (distinct from re-login):

- If the user says “switch home”, “change home”, “use another home”, etc.: **do not** default to re-login. With a valid `aqara_api_key`, go straight to `references/home-space-manage.md` **step 0** (fetch homes) → if multiple homes, **step 1** (user picks index/name; write `home_id` / `home_name`); if one home, **step 2** (auto-write).
- **Only** when the user **explicitly** asks to re-login / rotate the token, or the API clearly returns **token invalid / unauthorized / auth failure**, run the login + save `aqara_api_key` flow below.
- **Clear signal**: any response with **`unauthorized or insufficient permissions`** (or equivalent unauthorized/insufficient-permission text) means auth/permission failure — **must** run this section’s login + save `aqara_api_key` flow; then `references/home-space-manage.md` to refresh homes and reselect `home_id` if needed, then resume the original query/control intent.

---

**1 Login prompt and links**

- **Never** put `client_secret` or other secrets into links, chat, or this repo; if the platform needs extra params, add them only server-side or in local secure config.
- **User-facing copy is not hardcoded in this doc.** Read **`assets/login_prompt_i18n.json`** and use the strings for **one** locale only (see **Locale choice** below). Output **`section_heading`**, **`instruction_paragraph`**, and **`link_label`** **verbatim** for that locale—do not translate or rephrase on the fly.
- **Locale choice**: Pick the JSON key under `locales` that matches the user’s language—use the language of the **current user message** when obvious, e.g. English → `en`, Chinese → `zh`, Japanese → `ja`, Korean → `ko`, German → `de`, Spanish → `es`, Russian → `ru`, Portuguese → `pt`, Arabic → `ar`; honor an explicit locale the user asked for; or align with the same `lang` convention as `references/home-space-manage.md` when you already inferred `lang` for API calls (map API/lang tags to the closest `supported_locales` entry). **Fallback (兜底)**: if unsure, ambiguous, or the resolved locale is not in `supported_locales`, always use **`en`** (English)—see `fallback_locale` / `default_locale` and `fallback_policy` in that JSON file. Only add new languages by extending `supported_locales` and `locales`.
- **Layout** (in order; **blank line between blocks**):
  1. One subtitle line: the chosen locale’s **`section_heading`** value (e.g. bold **`Login`** or **`登录`** as given in the file).
  2. One explanatory paragraph: the chosen locale’s **`instruction_paragraph`** exactly as in the file.
  3. **Link block (clickable + copyable)**: Then output in order:
     1. **Clickable**: one Markdown link line; bracket text = that locale’s **`link_label`** verbatim; URL = full configured `login_url` (from runtime / API path config, e.g. `https://agent.aqara.com/login`).
     2. **Copyable**: **blank line**, then **one line** with the **exact** bare `login_url` (no angle brackets, no backticks, no Markdown wrapping).
     **Do not** use `<https://...>`. If the client cannot render Markdown links, you may omit the first line but **must** keep the bare URL line; when Markdown works, show **both** lines—do not choose only one.
  4. Render a QR code for `login_url` **below** the bare URL line.

**2 After the user pastes `aqara_api_key` (agent/terminal only — not shown to user)**

- Run the save script automatically (for agent/terminal only; **do not** paste into user-visible replies):

 ```bash
python3 scripts/save_user_account.py aqara_api_key '<aqara_api_key>'
```

- **Split from the next step**: after the token save **finishes**, run **separately** `python3 scripts/aqara_open_api.py homes` from `references/home-space-manage.md` step **0**. **Do not** chain in one shell with `&&` (e.g. `save_user_account.py ... && aqara_open_api.py homes`). Use two independent commands/processes so `user_account.json` is flushed before listing homes.

**3 User-visible feedback after save**

- Short confirmation using the **same locale**’s **`token_saved_message`** from `assets/login_prompt_i18n.json` (verbatim); **do not** show exit codes, terminal JSON, bash, or `scripts/` paths.

**4 Immediately continue home/space flow (mandatory)**

- **Do not** follow token save with vague prompts like “send your home name” or “e.g. my home”.
- **Must** next run `references/home-space-manage.md`: **0** fetch homes → single home **2** auto-write (you may briefly name the default home in reply); multiple homes **1** list index + name once for user choice.

## Notes

- Do not verbalize internal step numbers to the user.
- User-visible text **must not** mention `assets/user_account.json` or “writing xxx.json”; after paste, say things like “Access token saved”.
- **Never show users**: terminal commands, `save_user_account.py`, script stdout/debug JSON, `references/` or repo paths, or technical details beyond the login flow.
- **Re-login / new token**: users only see the login link and “paste the new token”; **do not** explain whether an old `aqara_api_key`/`home_id` exists, overwrite behavior, or auto home re-selection (handle in the agent backend).
- **Switching homes**: do not assume token expiry from intent alone; fetch the home list first; re-login only on explicit auth failure or explicit user request.
