import { test, expect } from "@playwright/test";

test.describe("Game Context Diagnosis", () => {
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
      localStorage.removeItem('selectedGameData');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test("Diagnose game context loading", async ({ page }) => {
    console.log("=== 开始诊断游戏上下文加载 ===");

    // 设置游戏上下文到localStorage
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
      console.log("游戏上下文已设置:", gameData);
    });

    // 访问事件节点构建器页面
    console.log("导航到事件节点构建器页面...");
    await page.goto("http://127.0.0.1:5001/#/event-node-builder?game_gid=10000147");

    // 等待React应用加载
    console.log("等待React应用渲染（5秒）...");
    await page.waitForTimeout(5000);

    // 检查页面状态
    const pageState = await page.evaluate(() => {
      return {
        url: window.location.href,
        hash: window.location.hash,
        gameData: window.gameData,
        localStorageGameGid: localStorage.getItem('selectedGameGid'),
        localStorageGameData: localStorage.getItem('selectedGameData'),
        hasEventNodeBuilder: !!document.querySelector('.event-node-builder'),
        hasLoadingMsg: !!document.querySelector('.event-node-builder-loading'),
        bodyHTML: document.body.innerHTML.substring(0, 500),
        bodyClasses: document.body.className,
      };
    });

    console.log("=== 页面状态 ===");
    console.log(JSON.stringify(pageState, null, 2));

    // 检查React应用是否加载
    const reactRoot = await page.locator('#app-root').count();
    console.log("React app-root count:", reactRoot);

    // 检查是否有错误
    const errors = await page.evaluate(() => {
      const errors = [];
      // 检查React错误
      const rootElement = document.getElementById('app-root');
      if (rootElement && rootElement._reactRootContainer) {
        errors.push("React root container found");
      }
      return errors;
    });

    console.log("Errors:", errors);
  });
});
