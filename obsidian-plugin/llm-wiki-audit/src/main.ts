import {
  App,
  Editor,
  MarkdownView,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  TFile,
} from "obsidian";
import {
  buildAuditMarkdown,
  contextAround,
  isAllowedWikiTarget,
  lineRangeFromOffsets,
  normalizeVaultPath,
  processHint,
  VALID_SEVERITIES,
} from "./audit-core.js";

interface LlmWikiAuditSettings {
  defaultAuthor: string;
  requireWikiPath: boolean;
}

const DEFAULT_SETTINGS: LlmWikiAuditSettings = {
  defaultAuthor: "you",
  requireWikiPath: true,
};

export default class LlmWikiAuditPlugin extends Plugin {
  settings: LlmWikiAuditSettings = DEFAULT_SETTINGS;

  async onload() {
    await this.loadSettings();

    this.addCommand({
      id: "add-audit-from-selection",
      name: "记 llm-wiki 批注（选区）",
      editorCallback: (editor: Editor, view: MarkdownView) => {
        void this.beginAuditFromEditor(editor, view);
      },
    });

    this.registerEvent(
      this.app.workspace.on("editor-menu", (menu, editor, info) => {
        const view = info as MarkdownView;
        menu.addItem((item) => {
          item
            .setTitle("记 llm-wiki 批注")
            .setIcon("message-square-warning")
            .onClick(() => {
              void this.beginAuditFromEditor(editor, view);
            });
        });
      }),
    );

    this.addCommand({
      id: "copy-process-audits-hint",
      name: "复制「处理批注」提示给 Codex",
      callback: () => {
        const text = "处理批注";
        void navigator.clipboard.writeText(text).then(
          () => new Notice("已复制：处理批注"),
          () => new Notice(text),
        );
      },
    });

    this.addSettingTab(new LlmWikiAuditSettingTab(this.app, this));
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  async beginAuditFromEditor(editor: Editor, view: MarkdownView) {
    const file = view?.file;
    if (!file) {
      new Notice("没有打开的 Markdown 文件");
      return;
    }

    const selection = editor.getSelection();
    if (!selection || !selection.trim()) {
      new Notice("请先选中要批注的原文");
      return;
    }

    const rel = normalizeVaultPath(file.path);
    if (this.settings.requireWikiPath && !isAllowedWikiTarget(rel)) {
      new Notice(
        `当前文件不在 wiki/ 下（${rel}）。可在插件设置中关闭「仅允许 wiki/ 页面」。`,
      );
      return;
    }
    if (!rel.toLowerCase().endsWith(".md")) {
      new Notice("仅支持 Markdown 文件");
      return;
    }
    if (rel.startsWith("audit/") || rel.includes("/audit/")) {
      new Notice("不要对 audit/ 下的文件记批注");
      return;
    }

    const fullText = editor.getValue();
    const from = editor.posToOffset(editor.getCursor("from"));
    const to = editor.posToOffset(editor.getCursor("to"));
    const target_lines = lineRangeFromOffsets(fullText, from, to);
    const ctx = contextAround(fullText, from, to);

    new AuditModal(this.app, {
      defaultAuthor: this.settings.defaultAuthor,
      selection,
      onSubmit: async (payload) => {
        await this.writeAudit({
          target: rel,
          anchor_text: selection,
          anchor_before: ctx.anchor_before,
          anchor_after: ctx.anchor_after,
          target_lines,
          severity: payload.severity,
          comment: payload.comment,
          author: payload.author,
        });
      },
    }).open();
  }

  async writeAudit(input: {
    target: string;
    anchor_text: string;
    anchor_before: string;
    anchor_after: string;
    target_lines: [number, number];
    severity: string;
    comment: string;
    author: string;
  }) {
    const built = buildAuditMarkdown({
      ...input,
      source: "obsidian-plugin",
    });
    if (!built.ok) {
      new Notice(`无法写入：${built.error}`);
      return;
    }

    const folder = "audit";
    if (!(await this.app.vault.adapter.exists(folder))) {
      await this.app.vault.createFolder(folder);
    }
    // ensure resolved exists (harmless)
    if (!(await this.app.vault.adapter.exists("audit/resolved"))) {
      try {
        await this.app.vault.createFolder("audit/resolved");
      } catch {
        /* ignore */
      }
    }

    let path = `${folder}/${built.filename}`;
    if (await this.app.vault.adapter.exists(path)) {
      path = `${folder}/${built.filename.replace(/\.md$/, "")}-${built.id.slice(-4)}.md`;
    }

    await this.app.vault.create(path, built.body);

    // Do NOT modify the target wiki page.
    new Notice(`已记录 open audit：${path}`);
    const hint = processHint(path, built.id);
    void navigator.clipboard.writeText(hint).then(
      () => new Notice("已复制给 Codex 的处理提示"),
      () => undefined,
    );

    const af = this.app.vault.getAbstractFileByPath(path);
    if (af instanceof TFile) {
      await this.app.workspace.getLeaf(true).openFile(af);
    }
  }
}

type ModalSubmit = {
  severity: string;
  comment: string;
  author: string;
};

class AuditModal extends Modal {
  private selection: string;
  private defaultAuthor: string;
  private onSubmit: (p: ModalSubmit) => void | Promise<void>;
  private severity = "warn";
  private comment = "";
  private author: string;

  constructor(
    app: App,
    opts: {
      selection: string;
      defaultAuthor: string;
      onSubmit: (p: ModalSubmit) => void | Promise<void>;
    },
  ) {
    super(app);
    this.selection = opts.selection;
    this.defaultAuthor = opts.defaultAuthor;
    this.author = opts.defaultAuthor;
    this.onSubmit = opts.onSubmit;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.addClass("llm-wiki-audit-modal");
    contentEl.createEl("h2", { text: "记 llm-wiki 批注" });
    contentEl.createEl("p", {
      text: "只写入 audit/ 的 open 文件，不改正文。处理时对 Codex 说「处理批注」。",
      cls: "llm-wiki-audit-hint",
    });

    contentEl.createEl("label", { text: "选中原文（anchor_text）" });
    const sel = contentEl.createEl("textarea", { cls: "llm-wiki-audit-selection" });
    sel.value = this.selection;
    sel.readOnly = true;
    sel.rows = 4;

    new Setting(contentEl)
      .setName("severity")
      .addDropdown((dd) => {
        for (const s of VALID_SEVERITIES) {
          dd.addOption(s, s);
        }
        dd.setValue(this.severity);
        dd.onChange((v) => {
          this.severity = v;
        });
      });

    new Setting(contentEl)
      .setName("author")
      .addText((t) => {
        t.setValue(this.author);
        t.onChange((v) => {
          this.author = v;
        });
      });

    contentEl.createEl("label", { text: "Comment（纠错说明）" });
    const commentEl = contentEl.createEl("textarea", { cls: "llm-wiki-audit-comment" });
    commentEl.rows = 4;
    commentEl.placeholder = "实际应为…；依据…";
    commentEl.addEventListener("input", () => {
      this.comment = commentEl.value;
    });

    new Setting(contentEl)
      .addButton((btn) => {
        btn.setButtonText("取消").onClick(() => this.close());
      })
      .addButton((btn) => {
        btn
          .setButtonText("写入 audit/")
          .setCta()
          .onClick(() => {
            void (async () => {
              this.comment = commentEl.value;
              if (!this.comment.trim()) {
                new Notice("请填写 Comment");
                return;
              }
              await this.onSubmit({
                severity: this.severity,
                comment: this.comment.trim(),
                author: this.author.trim() || this.defaultAuthor,
              });
              this.close();
            })();
          });
      });
  }

  onClose() {
    this.contentEl.empty();
  }
}

class LlmWikiAuditSettingTab extends PluginSettingTab {
  plugin: LlmWikiAuditPlugin;

  constructor(app: App, plugin: LlmWikiAuditPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "llm-wiki Audit" });

    new Setting(containerEl)
      .setName("默认 author")
      .setDesc("写入 frontmatter.author")
      .addText((t) => {
        t.setValue(this.plugin.settings.defaultAuthor);
        t.onChange(async (v) => {
          this.plugin.settings.defaultAuthor = v || "you";
          await this.plugin.saveSettings();
        });
      });

    new Setting(containerEl)
      .setName("仅允许 wiki/ 页面")
      .setDesc("关闭后可对 vault 内任意 .md 记批注（仍禁止 audit/）")
      .addToggle((tg) => {
        tg.setValue(this.plugin.settings.requireWikiPath);
        tg.onChange(async (v) => {
          this.plugin.settings.requireWikiPath = v;
          await this.plugin.saveSettings();
        });
      });
  }
}
