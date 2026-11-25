// The session: the sid in the browser, a lost connection, SAVE and QUIT.
// Rule IDs: brown_field/web/spec/specification.md.
import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import App from "../../src/App";
import { SID, error } from "../mocks/bodies";
import { sentTo, server } from "../mocks/server";
import { api, messages, openTheGameAt, until } from "./game";

const unknownPlayer = () =>
  server.use(
    http.get(api("/player/:sid/location"), () =>
      HttpResponse.json(error(404, `PLAYER ${SID} NOT FOUND.`), { status: 404 }),
    ),
  );

describe("the session", () => {
  it("WEB-SESSION-1: a sid kept in the browser resumes the game after a reload", async () => {
    await openTheGameAt("BRICK LANE");
    expect(screen.queryByRole("button", { name: "START" })).toBeNull();
    expect(sentTo("GET", `/api/player/${SID}/location`).length).toBeGreaterThanOrEqual(1);
  });

  it("WEB-SESSION-2: an unknown sid shows CONNECTION LOST, retries at once, then every 2 s", async () => {
    vi.useFakeTimers({ toFake: ["setInterval"] });
    unknownPlayer();
    localStorage.setItem("katacombs.sid", SID);
    render(<App />);
    expect(await screen.findByRole("status")).toHaveTextContent("CONNECTION LOST. RETRYING...");
    const asked = () => sentTo("GET", `/api/player/${SID}/location`).length;
    // The first request fails; turning to "lost" runs the effect again, so the
    // client retries once at once, then every 2 s.
    // Let the requests settle with no interval tick: exactly 2, not 1, and no more.
    await new Promise((resolve) => setTimeout(resolve, 300));
    expect(asked()).toBe(2);
    await act(async () => {
      vi.advanceTimersByTime(2000);
    });
    await until(() => expect(asked()).toBe(3));
    await act(async () => {
      vi.advanceTimersByTime(2000);
    });
    await until(() => expect(asked()).toBe(4));
  });

  it("WEB-SESSION-2: NOT YOU? START AGAIN forgets the sid and shows the start screen", async () => {
    unknownPlayer();
    localStorage.setItem("katacombs.sid", SID);
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "NOT YOU? START AGAIN" }));
    expect(screen.getByRole("button", { name: "START" })).toBeInTheDocument();
    expect(localStorage.getItem("katacombs.sid")).toBeNull();
  });

  it("WEB-SESSION-3: SAVE shows the server's answer GAME SAVED.", async () => {
    const user = userEvent.setup();
    await openTheGameAt();
    await user.click(screen.getByRole("button", { name: "SAVE" }));
    expect(await within(messages()).findByText("GAME SAVED.")).toBeInTheDocument();
  });

  it("WEB-SESSION-4: QUIT returns to the start screen even when the server refuses", async () => {
    server.use(http.delete(api("/game/player/:sid"), () => new HttpResponse("boom", { status: 500 })));
    const user = userEvent.setup();
    await openTheGameAt();
    await user.click(screen.getByRole("button", { name: "QUIT" }));
    expect(await screen.findByRole("button", { name: "START" })).toBeInTheDocument();
    expect(localStorage.getItem("katacombs.sid")).toBeNull();
    expect(sentTo("DELETE", `/api/game/player/${SID}`)).toHaveLength(1);
  });
});
