# Ambience (mood orchestration)

Match **saved scenes** first; else **composite**: target-scope **all lights off**, then **`post_device_control`** (mood, power on, dim / CT / color) **in parallel with** optional **`music_on_demand`**, then **`get_home_lighting_effects_query`**, then **`post_lighting_effect_control`**. Distinct from thin scene-only (`scene-manage.md`) and generic control (`devices-control.md`).

**Routing:** Classify **`ambience_create`** when the user **applies or creates** a named mood for a **room** or **whole home**. **Must** run **[Workflow](#ambience-workflow)**. **List or thin single-preset only** goes to **[Fast path](#fast-path-lighting-preset-inquiry-only)** (not `ambience_create`). **Forbidden** to treat `ambience_create` as presets plus **`post_device_control`** alone.

**Skill:** **`SKILL.md`**, row **Ambience create** (`ambience_create`).

**Contracts to API:** `scene_base_inquiry` maps to **`get_home_scenes`** (+ **`post_scene_detail_query`**). **`fuzzy_device_batch_control` is only Sec. 4b:** batch **`post_device_control`** to turn lights **off** in target `position_id`(s); **Forbidden** any other use. **`mood_device_batch_control` is Sec. 4c:** batch **`post_device_control`** from **`MOOD_PRESETS`**. **`music_on_demand`** is product audio (may be non-OpenAPI).

**IDs:** Use **`home-space-manage.md`**, **`get_rooms`**, **`get_home_devices`** / **`devices-inquiry.md`**. **Forbidden** to pass unchecked natural language as JSON ids.

---

<a id="lighting-effect-agent"></a>

## LightingEffectAgent (aligned with Workflow)

- **Tools:** Ambience, execution, and lamp control **Must** call real Open APIs; **Forbidden** to claim ambience is applied without tool calls. **Persisted scene save** APIs **Must** run only when the user **explicitly** asks to save (e.g. "save", "save as a scene", or equivalent); otherwise **Must not** call them; if the user asked to save, **Forbidden** to report success by voice only. **Save path:** **`post_create_scene`** with JSON built only from **[Save scene payload](#save-scene-payload)** in this file (same fields the Open API expects); **Must** invoke it directly (e.g. `python3 scripts/aqara_open_api.py post_create_scene '<json>'`). **Forbidden** to require opening or following **`references/scene-workflow/create.md`** for this ambience-save flow—the contract here is sufficient. Name mapping: **`scene_run`** to **`post_execute_scene`**; **`device_status_control`** to **`post_device_control`**; **`lighting_effect_control`** to **`post_lighting_effect_control`** (after **`get_home_lighting_effects_query`**); **`device_status_inquiry`** to device queries in **`devices-inquiry.md`**; other scene catalog / run flows remain in **`scene-manage.md`** / **`scene-workflow/`** (do not confuse persisted save with **`post_execute_scene`**).
- **`exist_light`:** After scope is fixed and before lamp control, use the device list to see if any controllable lights exist; if **false**, tell the user in their language that there are no lights and **stop**.
- **Rooms:** Lamp **`post_device_control`** and **`post_lighting_effect_control`** only under **`position_id`(s)** from **Sec. 1**. Offer only rooms that have lights; if exactly **one** lit room, **May** auto-select; if several lit rooms and the user named none, **Must** ask for a room first (optional ambience-based hints; if weak link, list all lit rooms). If mood is missing, **May** prompt; **Must** ask at most **one** critical missing field per turn.
- **Scenes (Sec. 3):** Filter inside the user scope; **`ambience_name`** vs **`scene_name`** semantic match, default **>= 0.85**; if several pass, take **highest score with position scope matching** the user scope, then **`post_execute_scene`** and stop.
- **Composite (Sec. 4):** Order **4b lights off** to **4c** numeric / switch (**Must** use **`post_device_control`** for brightness, CT, color; **Forbidden** to replace that with the lighting-effect API) to **4d** to **4e**: if a valid **`effect_name`** exists, **Must** call **`post_lighting_effect_control`**; else **May** skip 4e and explain. **Before lighting effect:** for each lamp that gets an effect, **Must** turn it **on** first, then **`post_lighting_effect_control`**.
- **Relative wording:** "Too" bright or dark implies a single step of at least **30** (within device limits); "a bit" implies at least **15**. "Coldest / warmest color temperature" means **min / max** CT in the device range per CSV; **Forbidden** to invert meaning.
- **Groups and space:** Same prefix plus serial suffix often means group members; "light group", "membrane group", or prefix-only often means the group entity; **Should** cover the whole group semantically. After the user fixes a location, **Must** keep using it until they change it. Zone phrases (e.g. TV wall) apply to **all** relevant lamps there; rainbow on color membranes means **ordered** color steps.
- **`{atmosphere_knowledge}`:** Injected at runtime by product or agent config, not static text in this repo.
- **Choice template (translate `label` to the user language; `value` is fixed):** focus, cinema, lively, candle, relax, cozy, bright, sleep (map any localized label to these keys as needed).
- **Replies:** Before the first tool call, **Must** send a short ack in the user language (e.g. "Okay"); the full reply **Must** stay in the user language; do not switch language because tool strings are in another locale.
- **Save (after explicit ask):** Collapse to **final** parameters (last brightness wins); poetic **`scene_name`** plus a success line in the user language (e.g. "Scene **xxx** saved"). Build **[Save scene payload](#save-scene-payload)** and call **`post_create_scene`** immediately; **Must not** treat **`references/scene-workflow/create.md`** as a prerequisite read for this step.
- **Copy A to B:** Read A lamp state, then **`post_device_control`** on B for switch, brightness, CT, color, then **`post_lighting_effect_control`** if needed.
- **Data:** Follow **`user_account.json`**, `home-space-manage.md`, and product privacy; **Forbidden** to leak tokens or raw ids.

---

<a id="save-scene-payload"></a>

### Save scene payload (`query`: save scene)

**When:** After the user **explicitly** asks to save (not the same as **`post_execute_scene`**), build this structure and call **`post_create_scene`** with it—**self-contained in this doc**; **Forbidden** to mandate loading **`references/scene-workflow/create.md`** for the save step. **`scene_name`**, **`position_id`** (single room), and **`scene_data`** must still be resolved from live **`get_rooms`** / **`get_home_devices`** / status as needed; slot rules use **`device_control_action_table.csv`**.

| Top-level | Meaning |
| --- | --- |
| **`scene_name`** | Short or poetic name shown to the user. |
| **`position_id`** | Single-room platform `position_id` (multi-room behavior is product-defined: multiple calls or multiple `scene_data` rows). |
| **`scene_data`** | Array of blocks; each block applies one **`slots`** list to many devices (**final** state, not intermediate steps). |

**Each `scene_data[]` item**

| Field | Meaning |
| --- | --- |
| **`device_ids`** | String array; devices that share the same **`slots`** may appear in one row. |
| **`slots`** | List of attribute actions for that batch; **`attribute`**, **`action`**, **`value`** must match **`device_control_action_table.csv`** and platform effect names. |

**Common `slots[].attribute` for lamp ambience**

| `attribute` | `action` (examples; follow product and CSV) | `value` |
| --- | --- | --- |
| `on_off` | `on` or `off` | Often empty string `""` |
| `brightness` | `set`, `up`, ... | Target or step as a string |
| `color` | `set` | Color literal allowed by the platform |
| `color_temperature` | `set`, `warmer`, ... | Number or `""` |
| `lighting_effect` | `set` | Platform **`effect_name`** (must match a name validated via **`get_home_lighting_effects_query`**) |

**Example (valid JSON; real `action` sets follow product enums)**

```json
{
  "scene_name": "summarized_scene_name",
  "position_id": "position_id",
  "scene_data": [
    {
      "device_ids": ["xx1", "xx2", "xx100"],
      "slots": [
        { "attribute": "on_off", "action": "on", "value": "" },
        { "attribute": "brightness", "action": "set", "value": "30" },
        { "attribute": "color", "action": "set", "value": "#ff702d" },
        { "attribute": "color_temperature", "action": "set", "value": "2700" },
        { "attribute": "lighting_effect", "action": "set", "value": "Movie" }
      ]
    }
  ]
}
```

- **Must:** for each **`scene_data`** entry, **`slots`** is the **final** snapshot for that **`device_ids`** list (e.g. if brightness was 15 then 30, keep **30** only).
- **May:** multiple **`scene_data`** rows when different device groups need different **`slots`**.

---

<a id="ambience-workflow"></a>

## Workflow (ordered)

### 1. `ambience_name` + `position_id`(s)

| Field | Rule |
| --- | --- |
| `ambience_name` | From user; **May** map to **`MOOD_PRESETS`** key; keep original string for scene and effect matching. |
| `position_id`(s) | Map NL to id via **`get_rooms`**. If there is **no** room phrase and **no** explicit whole-home phrase: **Must** list positions (numbering **recommended**), user picks **one, several, or whole home** before Sec. 2-4; **Forbidden** silent default. **Whole home** means all room ids from that **`get_rooms`**. **Forbidden** unchecked NL ids. **Agent:** room list **Should** filter **`exist_light`**; exactly **one** lit room **May** auto-pick. |

**Synonyms** apply end-to-end: presets, **`scene_name`**, per-position effect names after **`get_home_lighting_effects_query`**, using semantic match; HTTP bodies use **platform-exact** strings and CSV enums.

### 2. `scene_base_inquiry`

**Must** run **`get_home_scenes`** (`scene-manage.md`, `scene-workflow/list.md`). **May** run **`post_scene_detail_query`**. Output at least: `scene_id`, `scene_name`, scope / `position_id`.

### 3. Scene match, early exit

Filter to user scope; score **`ambience_name`** vs **`scene_name`** (document **>= 0.85** default in code). **Tie-break:** highest score among rows whose **position scope matches** the user target **`position_id`(s)** exactly, then **`post_execute_scene`**, then **[Result](#result)** with `applied_path: scene_direct`, then **stop**. Else go to Sec. 4.

### 4. Composite (no qualifying scene)

**4a `MOOD_PRESETS`** -- Agent table: drives **`mood_device_batch_control`**, optional **`lighting_effect`**, **`music_on_demand`**. Brightness, CT, color only via **`post_device_control`**; named preset only in 4e.

**4b** -- **`fuzzy_device_batch_control`:** all lights **off** in Sec. 1 **`position_id`(s)** via **`post_device_control`** (**Forbidden** to skip; **Forbidden** to turn off lights outside target scope); **await**; record **`target_scope_lights_off`** in Result.

**4c** -- **`mood_device_batch_control`** in parallel with **`music_on_demand`** (after 4b). Batch **`post_device_control`**: lights **on**, mood fields, other devices per CSV; **Forbidden** **`post_lighting_effect_control`** in this step.

**4d** -- **Await** both 4c branches.

**4e** -- After 4c-4d: **`get_home_lighting_effects_query`**, match `effect_name` per position (synonyms), then **`post_lighting_effect_control`**. **Forbidden** `effect_name` not listed for that position. **`device_ids` vs `position_ids`:** if both are sent, OpenAPI prefers **`device_ids`**. **May** omit if no match; tell the user if a synonym label was applied (no raw ids in user text).

**`MOOD_PRESETS` sample (production effect strings come from the platform; `lighting_effect` must match `get_home_lighting_effects_query`):**

```python
MOOD_PRESETS = {
    "cozy": {"on_off": "on", "brightness": 45, "color_temp": 2700, "color": "#ffebc8", "lighting_effect": "Cozy"},
    "movie": {"on_off": "on", "brightness": 10, "color_temp": 1900, "color": "#ff702d", "lighting_effect": "Movie"},
    # Add other moods with the same shape.
}
```

---

<a id="result"></a>

## Result

Structured JSON for the orchestrator; user-facing text **outcome-first**; **Forbidden** raw ids unless the product allows.

| Field | Meaning |
| --- | --- |
| `applied_path` | `scene_direct` or `composite` |
| `exist_light` | Optional: target scope had controllable lights |
| `ambience_name`, `position_scope`, `user_summary` | Strings |
| `scene` | If Sec. 3: `{ scene_name, executed }` (ids stay internal) |
| `parallel` | `{ mood_device_batch_control, music_on_demand }`, each `{ ok, error? }` |
| `target_scope_lights_off` | Composite 4b: `{ ok, error? }` |
| `lighting_effect` | 4e: `{ ok, effect_name_applied?, error? }` |

**Partial failure:** reflect in **`user_summary`** and per-field **`error`**; **Forbidden** to claim full success when a required step failed.

---

<a id="fast-path-lighting-preset-inquiry-only"></a>

## Fast path: lighting preset inquiry only

- List home presets: `python3 scripts/aqara_open_api.py get_home_lighting_effects_query`
- Per device: `python3 scripts/aqara_open_api.py post_device_lighting_effect_query '{"device_ids":[...]}'`
- **Thin apply one preset:** **Must** run **`get_home_lighting_effects_query`** immediately before **`post_lighting_effect_control`**; `effect_name` must appear in that response only.

---

## Auth and related

`aqara_api_key` and home header context: **`home-space-manage.md`**. **Related:** `scene-manage.md`, `scene-workflow/*` (list / execute / snapshot / logs, etc.—**not** required reading for ambience **save → `post_create_scene`**), `devices-control.md`, `assets/device_control_action_table.csv`, `devices-inquiry.md`.
