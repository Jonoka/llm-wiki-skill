# 验收矩阵（Jonoka llm-wiki）

> 与 [PRODUCT.md](../PRODUCT.md) 绑定。  
> **主平台：Codex。** 其它平台 best-effort，不默认阻塞 v0.1。  
> 状态：`pass` / `fail` / `blocked` / `skip` / `todo`。

更新约定：每完成一项，改「状态」列并在「记录」写日期与简述（可链到 log 或 issue）。

---

## 图例

| 优先级 | 含义 |
|--------|------|
| **P0** | v0.1 必达 |
| **P1** | v0.1 强烈建议（有结论即可，含 blocked 说明） |
| **P2** | v0.2 或标「支持未验」 |

| 档位 | 含义 |
|------|------|
| 精简 | 默认 install，无 `--with-optional-adapters` |
| 完整 | install 带 `--with-optional-adapters` |

---

## 矩阵

| ID | 用例 | 档位 | 优先级 | 状态 | 记录 |
|----|------|------|--------|------|------|
| **U1** | init 新知识库（目录、schema、audit/、purpose） | 精简 | P0 | pass | 2026-07-22 演示库 |
| **U2** | 消化本地 Markdown / 已有 raw 文件 | 精简 | P0 | pass | 2026-07-22 Karpathy gist（含人工种子 + Codex 复核） |
| **U3** | status + lint 干净（断链/孤立/index/audit） | 精简 | P0 | pass | 2026-07-23/24；Windows lint stdin 已修 |
| **U4** | audit-file 一条 +「处理批注」accept 归档 | 精简 | P0 | pass | 2026-07-27 RAG.md suggest |
| **U5** | 完整安装 `--with-optional-adapters` 成功 | 完整 | P0 | pass | 2026-07-28：`CODEX_HOME=D:/CodexHome`，`install.sh --platform codex --target-dir .../llm-wiki --with-optional-adapters` exit 0；sibling `baoyu-url-to-markdown`（bun deps）、`youtube-transcript`、全局 `wechat-article-to-markdown`（uv）就位；`adapter-state.sh summary-human`（在 llm-wiki 包根、installed_skill）显示网页/X/知乎/YouTube/公众号为可用；小红书仍 manual_only；未开 Chrome 9222（可临时拉起，不阻塞 U5） |
| **U6** | URL ingest 且 **adapter 路径可用**（非仅 agent 自抓） | 完整 | P0 | pass | 2026-07-28：`web_article` available；`bun main.ts` 调 `baoyu-url-to-markdown` 抓取 https://www.sharktime.com/Blog_en_202604_LLM_Wiki.html → md ~23k 字 + html 快照；`classify-run` 有效正文；写入 raw/sources 并增量更新实体/主题；cache HIT。证据：`docs/u6-evidence.json`。**不是** Codex agent 自抓。 |
| **U7** | 提取失败时标准回退（粘贴 / 说明 not_installed） | 精简或完整 | P0 | pass | 2026-07-28：脚本层验证 not_installed / runtime_failed / empty_result / unsupported / 核心 available；字段含 install_hint+fallback_hint；SKILL 已有五态与回退规则；新增 `references/adapter-fallback-guide.md` + `docs/u7-evidence.json`。E2E 聊天服从度靠 SKILL 约束，不作单独 UI 测。 |
| **U8** | 安装到 `$CODEX_HOME/skills/llm-wiki` | 精简 | P0 | pass | 2026-07；runtime-context 已尊重 CODEX_HOME |
| **U9** | `install.sh --upgrade` 不丢 Jonoka 补丁 | 任一 | P1 | pass | 2026-07-28：从 **Jonoka fork** 工作树执行 `--upgrade --platform codex --target-dir $CODEX_HOME/skills/llm-wiki`；`git pull`→Already up to date；10 个关键文件无缺失；audit/runtime CODEX_HOME/lint argv/PRODUCT/指南均在；`resolve_platform_skill_root codex`→`D:/CodexHome/skills`。仅 `PRODUCT.md` 哈希因 fork 源刷新变化（仍为 Jonoka 内容）。**风险**：若在 **纯上游** clone 上 upgrade，`git pull`+重装会丢掉 fork 补丁。证据：`docs/u9-evidence.json`。 |
| **U10** | query 基于 wiki 作答并引用页面 | 精简 | P1 | pass | 2026-07-29：基于 index/wiki 检索作答，引用 `[[LLM Wiki]]`/`[[RAG]]` 等；持久化 `wiki/queries/2026-07-29-llm-wiki-vs-rag.md`；更新 index/log。证据：`docs/u10-u11-evidence.json`。 |
| **U11** | delete 素材级联 + cache invalidate | 精简 | P1 | pass | 2026-07-29：fixture raw+source → cache HIT → `delete-helper scan-refs` 命中实体与摘要 → 删 raw/source、去 LLM Wiki/index 引用 → `cache.sh invalidate`→INVALIDATED；残留检查全清。证据同上。 |
| **U12** | batch-ingest 文件夹 | 精简 | P2 | pass | 2026-07-29：2 个 md fixture → raw/notes + sources + cache + index/log。证据 `docs/u12-u16-evidence.json`。 |
| **U13** | digest 深度报告 / 对比 / 时间线 | 精简 | P2 | pass | 2026-07-29：`wiki/synthesis/LLM-Wiki与RAG-深度报告.md` 综合 3 篇核心素材。 |
| **U14** | graph Mermaid + HTML（jq/node） | 精简 | P2 | pass | 2026-07-29：`build-graph-data.sh`→14 节点/57 边；`build-graph-html.sh`→html ~604KB。修复 Windows `jq --argjson "$(cat…)"` ARG_MAX（改 `--slurpfile`）。HTML 需 `packages/graph-engine/dist`（skill 默认安装清单未带，monorepo build 后拷贝）。另有 mermaid 页。 |
| **U15** | crystallize 对话结晶 | 精简 | P2 | pass | 2026-07-29：`wiki/synthesis/sessions/U15-Codex优先与两档安装-2026-07-29.md` + log。 |
| **U16** | 多知识库 / `~/.llm-wiki-path` 切换 | 精简 | P2 | pass | 2026-07-29：init 第二库 `D:\wikis\u16-second-wiki`（含 audit）；切换 `~/.llm-wiki-path` 后恢复主库。CWD `.wiki-schema.md` 优先。 |

---

## P0 用例步骤（摘要）

### U1 init

1. 空目录或新路径。  
2. 「帮我初始化一个知识库」。  
3. 存在：`raw/`、`wiki/`、`audit/`、`index.md`、`log.md`、`purpose.md`、`.wiki-schema.md`。

### U2 本地 ingest

1. 本地 `.md` 或 raw 文件。  
2. `消化：<路径>` 或等价。  
3. 新增/更新 source、实体或主题；`index`/`log` 更新；cache 可 HIT。

### U3 status / lint

1. `知识库状态` / `检查知识库`。  
2. 无异常断链（模板占位除外且应已修）；coverage 不因 `/dev/stdin` 报错。

### U4 audit

1. 对某页记反馈或已有 `audit/*.md`。  
2. `处理批注`。  
3. open→0；`resolved/` 有 Resolution；正文或 reject 理由；log 有 audit 行。

### U5 完整安装

```bash
export CODEX_HOME="D:/CodexHome"   # 按实际
bash install.sh --platform codex --with-optional-adapters
# 或 --target-dir "$CODEX_HOME/skills/llm-wiki"
```

1. 安装无致命失败（允许单个 adapter warn）。  
2. `adapter-state` / status 外挂摘要不再是「全部未安装」（至少一类 available 或明确缺依赖）。

### U6 adapter URL ingest

1. 完整档已装。  
2. 选官方支持的公开 URL。  
3. 流程走 source-registry + adapter，而非仅「模型凭记忆写摘要」。  
4. raw 落盘且含可追溯正文。

### U7 回退

1. 精简档喂 URL，或完整档故意缺依赖。  
2. Agent 应提示安装完整档或请粘贴正文，**不中断核心 skill、不假装已 ingest**。

### U8 CODEX_HOME

1. `CODEX_HOME` 非 `~/.codex`。  
2. 技能出现在 `$CODEX_HOME/skills/llm-wiki`。  
3. 不依赖误装到 `%USERPROFILE%\.codex\skills`。

### U9 upgrade

1. 记录 fork 文件哈希或 `git log`（audit 脚本、runtime-context 等）。  
2. `bash install.sh --upgrade --platform codex`（加 target-dir/CODEX_HOME）。  
3. Jonoka 补丁仍在或有文档说明「须从 fork 源重装」。

---

## 反模式（验收时不要）

- 用 **agent 随便抓了网页** 就勾 U6。  
- 为刷矩阵 **狂堆个人笔记**。  
- 把 **workbench e2e** 算进 v0.1。  
- 四平台全测才允许发布。

---

## 当前进度快照

| 集合 | 进度 |
|------|------|
| P0 U1–U8 | **全部 pass** |
| P1 U9–U11 | **全部 pass** |
| P2 U12–U16 | **全部 pass**（U14 HTML 依赖 monorepo engine dist） |

### U5 实装备忘（2026-07-28）

- 命令：`export CODEX_HOME=D:/CodexHome` 后  
  `bash install.sh --platform codex --target-dir "$CODEX_HOME/skills/llm-wiki" --with-optional-adapters`
- 依赖本机已有：node/npm、bun、uv、Git Bash PATH 需包含它们。
- 校验：在 **`llm-wiki` 安装目录**执行  
  `bash scripts/adapter-state.sh summary-human`  
  （`installed_skill` 下 optional root = 父目录 `skills/`，勿把 `--skill-root` 误指成 `llm-wiki` 自身却又期望 sibling 在更外层时搞反；默认从包根跑即可。）
- `--skill-root` 若传入，语义是 **skills 根**（含 baoyu 的那一层），不是 `llm-wiki` 子目录。

### U6 实装备忘（2026-07-28）

1. `adapter-state.sh check web_article` → `available`  
2. 运行（Windows 需真实 `bun.exe` 路径，npm 的 bun shim 在纯 bash 下可能坏）：  
   `bun main.ts <url> -o out.md --timeout 120000`  
   于 ` $CODEX_HOME/skills/baoyu-url-to-markdown/scripts`  
3. 成功标志：exit 0、markdown 有正文、可选 `*-captured.html`  
4. 写入知识库 raw + source；frontmatter 标注 `extract_path: baoyu-url-to-markdown`  
5. 与「agent 自己 fetch」区分：必须能指出 companion 命令与输出文件  

### U7 实装备忘（2026-07-28）

| 场景 | 命令要点 | 期望 state |
|------|----------|------------|
| 完整档网页 | `check web_article` | available |
| 模拟未装 | `--skill-root <空skills> --layout-mode installed_skill check web_article` | not_installed + 含 `--with-optional-adapters` 的 install_hint |
| 运行失败 | `classify-run web_article 1 /no/file` | runtime_failed |
| 空正文 | `classify-run web_article 0 empty.md` | empty_result |
| 小红书 | `check xiaohongshu_post` | unsupported |
| 粘贴/本地 | `check plain_text` / `local_document` | available（不依赖外挂） |

指南：`references/adapter-fallback-guide.md`  
证据：`docs/u7-evidence.json`

### U9 实装备忘（2026-07-28）

```bash
export CODEX_HOME="D:/CodexHome"
cd /path/to/Jonoka/llm-wiki-skill   # 必须是本 fork
bash install.sh --upgrade --platform codex --target-dir "$CODEX_HOME/skills/llm-wiki"
# 完整档另加：--with-optional-adapters
```

| 安全 | 危险 |
|------|------|
| origin = Jonoka/llm-wiki-skill，从该工作树 upgrade | 工作树是 sdyckjq 上游 only，`git pull` 后重装覆盖 Jonoka 文件 |

证据：`docs/u9-evidence.json`、`docs/u9-before.json`、`docs/u9-after.json`

### U10 / U11 备忘（2026-07-29）

**U10 query**

1. 读 `index.md` + 在 `wiki/` 检索关键词  
2. 综合回答须含 `[[页面名]]` 引用（ grounded 于库内页）  
3. 有价值的综合可写入 `wiki/queries/{date}-{slug}.md`（`type: query` `derived: true`）  
4. 更新 index「查询结果」与 log  

**U11 delete**

1. 可对 disposable 素材演练，避免误删种子文  
2. `delete-helper.sh scan-refs <wiki> <素材文件名或 slug>`  
3. 删 `raw/` + `wiki/sources/`；清理其它页引用与 index  
4. `cache.sh invalidate <raw路径>`（文件已删也可）  
5. 确认 cache 无条目、无残留链接  

证据：`docs/u10-u11-evidence.json`

### U12–U16 备忘（2026-07-29）

| ID | 要点 |
|----|------|
| U12 | 文件夹内多 md → 逐个 raw/notes + sources + cache；log 记 batch-ingest |
| U13 | `wiki/synthesis/` 深度报告，引用多 source |
| U14 | 需 **jq** + **node**；`build-graph-data.sh` 已修 Windows ARG_MAX；HTML 另需 monorepo `npm run build -w @llm-wiki/graph-engine` 的 `engine.iife.js` |
| U15 | `wiki/synthesis/sessions/`，默认 INFERRED |
| U16 | 第二库 init；`~/.llm-wiki-path` 可切换；工作区含 `.wiki-schema.md` 时优先生效 |

证据：`docs/u12-u16-evidence.json`

最后更新：2026-07-29（**P2 闭环**）。
