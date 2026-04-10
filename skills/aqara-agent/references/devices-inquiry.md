# Device Inquiry

## Step 1: Sub-Intent

- **`devices_detail`:** list/count, which room, device inventory.
- **`query_state`:** live attributes (online, temp, humidity, switch, ...).
- Unclear -> start `devices_detail`, then clarify.

## Workflow

**Mixed utterance** (e.g. query + control): **Must** split sub-requests; semantic order; **Must** query before control when both appear in one sub-request.

1. **Locate:** `home-space-manage.md` for layout; then:

```bash
python3 scripts/aqara_open_api.py get_home_devices
```

   Fuzzy-match room, name, **`device_type`** (table below) on `home_devices`.

2. **`query_state` only:** build `device_ids` from `endpoint_id`; then:

```bash
python3 scripts/aqara_open_api.py post_device_status '{"device_ids":["device_id_1", "device_id_2"]}'
```

   Else stop after list/detail for `devices_detail`.

3. **Reply:** conclusion first; online/offline, room, key values; sort room -> name; **Forbidden** raw device/position ids in user text.

## Device Type -> Category (Substring on `device_type`)

**Rule:** category match when `device_type` **contains** substring (API casing, usually PascalCase).

| `device_type` contains | EN examples | Extra fuzzy hints (localized speech) |
| --- | --- | --- |
| `Light` | lights, lamps | light, lamp, bulb, fixture |
| `AirConditioner` | AC, air conditioner | cooling, heating, HVAC |
| `WindowCovering` | curtains, shades | blind, drape, shutter |
| `ClotheDryingMachine` | drying rack | laundry rack, clothes dryer (rack) |
| `SweepingRobot` | robot vacuum | floor robot, vacuum bot |
| `Speaker` | smart speaker | audio, sound bar |
| `Camera` | camera (video) | cam, security camera |
| `VideoDoorbell` | doorbell | video door, chime |
| `PetFeeder` | pet feeder | animal feeder |

Extend when new families appear. **Control** after resolve -> `devices-control.md`.

## Optional: `post_device_base_info`, `post_device_log`

Same `home_id` gate. **Must** resolve `device_ids` from `get_home_devices` unless tenant allows otherwise.

```bash
python3 scripts/aqara_open_api.py post_device_base_info '{"device_ids":["<endpoint_id>"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_log '{"device_ids":["<endpoint_id>"]}'
```

Bodies follow live Open API.

## Disambiguation

- **Must** <= one key question when needed (name clash, missing room).
- No match: **Must** say so + 2-5 candidate names + example phrasing.

## Failure

- **Forbidden** raw error codes to user.
- No match -> state + candidates. Stale layout -> **Must** re-run `get_home_devices` and retry.
- Ambiguous -> list conflicts; one question (room or full name).
- Live state failed -> say so; cached only if actually held.
- **`unauthorized or insufficient permissions`:** **Forbidden** retry business APIs with old token; **Must** `aqara-account-manage.md` re-login -> refresh homes/devices.

## Output Templates

- **List:** conclusion (counts/online); detail `name | type | room`.
- **State:** conclusion (headline metrics); detail `name | metric | value | updated_at`.
- **Failure:** short reason; **Forbidden** invent data.

## Opening Ratio (Logs / History)

| Value | Meaning |
| --- | --- |
| 0% or 1% | Closed |
| 100% | Open |
| Other | Partial; report number if user wants precision |
