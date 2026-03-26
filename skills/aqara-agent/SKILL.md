---
name: aqara-agent
description: "aqara-agent is an official AI Agent skill built on Aqara Home. It supports natural-language login/session setup, home-space management, device inquiry, device control, and scene management (list and execute scenes). Examples: \"How many lights are at home?\", \"Turn off the living room AC\", \"What's the temperature and humidity in the bedroom?\", \"Run Movie scene\"."
---

# Aqara Smart Home AI Agent Skill

## Basics
- **Aqara Open Host (default)**: `agent.aqara.com` (override via `AQARA_OPEN_HOST`)
- **Skill root**: `skills/aqara-agent/` (in-repo skill)
- **Python wrapper** for the Aqara Open API: `scripts/aqara_open_api.py` — calls the API surface directly.


## Core workflow

High-level order: **deps → sign-in → pick home → intent → follow `references/*.md` and summarize**.

## Ground truth: no fabricated smart-home data

Large models may **hallucinate** plausible homes, rooms, devices, states, or counts. For this skill, that is **explicitly forbidden**:

- **Sources of truth only**: Homes, rooms, device names/IDs (for internal use), capabilities, live attributes (temperature, brightness, switch state, online/offline, etc.), lists, counts, logs, and control outcomes **must** come **only** from executed skill scripts and real Aqara API responses—or from user-supplied input the skill is designed to accept (e.g. pasted `aqara_api_key`). If the corresponding inquiry or control flow **has not** been run successfully, **do not** present any of that information as factual.
- **Never invent or “plausible-fill”**: Example or demo-style device/home lists; guessed room layouts; assumed device counts; synthetic attribute values; fabricated success after errors, timeouts, skipped steps, or missing auth; JSON or prose that mimics API output without a real response.
- **When data is missing**: State clearly that it could not be retrieved (and why, e.g. not signed in, API error), then follow auth/retry/`references/`—**never** substitute imagined content to make the answer feel complete.

Align with **usage** and **core workflow** above; implement in order:

1. **Environment**

- Set environment host first (single-switch for test/prod):

```bash
export AQARA_OPEN_HOST=agent.aqara.com
```

- Install dependencies before use:

```bash
cd skills/aqara-agent
pip install -r scripts/requirements.txt
```

2. **Auth** — Before any feature, verify Aqara account auth and ensure **`user_account.json` is readable/writable** (project rules may require reading it first). Follow **`references/aqara-account-manage.md`** for switch-home vs re-login, token save, and **§1** login layout. Locale strings and **`default_login_url`** live in **`assets/login_reply_prompt.json`**—match the user’s language; **fallback** to **`en`** when unknown (`fallback_locale` / `default_locale` in that file). Login URL / QR / “stop after `qr_fallback_line`” rules: see **Canonical login** above.

`user_account.json` shape:

```json
{
  "aqara_api_key": "",
  "updated_at": "",
  "home_id": "",
  "home_name": ""
}
```S

3. **Home management**
- After `aqara_api_key` is saved, **automatically** follow `references/home-space-manage.md` to fetch the home list and finalize selection: run that doc’s **step 0** **immediately**; if there is a single home, write it; if multiple, ask the user to pick by index/name. **Do not** end with only “please reply with a home name” without running the fetch.
- When the agent/terminal runs scripts: `save_user_account.py` (write token) and `aqara_open_api.py homes` (fetch homes) **must be two separate runs** — **do not** chain with `&&` in one shell line; see `references/aqara-account-manage.md` step **2** and `references/home-space-manage.md` step **0**.
- **Switching homes**: by default **only** re-fetch the home list and let the user choose (see `references/home-space-manage.md`); **do not** default to re-login. **Only** if the user clearly asks to re-login/rotate the token, or the API indicates an expired/unauthorized token, follow `references/aqara-account-manage.md` for login.

4. **Intent**
- Space / device query / device control; for multiple intents **query first, then control**, following clause order in the utterance.

| Intent | Capability | Reference |
|--------|------------|-----------|
| Space | List all homes; list rooms in a home | `references/home-space-manage.md` |
| Device query | Filter by home/room; device details (incl. current attributes) | `references/devices-inquiry.md` |
| Device control | Control hardware in the home | `references/devices-control.md` |
| Scene | List and execute scenes | `references/scene-manage.md` |

5. **Route** to the matching `references/` doc, execute, and summarize.
- Summarize from real outcomes only; **never fabricate success** or any **homes, rooms, devices, attributes, counts, or states** that are not grounded in **actual** script/API output (see **Ground truth: no fabricated smart-home data** above).

**Wrapper shape (illustrative)** — CLI scripts may print JSON with `call_tool` output under `result` for troubleshooting (fields as actually returned):

```json
{
  "tool_name": "device_status_inquiry",
  "headers": { "position_id": "..." },
  "params": { "device_ids": ["..."] },
  "result": {}
}
```

**On bad params or JSON parse errors (illustrative)**:

```json
{
  "ok": false,
  "error": "..."
}
```

### Error handling

| Situation | Action |
|-----------|--------|
| Device not found | Say no match for “X”; optionally list a few candidate names |
| Capability not supported | State the unsupported action/attribute; do not pretend success |
| Home/room not found | Say no hit; suggest checking the home or re-fetching space/device lists per `references/` |
| Multiple devices match | List matches; ask the user to pick room or full name (one question at a time) |
| Not signed in / no `aqara_api_key` | Guide login and saving `aqara_api_key`, then continue with home fetch |
| No home selected | Clarify proactively; point to space-management flow |
| Invalid `aqara_api_key` or auth failure | Ask to re-login or refresh the token (no sensitive leakage). On **home switch**, only treat as auth failure if the home list call fails with an auth-class error—do not require login just because the user said “switch home”. **If the platform returns `unauthorized or insufficient permissions` (or equivalent), always follow `references/aqara-account-manage.md` to re-login and save the token; never fake query/control success** |
| Control path unavailable | Say the device was located but the command could not be sent |
| Other | Short, understandable summary + retry or check `references/`; do not expose internal URLs or full request headers |
| Indeterminate | Use `references/` and script output; if it’s a skill bug, file an issue in the skill repo |
| Risk of empty/missing API output | **Do not** invent homes, rooms, devices, or readings to fill the gap; re-run the correct flow or explain the failure—see **Ground truth: no fabricated smart-home data** |

## Notes

1. Do not expose raw IDs in user-facing replies (device id, position id, home_id, …).
2. Default **query before control** for multiple intents in one utterance.
3. After adding/moving devices or rooms, if matching fails, re-fetch space and device lists via `references/home-space-manage.md` and `devices-inquiry.md`, then retry.
4. User-visible replies: **conclusion first, then detail**; **one** key clarification question at a time.
5. **Session gate first**: if not signed in, the “conclusion” should guide setup—not pretend devices were controlled.
6. When `scripts/*.py` must run, **execute automatically**; details follow **mandatory script execution policy** (if defined elsewhere).
7. After switching account or home, update `user_account.json` and re-run the relevant steps in [`aqara-account-manage.md`](references/aqara-account-manage.md).
8. Do not echo tokens or full headers; treat `user_account.json` and caches as sensitive.
9. Device name matching is often fuzzy; ask the user to confirm when multiple hits exist.
10. In user-visible replies, **do not** print shell commands, script paths, raw stdout (incl. debug JSON), or `references/` filenames; the agent runs scripts; summarize in plain language.
11. When control APIs return success, keep the closing brief (result + essentials only); **do not** add hedging like “if some lights didn’t turn on, tell me”—troubleshoot only when the user reports an issue.
12. **Anti-hallucination**: Treat **Ground truth: no fabricated smart-home data** as binding for every turn; any user-visible home/room/device/state detail must trace to a real run of this skill’s tooling, not to model imagination or general knowledge of “typical” smart homes.
13. Never invent homes, rooms, devices, scenes, or states: only report data from executed scripts/API responses."

## Out of scope

The skill **does not** support:
- **Video / cameras** — live view, playback
- **Door locks** — unlock, lock/unlock smart locks (security-sensitive)
- **Automations** — list or create automations
- **Energy** — power usage / billing
- **Weather** — forecasts

If asked, say clearly that the skill cannot do it and suggest the Aqara Home app.
