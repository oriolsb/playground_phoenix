// The test runner's config. It extends vite.config.ts, which stays as it is.
import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      environmentOptions: { jsdom: { url: "http://localhost:5173/" } },
      setupFiles: ["./tests/setup.ts"],
      include: ["tests/component/**/*.test.tsx", "tests/mocks/**/*.test.ts", "tests/fitness/**/*.test.ts"],
      testTimeout: 15000,
    },
  }),
);
