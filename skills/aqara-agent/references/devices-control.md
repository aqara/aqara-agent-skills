# Device Control

## Goal

**Must** locate devices before control. **Must** user-facing: outcome first; zh users: success = affirmative + location + device + outcome; failure = short `{location}{device} control failed` (or omit location if unknown). **Must** add auth/next steps only when required (`Auth failure`, end of reply patterns).

## Action Table

| attribute | action | value |
| --- | --- | --- |
| on_off | on,count,off,query | on,off |
| brightness | up,query,down,set | empty, number, max, min |
| color_temperature | up,query,down,set | empty, number, warm, cool |
| color | query,set | green,yellow,orange,purple,white,red,blue |
| online_offline | count,query | online,offline |
| ac_mode | query,set | empty, heat, dry, cool, auto, fan |
| temperature | up,query,down,set | empty, number, max, min |
| wind_speed | up,query,down,set | empty, low_speed, min, max, medium_speed, high_speed |
| wind_direction | query,set | on,off,left_right,up_down |
| percentage | up,query,down,set | number |
| motion | set | stop |
| sweep | set | on,continue,off,stop |
| volume | up,down,set | empty, number, max, min |
| play_mode | set | single_cycle,shuffle,order |
| play_control | set | play,previous,continue,stop,next |
| count | query | online,offline |

## Workflow

1. **Split** multi-device/action utterances; semantic order; **Must** query before control if both in one sub-request.
2. **Locate:** `home-space-manage.md` + `devices-inquiry.md` list. Generic categories (“all lights”, AC, curtains): **Must** filter `get_home_devices` by `device_type` substring (`devices-inquiry.md` table). Multi-match → `endpoint_id` → `device_ids`.
3. **Map** user intent → `attribute` / `action` / `value`. Unsupported capability → **Must** say unsupported.
4. **Send:**

```bash
python3 scripts/aqara_open_api.py post_device_control '{"device_ids":["device_id_1","device_id_2"],"attribute":"brightness","action":"set","value":"30"}'
```

5. **Reply** per patterns below.

## User-Facing Patterns

**Forbidden** `endpoint_id` or other raw ids in user message.

### Success

| Case | Shape |
| --- | --- |
| On | `[Affirmative], [location] [device] [opened].` |
| Off | `[Affirmative], [location] [device] [closed].` |
| Adjust | `[Affirmative], [location] [device] [set to] {target}.` |

Localize. Multi-step: one sentence per step or summary + lines.

### Failure (Non-Auth)

**Must** one short line: `{location}{device} control failed` (e.g. `Living room light control failed.`).

### Auth

**`unauthorized or insufficient permissions`:** **Must** `aqara-account-manage.md` (re-login); **Forbidden** only generic failure line without guidance; **Allowed:** add localized “sign in again and retry” with failure pattern.

## Auth Failure

**`unauthorized or insufficient permissions`:** **Must** re-login per `aqara-account-manage.md`; **Forbidden** claim control succeeded.
