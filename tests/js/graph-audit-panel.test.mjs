import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { createRequire } from "node:module";
import vm from "node:vm";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const PANEL = path.join(REPO, "skill-assets/graph-audit-panel.js");

function loadPanel() {
  const code = readFileSync(PANEL, "utf8");
  const sandbox = { console, globalThis: {} };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.runInNewContext(code, sandbox, { filename: "graph-audit-panel.js" });
  return sandbox.LlmWikiGraphAuditPanel;
}

test("toWikiTarget normalizes absolute and relative paths", () => {
  const api = loadPanel();
  assert.equal(api.toWikiTarget("wiki/entities/Foo.md"), "wiki/entities/Foo.md");
  assert.equal(
    api.toWikiTarget("D:/wikis/demo/wiki/entities/Foo.md"),
    "wiki/entities/Foo.md",
  );
  assert.equal(api.toWikiTarget("/fake/wiki/entities/A.md"), "wiki/entities/A.md");
});

test("buildAuditMarkdown produces contract open file", () => {
  const api = loadPanel();
  const r = api.buildAuditMarkdown({
    target: "wiki/entities/SampleConcept.md",
    anchor_text: "知识库纠错应写入 audit 目录而不是只留在聊天里。",
    comment: "V5 unit",
    severity: "warn",
    author: "t",
    source: "web-viewer",
    stamp: "20260801-120000",
    created: "2026-08-01T12:00:00+08:00",
    hex4: "abcd",
  });
  assert.equal(r.ok, true);
  assert.match(r.body, /source: web-viewer/);
  assert.match(r.body, /status: open/);
  assert.match(r.body, /V5 unit/);
});

test("rejects non-wiki targets", () => {
  const api = loadPanel();
  assert.equal(
    api.buildAuditMarkdown({
      target: "notes/x.md",
      anchor_text: "a",
      comment: "c",
      severity: "warn",
    }).error,
    "target_not_wiki_page",
  );
});
