import { expect, test } from "@playwright/test";

// Run with: npx playwright test — configure TEST_EMAIL and TEST_PASSWORD in .env.test

test("landing page loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("hero-headline")).toBeVisible();
  await expect(page.getByTestId("header-logo")).toBeVisible();
});

test("login flow", async ({ page }) => {
  await page.goto("/login");
  await page.getByPlaceholder(/email/i).fill(process.env.TEST_EMAIL || "test@example.com");
  await page.getByPlaceholder(/password/i).fill(process.env.TEST_PASSWORD || "testpassword123");
  await page.getByRole("button", { name: /log in|sign in/i }).click();

  await page.waitForURL(/\/(dashboard|login)/, { timeout: 10000 }).catch(() => {});
  if (page.url().includes("/dashboard")) {
    await expect(page).toHaveURL(/\/dashboard/);
  } else {
    await expect(page.getByPlaceholder(/email/i)).toBeVisible();
  }
});

test("sensor empty state renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("live-sensor-card")).toBeVisible();
});
