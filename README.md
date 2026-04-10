# Aqara Agent Skills

本仓库提供面向 **Aqara 智家** 的 Agent **Skill**：通过 **Aqara 开放平台 REST API**，用自然语言完成家庭/空间、设备、场景、自动化与能耗等查询与控制。Skill 按常见宿主约定的 `skills/` 目录结构打包，适用于 **OpenClaw**、**Claude** 等会加载 `SKILL.md` 的环境。

## 仓库里有什么

| 项 | 说明 |
|----|------|
| **aqara-agent** | 唯一 Skill；入口为 `skills/aqara-agent/SKILL.md`（规范）与 `skills/aqara-agent/README.md`（人读索引）。 |

**能力概览（与 `SKILL.md` 一致）：** 家庭与房间、设备查询/状态/日志/控制、场景（列表、执行、推荐、创建、快照、执行记录等）、自动化（列表、详情、开关、执行记录）、能耗/电费类统计；室外天气接口仅在场景「离家推荐」等流程中按规程使用。

## 目录结构（扫描结果）

```text
Aqara Agent Skills/
├── README.md                 # 本文件：仓库级说明
└── skills/
    └── aqara-agent/
        ├── SKILL.md          # 宿主与模型的规范性说明（Must / Forbidden、路由、错误、范围）
        ├── README.md         # Skill 人读总览与 references 索引
        ├── assets/
        │   ├── login_reply_prompt.json       # 官方登录文案与 official_open_login_url / login_url_policy
        │   ├── user_account.example.json     # 会话文件模板
        │   ├── user_account.json             # 本地会话（敏感，勿提交或外传）
        │   └── device_control_action_table.csv
        ├── scripts/
        │   ├── aqara_open_api.py             # CLI + Open API 客户端
        │   ├── save_user_account.py
        │   ├── runtime_utils.py
        │   └── requirements.txt
        └── references/
            ├── aqara-account-manage.md
            ├── home-space-manage.md
            ├── devices-inquiry.md
            ├── devices-control.md
            ├── scene-manage.md                 # 场景总索引
            ├── automation-manage.md            # 自动化总索引
            ├── energy-statistic.md
            ├── weather-forecast.md
            ├── scene-workflow/                 # 场景子流程
            │   ├── list.md
            │   ├── execute.md
            │   ├── recommend.md
            │   ├── create.md
            │   ├── snapshot.md
            │   ├── execution-log.md
            │   ├── failure-response.md
            │   └── appendices.md
            └── automation-workflow/            # 自动化子流程
                ├── list.md
                ├── toggle.md
                ├── execution-log.md
                └── failure-response.md
```

## 先读哪里

| 文件 | 作用 |
|------|------|
| [`skills/aqara-agent/SKILL.md`](skills/aqara-agent/SKILL.md) | 核心工作流、**Must** / **Forbidden**、意图与文档路由、错误与超范围说明。 |
| [`skills/aqara-agent/README.md`](skills/aqara-agent/README.md) | 能力说明、`references/` 表格索引、安装与 CLI 摘要。 |
| [`skills/aqara-agent/references/`](skills/aqara-agent/references/) | 分主题规程及与 `aqara_open_api.py` 配套的示例。 |

## 本地快速准备（脚本依赖）

在 Skill 根目录执行：

```bash
cd skills/aqara-agent
pip install -r scripts/requirements.txt
```

登录与家庭：按需将 [`skills/aqara-agent/assets/user_account.example.json`](skills/aqara-agent/assets/user_account.example.json) 复制为 `user_account.json`，再按 [`skills/aqara-agent/references/aqara-account-manage.md`](skills/aqara-agent/references/aqara-account-manage.md) 与 [`skills/aqara-agent/references/home-space-manage.md`](skills/aqara-agent/references/home-space-manage.md) 操作。**禁止**将真实的 `user_account.json` 或 API 密钥提交到版本库或打入对外分发的压缩包。

## 在 Cursor 中使用

将 **`skills/aqara-agent` 整个文件夹** 复制到 Cursor 的 skills 目录，例如：

`~/.cursor/skills/aqara-agent/`

（与仓库内结构一致：该目录下直接包含 `SKILL.md`、`assets/`、`scripts/`、`references/`。）更新后如未出现在 Agent 中，可重启 Cursor 或新开对话。若项目内使用 `.cursor/rules` 引用本 Skill，请仍遵守 Skill 内对登录 URL 与账号文件的约束。

## 打包分发（可选）

在 `skills/` 下生成与文件夹同名的 zip，便于分享安装：

```bash
cd skills
zip -r aqara-agent.zip aqara-agent -x "*.DS_Store" -x "*__pycache__*"
```

对外分发前：删除或替换包内 `assets/user_account.json`，或仅用模板与示例文件重新打包，避免泄露令牌。

## 与 `skills/` 下 zip 的关系

若存在 `skills/aqara-agent.zip`，一般为 `aqara-agent/` 的快照；安装时解压到宿主的 `skills/` 对应位置即可。当前仓库未必始终包含该 zip，需要时可按上一节命令在本地生成。
