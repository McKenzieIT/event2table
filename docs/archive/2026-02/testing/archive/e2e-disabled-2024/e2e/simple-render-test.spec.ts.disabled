import { test, expect } from "@playwright/test";

test.describe("Simple Render Test", () => {
  test.afterEach(async ({ page }) => {
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
      localStorage.removeItem('selectedGameData');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test("EventNodeBuilder should render after extended wait", async ({ page }) => {
    // Enable console logging
    page.on("console", (msg) => {
      console.log(`[${msg.type()}]`, msg.text());
    });

    page.on("pageerror", (err) => {
      console.error("Page Error:", err.message);
    });

    // Set up game context
    await page.goto("http://127.0.0.1:5001/");
    await page.evaluate(() => {
      const gameData = {
        id: 325,
        gid: 10000147,
        name: "Duplicate Game",
        ods_db: "ieu_ods"
      };
      localStorage.setItem('selectedGameGid', '10000147');
      localStorage.setItem('selectedGameData', JSON.stringify(gameData));
      window.gameData = gameData;
    });

    // Navigate to event-node-builder
    console.log("Navigating to event-node-builder...");
    await page.goto("http://127.0.0.1:5001/#/event-node-builder?game_gid=10000147");

    // Wait longer for everything to settle
    console.log("Waiting 10 seconds for components to render...");
    await page.waitForTimeout(10000);

    // Check page state
    const pageState = await page.evaluate(() => {
      const appRoot = document.getElementById('app-root');
      return {
        hasAppRoot: !!appRoot,
        appRootHTML: appRoot?.innerHTML.substring(0, 1000) || "",
        hasEventNodeBuilder: !!document.querySelector('.event-node-builder'),
        hasSidebarLeft: !!document.querySelector('.sidebar-left'),
        hasFieldCanvas: !!document.querySelector('.field-canvas'),
        gameData: window.gameData,
      };
    });

    console.log("Page State:", JSON.stringify(pageState, null, 2));

    // Try to find the container
    const container = page.locator(".event-node-builder");
    const count = await container.count();
    console.log("EventNodeBuilder container count:", count);

    if (count > 0) {
      console.log("✅ Test PASSED: EventNodeBuilder rendered");
    } else {
      console.log("❌ Test FAILED: EventNodeBuilder not found");

      // Take a screenshot for debugging
      await page.screenshot({ path: 'test-results/simple-render-debug.png' });
      console.log("Screenshot saved to test-results/simple-render-debug.png");
    }

    // This assertion will show the actual state
    expect(count).toBe(1);
  });
});
