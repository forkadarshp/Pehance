import { expect, test } from "@playwright/test";

test("has title", async ({ page }) => {
  await page.goto("http://localhost:3000/");

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Pehance/);
});

test("get enhance button", async ({ page }) => {
  await page.goto("http://localhost:3000/");

  // Click the get started link.
  await page.getByRole("button", { name: "Enhance" }).click();

  // Expects the URL to contain intro.
  await expect(page.getByRole("textbox")).toBeVisible();
}); 