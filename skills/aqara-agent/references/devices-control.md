# Device Control

## Goals

Handle requests like "turn on/off / adjust / change mode" by:

- Locating devices before controlling
- One response that states the outcome first, then detail
- If control cannot run, say why and what to do next

## Action Table (Attribute / Action / Value)

| attribute | action | value |
| --- | --- | --- |
| on_off | on,count,off,query | on,off |
| brightness | up,query,down,set | empty string, number, max, min |
| color_temperature | up,query,down,set | empty string, number, warm, cool |
| color | query,set | green,yellow,orange,purple,white,red,blue |
| online_offline | count,query | online,offline |
| ac_mode | query,set | empty string, heat, dry, cool, auto, fan |
| temperature | up,query,down,set | empty string, number, max, min |
| wind_speed | up,query,down,set | empty string, low_speed, min, max, medium_speed, high_speed |
| wind_direction | query,set | on,off,left_right,up_down |
| percentage | up,query,down,set | number |
| motion | set | stop |
| sweep | set | on,continue,off,stop |
| volume | up,down,set | empty string, number, max, min |
| play_mode | set | single_cycle,shuffle,order |
| play_control | set | play,previous,continue,stop,next |
| count | query | online,offline |

### Control Workflow

For utterances like "Turn on the living room lights and set the AC to 26°C":

1. **Split the request**
   - If several devices/actions, split into multiple sub-queries.
   - Each sub-query follows the control flow (or confirmation) on its own.
   - Example: "Turn on the bedroom light and turn off the living room AC" -> do bedroom light first, then living room AC.
   - Mixed intents: split in semantic order, then classify each sub-query as query vs control.
   - If a sub-query mixes **query + control**, run the query first, then control for that sub-query.

2. **Locate devices** from names or locations the user gave
   - Load home/room layout via `references/home-space-manage.md`.
   - Before control, load the current home's devices via `references/devices-inquiry.md`.
   - Extract room name, device name, device type from the query.
   - Device name only (e.g. "AC") -> call list-all-devices style data and fuzzy-match by name.
   - Location + device (e.g. "living room AC") -> homes -> rooms -> devices in that room.
   - If multiple matches, use `endpoint_id` from the device list to build `device_ids`.

3. **Map intent** to attribute / action / value
   - Use the action table above to fill slots: `attribute`, `action`, `value`.
   - If the device does not support the capability, say so clearly.

4. **Send command** - call the `device_control` API with a **JSON string**. Bash example:

```bash
python3 scripts/aqara_open_api.py device_control '{"device_ids":["device_id_1", "device_id_2"],"attribute":"brightness","action":"set","value":"30"}'
```

5. **Respond** - tell the user whether it succeeded.

## Auth Failure

- If control or prerequisite calls return **`unauthorized or insufficient permissions`**: treat as invalid token or insufficient permission - **must** follow `references/aqara-account-manage.md` to **re-login** and save a new token; do not pretend control succeeded.
