// Browser end-to-end: the real server and the production build of the client.
// The server writes its files to a new temporary folder, never to the repo.
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { defineConfig } from "@playwright/test";

const files = process.env.KATACOMBS_E2E_DIR ?? mkdtempSync(join(tmpdir(), "katacombs-e2e-"));
process.env.KATACOMBS_E2E_DIR = files;

export default defineConfig({
  testDir: "tests/e2e",
  fullyParallel: false,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:4173", trace: "retain-on-failure" },
  webServer: [
    {
      // CONF-3: python -m brown_field serves on 127.0.0.1:8000.
      command: "uv run python -m brown_field",
      cwd: "../..",
      url: "http://127.0.0.1:8000/leaderboard",
      reuseExistingServer: false,
      timeout: 60_000,
      env: {
        KATACOMBS_DB: join(files, "katacombs.db"),
        KATACOMBS_HIGHSCORES: join(files, "highscores.jsonl"),
      },
    },
    {
      // The production build, served by vite preview with the /api proxy.
      command: "npx vite build --logLevel error && npx vite preview --host 127.0.0.1 --port 4173 --strictPort",
      url: "http://127.0.0.1:4173",
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
