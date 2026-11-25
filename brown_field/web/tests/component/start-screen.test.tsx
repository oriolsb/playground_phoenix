// The start screen: start a game, log in, register. Each test pins what the
// client does today; the rule IDs are in brown_field/web/spec/specification.md.
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import App from "../../src/App";
import { SID, error } from "../mocks/bodies";
import { sentTo, server } from "../mocks/server";

const api = (path: string) => `http://localhost:5173/api${path}`;

describe("the start screen", () => {
  it("WEB-START-1: START sends the name trimmed and in upper case, then shows the game", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("NAME"), "  ana ");
    await user.click(screen.getByRole("button", { name: "START" }));
    expect(await screen.findByRole("heading", { name: "BRICK LANE" })).toBeInTheDocument();
    expect(sentTo("POST", "/api/game/player")[0].body).toEqual({ name: "ANA" });
  });

  it("WEB-START-1: the new sid is kept in the browser as katacombs.sid", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("NAME"), "ana");
    await user.click(screen.getByRole("button", { name: "START" }));
    await screen.findByRole("heading", { name: "BRICK LANE" });
    expect(localStorage.getItem("katacombs.sid")).toBe(SID);
  });

  it("WEB-START-2: the NAME box stops at 40 characters (the server allows 50)", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("NAME"), "A".repeat(45));
    expect(screen.getByLabelText("NAME")).toHaveValue("A".repeat(40));
  });

  it("WEB-START-3: REGISTER registers the account, then logs in", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("NAME"), "ana");
    await user.type(screen.getByLabelText("EMAIL"), "ana@example.org");
    await user.type(screen.getByLabelText("PASSWORD"), "pw");
    await user.click(screen.getByRole("button", { name: "REGISTER" }));
    await screen.findByRole("heading", { name: "BRICK LANE" });
    expect(sentTo("POST", "/api/accounts")[0].body).toEqual({ email: "ana@example.org", password: "pw", name: "ANA" });
    expect(sentTo("POST", "/api/accounts/login")[0].body).toEqual({ email: "ana@example.org", password: "pw" });
  });

  it("WEB-START-3: LOG IN logs in with the email and the password", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("EMAIL"), "ana@example.org");
    await user.type(screen.getByLabelText("PASSWORD"), "pw");
    await user.click(screen.getByRole("button", { name: "LOG IN" }));
    await screen.findByRole("heading", { name: "BRICK LANE" });
    expect(sentTo("POST", "/api/accounts")).toHaveLength(0);
  });

  it("WEB-MSG-1: the server's message for a refusal appears in the messages", async () => {
    server.use(
      http.post(api("/game/player"), () => HttpResponse.json(error(400, "THIS NAME IS RESERVED."), { status: 400 })),
    );
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("NAME"), "admin");
    await user.click(screen.getByRole("button", { name: "START" }));
    const messages = screen.getByRole("list", { name: "messages" });
    expect(await within(messages).findByText("THIS NAME IS RESERVED.")).toBeInTheDocument();
  });

  it("WEB-MSG-2: a refusal without a JSON message shows SOMETHING WENT WRONG.", async () => {
    server.use(http.post(api("/game/player"), () => new HttpResponse("Internal Server Error", { status: 500 })));
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("NAME"), "ana");
    await user.click(screen.getByRole("button", { name: "START" }));
    const messages = screen.getByRole("list", { name: "messages" });
    expect(await within(messages).findByText("SOMETHING WENT WRONG.")).toBeInTheDocument();
  });

  it("WEB-MSG-2: the framework's {detail} body also shows SOMETHING WENT WRONG.", async () => {
    server.use(http.post(api("/game/player"), () => HttpResponse.json({ detail: "Not Found" }, { status: 404 })));
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByLabelText("NAME"), "ana");
    await user.click(screen.getByRole("button", { name: "START" }));
    await waitFor(() =>
      expect(within(screen.getByRole("list", { name: "messages" })).getByText("SOMETHING WENT WRONG.")).toBeInTheDocument(),
    );
  });
});
