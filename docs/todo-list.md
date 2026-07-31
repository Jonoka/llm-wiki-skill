# todo-list.md — Jonoka llm-wiki 待办清单（单源）

> 按「价值 vs 成本」排序；每项完成后改「状态」并写「记录」。  
> **只维护本文件**，不要另起一套口头清单。

更新：2026-07-31（V2 完成）

---

## 总览

| 集合 | 进度 |
|------|------|
| P0 U1–U8 | **全部 pass** |
| P1 U9–U11 | **全部 pass** |
| P2 U12–U16 | **全部 pass**（见矩阵） |
| 安装体验 | graph dist 默认安装 **已做**（2026-07-30） |
| 发布 v0.1 | **`v0.1.3-jonoka`** 已 push（2026-07-31） |
| 余项 A–F | **全部 pass**（2026-07-31；G oos） |
| **v0.2 Audit 真插件** | V0–V2 **pass**；下一步 **V3** 文档分发 / **V4** 验收；见 [brief](./v0.2-audit-plugins-brief.md) |

详细记录以 [references/acceptance-matrix.md](../references/acceptance-matrix.md) 为准。

---

## 已完成（勿重复当「下一步」）

| ID | 项 | 状态 | 记录 |
|----|----|------|------|
| U1–U4 | init / 本地 ingest / lint / audit | pass | 演示库 + 2026-07 |
| U5 | `--with-optional-adapters` | pass | 2026-07-28 |
| U6 | baoyu adapter URL ingest | pass | 2026-07-28；`docs/u6-evidence.json` |
| U7 | 外挂失败回退协议 | pass | 2026-07-28；`adapter-fallback-guide` |
| U8 | `CODEX_HOME` 安装 | pass | 2026-07 |
| U9 | upgrade 从 fork 不丢补丁 | pass | 2026-07-28/29；`docs/u9-evidence.json` |
| **U10** | **query 引用 + queries/ 持久化** | **pass** | **2026-07-29**；`wiki/queries/…`；`docs/u10-u11-evidence.json` |
| **U11** | **delete 级联 + cache invalidate** | **pass** | **2026-07-29**；证据同上 |
| U12–U16 | batch / digest / graph / crystallize / 多库 | pass | 2026-07-29+；graph IIFE 默认安装 |
| A–F | tag / 文档 / 缺 jq / IIFE 门禁 / Codex E2E / 轻量 audit 录入 | pass | 2026-07-31 |
| G | skill 打包 monorepo 其余 | out of scope | — |
| **V0** | **v0.2 立项 brief** | **pass** | **2026-07-31**；`docs/v0.2-audit-plugins-brief.md` |
| **V1** | **契约 + fixture + check-audit-compat** | **pass** | **2026-07-31**；`docs/v1-evidence.json` |
| **V2** | **Obsidian 插件 MVP** | **pass** | **2026-07-31**；`obsidian-plugin/llm-wiki-audit`；`docs/v2-evidence.json` |

---

## v0.2 待办（真·下一步，按推荐序）

> 规格真源：[v0.2-audit-plugins-brief.md](./v0.2-audit-plugins-brief.md) · 契约：[audit-contract-v1.md](../references/audit-contract-v1.md)。只改本表状态。

| 序 | 项 | 为何 | 状态 |
|----|----|------|------|
| **V1** | 契约冻结 + 最小 vault fixture + 兼容检查清单 | 插件与 `audit-file.py` 同构 | **pass**（2026-07-31） |
| **V2** | **Obsidian 插件 MVP**：选区 → severity/comment → 写 `audit/`（`source: obsidian-plugin`） | 核心价值 | **pass**（2026-07-31；`docs/v2-evidence.json`） |
| **V3** | 用户文档与分发（装插件 / 与「处理批注」衔接） | 可安装 | todo |
| **V4** | 验收 U17/U18 + evidence；矩阵补行 | 可证明 | todo |
| **V5** | 图谱 HTML 选区/预填增强（默认方案 A，不强写盘） | 体验；可后移 | later |
| **V6** | 发版 `v0.2.0-jonoka`（或插件独立版本说明） | 钉发布点 | todo（依赖 V2–V4） |

---

## 禁止

- 把已 pass 的 U1–U16 / A–F 再当「下一步」重做（除非回归）。  
- 未完成 V2 就扩张 workbench / 新 adapter 战场。  
- 插件内自动改正文并 resolved（那是 Agent「处理批注」）。  
- 另起第三份口头待办，与本文件冲突。

## 使用

1. 只改本文件状态/记录；细节写 brief / 矩阵 / FORK。  
2. 做完一项：本文件勾选 + 必要时 evidence json + 矩阵。  
3. v0.1 轻量路径（模板 / `audit-entry.html`）在 v0.2 期间 **保持可用**。
