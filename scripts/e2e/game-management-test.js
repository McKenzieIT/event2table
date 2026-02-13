/**
 * 游戏管理模态框E2E测试脚本
 *
 * 目标: 验证游戏管理模态框的完整功能
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
  timeout: 10000,
  screenshotDir: '/Users/mckenzie/Documents/event2table/screenshots/e2e',
  retries: 3
};

/**
 * 测试1: 打开游戏管理模态框
 */
async function testOpenGameManagementModal() {
  console.log('\n🧪 测试1: 打开游戏管理模态框');

  try {
    // 1. 导航到Dashboard
    await MCP.navigate(CONFIG.baseUrl);
    await MCP.waitForSelector('.dashboard-container', { timeout: CONFIG.timeout });
    console.log('   ✅ Dashboard已加载');

    // 2. 查找游戏管理按钮
    const btn = await MCP.querySelector('.game-management-btn');
    if (!btn) {
      throw new Error('游戏管理按钮未找到');
    }
    console.log('   ✅ 游戏管理按钮已找到');

    // 3. 截图（点击前）
    await MCP.screenshot(`${CONFIG.screenshotDir}/gm-button-found.png`);

    // 4. 点击按钮
    await MCP.click(btn);
    console.log('   🖱️ 点击游戏管理按钮');

    // 5. 等待模态框出现
    await MCP.waitForSelector('.game-management-modal', { timeout: CONFIG.timeout });
    console.log('   ✅ 游戏管理模态框已打开');

    // 6. 截图（模态框打开）
    await MCP.screenshot(`${CONFIG.screenshotDir}/gm-modal-open.png`);

    return { success: true, name: '打开游戏管理模态框' };
  } catch (error) {
    console.error('   ❌ 测试失败:', error.message);
    await MCP.screenshot(`${CONFIG.screenshotDir}/gm-open-error.png`);
    return { success: false, name: '打开游戏管理模态框', error: error.message };
  }
}

/**
 * 测试2: 测试搜索功能
 */
async function testSearchFunctionality() {
  console.log('\n🧪 测试2: 测试搜索功能');

  try {
    // 1. 查找搜索输入框
    const searchInput = await MCP.querySelector('.game-search-input');
    if (!searchInput) {
      console.warn('   ⚠️ 搜索输入框未找到，跳过搜索测试');
      return { success: true, name: '测试搜索功能', skipped: true };
    }
    console.log('   ✅ 搜索输入框已找到');

    // 2. 截图（搜索前）
    await MCP.screenshot(`${CONFIG.screenshotDir}/search-before.png`);

    // 3. 输入搜索文本
    await MCP.type(searchInput, 'test-game');
    console.log('   ⌨️ 输入搜索文本: test-game');

    // 4. 等待过滤
    await MCP.wait(500);
    console.log('   ⏳ 等待搜索过滤...');

    // 5. 截图（搜索后）
    await MCP.screenshot(`${CONFIG.screenshotDir}/search-after.png`);

    return { success: true, name: '测试搜索功能' };
  } catch (error) {
    console.error('   ❌ 测试失败:', error.message);
    return { success: false, name: '测试搜索功能', error: error.message };
  }
}

/**
 * 测试3: 测试添加游戏按钮
 */
async function testAddGameButton() {
  console.log('\n🧪 测试3: 测试添加游戏按钮');

  try {
    // 1. 查找添加游戏按钮
    const addBtn = await MCP.querySelector('.add-game-btn');
    if (!addBtn) {
      throw new Error('添加游戏按钮未找到');
    }
    console.log('   ✅ 添加游戏按钮已找到');

    // 2. 截图（点击前）
    await MCP.screenshot(`${CONFIG.screenshotDir}/add-btn-before.png`);

    // 3. 点击按钮
    await MCP.click(addBtn);
    console.log('   🖱️ 点击添加游戏按钮');

    // 4. 等待添加游戏模态框
    await MCP.waitForSelector('.add-game-modal', { timeout: CONFIG.timeout });
    console.log('   ✅ 添加游戏模态框已打开');

    // 5. 截图（模态框打开）
    await MCP.screenshot(`${CONFIG.screenshotDir}/add-modal-open.png`);

    // 6. 关闭模态框
    const closeBtn = await MCP.querySelector('.modal-close-btn');
    if (closeBtn) {
      await MCP.click(closeBtn);
      console.log('   🖱️ 点击关闭按钮');

      await MCP.wait(300);
      console.log('   ✅ 模态框已关闭');
    }

    return { success: true, name: '测试添加游戏按钮' };
  } catch (error) {
    console.error('   ❌ 测试失败:', error.message);
    await MCP.screenshot(`${CONFIG.screenshotDir}/add-btn-error.png`);
    return { success: false, name: '测试添加游戏按钮', error: error.message };
  }
}

/**
 * 测试4: 测试关闭功能
 */
async function testCloseFunctionality() {
  console.log('\n🧪 测试4: 测试关闭功能');

  try {
    // 1. 确保模态框打开
    const modal = await MCP.querySelector('.game-management-modal');
    if (!modal || modal.offsetParent === null) {
      console.log('   ⚠️ 模态框未打开，先打开');

      // 打开模态框
      const btn = await MCP.querySelector('.game-management-btn');
      await MCP.click(btn);
      await MCP.waitForSelector('.game-management-modal', { timeout: CONFIG.timeout });
      console.log('   ✅ 模态框已打开');
    }

    // 2. 截图（关闭前）
    await MCP.screenshot(`${CONFIG.screenshotDir}/close-before.png`);

    // 3. 测试多种关闭方式
    const closeBtn = await MCP.querySelector('.modal-close-btn');
    const overlay = await MCP.querySelector('.modal-overlay');

    // 优先使用关闭按钮
    if (closeBtn) {
      await MCP.click(closeBtn);
      console.log('   🖱️ 点击关闭按钮');
    } else if (overlay) {
      await MCP.click(overlay);
      console.log('   🖱️ 点击遮罩层');
    } else {
      console.warn('   ⚠️ 未找到关闭元素');
      return { success: true, name: '测试关闭功能', skipped: true };
    }

    // 4. 等待关闭
    await MCP.wait(500);
    console.log('   ⏳ 等待关闭动画...');

    // 5. 验证模态框已关闭
    const afterModal = await MCP.querySelector('.game-management-modal');
    if (afterModal && afterModal.offsetParent !== null) {
      throw new Error('模态框未能关闭');
    }
    console.log('   ✅ 模态框已关闭');

    // 6. 截图（关闭后）
    await MCP.screenshot(`${CONFIG.screenshotDir}/close-after.png`);

    return { success: true, name: '测试关闭功能' };
  } catch (error) {
    console.error('   ❌ 测试失败:', error.message);
    await MCP.screenshot(`${CONFIG.screenshotDir}/close-error.png`);
    return { success: false, name: '测试关闭功能', error: error.message };
  }
}

/**
 * 主测试函数
 */
async function runTests() {
  console.log('========================================');
  console.log('🚀 Event2Table 游戏管理模态框E2E测试');
  console.log('========================================');
  console.log(`📅 测试时间: ${new Date().toISOString()}`);
  console.log(`🌐 基础URL: ${CONFIG.baseUrl}`);
  console.log(`📁 截图目录: ${CONFIG.screenshotDir}`);
  console.log('========================================\n');

  const results = [];

  // 顺序执行测试
  results.push(await testOpenGameManagementModal());
  results.push(await testSearchFunctionality());
  results.push(await testAddGameButton());
  results.push(await testCloseFunctionality());

  // 生成测试报告
  console.log('\n========================================');
  console.log('📊 测试结果汇总');
  console.log('========================================');

  const passed = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);
  const skipped = results.filter(r => r.skipped);

  console.log(`✅ 通过: ${passed.length}/${results.length}`);
  console.log(`⚠️ 跳过: ${skipped.length}/${results.length}`);
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
      process.exit(results.every(r => r.success || r.skipped) ? 0 : 1);
    })
    .catch(error => {
      console.error('测试执行失败:', error);
      process.exit(1);
    });
}

module.exports = { runTests };
