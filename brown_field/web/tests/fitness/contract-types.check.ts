// Type-checked, never run. tsc compiles this file against types generated
// from brown_field/spec/openapi.yaml (see contract-types.test.ts).
//
// Fits<Server, Client> is true when every value the server's contract allows
// also fits the type that src/api.ts declares for it by hand. Each line pins
// today's answer: a drift in either file changes an answer and fails tsc.
import type { components } from "./generated/openapi";
import type * as client from "../../src/api";

type S = components["schemas"];
type Fits<Server, Client> = [Server] extends [Client] ? true : false;

export const item: Fits<S["Item"], client.Item> = true;
export const location: Fits<S["Location"], client.Location> = true;
export const bag: Fits<S["BagWithEnergy"], client.Bag> = true;
export const chat: Fits<S["ChatMessage"], client.ChatLine> = true;
export const score: Fits<S["FinishedGame"], client.Score> = true;

// Known drift, pinned as it is: src/api.ts gives Player.bag the type Bag,
// which requires `energy`. The server sends the player's bag without energy
// (the energy is on the player, and on GET /bag). The client never reads
// player.bag.energy, so the game works; the type is wrong.
export const player: Fits<S["PlayerWithEnergy"], client.Player> = false;
