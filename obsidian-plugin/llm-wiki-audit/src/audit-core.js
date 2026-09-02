/**
 * Pure helpers for llm-wiki audit files (contract v1).
 * Shared by Obsidian plugin and Node unit tests — no Obsidian API here.
 */

export const VALID_SEVERITIES = ["error", "warn", "suggest", "info"];
export const SOURCE_PLUGIN = "obsidian-plugin";
export const CONTEXT_MAX = 200;

/** @param {string} text @param {number} [maxLen] */
export function slugify(text, maxLen = 40) {
  const s = String(text || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w\u4e00-\u9fff-]+/g, "")
    .replace(/^-+|-+$/g, "")
    .slice(0, maxLen);
  return s || "note";
}

/** @param {string} s */
export function yamlEscape(s) {
  return (
    '"' +
    String(s ?? "")
      .replace(/\\/g, "\\\\")
      .replace(/"/g, '\\"')
      .replace(/\r/g, "")
      .replace(/\n/g, "\\n") +
    '"'
  );
}

/**
 * @param {Date} [d]
 * @returns {{ stamp: string, created: string, hex4: string }}
 */
export function nowParts(d = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");
  const stamp =
    d.getFullYear() +
    pad(d.getMonth() + 1) +
    pad(d.getDate()) +
    "-" +
    pad(d.getHours()) +
    pad(d.getMinutes()) +
    pad(d.getSeconds());
  const offMin = -d.getTimezoneOffset();
  const sign = offMin >= 0 ? "+" : "-";
  const abs = Math.abs(offMin);
  const tz = sign + pad(Math.floor(abs / 60)) + ":" + pad(abs % 60);
  const created =
    d.getFullYear() +
    "-" +
    pad(d.getMonth() + 1) +
    "-" +
    pad(d.getDate()) +
    "T" +
    pad(d.getHours()) +
    ":" +
    pad(d.getMinutes()) +
    ":" +
    pad(d.getSeconds()) +
    tz;
  const hex4 = Math.floor(Math.random() * 0x10000)
    .toString(16)
    .padStart(4, "0");
  return { stamp, created, hex4 };
}

/**
 * Vault-relative path with forward slashes.
 * @param {string} path
 */
export function normalizeVaultPath(path) {
  return String(path || "")
    .replace(/\\/g, "/")
    .replace(/^\.\//, "");
}

/**
 * True if path is a wiki content page we allow auditing.
 * @param {string} relPath
 */
export function isAllowedWikiTarget(relPath) {
  const raw = String(relPath || "").replace(/\\/g, "/");
  if (raw.split("/").some((part) => !part || part === "." || part === "..")) return false;
  const p = normalizeVaultPath(raw);
  if (/^(?:\/|[A-Za-z]:\/)/.test(p)) return false;
  if (!p.toLowerCase().endsWith(".md")) return false;
  if (p.startsWith("audit/") || p.includes("/audit/")) return false;
  return p.startsWith("wiki/");
}

/**
 * @param {string} fullText
 * @param {number} from  // 0-based char offset inclusive
 * @param {number} to    // 0-based char offset exclusive
 */
export function lineRangeFromOffsets(fullText, from, to) {
  const start = Math.max(0, Math.min(from, fullText.length));
  const end = Math.max(start, Math.min(to, fullText.length));
  let line = 1;
  let startLine = 1;
  let endLine = 1;
  for (let i = 0; i < fullText.length; i++) {
    if (i === start) startLine = line;
    if (i < end && fullText[i] === "\n") {
      // end is exclusive; line of last included char
    }
    if (i === end - 1 || (end === start && i === start)) endLine = line;
    if (fullText[i] === "\n") line++;
  }
  if (end === start) endLine = startLine;
  else {
    // recompute endLine as line of character at end-1
    line = 1;
    for (let i = 0; i < end; i++) {
      if (i === end - 1) endLine = line;
      if (fullText[i] === "\n") line++;
    }
  }
  return [startLine, Math.max(startLine, endLine)];
}

/**
 * @param {string} fullText
 * @param {number} from
 * @param {number} to
 * @param {number} [max]
 */
export function contextAround(fullText, from, to, max = CONTEXT_MAX) {
  const before = fullText.slice(Math.max(0, from - max), from);
  const after = fullText.slice(to, Math.min(fullText.length, to + max));
  return {
    anchor_before: before.slice(-max),
    anchor_after: after.slice(0, max),
  };
}

/**
 * @typedef {object} AuditDraft
 * @property {string} target
 * @property {string} anchor_text
 * @property {string} [anchor_before]
 * @property {string} [anchor_after]
 * @property {[number, number]} [target_lines]
 * @property {string} severity
 * @property {string} comment
 * @property {string} [author]
 * @property {string} [source]
 * @property {Date} [now]
 * @property {string} [hex4] fixed for tests
 * @property {string} [stamp] fixed for tests
 * @property {string} [created] fixed for tests
 */

/**
 * @param {AuditDraft} draft
 * @returns {{ ok: true, filename: string, body: string, id: string } | { ok: false, error: string }}
 */
export function buildAuditMarkdown(draft) {
  const target = normalizeVaultPath(draft.target || "");
  const anchor_text = draft.anchor_text ?? "";
  const comment = String(draft.comment || "").trim();
  const severity = draft.severity || "warn";
  const author = String(draft.author || "you").trim() || "you";
  const source = draft.source || SOURCE_PLUGIN;

  if (!anchor_text.trim()) return { ok: false, error: "empty_selection" };
  if (!comment) return { ok: false, error: "empty_comment" };
  if (!target) return { ok: false, error: "empty_target" };
  if (!isAllowedWikiTarget(target)) return { ok: false, error: "target_not_wiki_page" };
  if (!VALID_SEVERITIES.includes(severity)) return { ok: false, error: "bad_severity" };
  if (!["manual", "agent", "obsidian-plugin", "web-viewer"].includes(source)) {
    return { ok: false, error: "bad_source" };
  }

  const parts = nowParts(draft.now);
  const stamp = draft.stamp || parts.stamp;
  const created = draft.created || parts.created;
  const hex4 = draft.hex4 || parts.hex4;
  const id = `${stamp}-${hex4}`;
  const slug = slugify(comment || anchor_text);
  const filename = `${stamp}-${slug}.md`;
  const lines = draft.target_lines || [1, 1];
  const start = Math.max(1, Number(lines[0]) || 1);
  const end = Math.max(start, Number(lines[1]) || start);
  const before = String(draft.anchor_before ?? "").slice(-CONTEXT_MAX);
  const after = String(draft.anchor_after ?? "").slice(0, CONTEXT_MAX);

  const body =
    `---\n` +
    `id: ${id}\n` +
    `target: ${target}\n` +
    `target_lines: [${start}, ${end}]\n` +
    `anchor_before: ${yamlEscape(before)}\n` +
    `anchor_text: ${yamlEscape(anchor_text)}\n` +
    `anchor_after: ${yamlEscape(after)}\n` +
    `severity: ${severity}\n` +
    `author: ${author}\n` +
    `source: ${source}\n` +
    `created: ${created}\n` +
    `status: open\n` +
    `---\n\n` +
    `# Comment\n\n` +
    `${comment}\n\n` +
    `# Resolution\n\n` +
    `<!-- Filled when processed and moved to audit/resolved/ -->\n`;

  return { ok: true, filename, body, id };
}

/**
 * Build codex-facing short prompt after write.
 * @param {string} relAuditPath
 * @param {string} [id]
 */
export function processHint(relAuditPath, id) {
  const path = normalizeVaultPath(relAuditPath);
  if (id) {
    return `处理批注：请处理 open audit ${id}（${path}）。`;
  }
  return `处理批注：请处理 open audit（${path}）。`;
}
