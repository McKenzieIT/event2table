/**
 * 按钮点击测试脚本
 * 用于测试Event2Table所有页面的按钮点击响应
 */

class ButtonClickTester {
  constructor() {
    this.results = [];
    this.currentPage = '';
  }

  /**
   * 获取所有可点击的按钮
   */
  getAllButtons() {
    const buttons = Array.from(document.querySelectorAll('button, [role="button"]'));
    return buttons
      .filter(btn => btn.offsetParent !== null) // 只包含可见按钮
      .map((btn, index) => ({
        index,
        text: btn.textContent.trim().substring(0, 100),
        className: btn.className,
        disabled: btn.disabled,
        type: btn.type || 'button',
        tagName: btn.tagName,
        ariaLabel: btn.getAttribute('aria-label') || ''
      }));
  }

  /**
   * 判断是否为危险操作按钮
   */
  isDangerousButton(buttonText) {
    const dangerousKeywords = ['删除', 'delete', 'remove', '清空', '清除', '重置'];
    return dangerousKeywords.some(keyword => buttonText.toLowerCase().includes(keyword));
  }

  /**
   * 点击单个按钮并记录结果
   */
  async clickButton(button, index) {
    const result = {
      index,
      text: button.text,
      className: button.className,
      dangerous: this.isDangerousButton(button.text),
      tested: false,
      response: '',
      error: null
    };

    // 跳过危险按钮
    if (result.dangerous) {
      result.response = 'Skipped (dangerous operation)';
      return result;
    }

    // 跳过禁用按钮
    if (button.disabled) {
      result.response = 'Skipped (disabled)';
      return result;
    }

    try {
      // 获取当前URL
      const beforeUrl = window.location.href;
      const beforeModalCount = document.querySelectorAll('[role="dialog"], .modal, [class*="modal"]').length;

      // 点击按钮
      const btnElement = document.querySelectorAll('button, [role="button"]')[index];
      btnElement.click();

      // 等待响应
      await new Promise(resolve => setTimeout(resolve, 500));

      // 检测响应类型
      const afterUrl = window.location.href;
      const afterModalCount = document.querySelectorAll('[role="dialog"], .modal, [class*="modal"]').length;

      if (beforeUrl !== afterUrl) {
        result.response = 'Navigation';
        result.details = `From: ${beforeUrl}\nTo: ${afterUrl}`;
      } else if (afterModalCount > beforeModalCount) {
        result.response = 'Modal opened';
      } else if (afterModalCount < beforeModalCount) {
        result.response = 'Modal closed';
      } else {
        result.response = 'Click registered (no visible change)';
      }

      result.tested = true;

    } catch (error) {
      result.error = error.message;
      result.response = 'Error';
    }

    return result;
  }

  /**
   * 测试当前页面的所有按钮
   */
  async testCurrentPage() {
    this.currentPage = window.location.href;
    console.log(`\n📄 Testing page: ${this.currentPage}`);

    const buttons = this.getAllButtons();
    console.log(`🔍 Found ${buttons.length} buttons`);

    const results = [];

    for (let i = 0; i < buttons.length; i++) {
      const button = buttons[i];
      console.log(`  [${i + 1}/${buttons.length}] Testing: "${button.text}"`);

      const result = await this.clickButton(button, i);
      results.push(result);

      // 如果发生了导航，需要重新获取按钮
      if (result.response === 'Navigation') {
        console.log(`    ⚠️ Navigation occurred, reloading page...`);
        window.location.href = this.currentPage;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    this.results.push({
      page: this.currentPage,
      totalButtons: buttons.length,
      testedButtons: results.filter(r => r.tested).length,
      skippedButtons: results.filter(r => !r.tested).length,
      results
    });

    return results;
  }

  /**
   * 生成测试报告
   */
  generateReport() {
    let report = '\n' + '='.repeat(80) + '\n';
    report += 'BUTTON CLICK TEST REPORT\n';
    report += '='.repeat(80) + '\n';

    let totalButtons = 0;
    let totalTested = 0;
    let totalSkipped = 0;
    let totalErrors = 0;

    this.results.forEach(pageResult => {
      report += `\n📄 Page: ${pageResult.page}\n`;
      report += `   Total buttons: ${pageResult.totalButtons}\n`;
      report += `   Tested: ${pageResult.testedButtons}\n`;
      report += `   Skipped: ${pageResult.skippedButtons}\n`;

      const pageErrors = pageResult.results.filter(r => r.error);
      if (pageErrors.length > 0) {
        report += `   ❌ Errors: ${pageErrors.length}\n`;
      }

      report += '\n';

      // 显示每个按钮的测试结果
      pageResult.results.forEach(r => {
        const icon = r.error ? '❌' : (r.dangerous || !r.tested ? '⏭️ ' : '✅');
        report += `   ${icon} [${r.index}] "${r.text}"\n`;
        report += `       Response: ${r.response}\n`;
        if (r.details) {
          report += `       Details: ${r.details}\n`;
        }
        if (r.error) {
          report += `       Error: ${r.error}\n`;
        }
        report += '\n';
      });

      totalButtons += pageResult.totalButtons;
      totalTested += pageResult.testedButtons;
      totalSkipped += pageResult.skippedButtons;
      totalErrors += pageErrors.length;
    });

    report += '='.repeat(80) + '\n';
    report += 'SUMMARY\n';
    report += '='.repeat(80) + '\n';
    report += `Total pages tested: ${this.results.length}\n`;
    report += `Total buttons: ${totalButtons}\n`;
    report += `Total tested: ${totalTested}\n`;
    report += `Total skipped: ${totalSkipped}\n`;
    report += `Total errors: ${totalErrors}\n`;
    report += '='.repeat(80) + '\n';

    return report;
  }

  /**
   * 导出为JSON
   */
  exportJSON() {
    return JSON.stringify(this.results, null, 2);
  }
}

// 创建全局实例
window.buttonClickTester = new ButtonClickTester();

// 使用方法：
// 1. 导航到页面
// 2. 运行: await window.buttonClickTester.testCurrentPage()
// 3. 生成报告: console.log(window.buttonClickTester.generateReport())
// 4. 导出JSON: copy(window.buttonClickTester.exportJSON())
