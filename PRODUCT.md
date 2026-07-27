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
- Obsidian / Web 选中批注插件（属 v0.2+ 体验，不挡 v0.1）。

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
- [ ] Codex 精简安装文档含 `CODEX_HOME` 与 Windows 注意点  
- [ ] 完整档 `--with-optional-adapters` 写进主安装叙事  
- [ ] 验收：**U1–U4**（init / 本地 ingest / status·lint / audit）通过  
- [ ] 验收：**U5–U7**（完整安装 / adapter URL / 失败回退）有结论（通过或记录阻塞）  
- [ ] 验收：**U8**（`CODEX_HOME` 路径）通过  
- [ ] **U9**（upgrade 不丢 fork 补丁）有结论  
- [ ] 工作流 U10+ 在矩阵中标为抽检 / v0.2，不默认为「没做就不完整」  
- [ ] `workbench` 深度开发标为范围外  
- [ ] 可 `git push` + tag（如 `v0.1.0-jonoka`）作为发布点  

## 路线图（防跑偏）

```text
0  锁定本文 + 验收矩阵          ← 当前
1  产品骨架文档（安装两档等）    ← 当前
2  本机夹具验收 U5–U9           ← 下一阶段（实装，不为养库）
3  按失败打磨 SKILL / install
4  发布 tag
5  v0.2：graph/query/delete 等抽样与 audit UX
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
| [SKILL.md](SKILL.md) | Agent 执行规范 |
| [platforms/codex/AGENTS.md](platforms/codex/AGENTS.md) | Codex 薄入口 |
