# Step 02 - Fill `cell_info` and pack `raw_config`

**Input:** Step 01 rows (each `cell_info` was `{}`). Optional: scenes, devices, rooms, weather / geo context.

**Output:** Tenant-shaped `raw_config` for the **first** `post_create_automation` (and the same non-empty payload on **every** later call per [`../automation-create.md#post-create-raw-config-always`](../automation-create.md#post-create-raw-config-always)).

**When:** After Step 01, before first `post_create_automation`. Index: [`manifest.json`](manifest.json) - **`conditions_actions_cell_info_fill`**. Parent: [`../automation-create.md#step-2-cell-info`](../automation-create.md#step-2-cell-info).

---

<a id="raw-config-required-fields"></a>

## `raw_config` **Must** retain these keys (with Step 01 semantics)

After packing, **`raw_config`** **must** be a **non-empty** object, and it is **forbidden** in Step 02 to drop or rename the following keys (unless the tenant Open doc mandates a different key name, in which case **must** preserve equivalent semantics):

| Key / path | Type | **Must** semantics |
| --- | --- | --- |
| `name` | `string` | **Full automation title derived from the user query** (same as Step 01). |
| `conditions[].sub_query` | `string` | **This row’s condition clause cut from the query** (same as Step 01; only minimal normalization for tenant validation, **forbidden** to change trigger meaning). |
| `conditions[].intent` | `int` | **Intent for this row’s `sub_query`**; **must** come from the **§ III.A** allowlist in Step 01 (**forbidden** to use `0` or string aliases). |
| `conditions[].sub_query_contain_position_name` | `bool` | **Whether this row’s `sub_query` mentions a place / room name** (`true` if yes, else `false`). |
| `conditions[].position_id` | `int` \| `null` or tenant position id | **If this row mentions a place:** **must** write the **real** position id resolved from `get_rooms`; if not mentioned or unresolvable, JSON `null`. **Forbidden** to invent. If the tenant requires string `positionId`, follow the list API return shape. |
| `actions[].sub_query` | `string` | **This row’s action clause cut from the query** (same as Step 01). |
| `actions[].intent` | `int` | **Intent for this row’s `sub_query`**. |
| `actions[].sub_query_contain_position_name` | `bool` | **Whether this row’s `sub_query` mentions a place / room name**. |
| `actions[].position_id` | `int` \| `null` or tenant position id | **Same as above:** fill real position id when mappable, else `null`; string form per tenant. |

Beyond the fields above, Step 02 **must** write **`cell_info`** for every row and keep top-level fields consistent with Step 01 (`conditions_relation`, `actions_relation`, `execute_once`, etc.); **concrete keys and the empty-object rule** are in **[`cell_info` boundary (no junk for unlisted intents)](#cell-info-boundary)** (fill per the intent tables where defined; otherwise **`{}`**).

---

## Pre-flight

- [ ] **`raw_config` row contract** (see **[Must retain](#raw-config-required-fields)**): `name` and each row’s `sub_query`, `intent`, `sub_query_contain_position_name`, `position_id` **must** carry over from Step 01 and have `position_id` completed here from APIs; **forbidden** to omit.
- [ ] Row count and `sub_query` meanings match Step 01; **forbidden** new rows unless the tenant explicitly allows expansion here.
- [ ] In the packed **`raw_config`**, every **`conditions[].intent`** and **`actions[].intent`** **must** be an **`int`**, with semantics taken **only** from the **`conditions[].intent`** (**1**–**7**, **9**) and **`actions[].intent`** (**1**–**6**, **9**) tables in [step-01-conditions-actions-extract.md](step-01-conditions-actions-extract.md). **Forbidden:** string aliases such as `delay`, `device_control`, `schedule`.
- [ ] Schedule / delay rows (`intent` **4** / **5**): fill `cell_info.crontab_time` per [**`crontab_time` format (five-field)**](#crontab_time-format-five-field-schedule-string) when the host uses that contract; otherwise use [**6-field `crontab` (Quartz)**](#six-field-crontab-quartz) when the tenant requires Quartz-style six fields. **Forbidden** mixing conventions in one payload without tenant confirmation.
- [ ] User-specified scenes/devices: IDs resolved from real lists; for rows whose **`intent`** has a **`cell_info`** shape in this doc, required fields **must not** be left blank; for other intents **`cell_info` must be `{}`** per **[cell_info boundary](#cell-info-boundary)**.
- [ ] `raw_config` stays **non-empty** on every `post_create_automation` (including after Step 03).

---

## `intent` in `raw_config` (integer codes, normative)

**`conditions[].intent`** and **`actions[].intent`** serialized into **`raw_config`** **must** match the two tables in [step-01-conditions-actions-extract.md](step-01-conditions-actions-extract.md) — **`conditions[].intent`** (**1**–**7**, **9**) and **`actions[].intent`** (**1**–**6**, **9**) — with type **`int`** (**forbidden:** `0`, **forbidden:** string aliases). Meaning and table selection follow Step 01; Step 02 only fills **`cell_info`**, schedule **`crontab`** / **`crontab_time`**, and other tenant fields for the resolved **`intent`**.

---

## `cell_info` by intent (aligned with Step 01 numeric `intent`)

Numeric **`intent`** values match **`conditions[].intent` / `actions[].intent`** in [`step-01-conditions-actions-extract.md`](step-01-conditions-actions-extract.md). Fill **only** from that row's **`sub_query`**; resolve IDs via inventory / APIs, then write **`cell_info`** (aligned with the tenant **`raw_config`** shape).

### Trigger conditions (`conditions[]`)

| `intent` | `cell_info` | Notes |
| --- | --- | --- |
| **1** Device control / **2** Device inquiry | `{"device_ids": [...]}` | **Must** resolve devices from the current `sub_query` into resolved `device_id`s (**forbidden** placeholder fake IDs; an empty array means not yet resolved). |
| **3** Spatial query | `{"space_subject": <int>}` | From `sub_query`, **only**: `1` = lights, `2` = AC, `3` = temperature / humidity. |
| **4** Schedule / **5** Delay | `{"crontab_time": "<str>"}` | **Must** extract user time semantics from the current `sub_query` (natural language or normalized instant / interval; string format per tenant). Intent **4** = wall-clock / repeat; **5** = relative delay. See [**`crontab_time` format (five-field)**](#crontab_time-format-five-field-schedule-string) below when the integration uses the Open-style single string; otherwise follow the tenant contract (including Quartz-style 6-field if required). |
| **7** Outdoor weather | `{"weather_type": <int>, "weather_location_en": [<str>, ...]}` | Classify `weather_type` from `sub_query`, **only**: `1` current weather, `2` forecast weather, `3` outdoor temperature, `4` outdoor humidity, `5` outdoor air quality, `6` sunset, `7` sunrise, `8` other. For **`weather_location_en`**: the key **must** be present on `intent` **7** rows. If the user **names** a place in `sub_query`, normalize to **English**, include administrative levels (Province / City / District, consistent with the utterance); e.g. Shenzhen Nanshan → `["Shenzhen City", "Nanshan District"]` (granularity per `sub_query`). If the user **does not** name any city / district / region for the weather condition (e.g. only "outdoor temperature" with no place name), **`weather_location_en` must be `[]`** — **forbidden** to invent or default to any specific city. See [**Intent 7 — unnamed weather city**](#intent-7-unnamed-weather-city) below. |

### Actions (`actions[]`)

| `intent` | `cell_info` | Notes |
| --- | --- | --- |
| **1** Device control | `{"device_ids": [...], "attribute": "", "action": "", "value": ""}` | **Must** resolve target devices from the current `sub_query` into `device_ids`. **`attribute` / `action` / `value`** slots **must** match immediate device control: [`../devices-control.md`](../devices-control.md) + [`../../assets/device_control_action_table.csv`](../../assets/device_control_action_table.csv), plus the **Device** section below and [`../automation-create.md#device-intent-ir-filter`](../automation-create.md#device-intent-ir-filter). |
| **2** Spatial control | `{"space_subject": <int>}` | From `sub_query`, **only**: `1` = lights, `2` = AC, `3` = curtains (**forbidden** to mix with condition row **3** temp-humidity codes). |
| **3** Scene execute | `{"scene_id": "<str>"}` | Bind scene from `sub_query`: **prefer** the catalog scene under the user's **current position** (`current_position` / this row's `position_id` context), then `scene_id`; if none, search other positions / whole-home scene list. Parsing and fuzzy rules: [`../scene-manage.md`](../scene-manage.md). |

<a id="cell-info-boundary"></a>

### `cell_info` boundary (no junk fields for intents not listed here)

When packing **`cell_info`**, obey:

- **`conditions[]`:** Only when this row’s **`intent` is 1, 2, 3, 4, 5, or 7**, fill the concrete fields described in the **Trigger conditions** table above; **for all other** condition intents (e.g. **6** security / guard, **9** other — any intent **without** a key structure in this section), **must not** invent tenant fields, guessed threshold keys, or keys unrelated to `sub_query`; **`cell_info` must be `{}` (empty object)**.
- **`actions[]`:** Only when this row’s **`intent` is 1, 2, or 3**, fill the concrete fields in the **Actions** table above; **for all other** action intents (e.g. **4** push, **5** alarm push, **6** security actions, **9** other — no key structure in this section), **`cell_info` must be `{}`** likewise.
- **Forbidden:** stuffing placeholder keys not defined in tenant Open docs or this file just to look complete, ad hoc `message`/`notify` blobs, or dirty data unrelated to that row’s **`intent` / `sub_query`**; if an intent later gets a formal field table in Open docs or this file, add it in a dedicated update — **do not** pre-fill placeholders before this section defines them.

**Note:** Condition row **3** `space_subject` (lights / AC / **temp-humidity**) and action row **2** `space_subject` (lights / AC / **curtains**) use different semantics and enums—use the table for that row type.

<a id="intent-7-unnamed-weather-city"></a>

### Intent 7 — unnamed weather city

When the natural-language condition is outdoor weather (temperature rise/drop, humidity, sunrise/sunset tied to **no** user-named geography, etc.) and **`sub_query` does not contain an explicit city / district / administrative place**, **`cell_info.weather_location_en` must be the empty array `[]`**. **Forbidden:** filling a default or assumed city (e.g. capital, account region, or "usual home city") in `weather_location_en` or in parallel tenant fields without the user stating that place. Let the first `post_create_automation` round and any **`LLMConfigReference` / `PD.cityId`** (or tenant-equivalent) prompt the user or the product flow to bind the city when the platform requires it.

---

<a id="crontab_time-format-five-field-schedule-string"></a>

## `crontab_time` format (five-field schedule string)

**Scope:** Filling `cell_info.crontab_time` for **schedule (intent 4)** and **delay (intent 5)** when the tenant / Open mapping expects a **single space-separated string**: **`minute hour day month weekday`** (five fields).

**Reconciliation:** Some deployments encode schedule in `crontab_time` with this **five-field** convention (Aqara Open docs: minute / hour / day-of-month / month / weekday). Others require **Quartz-style six-field** expressions in payloads or a different field name—**must** follow the live **`automation/create`** contract for your host. When both appear in this skill, resolve conflicts by **successful API validation**, not by prose alone.

### 1. Field rules (space-separated)

- **Minute:** `0`–`59`; `*` = no restriction; multiple values = comma-separated (e.g. `10,20,30` = at minutes 10, 20, 30 within the resolved hour context).
- **Hour:** `0`–`23`; `*` = no restriction; comma lists allowed (e.g. `2,4` = 02:00 and 04:00).
- **Day of month:** `1`–`31`; `*` = no restriction.
- **Month:** `1`–`12`; `*` = no restriction.
- **Weekday:** `0` = Sunday, `1`–`6` = Monday–Saturday, `7` = holiday (per platform definition), `8` = working day (per platform definition), `*` = no restriction.

### 2. Examples (align calendar fields to anchor `{now}` when the user does not name a date)

Assume anchor for worked examples: **2026-01-05 22:46, Monday** (use the real `{now}` in production).

| User phrase (summary) | `crontab_time` (example string) | Notes |
| --- | --- | --- |
| 20:45 (clock time; resolve to intended calendar day) | `45 20 5 1 *` | Minute **45**, hour **20**, **day 5**, **month 1** for same-day Jan 5; adjust day/month if the utterance implies another date. |
| In 6 hours 43 minutes | `29 5 6 1 *` | Resolved absolute time **2026-01-06 05:29** from the anchor above. |
| Every day at 02:30 | `30 2 * * *` | |
| Every Mon–Fri at 01:00 | `0 1 * * 1,2,3,4,5` | |
| Weekends at 01:00 | `0 1 * * 0,6` | |
| Legal working day at 20:00 | `0 20 * * 8` | |
| Legal holiday at 20:00 | `0 20 * * 7` | |
| In 1 hour (from anchor 22:46 same day) | `46 23 5 1 *` | |
| Every day at sunset | `sunset 0 ? * *` | Token form when the platform supports sunset in this field. |
| 4 hours after sunrise | `sunrise 240 * * *` | Offset in minutes after sunrise when supported. |
| Every Monday, 45 minutes before sunset | `sunset -45 * * 1` | |
| This week's Thursday at 10:18 | `18 10 8 1 *` | Example: Thursday falls on **Jan 8** in the same week as anchor Jan 5, 2026—recompute `day` / `month` / `weekday` from `{now}`. |

**Must** recompute relative delays ("in X hours / minutes") and "this week's Thursday at …" from the authoritative clock / timezone the host injects as `{now}`; **forbidden** hard-coding illustrative dates in production payloads.

---

<a id="six-field-crontab-quartz"></a>

## 6-field `crontab` (condition `intent` = **4** schedule)

**When to use:** Tenants that expect **Quartz** cron in a **six-field** pattern: `second minute hour day month weekday` (confirm whether `0`–`6` or `7` = Sunday with the platform).

| Natural language (example) | Example | Note |
| --- | --- | --- |
| Daily 22:30 | `0 30 22 * * ?` | Use `?` when day-of-month or weekday is unused |
| Mon–Fri 07:00 | `0 0 7 ? * 2-6` | Adjust numeric ranges to tenant rules |
| Sundays 09:00 | `0 0 9 ? * 1` | If Sunday = 1 in tenant mapping |
| Hourly | `0 0 * * * ?` | |
| 1st of month 00:00 | `0 0 0 1 * ?` | |

**Forbidden** for this subsection: **5-field-only** strings if the tenant requires six fields. If the user gave clock time only, pad **seconds** with `0`.

---

## Scene (action `intent` = **3** — run catalog scene)

Resolve `scene_name` / `scene_id` from the real scene list; fuzzy match rules in [`../scene-manage.md`](../scene-manage.md). Utterance shape "at time **T**, run scene **X**" → condition row **`intent` = 4** (schedule), action row **`intent` = 3** (scene execute).

---

## Device (condition **`intent` 1 / 2** or action **`intent` 1** — device control)

Match `device_name` / `device_id` to inventory; disambiguate by room on name clashes. `paramName` / `value` follow the resource model. **IR:** [`../automation-create.md#device-intent-ir-filter`](../automation-create.md#device-intent-ir-filter) — **forbidden** IR virtual keys in `cell_info` / `raw_config`; native capabilities only.

---

## Pack `raw_config`

Fill every Step 01 row (`intent`, `sub_query`, `sub_query_contain_position_name`, `position_id`, etc. — **must** carry over verbatim or merge with API resolution), then write `cell_info` per intent in this file (schedules, device/scene ids, `space_subject`, `weather_*`, etc.), serialized to the shape required by tenant **`automation/create`**. **Do not** drop rows; **do not** add rows unless allowed above. **Forbidden** to omit the `name` / per-row `sub_query` / `intent` / `sub_query_contain_position_name` / `position_id` keys listed in **[the previous section](#raw-config-required-fields)**.

**Order:** Step 02 finishes before Step 03. Step 03 runs only after a response that needs `LLMConfigReference` matching.
