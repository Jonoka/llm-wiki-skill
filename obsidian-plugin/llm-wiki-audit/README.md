# llm-wiki Audit（Obsidian 插件 · v0.2 MVP）

选中 wiki 页原文 → **记 llm-wiki 批注** → 写入知识库 `audit/*.md`（`source: obsidian-plugin`）。  
**不改正文**；处理仍对 Codex 说「处理批注」。

契约：[references/audit-contract-v1.md](../../references/audit-contract-v1.md)

## 安装（开发 / 手动）

1. 用 Obsidian 打开你的 **知识库根** 作为 vault（含 `wiki/`、`audit/`）。  
2. 创建目录：  
   `<vault>/.obsidian/plugins/llm-wiki-audit/`  
3. 复制本目录中的：  
   - `main.js`  
   - `manifest.json`  
   - `styles.css`  
4. 设置 → 第三方插件 → 启用 **llm-wiki Audit**。

或从 monorepo 构建后再拷贝：

```bash
cd obsidian-plugin/llm-wiki-audit
npm install
npm run build
# 再复制 main.js manifest.json styles.css 到 vault 插件目录
```

## 使用

1. 打开 `wiki/**/*.md`  
2. 选中有问题的句子  
3. 命令面板：`记 llm-wiki 批注（选区）`，或编辑器右键同名项  
4. 填 severity / Comment → 写入 `audit/`  
5. 对话：**处理批注**

## 开发

```bash
npm install
npm run dev     # watch
npm test        # audit-core unit tests（仓库根 tests/js）
```

生成文件须通过：

```bash
python scripts/check-audit-compat.py <vault>
```

## 范围（MVP）

- ✅ 选区、锚点上下文、target 路径、open audit  
- ✅ 设置：默认 author、是否强制 `wiki/`  
- ✅ 复制「处理批注」提示  
- ❌ 插件内 accept/改正文  
- ❌ 图谱 HTML（V5）
