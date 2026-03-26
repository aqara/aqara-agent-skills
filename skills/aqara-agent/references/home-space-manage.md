# Home & space management

**When this applies (mandatory)**

- Right after `aqara_api_key` is saved (see `references/aqara-account-manage.md`), **automatically** run **step 0** here and continue **1 / 2**—**do not** open with vague “please send a home name”; only if there are **multiple** homes, use **1** to ask for index or name.
- When the user says **switch / change / another home**: again run **step 0** first (**no** re-login by default; exceptions in `references/aqara-account-manage.md`: user explicitly re-logins, or API says token invalid).

**0. Fetch homes / positions**

- Infer `lang` from user input when relevant, e.g. `zh`, `en`.
- **Recommended**: from **`skills/aqara-agent`**, run:

```bash
python3 scripts/aqara_open_api.py homes
```

- **After saving token**: if the previous step was `save_user_account.py aqara_api_key ...`, this command **must be a new, separate invocation**—**do not** chain with `&&` on the same line as the save script (see `references/aqara-account-manage.md` step **2**).

**1. Multiple homes** (when the script shows two or more homes)

- In chat, list homes for selection, e.g. **1-xxxx, 2-xxxx** (index + home name).
- Wait for the user’s choice (`1`, `2`, or a name string).
- Write the chosen **`home_id`** and **`home_name`** to **`assets/user_account.json`** via:

```bash
python3 scripts/save_user_account.py home  '<home_id>'  '<home_name>'
```

- That home becomes the default; you do not need to ask for home info every time.

**2. Single home**

- If there is only one home, write `home_id` and `home_name` straight into **`assets/user_account.json`**—no user choice needed.

**3. Room list** — With a selected home and valid `home_id` in `user_account.json`:

```bash
python3 scripts/aqara_open_api.py rooms
```

##注意

**切换家庭**（与重新登录不同）：

- 若用户说「切换家庭」「换一个家庭」「用另一个家」等：**不要**默认走重新登录。在已有有效 `aqara_api_key` 时，直接进入 `references/home-space-manage.md` **步骤 0**（拉取家庭）→ 若多个家庭，**步骤 1**（用户按序号/名称选择；写入 `home_id` / `home_name`）；若仅一个家庭，**步骤 2**（自动写入）。
- **仅当**用户**明确**要求重新登录/轮换令牌，或接口明确返回 **令牌无效 / 未授权 / 鉴权失败** 时，才执行下文「登录并保存 `aqara_api_key`」流程。
- **明确信号**：任意响应中出现 **`unauthorized or insufficient permissions`**（或同义的未授权/权限不足表述），即视为鉴权/权限失败——**必须**执行本节「登录并保存 `aqara_api_key`」流程；再按 `references/home-space-manage.md` 刷新家庭并在需要时重选 `home_id`，然后继续原先查询/控制意图。
