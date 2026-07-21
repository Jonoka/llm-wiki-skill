# Audit 指南 — 人类对 wiki 内容的定点反馈（Phase 1）

> 设计借鉴 [lewislulu/llm-wiki-skill](https://github.com/lewislulu/llm-wiki-skill) 的 audit 协议，  
> 路径与日志约定适配 sdyckjq-lab 系知识库（本 fork：Jonoka/llm-wiki-skill）。

## 为什么需要 audit

- AI 写的 wiki 会错；素材之间会矛盾。
- 对话里的纠正容易丢。
- `audit/` 给纠正一个**带文本锚点、可归档**的永久位置。

## 目录布局

```
<wiki-root>/
├── audit/
│   ├── 20260720-143022-数字有误.md    ← open（待处理）
│   └── resolved/
│       └── 20260719-...md             ← 已处理（含 Resolution，永不删除）
├── wiki/
├── log.md
└── .wiki-schema.md
```

- `audit/*.md`：open 反馈  
- `audit/resolved/*.md`：已处理；拒绝也进这里并写清理由  

## 文件格式

文件名：`YYYYMMDD-HHMMSS-<slug>.md`

```markdown
---
id: 20260720-143022-a1b2
target: wiki/entities/某概念.md
target_lines: [45, 52]
anchor_before: "## 概述\n\n"
anchor_text: "大约 1900 个文件"
anchor_after: "\n\n## 细节"
severity: warn
author: you
source: manual
created: 2026-07-20T14:30:22+08:00
status: open
---

# Comment

实际约 1800 个文件，见 commit abc123。

# Resolution

<!-- 处理完成后填写，并 status: resolved，文件移到 resolved/ -->
```

### Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | `YYYYMMDD-HHMMSS-<4hex>` |
| `target` | 是 | **相对知识库根**的路径，推荐 `wiki/entities/...md` |
| `target_lines` | 是 | 选中时的 1-based 行范围，可能漂移 |
| `anchor_before` | 是 | 选区前最多约 80 字（可空字符串） |
| `anchor_text` | 是 | 选中原文（ verbatim ） |
| `anchor_after` | 是 | 选区后最多约 80 字 |
| `severity` | 是 | `info` \| `suggest` \| `warn` \| `error` |
| `author` | 是 | 自由文本 |
| `source` | 是 | `manual` \| `agent` \| `obsidian-plugin` \| `web-viewer` |
| `created` | 是 | ISO 8601 |
| `status` | 是 | `open` 或 `resolved` |

### severity 语义

| 级别 | 含义 | 处理优先级 |
|------|------|------------|
| error | 事实错误 | 最高 |
| warn | 可疑/过时 | 高 |
| suggest | 建议改写/重组 | 中 |
| info | 补充说明 | 最低 |

### 与置信度标签的关系

| audit severity | 处理时建议 |
|----------------|------------|
| error / warn | 优先改正文；必要时把相关 claim 降为 `AMBIGUOUS` 或修正 `EXTRACTED` |
| suggest | 改措辞/结构，可不改 confidence |
| info | 可 defer 写入 `purpose.md` 开放问题 |

## 锚点定位算法（agent 处理时）

行号会因编辑失效，必须以文本窗口为准：

1. 用 `target_lines` 看该范围是否仍包含 `anchor_text`  
2. 否则在全文搜索 `anchor_text`；唯一命中则用该处  
3. 多命中时用 `anchor_before + anchor_text + anchor_after` 组合定位  
4. 仍找不到 → **stale**：不要静默丢弃；问用户 re-anchor / reject / archive  

## 写入入口（Phase 1）

### A. 脚本（推荐）

```bash
python ${SKILL_DIR}/scripts/audit-file.py "<wiki_root>" \
  --target "wiki/entities/某概念.md" \
  --anchor-text "原文片段" \
  --comment "纠错说明" \
  --severity warn \
  --author you \
  --source manual
```

### B. Agent 代写

用户说「对 [[某页]] 这段有意见…」→ agent 用 `audit-file.py` 或按模板写入 `audit/`，**默认只建 open 文件，不立刻改页**（除非用户明确要求「直接改」）。

### C. 手写 markdown

复制 `templates/audit-template.md`，填好 frontmatter 后放到 `audit/`。

## 处理工作流（audit 操作）

1. `python ${SKILL_DIR}/scripts/audit-review.py <wiki_root> --open`  
2. 按 severity：error → warn → suggest → info  
3. 对每条：定位锚点 → accept / partial / reject / defer  
4. 最小范围改正文  
5. 在 audit 文件追加 `# Resolution`，`status: resolved`  
6. 移到 `audit/resolved/`（**不删除**）  
7. `log.md` 追加：`## {日期} audit | resolved {id} — 一句话`  

### Resolution 示例

```markdown
# Resolution

2026-07-20 · accepted.
将「约 1900」改为「约 1800」，依据 commit abc123。
Updated: wiki/entities/某概念.md
```

## 工具

| 工具 | 作用 |
|------|------|
| `scripts/audit-file.py` | 创建 open audit |
| `scripts/audit-review.py` | 按 target 分组列出 open/resolved |
| `scripts/lint-runner.sh` | 机械检查 frontmatter 与 target 是否存在 |
| `templates/audit-template.md` | 手写模板 |

## 旧知识库

已有知识库没有 `audit/` 时：

```bash
mkdir -p "<wiki_root>/audit/resolved"
```

或任意一次成功的 `audit-file.py` 会自动创建目录。

## Phase 2（未做）

- Obsidian 选中批注插件  
- Web 预览选中批注  
- 共享 `audit-shared` TypeScript 库  
