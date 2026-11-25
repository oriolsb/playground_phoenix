// Shared helpers for the tests of the game screen.
import { render, screen } from "@testing-library/react";
import { createElement } from "react";
import App from "../../src/App";
import { SID } from "../mocks/bodies";

export const api = (path: string) => `http://localhost:5173/api${path}`;

/** Open the client as a returning player: the sid is in the browser already. */
export async function openTheGameAt(title = "BRICK LANE") {
  localStorage.setItem("katacombs.sid", SID);
  const view = render(createElement(App));
  await screen.findByRole("heading", { name: title });
  return view;
}

export const messages = () => screen.getByRole("list", { name: "messages" });

/**
 * Wait until a check passes, polling with setTimeout. Use it instead of
 * waitFor in a test that fakes setInterval: waitFor polls with setInterval,
 * so it would then re-check only when the DOM changes.
 */
export async function until(check: () => void, timeout = 2000) {
  const deadline = Date.now() + timeout;
  for (;;) {
    try {
      check();
      return;
    } catch (failure) {
      if (Date.now() > deadline) throw failure;
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  }
}
