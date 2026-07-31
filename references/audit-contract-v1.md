# Audit 契约 v1（冻结 · 给 v0.2 插件）

> **状态**：冻结（2026-07-31，V1）  
> **人类说明**：[audit-guide.md](./audit-guide.md)  
> **立项**：[docs/v0.2-audit-plugins-brief.md](../docs/v0.2-audit-plugins-brief.md)  
> **校验入口**：`python scripts/check-audit-compat.py <wiki_root>`  
> **夹具**：`tests/fixtures/audit-v1-wiki/`

本文件是 **机器可读意图的契约真源**：Obsidian / Web 插件写入的 open audit **必须**与此一致。  
**禁止**在插件侧发明 frontmatter 字段或改目录语义。若要改契约，须升版本（v2）并同步 `audit-file.py` / `audit-review.py` / lint。

---

## 1. 目录

| 路径 | 含义 |
|------|------|
| `<wiki_root>/audit/*.md` | **open** 反馈（待处理） |
| `<wiki_root>/audit/resolved/*.md` | **resolved**（含 Resolution；永不删除） |
| 插件默认只写 | `audit/` open；**不**写 `resolved/` |

文件名建议：`YYYYMMDD-HHMMSS-<slug>.md`（slug 可来自 comment 摘要）。

---

## 2. Frontmatter 字段（全部必填键）

| 字段 | 类型 | 规则 |
|------|------|------|
| `id` | string | `YYYYMMDD-HHMMSS-` + 4 位 hex（小写） |
| `target` | string | **相对知识库根**，正斜杠，如 `wiki/entities/Foo.md` |
| `target_lines` | `[int, int]` | 1-based 闭区间；可漂移，处理时以文本锚点为准 |
| `anchor_before` | string | 选区前上下文，建议 ≤200 字；**允许空串** |
| `anchor_text` | string | 选中原文 **verbatim**；**禁止空** |
| `anchor_after` | string | 选区后上下文；**允许空串** |
| `severity` | enum | `error` \| `warn` \| `suggest` \| `info` |
| `author` | string | 非空 |
| `source` | enum | `manual` \| `agent` \| `obsidian-plugin` \| `web-viewer` |
| `created` | string | ISO 8601（可含时区） |
| `status` | enum | open 区必须为 `open`；resolved 区为 `resolved` |

### source 语义

| 值 | 谁写 |
|----|------|
| `manual` | 手写 / Obsidian 核心 Templates |
| `agent` | Codex / Agent 调 `audit-file.py` |
| `obsidian-plugin` | **v0.2 真插件** |
| `web-viewer` | `audit-entry.html` 或图谱 Web 录入 |

### YAML 字符串

- 含 `:`、引号、换行时用双引号；`"` → `\"`，换行 → `\n`（与 `audit-file.py` 的 `yaml_escape` 一致）。

---

## 3. 正文结构

```markdown
---
# frontmatter
---

# Comment

<人类纠错说明，至少一行非空>

# Resolution

<!-- 处理完成后填写；插件 MVP 不要填 resolved 流程 -->
```

- `# Comment` 标题下至少一行有效说明。  
- 插件 **不得** 修改 `target` 指向的 wiki 正文。

---

## 4. 与脚本的等价性

同一 vault 内，下列两路径在 **字段集合与枚举** 上必须等价（`id` / `created` / 文件名可不同）：

1. `python scripts/audit-file.py … --source obsidian-plugin`  
2. Obsidian 插件（V2）写入的 open 文件  

校验命令：

```bash
# 校验夹具或任意 wiki
python scripts/check-audit-compat.py tests/fixtures/audit-v1-wiki

# 再跑一遍「脚本写入 + 形状检查」（临时目录，不污染夹具）
python scripts/check-audit-compat.py tests/fixtures/audit-v1-wiki --smoke-write
```

回归：

```bash
bash tests/audit-compat.regression-1.sh
```

---

## 5. 实现者检查清单（V2 前必过）

- [ ] 只写 `audit/`，不写 `resolved/`，不改正文  
- [ ] 11 个 frontmatter 键齐全；`source: obsidian-plugin`  
- [ ] `anchor_text` = 编辑器选区原文  
- [ ] `target` 为相对 vault 根的 `wiki/...` 路径  
- [ ] 无选区 / target 不在 wiki 页 → **拒绝写入**并提示  
- [ ] 生成文件后 `check-audit-compat.py <vault>` 退出 0  
- [ ] `audit-review.py <vault> --open` 能列出新文件  
- [ ] 不依赖 lewislulu 按日 `log/`；log 仍由 Agent 在「处理批注」时写 `log.md`

---

## 6. 版本策略

| 版本 | 含义 |
|------|------|
| **v1**（本文件） | 与 v0.1 Phase 1 协议相同；冻结给插件 |
| v2（未来） | 仅当必须加字段时；需双读兼容期 |

**契约版本号** 可写在插件 `manifest` / 设置里供调试，**不要**写进 audit frontmatter（避免旧 Agent 不认）。
