// The bodies that the mock server answers with, each named with the schema of
// brown_field/spec/openapi.yaml that it must match. mocks/contract.test.ts
// validates every one of them, so the component tests cannot drift from the
// real server's shapes.

export const SID = "123456-123456789012-12345678";
export const BEER_SID = "000100-000000000000-00000001";
export const KEY_SID = "000100-000000000000-00000002";

export const beer = {
  sid: BEER_SID,
  name: "BEER",
  description: "A BOTTLE OF CRAFTED BEER FROM THE BREWERY.",
  actions: ["pick", "drop", "use"],
  value: 0,
};

export const key = {
  sid: KEY_SID,
  name: "KEY",
  description: "A SMALL IRON KEY. IT HAS A PICTURE OF A MANHOLE ON IT.",
  actions: ["pick", "drop", "use"],
  value: 0,
};

export const brickLane = {
  title: "BRICK LANE",
  description: "YOU ARE STANDING AT THE END OF BRICK LANE.",
  exits: ["north", "east", "west", "south"],
  items: [],
  isExit: false,
};

export const brewery = {
  title: "OLD TRUMAN BREWERY",
  description: "YOU ARE INSIDE THE OLD BREWERY.",
  exits: ["south", "up", "down"],
  items: [beer],
  isExit: false,
};

export const katacombsExit = {
  title: "KATACOMBS EXIT",
  description: "DAYLIGHT! YOU HAVE FOUND THE WAY OUT OF THE KATACOMBS.",
  exits: ["west"],
  items: [],
  isExit: true,
};

export const emptyBag = { items: [], gold: 0, score: 0, energy: 12 };

export const bagWithKey = { items: [key], gold: 5, score: 5, energy: 11 };

export function player(name = "ANA") {
  return {
    sid: SID,
    name,
    location: brickLane,
    bag: { items: [], gold: 0, score: 0 },
    hasWon: false,
    energy: 12,
  };
}

export const message = (text: string) => ({ message: text });

export const error = (code: number, text: string) => ({ code, message: text });

export const chatLines = [{ name: "BO", text: "hi", at: "2026-01-05T10:15:00+00:00" }];

// Every body above, with the schema that it must match.
export const CONTRACT_SAMPLES: [string, unknown][] = [
  ["Item", beer],
  ["Item", key],
  ["Location", brickLane],
  ["Location", brewery],
  ["Location", katacombsExit],
  ["BagWithEnergy", emptyBag],
  ["BagWithEnergy", bagWithKey],
  ["PlayerWithEnergy", player()],
  ["Message", message("TAKEN.")],
  ["Error", error(405, "YOU CAN'T GO THAT WAY.")],
  ["Error", error(404, `PLAYER ${SID} NOT FOUND.`)],
  ["Account", { email: "ana@example.org", name: "ANA" }],
  ["ChatMessage", chatLines[0]],
  ["SaveResult", { message: "GAME SAVED.", path: "katacombs.db" }],
];
