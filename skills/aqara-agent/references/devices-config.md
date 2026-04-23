# Device Configuration

## Scope (Binding)

**Device configuration** means **home-administration style** operations on a device (firmware / OTA, and future config surfaces), **not** day-to-day `attribute` / `action` / `value` control.

## Firmware-only scope

**Firmware / OTA only:** **Upgrade execution** maps to `post_device_firmware_upgrade` / `device/firmware/upgrade`. **Pre-upgrade firmware read** (current version, latest version, online/offline gate) **Must** use `post_device_firmware_query` / `device/firmware/query` per [Workflow](#workflow) step **3** (and `post_device_status` when needed for online only).

**Forbidden:** treat device configuration as **device rename**, **move room or position**, or **any non-firmware device record edit** — **Must** not route those intents here. **Must** direct users to **Aqara Home app** for rename, reposition, and other settings.

| Category | User intent examples | Procedure | API (this skill) |
| --- | --- | --- | --- |
| **Device query** | How many lights; is the hub online; current temperature; show logs; **firmware version / update info (read-only)** | `devices-inquiry.md` | `get_home_devices`, `post_device_status`, optional `post_device_base_info`, `post_device_log`, **`post_device_firmware_query`** (`device_firmware_inquiry`) |
| **Device control** | Turn on, dim to 30%, set AC to 26° | `devices-control.md` + **`assets/device_control_action_table.csv`** | `post_device_control` |
| **Device configuration** | Upgrade firmware, OTA, update device software | This file | `post_device_firmware_query` (pre-upgrade gate) **then** `post_device_firmware_upgrade` |

**Must** route **firmware / OTA upgrade** / "upgrade firmware" / "flash device" (consumer) **execution** to this doc — **Forbidden** map upgrade to `post_device_control` or to the action table. Read-only firmware version / update availability query stays **`devices-inquiry.md`** (**`device_firmware_inquiry`** / `post_device_firmware_query`).

**Must** route **read-only firmware version / "is there new firmware" / OTA availability** questions (no upgrade requested) to `devices-inquiry.md` sub-intent **`device_firmware_inquiry`** → `post_device_firmware_query`. When the user asks to **start** an upgrade, **Must** follow **this** file’s Workflow (including **mandatory** pre-upgrade `post_device_firmware_query` in step **3** before `post_device_firmware_upgrade`). Other read-only version / online / capability questions may use `post_device_base_info` / `post_device_status` per `devices-inquiry.md`.

**Mixed utterance** (e.g. “list my hubs then upgrade the living room one”): **Must** split; **Must** list/locate (`devices-inquiry.md`) before upgrade, in semantic order.

## Goal

**Must** resolve upgrade targets: either **concrete device(s)** via `get_home_devices` (room, name, `device_type`, disambiguation when needed), or a **batch scope** via the same optional body lists as status query (`device_ids` / `position_ids` / `device_types`). **Must** user-facing: outcome first; **Forbidden** raw `endpoint_id` / position ids in user text.

<a id="workflow"></a>

## Workflow

1. **Home gate:** `home-space-manage.md` — valid `home_id` / position context.
2. **Scope:** `get_home_devices` (+ `get_rooms` when using rooms). Named single device → fuzzy match; multi-match → one disambiguation question. **Batch / broad scope:** build the JSON body with **one or more** of the lists below (same idea as `post_device_status` in `devices-inquiry.md`); **`device_ids` may be omitted** when `position_ids` and/or `device_types` define the set — **Must** still resolve `position_ids` from APIs, not unchecked natural-language room strings as ids.

3. **Firmware info gate (before upgrade):** **Must** call **`post_device_firmware_query`** on the **same scope** as the planned upgrade (reuse the same `device_ids` / `position_ids` / `device_types` lists where applicable — see `devices-inquiry.md` **`device_firmware_inquiry`**). **Must** summarize from **real** response only:

   - **Current firmware version** (tenant field names as returned).
   - **Latest available firmware version** (or tenant-equivalent “new firmware” indicator).
   - **Online / offline** for each target: use fields from the firmware query response when present; if the response does not expose connectivity, **Must** call **`post_device_status`** on the same scope (`devices-inquiry.md`) to determine online/offline before upgrading.

   **Offline rule:** **Forbidden** send **`post_device_firmware_upgrade`** for devices that are **offline**; **Must** state that offline targets **do not support** firmware upgrade in this flow, list which targets are skipped (by human-readable name/room, no raw ids), and **Must** only proceed with **online** targets (or **Must** abort the whole upgrade request if **all** targets are offline / none eligible — **Forbidden** imply upgrade ran).

   **Already-up-to-date (optional gate):** if the API clearly indicates no newer firmware for an online target, **May** skip upgrade for that target after a short user-facing explanation; **Must** not claim an upgrade completed without **`post_device_firmware_upgrade`** success when nothing was sent.

   **CLI (same placeholders as upgrade body):**

```bash
python3 scripts/aqara_open_api.py post_device_firmware_query '{"device_ids":["device_id_1","device_id_2"]}'
```

4. **Body:** JSON for `device/firmware/upgrade` **per live Open Platform** (field names may differ by tenant). When the platform matches the device-status pattern, use:

   | Field | Required | Meaning |
   | --- | --- | --- |
   | `device_ids` | No | Endpoint / device ids from `get_home_devices`. Omit or `[]` when using room/type filters. |
   | `position_ids` | No | Room ids from `get_rooms` / `home-space-manage.md`. **Forbidden** use unchecked NL room names as JSON ids. |
   | `device_types` | No | Type filters; align with `device_type` from `get_home_devices` (see `devices-inquiry.md` for token examples). |

   **Broad batch (e.g. whole-room or whole-type OTA):** **Allowed:** one short scope confirmation (count / room / types) before sending — **Forbidden** imply upgrade completed without API success.

5. **Invoke** (placeholders = real ids from APIs; extend body per tenant if required; **only after** step 3 passes for intended targets):

```bash
python3 scripts/aqara_open_api.py post_device_firmware_upgrade '{"device_ids":["device_id_1","device_id_2"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_firmware_upgrade '{"position_ids":["position_id_1","position_id_2"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_firmware_upgrade '{"device_types":["Light","AirConditioner"]}'
```

```bash
python3 scripts/aqara_open_api.py post_device_firmware_upgrade '{"position_ids":["<living_room_position_id>"],"device_types":["Light"]}'
```

   **NL → resolution (agents):** e.g. “upgrade firmware for the bedroom lights” → `position_ids` from `get_rooms` for bedroom + `device_types` `["Light"]`; “OTA all ACs” → `device_types` `["AirConditioner"]`; “update these two hubs” → explicit `device_ids` after list match. Combine lists only if the tenant API accepts it.

   **Forbidden** CLI method aliases — **Must** match `SKILL.md` ground list. **Must** not invent success; **Must** follow **actual** API response.

6. **Reply:** success/failure from response only; on auth errors **Must** `aqara-account-manage.md` (same as `devices-control.md`). **Must** reflect what step 3 showed (versions / online) when relevant; **Forbidden** omit that the user asked for upgrade but only offline targets existed.

## Failure

- **Unsupported device / capability:** **Must** say unsupported; **Forbidden** imply upgrade started.
- **Offline target(s):** **Must** not send upgrade for those endpoints; **Must** explain offline devices do not support upgrade in this flow (see Workflow step 3).
- **Firmware query failed / empty:** **Must** not proceed to upgrade on blind scope; **Must** brief reason + retry or re-list devices.
- **`unauthorized or insufficient permissions`:** **Must** re-login per `aqara-account-manage.md`; **Forbidden** claim upgrade succeeded.
- **Stale layout:** **Must** re-run `get_home_devices` and retry locate.

## Future

Additional configuration flows (e.g. network setup, advanced device options) **Must** be listed in this file and on `AqaraOpenAPI` + `SKILL.md` ground list before use.
