import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E测试配置
 *
 * 支持两种测试模式：
 * 1. UI测试: 使用page对象测试前端界面（默认）
 * 2. HQL V2测试: 测试后端HQL生成API（独立项目配置）
 */
export default defineConfig({
  testDir: "./tests/e2e",

  // UI测试配置（默认）
  fullyParallel: false, // Disable full parallel due to game context race conditions
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Use single worker for stable test execution

  // 全局配置
  reporter: "html",
  globalSetup: "./tests/e2e/global-setup.ts", // HQL V2测试的全局设置

  use: {
    baseURL: "http://127.0.0.1:5001",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },

  // 测试项目配置
  projects: [
    // 默认项目: UI测试
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      testIgnore: [
        "**/manual/**",
        "**/textbutton-fieldcanvas.spec.ts",
        "**/wait-test.spec.ts",
        "**/where-builder-debug.spec.ts",
        "**/where-builder.spec.ts",
        "**/tdz-diagnostic.spec.ts",
      ],
    },
    // HQL V2测试项目: 使用独立配置
    {
      name: "hql-v2",
      testMatch: /tests\/e2e\/hql-v2\/.*/,  // 仅匹配hql-v2子目录
      testIgnore: ["**/*.md"],  // Ignore markdown files (CLAUDE.md, etc.)
      use: {
        ...devices["Desktop Chrome"],
        baseURL: "http://127.0.0.1:5001",
      },
      fullyParallel: true,        // HQL V2测试启用并行
      workers: 3,                 // 性能优化的worker数
      retries: 0,                 // 不重试（测试自带重试逻辑）
    },
  ],
});
