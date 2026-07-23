const path = require("node:path");
const { test, expect } = require("playwright/test");

const repoRoot = path.resolve(__dirname, "..", "..");
const frontendUrl = `file://${path.join(repoRoot, "frontend", "index.html")}`;
const apiOrigin = "http://127.0.0.1:8787";
const allowedApiPaths = new Set([
  "/analysis-units/tcja-2017-representative-provisions",
  "/sources",
  "/ai-decision-ledger",
  "/reports/tcja-2017-representative-provisions",
  "/candidates/status",
]);

function fixturePayload(pathname) {
  if (pathname === "/analysis-units/tcja-2017-representative-provisions") {
    return {
      title: "TCJA privacy browser fixture",
      expected_outputs: { plain_language_summary: "fixture summary" },
      claims: [{ claim: "fixture claim" }],
    };
  }
  if (pathname === "/sources") {
    return { sources: [] };
  }
  if (pathname === "/ai-decision-ledger") {
    return { entries: [] };
  }
  if (pathname === "/reports/tcja-2017-representative-provisions") {
    return { report_id: "fixture_report" };
  }
  if (pathname === "/candidates/status") {
    return {
      candidates: [
        {
          title: "candidate",
          publication_state: "draft",
          promotable: false,
          source_record_ids: ["source"],
          candidate_provision_ids: ["candidate_provision"],
          promotion_blockers: [{ gate: "promotion_disabled", reason: "disabled" }],
        },
      ],
    };
  }
  return {};
}

test("local privacy controls do not transmit local values", async ({ page }) => {
  const observedRequests = [];
  const unexpectedApiRequests = [];

  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    observedRequests.push({
      method: request.method(),
      url: request.url(),
      postData: request.postData() || "",
    });

    if (url.origin === apiOrigin && allowedApiPaths.has(url.pathname)) {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify(fixturePayload(url.pathname)),
      });
      return;
    }

    if (url.origin === apiOrigin) {
      unexpectedApiRequests.push(request.url());
      await route.fulfill({ status: 599, body: "Unexpected local API request" });
      return;
    }

    await route.continue();
  });

  await page.goto(frontendUrl);
  await expect(page.locator("#analysis")).toContainText("TCJA privacy browser fixture");

  const initialCount = observedRequests.length;
  await page.locator("#filing-unit").selectOption("head");
  await page.locator("#dependents").fill("9");
  await page.locator("#itemizes").check();
  await page.locator("#clear-local").click();
  await expect(page.locator("#local-result")).toContainText("No household financial values are collected or sent");

  const localControlRequests = observedRequests.slice(initialCount);
  expect(unexpectedApiRequests).toEqual([]);
  expect(localControlRequests).toEqual([]);

  const serializedRequests = JSON.stringify(observedRequests);
  expect(serializedRequests).not.toContain("head");
  expect(serializedRequests).not.toContain("sentinel-local-only");
  expect(serializedRequests).not.toContain("dependents=9");
});
