import { test, expect } from '@playwright/test';

test.describe('Game Edit Fix Verification', () => {
  test.afterEach(async ({ page }) => {
    // 清理测试状态
    await page.evaluate(() => {
      sessionStorage.clear();
      localStorage.removeItem('selectedGameGid');
      localStorage.removeItem('gamesFilters');
      localStorage.removeItem('gamesSearchQuery');
      if ((window as any).gameData) {
        delete (window as any).gameData;
      }
    });
    await page.waitForTimeout(300);
  });

  test('should load edit form with GID parameter', async ({ page }) => {
    // Navigate to edit page using GID
    await page.goto('/#/games/10000147/edit');

    // Wait for page to load
    await page.waitForSelector('#app-root', { timeout: 5000 });

    // Wait for form to appear (not loading state)
    await page.waitForSelector('input[name="name"]', { state: 'visible', timeout: 10000 });

    // Verify form title
    await expect(page.locator('h1')).toContainText('编辑游戏');

    // Verify field is pre-filled with data
    const nameInput = page.locator('input[name="name"]');
    const nameValue = await nameInput.inputValue();
    console.log('Game name loaded:', nameValue);

    // Verify the name has a value (not empty)
    expect(nameValue.trim().length).toBeGreaterThan(0);

    // Verify GID field is disabled
    const gidInput = page.locator('input[name="gid"]');
    await expect(gidInput).toBeDisabled();

    // Verify ODS radio button is selected (check for selected class)
    const selectedOption = page.locator('.option-card.selected, .option-card.selected-green');
    const optionCount = await selectedOption.count();
    expect(optionCount).toBeGreaterThan(0);
    console.log('✅ Edit form loaded successfully with GID parameter');
  });

  test('should verify API endpoint works', async ({ page }) => {
    // Test the API directly
    const response = await page.request.get('http://127.0.0.1:5001/api/games/by-gid/10000147');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data.gid).toBe('10000147');
    expect(data.data.name).toBeTruthy();

    console.log('✅ API endpoint /api/games/by-gid/10000147 works correctly');
  });
});
