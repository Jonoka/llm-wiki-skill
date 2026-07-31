import assert from "node:assert/strict";
import { mkdirSync, writeFileSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { spawnSync } from "node:child_process";

import {
  buildAuditMarkdown,
  isAllowedWikiTarget,
  lineRangeFromOffsets,
  processHint,
  slugify,
  yamlEscape,
} from "../../obsidian-plugin/llm-wiki-audit/src/audit-core.js";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

test("slugify and yamlEscape", () => {
  assert.equal(slugify("Hello 世界!!"), "hello-世界");
  assert.equal(yamlEscape('a"b\nc'), '"a\\"b\\nc"');
});

test("isAllowedWikiTarget", () => {
  assert.equal(isAllowedWikiTarget("wiki/entities/Foo.md"), true);
  assert.equal(isAllowedWikiTarget("audit/x.md"), false);
  assert.equal(isAllowedWikiTarget("index.md"), false);
});

test("lineRangeFromOffsets", () => {
  const text = "a\nbb\nccc\n";
  // "bb" is line 2
  const from = text.indexOf("bb");
  const to = from + 2;
  assert.deepEqual(lineRangeFromOffsets(text, from, to), [2, 2]);
});

test("buildAuditMarkdown happy path matches contract fields", () => {
  const r = buildAuditMarkdown({
    target: "wiki/entities/SampleConcept.md",
    anchor_text: "知识库纠错应写入 audit 目录而不是只留在聊天里。",
    anchor_before: "## 概述\n\n",
    anchor_after: "\n\n## 细节",
    target_lines: [11, 11],
    severity: "warn",
    comment: "V2 unit test comment",
    author: "tester",
    source: "obsidian-plugin",
    stamp: "20260731-160000",
    created: "2026-07-31T16:00:00+08:00",
    hex4: "abcd",
  });
  assert.equal(r.ok, true);
  if (!r.ok) return;
  assert.equal(r.id, "20260731-160000-abcd");
  assert.match(r.filename, /^20260731-160000-/);
  assert.match(r.body, /source: obsidian-plugin/);
  assert.match(r.body, /status: open/);
  assert.match(r.body, /# Comment/);
  assert.match(r.body, /V2 unit test comment/);
  assert.doesNotMatch(r.body, /status: resolved/);
});

test("buildAuditMarkdown rejects empty selection and non-wiki", () => {
  assert.equal(
    buildAuditMarkdown({
      target: "wiki/x.md",
      anchor_text: "  ",
      comment: "c",
      severity: "warn",
    }).ok,
    false,
  );
  assert.equal(
    buildAuditMarkdown({
      target: "notes/x.md",
      anchor_text: "hi",
      comment: "c",
      severity: "warn",
    }).error,
    "target_not_wiki_page",
  );
});

test("processHint", () => {
  assert.match(processHint("audit/a.md", "id1"), /处理批注/);
});

test("written file passes check-audit-compat", () => {
  const fixture = path.join(REPO, "tests/fixtures/audit-v1-wiki");
  const tmp = mkdtempSync(path.join(tmpdir(), "v2-plugin-"));
  // minimal copy: entity + empty audit
  mkdirSync(path.join(tmp, "wiki/entities"), { recursive: true });
  mkdirSync(path.join(tmp, "audit/resolved"), { recursive: true });
  writeFileSync(
    path.join(tmp, "wiki/entities/SampleConcept.md"),
    readFileSync(path.join(fixture, "wiki/entities/SampleConcept.md")),
  );
  const built = buildAuditMarkdown({
    target: "wiki/entities/SampleConcept.md",
    anchor_text: "知识库纠错应写入 audit 目录而不是只留在聊天里。",
    anchor_before: "## 概述\n\n",
    anchor_after: "\n\n## 细节",
    target_lines: [11, 11],
    severity: "suggest",
    comment: "plugin-core generated open audit",
    author: "v2-test",
    source: "obsidian-plugin",
    stamp: "20260731-161000",
    created: "2026-07-31T16:10:00+08:00",
    hex4: "ef01",
  });
  assert.equal(built.ok, true);
  if (!built.ok) return;
  writeFileSync(path.join(tmp, "audit", built.filename), built.body, "utf8");

  const py = spawnSync(
    process.platform === "win32" ? "python" : "python3",
    [path.join(REPO, "scripts/check-audit-compat.py"), tmp],
    { encoding: "utf8" },
  );
  assert.equal(py.status, 0, py.stdout + py.stderr);
});
