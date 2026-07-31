# Obsidian 插件安装与「处理批注」衔接（v0.2）

> Jonoka **llm-wiki Audit** 插件：在 vault 里选中 wiki 原文 → 一键写入 `audit/`。  
> 插件源码与构建产物：[`obsidian-plugin/llm-wiki-audit/`](../obsidian-plugin/llm-wiki-audit/)  
> 契约：[`references/audit-contract-v1.md`](../references/audit-contract-v1.md)

---

## 你需要什么

| 项 | 说明 |
|----|------|
| 知识库 | 已 `init` 的目录（含 `wiki/`、`audit/`、`.wiki-schema.md`） |
| Obsidian | 用该目录作 **vault 根**（不是 skill 安装目录） |
| 插件文件 | `main.js` + `manifest.json` + `styles.css` |
| Codex skill | 已装 llm-wiki（用于说「处理批注」） |

插件装在 **vault**，不装在 `CODEX_HOME/skills`。

---

## 安装（推荐：从 monorepo 拷贝构建产物）

### 1. 拿到三份文件

已提交到仓库，无需本机构建：

```text
obsidian-plugin/llm-wiki-audit/main.js
obsidian-plugin/llm-wiki-audit/manifest.json
obsidian-plugin/llm-wiki-audit/styles.css
```

（开发者改源码后：`cd obsidian-plugin/llm-wiki-audit && npm install && npm run build`）

### 2. 放入 vault 插件目录

将知识库根记为 `WIKI`（例：`D:/wikis/我的知识库`）。

**Git Bash / macOS / Linux：**

```bash
WIKI="/path/to/your-wiki"          # 改成知识库根
PLUGIN="$WIKI/.obsidian/plugins/llm-wiki-audit"
REPO="/path/to/llm-wiki-skill"     # 改成本仓库克隆路径

mkdir -p "$PLUGIN"
cp "$REPO/obsidian-plugin/llm-wiki-audit/main.js" "$PLUGIN/"
cp "$REPO/obsidian-plugin/llm-wiki-audit/manifest.json" "$PLUGIN/"
cp "$REPO/obsidian-plugin/llm-wiki-audit/styles.css" "$PLUGIN/"
```

**Windows PowerShell：**

```powershell
$Wiki  = "D:\wikis\我的知识库"              # 改成知识库根
$Repo  = "D:\grok-projects\llm-wiki-skill" # 改成仓库路径
$Plugin = Join-Path $Wiki ".obsidian\plugins\llm-wiki-audit"
New-Item -ItemType Directory -Force -Path $Plugin | Out-Null
Copy-Item "$Repo\obsidian-plugin\llm-wiki-audit\main.js","$Repo\obsidian-plugin\llm-wiki-audit\manifest.json","$Repo\obsidian-plugin\llm-wiki-audit\styles.css" -Destination $Plugin -Force
```

### 3. 在 Obsidian 启用

1. 打开该 vault  
2. **设置 → 第三方插件**  
3. 关闭「安全模式」（若仍开启）  
4. 启用 **llm-wiki Audit**  
5. （可选）插件设置：默认 author；是否「仅允许 wiki/ 页面」

升级插件：重新拷贝三文件 → 禁用再启用，或重启 Obsidian。

---

## 日常：记批注 → 处理批注

```text
┌─────────────────────┐     ┌──────────────────────┐
│ Obsidian（录入）     │     │ Codex + llm-wiki      │
│ 选中 wiki 原文       │     │ 说：处理批注           │
│ → 记 llm-wiki 批注  │ ──► │ 读 audit/*.md         │
│ → 写入 audit/*.md   │     │ accept/reject →       │
│   source:           │     │ audit/resolved/ + log │
│   obsidian-plugin   │     │ （改正文仅此时发生）    │
└─────────────────────┘     └──────────────────────┘
```

### A. 在 Obsidian 记一条

1. 打开 `wiki/**/*.md`（默认不允许非 wiki 页；可在设置关闭限制）  
2. **选中**有问题的原文（须与页面一字不差）  
3. 命令面板：`记 llm-wiki 批注（选区）`  
   - 或编辑器右键 → **记 llm-wiki 批注**  
4. 选 severity，填写 Comment → **写入 audit/**  
5. 插件会打开新文件，并尽量复制一句给 Codex 的提示  

**不会**修改你正在读的 wiki 正文。

### B. 在 Codex 处理

在**知识库目录**为工作区（或已配置 `~/.llm-wiki-path`）时说：

```text
处理批注
```

或更具体：

```text
处理批注：请处理 open audit（audit/某文件.md）。
```

Agent 按 SKILL 工作流 12：列表 → 定位锚点 → accept/partial/reject/defer → 改正文（若 accept）→ `resolved/` + `log.md`。

自检 open 列表（可选）：

```bash
python "$SKILL_DIR/scripts/audit-review.py" "<wiki_root>" --open
```

形状自检：

```bash
python "$SKILL_DIR/scripts/check-audit-compat.py" "<wiki_root>"
```

---

## 其它录入方式（仍可用）

| 方式 | 何时用 |
|------|--------|
| **本插件** | 日常在 Obsidian 读 wiki 时 |
| 对话「对 [[某页]] 这段有问题…」 | 已在 Codex 里讨论 |
| `templates/obsidian-audit.md` | 无第三方插件时 |
| `skill-assets/audit-entry.html` | 浏览器表单 / 图谱旁路 |
| `audit-file.py` | 脚本 / CI / Agent |

均须最终落到 `audit/*.md`，再「处理批注」。

---

## 排障

| 现象 | 处理 |
|------|------|
| 插件列表没有 llm-wiki Audit | 检查三文件是否在 `.obsidian/plugins/llm-wiki-audit/`；关安全模式 |
| 「请先选中原文」 | 先拖选文本再执行命令 |
| 「不在 wiki/ 下」 | 只在 `wiki/` 内批注，或设置里关闭「仅允许 wiki/」 |
| Codex 说没有 open audit | 确认 vault 根 = 知识库根；`audit/` 下有 `.md` 且不在 `resolved/` |
| 处理后找不到改动 | accept 才会改正文；reject 只归档理由 |

---

## 相关链接

| 文档 | 内容 |
|------|------|
| [obsidian-plugin/llm-wiki-audit/README.md](../obsidian-plugin/llm-wiki-audit/README.md) | 开发构建 |
| [references/audit-guide.md](../references/audit-guide.md) | 完整 audit 协议 |
| [docs/v0.2-audit-plugins-brief.md](./v0.2-audit-plugins-brief.md) | v0.2 立项与里程碑 |
| [docs/todo-list.md](./todo-list.md) | 单源进度（V 序） |
