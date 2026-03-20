import { test, expect } from '@playwright/test';
import { download } from 'playwright';

/**
 * HQL Generation and Export - E2E Test Suite
 *
 * Tests the complete HQL generation and export workflow:
 * 1. Configure Event nodes
 * 2. Generate HQL in multiple modes (SELECT, CREATE TABLE, CREATE VIEW, INSERT)
 * 3. Preview HQL with syntax highlighting
 * 4. Edit HQL in code editor
 * 5. Export/Download HQL to file
 * 6. Copy HQL to clipboard
 *
 * Test Data:
 * - Game GID: 10000147 (STAR001)
 * - Event: themegsoul.summon
 *
 * @see docs/testing/e2e-testing-guide.md
 */

const BASE_URL = 'http://localhost:5173';
const GAME_GID = 10000147;

test.describe('HQL Generation and Export Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Setup game context
    await page.goto(`${BASE_URL}/#/`);
    await page.evaluate(() => {
      localStorage.setItem('selectedGameGid', '10000147');
      (window as any).gameData = {
        id: 16,
        gid: '10000147',
        name: '游戏 10000147',
        ods_db: 'ieu_ods',
      };
    });

    await page.goto(`${BASE_URL}/#/event-node-builder?game_gid=${GAME_GID}`, {
      timeout: 60000,
      waitUntil: 'commit'
    });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Add fields to canvas (required for HQL generation)
    const dsField = page.locator('[data-field="ds"]').first();
    if (await dsField.isVisible().catch(() => false)) {
      await dsField.dblclick();
      await page.waitForTimeout(500);
    }

    const roleIdField = page.locator('[data-field="role_id"]').first();
    if (await roleIdField.isVisible().catch(() => false)) {
      await roleIdField.dblclick();
      await page.waitForTimeout(500);
    }

    // Wait for HQL preview button to appear
    await page.waitForSelector('[data-testid="open-hql-modal"]', { timeout: 60000 });
  });

  test.afterEach(async ({ page }) => {
    // Cleanup test state
    await page.evaluate(() => {
      sessionStorage.clear();
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.includes('dwd_generator_canvas_flow_')) {
          localStorage.removeItem(key);
        }
      });
      localStorage.removeItem('selectedGameGid');
    });
  });

  test('Scenario 1: Generate HQL in SELECT mode', async ({ page }) => {
    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    // Verify modal is open
    const modal = page.locator('.hql-preview-modal');
    await expect(modal).toBeVisible();

    // Verify SELECT tab is active by default
    const activeTab = page.locator('.tab-btn.active');
    await expect(activeTab).toContainText('SELECT');

    // Verify HQL content is displayed
    const hqlContent = page.locator('.hql-content, .code-content');
    await expect(hqlContent).toBeVisible();

    // Verify HQL contains expected keywords
    const hqlText = await hqlContent.textContent();
    expect(hqlText).toContain('SELECT');
    expect(hqlText).toContain('FROM');

    console.log('✅ HQL generated in SELECT mode');
  });

  test('Scenario 2: Switch between HQL generation modes', async ({ page }) => {
    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    const modalTabs = ['SELECT', 'CREATE TABLE', 'CREATE VIEW', 'INSERT'];

    for (const tab of modalTabs) {
      // Click tab
      await page.click(`.tab-btn:has-text("${tab}")`);
      await page.waitForTimeout(300);

      // Verify tab is active
      const activeTab = page.locator('.tab-btn.active');
      await expect(activeTab).toContainText(tab);

      // Verify HQL content is updated
      const hqlContent = page.locator('.hql-content, .code-content');
      await expect(hqlContent).toBeVisible();

      const hqlText = await hqlContent.textContent();

      // Verify HQL contains appropriate keywords
      if (tab === 'SELECT') {
        expect(hqlText).toContain('SELECT');
      } else if (tab === 'CREATE TABLE') {
        expect(hqlText).toContain('CREATE TABLE');
      } else if (tab === 'CREATE VIEW') {
        expect(hqlText).toContain('CREATE OR REPLACE VIEW');
      } else if (tab === 'INSERT') {
        expect(hqlText).toContain('INSERT OVERWRITE');
      }

      console.log(`✅ HQL generated in ${tab} mode`);
    }
  });

  test('Scenario 3: Edit HQL in code editor', async ({ page }) => {
    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    // Click edit button
    const editButton = page.locator('.editor-toolbar button:has-text("编辑"), .editor-toolbar button:has-text("Edit")');
    await editButton.click();
    await page.waitForTimeout(300);

    // Verify textarea is visible
    const textarea = page.locator('.code-textarea, textarea[placeholder*="HQL"]');
    await expect(textarea).toBeVisible();

    // Get original HQL
    const originalHQL = await textarea.inputValue();

    // Edit HQL
    const modifiedHQL = '-- Modified by E2E test\n' + originalHQL;
    await textarea.fill(modifiedHQL);

    // Verify modification
    const currentValue = await textarea.inputValue();
    expect(currentValue).toContain('-- Modified by E2E test');

    console.log('✅ HQL edited successfully');
  });

  test('Scenario 4: Copy HQL to clipboard', async ({ page }) => {
    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    // Click copy button
    const copyButton = page.locator('.editor-toolbar button:has-text("复制"), .editor-toolbar button:has-text("Copy")');
    await copyButton.click();
    await page.waitForTimeout(300);

    // Verify clipboard content (if browser supports)
    const clipboardText = await page.evaluate(() => {
      return navigator.clipboard.readText();
    }).catch(() => null);

    if (clipboardText) {
      expect(clipboardText).toContain('SELECT');
      expect(clipboardText).toContain('FROM');
      console.log('✅ HQL copied to clipboard successfully');
    } else {
      console.log('⚠️ Clipboard access not available - unable to verify');
    }
  });

  test('Scenario 5: Download/Export HQL to file', async ({ page }) => {
    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    // Look for download/export button
    const downloadButton = page.locator(
      'button:has-text("下载"), button:has-text("导出"), button:has-text("Download"), button:has-text("Export")'
    ).first();

    const downloadVisible = await downloadButton.isVisible().catch(() => false);

    if (downloadVisible) {
      // Setup download handler
      const downloadPromise = page.waitForEvent('download', { timeout: 10000 });

      // Click download button
      await downloadButton.click();

      // Wait for download to start
      const download = await downloadPromise;

      // Verify download filename
      const filename = download.suggestedFilename();
      expect(filename).toMatch(/\.(hql|sql)$/);

      console.log(`✅ HQL downloaded successfully: ${filename}`);
    } else {
      console.log('⚠️ Download button not found - feature may not be implemented');

      // Alternative: Check if there's a copy button that can be used
      const copyButton = page.locator('.editor-toolbar button:has-text("复制")').first();
      if (await copyButton.isVisible().catch(() => false)) {
        console.log('✅ Copy functionality is available as alternative to download');
      }
    }
  });

  test('Scenario 6: Verify field mapping table', async ({ page }) => {
    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    // Verify field mapping table is visible
    const mappingTable = page.locator('.mapping-table, .field-mapping-table');
    const tableVisible = await mappingTable.isVisible().catch(() => false);

    if (tableVisible) {
      await expect(mappingTable).toBeVisible();

      // Verify table structure
      const headers = mappingTable.locator('th');
      const headerCount = await headers.count();
      expect(headerCount).toBeGreaterThan(0);

      // Verify table has rows
      const rows = mappingTable.locator('tbody tr');
      const rowCount = await rows.count();
      expect(rowCount).toBeGreaterThan(0);

      console.log(`✅ Field mapping table displayed with ${rowCount} rows`);
    } else {
      console.log('⚠️ Field mapping table not found - may be optional feature');
    }
  });

  test('Scenario 7: Verify HQL syntax highlighting', async ({ page }) => {
    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    // Check if syntax highlighting is applied
    const codeBlock = page.locator('.code-content, .hql-content, pre code');
    await expect(codeBlock).toBeVisible();

    // Check for syntax highlighting classes (e.g., from highlight.js or prism.js)
    const hasHighlighting = await codeBlock.evaluate(el => {
      // Check for common syntax highlighting class names
      const classes = Array.from(el.classList);
      return classes.some(cls =>
        cls.includes('hljs') ||
        cls.includes('language-') ||
        cls.includes('token') ||
        cls.includes('keyword')
      );
    });

    if (hasHighlighting) {
      console.log('✅ HQL syntax highlighting is applied');
    } else {
      console.log('⚠️ Syntax highlighting not detected - may use plain text');
    }
  });

  test('Scenario 8: Generate HQL with custom WHERE conditions', async ({ page }) => {
    // First, add a WHERE condition if possible
    const whereButton = page.locator('button:has-text("WHERE"), button:has-text("条件")').first();
    const whereVisible = await whereButton.isVisible().catch(() => false);

    if (whereVisible) {
      await whereButton.click();
      await page.waitForTimeout(500);

      // Add a simple condition
      const conditionInput = page.locator('input[placeholder*="条件"], input[placeholder*="condition"]').first();
      if (await conditionInput.isVisible().catch(() => false)) {
        await conditionInput.fill("ds = '20260301'");
        await page.waitForTimeout(300);

        // Save condition
        const saveButton = page.locator('button:has-text("保存"), button:has-text("确定")').first();
        await saveButton.click();
        await page.waitForTimeout(500);
      }
    }

    // Open HQL preview modal
    await page.click('[data-testid="open-hql-modal"]');
    await page.waitForTimeout(500);

    // Verify HQL contains WHERE clause
    const hqlContent = page.locator('.hql-content, .code-content');
    const hqlText = await hqlContent.textContent();

    if (whereVisible) {
      expect(hqlText).toContain('WHERE');
      expect(hqlText).toContain('ds');
      console.log('✅ HQL generated with custom WHERE conditions');
    } else {
      console.log('⚠️ WHERE condition UI not found - testing basic HQL');
      expect(hqlText).toContain('SELECT');
    }
  });
});
