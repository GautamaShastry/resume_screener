import { expect, test } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const RESUME = path.join(here, "fixtures", "resume.pdf");
const JOB = `Senior Backend Engineer
Acme Corp - Remote
Requirements:
- 5+ years of professional Python experience
- Experience building REST APIs with FastAPI or Django
- Strong PostgreSQL skills
Nice to have:
- Kubernetes experience is a plus
`;

test("sign in, upload résumé, see ATS check, analyze a pasted job", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Email").fill(`e2e-${Date.now()}@example.com`);
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByRole("navigation", { name: "Main" })).toBeVisible();

  await page.getByRole("link", { name: "Résumés" }).click();
  await page.getByRole("button", { name: "Upload résumé" }).click();
  await page.getByLabel("Résumé file").setInputFiles(RESUME);
  await page.getByLabel("Title").fill("E2E résumé");
  await page.getByRole("button", { name: "Upload", exact: true }).click();
  await expect(page.getByRole("heading", { name: "ATS check" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByRole("heading", { name: "What an ATS sees" })).toBeVisible();

  await page.getByRole("link", { name: "Home" }).click();
  await page.getByRole("tab", { name: "Paste text" }).click();
  await page.getByLabel("Job description").fill(JOB);
  await page.getByLabel("Résumé").selectOption({ label: "E2E résumé (v1)" });
  await page.getByRole("button", { name: "Analyze" }).click();

  await expect(page.getByRole("heading", { name: /Match score: \d+/ })).toBeVisible({
    timeout: 90_000,
  });
  await expect(page.getByRole("table", { name: "Requirements" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Gaps", exact: true })).toBeVisible();
});
