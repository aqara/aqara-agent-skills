# Create scene

Use when the user **explicitly** intends to **create** a **saved scene** in Aqara (e.g. "help me create a scene", "create a good-night scene in the bedroom", "create a new movie-watching scene"). **Forbidden** use this path for **run existing catalog scene**, **scene snapshot**, or **only** ephemeral **`post_device_control`** without persist intent. **Forbidden** **`post_current_outdoor_weather`** here - that call is **only** for **[Scene recommend workflow](recommend.md)**, leaving-home step 7 (see **[weather-forecast.md](../weather-forecast.md)**).

Implement the **plan** with the same **`device_status_control`** pattern as **[Device status control (`device_status_control`)](recommend.md#device-status-control-device_status_control)**: **`post_device_status`** through step 6, then **`scene_data`** + **`post_create_scene`** instead of recommend step 7 **`post_device_control`**.

**Must** follow [`scene-manage.md`](../scene-manage.md) for session and cross-intent rules.

## Prerequisite

- Valid `aqara_api_key` + `home_id` (`aqara-account-manage.md`, `home-space-manage.md`).

## Location and room choice (mandatory before planning)

Align with **[Scene recommend workflow - Location scope resolution](recommend.md#location-scope-resolution-mandatory-before-steps-1-8)** on **no silent defaults** and **listing options from live API**, with this **API constraint**: **`post_create_scene` requires exactly one `position_id` (one room)**. There is **no** whole-home `position_id`.

1. **When the user already names one room** that maps to a single row in the latest **`get_rooms`** output - **May** set **`position_id`** after confirming against **`home-space-manage.md`**. Apply the same **closest room name** rule as **[Scene snapshot](snapshot.md)** when names collide (e.g. "Bedroom" vs "Bedroom 1"). **Forbidden** substitute another room by guess.

2. **When the user does not name a room** or scope is ambiguous (no place, vague "here", unclear which bedroom, or only situational words like "good night" without "in ..."):
   - **Must** call **`get_rooms`** (if not already done in workflow step 1).

     ```bash
     python3 scripts/aqara_open_api.py get_rooms
     ```

   - **Must** show the user **all** scope options: **whole home** **plus** **each** room from the API (human-readable names; **Forbidden** omit **whole home** from the list).
   - **Must** ask **one** clarification so the user picks **exactly one** listed option (or synonymous explicit wording).
   - **Forbidden** default **any** room or **whole home** by common sense, "typical" bedtime room, device count, or prior turns unless the user's **current** utterance fixes the room.

3. **Interpreting "whole home" for Create scene** - If the user picks **whole home**, **Must** explain briefly that a **saved** scene card is stored under **one room** in Aqara Home and **`scene_data` devices must belong to that room** for this API call. **Must** ask **one** follow-up clarification: **which single room** should own the scene (**list room names again** from **`get_rooms`**). **Forbidden** pick that room for them. After they name one room, **Must** set **`position_id`** to that room and **Must** filter **`get_home_devices`** to **only** that room for planning and **`scene_data`**.

4. **Interpreting a single-room choice** - **Must** set **`position_id`** to that room. **Must** filter **`get_home_devices`** to **only** endpoints in that room (match **`position name` / `position id`** per **`home-space-manage.md`**). **Forbidden** include devices from other rooms in the plan or in **`scene_data`**.

5. **Forbidden** call **`get_home_devices`** for planning, **`post_device_status`**, **`post_create_scene`**, or build **`scene_data`** until **`position_id`** is fixed per above.

## Execution pace and user interaction

Except for **room / position** and **scene name**, which **May** require user questions or confirmation, all other steps **Must** run **end-to-end** in **[Workflow](#workflow)** order (fetch devices, query status, plan, build `scene_data`, call `post_create_scene`, reply from real results). **Forbidden** interrupt the user repeatedly on substeps for extra confirmation.

- **May** ask the user for input or confirmation **only** for: (1) **`position_id` not yet fixed** - follow **[Location and room choice](#location-and-room-choice-mandatory-before-planning)**, list options, and clarify **once** until the user picks a single room (including after **whole home**, then the owning room); (2) **`scene_name` missing or unusable** - per workflow step 3, **once** prompt or suggest until a non-empty name is confirmed.
- **Forbidden** after **`position_id`** and **`scene_name`** are satisfied, keep asking step-by-step ("proceed?", "include this device type?", "approve this plan?"); planning, assembling **`scene_data`**, and calling **`post_create_scene`** **Must** run back-to-back without that friction.
- If the API fails (including invalid parameters or unsupported capability), **Must** state the outcome or error from the **actual** response in the final reply; **Forbidden** stall after successful reads waiting for verbal approval instead of issuing the create call.


## Workflow

1. **Preload home + rooms** - **Must** have **home display name** and **all room names** in context before clarifying or planning: use `home_name` from `user_account.json` (after home selection) and/or `get_homes` as needed, and **Must** call:

   ```bash
   python3 scripts/aqara_open_api.py get_rooms
   ```

   Use this list for **position** labels and ids (internal resolution only).

2. **`position_id` (scene location)** - **Required**, **one room** (this API uses a single room id). **Must** satisfy **[Location and room choice (mandatory before planning)](#location-and-room-choice-mandatory-before-planning)**; **Forbidden** call `post_create_scene` until **`position_id`** is set.

3. **`scene_name`** - **Required**, non-empty. **Must** take it from the user when they name the scene (e.g. "Good night scene"). If they **do not** provide a scene name - **Must** prompt using **[Common family scene names](appendices.md#common-family-scene-names)** as suggestions and/or **one** short question so the chosen name is non-empty before the API call.

4. **Plan device states (reuse Scene recommend workflow steps 1-6 only)** - For the **chosen room only** (`position_id`), this is the **`device_status_control`** planning half: status via **`post_device_status`**, plan via step 6 (**Must not** run **`post_device_control`** here). See **[Scene recommend workflow - Execution steps](recommend.md#execution-steps)** steps 1-6 **with execution step 2 interpreted as that single room only** (not whole-home device list), and **[Creative, room-aware configuration](recommend.md#creative-room-aware-configuration)** for step 6.
   **Must not** run **step 7** (`post_device_control`) or **step 8** of that workflow for this intent.

5. **Build `scene_data`** - From the step-6 plan (same logical actions as **`device_status_control`** would apply, but serialized for persist), assemble the payload the API expects: a **list** of blocks, each:

   | Field | Rule |
   | --- | --- |
   | `device_ids` | **Required**, non-empty list of endpoint ids. If the user **did not** name specific devices in the conversation, **Must** set `device_ids` to **all** device endpoint ids under the chosen `position_id` (from the **room-filtered** list used in workflow step 4, before or after the controllable-type filter - **Must** match live `post_create_scene` contract; if the platform rejects non-controllable types, restrict to the same controllable set as **[Scene recommend workflow - Execution steps](recommend.md#execution-steps)** step 3). If the user named devices, **Must** use only those resolved ids. |
   | `slots` | **Required** (may be empty list only if API allows; prefer at least one slot when there is a real plan). Each slot: `attribute`, `action`, `value`. |

   **Slot semantics (normative CSV):** **Must** choose **`attribute`**, **`action`**, and **`value`** per device type using **[`assets/device_control_action_table.csv`](../../assets/device_control_action_table.csv)** (`device_type`, `attribute`, comma-separated **`action`** list, `value_range`). Match each planned device to its **device type** (from status / catalog), then emit slots only from rows that apply to that type. **Forbidden** invent attribute-action pairs or values outside the CSV (and live `post_device_status` / API constraints).

   - **`attribute` / `action`:** Use CSV columns **`attribute`** and allowed **`action`** tokens for that row (e.g. Light `brightness`: `up`, `query`, `down`, `set`). Where the CSV lists multiple rows for the same attribute (e.g. `wind_speed`), pick the row whose actions fit the plan.
   - **`value`:** **Must** stay within **`value_range`** for that row (numeric bands, enums like `low_speed` / `max` / `empty`, or documented aliases). Lighting-effect-style names **May** apply when the plan uses **`lighting_effect`**; **`action`** for that attribute **Must** be **`set`** (see [JSON body](#json-body-post_create_scene)).
   - If **`action`** is omitted in the plan, **Must** use **`set`** wherever the CSV allows **`set`** for that attribute (see same section).

   **Special rules (still apply on top of CSV):**
   **`color`** - **`value`** **Must** be **English lowercase** per CSV palette (e.g. `red`). **Must** normalize string `value` to trimmed lowercase before building the CLI JSON; **Must** map localized color words to English tokens in the plan.

6. **`post_create_scene`** - **Must** call with **`scene_name`**, **`position_id`**, **`scene_data`**. On success, the response includes **`scene_id`** for **scene card** presentation - **May** surface that id to the user when the product shows a scene card (**exception** to generic "no raw ids" guidance for this success path only, if your client requires it).

   ```bash
   python3 scripts/aqara_open_api.py post_create_scene '{
     "scene_name": "Good night scene",
     "position_id": "<room_position_id_from_get_rooms>",
     "scene_data": [
       {
         "device_ids": ["<endpoint_id_1>", "<endpoint_id_2>"],
         "slots": [
           {"attribute": "on_off", "action": "on", "value": ""},
           {"attribute": "brightness", "action": "set", "value": "80"},
           {"attribute": "color", "action": "set", "value": "red"},
           {"attribute": "color_temperature", "action": "set", "value": "warm"}
         ]
       },
       {
         "device_ids": ["<endpoint_id_3>", "<endpoint_id_4>"],
         "slots": [
           {"attribute": "on_off", "action": "off", "value": ""},
           {"attribute": "temperature", "action": "set", "value": "26"}
         ]
       }
     ]
   }'
   ```

7. **Reply** - **Must** summarize from real API output only; **Forbidden** fabricate success. On auth errors - **`aqara-account-manage.md`** then retry.

## JSON body (`post_create_scene`)

`aqara_open_api.py` **`post_create_scene`** sends the JSON body **unchanged** to **`scene/create`**. **Must** shape the payload correctly before the call; invalid bodies surface as API errors.

### Top-level

| Field | Type | Rule |
| --- | --- | --- |
| `scene_name` | string | **Required**, non-empty after trim. |
| `position_id` | string | **Required**, non-empty after trim; **one** room id from **`get_rooms`** (see [Location and room choice](#location-and-room-choice-mandatory-before-planning)). |
| `scene_data` | array | **Required**, non-empty. Each element is one **block** (object). |

### Each `scene_data` block

| Field | Type | Rule |
| --- | --- | --- |
| `device_ids` | array of strings | **Required**, non-empty; every element a non-empty endpoint id string (trim whitespace). |
| `slots` | array | **Required**; each element a **slot** object. Prefer non-empty when there is a real plan (empty only if the platform documents it). |

### Each slot object

| Field | Type | Rule |
| --- | --- | --- |
| `attribute` | string | Per **[`device_control_action_table.csv`](../../assets/device_control_action_table.csv)** for the device type. |
| `action` | string | Per CSV allowed actions for that row. If omitted when assembling the payload: use **`set`** for `attribute` **`lighting_effect`**; otherwise use **`set`** only where the CSV allows **`set`** for that attribute. |
| `value` | string / number / etc. | Per CSV **`value_range`**. For `attribute` **`color`** with a string `value`, **Must** be trimmed **English lowercase** (e.g. `red`). |

## Errors

- Same as **Scene recommend workflow**: **Forbidden** invent devices or capabilities; **Must** follow **`unauthorized or insufficient permissions`** re-login flow.

**Related:** [Scene recommend workflow](recommend.md), [Scene snapshot](snapshot.md), [`scene-manage.md`](../scene-manage.md).
