// The item buttons in HERE and BAG. Rule IDs: brown_field/web/spec/specification.md.
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { delay, http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { BEER_SID, SID, bagWithKey, brewery, error } from "../mocks/bodies";
import { sentTo, server } from "../mocks/server";
import { api, messages, openTheGameAt } from "./game";

const atTheBrewery = () => server.use(http.get(api("/player/:sid/location"), () => HttpResponse.json(brewery)));
const pickPath = `/api/player/${SID}/item/${BEER_SID}/use/pick`;

describe("the items here", () => {
  it("WEB-ITEM-1: an item here shows every action but DROP", async () => {
    atTheBrewery();
    await openTheGameAt("OLD TRUMAN BREWERY");
    const here = screen.getByRole("region", { name: "items here" });
    expect(within(here).getByRole("button", { name: "PICK BEER" })).toBeInTheDocument();
    expect(within(here).getByRole("button", { name: "USE BEER" })).toBeInTheDocument();
    expect(within(here).queryByRole("button", { name: "DROP BEER" })).toBeNull();
  });

  it("WEB-ITEM-2: PICK sends one take when the server answers fast", async () => {
    atTheBrewery();
    const user = userEvent.setup();
    await openTheGameAt("OLD TRUMAN BREWERY");
    await user.click(screen.getByRole("button", { name: "PICK BEER" }));
    expect(await within(messages()).findByText("TAKEN.")).toBeInTheDocument();
    await new Promise((resolve) => setTimeout(resolve, 900));
    expect(sentTo("PUT", pickPath)).toHaveLength(1);
  });

  it("WEB-ITEM-2: PICK sends the take again after 800 ms without an answer", async () => {
    atTheBrewery();
    let calls = 0;
    server.use(
      http.put(api("/player/:sid/item/:item/use/pick"), async () => {
        calls += 1;
        if (calls === 1) await delay(1500);
        return HttpResponse.json({ message: "TAKEN." });
      }),
    );
    const user = userEvent.setup();
    await openTheGameAt("OLD TRUMAN BREWERY");
    const started = Date.now();
    await user.click(screen.getByRole("button", { name: "PICK BEER" }));
    await waitFor(() => expect(sentTo("PUT", pickPath)).toHaveLength(2), { timeout: 3000 });
    expect(Date.now() - started).toBeGreaterThanOrEqual(750);
    expect(await within(messages()).findByText("TAKEN.")).toBeInTheDocument();
  });

  it("WEB-ITEM-3: USE on an item here is sent, and the server's refusal is shown", async () => {
    atTheBrewery();
    server.use(
      http.put(api("/player/:sid/item/:item/use/use"), () =>
        HttpResponse.json(error(405, "YOU ARE NOT CARRYING THE BEER."), { status: 405 }),
      ),
    );
    const user = userEvent.setup();
    await openTheGameAt("OLD TRUMAN BREWERY");
    await user.click(screen.getByRole("button", { name: "USE BEER" }));
    expect(await within(messages()).findByText("YOU ARE NOT CARRYING THE BEER.")).toBeInTheDocument();
  });

  it("WEB-ITEM-4: a double-click on an item here calls the legacy pickup", async () => {
    atTheBrewery();
    const user = userEvent.setup();
    await openTheGameAt("OLD TRUMAN BREWERY");
    // The double-click target has no role and no accessible name: found by its text.
    const here = screen.getByRole("region", { name: "items here" });
    await user.dblClick(within(here).getByText("BEER"));
    await waitFor(() => expect(sentTo("PUT", `/api/player/${SID}/pickup/${BEER_SID}`)).toHaveLength(1));
  });
});

describe("the bag", () => {
  it("WEB-BAG-1: the bag shows the gold, the score, the energy, and DROP and USE only", async () => {
    server.use(http.get(api("/player/:sid/bag"), () => HttpResponse.json(bagWithKey)));
    await openTheGameAt();
    const bag = screen.getByRole("region", { name: "bag" });
    expect(await within(bag).findByText("GOLD 5 · SCORE 5 · ENERGY 11")).toBeInTheDocument();
    expect(within(bag).getByRole("button", { name: "DROP KEY" })).toBeInTheDocument();
    expect(within(bag).getByRole("button", { name: "USE KEY" })).toBeInTheDocument();
    expect(within(bag).queryByRole("button", { name: "PICK KEY" })).toBeNull();
  });
});
