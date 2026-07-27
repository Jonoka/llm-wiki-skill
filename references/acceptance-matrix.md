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
| **U5** | 完整安装 `--with-optional-adapters` 成功 | 完整 | P0 | todo | 未在 CODEX_HOME 实装验收 |
| **U6** | URL ingest 且 **adapter 路径可用**（非仅 agent 自抓） | 完整 | P0 | todo | 须看 adapter-state / companion |
| **U7** | 提取失败时标准回退（粘贴 / 说明 not_installed） | 精简或完整 | P0 | todo | 文档+行为；部分口头有，未钉死 |
| **U8** | 安装到 `$CODEX_HOME/skills/llm-wiki` | 精简 | P0 | pass | 2026-07；runtime-context 已尊重 CODEX_HOME |
| **U9** | `install.sh --upgrade` 不丢 Jonoka 补丁 | 任一 | P1 | todo | 未演练 |
| **U10** | query 基于 wiki 作答并引用页面 | 精简 | P1 | todo | 未系统测 |
| **U11** | delete 素材级联 + cache invalidate | 精简 | P1 | todo | 未测 |
| **U12** | batch-ingest 文件夹 | 精简 | P2 | todo | |
| **U13** | digest 深度报告 / 对比 / 时间线 | 精简 | P2 | todo | |
| **U14** | graph Mermaid + HTML（jq/node） | 精简 | P2 | todo | 可标「支持未验」 |
| **U15** | crystallize 对话结晶 | 精简 | P2 | todo | |
| **U16** | 多知识库 / `~/.llm-wiki-path` 切换 | 精简 | P2 | todo | 机制有，文档级即可 |

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
| P0 U1–U4, U8 | 已 pass |
| P0 U5–U7 | todo（下一阶段实装重点） |
| P1 U9–U11 | todo |
| P2 U12–U16 | 延后 |

最后更新：2026-07-28（文档落盘；实装状态以上表为准）。
