# Step 03 - Config list to `auxiliary_config`

**Sources:** **`LLMConfigReference`** (or tenant `config_list`) is the **only** source for rows: **query**, **serialNum**, **queryType** (condition / action), **configs**. **Forbidden:** derive `triggerId` / `actionId` / `params` from the first round **`raw_config` body** (no logical dependency on rereading it). **Every** `post_create_automation` still ships **non-empty** `raw_config` ([`../automation-create.md#post-create-raw-config-always`](../automation-create.md#post-create-raw-config-always)); round 2+ adds this step's **`auxiliary_config`** (or tenant merge) per [`../automation-create.md#step-3b-auxiliary-config`](../automation-create.md#step-3b-auxiliary-config).

**Output:** One JSON object parseable by `json.loads` -> **`auxiliary_config`** (typically root `conditions` / `actions`). **Forbidden:** follow-up HTTP with only this object and no **non-empty** `raw_config`.

`post_create_automation(raw_config=raw_config, auxiliary_config=auxiliary_config)`

**When:** First create response needs config-list matching. Before manifest **`automation_auxiliary_config_match`**. Index: [`manifest.json`](manifest.json).

---

## Pre-flight

- [ ] Table rows / IDs come **only** from **`LLMConfigReference`** (or equivalent); **forbidden** invented `triggerId` / `actionId`.
- [ ] Host injects **`{config_list}`** from that reference; **`{output_format}`** when overriding shape. **query** and **serialNum** align with reference rows, **not** back-filled from `raw_config`.
- [ ] Model returns **JSON only** (no fences, no prose). After parse, call API with **non-empty** `raw_config` **plus** `auxiliary_config`.

---

## Host placeholders

| Token | Role |
| --- | --- |
| `{config_list}` | Parsed trigger/execute list (same fields as API) |
| `{output_format}` | Optional stricter schema / notes; see example below |

---

## `{output_format}` example (shape only)

Valid `json.loads`; use JSON **`null`** for absent `paramEnum`. IDs and copy **must** come from the live **`LLMConfigReference`** for this round, **not** from this sample.

```json
{
  "conditions": [
    {
      "serialNum": 1,
      "query": "At sunset in Haidian District, Beijing",
      "configs": [
        {
          "triggerName": "At sunset",
          "triggerId": "1",
          "params": [
            {
              "paramUnit": "",
              "paramId": "PD.cityId",
              "paramName": "City",
              "value": "Haidian District, Beijing",
              "paramEnum": null
            }
          ]
        }
      ]
    }
  ],
  "actions": [
    {
      "serialNum": 1,
      "query": "Security hub: turn off alarm",
      "configs": [
        {
          "actionId": "2",
          "actionName": "Turn off alarm"
        }
      ]
    }
  ]
}
```

---

## LLM prompt template

Concatenate with `{config_list}`, optional `{output_format}`, and any host constraints, then send:

```text
You match smart-home automation triggers and actions to a fixed config list and return one JSON object.

Goals:
- Pick triggers only from list trigger rows; actions only from list execute rows. Never invent rows.
- Normalize synonyms ("close" / "turn off"; "someone" / "motion") when the list supports a single target.
- Cover every user-mentioned condition and action; each becomes one element in `conditions` / `actions` with its own `configs` array (empty `configs` if nothing fits, unless host says otherwise).
- Params: use user text first, else list default; omit params when the list row has none.

Procedure:
1) For each reference `query`, best semantic match to list configs; do not use positionName as the primary key.
2) For each matched config, fill params in order: user value, then default.

Hard rules:
- triggerId, actionId, triggerName, actionName must be exact strings from the list.
- ASCII JSON only: double-quoted keys, normal commas; no comments, no Markdown, no extra text outside the JSON.
- json.loads must succeed on the entire model output once.
- One best matching config per `query` in `configs` unless the tenant marks a device trigger with duplicate same-name rows you cannot split: then you may return multiple list rows that all fit.

Heuristics:
- Door + motion may both appear for "someone opened the door"; spotlight "turned on" -> on-edge for those lights; alarm fired -> hub alarm template; curtains opening -> list's curtain-open template.
- "All AC on/off" -> list's AC on/off templates.
- Notifications: one template - generic push vs custom body vs alert/SMS per list semantics and user text.
- If `{output_format}` is provided, obey it; else use: root `conditions` and `actions` arrays; each item has serialNum (int), query (str), configs (array). configs entries: triggers use triggerName, triggerId, params (array or []); actions use actionId, actionName, params. params objects include paramUnit, paramId, paramName, value (string), paramEnum (object or null) exactly as the list defines.
```

---

## Output shape (host validation)

Placeholder types; real names and params follow tenant `config_list`.

```json
{
  "conditions": [
    {
      "serialNum": 0,
      "query": "",
      "configs": [
        {
          "triggerName": "",
          "triggerId": "",
          "params": [
            {
              "paramUnit": "",
              "paramId": "",
              "paramName": "",
              "value": "",
              "paramEnum": {}
            }
          ]
        }
      ]
    }
  ],
  "actions": [
    {
      "serialNum": 0,
      "query": "",
      "configs": [
        {
          "actionId": "",
          "actionName": "",
          "params": [
            {
              "paramUnit": "",
              "paramId": "",
              "paramName": "",
              "value": "",
              "paramEnum": {}
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Linkage

- No NL re-split; selections live **only** inside **`LLMConfigReference`**. **`serialNum`** / **query** stay aligned with that reference for the tenant session. Round 2+ HTTP: **non-empty** `raw_config` + this **`auxiliary_config`** (merge per tenant / [`../automation-create.md#step-3b-auxiliary-config`](../automation-create.md#step-3b-auxiliary-config)).
