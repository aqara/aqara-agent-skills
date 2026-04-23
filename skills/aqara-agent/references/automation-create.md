# Create automation

If the user is still in the **recommendation-style, example-sentence** phase (they have not yet chosen one complete rule sentence), **Must** complete steps 0-5 in [`automation-workflow/recommend.md`](automation-workflow/recommend.md) first; after they confirm an example sentence, continue from Step 1 in this document.

Use this document when the user **clearly** wants to **create** a new home automation (rule / routine).

**Create-automation routing (time-first flows):** When NL maps to **scheduled or delayed device control**, **scheduled or delayed scene control**, or anything with the same shape (time or schedule first, then devices or spatial targets such as lights / AC / curtains, or **catalog** scene execution semantics like **`post_execute_scene`**), treat it as **create automation** no matter the exact words: **Must** use **`post_create_automation`** here, resolve scenes with **`get_home_scenes`** (and related APIs), and use **automation-create-workflow** **action intent 3** for scene rows. **Forbidden** to replace that path with a host-only cron job, deferred `post_device_control`, or "run `post_execute_scene` later" as the main answer.

**Out of scope for this doc:** Listing only ([`automation-workflow/list.md`](automation-workflow/list.md)), toggle only ([`automation-workflow/toggle.md`](automation-workflow/toggle.md)), **immediate** catalog scene run only ([`scene-manage.md`](scene-manage.md) + [`scene-workflow/execute.md`](scene-workflow/execute.md)), **immediate** device control only, or edit / delete flows not documented in this skill (those **Must** use **Aqara Home App** or the referenced docs).

Session, execution order, and automation vs scene routing: **Must** follow [`automation-manage.md`](automation-manage.md).

---

## Prerequisites

- Valid `aqara_api_key` + `home_id` (see `aqara-account-manage.md`, `home-space-manage.md`).
- Before treating any **IDs** inside `raw_config` as final, **Must** resolve devices / rooms / scenes via real APIs (e.g. `get_home_devices`, `get_rooms`, `get_home_scenes`).
- **Existing automations:** **Must not** call **`get_home_automations`** (or otherwise list the home’s automations) **before** **`post_create_automation`** only to check for **name conflicts** or **“already exists”** — the platform **allows multiple automations with the same display** **`name`** to coexist. Use **`get_home_automations`** only when the user’s task is **list / toggle / logs** or they explicitly need to relate the new rule to **existing** automations; it is **not** a create prerequisite.

---

<a id="step-1-nl-split"></a>

## Step 1: Natural-language split (conditions / actions)

**Normative reference:** [`automation-create-workflow/step-01-conditions-actions-extract.md`](automation-create-workflow/step-01-conditions-actions-extract.md).

- **Manifest index:** [`automation-create-workflow/manifest.json`](automation-create-workflow/manifest.json): entry `conditions_actions_nl_parse`.
- **Output:** Structured rows: `conditions[]` / `actions[]` with `sub_query`, `intent`, `cell_info: {}`, relation fields, `name`, `execute_once`, etc.

<a id="step-2-cell-info"></a>

## Step 2: Fill `cell_info` and pack `raw_config`

**Normative reference:** [`automation-create-workflow/step-02-cell-info-fill.md`](automation-create-workflow/step-02-cell-info-fill.md).

- **Manifest index:** [`automation-create-workflow/manifest.json`](automation-create-workflow/manifest.json): entry `conditions_actions_cell_info_fill`.
- **Deliverable:** **`raw_config`** - a single `dict` used on **every** `post_create_automation` call (**Must** always be non-empty; see [Non-negotiable](#post-create-raw-config-always)). After Step 1 JSON has each row's `cell_info` filled by intent, normalize per tenant rules (resolved device/scene IDs, room/position fields, etc.) so the body matches the tenant **`automation/create`** "first payload / minimal try" shape; follow-up rounds **Must** reuse or carry a non-empty `raw_config` with the same business meaning per tenant rules.

<a id="raw-config-contract"></a>

### `raw_config` contract (summary)

- Holds everything the pipeline can derive **without** tenant trigger/execute **config-list disambiguation** (that layer is **`auxiliary_config`**).
- Any field that uses an **ID** **Must** come only from **real API** lists; **Forbidden** to invent IDs.

<a id="post-create-raw-config-always"></a>

### `post_create_automation` and `raw_config` (**non-negotiable**)

- **Every** call to `post_create_automation` (including the **first**, a **second** when `LLMConfigReference` requires follow-up, and **any** later retry or continuation) **Must** include **`raw_config`** in the request body, and **`raw_config` Must be non-empty** (do not omit the key; do not use `{}` as a substitute for "no business content").
- **Forbidden** to send only `auxiliary_config`, or a root body with **only** `conditions` / `actions` supplemental shapes **without** a non-empty `raw_config`; tenants often reject such calls.
- Host / agent when building the HTTP body: **Must** satisfy the above; if local wrappers (e.g. `scripts/aqara_open_api.py`) diverge from the tenant's latest contract, **Must** align the wrapper with the tenant Open API so **every** request has a non-empty `raw_config`.

<a id="step-3-post-create"></a>

## Step 3: `post_create_automation` - validate / create

Call the Open API wrapper (see `scripts/aqara_open_api.py`):

```python
api.post_create_automation(raw_config=raw_config)
# First call: omit auxiliary_config (None -> {}) or pass auxiliary_config={}
# Every call must satisfy the non-empty raw_config rule above; see raw_config contract / post_create_automation + raw_config (non-negotiable).
```

**Semantics:**

1. **First call (process rule; not necessarily runtime-enforced in code)** - **Must** send a **non-empty** **`raw_config`** (see **Non-negotiable** above); **`auxiliary_config` Must be empty**: omit the argument, or pass **`{}`** (same as `None` -> `{}` in `aqara_open_api.py`). **Forbidden** to send a non-empty `auxiliary_config` on the first call; hosts/agents obey this; `post_create_automation` may not enforce it at runtime. Retries: see Step 3 supplement below.
2. **Interpret the response** (HTTP status + JSON body; success / "needs more" **business codes are tenant-defined**):
   - **Terminal success** - e.g. returns an automation id, or business `code` means created; **stop**.
   - **Needs auxiliary configuration** - response indicates missing/ambiguous trigger or execute bindings, or asks to choose from a config list; **go to** [Step 3 supplement - `auxiliary_config`](#step-3b-auxiliary-config).
   - **Hard failure** - follow [`automation-workflow/failure-response.md`](automation-workflow/failure-response.md); **Forbidden** to fake success.

<a id="step-3b-auxiliary-config"></a>

## Step 3 supplement: `auxiliary_config` + second `post_create_automation`

Use this when the **first** Step 3 response needs **extra structured bindings** (usually trigger or execute rows tied to a tenant **config list**).

**Procedure (in order)**

1. **Config list source** - Treat **`LLMConfigReference`** in the response (or tenant-equivalent table / JSON) as Step 03 **`{config_list}`**. **Forbidden** to derive `triggerId`, `actionId`, or `params` for `auxiliary_config` by re-reading or stitching the first round **`raw_config` body**; Step 03 trusts **`LLMConfigReference`** only. Every HTTP round **Must** still include **non-empty** `raw_config` ([Non-negotiable](#post-create-raw-config-always)).
2. **Prompt + manifest** - Run [`automation-create-workflow/step-03-parse-config-prompt.md`](automation-create-workflow/step-03-parse-config-prompt.md) using **`LLMConfigReference`** fields only: **query**, **serialNum**, **queryType** (condition / action), and **configs**, for rows that still need completion (conditions only, actions only, or both). **Manifest:** `automation_auxiliary_config_match` in [`automation-create-workflow/manifest.json`](automation-create-workflow/manifest.json).
3. **Parse** - Model output **Must** `json.loads` to an **`auxiliary_config`** `dict` whose shape matches Step 03 (for example `conditions` / `actions` with `serialNum`, `query`, `configs`, `triggerId` / `actionId`, `params`).
4. **Second and later calls** - **Must** resend the same-meaning **non-empty** **`raw_config`** (typically the validated first-round payload or tenant-required minimum) **and** attach Step 03 **`auxiliary_config`** (or a tenant-valid merge per **`automation/create`**). **Forbidden** to send supplemental `conditions` / `actions` JSON **without** a non-empty `raw_config` at the root ([Non-negotiable](#post-create-raw-config-always)).

**Python example**

```python
from aqara_open_api import AqaraOpenAPI

api = AqaraOpenAPI()

# Outer JSON is tenant-specific; raw_config must stay non-empty.
first_payload = {"raw_config": {...}}

api.post_create_automation(raw_config=first_payload)
# If the response includes LLMConfigReference, run Step 03, then:
auxiliary_config = {"conditions": [...], "actions": [...]}

api.post_create_automation(
    raw_config=first_payload,
    auxiliary_config=auxiliary_config,
)
```

**Merge behavior (`scripts/aqara_open_api.py`)** - With both arguments, the wrapper **shallow-merges** into one HTTP body starting from `raw_config`. Keys such as `conditions` / `actions` from `auxiliary_config` are written **at the same level** without dropping `raw_config`. If the tenant needs different names or nesting, reshape `first_payload` before merge per Open API docs. Implementations **Must** never serialize only the supplemental object; every request **Must** include **non-empty** `raw_config` (or one merged body that still satisfies the contract).

5. **Retries and CLI** - Re-evaluate each response like Step 3. If still incomplete, **May** revise **`auxiliary_config`** and call again while keeping **non-empty** `raw_config`; recommend a **retry cap**. **CLI:** every body **Must** parse to JSON that includes **non-empty** `raw_config`; round two+ **Must** add Step 03 output or an equivalent merged payload; **Forbidden** to send only root-level `conditions` / `actions` without `raw_config`.

---

<a id="device-intent-ir-filter"></a>

## Device intents and IR filter

When **`raw_config`** (or merged body) still binds devices from NL rows: for **condition** intents **1 / 2** or **action** intent **1**, after candidates from `get_home_devices`, **Must** drop IR virtual endpoints: **exclude** any entry whose `deviceId` **starts with the `ir.` prefix**, then treat the list as final. If nothing remains, **Must** raise **`IRDeviceNotSupported`** (or equivalent) per product rules.

---

## End-to-end workflow

1. **Session** - `aqara_api_key` + `home_id`.
2. **[Step 1](#step-1-nl-split)** - NL split.
3. **[Step 2](#step-2-cell-info)** - Fill `cell_info`, validate IDs, **produce `raw_config`**.
4. **[Step 3](#step-3-post-create)** - `post_create_automation(raw_config=raw_config)`.
5. If needed, **[Step 3 supplement](#step-3b-auxiliary-config)** - follow **`LLMConfigReference`** through Step 03 to **`auxiliary_config`**.
   - **Abort** if Step 03 yields **empty** or invalid `auxiliary_config` (including no valid `conditions` / `actions` / `configs`), mapping is impossible, or a **condition / action** is **unsupported** in the config table with no legal fill; explain to the user; **Forbidden** to spin `post_create_automation` on empty or invalid supplemental payloads.
   - **Otherwise**, when `auxiliary_config` is **non-empty**, matches **`LLMConfigReference`**, and self-check passes, call `post_create_automation` again with **non-empty** `raw_config` + **`auxiliary_config`** ([Non-negotiable](#post-create-raw-config-always)).
6. **User-facing reply** - **Must** follow [User-facing reply after create (unified rules)](#create-complete-user-reply); except where product rules allow, **Forbidden** to dump raw IDs in user text; hard-failure phrasing also see [`automation-workflow/failure-response.md`](automation-workflow/failure-response.md).

---

<a id="create-complete-user-reply"></a>

## User-facing reply after create (unified rules)

After the full **`post_create_automation`** flow ends (**terminal** state, including after any auxiliary rounds), the user-visible reply **Must** follow the table below; also satisfy [`automation-manage.md`](automation-manage.md) and [`SKILL.md`](../SKILL.md) ("conclusion first", **Forbidden** raw ids in user text, etc.).

| Terminal state | User-visible reply |
| --- | --- |
| **Create failed** | **Only** the **failure reason** (one or more sentences allowed, but **Must not** imply success, repeat the pipeline, show script paths, raw JSON, device / automation **IDs**, or other noise). Reasons **Must** come from **real** API errors / business `message`, or readable text from this doc and [`automation-workflow/failure-response.md`](automation-workflow/failure-response.md). **Forbidden** in failure cases to list "triggers / actions" or success-style wording. |
| **Create succeeded** | See **Success structure** below (this row is an index only). |

**Success structure**

1. **First sentence (required)** - **Must** use an affirmative pattern: **"xxx" was created successfully** (or the user's locale). **`xxx` Must** be the automation **display name**: prefer top-level **`name`** in `raw_config` (consistent with Step 01-02); if the API omits it but a stable local `name` exists, reuse it. **Forbidden** to reply with only "Done" / "Created" **without** a distinguishing rule name.
2. **Triggers (required, separate block)** - **Must** list: in **`conditions[]`** order, one plain-language summary per row (may match each **`sub_query`** or be lightly polished). For multiple rows, list bullets only; **need not** explain **`conditions_relation`** to the user (do not spell out AND/OR connectors for relation alone).
3. **Actions (required, separate block)** - **Must** list: in **`actions[]`** order, one plain-language summary per row. Same as above for **`actions_relation`**.

**Forbidden on success:** Long preamble before "xxx was created successfully"; invent conditions or actions not present in the finalized **`raw_config`** (and tenant-accepted semantics after auxiliary rounds); expose `deviceId`, `position_id`, `automation_id`, etc. to the user (same as [`SKILL.md`](../SKILL.md) **Notes**).

---

## Failure handling

- **`unauthorized or insufficient permissions`:** **Must** follow [`aqara-account-manage.md`](aqara-account-manage.md).

---

## Related documents

- [`automation-manage.md`](automation-manage.md)
- [`automation-workflow/recommend.md`](automation-workflow/recommend.md)
- [`automation-workflow/list.md`](automation-workflow/list.md), [`automation-workflow/toggle.md`](automation-workflow/toggle.md), [`automation-workflow/failure-response.md`](automation-workflow/failure-response.md)
- [`automation-create-workflow/manifest.json`](automation-create-workflow/manifest.json)
