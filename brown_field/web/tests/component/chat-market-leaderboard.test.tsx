// The chat, the market banner and the hidden leaderboard.
// Rule IDs: brown_field/web/spec/specification.md.
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { SID, chatLines } from "../mocks/bodies";
import { sentTo, server } from "../mocks/server";
import { api, openTheGameAt, until } from "./game";

const chatPath = `/api/player/${SID}/chat`;

describe("the chat", () => {
  it("WEB-CHAT-1: the chat asks the server every 2 s and shows the lines", async () => {
    vi.useFakeTimers({ toFake: ["setInterval"] });
    server.use(http.get(api("/player/:sid/chat"), () => HttpResponse.json(chatLines)));
    await openTheGameAt();
    expect(sentTo("GET", chatPath)).toHaveLength(0);
    await act(async () => {
      vi.advanceTimersByTime(2000);
    });
    const chat = screen.getByRole("region", { name: "chat" });
    expect(await within(chat).findByText("BO: hi")).toBeInTheDocument();
    await act(async () => {
      vi.advanceTimersByTime(4000);
    });
    await until(() => expect(sentTo("GET", chatPath)).toHaveLength(3));
  });

  it("WEB-CHAT-2: SEND posts the text, clears the box and reads the chat again", async () => {
    const user = userEvent.setup();
    await openTheGameAt();
    await user.type(screen.getByRole("textbox", { name: "chat message" }), "hello");
    await user.click(screen.getByRole("button", { name: "SEND" }));
    await waitFor(() => expect(sentTo("POST", chatPath)).toHaveLength(1));
    expect(sentTo("POST", chatPath)[0].body).toEqual({ text: "hello" });
    await waitFor(() => expect(screen.getByRole("textbox", { name: "chat message" })).toHaveValue(""));
    await waitFor(() => expect(sentTo("GET", chatPath).length).toBeGreaterThanOrEqual(1));
  });

  it("WEB-CHAT-3: SEND with an empty box sends nothing (the server accepts an empty text)", async () => {
    const user = userEvent.setup();
    await openTheGameAt();
    await user.click(screen.getByRole("button", { name: "SEND" }));
    await new Promise((resolve) => setTimeout(resolve, 100));
    expect(sentTo("POST", chatPath)).toHaveLength(0);
  });
});

describe("the market banner", () => {
  const at = (minute: number, second = 0) => new Date(2026, 0, 5, 10, minute, second);

  it.each([
    [50, true],
    [59, true],
    [49, false],
    [0, false],
  ])("WEB-MARKET-1: at minute %i of the browser clock, the banner shows: %s", async (minute, shown) => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(at(minute));
    await openTheGameAt();
    const banner = screen.queryByRole("alert");
    if (shown) expect(banner).toHaveTextContent("THE MARKET IS CLOSED FOR CLEANING.");
    else expect(banner).toBeNull();
  });

  it("WEB-MARKET-2: the banner appears within 30 s, with no click", async () => {
    vi.useFakeTimers({ toFake: ["Date", "setInterval"] });
    vi.setSystemTime(at(49, 45));
    await openTheGameAt();
    expect(screen.queryByRole("alert")).toBeNull();
    await act(async () => {
      vi.setSystemTime(at(50, 15));
      vi.advanceTimersByTime(30000);
    });
    expect(await screen.findByRole("alert")).toHaveTextContent("THE MARKET IS CLOSED FOR CLEANING.");
  });

  it("WEB-MARKET-3: the banner does not disable GO EAST (only the server refuses)", async () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(at(55));
    await openTheGameAt();
    expect(screen.getByRole("alert")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "GO EAST" })).toBeEnabled());
  });
});

describe("the leaderboard", () => {
  it("WEB-BOARD-1: while the flag is off there is no leaderboard and no request for it", async () => {
    await openTheGameAt();
    await new Promise((resolve) => setTimeout(resolve, 100));
    expect(screen.queryByRole("region", { name: "leaderboard" })).toBeNull();
    expect(sentTo("GET", "/api/leaderboard")).toHaveLength(0);
  });
});
