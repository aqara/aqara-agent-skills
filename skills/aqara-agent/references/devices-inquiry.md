# Device Inquiry

## Step 1: Sub-Intent

- **`devices_detail`:** list/count, which room, device inventory.
- **`query_state`:** live attributes (online, temp, humidity, switch, ...).
- **`device_firmware_inquiry`:** read-only **firmware version / update availability** (what version, is there new firmware) — **Must** use [Firmware version query](#firmware-version-query-device_firmware_inquiry) with `post_device_firmware_query`, not `devices-config.md` until the user asks to **start** an upgrade.
- Unclear -> start `devices_detail`, then clarify.

**Not inquiry (upgrade):** if the user wants to **perform** a **firmware / OTA upgrade** (not only ask “what version”), **Must** route to `references/devices-config.md` after any needed list/locate.

## Workflow

**Mixed utterance** (e.g. query + control, query + firmware upgrade): **Must** split sub-requests; semantic order; **Must** run inquiry (list/locate/state/firmware query) before control **or** before device configuration (`devices-config.md`) when both appear in one sub-request.

1. **Locate:** `home-space-manage.md` for layout; then:

```bash
python3 scripts/aqara_open_api.py get_home_devices
```

   Fuzzy-match room, name, **`device_type`** (table below) on `home_devices`.

2. **`query_state`:** call `post_device_status` with a JSON body. Use **one or more** optional filters (all lists); **`device_ids` may be empty/omitted** when other filters narrow scope — avoids resolving every endpoint by hand when you want a **batch status** query.

   **Body fields (Open Platform; align with live tenant if keys differ):**

   | Field | Required | Meaning |
   | --- | --- | --- |
   | `device_ids` | No | Endpoint / device ids from `get_home_devices` (`endpoint_id` → id in list). Omit or `[]` when using room/type filters. |
   | `position_ids` | No | Room (position) ids — **Must** resolve from `get_rooms` / `home-space-manage.md`; **Forbidden** use unchecked natural-language room names as JSON ids. |
   | `device_types` | No | Type filters; values should match how `device_type` appears in `get_home_devices` (often PascalCase substring tokens), e.g. `Light`, `AirConditioner`, `Switch`, `Outlet`, `WindowCovering`, `ClotheDryingMachine`, `Camera`, `Speaker`, `BathroomHeater`, `TemperatureSensor`, `HumiditySensor`, `DoorSensor`, `MotionSensor`, `SweepingRobot`, `VideoDoorbell`, `PetFeeder`. |

   **CLI examples (placeholders are real ids from APIs):**

```bash
python3 scripts/aqara_open_api.py post_device_status '{"device_ids":["device_id_1","device_id_2"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_status '{"position_ids":["position_id_1","position_id_2"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_status '{"device_types":["Light","AirConditioner"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_status '{"position_ids":["<living_room_position_id>"],"device_types":["Light"]}'
```

   **NL → resolution (agents; not raw JSON for end users):** map utterance to filters after layout is known — e.g. “are the living room lights on?” → `position_ids` = living room’s id from `get_rooms`, `device_types` = `["Light"]`; “status of all ACs” → `device_types` = `["AirConditioner"]`; “bedroom temperature?” → bedroom `position_ids` + `["TemperatureSensor"]` (or the tenant’s thermometer `device_type`). Combine filters only when the API accepts it for your tenant.

   Else stop after list/detail for `devices_detail`.

<a id="firmware-version-query-device_firmware_inquiry"></a>

3. **`device_firmware_inquiry`:** after locate when needed, call `post_device_firmware_query` with a JSON body. **Same batching idea as** `post_device_status` **and** `post_device_firmware_upgrade`: use **one or more** of the three optional lists; **`device_ids` may be omitted or `[]`** when `position_ids` and/or `device_types` define the scope. **Must** resolve `position_ids` from `get_rooms` / `home-space-manage.md`; **Forbidden** use unchecked natural-language room names as JSON ids. **`device_types`** values align with `device_type` from `get_home_devices` (see table below).

   **Body fields (Open Platform; align with live tenant if keys differ):**

   | Field | Required | Meaning |
   | --- | --- | --- |
   | `device_ids` | No | Endpoint / device ids from `get_home_devices` (`endpoint_id` → id in list). Omit or `[]` when using room/type filters. |
   | `position_ids` | No | Room (position) ids — **Must** resolve from `get_rooms` / `home-space-manage.md`; **Forbidden** use unchecked natural-language room names as JSON ids. |
   | `device_types` | No | Type filters; values should match how `device_type` appears in `get_home_devices` (often PascalCase), e.g. `Light`, `AirConditioner`, `Camera`, `Switch` (same token set as status query). |

   **CLI examples (placeholders = real ids from APIs):**

```bash
python3 scripts/aqara_open_api.py post_device_firmware_query '{"device_ids":["device_id_1","device_id_2"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_firmware_query '{"position_ids":["position_id_1","position_id_2"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_firmware_query '{"device_types":["Light","AirConditioner"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_firmware_query '{"position_ids":["<living_room_position_id>"],"device_types":["Light"]}'
```

   **NL → resolution (agents; not raw JSON for end users):** e.g. “hub firmware version?” → resolve hub row(s) → `device_ids`; “any new firmware for bedroom lights?” → bedroom `position_ids` + `device_types` `["Light"]`; “OTA status for all cameras” → `device_types` `["Camera"]`. Combine lists only when the tenant API accepts it.

   **Forbidden** treat this path as starting an upgrade — **Must** `devices-config.md` + `post_device_firmware_upgrade` only after the user clearly asks to upgrade.

4. **Reply:** conclusion first; online/offline, room, key values (and firmware fields when applicable); sort room -> name; **Forbidden** raw device/position ids in user text.

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

Extend when new families appear. After resolve: **control** -> `devices-control.md`; **firmware version read** -> **`device_firmware_inquiry`** / `post_device_firmware_query` (this file); **firmware / OTA upgrade** -> `devices-config.md`.

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
- **`device_firmware_inquiry`:** conclusion (version / update summary per device or scope); detail from API fields only; **Forbidden** invent rows not in `post_device_firmware_query` response.
- **Failure:** short reason; **Forbidden** invent data.

## Opening Ratio (Logs / History)

| Value | Meaning |
| --- | --- |
| 0% or 1% | Closed |
| 100% | Open |
| Other | Partial; report number if user wants precision |
