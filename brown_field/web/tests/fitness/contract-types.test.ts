// Type-drift fitness: src/api.ts repeats the server's JSON shapes by hand.
// Types generated from the contract catch a drift at compile time.
import { spawnSync } from "node:child_process";
import { describe, expect, it } from "vitest";

const run = (args: string[]) => spawnSync("npx", args, { encoding: "utf-8", cwd: process.cwd() });

describe("the client's types and the server's contract", () => {
  it("WEB-FIT-1: tsc accepts the pinned answers of contract-types.check.ts", () => {
    const generated = run(["openapi-typescript", "../spec/openapi.yaml", "-o", "tests/fitness/generated/openapi.d.ts"]);
    expect(generated.status, generated.stderr).toBe(0);
    const compiled = run(["tsc", "-p", "tests/fitness/tsconfig.json"]);
    expect(compiled.status, compiled.stdout + compiled.stderr).toBe(0);
  }, 60000);
});
