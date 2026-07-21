# Jonoka fork notes

本仓库 fork 自 [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill)。

## Phase 1 — Audit 文件协议（已完成）

在 **sdyckjq 知识库布局**上叠加 [lewislulu/llm-wiki-skill](https://github.com/lewislulu/llm-wiki-skill) 风格的人类定点反馈（audit），**不**引入 Obsidian 插件 / Web 预览（留给 Phase 2）。

### 新增 / 修改

| 路径 | 说明 |
|------|------|
| `scripts/audit-file.py` | 写入 open audit |
| `scripts/audit-review.py` | 按 target 列出 open/resolved |
| `scripts/init-wiki.sh` | 创建 `audit/` + `audit/resolved/` |
| `scripts/lint-runner.sh` | 机械检查 open audit 形状与 target |
| `scripts/wiki-compat.sh` | `ensure-audit-dirs`；inspect 报告 `audit_dir` |
| `scripts/hook-session-start.sh` | 会话注入 open audit 数量提示 |
| `templates/audit-template.md` | 手写模板 |
| `templates/schema-template.md` | 目录说明 + Audit 规则 |
| `references/audit-guide.md` | 协议全文 |
| `SKILL.md` | 工作流 11 audit-file、12 audit；路由与 status/lint 扩展 |

### 知识库侧目录

```text
<wiki-root>/
├── audit/*.md           # open
└── audit/resolved/*.md  # 已处理（含 Resolution，不删除）
```

`target` 使用相对知识库根路径，例如 `wiki/entities/Foo.md`。  
日志仍写 sdyckjq 的单文件 `log.md`（不采用 lewislulu 的按日 `log/`）。

### 旧知识库

```bash
bash scripts/wiki-compat.sh ensure-audit-dirs "<wiki_root>"
# 或任意一次成功的 audit-file.py 会自动 mkdir
```

### 致谢

- Karpathy llm-wiki gist  
- sdyckjq-lab/llm-wiki-skill（底座）  
- lewislulu/llm-wiki-skill（audit 协议与锚点思路）  

### Phase 2（未做）

- Obsidian audit 插件路径适配  
- Web 预览选中批注  
- `audit-shared` TypeScript 库  
