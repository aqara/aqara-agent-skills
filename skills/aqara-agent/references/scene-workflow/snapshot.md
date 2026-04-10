# Scene snapshot

Use **only** when the user **clearly** requests a **scene snapshot** (capture current device states as a snapshot for a **room / position**). **Forbidden** run this path for catalog scene run, execution log, or **Scene recommend workflow** unless the utterance is explicitly about **snapshot**.

**Must** follow [`scene-manage.md`](../scene-manage.md) for session and cross-intent rules.

## Workflow

1. **Session** - **Must** valid `aqara_api_key` + `home_id` (`aqara-account-manage.md`, `home-space-manage.md`).
2. **Rooms** - **Must** fetch the current home's rooms:

   ```bash
   python3 scripts/aqara_open_api.py get_rooms
   ```

3. **Resolve room (position)** - **Must** parse the user's utterance for **which room(s)** to snapshot (names aligned with `get_rooms`).
   - **Closest name among similar rooms** - When the room list contains **nearby** names (e.g. `Bedroom`, `Bedroom 1`, `Bedroom 2`) and the user names a location, **Must** resolve to the **single closest** room name to what they said: prefer **exact** match first; if one name is a **prefix or strict substring** of another, prefer the **shortest / most specific match to the user's token** (e.g. utterance "create snapshot for Bedroom" + list has "Bedroom" and "Bedroom 1" - **choose `Bedroom`**, not `Bedroom 1`, unless the user explicitly said "Bedroom 1"). If two candidates remain equally plausible - **Must** one disambiguation question.
   - If **one** room clearly matches - build **`position_ids`** as a **one-element list** with that room's **position id** (internal only; from live JSON, e.g. `positionId`, `position_id`, `id`).
   - If **several** rooms are clearly requested and all resolve unambiguously - **`position_ids`** lists each resolved id (order not critical unless API says otherwise).
   - If **no** room is specified or scope is **ambiguous** - **Must** list **human-readable room names** from step 2 and ask **one** clarification. **Forbidden** call `post_scene_snapshot` until **`position_ids`** is non-empty and resolved.
   - **Whole home** snapshot: only if the user **explicitly** asks for whole-home snapshot **and** the platform supports passing the corresponding position id set; otherwise **Must** ask which room(s).

4. **Snapshot name (`snap_name`)** - **Required** in the API payload; **Must** never be empty or whitespace-only (**Forbidden** `snap_name` that normalizes to `""`).
   - **From query** - **Must** extract a short snapshot title from the user's wording when present (strip fixed phrases like "create scene snapshot", "scene snapshot", "please help", etc., and keep the meaningful fragment, e.g. "Living room arrival snapshot"). The **value sent to the API** after extraction **Must** be non-empty: if extraction yields nothing usable, **Must** use the localized default below (still non-empty).
   - **Default** when the user does not supply a usable name - zh locale - default string is applied by CLI for Chinese; for English (and other non-zh) - `scene snapshot`. The CLI wrapper applies the same default when `snap_name` is omitted or blank (`AQARA_DEFAULT_LOCALE`: unset or `zh*` uses Chinese default string in wrapper; else `scene snapshot`).

   Note: the literal default strings for `snap_name` are defined in `aqara_open_api.py` (Chinese vs English); this reference does not embed non-ASCII in examples. Set `AQARA_DEFAULT_LOCALE` as documented there.

5. **Create snapshot** - **Must** call `post_scene_snapshot` with JSON **`snap_name`** + **`position_ids`** (non-empty list of strings). Example:

   ```bash
   python3 scripts/aqara_open_api.py post_scene_snapshot '{"snap_name":"Living room snapshot","position_ids":["<room_position_id_from_get_rooms>"]}'
   ```

   Omitted `snap_name` - wrapper fills default per `AQARA_DEFAULT_LOCALE` rule in `aqara_open_api.py`. **Forbidden** empty **`position_ids`**.

6. **Reply** - **Must** summarize success/failure from the real response only; **Forbidden** raw internal ids in user text (**`SKILL.md`**). On **`unauthorized or insufficient permissions`**, **Must** `aqara-account-manage.md` then retry.

**Related:** [Create scene](create.md), [Scene execute](execute.md), [`scene-manage.md`](../scene-manage.md).
