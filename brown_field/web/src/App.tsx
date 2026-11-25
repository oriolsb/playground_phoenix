import { useEffect, useState } from "react";
import * as api from "./api";
import type { Bag, ChatLine, Location, Score } from "./api";

const SHOW_LEADERBOARD = false; // Marketing, 2024: hide until the season starts.

const PLACE_COLOURS: Record<string, string> = {
  "BRICK LANE": "#b5651d",
  "OLD TRUMAN BREWERY": "#8b4513",
  "BREWERY CELLAR": "#4b3621",
  "BREWERY ROOFTOP": "#4682b4",
  "SPITALFIELDS MARKET": "#b8860b",
  "BACK YARD": "#556b2f",
  "BRICK LANE BAKERY": "#a0522d",
  "COLUMBIA ROAD": "#c71585",
  BOXPARK: "#2f4f4f",
  "RAILWAY ARCHES": "#8b0000",
  "OLD TUBE TUNNEL": "#36454f",
  "TUNNEL JUNCTION": "#483d8b",
  KATACOMBS: "#1c1c1c",
  "KATACOMBS EXIT": "#228b22",
};

const DIRECTIONS = ["north", "south", "east", "west", "up", "down"];

const SID_KEY = "katacombs.sid";

export default function App() {
  const [sid, setSid] = useState<string | null>(() => localStorage.getItem(SID_KEY));
  const [location, setLocation] = useState<Location | null>(null);
  const [bag, setBag] = useState<Bag | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [lost, setLost] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [lines, setLines] = useState<ChatLine[]>([]);
  const [text, setText] = useState("");
  const [scores, setScores] = useState<Score[]>([]);
  const [, setTick] = useState(0);

  function say(message: string) {
    setLog((old) => [message, ...old].slice(0, 8));
  }

  async function refresh(current: string, here?: Location) {
    setLocation(here ?? (await api.look(current)));
    setBag(await api.bag(current));
  }

  function begin(newSid: string) {
    localStorage.setItem(SID_KEY, newSid);
    setSid(newSid);
    setLost(false);
    refresh(newSid).catch((error) => say(error.message));
  }

  useEffect(() => {
    if (!sid) return;
    let stop = false;
    const resume = () =>
      refresh(sid)
        .then(() => !stop && setLost(false))
        .catch(() => !stop && setLost(true));
    resume();
    const timer = setInterval(() => lost && resume(), 2000);
    return () => {
      stop = true;
      clearInterval(timer);
    };
  }, [sid, lost]);

  useEffect(() => {
    if (!sid || lost) return;
    const timer = setInterval(() => {
      api.chat(sid).then(setLines).catch(() => undefined);
    }, 2000);
    return () => clearInterval(timer);
  }, [sid, lost]);

  useEffect(() => {
    const timer = setInterval(() => setTick((n) => n + 1), 30000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (SHOW_LEADERBOARD) api.leaderboard().then(setScores).catch(() => undefined);
  }, [location]);

  async function start(event: React.FormEvent) {
    event.preventDefault();
    try {
      const player = await api.startGame(name.trim().toUpperCase());
      begin(player.sid);
    } catch (error) {
      say((error as Error).message);
    }
  }

  async function signIn(event: React.FormEvent) {
    event.preventDefault();
    try {
      begin((await api.login(email, password)).sid);
    } catch (error) {
      say((error as Error).message);
    }
  }

  async function signUp() {
    try {
      await api.register(email, password, name.trim().toUpperCase());
      begin((await api.login(email, password)).sid);
    } catch (error) {
      say((error as Error).message);
    }
  }

  async function go(direction: string) {
    if (!sid) return;
    try {
      const here = await api.move(sid, direction);
      await refresh(sid, here);
      if (here.isExit) say("YOU FOUND THE EXIT.");
    } catch (error) {
      say((error as Error).message);
    }
  }

  async function use(item: string, action: string) {
    if (!sid) return;
    try {
      const result = action === "pick" ? await api.pick(sid, item) : await api.act(sid, item, action);
      say(result.message);
      await refresh(sid);
    } catch (error) {
      say((error as Error).message);
    }
  }

  async function quickPick(item: string) {
    if (!sid) return;
    try {
      await api.quickPick(sid, item);
      await refresh(sid);
    } catch (error) {
      say((error as Error).message);
    }
  }

  async function keep() {
    if (!sid) return;
    try {
      say((await api.save(sid)).message);
    } catch (error) {
      say((error as Error).message);
    }
  }

  function forget() {
    localStorage.removeItem(SID_KEY);
    setSid(null);
    setLocation(null);
    setBag(null);
    setLost(false);
  }

  async function leave() {
    if (sid) await api.quit(sid).catch(() => undefined);
    forget();
  }

  async function send(event: React.FormEvent) {
    event.preventDefault();
    if (!sid || !text) return;
    try {
      await api.say(sid, text);
      setText("");
      setLines(await api.chat(sid));
    } catch (error) {
      say((error as Error).message);
    }
  }

  const marketClosed = new Date().getMinutes() >= 50;
  const tired = (bag?.energy ?? 0) <= 1; // Do not let a player get stuck at 0.

  if (sid && lost) {
    return (
      <main>
        <p role="status">CONNECTION LOST. RETRYING...</p>
        <button onClick={forget}>NOT YOU? START AGAIN</button>
      </main>
    );
  }

  if (!sid || !location) {
    return (
      <main>
        <h1>KATACOMBS</h1>
        <form onSubmit={start}>
          <label>
            NAME
            <input value={name} maxLength={40} onChange={(e) => setName(e.target.value)} />
          </label>
          <button type="submit">START</button>
        </form>
        <form onSubmit={signIn}>
          <label>
            EMAIL
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label>
            PASSWORD
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          <button type="submit">LOG IN</button>
          <button type="button" onClick={signUp}>
            REGISTER
          </button>
        </form>
        <ul aria-label="messages">
          {log.map((line, index) => (
            <li key={index}>{line}</li>
          ))}
        </ul>
      </main>
    );
  }

  return (
    <main>
      {marketClosed && <p role="alert">THE MARKET IS CLOSED FOR CLEANING.</p>}
      <section className="place" style={{ background: PLACE_COLOURS[location.title] ?? "#999" }}>
        <h2>{location.title}</h2>
        <p>{location.description}</p>
        {location.isExit && <p role="status">YOU FOUND THE EXIT. SCORE {bag?.score}.</p>}
      </section>

      <nav aria-label="moves">
        {DIRECTIONS.map((direction) => (
          <button
            key={direction}
            aria-label={`GO ${direction.toUpperCase()}`}
            disabled={!location.exits.includes(direction) || tired}
            onClick={() => go(direction)}
          >
            {direction.toUpperCase()}
          </button>
        ))}
      </nav>

      <section aria-label="items here">
        <h3>HERE</h3>
        {location.items.map((item) => (
          <div key={item.sid} onDoubleClick={() => quickPick(item.sid)}>
            <span>{item.name}</span>
            {item.actions
              .filter((action) => action !== "drop")
              .map((action) => (
                <button
                  key={action}
                  aria-label={`${action.toUpperCase()} ${item.name}`}
                  onClick={() => use(item.sid, action)}
                >
                  {action.toUpperCase()}
                </button>
              ))}
          </div>
        ))}
      </section>

      <section aria-label="bag">
        <h3>BAG</h3>
        <p>
          GOLD {bag?.gold} · SCORE {bag?.score} · ENERGY {bag?.energy}
        </p>
        {bag?.items.map((item) => (
          <div key={item.sid}>
            <span>{item.name}</span>
            {item.actions
              .filter((action) => action === "drop" || action === "use")
              .map((action) => (
                <button
                  key={action}
                  aria-label={`${action.toUpperCase()} ${item.name}`}
                  onClick={() => use(item.sid, action)}
                >
                  {action.toUpperCase()}
                </button>
              ))}
          </div>
        ))}
      </section>

      <section aria-label="chat">
        <h3>CHAT</h3>
        <ul>
          {lines.map((line, index) => (
            <li key={index}>
              {line.name}: {line.text}
            </li>
          ))}
        </ul>
        <form onSubmit={send}>
          <input aria-label="chat message" value={text} onChange={(e) => setText(e.target.value)} />
          <button type="submit">SEND</button>
        </form>
      </section>

      {SHOW_LEADERBOARD && (
        <section aria-label="leaderboard">
          <h3>LEADERBOARD</h3>
          <ol>
            {scores.map((entry, index) => (
              <li key={index}>
                {entry.name} {entry.score}
              </li>
            ))}
          </ol>
        </section>
      )}

      <footer>
        <button onClick={keep}>SAVE</button>
        <button onClick={leave}>QUIT</button>
      </footer>

      <ul aria-label="messages">
        {log.map((line, index) => (
          <li key={index}>{line}</li>
        ))}
      </ul>
    </main>
  );
}
