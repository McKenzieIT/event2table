/**
 * TestReporter - 测试报告生成器
 *
 * 职责：生成HTML测试报告，展示测试结果统计和详细信息
 *
 * @example
 * const reporter = new TestReporter();
 * reporter.addReport({
 *   testName: 'T01: 单事件基础生成',
 *   success: true,
 *   attempts: 1,
 *   fixLog: [],
 *   duration: 1234
 * });
 * const html = reporter.generateHTML();
 */
export interface TestReportData {
  testName: string;
  success: boolean;
  attempts: number;
  fixLog: Array<{
    timestamp: string;
    testName: string;
    errorType: string;
    fixAction: string;
    success: boolean;
    duration: number;
  }>;
  duration: number;
}

export class TestReporter {
  private reports: TestReportData[] = [];

  /**
   * Add a test report
   * @param report - The test report data
   * @throws {TypeError} If report is missing required fields
   */
  addReport(report: TestReportData): void {
    if (!report || typeof report !== 'object') {
      throw new TypeError('report must be an object');
    }
    if (typeof report.testName !== 'string') {
      throw new TypeError('report.testName must be a string');
    }
    if (typeof report.success !== 'boolean') {
      throw new TypeError('report.success must be a boolean');
    }
    if (typeof report.attempts !== 'number') {
      throw new TypeError('report.attempts must be a number');
    }
    if (typeof report.duration !== 'number') {
      throw new TypeError('report.duration must be a number');
    }
    if (!Array.isArray(report.fixLog)) {
      throw new TypeError('report.fixLog must be an array');
    }

    this.reports.push(report);
  }

  /**
   * Generate HTML report
   * @returns HTML string
   */
  generateHTML(): string {
    const totalTests = this.reports.length;
    const passedTests = this.reports.filter(r => r.success).length;
    const failedTests = totalTests - passedTests;
    const passRate = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(2) : '0.00';
    const totalDuration = this.reports.reduce((sum, r) => sum + r.duration, 0);
    const avgDuration = totalTests > 0 ? (totalDuration / totalTests).toFixed(2) : '0';

    return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>E2E Test Report - HQL V2 Self-Healing</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
      line-height: 1.6;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }

    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px;
      text-align: center;
    }

    .header h1 {
      font-size: 2.5rem;
      margin-bottom: 10px;
      font-weight: 700;
    }

    .header p {
      font-size: 1.1rem;
      opacity: 0.9;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      padding: 40px;
      background: #f8f9fa;
    }

    .summary-card {
      background: white;
      padding: 24px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      text-align: center;
      transition: transform 0.2s;
    }

    .summary-card:hover {
      transform: translateY(-4px);
    }

    .summary-card h3 {
      font-size: 0.9rem;
      color: #6c757d;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .summary-card .value {
      font-size: 2rem;
      font-weight: 700;
      margin-bottom: 4px;
    }

    .summary-card.total .value { color: #667eea; }
    .summary-card.passed .value { color: #28a745; }
    .summary-card.failed .value { color: #dc3545; }
    .summary-card.pass-rate .value { color: #ffc107; }
    .summary-card.duration .value { color: #17a2b8; }

    .test-results {
      padding: 40px;
    }

    .test-results h2 {
      font-size: 1.8rem;
      margin-bottom: 24px;
      color: #333;
    }

    .test-result {
      background: white;
      border: 1px solid #e9ecef;
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 16px;
      transition: all 0.2s;
    }

    .test-result:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .test-result.pass {
      border-left: 4px solid #28a745;
    }

    .test-result.fail {
      border-left: 4px solid #dc3545;
    }

    .test-result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .test-result h3 {
      font-size: 1.2rem;
      color: #333;
    }

    .status-badge {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
    }

    .status-badge.pass {
      background: #d4edda;
      color: #155724;
    }

    .status-badge.fail {
      background: #f8d7da;
      color: #721c24;
    }

    .test-details {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid #e9ecef;
    }

    .detail-item {
      font-size: 0.9rem;
      color: #6c757d;
    }

    .detail-item strong {
      color: #495057;
    }

    .fix-log {
      margin-top: 16px;
      padding: 16px;
      background: #f8f9fa;
      border-radius: 6px;
    }

    .fix-log h4 {
      font-size: 1rem;
      margin-bottom: 12px;
      color: #495057;
    }

    .fix-entry {
      padding: 8px 12px;
      background: white;
      border-radius: 4px;
      margin-bottom: 8px;
      font-size: 0.9rem;
    }

    .fix-entry:last-child {
      margin-bottom: 0;
    }

    .timestamp {
      color: #6c757d;
      font-size: 0.85rem;
    }

    .footer {
      text-align: center;
      padding: 24px;
      background: #f8f9fa;
      color: #6c757d;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🧪 E2E Test Report</h1>
      <p>HQL V2 Self-Healing Test Suite</p>
      <p style="margin-top: 8px; font-size: 0.9rem;">Generated: ${new Date().toISOString()}</p>
    </div>

    <div class="summary">
      <div class="summary-card total">
        <h3>Total Tests</h3>
        <div class="value">${totalTests}</div>
      </div>
      <div class="summary-card passed">
        <h3>Passed</h3>
        <div class="value">${passedTests}</div>
      </div>
      <div class="summary-card failed">
        <h3>Failed</h3>
        <div class="value">${failedTests}</div>
      </div>
      <div class="summary-card pass-rate">
        <h3>Pass Rate</h3>
        <div class="value">${passRate}%</div>
      </div>
      <div class="summary-card duration">
        <h3>Avg Duration</h3>
        <div class="value">${avgDuration}ms</div>
      </div>
    </div>

    <div class="test-results">
      <h2>Test Results</h2>
      ${this.reports.map(report => `
        <div class="test-result ${report.success ? 'pass' : 'fail'}">
          <div class="test-result-header">
            <h3>${report.testName}</h3>
            <span class="status-badge ${report.success ? 'pass' : 'fail'}">
              ${report.success ? 'PASS' : 'FAIL'}
            </span>
          </div>
          <div class="test-details">
            <div class="detail-item"><strong>Attempts:</strong> ${report.attempts}</div>
            <div class="detail-item"><strong>Duration:</strong> ${report.duration}ms</div>
          </div>
          ${report.fixLog && report.fixLog.length > 0 ? `
            <div class="fix-log">
              <h4>🔧 Fix Log (${report.fixLog.length} entries)</h4>
              ${report.fixLog.map(entry => `
                <div class="fix-entry">
                  <div><strong>${entry.fixAction}</strong> - ${entry.errorType}</div>
                  <div class="timestamp">${entry.timestamp}</div>
                </div>
              `).join('')}
            </div>
          ` : ''}
        </div>
      `).join('')}
    </div>

    <div class="footer">
      <p>Generated by TestReporter | E2E Test Suite v1.0.0</p>
    </div>
  </div>
</body>
</html>
    `;
  }

  /**
   * Save report to file (Node.js environment)
   * @param filePath - The file path to save the report
   */
  saveReport(filePath: string): void {
    if (typeof filePath !== 'string') {
      throw new TypeError('filePath must be a string');
    }

    const fs = require('fs');
    const html = this.generateHTML();
    fs.writeFileSync(filePath, html, 'utf-8');
  }

  /**
   * Get summary statistics
   * @returns Summary object
   */
  getSummary(): {
    total: number;
    passed: number;
    failed: number;
    passRate: string;
    totalDuration: number;
    avgDuration: number;
  } {
    const total = this.reports.length;
    const passed = this.reports.filter(r => r.success).length;
    const failed = total - passed;
    const passRate = total > 0 ? ((passed / total) * 100).toFixed(2) : '0.00';
    const totalDuration = this.reports.reduce((sum, r) => sum + r.duration, 0);
    const avgDuration = total > 0 ? totalDuration / total : 0;

    return { total, passed, failed, passRate, totalDuration, avgDuration };
  }

  /**
   * Clear all reports
   */
  clear(): void {
    this.reports = [];
  }
}
