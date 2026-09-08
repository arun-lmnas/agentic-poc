import { test, expect } from "@playwright/test";

test("accepts boundary-length tasks and rejects titles outside the range", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("No tasks yet.")).toBeVisible();

  await page.getByLabel("New task").fill("ab");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("alert")).toHaveText("Task title must be between 3 and 6 characters");

  await page.getByLabel("New task").fill("abc");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("listitem")).toHaveText("abc");
  await expect(page.getByRole("alert")).toHaveCount(0);

  await page.getByLabel("New task").fill("abcde");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("listitem")).toHaveCount(2);
  await expect(page.getByRole("listitem").nth(1)).toHaveText("abcde");

  await page.getByLabel("New task").fill("abcdef");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("listitem")).toHaveCount(3);
  await expect(page.getByRole("listitem").nth(2)).toHaveText("abcdef");

  await page.getByLabel("New task").fill("abcdefg");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("alert")).toHaveText("Task title must be between 3 and 6 characters");
});
