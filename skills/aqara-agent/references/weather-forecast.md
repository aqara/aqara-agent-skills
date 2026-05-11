# Outdoor weather

Open Platform **outdoor / current weather** query for the **selected home** context. Wrapper: **`post_current_outdoor_weather`** in `scripts/aqara_open_api.py` - HTTP POST path **`current/weather/query`** (requires `position_id` / home header like other home-scoped calls).

## Skill scope

**Allowed:** **only** inside **[Scene recommend workflow](scene-workflow/recommend.md)**, **step 7**, when the **Leaving home** gate applies, **before** the first **`post_device_control`**.

**Forbidden:** **Create scene**, **Scene snapshot**, **Scene execute** (catalog execute), **Execution log**, standalone device control, device inquiry-only, energy, automation, general weather Q&A, or any other path. **Forbidden** invent forecast data without calling the API.

Normative workflow order and user-facing rules: **[recommend.md](scene-workflow/recommend.md)** (Leaving home branch).

## Request parameters

- **`weather_type`** (**required**) - One of the supported weather query types:
  - **`normal`** - General weather
  - **`aqi`** - Air quality
  - **`temp_hum`** - Temperature and humidity
  - **`sun`** - Sunrise and sunset
  - **`moon`** - Moonrise and moonset (if Open API docs list a second `sun` by mistake, use **`moon`** for this case.)

- **`time_range`** (**required**) - Interval **`[start_time, end_time]`**; each element is a time string (e.g. **`YYYY-MM-DD HH:MM:SS`**).
  - Example: full day **2026-09-15**: `['2026-09-15 00:00:00', '2026-09-15 23:59:59']`
  - Example: **2026-09-15 14:00-18:00**: `['2026-09-15 14:00:00', '2026-09-15 18:00:00']`
  - For **current** weather, use **now** as start and **now + 5 minutes** as end (same string format).

- **`location_en`** (**optional**) - Geographic place names in **English**, including administrative levels (Province / City / District as applicable).
  - Example: Nanshan, Shenzhen -> `["Shenzhen City", "Nanshan District"]` (array shape per platform contract.)

## CLI

Same pattern as other **`post_*`** tools: second argument is a JSON object. **Must** include **`weather_type`** and **`time_range`**; **May** include **`location_en`**.

```bash
# Required: weather_type + time_range. Current weather: [now, now + 5 minutes] (example times - substitute at run time).
python3 scripts/aqara_open_api.py post_current_outdoor_weather '{"weather_type":"normal","time_range":["2026-04-09 15:30:00","2026-04-09 15:35:00"]}'
```

```bash
# Optional location_en (English administrative names).
python3 scripts/aqara_open_api.py post_current_outdoor_weather '{"weather_type":"normal","time_range":["2026-04-09 15:30:00","2026-04-09 15:35:00"],"location_en":["Shenzhen City","Nanshan District"]}'
```

## Request body (quick reference)

| Field | Required | Description |
| --- | --- | --- |
| **`weather_type`** | Yes | `normal` / `aqi` / `temp_hum` / `sun` / `moon` (see above) |
| **`time_range`** | Yes | Array of two time strings `[start, end]` |
| **`location_en`** | No | Array of English place names with administrative hierarchy |

## Response and user-facing summary

**Must** summarize **only** from the **actual** API response. **Forbidden** defer the weather summary until after device control in that step. If the call fails or data is unusable, **Must** say so briefly; **May** still run **`post_device_control`** when the user's intent remains device actions ([recommend.md](scene-workflow/recommend.md)).

## Errors

**`unauthorized or insufficient permissions`** (or equivalent): **[aqara-account-manage.md](aqara-account-manage.md)** (re-login / token), then retry. **Forbidden** fabricate success.

**Related:** [Scene management index](scene-manage.md), [SKILL.md](../SKILL.md) (Scene intent, Out of scope - Weather).
