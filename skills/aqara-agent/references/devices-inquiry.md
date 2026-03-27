# Device Inquiry

## Execution Order (Strict)

### Step 1: Classify the Query Sub-Intent

Two buckets:

- `devices_detail`: room or whole-home device list, which room a device is in, device counts.
- `query_state`: live state (online/offline, temperature, humidity, switch state, etc.).
- If unclear, start as `devices_detail`, then clarify.

### Device Query Workflow

For mixed utterances like "Turn on the living room light and set AC to 26°C":

1. **Split the request**
   - Multiple devices/actions -> multiple sub-queries.
   - Each sub-query follows control or query flow as appropriate.
   - Example: "Bedroom light on, living room AC off" -> bedroom light first, then living room AC.
   - Mixed intents: split in semantic order; label each sub-query as query or control.
   - If a sub-query mixes **query + control**, query first, then control.

2. **Locate devices** from names or locations
   - Load home/room layout via `references/home-space-manage.md`.
   - From the user query, extract room name; run the script for base device info (includes device id, device name, position name):

   ```bash
   python3 scripts/aqara_open_api.py home_devices
   ```

   - Fuzzy-match by location, device name, type (e.g. "AC") against the `home_devices` response.

3. **Fetch state** only if the sub-intent is `query_state`; otherwise stop after the prior steps and answer from list/detail:
   - If multiple devices match, build `device_ids` from `endpoint_id` in the list.
   - Example status call:

   ```bash
   python3 scripts/aqara_open_api.py device_status '{"device_ids":["device_id_1", "device_id_2"]}'
   ```

4. **Shape the reply**
   - Conclusion first, then detail.
   - Lead with online/offline, room, key state values.
   - Optional detail: capabilities, how you matched (do **not** expose raw ids in user text).
   - Sort multi-device answers by room -> device name for stable output.
   - Do not surface raw ids (device id, position id) to the user.

## Disambiguation (Minimal)

Ask only when needed, **one** key question:

- Ambiguous device name: `I found several "main lights": living room vs master bedroom. Which one?`
- Room missing but needed: `Which room? Options: living room, bedroom, study.`

When nothing matches:

- Say there is no exact match
- Offer 2-5 close candidate names
- Give an example sentence they can reuse

## Failure & Fallback

Describe outcomes plainly - no raw error codes:

- No match: say so + 2-5 candidate names
- Recent layout changes: list may be stale - suggest re-running device list (`home_devices`) and retry
- Ambiguous: list conflicting devices; ask for room or full name
- Live state unavailable: say real-time read failed; fall back to cached info if you have it
- Query call failed: short reason, no internal leakage
- **`unauthorized or insufficient permissions`**: token invalid or insufficient permission - **do not** keep retrying business APIs with the old token; guide the user through `references/aqara-account-manage.md` to re-login, save new `aqara_api_key`, then refresh homes and devices.

## Output Templates

### Template A: Lists (`device_detail`)

- Conclusion: `Living room has 8 devices; 7 online: ...`
- Detail: lines like `name | type | room`.

### Template B: State (`device_status`)

- Conclusion: `Living room AC 24°C; bedroom AC 26°C.` (use units from API when present; keep user-facing wording consistent.)
- Detail: `name | metric | value | updated_at (if any)`.

### Template C: Failure / Missing Context

- Conclusion: `Query could not be completed.`
- Reason: `Context incomplete or live state temporarily unavailable.`
- Suggestion: `Retry after fixing home_id or try again later.`
