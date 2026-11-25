// The mock server of the component tests (MSW). The default handlers answer
// as the real server does for a player at BRICK LANE; a test changes one
// answer with server.use(...). Every request is recorded in `requests`, so a
// test can assert what the client sent.
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import * as body from "./bodies";

export type Sent = { method: string; path: string; body: unknown };
export const requests: Sent[] = [];

const api = (path: string) => `http://localhost:5173/api${path}`;

export const handlers = [
  http.post(api("/game/player"), async ({ request }) => {
    const { name } = (await request.json()) as { name: string };
    return HttpResponse.json(body.player(name.trim().toUpperCase()), { status: 201 });
  }),
  http.post(api("/accounts"), async ({ request }) => {
    const sent = (await request.json()) as { email: string; name: string };
    return HttpResponse.json({ email: sent.email, name: sent.name }, { status: 201 });
  }),
  http.post(api("/accounts/login"), () => HttpResponse.json(body.player())),
  http.get(api("/player/:sid/location"), () => HttpResponse.json(body.brickLane)),
  http.get(api("/player/:sid/bag"), () => HttpResponse.json(body.emptyBag)),
  http.put(api("/player/:sid/move/:direction"), () => HttpResponse.json(body.brewery)),
  http.put(api("/player/:sid/item/:item/use/:action"), () => HttpResponse.json(body.message("TAKEN."))),
  http.put(api("/player/:sid/pickup/:item"), () => HttpResponse.json(body.message("OK"))),
  http.delete(api("/game/player/:sid"), () => HttpResponse.json(body.message("Game Over"))),
  http.post(api("/player/:sid/save"), () =>
    HttpResponse.json({ message: "GAME SAVED.", path: "katacombs.db" }),
  ),
  http.get(api("/player/:sid/chat"), () => HttpResponse.json([])),
  http.post(api("/player/:sid/chat"), () => HttpResponse.json(body.message("SENT."), { status: 201 })),
  http.get(api("/leaderboard"), () => HttpResponse.json([])),
];

export const server = setupServer(...handlers);

server.events.on("request:start", async ({ request }) => {
  const url = new URL(request.url);
  let sent: unknown = undefined;
  if (request.body) {
    try {
      sent = await request.clone().json();
    } catch {
      sent = undefined;
    }
  }
  requests.push({ method: request.method, path: url.pathname, body: sent });
});

export const sentTo = (method: string, path: string | RegExp) =>
  requests.filter((r) => r.method === method && (typeof path === "string" ? r.path === path : path.test(r.path)));
