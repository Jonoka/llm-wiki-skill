/**
 * Offline knowledge-graph.html helper (V5 scheme A):
 * prefill audit target from selected graph node + text selection,
 * then download open audit markdown (does NOT write vault disk).
 *
 * Exposes window.LlmWikiGraphAuditPanel
 * Contract: references/audit-contract-v1.md
 */
(function (global) {
  "use strict";

  var VALID_SEVERITIES = ["error", "warn", "suggest", "info"];
  var CONTEXT_MAX = 200;

  function slugify(text, maxLen) {
    maxLen = maxLen || 40;
    var s = String(text || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^\w\u4e00-\u9fff\-]+/g, "")
      .replace(/^-+|-+$/g, "")
      .slice(0, maxLen);
    return s || "note";
  }

  function yamlEscape(s) {
    return (
      '"' +
      String(s == null ? "" : s)
        .replace(/\\/g, "\\\\")
        .replace(/"/g, '\\"')
        .replace(/\r/g, "")
        .replace(/\n/g, "\\n") +
      '"'
    );
  }

  function pad(n) {
    return String(n).padStart ? String(n).padStart(2, "0") : (n < 10 ? "0" + n : "" + n);
  }

  function nowParts(d) {
    d = d || new Date();
    var stamp =
      d.getFullYear() +
      pad(d.getMonth() + 1) +
      pad(d.getDate()) +
      "-" +
      pad(d.getHours()) +
      pad(d.getMinutes()) +
      pad(d.getSeconds());
    var offMin = -d.getTimezoneOffset();
    var sign = offMin >= 0 ? "+" : "-";
    var abs = Math.abs(offMin);
    var tz = sign + pad(Math.floor(abs / 60)) + ":" + pad(abs % 60);
    var created =
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
    var hex4 = Math.floor(Math.random() * 0x10000)
      .toString(16)
      .padStart(4, "0");
    return { stamp: stamp, created: created, hex4: hex4 };
  }

  /**
   * Normalize node.source_path to vault-relative wiki/... path.
   */
  function toWikiTarget(sourcePath) {
    if (!sourcePath) return "";
    var p = String(sourcePath).replace(/\\/g, "/");
    var idx = p.indexOf("wiki/");
    if (idx >= 0) return p.slice(idx);
    if (p.indexOf("/wiki/") >= 0) return p.slice(p.indexOf("/wiki/") + 1);
    // bare filename under entities etc.
    if (/\.md$/i.test(p) && p.indexOf("/") < 0) return "wiki/entities/" + p;
    return p.replace(/^\//, "");
  }

  function isAllowedWikiTarget(relPath) {
    var p = String(relPath || "").replace(/\\/g, "/");
    if (!/\.md$/i.test(p)) return false;
    if (p.indexOf("audit/") === 0 || p.indexOf("/audit/") >= 0) return false;
    return p.indexOf("wiki/") === 0;
  }

  function getDomSelectionText() {
    try {
      var sel = global.getSelection && global.getSelection();
      if (!sel || sel.isCollapsed) return "";
      return String(sel.toString() || "");
    } catch (_) {
      return "";
    }
  }

  function buildAuditMarkdown(draft) {
    var target = String(draft.target || "").replace(/\\/g, "/");
    var anchor_text = draft.anchor_text == null ? "" : String(draft.anchor_text);
    var comment = String(draft.comment || "").trim();
    var severity = draft.severity || "warn";
    var author = String(draft.author || "you").trim() || "you";
    var source = draft.source || "web-viewer";

    if (!anchor_text.trim()) return { ok: false, error: "empty_selection" };
    if (!comment) return { ok: false, error: "empty_comment" };
    if (!target) return { ok: false, error: "empty_target" };
    if (!isAllowedWikiTarget(target)) return { ok: false, error: "target_not_wiki_page" };
    if (VALID_SEVERITIES.indexOf(severity) < 0) return { ok: false, error: "bad_severity" };

    var parts = nowParts(draft.now);
    var stamp = draft.stamp || parts.stamp;
    var created = draft.created || parts.created;
    var hex4 = draft.hex4 || parts.hex4;
    var id = stamp + "-" + hex4;
    var filename = stamp + "-" + slugify(comment || anchor_text) + ".md";
    var lines = draft.target_lines || [1, 1];
    var start = Math.max(1, Number(lines[0]) || 1);
    var end = Math.max(start, Number(lines[1]) || start);
    var before = String(draft.anchor_before || "").slice(-CONTEXT_MAX);
    var after = String(draft.anchor_after || "").slice(0, CONTEXT_MAX);

    var body =
      "---\n" +
      "id: " + id + "\n" +
      "target: " + target + "\n" +
      "target_lines: [" + start + ", " + end + "]\n" +
      "anchor_before: " + yamlEscape(before) + "\n" +
      "anchor_text: " + yamlEscape(anchor_text) + "\n" +
      "anchor_after: " + yamlEscape(after) + "\n" +
      "severity: " + severity + "\n" +
      "author: " + author + "\n" +
      "source: " + source + "\n" +
      "created: " + created + "\n" +
      "status: open\n" +
      "---\n\n" +
      "# Comment\n\n" +
      comment +
      "\n\n" +
      "# Resolution\n\n" +
      "<!-- Filled when processed and moved to audit/resolved/ -->\n";

    return { ok: true, filename: filename, body: body, id: id };
  }

  function downloadText(filename, body) {
    var blob = new Blob([body], { type: "text/markdown;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    setTimeout(function () {
      try {
        URL.revokeObjectURL(a.href);
      } catch (_) {}
    }, 1000);
  }

  function findNode(graphData, nodeId) {
    if (!graphData || !graphData.nodes || nodeId == null) return null;
    for (var i = 0; i < graphData.nodes.length; i++) {
      if (graphData.nodes[i] && graphData.nodes[i].id === nodeId) return graphData.nodes[i];
    }
    return null;
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "className") node.className = attrs[k];
        else if (k === "text") node.textContent = attrs[k];
        else if (k === "html") node.innerHTML = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) {
      if (c) node.appendChild(c);
    });
    return node;
  }

  function mount(options) {
    options = options || {};
    var getGraphData = options.getGraphData || function () { return null; };
    var getSelectedNodeId = options.getSelectedNodeId || function () { return null; };
    var headerHost = options.headerHost || document.querySelector(".offline-badges");

    // styles once
    if (!document.getElementById("llm-wiki-graph-audit-style")) {
      var style = document.createElement("style");
      style.id = "llm-wiki-graph-audit-style";
      style.textContent =
        ".llm-wiki-audit-btn{cursor:pointer;border:1px solid rgba(90,70,40,.25);background:rgba(255,252,244,.95);color:#3a3026;border-radius:999px;padding:4px 10px;font:inherit;font-size:12px}" +
        ".llm-wiki-audit-btn:hover{background:#fff}" +
        ".llm-wiki-audit-mask{position:fixed;inset:0;background:rgba(30,24,16,.35);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px}" +
        ".llm-wiki-audit-modal{width:min(520px,100%);max-height:90vh;overflow:auto;background:#fffdf8;border:1px solid #d9cfc0;border-radius:14px;padding:16px 18px;box-shadow:0 12px 40px rgba(0,0,0,.18);color:#1f1a14;font:14px/1.5 system-ui,sans-serif}" +
        ".llm-wiki-audit-modal h2{margin:0 0 6px;font-size:1.1rem}" +
        ".llm-wiki-audit-modal p.hint{margin:0 0 12px;color:#6b6258;font-size:.9rem}" +
        ".llm-wiki-audit-modal label{display:block;margin:10px 0 4px;font-size:.82rem;color:#6b6258}" +
        ".llm-wiki-audit-modal input,.llm-wiki-audit-modal textarea,.llm-wiki-audit-modal select{width:100%;box-sizing:border-box;border:1px solid #d9cfc0;border-radius:8px;padding:8px;font:inherit;background:#fff}" +
        ".llm-wiki-audit-modal textarea{min-height:72px;resize:vertical}" +
        ".llm-wiki-audit-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}" +
        ".llm-wiki-audit-actions button{border:0;border-radius:999px;padding:8px 14px;font:inherit;cursor:pointer}" +
        ".llm-wiki-audit-actions .primary{background:#8b3a2b;color:#fff}" +
        ".llm-wiki-audit-actions .ghost{background:transparent;border:1px solid #d9cfc0;color:#1f1a14}" +
        ".llm-wiki-audit-status{min-height:1.2em;margin-top:8px;font-size:.9rem;color:#2f5d3a}" +
        ".llm-wiki-audit-status.err{color:#8b3a2b}";
      document.head.appendChild(style);
    }

    if (headerHost && !headerHost.querySelector("[data-testid='offline-audit-btn']")) {
      var btn = el("button", {
        className: "llm-wiki-audit-btn",
        type: "button",
        "data-testid": "offline-audit-btn",
        "aria-label": "记 llm-wiki 批注",
        text: "记批注",
      });
      btn.addEventListener("click", function () {
        openModal();
      });
      headerHost.appendChild(btn);
    }

    function openModal() {
      var graphData = getGraphData();
      var nodeId = getSelectedNodeId();
      var node = findNode(graphData, nodeId);
      var target = node ? toWikiTarget(node.source_path || node.path || "") : "";
      var selectedText = getDomSelectionText();
      // if no DOM selection but node has content and user didn't select, leave empty (must select or paste)
      var mask = el("div", { className: "llm-wiki-audit-mask", "data-testid": "offline-audit-modal" });
      var modal = el("div", { className: "llm-wiki-audit-modal" });
      modal.appendChild(el("h2", { text: "记 llm-wiki 批注（图谱）" }));
      modal.appendChild(
        el("p", {
          className: "hint",
          text:
            "方案 A：下载 open audit 到本机，再放进知识库 audit/，对 Codex 说「处理批注」。不会直接写 vault 磁盘。",
        }),
      );

      modal.appendChild(el("label", { text: "节点" }));
      var nodeInfo = el("input", { type: "text", readonly: "readonly" });
      nodeInfo.value = node
        ? (node.label || node.id) + (target ? " → " + target : "（无 source_path）")
        : "（未选中节点 — 请先点图谱节点，或在下方手填 target）";
      modal.appendChild(nodeInfo);

      modal.appendChild(el("label", { text: "target（相对知识库根）" }));
      var targetInput = el("input", { type: "text", "data-testid": "offline-audit-target" });
      targetInput.value = target;
      targetInput.placeholder = "wiki/entities/Foo.md";
      modal.appendChild(targetInput);

      modal.appendChild(el("label", { text: "选中原文 anchor_text（可在抽屉正文中选中后点「记批注」）" }));
      var anchorTa = el("textarea", { "data-testid": "offline-audit-anchor" });
      anchorTa.value = selectedText;
      anchorTa.placeholder = "在图谱右侧正文中选中文字，或在此粘贴";
      modal.appendChild(anchorTa);

      modal.appendChild(el("label", { text: "severity" }));
      var sev = el("select", { "data-testid": "offline-audit-severity" });
      VALID_SEVERITIES.forEach(function (s) {
        var o = el("option", { value: s, text: s });
        if (s === "warn") o.selected = true;
        sev.appendChild(o);
      });
      modal.appendChild(sev);

      modal.appendChild(el("label", { text: "author" }));
      var authorInput = el("input", { type: "text", value: "you" });
      modal.appendChild(authorInput);

      modal.appendChild(el("label", { text: "Comment" }));
      var commentTa = el("textarea", { "data-testid": "offline-audit-comment" });
      commentTa.placeholder = "实际应为…；依据…";
      modal.appendChild(commentTa);

      var status = el("div", { className: "llm-wiki-audit-status", "data-testid": "offline-audit-status" });
      var actions = el("div", { className: "llm-wiki-audit-actions" });
      var cancel = el("button", { className: "ghost", type: "button", text: "取消" });
      var download = el("button", {
        className: "primary",
        type: "button",
        text: "下载 audit .md",
        "data-testid": "offline-audit-download",
      });
      cancel.addEventListener("click", function () {
        mask.remove();
      });
      download.addEventListener("click", function () {
        var built = buildAuditMarkdown({
          target: targetInput.value.trim(),
          anchor_text: anchorTa.value,
          comment: commentTa.value,
          severity: sev.value,
          author: authorInput.value,
          source: "web-viewer",
          target_lines: [1, 1],
        });
        if (!built.ok) {
          status.className = "llm-wiki-audit-status err";
          status.textContent = "无法生成：" + built.error;
          return;
        }
        downloadText(built.filename, built.body);
        status.className = "llm-wiki-audit-status";
        status.textContent =
          "已下载 " + built.filename + " → 请移到知识库 audit/ ，然后对 Codex 说「处理批注」";
      });
      actions.appendChild(cancel);
      actions.appendChild(download);
      modal.appendChild(actions);
      modal.appendChild(status);
      mask.appendChild(modal);
      mask.addEventListener("click", function (ev) {
        if (ev.target === mask) mask.remove();
      });
      document.body.appendChild(mask);
      commentTa.focus();
    }

    return {
      openModal: openModal,
      toWikiTarget: toWikiTarget,
      buildAuditMarkdown: buildAuditMarkdown,
    };
  }

  global.LlmWikiGraphAuditPanel = {
    mount: mount,
    toWikiTarget: toWikiTarget,
    buildAuditMarkdown: buildAuditMarkdown,
    isAllowedWikiTarget: isAllowedWikiTarget,
    slugify: slugify,
  };
})(typeof window !== "undefined" ? window : globalThis);
