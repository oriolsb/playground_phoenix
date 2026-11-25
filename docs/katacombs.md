# Katacombs

## Source

<https://github.com/conso/katacombs>

## Project Requirements

- Implement a REST API transport layer.
- Use an in-memory database.

## Game Overview

Katacombs is a text-based adventure game. In the game, players:

- explore locations that connect to each other,
- move in the cardinal directions or through special connections,
- collect treasures,
- find KATACOMBS EXIT to win,
- get a score from the value of the treasures that they collect,
- see their finished games on a leaderboard.

## Gameplay Guide

### Game Start

```text
LOST IN SHOREDITCH.
YOU ARE STANDING AT THE END OF BRICK LANE BEFORE A SMALL BRICK BUILDING CALLED THE OLD TRUMAN BREWERY.
AROUND YOU IS A FOREST OF RESTAURANTS.
A SMALL STREAM OF CRAFTED BEER FLOWS OUT OF THE BUILDING AND DOWN A GULLY.
>
```

### Available Commands

#### Movement

- `GO N/E/S/W` - Move in a cardinal direction.
- `GO UP/DOWN` - Use the stairs.
- `LOOK [direction/item]` - Examine the area around you, a direction, or
  an item.

#### Interaction

- `OPEN [item]` - Open a door, a gate, or a different item.
- `CLOSE [item]` - Close a door, a gate, or a different item.
- `TAKE [item]` - Collect an item (max 10 in bag).
- `DROP [item]` - Put down an item.
- `BAG` - Show the items in the bag.
- `USE [item]` - Use an item in a specific location.

#### System Commands

- `?` - Show the help menu.
- `QUIT` - End the game.

### Game Mechanics

#### Items and the Bag

- Bag limit: 10 items.
- You can take and drop items in all locations.
- The description of a location lists the items in the location.

#### Gold Collection

- The game collects gold automatically at these times:
  - the first visit to a location with gold,
  - the first time that a player opens an item that contains gold.
- The bag shows the total gold.

#### Leaderboard

- When a player reaches KATACOMBS EXIT (a win), the game records the
  finished game.
- A read-only list shows the finished games, ranked by score, highest
  first.
- Each entry shows the player name, the score, and the number of moves.

#### World Rules

1. Each location must have a unique title.
2. Each connection must have a reverse connection that matches it.
   - For example, south from A goes to B. Then north from B must go to A.
   - This rule applies to all directions (N/S/E/W/UP/DOWN).

## The World

All implementations use this world. The player starts at BRICK LANE.

### Locations

| Title               | Description                                                                                                                                                                                                              | Exits                                                    | Items at the start | Gold |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------- | ------------------ | ---- |
| BRICK LANE          | YOU ARE STANDING AT THE END OF BRICK LANE BEFORE A SMALL BRICK BUILDING CALLED THE OLD TRUMAN BREWERY. AROUND YOU IS A FOREST OF RESTAURANTS. A SMALL STREAM OF CRAFTED BEER FLOWS OUT OF THE BUILDING AND DOWN A GULLY. | N: OLD TRUMAN BREWERY, E: SPITALFIELDS MARKET            |                    | 0    |
| OLD TRUMAN BREWERY  | YOU ARE INSIDE THE OLD BREWERY. COPPER VATS LINE THE WALLS. A STAIRCASE GOES UP TO THE ROOF AND A TRAPDOOR GOES DOWN TO THE CELLAR.                                                                                      | S: BRICK LANE, UP: BREWERY ROOFTOP, DOWN: BREWERY CELLAR | BEER               | 5    |
| BREWERY CELLAR      | A COLD CELLAR FULL OF EMPTY BARRELS. SOMETHING SHINES ON THE FLOOR.                                                                                                                                                      | UP: OLD TRUMAN BREWERY                                   | RING               | 20   |
| BREWERY ROOFTOP     | YOU ARE ON THE ROOF OF THE BREWERY. YOU CAN SEE ALL OF SHOREDITCH.                                                                                                                                                       | DOWN: OLD TRUMAN BREWERY                                 | KEY                | 0    |
| SPITALFIELDS MARKET | THE OLD SPITALFIELDS MARKET. THE STALLS ARE CLOSED FOR THE NIGHT.                                                                                                                                                        | W: BRICK LANE, S: BACK YARD                              | CRATE              | 0    |
| BACK YARD           | A SMALL YARD BEHIND THE MARKET. THERE IS A MANHOLE COVER IN THE GROUND.                                                                                                                                                  | N: SPITALFIELDS MARKET                                   | MANHOLE            | 0    |
| KATACOMBS           | DAMP STONE TUNNELS. SKULLS LINE THE WALLS. A FAINT LIGHT GLOWS TO THE EAST.                                                                                                                                              | E: KATACOMBS EXIT                                        | GOBLET             | 30   |
| KATACOMBS EXIT      | DAYLIGHT! YOU HAVE FOUND THE WAY OUT OF THE KATACOMBS.                                                                                                                                                                   | W: KATACOMBS                                             |                    | 0    |

"Gold" is the gold in the location. See
[Gold Collection](#gold-collection) for when the game collects it.

KATACOMBS EXIT is the exit of the katacombs. A player who arrives there wins.

### Items

| Name    | Description                                            | Commands        | Treasure value |
| ------- | ------------------------------------------------------ | --------------- | -------------- |
| BEER    | A BOTTLE OF CRAFTED BEER FROM THE BREWERY.             | TAKE, DROP, USE |                |
| KEY     | A SMALL IRON KEY. IT HAS A PICTURE OF A MANHOLE ON IT. | TAKE, DROP, USE |                |
| RING    | A SILVER RING. SOMEBODY LOST IT A LONG TIME AGO.       | TAKE, DROP      | 20             |
| CRATE   | A HEAVY WOODEN CRATE WITH A LOOSE LID.                 | OPEN, CLOSE     |                |
| MANHOLE | A ROUND IRON MANHOLE COVER WITH A KEYHOLE.             | OPEN, CLOSE     |                |
| GOBLET  | A GOLDEN GOBLET. IT LOOKS VERY VALUABLE.               | TAKE, DROP      | 50             |

### Special items

- **CRATE:** the crate contains 10 gold.
- **MANHOLE:** the manhole is locked at the start. A locked item does not
  open.
- **KEY:** the key unlocks the manhole in the BACK YARD.
- **Special connection:** when the manhole is open, the BACK YARD goes
  DOWN to the KATACOMBS, and the KATACOMBS go UP to the BACK YARD. When
  the manhole closes, this connection closes too.
- **BEER:** when a player uses the beer, the player drinks it. The beer
  leaves the bag.

## Resources

- [Zork I gameplay example](https://www.youtube.com/watch?v=TNN4VPlRBJ8) —
  optional background. Watch the first two or three minutes to see typed
  commands, text descriptions, and game responses.
- [Play Zork I in the browser](https://archive.org/details/msdos_Zork_I_-_The_Great_Underground_Empire_1980) —
  optional background. Click Start, then try `examine mailbox`, `take
  leaflet`, `north`, and `inventory`.
- [MUD](https://en.wikipedia.org/wiki/Multi-user_dungeon)
- [How to program a text adventure in C](https://helderman.github.io/htpataic/htpataic01.html)
