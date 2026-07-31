import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
	normalizeIife,
	sha256Normalized,
	checkSkillAssetsGraphEngine,
} from "./check-skill-assets-graph-engine.mjs";

test("normalizeIife strips source map and normalizes newlines", () => {
	const raw = "code();\r\n//# sourceMappingURL=engine.iife.js.map\r\n";
	assert.equal(normalizeIife(raw), "code();\n");
	assert.equal(
		sha256Normalized(raw),
		sha256Normalized("code();\n"),
	);
});

test("check passes when hashes match and BUILD-INFO agrees", async () => {
	const root = await mkdtemp(path.join(tmpdir(), "skill-assets-graph-"));
	try {
		const body = "export const engine = 1;\n//# sourceMappingURL=x.map\n";
		const pkg = path.join(root, "packages/graph-engine/dist/engine.iife.js");
		const asset = path.join(root, "skill-assets/graph-engine/dist/engine.iife.js");
		const info = path.join(root, "skill-assets/graph-engine/dist/BUILD-INFO.txt");
		await mkdir(path.dirname(pkg), { recursive: true });
		await mkdir(path.dirname(asset), { recursive: true });
		await writeFile(pkg, body, "utf8");
		await writeFile(asset, normalizeIife(body), "utf8");
		const hash = sha256Normalized(body);
		await writeFile(info, `sha256=${hash}\nbytes=1\n`, "utf8");

		const result = checkSkillAssetsGraphEngine({
			repoRoot: root,
			pkgPath: pkg,
			assetPath: asset,
			infoPath: info,
		});
		assert.equal(result.ok, true);
		assert.equal(result.assetHash, hash);
	} finally {
		await rm(root, { recursive: true, force: true });
	}
});

test("check fails on content drift", async () => {
	const root = await mkdtemp(path.join(tmpdir(), "skill-assets-graph-"));
	try {
		const pkg = path.join(root, "packages/graph-engine/dist/engine.iife.js");
		const asset = path.join(root, "skill-assets/graph-engine/dist/engine.iife.js");
		await mkdir(path.dirname(pkg), { recursive: true });
		await mkdir(path.dirname(asset), { recursive: true });
		await writeFile(pkg, "version-a\n", "utf8");
		await writeFile(asset, "version-b\n", "utf8");

		const result = checkSkillAssetsGraphEngine({
			repoRoot: root,
			pkgPath: pkg,
			assetPath: asset,
			infoPath: path.join(root, "missing-info"),
		});
		assert.equal(result.ok, false);
		assert.match(result.errors.join("\n"), /dist drift/);
	} finally {
		await rm(root, { recursive: true, force: true });
	}
});

test("check fails when packages dist missing", () => {
	const result = checkSkillAssetsGraphEngine({
		repoRoot: path.join(tmpdir(), "no-such-root-xyz"),
		pkgPath: path.join(tmpdir(), "no-pkg-iife.js"),
		assetPath: path.join(tmpdir(), "no-asset-iife.js"),
	});
	assert.equal(result.ok, false);
	assert.match(result.errors.join("\n"), /missing packages build/);
});
