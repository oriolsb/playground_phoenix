// The GO buttons. Rule IDs: brown_field/web/spec/specification.md.
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { delay, http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import App from "../../src/App";
import { SID, brewery, error, katacombsExit } from "../mocks/bodies";
import { sentTo, server } from "../mocks/server";
import { api, messages, openTheGameAt } from "./game";

const DIRECTIONS = ["NORTH", "SOUTH", "EAST", "WEST", "UP", "DOWN"];

describe("the GO buttons", () => {
  it("WEB-MOVE-1: there is one GO button per direction, enabled only for an exit", async () => {
    await openTheGameAt("BRICK LANE");
    const moves = screen.getByRole("navigation", { name: "moves" });
    for (const direction of DIRECTIONS) {
      const button = within(moves).getByRole("button", { name: `GO ${direction}` });
      if (["NORTH", "EAST", "WEST", "SOUTH"].includes(direction)) expect(button).toBeEnabled();
      else expect(button).toBeDisabled();
    }
  });

  it("WEB-MOVE-2: every GO button is disabled at energy 1 (the server refuses only at 0)", async () => {
    server.use(http.get(api("/player/:sid/bag"), () => HttpResponse.json({ items: [], gold: 0, score: 0, energy: 1 })));
    await openTheGameAt();
    await waitFor(() => expect(screen.getByText(/ENERGY 1$/)).toBeInTheDocument());
    for (const direction of DIRECTIONS) expect(screen.getByRole("button", { name: `GO ${direction}` })).toBeDisabled();
  });

  it("WEB-MOVE-2: every GO button is disabled until the bag has loaded", async () => {
    server.use(
      http.get(api("/player/:sid/bag"), async () => {
        await delay("infinite");
        return HttpResponse.json({});
      }),
    );
    localStorage.setItem("katacombs.sid", SID);
    render(<App />);
    // The location shows first; the bag never answers, so the energy is unknown.
    expect(await screen.findByRole("heading", { name: "BRICK LANE" })).toBeInTheDocument();
    for (const direction of DIRECTIONS) expect(screen.getByRole("button", { name: `GO ${direction}` })).toBeDisabled();
  });

  it("WEB-MOVE-3: GO NORTH moves the player and shows the new location", async () => {
    const user = userEvent.setup();
    await openTheGameAt();
    await waitFor(() => expect(screen.getByRole("button", { name: "GO NORTH" })).toBeEnabled());
    await user.click(screen.getByRole("button", { name: "GO NORTH" }));
    expect(await screen.findByRole("heading", { name: brewery.title })).toBeInTheDocument();
    expect(sentTo("PUT", `/api/player/${SID}/move/north`)).toHaveLength(1);
  });

  it("WEB-MOVE-4: at the katacombs exit the screen shows the score", async () => {
    server.use(
      http.put(api("/player/:sid/move/:direction"), () => HttpResponse.json(katacombsExit)),
      http.get(api("/player/:sid/bag"), () => HttpResponse.json({ items: [], gold: 35, score: 85, energy: 6 })),
    );
    const user = userEvent.setup();
    await openTheGameAt();
    await waitFor(() => expect(screen.getByRole("button", { name: "GO EAST" })).toBeEnabled());
    await user.click(screen.getByRole("button", { name: "GO EAST" }));
    expect(await screen.findByRole("status")).toHaveTextContent("YOU FOUND THE EXIT. SCORE 85.");
    expect(within(messages()).getByText("YOU FOUND THE EXIT.")).toBeInTheDocument();
  });

  it("WEB-MSG-1: a refused move shows the server's message", async () => {
    server.use(
      http.put(api("/player/:sid/move/:direction"), () =>
        HttpResponse.json(error(405, "THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER."), { status: 405 }),
      ),
    );
    const user = userEvent.setup();
    await openTheGameAt();
    await waitFor(() => expect(screen.getByRole("button", { name: "GO EAST" })).toBeEnabled());
    await user.click(screen.getByRole("button", { name: "GO EAST" }));
    expect(await within(messages()).findByText("THE MARKET IS CLOSED FOR CLEANING. COME BACK LATER.")).toBeInTheDocument();
  });
});
