// WEB-E2E-1: a new player wins in a real browser, against the real server.
// The slide route (brewery, cellar, tube tunnel, junction, katacombs, exit)
// avoids the market: the server runs in its own process, so its clock can't
// be faked. The cellar rat can only take an item without value, and this bag
// is empty. Gold: brewery 5 + cellar 20 + katacombs 30 = 55.
import { expect, test } from "@playwright/test";

const route: [string, string][] = [
  ["NORTH", "OLD TRUMAN BREWERY"],
  ["DOWN", "BREWERY CELLAR"],
  ["DOWN", "OLD TUBE TUNNEL"],
  ["EAST", "TUNNEL JUNCTION"],
  ["NORTH", "KATACOMBS"],
  ["EAST", "KATACOMBS EXIT"],
];

test("WEB-E2E-1: a new player wins on the slide route", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("NAME").fill("ana");
  await page.getByRole("button", { name: "START" }).click();
  await expect(page.getByRole("heading", { name: "BRICK LANE" })).toBeVisible();

  for (const [direction, title] of route) {
    await page.getByRole("button", { name: `GO ${direction}` }).click();
    await expect(page.getByRole("heading", { name: title })).toBeVisible();
  }

  await expect(page.getByRole("status")).toHaveText("YOU FOUND THE EXIT. SCORE 55.");
  await expect(page.getByRole("list", { name: "messages" })).toContainText("YOU FOUND THE EXIT.");
  await expect(page.getByRole("region", { name: "bag" })).toContainText("GOLD 55 · SCORE 55 · ENERGY 6");
});

test("WEB-E2E-1: a reload resumes the game from the sid in the browser", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("NAME").fill("bo");
  await page.getByRole("button", { name: "START" }).click();
  await page.getByRole("button", { name: "GO NORTH" }).click();
  await expect(page.getByRole("heading", { name: "OLD TRUMAN BREWERY" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: "OLD TRUMAN BREWERY" })).toBeVisible();
});
