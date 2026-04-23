# Recommend automation

This document is the **only** normative spec for **recommend automation -> example create sentences -> formal create** (single file, end-to-end). It sits alongside [`../automation-manage.md`](../automation-manage.md) (list / detail / toggle / logs / **direct** create when the user already has an executable rule sentence). **Forbidden** to paste the body of list or toggle procedures from the same directory (**`list.md` / `toggle.md`**, etc.) into this file; use [`../automation-manage.md`](../automation-manage.md) and those subdocs instead.

When the user needs **situational help** (e.g. "Recommend a bedtime automation") but has **not** yet given one concrete create-ready rule sentence: **after** scope (position and/or device) is resolved per **§0–§1**, generate **example create sentences** from **real home data** including **`post_device_status`**; after the user picks or rewrites one, continue with [`../automation-create.md`](../automation-create.md) Steps 01-03 and **`post_create_automation`**.

**Forbidden** to call **`post_automation_recommend_query`**; **forbidden** to show the user platform "recommended template name" strings as a data source. **Must** satisfy [`../../SKILL.md`](../../SKILL.md) Ground truth (scripts + real API output only).

**Recommendation style (default):** Unless the user explicitly asks for advanced or multi-step rules, **recommended example sentences Must stay easy to read and easy to create**: prefer **one** clear **trigger** (one condition intent, e.g. a single schedule, a single sensor edge/threshold, or a single voice/device event) and **one** clear **outcome** (one action intent, e.g. turn one light group, run one named scene, open/close one curtain to one target). **Forbidden** in the default **§5.2** list: stacking unrelated triggers (e.g. **time +** separate **sensor state** in the same sentence), long chains of multiple device actions, or “do several things at once” prose. If richer ideas are useful, **split** them into **separate numbered examples** (each still one trigger → one outcome) rather than one compound sentence. **Anti-pattern (do not emit as a single recommended line):** "Every weekday at 8:30 a.m., and when the door/window sensor is closed, open the master bedroom curtain (Zigbee curtain motor) to about 50%." — **too complex** for the default recommend list; prefer e.g. only a time trigger **or** only a door/window condition, each in its own example. Details: **§4**.

---

## When to use this document

- The user wants **situational recommendation help** and has **not** yet supplied one complete rule sentence that can go straight to Step 01.

---

## Relation to the automation index

- **Session, home, `home_id`, and scene vs automation:** Still follow execution order and cross-domain rules in [`../automation-manage.md`](../automation-manage.md). List / toggle / logs flows **do not** use this document.
- **Formal create:** Only [`../automation-create.md`](../automation-create.md) and [`../automation-create-workflow/`](../automation-create-workflow/) carry that path.

---

## Close-out procedure (steps 0-5)

### 0. Session and scope

- **Validate** `aqara_api_key` and `home_id`; if invalid, finish account and home selection first ([`../aqara-account-manage.md`](../aqara-account-manage.md), [`../home-space-manage.md`](../home-space-manage.md)).
- **Position vs device in the user utterance (normative gate before §1):**
  - **Position** means: the user names or clearly selects a **room** (or equivalent **position** row from **`get_rooms`**) **or** an explicit **whole-home** scope (e.g. whole home / the home-level row when **`get_rooms`** returns one alongside rooms — **Must** map only to rows returned by **`get_rooms`**, not guessed names).
  - **Device** means: the user names at least one **concrete** device (or endpoint) **or** a **specific enough** device reference that **`get_home_devices`** can resolve **without** inventing a room (if cross-room ambiguous, **Must** disambiguate per bullet below — that still counts as “device specified” for the follow-up turn).
  - **Neither** a **position** **nor** a **device** can be resolved from the request: **Must** run **`get_rooms`** (see [`../home-space-manage.md`](../home-space-manage.md) Step 3). **Must** reply with a **single** purpose for that turn: ask the user to **choose one position**, and **Must** list **every** human-readable **position name** from the result (and include a **whole-home** choice in that list **only when** the API returns a row that represents it, e.g. a home-level name row — **Forbidden** inventing a pseudo-room). **Forbidden** in the same turn: **`get_home_devices`**, **`get_home_scenes`**, **`post_device_status`**, or the §5.2 **numbered `1`–`10` examples** block. **Forbidden** silently using whole-home device retrieval to draft examples when the user gave neither scope nor device.
  - **Position specified** (including whole home when it is a listed scope): proceed to **§1**; **Must** filter **`get_home_devices`** / scene rows to that scope (whole home → all rows under the current `home_id` inventory, or the union of positions per live table semantics — **Must** stay consistent with API rows, not prose defaults).
  - **Device specified** without a room: **Must** resolve from **`get_home_devices`**; if multiple matches across rooms, **Must** stop after a **short** disambiguation prompt (human-readable names only; **Forbidden** ids in user text per §5.1) and **Forbidden** §5.2 examples until resolved.
  - **Forbidden** attaching situational words (e.g. sleep, movie) to a **specific room** in generated examples until a **position** or **device** scope is fixed, unless the user themselves tied that word to a room/device.

### 1. Grounding on home facts

Run the CLI from the skill root (see [`../../SKILL.md`](../../SKILL.md), `aqara_open_api.py`):

- **`get_rooms`** — **Must** when not already satisfied in **§0** for this flow.
- **`get_home_devices`** — **Must** run; **Must** restrict the working set to **§0** scope: **position** path → keep rows for that **position** only; **device** path → keep only endpoints belonging to the resolved device(s). **Forbidden** include virtual endpoints whose **`deviceId`** **starts with** the **`ir.`** prefix in the working set (same IR filter as [`../automation-create.md`](../automation-create.md)).
- **`get_home_scenes`** — **Must** run; **Must** prefer scenes tied to the same **position name** when the user scoped a single room; for whole-home scope, include scenes across positions as returned by the table.
- **Optional:** **`get_home_automations`** — dedupe and reduce examples that overlap existing automations.

**Mandatory status pass (before §2–§4 wording work):**

- **`post_device_status`** — **Must** run **after** the working device list is known. Build the JSON body per [`../devices-inquiry.md`](../devices-inquiry.md): e.g. **`position_ids`** for a single chosen room, **`device_ids`** when the user scoped specific device(s), or combined filters when the API accepts them. **Goal:** ground **online/offline**, **current attribute readings** where returned, and **which attributes / resources the platform exposes** for those endpoints so §4 examples do not imply unsupported conditions or actions.
- **Optional:** **`post_device_base_info`** — **May** use for the same resolved **`device_ids`** when **`post_device_status`** is insufficient to judge **supported** attributes for recommendation.

### 2. Parse intent and keywords

- Classify intent: recommendation help vs already fairly specific.
- **Extract keywords:** room, device or scene type, time or delay, situational words (sleep, leave home, etc.), whether **outdoor weather** is implied (tag separately; **suggest 0-1 weather example sentences**).
- **Must** keep extracted entities **inside** the **§0–§1** working set (positions, devices, scenes) — **Forbidden** pulling names from outside the latest **`get_home_devices`** / **`get_home_scenes`** tables for this turn.
- **Do not** call `post_automation_recommend_query`; there is **no** platform "recommended template name" data source.

### 3. Filtering, status, time, and weather

- Filter device and scene subsets by keywords within the **§1** working set; **exclude** any **`ir.`**-prefixed virtual endpoints remaining in lists.
- **Empty filter:** relax keywords, or fall back to common controllable types in the **scoped** room.
- **Use the §1 `post_device_status` (and optional `post_device_base_info`) results:** **Must** use **connectivity**, **returned attribute keys / resources**, and **`device_type`** strings from **`get_home_devices`** together so that **recommended automations** **comprehensively** reflect **(a)** what is **currently** true where helpful (e.g. prefer “turn off” when target lights read **on**; avoid suggesting heavy actions on **offline** endpoints unless the user asked regardless), and **(b)** what the platform **supports** for conditions and actions (do not imply sensors or actions not evidenced by inventory + status/base_info). **Forbidden** to bake the **current snapshot** into a **fixed** rule the user did not ask for (e.g. **Forbidden** “when temperature is exactly 23°” solely because the live reading is 23°).
- **Current time:** fix time zone and clock source so they match schedule / delay examples and Step 02 `crontab_time` anchors.
- **Weather:** **By default** do **not** call `post_current_outdoor_weather`; outdoor-condition examples can be plain language with **region and threshold or phenomenon** spelled out. If this flow ever calls that API, **must** separately satisfy [`../../SKILL.md`](../../SKILL.md) and [`../weather-forecast.md`](../weather-forecast.md).
- **Simplicity vs coverage:** Still surface **diverse** ideas across the **10** lines, but each line **Must** obey the **one trigger → one outcome** default in **§4** (and the opening **Recommendation style** paragraph). **Forbidden** using one slot to pack a multi-trigger or multi-action “mega rule”.

### 4. Produce ten create-ready sentences (align with Step 01)

- Output **10** full rule sentences (prefer "When ..., then ..." / "If ..., then ..."); **entity names must come only** from **§1** API results.
- **Must** align proposed **conditions** and **actions** with **§1** evidence: **supported** attributes/resources and **`device_type`** strings, and **Must** respect **§3** viability (offline, unsupported capabilities).
- **Follow** [`../automation-create-workflow/step-01-conditions-actions-extract.md`](../automation-create-workflow/step-01-conditions-actions-extract.md): `conditions[].intent` / `actions[].intent`, **whole-scope wording gates**, delay vs "no motion for N minutes" boundaries, etc.
- **Default shape (normative for recommend examples):** Each of the **10** sentences **Must** read as **one** user-visible **trigger** and **one** user-visible **outcome** (one condition family + one action family). Examples:
  - **Allowed:** "Every night at 10:30 p.m., turn off the bedroom color light group." (schedule → single light/group action)
  - **Allowed:** "When the door/window sensor goes from open to closed, run the Good Night scene." (single sensor transition → single scene)
  - **Allowed:** "Every weekday at 8:30 a.m., open the master bedroom curtain (Zigbee curtain motor) to about 50%." (schedule → single curtain target) — **only if** the user did **not** ask for extra constraints;

### 5. Present and hand off (user-facing reply — **mandatory**)

#### 5.1 When anything is abnormal (errors / failures)

- **Must** respond **only** by stating the **error detail** the user needs (e.g. non-zero API `code` and `message`, HTTP failure, timeout, missing or invalid auth, script / environment failure). **No** successful recommendation body in the same turn.
- **Forbidden** in user-visible text: any **real resource identifier** for **home, device, endpoint, position (room), scene, or automation** (including values shaped like platform ids, e.g. strings beginning with `Aqr~`, and explicit `home_id` / `position_id` / `device_id` / `endpoint_id` / `scene_id` / `automation_id` style fields copied from API or CLI output).
- **Allowed:** **human-readable names** only (home name, room name, device name, endpoint display name, scene name, automation **title** as plain text) when they clarify the failure; generic `request_id` **May** appear if the platform returns it and it is **not** one of the forbidden resource id categories above.

#### 5.2 When the flow succeeds (ten examples ready)

- **Must** use this **structure** (order fixed; lead-in wording **localizes** — not a single frozen English string):
  - **Line 1 (lead-in):** One short sentence in the **same primary language** as the user’s input in that turn. It **Must** make clear they may **reply with a serial number** (`1`–`10`) or a **rewrite** of one line to continue with create. **Forbidden** defaulting to English when the user wrote only in another language (e.g. Chinese-only → Chinese lead-in). If the turn is **clearly mixed-language**, use one concise lead-in that matches the dominant language or a **brief** bilingual line — avoid robotic template tone.
  - **Lines 2–11:** `1.` through `10.` (ASCII period immediately after each numeral; **no** other punctuation between the digit and the sentence), each **immediately** followed by **one** full create-ready rule sentence from Step 4 (**Must** match the user’s language when they wrote in a **single** language).
- **Forbidden:** extra banners (e.g. ~~“Examples not created yet”~~ / ~~“Examples only, not created yet”~~), platform “recommended template” **names** as headings, raw JSON, shell transcripts, or any id type listed in §5.1.
- After the user **names a serial number** or **confirms a rewrite** of one line -> go **straight** to [`../automation-create.md`](../automation-create.md): Step 01 -> Step 02 -> **`post_create_automation`** (if the response includes `LLMConfigReference`, complete fields per [`../automation-create-workflow/step-03-parse-config-prompt.md`](../automation-create-workflow/step-03-parse-config-prompt.md); **every request must include non-empty `raw_config`**, see `automation-create.md`).

---

## Related documents

[`../automation-create.md`](../automation-create.md), [`../automation-manage.md`](../automation-manage.md), [`../devices-inquiry.md`](../devices-inquiry.md), [`failure-response.md`](failure-response.md).
