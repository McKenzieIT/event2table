import { test, expect } from '@playwright/test';

test.describe('Check Left Sidebar', () => {
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

  test('Check left sidebar structure', async ({ page }) => {
    // 设置游戏数据
    await page.goto('/#/');
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      (window as any).gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
    });

    await page.goto('/#/event-node-builder?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    console.log('\n=== Checking page structure ===');

    // Check for event section
    const eventSection = await page.locator('.event-section').count();
    console.log('Event section count:', eventSection);

    // Check for base field section
    const baseFieldSection = await page.locator('.base-field-section').count();
    console.log('Base field section count:', baseFieldSection);

    // Check for collapsed sections
    const collapsed = await page.locator('.collapsed').count();
    console.log('Collapsed sections:', collapsed);

    // Check for event list
    const eventList = await page.locator('.event-list').count();
    console.log('Event list count:', eventList);

    // Check for base fields
    const baseFields = await page.locator('[data-field]').count();
    console.log('Base fields with data-field:', baseFields);

    // Screenshot
    await page.screenshot({ path: 'left-sidebar-check.png', fullPage: true });

    // Try to click on sections to expand them
    const clickableSections = await page.locator('.section-header').all();
    console.log('Section headers:', clickableSections.length);

    for (let i = 0; i < Math.min(3, clickableSections.length); i++) {
      try {
        await clickableSections[i].click();
        await page.waitForTimeout(500);
        console.log(`Clicked section ${i}`);
      } catch (e) {
        console.log(`Failed to click section ${i}`);
      }
    }

    // Check again for base fields
    const baseFieldsAfter = await page.locator('[data-field]').count();
    console.log('Base fields after clicking:', baseFieldsAfter);

    // Final screenshot
    await page.screenshot({ path: 'left-sidebar-check-after.png', fullPage: true });
  });
});
