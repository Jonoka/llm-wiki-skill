# Jonoka fork notes

Fork 自 [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill)。

**先读：[PRODUCT.md](PRODUCT.md)**（目标、非目标、两档安装、v0.1 标准）。  
**验收：[references/acceptance-matrix.md](references/acceptance-matrix.md)**。

---

## 相对上游的差异（自管）

| 区域 | 内容 |
|------|------|
| Audit Phase 1 | `audit/` 协议、`audit-file.py` / `audit-review.py`、SKILL 工作流 11–12、`references/audit-guide.md` |
| 安装 | `CODEX_HOME` → `$CODEX_HOME/skills`（`scripts/runtime-context.sh`） |
| 安装清单 | `references/`、`FORK-NOTES.md` 进入 `MANAGED_ITEMS` |
| Lint | Windows 下 coverage 不读 `/dev/stdin`（临时文件 + `process.argv`） |
| 文档 | `PRODUCT.md`、本文件、`references/acceptance-matrix.md`、README/Codex 入口的 Jonoka 段 |

日志约定：仍用上游单文件 **`log.md`**（不用 lewislulu 按日 `log/`）。  
`target` 路径：相对知识库根，如 `wiki/entities/Foo.md`。

---

## 主平台：Codex

### 精简安装（核心主线）

```bash
export CODEX_HOME="D:/CodexHome"   # 若已改过 home；未改可省略
cd /path/to/llm-wiki-skill

bash install.sh --platform codex
# 等价显式：
# bash install.sh --platform codex --target-dir "$CODEX_HOME/skills/llm-wiki"
```

能力：本地文件、粘贴文本、PDF 等核心主线。  
**不含**官方网页/X/公众号/YouTube/知乎提取器。

### 完整安装（核心 + 可选提取器）

```bash
export CODEX_HOME="D:/CodexHome"
cd /path/to/llm-wiki-skill

bash install.sh --platform codex --with-optional-adapters
```

可能需要：`node` 或 `bun`、`uv`（公众号）、部分站点 Chrome 调试端口等。  
装完用「知识库状态」看外挂摘要；缺依赖时允许单包 warn，但应能区分 not_installed / available。

本机 CLI 自检（应在 **已安装的 llm-wiki 目录**下）：

```bash
export CODEX_HOME="D:/CodexHome"
cd "$CODEX_HOME/skills/llm-wiki"
bash scripts/adapter-state.sh summary-human
```

期望：网页 / X / 知乎 / YouTube / 公众号为「可用」或等价；小红书为手动。  
U5 已在 2026-07-28 于 `D:\CodexHome` 实装通过。

### Windows

- 推荐：Git Bash 执行 `install.sh`，或仓库根 `install.ps1`（处理编码）。  
- 系统自带 `C:\Windows\System32\bash.exe`（WSL 启动器）可能不可用；用 `Git\bin\bash.exe`。  
- 勿把「仅 WSL 路径」写死进文档。

### 升级（U9 已验收）

```bash
export CODEX_HOME="D:/CodexHome"
cd /path/to/Jonoka/llm-wiki-skill    # 必须是本 fork 工作树
bash install.sh --upgrade --platform codex --target-dir "$CODEX_HOME/skills/llm-wiki"
# 需要完整提取档时再加：--with-optional-adapters
```

**策略（2026-07-28 U9 pass）：**

| 做法 | 结果 |
|------|------|
| 在 **Jonoka fork** 目录执行 `--upgrade` | `git pull` 拉本 fork + `install_bundle` 重装 → **保留** audit / CODEX_HOME / lint / 文档补丁 |
| 在 **纯上游 sdyckjq clone** 执行 `--upgrade` | `git pull` 上游 + 重装 → **会丢掉** Jonoka 补丁 |

因此：**只从本 fork 升级**；若曾误用上游树，再从 fork 跑一次 `install.sh --platform codex`（或带 adapters）覆盖安装即可。

### 默认路径对照

| 条件 | 技能目录 |
|------|----------|
| 设置了 `CODEX_HOME` | `$CODEX_HOME/skills/llm-wiki` |
| 未设置 | `~/.codex/skills/llm-wiki`（兼容 `~/.Codex`） |

---

## 日常用法（Codex）

```text
消化：<文件路径或 URL>
知识库状态
处理批注
```

- 工作区打开知识库根目录更稳。  
- 路径文件：`~/.llm-wiki-path`（init 时可能写入）。  
- **Agent 自抓 URL** 成功 ≠ 完整档 adapter 已装（见 PRODUCT / U6）。

Audit 协议全文：[references/audit-guide.md](references/audit-guide.md)。

---

## 旧知识库补 audit 目录

```bash
bash scripts/wiki-compat.sh ensure-audit-dirs "<wiki_root>"
```

---

## Phase 与范围

| 阶段 | 状态 |
|------|------|
| Phase 1 audit 文件协议 | 已完成并本机验收（U4） |
| 产品文档骨架 | 进行中（本文 + PRODUCT + 矩阵） |
| 完整档 adapters 实装（U5） | **已通过**（2026-07-28，见 acceptance-matrix） |
| adapter URL ingest（U6） | **已通过**（2026-07-28 baoyu → SharkTime 文） |
| 提取失败回退（U7） | **已通过**（2026-07-28；见 adapter-fallback-guide） |
| upgrade 不丢补丁（U9） | **已通过**（须从 Jonoka fork 升级；见上节） |
| 发布标签 | `v0.1.0-jonoka` · 补丁 **`v0.1.1-jonoka`**（含 U9 文档与证据） |
| Phase 2 Obsidian/Web 批注 | 未做（v0.2+） |
| workbench 深度 | **范围外**（上游） |

---

## 致谢

Karpathy llm-wiki gist · sdyckjq-lab/llm-wiki-skill · lewislulu/llm-wiki-skill · 上游 optional adapter 作者们。
