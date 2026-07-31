# skill-assets

预构建、随 **默认 skill 安装** 分发的运行时资产（Jonoka）。

## graph-engine

| 路径 | 用途 |
|------|------|
| `graph-engine/dist/engine.iife.js` | `scripts/build-graph-html.sh` 内嵌的离线图谱引擎 |
| `graph-engine/dist/BUILD-INFO.txt` | 同步时间与内容哈希 |

安装器会：

1. 复制整个 `skill-assets/` 到技能目录  
2. 再把 IIFE 落到 `packages/graph-engine/dist/engine.iife.js`（兼容旧路径）

### 如何更新

在 monorepo 根目录：

```bash
npm run build -w @llm-wiki/graph-engine
bash scripts/sync-graph-engine-dist.sh
# 或：npm run sync:graph-engine-dist
```

然后提交 `skill-assets/graph-engine/dist/` 变更。

### 防漂移检查（CI / 发版）

改 `packages/graph-engine` 后若忘记 sync，下列命令会 **非 0 退出**：

```bash
# 需先有 packages/graph-engine/dist/engine.iife.js（quality 流水线会先 vite build）
npm run check:skill-assets-graph
# 等价 bash：
bash scripts/sync-graph-engine-dist.sh --check
```

`npm run quality-and-tests`（及 GitHub Actions `quality-and-tests.yml`）在 **build-graph 之后** 自动跑该检查。

**不要**把 `node_modules`、source map 或整个 `packages/graph-engine` 源码塞进 skill-assets。
