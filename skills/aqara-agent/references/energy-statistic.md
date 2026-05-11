# Energy Consumption & Electricity Cost

## When to Use

- User asks power / electricity usage / consumption / cost / bill / statistics for devices, rooms, or whole home.
- **Must** have valid `aqara_api_key` and `home_id` (`aqara-account-manage.md`, `home-space-manage.md`).

## Execution Order

1. **Filters (priority):**
   - **`device_ids`:** If the user names device(s), **Must** resolve endpoint ids via `get_home_devices` (`devices-inquiry.md`), then set `device_ids`.
   - **`positions` / `position_ids`:** If the scope is room(s) only, **Must** resolve room ids; use field names your tenant expects.
   - **Neither:** **Must** pass empty `device_ids` / `positions` (or `position_ids`) as appropriate.
2. **Must** build JSON per tables below.
3. **Must** call `post_energy_consumption_statistic`. **Route:** non-empty `device_ids` -> **`device/energy/consumption/query`**; otherwise -> **`position/energy/consumption/query`**. **Forbidden** fabricate numbers; **Must** summarize only API response.

## API / CLI

Same base URL / headers as other skill calls (`AQARA_OPEN_API_URL`, `Authorization`, `position_id`, ...).

| CLI (exact method) | HTTP | Path |
| --- | --- | --- |
| `post_energy_consumption_statistic` | POST | Device or position route per non-empty `device_ids` rule above. |

```bash
python3 scripts/aqara_open_api.py post_energy_consumption_statistic '<json_body>'
```

**Example: single day, whole home, no room or device filter** (adjust fields per live Open Platform):

```bash
python3 scripts/aqara_open_api.py post_energy_consumption_statistic '{
  "data_type": "1",
  "time_range": ["2025-09-15 00:00", "2025-09-15 23:59"],
  "time_gradient": "1day",
  "data_aggregation_mode": "total",
  "positions": [],
  "device_ids": []
}'
```

- Room-only: set `positions`; **Must** use `device_ids: []` so call uses **position** route. Device path: non-empty `device_ids`. Both fields may appear per live API; semantics follow platform contract.
- Timeout: `AQARA_OPEN_HTTP_TIMEOUT` (default 60s).

## Request Body

| Field | Required | Meaning |
| --- | --- | --- |
| `data_type` | Yes | `"1"` consumption, `"2"` cost, `"3"` both. |
| `time_range` | Yes | `[start, end]` `YYYY-MM-DD HH:mm`. |
| `time_gradient` | Yes | One of **`30min`**, **`1hour`**, **`1day`**, **`1week`**, **`1month`**. |
| `data_aggregation_mode` | Yes | **`total`:** one summary; **`detail`:** breakdown for by-device, by-room, compare, share, or proportion. |
| `positions` | No | Room ids; `[]` if unused. |
| `device_ids` | No | Endpoint ids; `[]` if unused. **Routing:** non-empty -> device endpoint. |

## Data Aggregation Mode and Time Gradient

**Must** match user time span and question (e.g. month question -> often `1month`; "each day this month" -> `1day` over month `time_range`; "last week" -> `1week`).

| User intent (examples) | `data_aggregation_mode` | `time_gradient` hint |
| --- | --- | --- |
| Which device uses most / ranking | **`detail`** | Per-entity breakdown |
| Total for one room (all devices there) | **`total`** | Resolve `positions` |
| This month usage or cost | **`total`** | Often **`1month`** |
| Daily breakdown within a month | **`total`** | **`1day`** over month range |
| Last week | **`total`** | **`1week`** |
| Share / % across rooms | **`detail`** | Per-room series for ratios |
| One summed number all rooms | **`total`** | As scoped |

If unsure: **which / ranking / per room / per device / share / proportion / ratio / comparison** -> **`detail`**; **single headline** for already-named scope -> **`total`**.

## Quick Reference

- `data_type`: `"1"` \| `"2"` \| `"3"`.
- `time_gradient`: only the five values above.
- Path choice: **only** whether `device_ids` is non-empty.

## Response

- **Must** conclusion first, then key figures/trends from response.
- **Forbidden** invent usage on empty or error responses.
- **`unauthorized or insufficient permissions`:** **Must** re-login per `aqara-account-manage.md`, then retry.
- Ranking / multi-room / buckets: **Must** follow structure below.

## Charts

If user wants comparison / ranking / share and the client **can** render graphics: **Must** pie/bar (or similar) **only** from API values + short summary. If **cannot** render: **Must** clear numeric/ratio text. **Forbidden** invented chart data.

## User-Facing Structure

1. **Must** open with a headline (metric, date range, scope in plain language). **Forbidden** paste internal JSON keys (`data_type`, `time_gradient`, `data_aggregation_mode`, raw position ids) unless the user asked for technical detail.
2. **Ranking table:** e.g. Rank \| Room \| Amount. Rows with data first. Rooms with no row in response: **Must** separate short line/bullet (e.g. "Other rooms (N): ..."); **Forbidden** cram all names into one malformed row.
3. **Time series:** **Must** small markdown table per room or clear blocks; **Forbidden** long unreadable `a -> b -> c` chains.
4. **Must** default rounded user-friendly numbers (e.g. 2 decimals for money); extra precision only if user needs reconciliation.
5. **Must** <= one closing disclaimer (tariff depends on Aqara config; empty response != proven zero). **Forbidden** repeat the same caveat.

## Scope

This doc: Open API **consumption / statistics** on the routes above. **Forbidden** claim full billing / invoices / utility tariffs unless separately documented.
