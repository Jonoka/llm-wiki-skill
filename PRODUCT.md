# Jonoka llm-wiki — 产品定义

> 本文锁定 fork 的目标与范围，避免「养个人库」与「做 skill 产品」混在一起。  
> 实现细节见 [SKILL.md](SKILL.md)；差异与安装见 [FORK-NOTES.md](FORK-NOTES.md)；验收见 [references/acceptance-matrix.md](references/acceptance-matrix.md)。

## 一句话

在 [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill) 的编译式知识库能力上，加上 [lewislulu](https://github.com/lewislulu/llm-wiki-skill) 风格的 **audit 纠错闭环**，并在 **Codex + Windows** 上开箱可用；支持 **精简安装** 与 **`--with-optional-adapters` 完整安装** 两档。

## 主用户

- 主要用 **OpenAI Codex**（含自定义 `CODEX_HOME`）维护本地 Markdown 知识库的人。
- 需要「知识编译进 wiki、持续维护」，而不是每次查询纯 RAG。
- 需要把纠错留在 `audit/`，而不是只留在聊天记录里。

## 主平台策略

| 平台 | 策略 |
|------|------|
| **Codex** | **优先**：安装、文档、验收、升级路径都按 Codex 打磨 |
| Claude Code / OpenClaw / Hermes | **best-effort**：继承上游安装入口，不保证与 Codex 同等验证 |

## 非目标（v0.1 明确不做）

- 把本机个人 wiki 的素材数量当 KPI（演示库只作验收夹具）。
- 深度运营 / 替代上游 `workbench/` 桌面产品。
- 保证全网站点、全登录态抓取成功。
- 四平台同等测试与同等文档篇幅。
- Obsidian / Web **真插件**（选区一键写 vault）属 v0.2+；v0.1 已提供 **轻量录入**（Obsidian 模板 + `skill-assets/audit-entry.html`，见 audit-guide Phase 1.5）。

## 两档安装（一等公民）

| 档位 | 命令要点 | 能力 |
|------|----------|------|
| **精简** | `install.sh --platform codex`（+ `CODEX_HOME` / `--target-dir`） | 本地 md/txt/pdf、粘贴；无官方 URL 提取器 |
| **完整** | 同上 + **`--with-optional-adapters`** | 另装网页 / X / 公众号 / YouTube / 知乎等提取依赖 |

说明：

- Agent **自己联网抓正文** ≠ 完整档 **adapter 路径**。验收完整档时必须以 `adapter-state` / 安装后的 companion skill 为准。
- 小红书等来源可能仍是 **manual_only**（粘贴），见来源总表。

## 日常三口令

```text
消化：<路径或 URL>
知识库状态
处理批注
```

可选：`检查知识库`、`对 wiki/entities/某页.md 这段有问题：…`

排障时再加长提示（路径、跳过隐私确认、禁止只口头总结等），**日常默认短句**。

## v0.1 成功标准（可勾选）

- [x] [PRODUCT.md](PRODUCT.md) / [FORK-NOTES.md](FORK-NOTES.md) / 验收矩阵与本文一致且已入库（2026-07-28）  
- [x] Codex 精简安装文档含 `CODEX_HOME` 与 Windows 注意点（FORK / README / platforms/codex）  
- [x] 完整档 `--with-optional-adapters` 写进主安装叙事（U5）  
- [x] 验收：**U1–U4**（init / 本地 ingest / status·lint / audit）通过  
- [x] 验收：**U5–U7**（完整安装 / adapter URL / 失败回退）通过（2026-07-28）  
- [x] 验收：**U8**（`CODEX_HOME` 路径）通过  
- [x] **U9**（upgrade 不丢 fork 补丁）通过：须从 Jonoka fork 工作树执行（2026-07-29）  
- [x] **U10 / U11**（query 引用持久化 / delete 级联+cache）通过（2026-07-29）  
- [x] **U12–U16**（batch / digest / graph / crystallize / 多库）通过（2026-07-29；**2026-07-30/31** 起默认安装含 graph IIFE，开箱 HTML）  
- [x] 工作流 U10–U16 已在矩阵标为 pass（P1/P2 抽样验收完成）  
- [x] `workbench` 深度开发标为范围外（见非目标）  
- [x] 可 `git push` + tag：`v0.1.0` · `v0.1.1` · `v0.1.2` · **`v0.1.3-jonoka`**（2026-07-31：默认 graph dist + 单源 todo-list）  
- [x] 余项 **A–F**（tag / 文档 / 缺 jq / IIFE 防漂移 / Codex E2E / 轻量 audit 录入）见 `docs/todo-list.md`（2026-07-31）

## v0.2 成功标准（立项中 · 可勾选）

> 规格：[docs/v0.2-audit-plugins-brief.md](docs/v0.2-audit-plugins-brief.md) · 进度：`docs/todo-list.md` V 序

- [x] **V0 立项**：brief 入库，范围 / 非目标 / MVP / 验收草案写清（2026-07-31）  
- [x] **V1 契约**：`references/audit-contract-v1.md` + fixture + `check-audit-compat.py`（2026-07-31）  
- [ ] **V2 Obsidian MVP**：选区一键写入 `audit/`（`source: obsidian-plugin`），不改正文  
- [ ] **U17 / U18**：插件录入 + Agent「处理批注」闭环有证据  
- [ ] 用户文档：安装插件 + 与 Codex 衔接；v0.1 轻量路径仍可用  
- [ ] 发版说明或 tag（如 `v0.2.0-jonoka` / 插件版本）

## 路线图（防跑偏）

```text
0–4  文档 + P0/P1/P2 验收 + 多版 tag     ← 已完成至 v0.1.3-jonoka
5    余项 A–F 已 pass；G out of scope
6    v0.2：Obsidian audit 真插件（V0 已立项 → V1 契约 → V2 MVP → …）
7    可选 V5：图谱 HTML 选区/预填；真插件写盘方案 B/C 另议
```

## 与本机知识库的关系

默认演示 / 回归路径示例：`D:\wikis\我的知识库`（可换）。

- **用途**：证明 skill 行为，不是产品交付物。  
- **不要**：为完善 skill 而无限堆个人笔记。  
- **可以**：保留少量种子素材 + 一条 audit 样例作为回归记忆。

## 致谢

- [Karpathy llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)  
- [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill)  
- [lewislulu/llm-wiki-skill](https://github.com/lewislulu/llm-wiki-skill)  
- 上游可选提取：baoyu-url-to-markdown、wechat-article-to-markdown、youtube-transcript 等  

## 相关文档

| 文档 | 内容 |
|------|------|
| [FORK-NOTES.md](FORK-NOTES.md) | 相对上游的差异、安装命令、自管文件 |
| [references/acceptance-matrix.md](references/acceptance-matrix.md) | U1–U16 验收矩阵 |
| [references/audit-guide.md](references/audit-guide.md) | audit 协议 |
| [docs/v0.2-audit-plugins-brief.md](docs/v0.2-audit-plugins-brief.md) | **v0.2** Audit 真插件立项简报 |
| [references/audit-contract-v1.md](references/audit-contract-v1.md) | **v0.2 V1** 插件数据契约（冻结） |
| [docs/todo-list.md](docs/todo-list.md) | 单源待办（含 v0.2 V 序） |
| [SKILL.md](SKILL.md) | Agent 执行规范 |
| [platforms/codex/AGENTS.md](platforms/codex/AGENTS.md) | Codex 薄入口 |
