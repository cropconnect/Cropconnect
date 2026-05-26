import { expect, test } from "@playwright/test";

// Run with: npx playwright test - configure TEST_EMAIL and TEST_PASSWORD in .env.test

test("CropConnect smoke flow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("hero-headline")).toBeVisible();

  await page.getByRole("link", { name: /sign in/i }).first().click();
  await page.getByPlaceholder(/email/i).fill(process.env.TEST_EMAIL || "test@example.com");
  await page.getByPlaceholder(/password/i).fill(process.env.TEST_PASSWORD || "password");
  await page.getByRole("button", { name: /log in|sign in/i }).click();

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/Soil Moisture/i).first()).toBeVisible();
});
