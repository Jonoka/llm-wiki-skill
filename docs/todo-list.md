# todo-list.md — Jonoka llm-wiki 待办清单（单源）

> 按「价值 vs 成本」排序；每项完成后改「状态」并写「记录」。  
> **只维护本文件**，不要另起一套口头清单。

更新：2026-07-30

---

## 总览

| 集合 | 进度 |
|------|------|
| P0 U1–U8 | **全部 pass** |
| P1 U9–U11 | **全部 pass** |
| P2 U12–U16 | **全部 pass**（见矩阵；部分在演示库已实装） |
| 安装体验 | graph dist 默认安装 **已做**（2026-07-30） |

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
| **U10** | **query 引用 + queries/ 持久化** | **pass** | **2026-07-29**；`wiki/queries/2026-07-29-llm-wiki-vs-rag.md`；`docs/u10-u11-evidence.json` |
| **U11** | **delete 级联 + cache invalidate** | **pass** | **2026-07-29**；disposable fixture 已删净；证据同上 |
| U12 | batch-ingest | pass | 2026-07-29；`docs/u12-u16-evidence.json` |
| U13 | digest | pass | 2026-07-29 |
| U14 | graph data + HTML | pass | 2026-07-29；2026-07-30 默认含 graph dist |
| U15 | crystallize | pass | 2026-07-29 |
| U16 | 多 wiki / `~/.llm-wiki-path` | pass | 2026-07-29；`D:\wikis\u16-second-wiki` |
| Graph dist 默认安装 | skill-assets IIFE | pass | 2026-07-30；`install_graph_engine_runtime` |
| 文档骨架 | PRODUCT / 矩阵 / FORK | pass | 2026-07-28+ |
| 发布 | `v0.1.0` / `0.1.1` / `0.1.2-jonoka` | pass | 已 push tags |

---

## 仍可做（真·待办，按推荐序）

| 序 | 项 | 为何 | 状态 |
|----|----|------|------|
| A | **发 `v0.1.3-jonoka`**（含 graph dist 默认安装） | 把 07-30 安装改进钉到 tag | todo |
| B | **install 文档补一句**：精简档已含离线图谱 IIFE；HTML 仍需本机 `jq`+`node` | 减少「装了还不能出 HTML」误解 | todo |
| C | **graph 缺 jq 时的友好报错**（`build-graph-data.sh` 已有，可再测 Windows PATH） | 体验 | todo |
| D | **把 `engine.iife` 更新流程写进 CI/发版检查**（改 engine 必跑 sync） | 防 dist 漂移 | todo |
| E | **Codex 聊天 E2E**：短口令再跑一轮 ingest/query/audit（人机） | 证明 agent 服从 SKILL，非仅脚本验收 | todo |
| F | **Obsidian / Web audit 录入（原 Phase 2 插件）** | 体验升级；非必需 | later |
| G | **skill 安装打包 graph-engine 以外的 monorepo 能力** | 明确不做除非改目标 | out of scope |

---

## 禁止

- 把已 pass 的 U10/U11/U12… 再当「下一步」重做一遍（除非回归）。  
- 为刷矩阵无限堆个人笔记。  
- 另起第三份口头待办，与本文件冲突。

## 使用

1. 只改本文件「仍可做」表的状态/记录。  
2. 细节与命令写在 acceptance-matrix / FORK-NOTES。  
3. 做完一项：本文件勾选 + 矩阵记录 + 必要时 evidence json。
