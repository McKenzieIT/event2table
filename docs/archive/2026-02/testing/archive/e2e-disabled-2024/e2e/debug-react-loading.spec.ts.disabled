import { test, expect } from "@playwright/test";

test.describe("Debug React Loading", () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test("Check browser console and page state", async ({ page }) => {
    // Enable console logging
    page.on("console", (msg) => {
      console.log(`Browser Console [${msg.type()}]:`, msg.text());
    });

    page.on("pageerror", (err) => {
      console.error("Browser Error:", err.message);
      console.error("Stack:", err.stack);
    });

    // Navigate to the page
    console.log("Navigating to http://127.0.0.1:5001/");
    await page.goto("http://127.0.0.1:5001/", { waitUntil: "networkidle" });

    // Wait a bit for any JS to execute
    await page.waitForTimeout(3000);

    // Check page state
    const pageState = await page.evaluate(() => {
      return {
        url: window.location.href,
        hash: window.location.hash,
        title: document.title,
        bodyHTML: document.body.innerHTML.substring(0, 1000),
        hasAppRoot: !!document.getElementById("app-root"),
        appRootChildren: document.getElementById("app-root")?.childElementCount || 0,
        appRootContent: document.getElementById("app-root")?.innerHTML.substring(0, 500) || "",
        scripts: Array.from(document.scripts).map((s) => s.src),
        stylesheets: Array.from(document.styleSheets).map((s) => s.href),
      };
    });

    console.log("=== Page State ===");
    console.log(JSON.stringify(pageState, null, 2));

    // Now navigate to event-node-builder with hash
    console.log("\nNavigating to event-node-builder with hash");
    await page.goto("http://127.0.0.1:5001/#/event-node-builder?game_gid=10000147");

    await page.waitForTimeout(5000);

    const hashPageState = await page.evaluate(() => {
      return {
        url: window.location.href,
        hash: window.location.hash,
        bodyHTML: document.body.innerHTML.substring(0, 1000),
        appRootContent: document.getElementById("app-root")?.innerHTML.substring(0, 1000) || "",
      };
    });

    console.log("\n=== Hash Page State ===");
    console.log(JSON.stringify(hashPageState, null, 2));
  });
});
