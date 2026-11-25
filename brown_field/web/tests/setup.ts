// Runs before each component test file.
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, beforeEach, vi } from "vitest";
import { requests, server } from "./mocks/server";

// The client calls relative URLs (`/api/...`), as a browser does. Node's
// fetch needs an absolute URL, so the tests resolve it against the page.
const nodeFetch = globalThis.fetch;
globalThis.fetch = ((input: RequestInfo | URL, init?: RequestInit) =>
  nodeFetch(typeof input === "string" ? new URL(input, window.location.href) : input, init)) as typeof fetch;

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
beforeEach(() => {
  localStorage.clear();
  requests.length = 0;
});
afterEach(() => {
  cleanup();
  server.resetHandlers();
  vi.useRealTimers();
});
afterAll(() => server.close());
