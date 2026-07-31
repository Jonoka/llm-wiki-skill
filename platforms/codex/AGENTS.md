# Codex 入口（Jonoka）

<!-- llm-wiki context: 如有知识库，优先查阅 wiki/index.md -->

薄入口。产品与范围：[PRODUCT.md](../../PRODUCT.md)。共享说明：[README.md](../../README.md)。行为：[SKILL.md](../../SKILL.md)。差异安装：[FORK-NOTES.md](../../FORK-NOTES.md)。

**主平台：Codex。** 其它平台 best-effort。

## 安装

若使用自定义 Codex home（常见于改过 `CODEX_HOME` 的环境）：

```bash
export CODEX_HOME="D:/CodexHome"   # 改成你的实际路径
```

### 精简档（核心主线）

```bash
bash install.sh --platform codex
# 或
bash install.sh --platform codex --target-dir "$CODEX_HOME/skills/llm-wiki"
```

能力：本地 Markdown/文本/HTML/PDF、纯文本粘贴；**默认含**离线图谱 IIFE（`skill-assets/graph-engine/dist`）。  
**不含**官方 URL 提取器。

生成交互式图谱 HTML 时，本机另需 **`jq` + `node`**（装 skill 不会自动装 jq）。完整档与否无关。

### 完整档（+ 可选提取器）

```bash
bash install.sh --platform codex --with-optional-adapters
```

启用网页、X/Twitter、微信公众号、YouTube、知乎等自动提取（依赖 node/bun、uv 等，见安装输出）。  
小红书等可能仍仅支持粘贴。

### 安装结果目录

| 条件 | 路径 |
|------|------|
| 已设置 `CODEX_HOME` | `$CODEX_HOME/skills/llm-wiki` |
| 未设置 | `~/.codex/skills/llm-wiki`（兼容旧 `~/.Codex/skills`） |

Windows：用 Git Bash 或仓库根目录 `install.ps1`。

### 记批注（Obsidian）→ 处理批注（Codex）

1. 安装插件：见 [docs/obsidian-audit-install.md](../../docs/obsidian-audit-install.md)  
   （`main.js` 等拷到 `<wiki>/.obsidian/plugins/llm-wiki-audit/`）  
2. Obsidian 选中 `wiki/**` 原文 →「记 llm-wiki 批注」→ 生成 `audit/*.md`  
3. 在本知识库上下文对 Codex 说：**处理批注**（不要让插件改正文；accept 由你执行）

### 升级

```bash
export CODEX_HOME="D:/CodexHome"   # 若使用自定义 home
cd /path/to/Jonoka/llm-wiki-skill  # 必须是本 fork
bash install.sh --upgrade --platform codex --target-dir "$CODEX_HOME/skills/llm-wiki"
```

**U9**：从本 fork 升级会保留 Jonoka 补丁；从纯上游 clone 升级会覆盖丢失。详见 [FORK-NOTES.md](../../FORK-NOTES.md)。

## 日常三口令

```text
消化：<路径或 URL>
知识库状态
处理批注
```

初始化：`帮我初始化一个知识库`。  
纠错：`对 wiki/entities/某页.md 这段有问题：…` 再 `处理批注`。

**注意**：未装完整档时，URL 可能靠 agent 自行抓取；那不表示 adapter 已安装。完整档验收见 [references/acceptance-matrix.md](../../references/acceptance-matrix.md) U5–U6。
