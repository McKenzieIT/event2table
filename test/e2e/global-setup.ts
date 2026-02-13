import { FullConfig } from '@playwright/test';

/**
 * E2E测试全局设置
 *
 * 在所有测试运行前执行的设置：
 * - 确保后端服务器运行
 * - 准备测试数据
 */
async function globalSetup(config: FullConfig) {
  // TODO: 启动Flask服务器（如果需要）
  // TODO: 初始化测试数据库

  console.log('E2E测试全局设置完成');
}

export default globalSetup;
