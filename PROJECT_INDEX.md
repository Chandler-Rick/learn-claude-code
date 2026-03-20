# 项目索引

## 1. 项目定位

`learn-claude-code` 是一个用于讲解 Agent Harness 工程的教学型仓库，当前由 3 个主要部分组成：

- `agents/`：Python 版分阶段 Agent 示例实现（s01-s12 + `s_full.py`）。
- `docs/`：中英日三语教程文档，对应每个阶段的讲解。
- `web/`：Next.js 可视化学习站点，用来展示教程、源码、diff 和交互式视图。

核心关系是：

`agents/ + docs/ -> web/scripts/extract-content.ts -> web/src/data/generated/*.json -> web/src/app/*`

## 2. 根目录结构

```text
learn-claude-code/
|- agents/                 Python Agent 示例
|- docs/                   教程文档（en / zh / ja）
|- skills/                 示例技能定义
|- web/                    Next.js 学习平台
|- .github/                CI 配置
|- .env.example            环境变量示例
|- requirements.txt        Python 依赖
|- README.md               英文说明
|- README-zh.md            中文说明
`- README-ja.md            日文说明
```

## 3. 目录职责

### `agents/`

用途：存放教学版 Agent Harness 代码，每个文件代表一个能力阶段。

关键文件：

- `agents/s01_agent_loop.py`：最小 Agent loop。
- `agents/s02_tool_use.py`：工具分发。
- `agents/s03_todo_write.py`：计划与 Todo。
- `agents/s04_subagent.py`：子 Agent。
- `agents/s05_skill_loading.py`：按需加载技能。
- `agents/s06_context_compact.py`：上下文压缩。
- `agents/s07_task_system.py`：任务系统。
- `agents/s08_background_tasks.py`：后台任务。
- `agents/s09_agent_teams.py`：Agent 团队。
- `agents/s10_team_protocols.py`：协作协议。
- `agents/s11_autonomous_agents.py`：自治 Agent。
- `agents/s12_worktree_task_isolation.py`：worktree 隔离。
- `agents/s_full.py`：完整参考实现。
- `agents/__init__.py`：目录说明。

索引规则：

- 文件名前缀 `s01` 到 `s12` 与教程章节一一对应。
- `web/scripts/extract-content.ts` 会扫描这个目录，提取类、函数、工具名、LOC 等元数据。

### `docs/`

用途：存放教程正文。

结构：

- `docs/zh/`：中文教程
- `docs/en/`：英文教程
- `docs/ja/`：日文教程https://github.com/msitarzewski/agency-agents

命名规则：

- `s01-the-agent-loop.md`
- `s02-tool-use.md`
- ...
- `s12-worktree-task-isolation.md`

索引规则：

- 文件名前缀同样与 `agents/` 中的版本号对应。
- `web/scripts/extract-content.ts` 会读取这些 Markdown，生成前端用的 `docs.json`。

### `skills/`

用途：示例技能目录，服务于 s05 “Skill Loading” 相关内容。

当前子目录：

- `skills/agent-builder/`
- `skills/code-review/`
- `skills/mcp-builder/`
- `skills/pdf/`

典型内容：

- `SKILL.md`：技能说明入口。
- `references/`：参考资料。
- `scripts/`：辅助脚本。

### `web/`

用途：Next.js 16 + React 19 前端站点。

关键结构：

- `web/src/app/`：App Router 页面入口。
- `web/src/components/`：页面组件、可视化组件、架构图、代码 diff 组件。
- `web/src/lib/`：常量、i18n、工具函数。
- `web/src/data/generated/`：由脚本生成的版本索引和文档数据。
- `web/src/data/scenarios/`：交互场景数据。
- `web/src/data/annotations/`：注解数据。
- `web/scripts/extract-content.ts`：生成 `versions.json` / `docs.json` 的核心脚本。
- `web/package.json`：前端依赖和脚本入口。

## 4. 前端关键入口

### 页面入口

- `web/src/app/page.tsx`：根入口跳转页。
- `web/src/app/[locale]/layout.tsx`：多语言布局。
- `web/src/app/[locale]/page.tsx`：首页，展示学习路径和架构概览。
- `web/src/app/[locale]/(learn)/[version]/page.tsx`：单章节页面。
- `web/src/app/[locale]/(learn)/[version]/diff/page.tsx`：章节 diff 页面。
- `web/src/app/[locale]/(learn)/timeline/page.tsx`：时间线页。
- `web/src/app/[locale]/(learn)/compare/page.tsx`：对比页。
- `web/src/app/[locale]/(learn)/layers/page.tsx`：分层视图页。

### 核心配置与常量

- `web/src/lib/constants.ts`：版本顺序、层次划分、章节元信息。
- `web/src/lib/i18n.tsx`：前端 i18n。
- `web/src/lib/i18n-server.ts`：服务端 i18n。
- `web/src/types/agent-data.ts`：生成数据的类型定义。

### 数据生成结果

- `web/src/data/generated/versions.json`：Agent 版本索引、diff、LOC、工具、函数等信息。
- `web/src/data/generated/docs.json`：三语教程内容聚合结果。

## 5. 数据流与依赖关系

### 教程内容生成链路

1. `agents/*.py` 提供源码。
2. `docs/{zh,en,ja}/*.md` 提供章节文档。
3. `web/scripts/extract-content.ts` 扫描并提取结构化信息。
4. 生成到 `web/src/data/generated/versions.json` 和 `web/src/data/generated/docs.json`。
5. `web/src/app/*` 和 `web/src/components/*` 消费这些 JSON 渲染页面。

### 版本元信息来源

- 展示顺序：`web/src/lib/constants.ts` 中的 `VERSION_ORDER` / `LEARNING_PATH`
- 标题、层级、核心洞察：`web/src/lib/constants.ts` 中的 `VERSION_META` / `LAYERS`

结论：

- 新增一个章节时，通常至少要同时修改 `agents/`、`docs/`、`web/src/lib/constants.ts`，然后重新执行 `npm run extract`。

## 6. 常用命令

### Python 示例

安装依赖：

```powershell
pip install -r requirements.txt
```

运行某个阶段：

```powershell
python agents/s01_agent_loop.py
python agents/s12_worktree_task_isolation.py
```

### Web 站点

安装依赖：

```powershell
cd web
npm install
```

生成内容索引：

```powershell
npm run extract
```

本地开发：

```powershell
npm run dev
```

生产构建：

```powershell
npm run build
```

## 7. 修改任务时的定位建议

如果你要改：

- 教程内容：优先看 `docs/zh/`、`docs/en/`、`docs/ja/`
- Python Agent 示例：优先看 `agents/`
- 前端页面布局：优先看 `web/src/app/` 和 `web/src/components/layout/`
- 章节展示逻辑：优先看 `web/src/app/[locale]/(learn)/[version]/` 和 `web/src/components/docs/`
- 版本排序/标题/层次：优先看 `web/src/lib/constants.ts`
- 生成逻辑：优先看 `web/scripts/extract-content.ts`
- 交互可视化：优先看 `web/src/components/visualizations/`
- 架构图：优先看 `web/src/components/architecture/`
- 技能示例：优先看 `skills/*/SKILL.md`

## 8. 当前项目的快速判断

- 仓库类型：教学型多模块仓库
- 主要语言：Python、TypeScript、Markdown
- 前端框架：Next.js 16 / React 19
- 文档语言：中文、英文、日文
- 核心生成脚本：`web/scripts/extract-content.ts`
- 核心教学资产：`agents/` 与 `docs/`
- 核心展示层：`web/`

## 9. 建议的后续维护方式

后续如果继续扩展仓库，建议同步维护这 4 处索引信息：

1. 本文件 `PROJECT_INDEX.md`
2. `README-zh.md` 的“项目结构”部分
3. `web/src/lib/constants.ts` 的版本元信息
4. `web/src/data/generated/*.json` 的重新生成结果
