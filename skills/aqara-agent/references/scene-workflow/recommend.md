# Scene recommend workflow (AI-recommended device states)

Situational **recommend** path: plan device actions and **execute now** with `post_device_control` (unless user chose **Create scene** / persist path). **Must** align with [`scene-manage.md`](../scene-manage.md).

## Device status control (`device_status_control`)

**Definition (skill pattern, not a single CLI symbol):** **`device_status_control`** is how **scene recommendation** (run the plan now) and **scene creation** (plan only, then persist) are realized:

1. **Status** - **Must** query current state with **`post_device_status`** (step 5) for all controllable targets in scope.
2. **Control** - **Must** apply commands with **`post_device_control`** when the user path is **immediate recommendation** (step 7 here), **or** **Must** encode the same logical actions into **`scene_data`** and call **`post_create_scene`** when the path is **Create scene** (persisted) (**Must not** run recommend step 7 `post_device_control` for that persist-only branch).

CLI: `python3 scripts/aqara_open_api.py post_device_status '...'` then `python3 scripts/aqara_open_api.py post_device_control '...'` per **`devices-control.md`** and **`assets/device_control_action_table.csv`**.

## Creative, room-aware configuration

When building the control plan (step 6) and when executing under **`device_status_control`** (step 7) or when filling **`scene_data`** for **Create scene**:

- **May** be **imaginative**: use the **actual room** (device mix, light types, scope from steps 1-2) and **common sense** to choose coherent settings for the situation (e.g. bedtime vs movie vs leaving home).
- **Must** actively consider **lighting and climate cues** where supported: **on/off**, **brightness**, **color**, **color_temperature** (and other attributes allowed by the CSV for each `device_type`), so the result **feels like** a real scene rather than a single generic toggle.
- **Must** still ground every command in **live `post_device_status`**, **CSV rows**, and **`devices-control.md`**; **Forbidden** unsupported attributes, **Forbidden** invent devices, **Forbidden** claim success without API truth.

<a id="unspecified-scene-time-anchor"></a>

## Unspecified scene name — time-anchored plan (mandatory for step 6)

Applies when the user asks to **recommend** a scene **without** naming a concrete situation or mood (e.g. generic “recommend a scene”, “suggest one scene”, or equivalent **without** tying the request to movie / sleep / leave home / morning / work / party / reading / guest visit, etc.).

1. **Must** anchor the step-6 situational intent to **current wall-clock** using the **authoritative `{now}`** (or equivalent) from the host / session — **Must** use the user’s **local timezone** when known (e.g. **Asia/Shanghai (北京时间)** for China-home contexts). **Forbidden** assume UTC or an unstated default timezone when the product or user context implies a home region.
2. **Must** derive **one** coherent situational plan from that time of day and execute **only** CSV-grounded controls. The bands below are **guidance**, not rigid API enums — adjust for culture, room mix, and step-5 state; **Must not** contradict `{now}` without an explicit user override:
   - **Late night** (illustrative: about **22:00–06:00** local) — **wind-down / pre-sleep** semantics: **low** brightness, **warm** `color_temperature` where supported, avoid whole-home “bright wake” patterns; curtains **May** favour privacy if consistent with user safety and device mix.
   - **Morning** — brighter, neutral-to-cool light where appropriate; gentle **wake / daytime start** semantics.
   - **Midday / afternoon** — moderate, activity-friendly lighting; **Must not** force dim **evening-only** defaults.
   - **Evening** (illustrative: roughly **17:00–21:30** local, adjustable) — warmer, softer **at-home evening** semantics; use this family **only** when `{now}` falls in such a band **or** the user implied evening / dinner / sunset mood.
3. **When the user names a situation explicitly** — **Must** follow that named intent for step 6; **May** use `{now}` only to refine parameters (e.g. slightly deeper dim after 23:00 for “bedroom relax”) but **Must not** replace the user’s named scene with an unrelated time-of-day default.

**Forbidden:** a **single fixed recipe** (e.g. always “evening cozy at home”) for **all** unspecified recommends **regardless of** `{now}` (e.g. **Must not** run a broad “evening return home” style plan at **23:54 北京时间** when the user only said “recommend a scene” and gave no evening wording).

## Scope - outdoor weather

**`post_current_outdoor_weather`** is **only** allowed inside **this** workflow, **only** in **step 7** when the **Leaving home** gate applies, **before** `post_device_control`. **Forbidden** call it for **Create scene**, **Scene snapshot**, **Scene execute** (catalog execute), **Execution log**, standalone device control, energy, automation, or any other skill path. **Normative API detail:** **[Outdoor weather](../weather-forecast.md)**.

## What "recommend" means

**Recommend** here means: the model derives `attribute` / `action` / `value` and target `device_ids` from the user's situational intent, then carries them out via **`device_status_control`** (status, then control or `scene_data`). The Open Platform has **no** API that returns a packaged "recommendation" - only device listing, status query, **`post_current_outdoor_weather`** (**only** as required by step 7 **Leaving home** below; see scope note above), and **`post_device_control`**. **Forbidden** suggest a dedicated recommend endpoint exists.

## When to use this workflow

**Path A (run catalog scene, no match)** - User intent is to **run** a saved scene; after `get_home_scenes` and resolved scope there is **no** match - **[Scene execute](execute.md)** **Must** state that no catalog scene matched, then **Must** **automatically** hand off into this section (**[Execution steps](#execution-steps)**) for the **same** situational intent - **Forbidden** wait for a separate user confirmation before recommendation. **Forbidden** `post_execute_scene` with invented `scene_ids`. If **location scope** was never settled in the prior **[Scene execute](execute.md)** branch, **Must** apply **[Location scope resolution](#location-scope-resolution-mandatory-before-steps-1-8)** below **before** steps 1-8.

**Path B (explicit create/recommend)** - User directly asks to **create** or **recommend** a situational scene (e.g. homecoming) - **Must** have **Location scope** resolved per **[Location scope resolution](#location-scope-resolution-mandatory-before-steps-1-8)** (same rules as **[Scene execute](execute.md)** step 3 when the user already named a room or **whole home** clearly; otherwise **Must** `get_rooms` and ask - **Forbidden** rely on "already clear under Scene execute" if that step was skipped). If the goal is **Create scene** (persisted scene card) - **Must** use **[Create scene](create.md)** (recommend steps 1-6 + `post_create_scene`). Otherwise - **Must** run this section (full steps 1-8). **Must not** require a catalog match first.

## Location scope resolution (mandatory before steps 1-8)

Applies to **every** entry into this workflow (Path A after consent, Path B, or any situational recommend). **Forbidden** plan, list devices for control, or call **`post_device_status`** / **`post_device_control`** until scope is explicit.

1. **When location is already explicit** - **May** proceed: user names a **single room** that maps to one `get_rooms` row, or unambiguous **whole home** wording (e.g. "whole home", "entire house", "everywhere", or equivalent in the user's language). **Must** align that choice with **`get_rooms`** + **`home-space-manage.md`** when resolving `position_id` / names for filtering.

2. **When location is missing or ambiguous** (no room, vague "here", multiple possible rooms, or unclear whether they mean one room vs whole home):
   - **Must** call `get_rooms` (see **`home-space-manage.md`**).

     ```bash
     python3 scripts/aqara_open_api.py get_rooms
     ```

   - **Must** show the user **all** scope options: **whole home** **plus** **each** room from the API (human-readable names from the response; **Forbidden** omit **whole home** from the list).
   - **Must** ask **one** clarification so the user **picks exactly one** option from that list (or replies with synonymous explicit scope).
   - **Forbidden** default to **whole home** or any room "by common sense", "by typical bedtime", or by model guess. **Forbidden** infer scope from device density or prior turns unless the user's **current** utterance explicitly fixes scope.

3. **After the user chooses** - **Must** treat **whole home** as: all endpoints from `get_home_devices` for the current home. **Must** treat **one room** as: keep only rows whose **position** matches the chosen room (name/id per **`home-space-manage.md`** and latest `get_rooms`). **Forbidden** plan controls outside that scope.

## Execution steps

1. **Device list** (current home) - **only after [Location scope resolution](#location-scope-resolution-mandatory-before-steps-1-8)**
   `python3 scripts/aqara_open_api.py get_home_devices`

2. **Filter by location** (strictly per user-chosen scope from Location scope resolution)
   - **Whole home**: all endpoints returned for the home (per API shape).
   - **One room**: keep only endpoints in that room; align names/ids with `get_rooms` (**`home-space-manage.md`**). **Forbidden** include devices from other rooms when the user chose a single room.

3. **Controllable candidates**
   From step 2, **drop** endpoints whose `device_type` matches **either** rule:
   - **Sensor suffix:** string ends with `Sensor` (PascalCase, e.g. `MotionSensor`, `TemperatureSensor`).
   - **Other non-controllable types** (match API strings exactly; types already covered by `*Sensor` are not listed again):
     `AttitudeDetector`, `Camera`, `Computer`, `Cube`, `Doorbell`, `Speaker`, `Fan`, `Hub`, `IRDevice`, `Kettle`, `Microwave`, `Other`, `Outlet`, `Panel`, `PetFeeder`, `Projector`, `Refrigerator`, `SmartBed`, `SmartToilet`, `SweepingRobot`, `TV`, `VoiceMate`, `Water Heater`

4. **Empty after filter**
   State clearly there is no controllable device in scope; **Forbidden** invent `post_device_control`.

5. **Live status (`device_status_control` - status leg)**
   For remaining `endpoint_id`s (**`devices-inquiry.md`**):
   `python3 scripts/aqara_open_api.py post_device_status '{"device_ids":["<id1>","<id2>"]}'`
   Chunk if batch limits apply.

6. **Control plan (LLM)**
   Read **`assets/device_control_action_table.csv`** and **`devices-control.md`** (`device_type` / `Any` / slash rules). Map situational intent to `attribute` / `action` / `value` **only** for rows in the CSV with supported capability, using step 5 state. Apply **[Creative, room-aware configuration](#creative-room-aware-configuration)** so the plan uses varied, plausible lighting and related attributes where the room and devices allow. **When the user did not name a concrete scene or situation**, **Must** apply **[Unspecified scene name — time-anchored plan](#unspecified-scene-time-anchor)** so the chosen mood matches **local `{now}`** (e.g. late-night wind-down vs evening at home). **Forbidden** skip this step or fabricate "recommend API" results.

7. **Execute (`device_status_control` - control leg)**

   **Leaving home - before any control**
   Applies **only** in **Scene recommend workflow** (situational recommend), not in **Create scene** or any other business. When step-6 situational intent matches **leaving home** (e.g. **Leaving home scene** from **[Common family scene names](appendices.md#common-family-scene-names)**, or natural phrases such as heading out, leaving home, nobody home, off to work):

   1. **Must** call **`post_current_outdoor_weather`** **before** the first **`post_device_control`**, following **[weather-forecast.md](../weather-forecast.md)** (CLI, request body, **`time_range`** = [now, now + 5 minutes] for this step, user-facing summary rules).

   2. **Must** **immediately** give the user a short summary of **current outdoor weather** from **only** that API response (**Must** not defer until after control). **Forbidden** invent conditions. If the call fails or returns no usable data - **Must** say so briefly; **May** still proceed with control if the user's intent remains device actions.

   3. **Must** then run **`post_device_control`** as planned (same step 7 success rules).

   **All other situational intents** - Call **`post_device_control`** with real `device_ids`; **may** call multiple times (groups or steps). Execution **May** be **rich and layered** (multiple attributes per device where allowed), consistent with **[Creative, room-aware configuration](#creative-room-aware-configuration)**. Success per actual API responses (**`SKILL.md`** ground truth).

8. **User-facing reply**
   **Must** lead with outcome (**conclusion first**). After **`post_device_control`** (and any step-7 weather summary when applicable), **Must** briefly list **which devices were actually acted on** and **how each was controlled** - use **human-readable** names from the latest `get_home_devices` / status pass (**position** + **endpoint name** or **device name** as shown to users), and describe each action in plain language (or compact `attribute` / `action` / `value` wording when it aids clarity). **When step 6 used [Unspecified scene name — time-anchored plan](#unspecified-scene-time-anchor)** (generic recommend with no named scene), **Must** state in **one short phrase** the **time-based theme** actually applied (e.g. local late-night wind-down vs morning bright-up) so the user sees why this recipe was chosen. **Must** align this list **only** with steps that **succeeded** per API; **Must** note any partial failure the same way. **Forbidden** dump raw `endpoint_id` / `device_ids`, shell transcripts, or full JSON. **Forbidden** claim devices or actions that were not in the executed plan or successful responses.

## Errors and user-facing (this workflow)

- **`unauthorized or insufficient permissions`:** **`aqara-account-manage.md`** (re-login) then retry.
- Partial failures: report per API output only.
- Same as rest of this reference: **Forbidden** fabricate success; **Forbidden** expose internal id detail to users.

**Related:** [Scene execute](execute.md), [Create scene](create.md), [`scene-manage.md`](../scene-manage.md).
