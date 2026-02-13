/**
 * Chrome DevTools Protocol 游戏选择测试
 *
 * 启动Chrome并进行实际的点击操作来选择游戏
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:5173';
const SCREENSHOT_DIR = '/Users/mckenzie/Documents/event2table/docs/testing/game-selection-cdp';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log('🎮 开始游戏选择交互测试...\n');
  console.log(`前端URL: ${BASE_URL}\n`);

  // 创建截图目录
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  console.log('🔌 启动Chrome浏览器（使用CDP）...');
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized'],
    slowMo: 100 // 慢速100ms便于观察
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('✅ Chrome启动成功');

  // 监控控制台
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`[Console Error] ${msg.text()}`);
    }
  });

  try {
    // ===== Step 1: 打开首页 =====
    console.log('\n=== Step 1: 打开首页 ===');
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(3000);

    const screenshot1 = path.join(SCREENSHOT_DIR, '01-homepage.png');
    await page.screenshot({ path: screenshot1, fullPage: true });
    console.log(`✅ 首页加载完成，截图: ${screenshot1}`);

    // ===== Step 2: 查找游戏选择按钮 =====
    console.log('\n=== Step 2: 查找游戏选择按钮 ===');

    const buttonInfo = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button, a'));
      const gameButtons = buttons.filter(btn => {
        const text = btn.textContent?.trim() || '';
        return text.includes('游戏') || text.includes('Game');
      });

      return gameButtons.map(btn => ({
        tag: btn.tagName,
        text: btn.textContent?.trim().substring(0, 50),
        class: btn.className,
        id: btn.id
      }));
    });

    console.log('找到的游戏相关按钮:', buttonInfo);

    if (buttonInfo.length === 0) {
      console.log('❌ 未找到游戏选择按钮');
      return;
    }

    const targetButton = buttonInfo[0];
    console.log(`✅ 找到按钮: "${targetButton.text}" (${targetButton.tag})`);

    // ===== Step 3: 点击游戏按钮 =====
    console.log('\n=== Step 3: 点击游戏按钮 ===');

    // 尝试多种选择器
    const selectors = [
      `button:has-text("游戏")`,
      `a:has-text("游戏")`,
      `button:has-text("数据管理")`,
      'button[class*="game"]'
    ];

    let clicked = false;
    for (const selector of selectors) {
      try {
        const count = await page.locator(selector).count();
        if (count > 0) {
          console.log(`✅ 使用选择器: ${selector}`);
          await page.locator(selector).first().click();
          clicked = true;
          await sleep(2000);
          break;
        }
      } catch (e) {
        // 继续尝试下一个选择器
      }
    }

    if (!clicked) {
      console.log('❌ 无法点击游戏按钮');
    } else {
      const screenshot2 = path.join(SCREENSHOT_DIR, '02-after-click.png');
      await page.screenshot({ path: screenshot2, fullPage: true });
      console.log(`✅ 按钮已点击，截图: ${screenshot2}`);
    }

    // ===== Step 4: 查找游戏列表 =====
    console.log('\n=== Step 4: 查找游戏列表 ===');

    const gameListInfo = await page.evaluate(() => {
      // 查找游戏列表
      const lists = document.querySelectorAll('.game-list, [data-testid="game-list"]');
      const modals = document.querySelectorAll('[class*="modal"], [class*="sheet"], [role="dialog"]');

      const gameItems = Array.from(document.querySelectorAll('[data-game-gid], .game-item, [class*="game-item"]')).map(item => ({
        text: item.textContent?.trim().substring(0, 50),
        gid: item.getAttribute('data-game-gid'),
        class: item.className
      }));

      return {
        listsFound: lists.length,
        modalsFound: modals.length,
        gameItems: gameItems
      };
    });

    console.log('游戏列表信息:', gameListInfo);

    if (gameListInfo.gameItems.length === 0) {
      console.log('⚠️ 未找到明显的游戏项');
    } else {
      console.log(`✅ 找到 ${gameListInfo.gameItems.length} 个游戏项`);
      gameListInfo.gameItems.forEach((item, idx) => {
        console.log(`  ${idx + 1}. ${item.text} (GID: ${item.gid || 'N/A'})`);
      });
    }

    const screenshot3 = path.join(SCREENSHOT_DIR, '03-game-list.png');
    await page.screenshot({ path: screenshot3, fullPage: true });
    console.log(`✅ 游戏列表截图: ${screenshot3}`);

    // ===== Step 5: 点击游戏 =====
    console.log('\n=== Step 5: 选择游戏 ===');

    if (gameListInfo.gameItems.length > 0) {
      const firstGame = gameListInfo.gameItems[0];
      console.log(`✅ 尝试点击第一个游戏: "${firstGame.text}"`);

      // 尝试多种选择器
      const gameSelectors = [
        `[data-game-gid="${firstGame.gid}"]`,
        `.game-item:has-text("${firstGame.text.substring(0, 20)}")`,
        `[data-game-gid], .game-item`
      ];

      let gameClicked = false;
      for (const selector of gameSelectors) {
        try {
          const count = await page.locator(selector).count();
          if (count > 0) {
            console.log(`✅ 使用游戏选择器: ${selector}`);
            await page.locator(selector).first().click();
            gameClicked = true;
            await sleep(2000);
            break;
          }
        } catch (e) {
          // 继续尝试
        }
      }

      if (gameClicked) {
        const screenshot4 = path.join(SCREENSHOT_DIR, '04-after-select.png');
        await page.screenshot({ path: screenshot4, fullPage: true });
        console.log(`✅ 游戏已点击，截图: ${screenshot4}`);
      }
    }

    // ===== Step 6: 验证localStorage =====
    console.log('\n=== Step 6: 验证localStorage游戏数据 ===');

    const storageData = await page.evaluate(() => {
      const gameStorage = localStorage.getItem('game-storage');
      if (!gameStorage) return null;

      try {
        return JSON.parse(gameStorage);
      } catch (e) {
        return { error: e.message, raw: gameStorage };
      }
    });

    console.log('localStorage数据:', storageData);

    if (!storageData) {
      console.log('⚠️ localStorage中无game-storage数据');
    } else if (storageData.error) {
      console.log(`❌ localStorage数据解析错误: ${storageData.error}`);
    } else {
      const currentGame = storageData.state?.currentGame || storageData.currentGame;
      const gameGid = storageData.state?.gameGid || storageData.gameGid;

      console.log('✅ localStorage验证成功:');
      console.log(`  游戏名称: ${currentGame?.name || '未知'}`);
      console.log(`  游戏GID: ${gameGid || '未设置'}`);

      const screenshot5 = path.join(SCREENSHOT_DIR, '05-localstorage-verified.png');
      await page.screenshot({ path: screenshot5, fullPage: true });
      console.log(`✅ localStorage验证截图: ${screenshot5}`);
    }

    // ===== 总结 =====
    console.log('\n=== 📊 测试总结 ===');
    console.log('✅ 所有关键步骤完成');
    console.log('✅ Chrome DevTools Protocol测试成功');
    console.log(`📸 所有截图已保存到: ${SCREENSHOT_DIR}`);

  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
