/**
 * 连接到已运行的Chrome并执行实际的游戏选择操作
 *
 * 使用Chrome DevTools Protocol (CDP)连接到现有Chrome实例
 * 进行实际的点击操作来选择游戏
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:5173';
const SCREENSHOT_DIR = '/Users/mckenzie/Documents/event2table/docs/testing/game-selection-test';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Test results
const results = [];

function log(step, status, message) {
  const entry = { step, status, message, timestamp: new Date().toISOString() };
  results.push(entry);
  console.log(`[${status}] ${step}: ${message}`);
}

async function main() {
  console.log('🎮 开始游戏选择交互测试...\n');
  console.log(`前端URL: ${BASE_URL}\n`);

  // 创建截图目录
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  // 连接到Chrome
  console.log('🔌 连接到Chrome浏览器...');
  const browser = await chromium.connectOverCDP('http://localhost:9222');

  const context = browser.contexts()[0];
  const page = context.pages()[0] || await context.newPage();

  console.log('✅ Chrome连接成功');

  try {
    // ===== Step 1: 打开首页 =====
    log('Step 1', '开始', '打开首页');
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await sleep(3000);

    const screenshot1 = path.join(SCREENSHOT_DIR, '01-homepage.png');
    await page.screenshot({ path: screenshot1, fullPage: true });
    log('Step 1', '✅', `首页加载完成，截图: ${screenshot1}`);

    // ===== Step 2: 查找游戏选择按钮 =====
    log('Step 2', '开始', '查找游戏选择按钮');

    const buttonInfo = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button, a'));
      const gameButtons = buttons.filter(btn => {
        const text = btn.textContent?.trim() || '';
        return text.includes('游戏') || text.includes('Game') || text.includes('数据管理');
      });

      return gameButtons.map(btn => ({
        tag: btn.tagName,
        text: btn.textContent?.trim().substring(0, 50),
        class: btn.className,
        id: btn.id,
        selector: btn.tagName === 'BUTTON' ? `button:has-text("${btn.textContent?.trim().substring(0, 20)}")` : `a:has-text("${btn.textContent?.trim().substring(0, 20)}")`
      }));
    });

    console.log('找到的游戏相关按钮:', buttonInfo);

    if (buttonInfo.length === 0) {
      log('Step 2', '❌', '未找到游戏选择按钮');
      return;
    }

    const targetButton = buttonInfo[0];
    log('Step 2', '✅', `找到按钮: "${targetButton.text}" (${targetButton.tag})`);

    // ===== Step 3: 点击游戏按钮 =====
    log('Step 3', '开始', `点击按钮: "${targetButton.text}"`);

    const selector = targetButton.selector;
    await page.locator(selector).first().click();
    await sleep(2000); // 等待动画

    const screenshot2 = path.join(SCREENSHOT_DIR, '02-after-click.png');
    await page.screenshot({ path: screenshot2, fullPage: true });
    log('Step 3', '✅', `按钮已点击，截图: ${screenshot2}`);

    // ===== Step 4: 查找游戏列表 =====
    log('Step 4', '开始', '查找游戏列表');

    const gameListInfo = await page.evaluate(() => {
      // 查找游戏列表或模态框
      const lists = document.querySelectorAll('.game-list, [data-testid="game-list"], .game-item, [data-game-gid]');
      const modals = document.querySelectorAll('[class*="modal"], [class*="sheet"], [role="dialog"]');

      const gameItems = Array.from(document.querySelectorAll('[data-game-gid], .game-item, [data-game-name]')).map(item => ({
        gid: item.getAttribute('data-game-gid'),
        name: item.getAttribute('data-game-name') || item.textContent?.trim().substring(0, 50),
        text: item.textContent?.trim().substring(0, 50)
      }));

      return {
        listsFound: lists.length,
        modalsFound: modals.length,
        gameItems: gameItems
      };
    });

    console.log('游戏列表信息:', gameListInfo);

    if (gameListInfo.listsFound === 0 && gameListInfo.modalsFound === 0) {
      log('Step 4', '⚠️', '未找到明显的游戏列表或模态框');
    } else {
      log('Step 4', '✅', `找到列表: ${gameListInfo.listsFound}, 模态框: ${gameListInfo.modalsFound}`);
    }

    const screenshot3 = path.join(SCREENSHOT_DIR, '03-game-list.png');
    await page.screenshot({ path: screenshot3, fullPage: true });
    log('Step 4', '✅', `游戏列表截图: ${screenshot3}`);

    // ===== Step 5: 查找并点击STAR001游戏 =====
    log('Step 5', '开始', '查找并选择STAR001游戏');

    // 列出所有可能的游戏项
    const allGames = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('[data-game-gid], .game-item, button, a')).filter(el => {
        const text = el.textContent?.trim() || '';
        return text.includes('STAR') || text.includes('001') || el.hasAttribute('data-game-gid');
      }).map(el => ({
        tag: el.tagName,
        text: el.textContent?.trim().substring(0, 50),
        gid: el.getAttribute('data-game-gid'),
        class: el.className
      }));
    });

    console.log('所有游戏项:', allGames);

    if (allGames.length === 0) {
      log('Step 5', '❌', '未找到任何游戏项');
    } else {
      const star001 = allGames.find(g => g.text.includes('STAR') || g.gid?.includes('001'));

      if (star001) {
        log('Step 5', '✅', `找到STAR001: "${star001.text}"`);

        // 点击游戏项
        await page.locator(`[data-game-gid="${star001.gid}"], .game-item:has-text("STAR")`).first().click();
        await sleep(2000);

        const screenshot4 = path.join(SCREENSHOT_DIR, '04-after-select.png');
        await page.screenshot({ path: screenshot4, fullPage: true });
        log('Step 5', '✅', `游戏已选择，截图: ${screenshot4}`);
      } else {
        log('Step 5', '⚠️', '找到游戏但未找到STAR001');
        // 点击第一个游戏
        const firstGame = allGames[0];
        await page.locator(`[data-game-gid="${firstGame.gid}"], .game-item`).first().click();
        await sleep(2000);

        const screenshot4 = path.join(SCREENSHOT_DIR, '04-selected-first.png');
        await page.screenshot({ path: screenshot4, fullPage: true });
        log('Step 5', '⚠️', `已选择第一个游戏: "${firstGame.text}"`);
      }
    }

    // ===== Step 6: 验证localStorage =====
    log('Step 6', '开始', '验证localStorage游戏数据');

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
      log('Step 6', '⚠️', 'localStorage中无game-storage数据');
    } else if (storageData.error) {
      log('Step 6', '❌', `localStorage数据解析错误: ${storageData.error}`);
    } else {
      const currentGame = storageData.state?.currentGame || storageData.currentGame;
      const gameGid = storageData.state?.gameGid || storageData.gameGid;

      log('Step 6', '✅', `localStorage验证成功:
        - 游戏名称: ${currentGame?.name || '未知'}
        - 游戏GID: ${gameGid || '未设置'}
        - 完整数据: ${JSON.stringify(currentGame).substring(0, 100)}...`);

      const screenshot5 = path.join(SCREENSHOT_DIR, '05-localstorage-verified.png');
      await page.screenshot({ path: screenshot5, fullPage: true });
    }

    // ===== 打印总结 =====
    console.log('\n=== 📊 测试总结 ===');
    console.log(`总步骤数: ${results.length}`);
    console.log(`成功: ${results.filter(r => r.status === '✅').length}`);
    console.log(`失败: ${results.filter(r => r.status === '❌').length}`);
    console.log(`警告: ${results.filter(r => r.status === '⚠️').length}`);

    // 保存结果
    const reportPath = '/Users/mckenzie/Documents/event2table/docs/testing/game-selection-report.json';
    fs.writeFileSync(reportPath, JSON.stringify({ results }, null, 2));
    console.log(`\n📄 测试报告已保存: ${reportPath}`);
    console.log(`📸 所有截图已保存到: ${SCREENSHOT_DIR}`);

  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    console.error(error.stack);
  }
}

main().catch(console.error);
