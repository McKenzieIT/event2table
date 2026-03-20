import { test, expect } from '@playwright/test';

test.describe('Search Box Alignment - Events Page', () => {
  test('should have properly aligned search input wrapper and input', async ({ page }) => {
    // 访问Events页面
    await page.goto('http://localhost:5173/#/events/list?game_gid=10000147');

    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 获取搜索框容器（SearchInput组件生成的.search-input-wrapper）
    const searchInputWrapper = page.locator('.filters-bar .search-input-wrapper').first();
    await expect(searchInputWrapper).toBeVisible();

    // 获取实际的输入框（SearchInput组件内部的.search-input）
    const actualInput = page.locator('.filters-bar .search-input').first();
    await expect(actualInput).toBeVisible();

    // 验证：输入框应该在容器内部（不应该溢出）
    const wrapperBox = await searchInputWrapper.boundingBox();
    const inputBox = await actualInput.boundingBox();

    console.log('SearchInput wrapper box:', wrapperBox);
    console.log('SearchInput box:', inputBox);

    // 检查宽度关系：输入框宽度应该接近或等于容器宽度
    expect(inputBox?.width).toBeLessThanOrEqual(wrapperBox!.width + 5); // 允许5px误差

    // 验证：输入框应该垂直居中于容器内
    expect(inputBox?.y).toBeGreaterThanOrEqual(wrapperBox!.y - 2); // 允许2px误差
    expect(inputBox!.y + inputBox!.height).toBeLessThanOrEqual(wrapperBox!.y + wrapperBox!.height + 2);

    console.log('✅ 搜索框对齐检查通过');
  });

  test('should match search box style with Parameters page', async ({ page }) => {
    // 先访问Parameters页面（参考标准）
    await page.goto('http://localhost:5173/#/parameters/enhanced?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 获取Parameters页面的搜索框（使用SearchInput组件）
    const paramsSearchBox = page.locator('.search-input-wrapper').first();
    await expect(paramsSearchBox).toBeVisible();

    const paramsInput = page.locator('.search-input').first();
    await expect(paramsInput).toBeVisible();

    // 记录Parameters页面的搜索框特征
    const paramsHasSearchInputWrapper = await paramsSearchBox.count();
    const paramsHasSearchInputClass = await paramsInput.count();

    console.log('Parameters page - search-input-wrapper count:', paramsHasSearchInputWrapper);
    console.log('Parameters page - search-input count:', paramsHasSearchInputClass);

    // 现在访问Events页面
    await page.goto('http://localhost:5173/#/events/list?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // 检查Events页面是否也使用SearchInput组件
    const eventsHasSearchInputWrapper = await page.locator('.filters-bar .search-input-wrapper').count();
    const eventsHasSearchInputClass = await page.locator('.filters-bar .search-input').count();

    console.log('Events page - search-input-wrapper count:', eventsHasSearchInputWrapper);
    console.log('Events page - search-input count:', eventsHasSearchInputClass);

    // 验证：Events页面现在也使用SearchInput组件（修复后）
    expect(eventsHasSearchInputWrapper).toBeGreaterThan(0);
    expect(eventsHasSearchInputClass).toBeGreaterThan(0);

    // 验证：Events页面不应该再有.cyber-input（旧的Input组件）
    const eventsHasCyberInput = await page.locator('.filters-bar .cyber-input').count();
    console.log('Events page - cyber-input count (should be 0 after fix):', eventsHasCyberInput);
    expect(eventsHasCyberInput).toBe(0);
  });

  test('should not have double borders or padding', async ({ page }) => {
    await page.goto('http://localhost:5173/#/events/list?game_gid=10000147');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // 获取SearchInput组件的wrapper（修复后使用SearchInput）
    const searchWrapper = page.locator('.filters-bar .search-input-wrapper').first();
    await expect(searchWrapper).toBeVisible();

    // 获取实际的input元素
    const actualInput = page.locator('.filters-bar .search-input').first();
    await expect(actualInput).toBeVisible();

    // 检查是否存在双重边框（修复前使用Input组件时会有这个问题）
    const wrapperBorder = await searchWrapper.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return {
        borderLeft: styles.borderLeftWidth,
        borderRight: styles.borderRightWidth,
        borderTop: styles.borderTopWidth,
        borderBottom: styles.borderBottomWidth
      };
    });

    const inputBorder = await actualInput.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return {
        borderLeft: styles.borderLeftWidth,
        borderRight: styles.borderRightWidth,
        borderTop: styles.borderTopWidth,
        borderBottom: styles.borderBottomWidth
      };
    });

    console.log('SearchInput wrapper border:', wrapperBorder);
    console.log('SearchInput border:', inputBorder);

    // 使用SearchInput组件后：
    // - wrapper不应该有边框（只有display: flex等布局样式）
    // - input应该有边框（这是正确的）
    const wrapperHasBorder = Object.values(wrapperBorder).some(v => v !== '0px');
    const inputHasBorder = Object.values(inputBorder).some(v => v !== '0px');

    console.log('Wrapper has border (should be false):', wrapperHasBorder);
    console.log('Input has border (should be true):', inputHasBorder);

    // 验证：wrapper不应该有边框，input应该有边框（修复后的正确行为）
    expect(wrapperHasBorder).toBe(false);
    expect(inputHasBorder).toBe(true);

    // 验证：不应该再有旧的.cyber-input（Input组件）
    const cyberInputExists = await page.locator('.filters-bar .cyber-input').count();
    console.log('CyberInput count (should be 0 after fix):', cyberInputExists);
    expect(cyberInputExists).toBe(0);
  });
});
