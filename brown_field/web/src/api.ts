const BASE = "/api";

export type Item = {
  sid: string;
  name: string;
  description: string;
  actions: string[];
  value: number;
};

export type Location = {
  title: string;
  description: string;
  exits: string[];
  items: Item[];
  isExit: boolean;
};

export type Bag = {
  items: Item[];
  gold: number;
  score: number;
  energy: number;
};

export type Player = {
  sid: string;
  name: string;
  location: Location;
  bag: Bag;
  hasWon: boolean;
  energy: number;
};

export type ChatLine = { name: string; text: string; at: string };

export type Score = { name: string; score: number; moves: number };

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(BASE + path, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(response.status, data.message ?? "SOMETHING WENT WRONG.");
  }
  return data as T;
}

export const startGame = (name: string) => call<Player>("POST", "/game/player", { name });

export const register = (email: string, password: string, name: string) =>
  call<{ email: string; name: string }>("POST", "/accounts", { email, password, name });

export const login = (email: string, password: string) =>
  call<Player>("POST", "/accounts/login", { email, password });

export const look = (sid: string) => call<Location>("GET", `/player/${sid}/location`);

export const bag = (sid: string) => call<Bag>("GET", `/player/${sid}/bag`);

export const move = (sid: string, direction: string) =>
  call<Location>("PUT", `/player/${sid}/move/${direction}`);

export const act = (sid: string, item: string, action: string) =>
  call<{ message: string }>("PUT", `/player/${sid}/item/${item}/use/${action}`);

export const quickPick = (sid: string, item: string) =>
  call<{ message: string }>("PUT", `/player/${sid}/pickup/${item}`);

export const quit = (sid: string) => call<{ message: string }>("DELETE", `/game/player/${sid}`);

export const save = (sid: string) => call<{ message: string }>("POST", `/player/${sid}/save`);

export const chat = (sid: string) => call<ChatLine[]>("GET", `/player/${sid}/chat`);

export const say = (sid: string, text: string) =>
  call<{ message: string }>("POST", `/player/${sid}/chat`, { text });

export const leaderboard = () => call<Score[]>("GET", "/leaderboard");

export async function pick(sid: string, item: string) {
  // Slow network on the train. Do not remove.
  const first = act(sid, item, "pick");
  first.catch(() => undefined);
  const late = new Promise<"late">((resolve) => setTimeout(() => resolve("late"), 800));
  const winner = await Promise.race([first, late]);
  if (winner === "late") {
    return act(sid, item, "pick");
  }
  return winner;
}
