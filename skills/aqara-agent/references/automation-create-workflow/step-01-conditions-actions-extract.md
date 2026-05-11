# Step 01 - Condition / action NL split (rows + placeholders only)

**Scope:** From the user utterance only, emit `conditions[]` / `actions[]` with per-row `sub_query`, `intent`, relations, top-level `name` / `execute_once`, etc. **Do not** put business data in `cell_info` (no schedules, weather, device or scene IDs).

**Convention:** Every row has `"cell_info": {}` (**forbidden** `null` or omitting the key).

**Routing:** Next: [`step-02-cell-info-fill.md`](step-02-cell-info-fill.md) (`conditions_actions_cell_info_fill`). Read before **Workflow - Plan** or manifest **`conditions_actions_nl_parse`**. Index: [`manifest.json`](manifest.json). Parent: [`../automation-create.md#step-1-nl-split`](../automation-create.md#step-1-nl-split).

---

<a id="step01-raw-config-field-contract"></a>

## Mandatory shape for fields that enter `raw_config` (**Must**)

After Step 02 packs `cell_info`, the payload **`raw_config`** **must** remain a single non-empty object that includes at least the following **normative** keys (same meanings after Step 02 merge per [`../automation-create.md`](../automation-create.md)):

| Key / path | Type | **Must** semantics |
| --- | --- | --- |
| `name` | `string` | **Full automation title derived from the user query** (full "when/if … then …" sentence or equivalent, same language as input; **forbidden** tag-only fragments). |
| `conditions[].sub_query` | `string` | **This row’s condition clause cut from the query** (only this trigger semantics; minimal split, no widening). |
| `conditions[].intent` | `int` | **Intent for this row’s `sub_query`**, **must** come from the **§ III.A** allowlist. |
| `conditions[].sub_query_contain_position_name` | `bool` | **Whether this row’s `sub_query` mentions a place / room name** (`true` if yes, else `false`). |
| `conditions[].position_id` | `int` \| `null` | **If this row’s `sub_query` already maps to a `get_rooms` position, fill that platform position id; else JSON `null`.** Step 01 usually keeps `null`; Step 02 fills after resolving rooms. **Reconciliation:** if tenant **`automation/create`** requires `position_id` as a string (matching `get_rooms`), Step 02 **must** follow the **real API**, **forbidden** to invent. |
| `actions[].sub_query` | `string` | **This row’s action clause cut from the query** (only this execution semantics; **not** the whole condition sentence). |
| `actions[].intent` | `int` | **Intent for this row’s `sub_query`**, **must** come from the **§ III.B** allowlist. |
| `actions[].sub_query_contain_position_name` | `bool` | **Whether this row’s `sub_query` mentions a place / room name**. |
| `actions[].position_id` | `int` \| `null` | **Same as above:** fill real position id when mappable, else `null`; string form per tenant. |

The top level also includes `conditions_relation`, `actions_relation`, `execute_once`, and per-row `cell_info` (Step 01 is `{}`, Step 02 fills by intent) — see **Output fields** below and Step 02.

---

## Gates (read first)

1. **Split only:** Rows, `intent`, and relations come **only** from the raw utterance. **Forbidden:** invented objects or scope, table-driven rewrites, or "helpful" paraphrase that changes meaning.
2. **Spatial action (2) / spatial query (3):** Use those intents **only** when the user **already** said whole-space language (**all / every / whole / any**, etc.) that matches the tables below. Otherwise stay literal; most actions stay **intent 1**.
3. **Literal `sub_query`:** Minimal cuts, **no** widening (e.g. "turn off the bedroom lights" stays that; **not** "turn off all bedroom lights" unless the user said **all**). "Home lights and AC" stays literal chunks; **not** "all home lights / all AC". **Forbidden:** action **intent 2** without explicit whole-scope words. Delay + lights: condition = time phrase (**intent 5**); action = user's light phrase (**intent 1**) unless they said **all** lights. *(Expanded split / intent policy: **Core rules § II–IV**.)*

---

## Core rules (mandatory; validate row-by-row)

Normative expansion of **Gates** and split / intent policy. If anything here tightens wording compared with older examples, **this section wins**.

### I. Basics

1. **Language consistency:** `sub_query`, `name`, and other free-text fields **must** match the **input query language** exactly (Chinese in → Chinese out; German in → German out).
2. **Null handling:** For any field with no applicable value, use JSON **`null`** (**forbidden:** Python `None`, empty string `""`, or other placeholders).
3. **Strict types:** JSON types **must** match the schema (`int` = integer only, `bool` = `true` / `false` only, `list` = JSON array).
4. **`cell_info` in this step:** Still always `{}` here (**forbidden** keys such as `device_ids`, `crontab_time`, `scene_id` in Step 01).

### II. Split rules (row granularity; do not merge)

#### 1. Location split and inheritance

- **Multiple locations:** Conditions or actions that refer to **different** places **must** become **separate rows** (e.g. "Turn on the kitchen and balcony lights" → two actions: "Turn on the kitchen lights", "Turn on the balcony lights").
- **Location inheritance:** When the user ties a condition to one space and an action to another, **each row carries the location implied by that row** (do not drop room on the action side).
  - Example: "When there is someone in the **bedroom** or **living room**, turn on the lights" → conditions: "Someone in the bedroom", "Someone in the living room"; actions: "Turn on bedroom lights", "Turn on living room lights".
  - Example: "In the **living room**, create an automation: **5 minutes later** turn off the lights" → condition: "5 minutes later"; action: "Turn off living room lights".
  - Example: "**Whole home** detects nobody **and** temperature drops to 22 °C → set **whole-home** strips to yellow" → conditions: "Whole home nobody", "Whole-home temperature drops to 22 °C"; action: "Whole-home strips to yellow".
  - Example: "When **bedroom** TVOC concentration **> 2**, open the curtains" → condition: "Bedroom TVOC concentration > 2"; action: "Open bedroom curtains".
  - Example: "**Bathroom** or **master bedroom**: no motion for 5 minutes → turn off lights" → conditions: "Bathroom no motion for 5 minutes", "Master bedroom no motion for 5 minutes"; actions: "Turn off bathroom lights", "Turn off master bedroom lights".
  - Example: "When **all** home AC is off → turn off **all** kitchen lights" → condition: "All home AC off" (scope: whole home); action: "Turn off all kitchen lights".
  - Example: "When **home** strip **or** spot is off → set **living room** AC to 26 °C" → conditions: "Home strip off", "Home spot off"; action: "Set living room AC to 26 °C".
  - Example: "**Every day at 20:00**, when **home** strip **or** spot is off → set **living room** AC to 26 °C" → conditions: "Every day at 20:00", "Home strip off", "Home spot off"; action: "Set living room AC to 26 °C".
  - Example: "In the **bedroom**, set an automation: **every day at 9:00** turn on the lights" → condition: "Every day at 9:00"; action: "Turn on bedroom lights".

#### 2. Operation split

- **Different devices** → separate action rows (e.g. "Turn on living room lights and bedroom AC" → two actions).
- **Same device, multiple settings** → separate rows when the user asked for **independent** knobs (e.g. "Living room AC to 25 °C cooling" → "Living room AC to 25 °C", "Living room AC to cooling mode").
- **Same device, multiple parameters** → separate rows (e.g. "All bedroom lights brightness 5 % and color temperature 2000 K" → "All bedroom lights brightness 5 %", "All bedroom lights color temperature 2000 K").
- **Different operations** → separate rows (e.g. "Turn on the light and brighten 10 %" → "Turn on the light", "Brighten the light 10 %").
- **Exception — do not split** when a **single supported motion-sensor style** sentence is one semantic unit, e.g. "Someone moved **and** illuminance is below / above **x** lux", or "Someone detected **and** no motion for **x** minutes before that" → **one** condition row when the product semantics treat it as one trigger.

### III. Intent classification (`intent` is taken **only** from here)

#### (A) `conditions[].intent` (allowed integers)

| intent | Meaning | Examples |
| --- | --- | --- |
| **1** | **Device control** | Condition is triggered by a **device action** (e.g. "when the light turns off", "after the AC turns on"). |
| **2** | **Device state inquiry** | Condition is a **concrete device** or local sensor state (e.g. "bedroom AC temperature > 27 °C", "outlet power < 5 W", "doorbell pressed", "window open"). |
| **3** | **Spatial inquiry** | **Only** when the user names a **space** plus **any / all / every / whole**-style scope for **one of three object families**: **1 = lights**, **2 = AC**, **3 = indoor temperature / humidity** (no specific device model in the wording for temp/humidity aggregate). Examples: "Any living room light is on", "Bedroom temperature > 30 °C" **without** naming "bedroom AC". **Without** any/all/every → **not** intent **3** for that clause. |
| **4** | **Schedule** | Fixed clock / repeat (e.g. "every day at 8:00", "every Monday at 10:00"). **Sunrise / sunset with no geography** also map here (or to **5** if phrased as pure delay — disambiguate by utterance). |
| **5** | **Delay** | **Relative** time (e.g. "in 5 minutes", "in 1 hour"); `sub_query` keeps **only** the time phrase. |
| **6** | **Security / guard** | Alarm / arm / disarm plus objects such as home / away / night guard (e.g. "when home guard alarms"). |
| **7** | **Outdoor / geo weather** | Outdoor weather (current / forecast), outdoor temp / humidity / air quality, or **sunrise / sunset tied to a geographic place** (e.g. "sunset in Haidian District, Beijing"). |
| **9** | **Other** | No match above. |

#### (B) `actions[].intent` (allowed integers)

| intent | Meaning | Examples |
| --- | --- | --- |
| **1** | **Device control** | Operation on a **named device** or **type-prefixed** device class (e.g. "turn on the Midea AC", "turn off living room spotlights", "set bedroom light to 3000 K", "set master bedroom downlight to reading scene"). |
| **2** | **Spatial control** | **Must** have **space** + explicit **whole-scope** wording (**all / every / turn all on / turn all off / whole …**) + **no extra device-type prefix** on the controlled object; object family **only** **1 = lights**, **2 = AC**, **3 = curtains**. Example: "Set **all** bedroom lights to 2000 K" → **2**. **Without** "all/every/…" → **1** (e.g. "bedroom light color temperature 2000 K" → **1**). |
| **3** | **Scene execute** | Run a **catalog scene only** — no per-device imperative in the same intent (e.g. "Run the Sleep scene"). |
| **4** | **Push** | Normal notification / message **without** stressing "alarm" (e.g. "push a message that temperature exceeded the limit", "send me a notification"). |
| **5** | **Alarm push** | User **clearly** stresses **alarm** / fault alerting or channels like SMS / phone / email with alarm semantics (e.g. "push AC fault **alarm**", "push **alarm** and text me"). |
| **6** | **Security actions** | Actions such as turn off alarm, auto arm, auto disarm, toggle arm/disarm; optional guard targets (home / away / night). |
| **9** | **Other** | No match above. |

### IV. Boundary rules (easy-to-confuse cases)

1. **Spatial inquiry (3) vs device state (2) vs outdoor (7)**
   - "Bedroom temperature > 30 °C" (no AC model named) → **3**.
   - "Bedroom AC temperature = 30 °C" → **2** (tied to a **device category** in a space).
   - "Outdoor temperature > 30 °C" → **7** (outdoor).
   - **Bare** temperature compare **with no room** (e.g. "temperature > 28 °C", "temperature drops to 22 °C") → **2** (device-style metric), **not** **3**, unless the utterance is a defined **whole-home indoor aggregate** (then **3** per aggregate table rows).

2. **Sunrise / sunset**
   - **With** geography ("Shanghai sunrise") → **7**.
   - **Without** geography ("at sunrise") → **4** (schedule) or **5** (delay) by phrasing.

3. **Spatial control (2) vs device control (1)**
   - "**All** bedroom lights brighter" → **2** (whole-scope + lights + no type prefix beyond "lights").
   - "**All** bedroom **spot**lights brighter" → **1** ("spotlights" is a **type prefix**).
   - For **2**, the `sub_query` **must** include an explicit whole-scope token (e.g. **all / every / whole home on|off / turn all on / turn all off**). Otherwise → **1**.
   - Examples: "Bedroom light color temperature 2000 K" → **1**; "**All** bedroom lights color temperature 2000 K" → **2**.
   - "Turn off home AC" (no whole-scope word) → **1**; "**Turn all** home AC off" → **2**.
   - "Turn off home lights and AC" (no per-category "all") → split / literal → typically **1** rows, **not** **2**.

4. **Spatial inquiry (3) vs device state (2) — stricter object list**
   - Intent **3** supports **only** aggregates on **lights**, **AC**, or **indoor temp/humidity**. Any other state → **2**.
   - Intent **3** **requires** whole-scope language (**any / all / every** …). Otherwise → **2**.
   - **Generic occupancy** vs **light aggregate:** e.g. "Whole home detects **nobody**" → **2**; "**All** whole-home lights are off" → **3** (light aggregate).
   - Examples: "Any living room light on" → **3**; "Living room light on" (no any/all) → **2**.
   - "**All** bedroom AC off" → **3**; "Bedroom AC off" (no all) → **2**.
   - "Bedroom TVOC > 2" → **2**; "Whole-home indoor temperature drops to 22 °C" as a **whole-home** aggregate → **3** (see edge-case table).

5. **Schedule / delay (4 / 5) vs device inquiry (2)**
   - "No person detected for 5 minutes" / "Someone detected **and** no motion for the previous hour" → **2** (sensor semantics), **not** **5**.
   - "In 5 minutes" (pure relative wait) → **5**.

6. **Spatial control (2) vs device control (1) vs scene execute (3)**
   - Named device or **fixture-level** scene wording ("set **downlight** to Cozy scene") → **1**.
   - Space + whole-scope + lights/AC/curtains **without** type narrowing → **2** (e.g. "**All** bedroom lights to Cozy scene").
   - Only "run **scene X**" → **3**.

---

## Pre-flight

- [ ] Host placeholders ready (`{query}`, `{now}`, `{month_start}`, `{week_start}`, `{current_position}`, `{positions_list}`, `{scene_list}`) per `automation-create.md` Step 1 (this step still outputs `cell_info: {}` only).
- [ ] Emit **JSON only** (no fences, no prose).
- [ ] `position_id` / `cell_info` content: resolve in Step 02 + API (`get_rooms`, `get_home_scenes`, `get_home_devices`, ...).

---

## Split granularity (do not merge)

Row granularity (multiple locations, location inheritance on each row, operation splits, motion-sensor single-row exception) is defined **only** in **Core rules — § II** (bullets there are normative). **Do not** merge rows that § II requires as separate `sub_query` rows.

---

## Intent integers (Step 01 output)

Per-row **`intent`** values are defined only in **Core rules — § III** (**§ III.A** `conditions[].intent`, **§ III.B** `actions[].intent`). **Forbidden:** string aliases such as `"delay"`, `"device_control"`, `"schedule"`; each code **must** be a JSON integer in the allowed ranges.

When Step 02 packs **`raw_config`** for `post_create_automation`, those same integer codes are serialized into **`raw_config`**; details: [step-02-cell-info-fill.md](step-02-cell-info-fill.md) and [`../automation-create.md`](../automation-create.md).

---

## Edge cases (retrieval tables)

Use **`case_id`** for stable lookup (grep, manifests, tests). Semantics follow **Gates**, **Core rules** (especially **§ IV**), and the **`case_id`** tables below (tables **illustrate** § IV; on conflict, **§ IV** wins).

### `conditions[]` - spatial query (3) vs device state (2) vs outdoor (7)

| case_id | user_pattern (summary) | `conditions[].intent` | notes |
| --- | --- | --- | --- |
| `cond_indoor_threshold_space_no_device` | Space + indoor temp/humidity, no device model in wording | 3 | e.g. bedroom > 30 C |
| `cond_device_category_in_space` | Space + named device category (e.g. bedroom AC) | 2 | ties to a device type |
| `cond_outdoor_or_geo_weather` | Outdoor / explicit geo weather | 7 | includes geo sunrise/sunset |
| `cond_aggregate_lights_ac_need_whole_words` | Lights or AC **state** as a space aggregate | 3 | usually needs any/all/every in wording |
| `cond_single_light_or_single_ac_state` | One light or one AC on/off without any/all/every | 2 | not a space aggregate query |
| `cond_presence_no_person_home` | Nobody / no person detected (whole home) | 2 | occupancy style, not "all lights" wording |
| `cond_all_home_lights_off_wording` | Explicit all-home lights off (aggregate) | 3 | whole-scope on lights |
| `cond_any_living_room_light_on` | Any + room + lights on | 3 | |
| `cond_living_room_light_on_no_any` | Room + light on, no any/all/every | 2 | |
| `cond_all_bedroom_ac_off` | All + room + AC off | 3 | |
| `cond_bedroom_ac_off_no_all` | Bedroom AC off, no all/every | 2 | |
| `cond_tvoc_or_air_metric_named` | TVOC / similar single-device or local metric | 2 | |
| `cond_generic_ac_temp_no_room` | AC temperature without a space name | 2 | bare device-class temp |
| `cond_whole_home_temperature_aggregate` | Whole-home indoor temperature aggregate | 3 | e.g. whole-home temp to 22 C |
| `cond_bare_temp_no_space` | Temperature compare, no room / space | 2 | e.g. temp > 28 with no room |

### `conditions[]` - sunrise / sunset

| case_id | user_pattern (summary) | `conditions[].intent` | notes |
| --- | --- | --- | --- |
| `cond_sunrise_sunset_with_geography` | Sunrise/sunset tied to a place | 7 | e.g. Shanghai sunrise |
| `cond_sunrise_sunset_no_place` | At sunrise / at sunset, no geography | 4 or 5 | schedule vs delay by phrasing |

### `conditions[]` - delay (5) vs sensor time window (2)

| case_id | user_pattern (summary) | `conditions[].intent` | notes |
| --- | --- | --- | --- |
| `cond_sensor_no_motion_window` | No motion for X minutes / occupancy-style window | 2 | sensor semantics |
| `cond_sensor_motion_plus_prior_empty` | Motion + prior period without motion | 2 | one semantic unit stays one row when allowed |
| `cond_delay_in_x_minutes` | In X minutes / after X hours (pure delay) | 5 | `sub_query` is only the time phrase |

### `actions[]` - spatial control (2) vs device control (1)

| case_id | user_pattern (summary) | `actions[].intent` | notes |
| --- | --- | --- | --- |
| `act_all_bedroom_lights_no_type_prefix` | All + bedroom + lights, no extra device-type word | 2 | spatial control |
| `act_all_bedroom_spotlights_prefixed` | All + bedroom + spotlights (typed subset) | 1 | prefix "spotlights" -> device control |
| `act_home_lights_and_ac_no_whole_scope` | Home lights + AC off without user saying all/every | 1 | literal `sub_query`; same as **Gates** item 3 |

### `actions[]` - device (1) vs spatial (2) vs scene (3)

| case_id | user_pattern (summary) | `actions[].intent` | notes |
| --- | --- | --- | --- |
| `act_named_device_or_prefixed_lights` | Named device or prefixed light type | 1 | includes brand or fixture type |
| `act_space_whole_scope_lights_ac_curtains` | Space + all/every/whole + lights/AC/curtains, no extra type prefix | 2 | |
| `act_run_scene_only` | Run scene only, no per-device ops in same intent | 3 | |

---

## Output fields

`conditions[].intent` and `actions[].intent` are **`int`** values from **Core rules — § III** (**forbidden** string digits or aliases). **`name`:** one full rule sentence in the input language ("When ..., then ..." / "If ..., then ..."); **forbidden** tag-like fragments ("bedroom lights" alone).

| Field | Type | Notes |
| --- | --- | --- |
| `name` | `string` | **Full automation title from the user query** (full rule sentence, input language). |
| `conditions` | `array` | Rows: `sub_query`, `intent`, `sub_query_contain_position_name`, `position_id`, `cell_info`. |
| `conditions_relation` | `int` | `0` OR, `1` AND; default **1**. |
| `actions` | `array` | Same row shape as conditions. |
| `actions_relation` | `int` | `0` OR, `1` AND; default **1**. |
| `execute_once` | `bool` | One-shot flag. |

**Row fields**

| Field | Type | Notes |
| --- | --- | --- |
| `sub_query` | `string` | **Condition row:** **condition clause** cut from the query; **action row:** **action clause** cut from the query. This row only; same language as input. |
| `intent` | `int` | Intent for this row’s `sub_query`; **must** come from **Core rules — § III** (conditions: **§ III.A**, actions: **§ III.B**). |
| `sub_query_contain_position_name` | `bool` | Whether this row’s `sub_query` mentions a place name. |
| `position_id` | `str \| null` or tenant-required id type | **If this row mentions a place:** after Step 02 resolves via `get_rooms`, write the **real** position id; before resolution JSON `null`. **Forbidden** placeholder fake ids. If Open returns string `positionId`, serialize per API. |
| `cell_info` | `object` | Step 01 is always `{}`. |

---

## JSON schema (illustrative `intent: 0` - replace with real intents)

```json
{
  "name": "str",
  "conditions": [
    {
      "sub_query": "str",
      "intent": 0,
      "sub_query_contain_position_name": false,
      "position_id": "",
      "cell_info": {}
    }
  ],
  "conditions_relation": 1,
  "actions": [
    {
      "sub_query": "str",
      "intent": 0,
      "sub_query_contain_position_name": false,
      "position_id": "",
      "cell_info": {}
    }
  ],
  "actions_relation": 1,
  "execute_once": false
}
```

Final `intent` values **must not** stay `0`. `position_id` is validated or filled later.

---

## Example

```json
{
  "name": "Every day at 9:00, turn on the bedroom lights and turn off the bedroom AC",
  "conditions": [
    {
      "sub_query": "Every day at 9:00",
      "intent": 4,
      "sub_query_contain_position_name": false,
      "position_id": null,
      "cell_info": {}
    }
  ],
  "conditions_relation": 1,
  "actions": [
    {
      "sub_query": "Turn on bedroom lights",
      "intent": 1,
      "sub_query_contain_position_name": true,
      "position_id": null,
      "cell_info": {}
    },
    {
      "sub_query": "Turn off bedroom AC",
      "intent": 1,
      "sub_query_contain_position_name": true,
      "position_id": null,
      "cell_info": {}
    }
  ],
  "actions_relation": 1,
  "execute_once": false
}
```

---

## Self-check

- [ ] **[Mandatory `raw_config` fields](#step01-raw-config-field-contract)**: `name` and each row’s `sub_query` / `intent` / `sub_query_contain_position_name` / `position_id` present with correct types.
- [ ] `name` is a full When/If-then style sentence (input language).
- [ ] No widened `sub_query`; no action **2** without whole-scope words (incl. home lights + AC case); aligns with **Core rules § II–IV**.
- [ ] Intents from **Core rules § III** only, never `0`.
- [ ] Every row: `"cell_info": {}` only; JSON parses with `json.loads`; no fences or extra text.

**Optional host line:** Return **only** one JSON string; no Markdown fences or explanation.

---

## Skill constraints

- Integer `intent` here is **not** Open Platform trigger/action **definition IDs**.
- Business `cell_info` -> [Step 02](step-02-cell-info-fill.md).
