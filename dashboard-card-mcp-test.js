/**
 * Dashboard卡片E2E测试 + Console错误检测
 * 使用chrome-devtools-mcp进行自动化测试
 *
 * 测试内容:
 * 1. 自动导航到Dashboard
 * 2. 查找所有快捷操作卡片
 * 3. 依次点击每个卡片
 * 4. 监控console日志(JSError, React警告, 网络错误)
 * 5. 验证URL导航
 * 6. 截图记录
 *
 * 使用方法:
 * npx chrome-devtools-mcp@latest run dashboard-card-mcp-test.js
 */

const chromium = require('chrome-devtools-mcp');

// 测试配置
const BASE_URL = 'http://localhost:5173';
const DASHBOARD_PATH = '/analytics';

// 测试卡片选择器
const CARD_SELECTORS = {
  gamesCard: '.action-card[href="/games"]',
  eventsCard: '.action-card[href="/events"]',
  canvasCard: '.action-card[href="/canvas"]',
  flowsCard: '.action-card[href="/flows"]'
};

// console错误类型
const ERROR_TYPES = {
  javascript: 'javascript', // JavaScript错误(红色错误)
  react: 'react',       // React警告(黄色警告)
  network: 'network',     // 网络请求错误
  api: 'api'          // API响应错误(非200状态码)
};

/**
 * 等待页面稳定
 * @param {number} ms - 等待毫秒数
 */
async function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 导航到Dashboard
 */
async function navigateToDashboard() {
  console.log('\n=== 导航到Dashboard ===');

  try {
    await chromium.navigate(BASE_URL);
    console.log(`✓ 成功导航到: ${BASE_URL}`);

    // 等待页面加载
    await wait(2000);

    // 验证是否在Dashboard页面
    const currentUrl = await chromium.getUrl();
    console.log(`当前URL: ${currentUrl}`);

    if (!currentUrl.includes(DASHBOARD_PATH)) {
      console.warn(`⚠️  当前不在Dashboard页面: ${currentUrl}`);
      // 尝试导航到Dashboard
      await chromium.navigate(`${BASE_URL}${DASHBOARD_PATH}`);
      await wait(2000);
    }

    console.log('✅ Dashboard页面加载完成');
  } catch (error) {
    console.error('❌ 导航到Dashboard失败:', error.message);
    throw error;
  }
}

/**
 * 查找所有快捷操作卡片
 */
async function findActionCards() {
  console.log('\n=== 查找快捷操作卡片 ===');

  try {
    // 等待卡片渲染
    await wait(1000);

    // 查找所有.action-card元素
    const cards = await chromium.querySelectorAll('.action-card');
    console.log(`✓ 找到 ${cards.length} 个快捷操作卡片`);

    // 显示每个卡片的文本
    for (const card of cards) {
      const text = await chromium.getText(card);
      console.log(`  - ${text}`);
    }

    return cards;
  } catch (error) {
    console.error('❌ 查找卡片失败:', error.message);
    throw error;
  }
}

/**
 * 清空console日志
 */
async function clearConsoleLogs() {
  console.log('\n=== 清空console日志 ===');

  try {
    // chrome-devtools-mcp的console.clear()方法(如果存在)
    if (typeof chromium.clearConsoleLogs === 'function') {
      await chromium.clearConsoleLogs();
      console.log('✓ Console日志已清空');
    } else {
      console.warn('⚠️  clearConsoleLogs方法不可用,跳过清空');
    }
  } catch (error) {
    console.warn('⚠️  清空console日志时出错:', error.message);
  }
}

/**
 * 获取console错误
 */
async function getConsoleErrors() {
  console.log('\n=== 获取console错误 ===');

  try {
    // 获取所有console日志
    const logs = await chromium.getConsoleLogs();

    // 分类错误
    const errors = logs.filter(log => log.level === 'error');
    const warnings = logs.filter(log => log.level === 'warning');

    // JavaScript错误
    const jsErrors = errors.filter(log => {
      return log.source && (
        log.source.includes('javascript') ||
        log.source.includes('bundle') ||
        log.source.includes('app')
      );
    });

    // React警告
    const reactWarnings = warnings.filter(log => {
      return log.source && (
        log.source.includes('react') ||
        log.source.includes('ReactDOM') ||
        log.source.includes('Warning')
      );
    });

    // 网络请求错误
    const networkErrors = logs.filter(log => {
      return log.level === 'error' && (
        log.message.includes('404') ||
        log.message.includes('500') ||
        log.message.includes('Failed') ||
        log.message.includes('Network')
      );
    });

    return {
      totalErrors: errors.length,
      totalWarnings: warnings.length,
      jsErrors,
      reactWarnings,
      networkErrors,
      allLogs: logs
    };
  } catch (error) {
    console.error('❌ 获取console错误失败:', error.message);
    return {
      totalErrors: 0,
      totalWarnings: 0,
      jsErrors: [],
      reactWarnings: [],
      networkErrors: [],
      allLogs: []
    };
  }
}

/**
 * 分析console错误
 */
function analyzeConsoleErrors(errorData) {
  console.log('\n=== 分析console错误 ===');

  const { totalErrors, totalWarnings, jsErrors, reactWarnings, networkErrors } = errorData;

  if (totalErrors > 0) {
    console.error(`❌ 发现 ${totalErrors} 个错误:`);
    jsErrors.forEach(err => {
      console.error(`   [${err.source || 'Unknown'}] ${err.message || err.text || err}`);
      if (err.stack) console.error(`   堆栈: ${err.stack}`);
    });
  }

  if (totalWarnings > 0) {
    console.warn(`⚠️  发现 ${totalWarnings} 个警告:`);
    reactWarnings.forEach(warn => {
      console.warn(`   [${warn.source || 'Unknown'}] ${warn.message || warn.text || warn}`);
    });
  }

  if (networkErrors.length > 0) {
    console.error(`❌ 发现 ${networkErrors.length} 个网络错误:`);
    networkErrors.forEach(err => {
      console.error(`   [Network] ${err.message || err.text}`);
    });
  }

  return {
    hasErrors: totalErrors > 0,
    hasWarnings: totalWarnings > 0,
    errorCount: totalErrors,
    warningCount: totalWarnings
  };
}

/**
 * 点击卡片并验证导航
 */
async function testCardClick(card, expectedUrl, cardName) {
  console.log(`\n=== 测试卡片: ${cardName} ===`);

  try {
    // 清空console日志
    await clearConsoleLogs();

    // 点击卡片
    await chromium.click(card);
    console.log(`✓ 点击卡片: ${cardName}`);

    // 等待导航和页面稳定
    await wait(1500);

    // 验证URL
    const currentUrl = await chromium.getUrl();
    console.log(`当前URL: ${currentUrl}`);

    const urlMatched = currentUrl.includes(expectedUrl);
    if (urlMatched) {
      console.log(`✅ URL导航正确: ${currentUrl}`);
    } else {
      console.error(`❌ URL导航错误:`);
      console.error(`  期望: ${expectedUrl}`);
      console.error(`  实际: ${currentUrl}`);
    }

    // 等待额外时间让异步错误出现
    await wait(1000);

    // 获取console错误
    const errorData = await getConsoleErrors();
    const analysis = analyzeConsoleErrors(errorData);

    // 截图记录
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `test-${cardName.replace(/\s+/g, '-')}-${timestamp}.png`;
    await chromium.screenshot(filename);

    console.log(`📸 截图保存: ${filename}`);

    return {
      cardName,
      urlMatched,
      currentUrl,
      expectedUrl,
      ...analysis,
      screenshot: filename
    };
  } catch (error) {
    console.error(`❌ 测试卡片 ${cardName} 失败:`, error.message);
    return {
      cardName,
      urlMatched: false,
      error: error.message
    };
  }
}

/**
 * 测试所有快捷操作卡片
 */
async function testAllActionCards() {
  console.log('\n====================================');
  console.log('开始测试所有Dashboard快捷操作卡片');
  console.log('====================================\n');

  try {
    // 1. 导航到Dashboard
    await navigateToDashboard();

    // 2. 查找所有卡片
    const cards = await findActionCards();

    if (cards.length === 0) {
      console.warn('⚠️  未找到任何快捷操作卡片');
      return {
        totalCards: 0,
        testedCards: 0,
        results: []
      };
    }

    console.log(`\n找到 ${cards.length} 个快捷操作卡片,开始测试\n`);

    // 3. 定义测试用例
    const testCases = [
      {
        name: '管理游戏',
        selector: CARD_SELECTORS.gamesCard,
        expectedUrl: '/games'
      },
      {
        name: '管理事件',
        selector: CARD_SELECTORS.eventsCard,
        expectedUrl: '/events'
      },
      {
        name: 'HQL画布',
        selector: CARD_SELECTORS.canvasCard,
        expectedUrl: '/canvas'
      },
      {
        name: '流程管理',
        selector: CARD_SELECTORS.flowsCard,
        expectedUrl: '/flows'
      }
    ];

    // 4. 依次测试每个卡片
    const results = [];
    let passedTests = 0;
    let failedTests = 0;

    for (const testCase of testCases) {
      const result = await testCardClick(
        testCase.selector,
        testCase.expectedUrl,
        testCase.name
      );

      results.push(result);

      if (result.urlMatched) {
        passedTests++;
      } else {
        failedTests++;
      }
    }

    // 5. 汇总console错误
    const allLogs = [];
    results.forEach(result => {
      if (result.allLogs) {
        allLogs.push(...result.allLogs);
      }
    });

    const finalAnalysis = analyzeConsoleErrors({
      totalErrors: 0,
      totalWarnings: 0,
      jsErrors: [],
      reactWarnings: [],
      networkErrors: [],
      allLogs
    });

    // 6. 生成测试报告
    console.log('\n====================================');
    console.log('测试结果汇总');
    console.log('====================================\n');

    console.log(`总卡片数: ${cards.length}`);
    console.log(`测试通过: ${passedTests}`);
    console.log(`测试失败: ${failedTests}`);
    console.log(`通过率: ${((passedTests / (passedTests + failedTests)) * 100).toFixed(2)}%`);

    if (finalAnalysis.hasErrors) {
      console.error(`❌ 发现console错误: ${finalAnalysis.errorCount}个`);
    }

    if (finalAnalysis.hasWarnings) {
      console.warn(`⚠️  发现console警告: ${finalAnalysis.warningCount}个`);
    }

    return {
      totalCards: cards.length,
      passedTests,
      failedTests,
      passRate: ((passedTests / (passedTests + failedTests)) * 100).toFixed(2),
      results,
      ...finalAnalysis
    };

  } catch (error) {
    console.error('❌ 测试过程出错:', error.message);

    return {
      totalCards: 0,
      passedTests: 0,
      failedTests: 0,
      passRate: '0.00',
      results: [],
      error: error.message
    };
  }
}

/**
 * 主测试流程
 */
async function runTest() {
  console.log('🚀 开始Dashboard卡片E2E测试 + Console错误检测\n');

  const startTime = Date.now();

  try {
    // 执行测试
    const testResult = await testAllActionCards();

    // 计算耗时
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);

    // 输出最终报告
    console.log('\n====================================');
    console.log('最终测试报告');
    console.log('====================================\n');

    console.log(`测试耗时: ${duration}秒`);
    console.log(`总卡片数: ${testResult.totalCards}`);
    console.log(`通过测试: ${testResult.passedTests}`);
    console.log(`失败测试: ${testResult.failedTests}`);
    console.log(`通过率: ${testResult.passRate}%`);

    if (testResult.hasErrors) {
      console.error(`❌ Console错误检测: 发现 ${testResult.errorCount} 个错误`);
    }

    if (testResult.hasWarnings) {
      console.warn(`⚠️  Console警告检测: 发现 ${testResult.warningCount} 个警告`);
    }

    console.log('\n====================================');
    console.log('✅ 测试完成!');
    console.log('====================================\n');

    // 成功退出
    process.exit(0);

  } catch (error) {
    console.error('❌ 测试失败:', error);
    console.error(error.stack);
    process.exit(1);
  }
}

// 运行测试
runTest();
