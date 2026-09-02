import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import vm from "node:vm";

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

test("lightweight audit entry rejects absolute and dot-segment targets", () => {
  const html = readFileSync(path.join(repo, "skill-assets/audit-entry.html"), "utf8");
  const source = html.match(/function isAllowedWikiTarget\(relPath\) \{[\s\S]*?\n    \}/)?.[0];
  assert.ok(source, "target guard must remain embedded in the standalone page");
  const sandbox = {};
  vm.runInNewContext(`${source}; result = isAllowedWikiTarget;`, sandbox);
  assert.equal(sandbox.result("wiki/entities/Foo.md"), true);
  for (const target of [
    "wiki/../../../../SKILL.md",
    "wiki/entities/../Foo.md",
    "/wiki/entities/Foo.md",
    "D:/wiki/entities/Foo.md",
  ]) {
    assert.equal(sandbox.result(target), false, target);
  }
});
