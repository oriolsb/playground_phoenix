// WEB-OPS-1: the production JavaScript bundle is at most 250 KB, gzipped.
// Source: the workshop (brown_field/README.md). Players open the game on a
// slow network.
import { spawnSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { gzipSync } from "node:zlib";
import { describe, expect, it } from "vitest";

const LIMIT_BYTES = 250 * 1024;

describe("the production bundle", () => {
  it("WEB-OPS-1: the JavaScript of a production build is at most 250 KB gzipped", () => {
    const outDir = mkdtempSync(join(tmpdir(), "katacombs-bundle-"));
    const build = spawnSync("npx", ["vite", "build", "--outDir", outDir, "--emptyOutDir", "--logLevel", "error"], {
      encoding: "utf-8",
    });
    expect(build.status, build.stderr).toBe(0);
    const assets = join(outDir, "assets");
    const scripts = readdirSync(assets).filter((name) => name.endsWith(".js"));
    expect(scripts.length).toBeGreaterThan(0);
    const gzipped = scripts.reduce((total, name) => total + gzipSync(readFileSync(join(assets, name))).length, 0);
    console.info(`WEB-OPS-1: ${scripts.length} script(s), ${(gzipped / 1024).toFixed(1)} KB gzipped`);
    expect(gzipped).toBeLessThanOrEqual(LIMIT_BYTES);
  }, 60000);
});
