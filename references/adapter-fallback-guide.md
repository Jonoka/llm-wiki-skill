# 外挂失败回退指南（U7）

> Agent 必须先跑 `adapter-state.sh`，**用返回字段生成提示**，不要另写一套文案。  
> 核心主线（本地文件 / 粘贴）**不因外挂失败而中断**。

## 状态机

| state | 含义 | Agent 应做 |
|-------|------|------------|
| `available` | 可自动提取 | 调用对应 adapter；成功后再 `classify-run` |
| `not_installed` | 未装 companion / 工具 | **不要假装已抓取**；提示 `--with-optional-adapters` 或 `install_hint`；允许粘贴/本地文件 |
| `env_unavailable` | 缺 uv 等环境 | 提示补环境 + 手动入口 |
| `runtime_failed` | 提取进程失败 | 可重试一次；仍失败则手动入口 |
| `empty_result` | 跑完但无有效正文 | 请用户补全文，再 ingest |
| `unsupported` | 如小红书 | 只走手动粘贴，不调用外挂 |

`check` / `classify-run` 输出 8 列：

```text
source_id  source_label  state  state_label  detail  recovery_action  install_hint  fallback_hint
```

## 推荐话术骨架（短）

**not_installed（精简档喂 URL 时）：**

```text
当前是精简安装，网页自动提取未就绪（not_installed）。
你可以：
1) 完整安装：bash install.sh --platform codex --with-optional-adapters
2) 直接把正文粘贴给我，或提供本地 .md/.pdf
本地文件与粘贴不依赖外挂，可以马上消化。
```

**runtime_failed：**

```text
自动提取这次失败了（runtime_failed）。可以重试一次；若仍失败请粘贴全文或另存本地文件后再消化。
```

**empty_result：**

```text
提取跑完了但没有有效正文（empty_result）。请补全文或换本地文件，我再写入知识库。
```

**unsupported（小红书等）：**

```text
该来源不支持自动提取，请从 App/网页复制正文粘贴。
```

## 禁止

- 外挂失败时仍生成「已消化」且 raw 无真实来源正文  
- 忽略 `fallback_hint` / `install_hint` 自己编安装步骤  
- 因外挂失败拒绝处理用户已提供的粘贴文本或本地路径  

## 自检命令

```bash
cd "$CODEX_HOME/skills/llm-wiki"   # 或本仓库根（source_checkout）

# 已装完整档
bash scripts/adapter-state.sh check web_article
# → state=available

# 模拟未装（skill-root 指空的 skills 目录）
bash scripts/adapter-state.sh --skill-root /path/to/empty-skills \
  --layout-mode installed_skill check web_article
# → state=not_installed，含 install_hint 与 fallback_hint

bash scripts/adapter-state.sh classify-run web_article 1 /no/such.md
# → runtime_failed

bash scripts/adapter-state.sh classify-run web_article 0 /path/to/empty.md
# → empty_result
```

## 与 U5 / U6 的关系

| 用例 | 验证点 |
|------|--------|
| U5 | 完整安装后多为 `available` |
| U6 | `available` 下真实 baoyu 抓取成功 |
| U7 | 失败态字段齐全 + Agent/文档按表回退（本指南） |
