# Scene Management (index)

This file is the **entry point** for all scene-related agent behavior. **Normative detail** is split under **`references/scene-workflow/`**; open the workflow that matches the user's intent. **Must** still satisfy **`SKILL.md`** ground truth (scripts + real API output only).

**Pattern:** **Scene recommendation** (execute now) and **scene creation** (persisted card) both use **`device_status_control`**: **`post_device_status`**, then **`post_device_control`** (recommend path) or **`scene_data`** + **`post_create_scene`** (create path). See [Scene recommend workflow](scene-workflow/recommend.md#device-status-control-device_status_control).

## Not immediate catalog execute (routing)

**Scheduled scene control** and **delayed scene control** (time or clock condition + run an **existing catalog scene**, and **not** immediate **`post_execute_scene`**): whenever NL / intent falls here, semantically this is equivalent to **creating an automation** (action is scene execution; see **`automation-create-workflow`** action intent **3** and [`automation-create.md`](automation-create.md)), **Must** **go straight to** [`automation-create.md`](automation-create.md), **Forbidden** to replace the primary path with the immediate flow in [`scene-workflow/execute.md`](scene-workflow/execute.md) or host timers that only defer `post_execute_scene`. Wording is not limited to fixed example sentences; classify by whether intent falls in the above category.

## Scene name matching (shared)

**Shared business rules** for resolving a user's **scene name** to catalog entries from the latest **`get_home_scenes`** (within the resolved **room / whole-home** scope). **Must** apply the same rules when matching for **scene execute (catalog)**, **execution log** (`scene_ids` resolution), or any other flow that maps NL to catalog scene names.

1. **Full match first** - **Must** try **exact / full-name** match first: catalog **scene name** equals the user's intended name (after consistent normalization only, e.g. trim spaces; do not silently rename).
2. **No full match** - **Must** then apply **generalized matching**: among catalog names still in scope, pick the entry with the **highest similarity** to the user's wording (semantic / embedding, synonym rules, edit distance, or a fixed combination; **Must** stay consistent in one session). **Example (illustrative):** "dusk" and "sunset" may be treated as **~95%** similar, so a user asking for a "dusk" mood **May** match a catalog scene named "Sunset scene" when no **full** match exists and that candidate ranks highest.
3. **Ties and ambiguity** - If **several** candidates share the top score or the best score is below your confidence threshold, **Must** **one** clarification (list **2-5** human-readable catalog names); **Forbidden** `post_execute_scene` (or any execute) on a guess.
4. **Appendix** - Use **[NL to canonical scene name hints (examples)](scene-workflow/appendices.md#nl-to-canonical-scene-name-hints-examples)** for NL to canonical name hints; **May** combine with similarity scoring. **Forbidden** invent catalog names not present in the last `get_home_scenes` response.

---

## Contents (split references)

| Topic | File |
| --- | --- |
| **Scene name matching (shared, this file)** | [Scene name matching](#scene-name-matching-shared) |
| List catalog scenes | [scene-workflow/list.md#catalog-list](scene-workflow/list.md#catalog-list) |
| Scenes linked to devices | [scene-workflow/list.md#scenes-by-device](scene-workflow/list.md#scenes-by-device) |
| Run saved scenes (NL + name match + execute) | [scene-workflow/execute.md](scene-workflow/execute.md) |
| Situational recommend / AI device plan + control | [scene-workflow/recommend.md](scene-workflow/recommend.md) |
| Outdoor weather (`post_current_outdoor_weather`, leaving-home only) | [weather-forecast.md](weather-forecast.md) |
| Persist new scene (`post_create_scene`) | [scene-workflow/create.md](scene-workflow/create.md) |
| Scene snapshot | [scene-workflow/snapshot.md](scene-workflow/snapshot.md) |
| Scene execution log | [scene-workflow/execution-log.md](scene-workflow/execution-log.md) |
| Failure + user-facing response | [scene-workflow/failure-response.md](scene-workflow/failure-response.md) |
| **Scene recommend — user-facing reply (index rule)** | [User-facing reply: scene recommend path](#user-facing-reply-scene-recommend-path-mandatory) + [recommend.md step 8](scene-workflow/recommend.md#execution-steps) |
| Name lists + NL hints | [scene-workflow/appendices.md](scene-workflow/appendices.md) |

---

## Intents (routing)

- **Scheduled / delayed scene control** (time or clock + run catalog scene, not immediate) → [`automation-create.md`](automation-create.md) (`post_create_automation`); **Must not** prefer the immediate [execute.md](scene-workflow/execute.md) path. Routing overview: [`automation-manage.md`](automation-manage.md).
- List/discover scenes - [list.md#catalog-list](scene-workflow/list.md#catalog-list).
- Scenes involving a device - [list.md#scenes-by-device](scene-workflow/list.md#scenes-by-device).
- Run catalog scene (NL or explicit) - [execute.md](scene-workflow/execute.md).
- **Create / recommend by situation** - If persist card: [create.md](scene-workflow/create.md). Else after scope: [execute.md](scene-workflow/execute.md) (explicit create/recommend) + [recommend.md](scene-workflow/recommend.md).
- **Create scene** (persisted) - [create.md](scene-workflow/create.md).
- **Scene snapshot** - [snapshot.md](scene-workflow/snapshot.md).
- Execution history - [execution-log.md](scene-workflow/execution-log.md).

---

## Execution order

1. **Session:** **Must** `aqara_api_key` + `home_id` (`aqara-account-manage.md`, `home-space-manage.md`).

2. **Catalog run (default):** **Must** list (`get_home_scenes`) before **catalog** run; **Must** match run target against latest list. For **natural-language run** without a clear room/whole-home scope, **Must** complete **Scene execute** steps 2-4 (rooms, scope, scenes) in [execute.md](scene-workflow/execute.md) before `post_execute_scene`.

   **Exceptions:**

   - **Create / recommend** (situational): **Must** branch once scope is resolved; **Must not** block on finding a catalog scene first.
   - **Create scene** (persisted): **Must** follow [create.md](scene-workflow/create.md) (not catalog run).
   - **Scene snapshot:** **Must** follow [snapshot.md](scene-workflow/snapshot.md); **Must not** require `get_home_scenes` first.

3. Multi-intent: utterance order; query + execute - **Must** query first.

4. Device to scenes: **Must** `get_home_devices`, then `device_ids`, then `post_scene_detail_query`; **Forbidden** invent/paste ids without list step. See [list.md#scenes-by-device](scene-workflow/list.md#scenes-by-device).

5. **Persisted scene authoring** - **Allowed** only **`post_create_scene`** per [create.md](scene-workflow/create.md). **Forbidden** ad-hoc scene edit/delete via undocumented APIs. For **scene recommendation** (immediate effect), **Must** complete **`device_status_control`** in [recommend.md](scene-workflow/recommend.md) steps 5-7 when **not** using the **Create scene** persist path.

---

## User-facing reply: scene recommend path (mandatory)

Applies whenever the business path is **scene recommendation** ([recommend.md](scene-workflow/recommend.md))—including **Path A** handoff from [execute.md](scene-workflow/execute.md) when **no** catalog scene matched, **Path B** explicit create/recommend (execute-now branch), or any situational branch that ends with **`post_device_control`** under **`device_status_control`** instead of **`post_execute_scene`**.

**Forbidden** (on this path only): Replies that **mimic a catalog scene card** or a generic **`post_execute_scene`** success template, for example:

- A headline-only "scene executed successfully" / "good night scene ran successfully" **without** per-device detail.
- A **“scene details”** block that only states a **user- or model-invented scene title**, **location**, and an echoed generic API line such as **“Scene run successfully”** (or equivalent) **as the sole outcome**.
- Vague closings like “lights should already be in sleep / reading mode” **when** the user-visible text **does not list which endpoints were controlled and how** (must follow the rule below instead).

**Must** satisfy [recommend.md](scene-workflow/recommend.md) **step 8 — User-facing reply** after **`post_device_control`** (and step-7 **Leaving home** weather summary when applicable): **conclusion first**, then a **brief, explicit list** of **each device that was actually acted on**—using **human-readable** **position (room) + endpoint name or device name** from the latest **`get_home_devices`** / **`post_device_status`** pass—and **plain-language (or compact attribute / action / value) description of each control** (e.g. off, brightness set to ~70%, curtain to X%). **Must** align **only** with commands that **succeeded** per API; **Must** state partial failures the same way. **Forbidden** raw `endpoint_id` / `device_ids`, shell transcripts, or full JSON; **Forbidden** claim devices or actions not in the executed plan.

**Contrast:** A genuine **catalog** run via **`post_execute_scene`** is **not** scene recommendation; its user-facing success wording follows **`SKILL.md`** and [execute.md](scene-workflow/execute.md) and **may** briefly name the **matched catalog scene** plus truth from API—**Must not** substitute that short catalog-style confirmation for the **per-device list** required above when the path was **recommend**.

---

## Intent routing (quick)

| User goal | Read | Primary tool(s) |
| --- | --- | --- |
| List catalog scenes | [list.md#catalog-list](scene-workflow/list.md#catalog-list) | `get_home_scenes` |
| Scenes tied to a device | [list.md#scenes-by-device](scene-workflow/list.md#scenes-by-device) | `post_scene_detail_query` |
| Run a **saved** scene | [execute.md](scene-workflow/execute.md) | `get_rooms`, `get_home_scenes`, `post_execute_scene` |
| Situation create/recommend, **execute now** | [recommend.md](scene-workflow/recommend.md) | `get_home_devices`, **`device_status_control`**, `post_current_outdoor_weather` (leaving-home only, before first control) |
| **Persisted** create scene | [create.md](scene-workflow/create.md) | recommend steps 1-6 pattern + `post_create_scene` |
| **Scene snapshot** | [snapshot.md](scene-workflow/snapshot.md) | `get_rooms`, `post_scene_snapshot` |
| Scene run history | [execution-log.md](scene-workflow/execution-log.md) | `post_scene_execution_log` |

---

## After you pick a workflow

1. Open the linked **`scene-workflow/*.md`** file.
2. Run `scripts/aqara_open_api.py` (and other scripts) as documented there.
3. On errors or user-facing rules, see [failure-response.md](scene-workflow/failure-response.md) and **`SKILL.md`**.
