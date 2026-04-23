# Scene execute (catalog)

Run saved catalog scenes by natural language or explicit name. **Must** follow [`scene-manage.md`](../scene-manage.md) for session, execution order, cross-intent rules, and **[Scene name matching (shared)](../scene-manage.md#scene-name-matching-shared)**.

## Timed / delayed scene execution (routing)

Utterances classified as **scheduled scene control** or **delayed scene control** (time or schedule condition + run a **catalog** scene, **not** an immediate run): **Must** follow [`automation-create.md`](../automation-create.md) and **`post_create_automation`** — **Forbidden** this document’s **`post_execute_scene`** path as the primary solution, and **Forbidden** host-side timers that only defer **`post_execute_scene`**. Intent classification is open-ended (no fixed example sentence). See [`scene-manage.md`](../scene-manage.md#not-immediate-catalog-execute-routing).

## Explicit create / recommend intent

Use when the user **directly** asks to **create**, **design**, or **have you recommend** a scene for a situation (e.g. "help me create a scene that fits coming home", "recommend a bedtime scene", "set up a movie mode"), **not** only "run / execute scene X".

1. **Trigger** - **Must** treat as **scene recommend** path, **not** catalog execution-first, **unless** the utterance matches **Create scene** (e.g. "help me create a scene", "create a good-night scene in the bedroom") - **Must** follow **[Create scene](create.md)** instead of steps 7-8 in [Scene recommend workflow](recommend.md). For that persist path, **Must** honor **[Create scene - Location and room choice](create.md#location-and-room-choice-mandatory-before-planning)** (**Forbidden** default a room; **whole home** in the list **Must** lead to the documented follow-up so **`position_id`** is explicit).
2. **Rooms + scope** - **Must** `get_rooms` and resolve **whole home vs room** per **Location scope** below (step 3 under natural-language execution) when the path is **recommend / ephemeral device actions**; **Forbidden** run **[Scene recommend workflow](recommend.md)** on the wrong scope. **Create scene** path: **Must** satisfy **[Location and room choice](create.md#location-and-room-choice-mandatory-before-planning)** for **`position_id`** and for which devices may enter **`scene_data`** (**one room** after the user resolves **whole home** per that doc if applicable); **Forbidden** plan or call **`post_create_scene`** with a silently assumed room.
3. **Handoff** - If **not** **Create scene** intent: **Must** run **[Scene recommend workflow](recommend.md)** immediately after scope is clear. **Forbidden** `post_execute_scene` with invented `scene_ids`. **Optional:** if a same-named catalog scene obviously exists and user might have meant "run", **May** offer one short disambiguation ("Run existing scene X, or build new device actions?") - **Must not** skip the user's clear create/recommend intent.

## Workflow (natural-language execution - run existing catalog scene)

Use this when the user asks to **run** a scene in natural language (e.g. "help me run a homecoming scene", "goodnight scene in the bedroom"), **without** wording that is primarily **create / recommend** (see above), and **without** **[Timed / delayed scene execution](#timed--delayed-scene-execution-routing)** (if that applies, **Must** branch to **`automation-create.md`** first — **Must not** continue here for immediate execute).

1. **Trigger** - **Must** treat such utterances as **execute** intent under this reference (not device control until fallback below).
2. **Rooms** - **Must** fetch the current home's rooms via API (`get_rooms`; see `references/home-space-manage.md`).

   ```bash
   python3 scripts/aqara_open_api.py get_rooms
   ```

3. **Location scope** - **Must** determine whether the user **specified** a room or whole-home scope in the instruction.
   - If **not** specified (ambiguous scope) - **Must** list options and ask **one** clarification: **whole home** vs **which room** (use human-readable room names from step 2). **Forbidden** match or execute scenes until scope is resolved.
   - If already clear (e.g. "bedroom ...") - use that scope for matching.
4. **Scene list and match** - **Must** call `get_home_scenes`, then match the user's requested scene **name + room scope** against the returned list per **[Scene name matching (shared)](../scene-manage.md#scene-name-matching-shared)**.
5. **No catalog match** - If **no** scene qualifies after step 4 (no full match and no acceptable similarity hit, or user declines the fuzzy candidate):  
   - **Must** tell the user clearly that **no matching saved scene was found** (phrase in the user's locale as needed) - **conclusion first**, **Forbidden** imply a catalog scene ran. **May** briefly offer **2-5** closest catalog names from `get_home_scenes` as hints only.  
   - **Must** **immediately** continue into **[Scene recommend workflow](recommend.md)** for the **same** situational intent implied by the user's wording (e.g. good night, movie, reading) and the **same** location scope once step 3 is satisfied - **Forbidden** pause to ask whether they want AI actions; **Forbidden** require a second **affirmative** reply before starting recommendation.  
   - If step 3 **location scope** is **still unresolved**, **Must** finish that **one** clarification **first**; **Must not** start **[Scene recommend workflow](recommend.md)** until scope is explicit, then apply the bullets above if the catalog still has no match.  
   - **Forbidden** `post_execute_scene` with guessed `scene_ids`; **Forbidden** fabricate success.

## Execute matched scene

When a catalog scene matches (steps above), **Must** match **name + room** vs the latest `get_home_scenes` output using **[Scene name matching (shared)](../scene-manage.md#scene-name-matching-shared)**, then:

```bash
python3 scripts/aqara_open_api.py post_execute_scene '{"scene_ids":["scene_id_1","scene_id_2"]}'
```

- **Must** one unambiguous target unless user wants several.
- Collisions - **Must** one clarification; **Forbidden** guess and execute.

**Related:** [List scenes](list.md), [Create scene](create.md) (see [Location and room choice](create.md#location-and-room-choice-mandatory-before-planning)), [Scene recommend workflow](recommend.md), [Execution log](execution-log.md), [`scene-manage.md`](../scene-manage.md).
