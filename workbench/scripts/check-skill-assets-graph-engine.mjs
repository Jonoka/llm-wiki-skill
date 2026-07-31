/**
 * Fail if skill-assets engine.iife.js drifted from packages/graph-engine build.
 *
 * Intended for CI / `npm run quality-and-tests` after build-graph, and for
 * release gates. Normalization matches scripts/sync-graph-engine-dist.sh:
 * strip //# sourceMappingURL, CRLF→LF, single trailing newline, then SHA-256.
 *
 * Usage:
 *   node workbench/scripts/check-skill-assets-graph-engine.mjs
 *   npm run check:skill-assets-graph
 */
import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const PKG_IIFE = path.join(REPO_ROOT, "packages/graph-engine/dist/engine.iife.js");
const ASSET_IIFE = path.join(REPO_ROOT, "skill-assets/graph-engine/dist/engine.iife.js");
const BUILD_INFO = path.join(REPO_ROOT, "skill-assets/graph-engine/dist/BUILD-INFO.txt");

export function normalizeIife(text) {
	return `${String(text)
		.replace(/\r\n/g, "\n")
		.replace(/\r/g, "\n")
		.replace(/\/\/# sourceMappingURL=.*$/m, "")
		.replace(/\s+$/u, "")}\n`;
}

export function sha256Normalized(text) {
	return createHash("sha256").update(normalizeIife(text), "utf8").digest("hex");
}

export function checkSkillAssetsGraphEngine({
	repoRoot = REPO_ROOT,
	pkgPath = path.join(repoRoot, "packages/graph-engine/dist/engine.iife.js"),
	assetPath = path.join(repoRoot, "skill-assets/graph-engine/dist/engine.iife.js"),
	infoPath = path.join(repoRoot, "skill-assets/graph-engine/dist/BUILD-INFO.txt"),
} = {}) {
	const errors = [];
	if (!existsSync(pkgPath)) {
		errors.push(
			`missing packages build: ${pkgPath}\n  Run: npm run build -w @llm-wiki/graph-engine`,
		);
		return { ok: false, errors };
	}
	if (!existsSync(assetPath)) {
		errors.push(
			`missing skill-assets IIFE: ${assetPath}\n  Run: npm run build -w @llm-wiki/graph-engine && bash scripts/sync-graph-engine-dist.sh`,
		);
		return { ok: false, errors };
	}

	const pkgHash = sha256Normalized(readFileSync(pkgPath, "utf8"));
	const assetHash = sha256Normalized(readFileSync(assetPath, "utf8"));
	if (pkgHash !== assetHash) {
		errors.push(
			[
				"skill-assets graph-engine IIFE is out of date (dist drift)",
				`  packages/graph-engine/dist  sha256=${pkgHash}`,
				`  skill-assets/.../engine.iife.js sha256=${assetHash}`,
				"  Fix: npm run build -w @llm-wiki/graph-engine && bash scripts/sync-graph-engine-dist.sh",
				"  Then commit skill-assets/graph-engine/dist/",
			].join("\n"),
		);
	}

	if (existsSync(infoPath)) {
		const info = readFileSync(infoPath, "utf8");
		const match = info.match(/^sha256=(.+)$/m);
		const infoHash = match?.[1]?.trim() ?? "";
		if (infoHash && infoHash !== assetHash) {
			errors.push(
				[
					"BUILD-INFO.txt sha256 does not match skill-assets IIFE",
					`  BUILD-INFO sha256=${infoHash}`,
					`  file      sha256=${assetHash}`,
					"  Fix: bash scripts/sync-graph-engine-dist.sh",
				].join("\n"),
			);
		}
	}

	return {
		ok: errors.length === 0,
		errors,
		pkgHash,
		assetHash,
	};
}

function main() {
	const result = checkSkillAssetsGraphEngine();
	if (!result.ok) {
		for (const err of result.errors) {
			console.error(`ERROR: ${err}`);
		}
		process.exitCode = 1;
		return;
	}
	console.log(
		`OK: skill-assets graph-engine IIFE matches packages build (sha256=${result.assetHash})`,
	);
}

const isDirect =
	process.argv[1] &&
	path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isDirect) {
	main();
}
