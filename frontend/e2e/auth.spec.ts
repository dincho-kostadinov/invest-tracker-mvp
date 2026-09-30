import { expect, test } from "@playwright/test";

function uniqueEmail(): string {
  return `e2e-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
}

test("sign up, reach the dashboard, log out, then get redirected when unauthenticated", async ({
  page,
}) => {
  const email = uniqueEmail();

  await page.goto("/signup");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("correcthorse123");
  await page.getByRole("button", { name: "Sign up" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText("Invest Tracker")).toBeVisible();

  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/login$/);

  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);
});
