/**
 * Dashboard卡片E2E测试脚本
 *
 * 目标: 验证所有Dashboard快捷操作卡片可正常点击和导航
 *
 * 环境要求:
 * - 后端服务运行中 (http://127.0.0.1:5001)
 * - 前端开发服务器运行中 (http://localhost:5173)
 * - chrome-devtools-mcp已安装
 */

const MCP = require('chrome-devtools-mcp');

// 测试配置
const CONFIG = {
  baseUrl: 'http://localhost:5173',
  timeout: 10000, // 10秒超时
  screenshotDir: '/Users/mckenzie/Documents/event2table/screenshots/e2e',
  retries: 3
};

// 测试场景
const TEST_SCENARIOS = [
  {
    name: '管理游戏卡片',
    selector: '.action-card[href="/games"]',
    expectedUrl: '/games',
    description: '点击"管理游戏"卡片应导航到游戏列表'
  },
  {
    name: '管理事件卡片',
    selector: '.action-card[href="/events"]',
    expectedUrl: '/events',
    description: '点击"管理事件"卡片应导航到事件列表'
  },
  {
    name: 'HQL画布卡片',
    selector: '.action-card[href="/canvas"]',
    expectedUrl: '/canvas',
    description: '点击"HQL画布"卡片应导航到画布页面'
  },
  {
    name: '流程管理卡片',
    selector: '.action-card[href="/flows"]',
    expectedUrl: '/flows',
    description: '点击"流程管理"卡片应导航到流程管理'
  }
];

/**
 * 执行单个卡片测试
 */
async function testCard(card) {
  console.log(`\n🧪 测试: ${card.name}`);
  console.log(`   ${card.description}`);

  try {
    // 1. 导航到Dashboard
    console.log('   Ⓨ 导航到Dashboard...');
    await MCP.navigate(CONFIG.baseUrl);
    await MCP.waitForSelector('.dashboard-container', { timeout: CONFIG.timeout });
    console.log('   ✅ Dashboard已加载');

    // 2. 清空控制台日志
    await MCP.clearConsoleLogs();
    console.log('   🧹 控制台已清空');

    // 3. 查找卡片元素
    const cardElement = await MCP.querySelector(card.selector);
    if (!cardElement) {
      throw new Error(`卡片未找到: ${card.selector}`);
    }
    console.log('   ✅ 卡片已找到');

    // 4. 截图记录（点击前）
    const beforeScreenshot = `${CONFIG.screenshotDir}/dashboard-before-${card.name.replace(/\s+/g, '-')}.png`;
    await MCP.screenshot(beforeScreenshot);
    console.log(`   📸 截图已保存: ${beforeScreenshot}`);

    // 5. 点击卡片
    console.log('   🖱️ 点击卡片...');
    await MCP.click(cardElement);

    // 6. 等待导航
    console.log('   ⏳ 等待导航...');
    await MCP.waitForLoadState('networkidle', { timeout: CONFIG.timeout });

    // 7. 获取当前URL
    const currentUrl = await MCP.getUrl();
    console.log(`   🌐 当前URL: ${currentUrl}`);

    // 8. 验证URL包含预期路径
    if (!currentUrl.includes(card.expectedUrl)) {
      throw new Error(`URL验证失败: 期望 ${card.expectedUrl}, 实际 ${currentUrl}`);
    }
    console.log('   ✅ URL验证成功');

    // 9. 检查控制台错误
    const logs = await MCP.getConsoleLogs();
    const errors = logs.filter(log => log.level === 'error');
    const warnings = logs.filter(log => log.level === 'warning');

    if (errors.length > 0) {
      console.error(`   ❌ 发现 ${errors.length} 个错误:`);
      errors.forEach(err => {
        console.error(`      [${err.source}] ${err.message}`);
        if (err.stack) console.error(`      堆栈: ${err.stack}`);
      });
    } else {
      console.log('   ✅ 无JavaScript错误');
    }

    if (warnings.length > 0) {
      console.warn(`   ⚠️ 发现 ${warnings.length} 个警告:`);
      warnings.forEach(warn => {
        console.warn(`      [${warn.source}] ${warn.message}`);
      });
    } else {
      console.log('   ✅ 无React警告');
    }

    // 10. 截图记录（点击后）
    const afterScreenshot = `${CONFIG.screenshotDir}/dashboard-after-${card.name.replace(/\s+/g, '-')}.png`;
    await MCP.screenshot(afterScreenshot);
    console.log(`   📸 截图已保存: ${afterScreenshot}`);

    console.log(`   ✅ 测试通过: ${card.name}\n`);

    return {
      success: true,
      name: card.name,
      errors: errors,
      warnings: warnings,
      screenshots: [beforeScreenshot, afterScreenshot]
    };

  } catch (error) {
    console.error(`   ❌ 测试失败: ${card.name}`);
    console.error(`   错误: ${error.message}`);

    // 错误截图
    const errorScreenshot = `${CONFIG.screenshotDir}/dashboard-error-${card.name.replace(/\s+/g, '-')}.png`;
    await MCP.screenshot(errorScreenshot);
    console.log(`   📸 错误截图: ${errorScreenshot}`);

    return {
      success: false,
      name: card.name,
      error: error.message,
      screenshot: errorScreenshot
    };
  }
}

/**
 * 主测试函数
 */
async function runTests() {
  console.log('========================================');
  console.log('🚀 Event2Table Dashboard卡片E2E测试');
  console.log('========================================');
  console.log(`📅 测试时间: ${new Date().toISOString()}`);
  console.log(`🌐 基础URL: ${CONFIG.baseUrl}`);
  console.log(`📁 截图目录: ${CONFIG.screenshotDir}`);
  console.log('========================================\n');

  const results = [];

  for (const scenario of TEST_SCENARIOS) {
    const result = await testCard(scenario);
    results.push(result);
  }

  // 生成测试报告
  console.log('\n========================================');
  console.log('📊 测试结果汇总');
  console.log('========================================');

  const passed = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  console.log(`✅ 通过: ${passed.length}/${results.length}`);
  console.log(`❌ 失败: ${failed.length}/${results.length}`);

  if (failed.length > 0) {
    console.log('\n失败详情:');
    failed.forEach(f => {
      console.log(`  - ${f.name}: ${f.error || '未知错误'}`);
    });
  }

  console.log('\n========================================');
  console.log('🎉 测试完成');
  console.log('========================================\n');

  return results;
}

// 导出测试函数
if (require.main === module) {
  runTests()
    .then(results => {
      process.exit(results.every(r => r.success) ? 0 : 1);
    })
    .catch(error => {
      console.error('测试执行失败:', error);
      process.exit(1);
    });
}

module.exports = { testCard, runTests };
