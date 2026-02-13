import { TestReporter } from '../TestReporter';

describe('TestReporter', () => {
  test('generate HTML report', () => {
  const reporter = new TestReporter();

  reporter.addReport({
    testName: 'T01: Test 1',
    success: true,
    attempts: 1,
    fixLog: [],
    duration: 1234
  });

  reporter.addReport({
    testName: 'T02: Test 2',
    success: false,
    attempts: 3,
    fixLog: [
      {
        timestamp: '2026-02-08T10:00:00Z',
        testName: 'T02',
        errorType: 'API_NOT_FOUND',
        fixAction: 'cache_cleared',
        success: true,
        duration: 1000
      }
    ],
    duration: 5678
  });

  const html = reporter.generateHTML();

  expect(html).toContain('E2E Test Report');
  expect(html).toContain('T01: Test 1');
  expect(html).toContain('T02: Test 2');
  expect(html).toContain('Total Tests');
  expect(html).toContain('2'); // Total tests
  expect(html).toContain('50.00%'); // Pass rate
});

  test('getSummary', () => {
  const reporter = new TestReporter();

  reporter.addReport({
    testName: 'T01',
    success: true,
    attempts: 1,
    fixLog: [],
    duration: 1000
  });

  const summary = reporter.getSummary();

  expect(summary.total).toBe(1);
  expect(summary.passed).toBe(1);
  expect(summary.failed).toBe(0);
  expect(summary.passRate).toBe('100.00');
  expect(summary.totalDuration).toBe(1000);
  expect(summary.avgDuration).toBe(1000);
});

  test('input validation', () => {
  const reporter = new TestReporter();

  // Test null report
  expect(() => {
    // @ts-ignore - testing null input
    reporter.addReport(null);
  }).toThrow(TypeError);

  // Test empty object
  expect(() => {
    // @ts-ignore - testing empty object
    reporter.addReport({});
  }).toThrow(TypeError);

  // Test invalid testName
  expect(() => {
    // @ts-ignore - testing invalid type
    reporter.addReport({
      testName: 123,
      success: true,
      attempts: 1,
      fixLog: [],
      duration: 1000
    });
  }).toThrow(TypeError);

  // Test invalid success
  expect(() => {
    // @ts-ignore - testing invalid type
    reporter.addReport({
      testName: 'Test',
      success: 'true',
      attempts: 1,
      fixLog: [],
      duration: 1000
    });
  }).toThrow(TypeError);

  // Test invalid attempts
  expect(() => {
    // @ts-ignore - testing invalid type
    reporter.addReport({
      testName: 'Test',
      success: true,
      attempts: '1',
      fixLog: [],
      duration: 1000
    });
  }).toThrow(TypeError);

  // Test invalid duration
  expect(() => {
    // @ts-ignore - testing invalid type
    reporter.addReport({
      testName: 'Test',
      success: true,
      attempts: 1,
      fixLog: [],
      duration: '1000'
    });
  }).toThrow(TypeError);

  // Test invalid fixLog
  expect(() => {
    // @ts-ignore - testing invalid type
    reporter.addReport({
      testName: 'Test',
      success: true,
      attempts: 1,
      fixLog: 'invalid',
      duration: 1000
    });
  }).toThrow(TypeError);
});

  test('clear reports', () => {
  const reporter = new TestReporter();

  reporter.addReport({
    testName: 'T01',
    success: true,
    attempts: 1,
    fixLog: [],
    duration: 1000
  });

  expect(reporter.getSummary().total).toBe(1);

  reporter.clear();

  expect(reporter.getSummary().total).toBe(0);
});

  test('HTML structure validation', () => {
  const reporter = new TestReporter();

  reporter.addReport({
    testName: 'T01: Success Test',
    success: true,
    attempts: 1,
    fixLog: [],
    duration: 1234
  });

  reporter.addReport({
    testName: 'T02: Failed Test',
    success: false,
    attempts: 2,
    fixLog: [
      {
        timestamp: '2026-02-08T10:00:00Z',
        testName: 'T02',
        errorType: 'TIMEOUT',
        fixAction: 'retry_with_backoff',
        success: true,
        duration: 500
      }
    ],
    duration: 2345
  });

  const html = reporter.generateHTML();

  // Check HTML structure
  expect(html).toContain('<!DOCTYPE html>');
  expect(html).toContain('<html lang="zh-CN">');
  expect(html).toContain('<head>');
  expect(html).toContain('<body>');
  expect(html).toContain('class="container"');
  expect(html).toContain('class="header"');
  expect(html).toContain('class="summary"');
  expect(html).toContain('class="test-results"');

  // Check test result styling
  expect(html).toContain('test-result pass');
  expect(html).toContain('test-result fail');
  expect(html).toContain('status-badge pass');
  expect(html).toContain('status-badge fail');

  // Check fix log display
  expect(html).toContain('Fix Log');
  expect(html).toContain('retry_with_backoff');
  expect(html).toContain('TIMEOUT');
});

  test('empty report', () => {
  const reporter = new TestReporter();

  const html = reporter.generateHTML();
  const summary = reporter.getSummary();

  expect(summary.total).toBe(0);
  expect(summary.passed).toBe(0);
  expect(summary.failed).toBe(0);
  expect(summary.passRate).toBe('0.00');
  expect(html).toContain('Total Tests');
  expect(html).toContain('0'); // No tests
});
});


  test('multiple fix logs', () => {
  const reporter = new TestReporter();

  reporter.addReport({
    testName: 'T01: Multi-fix Test',
    success: true,
    attempts: 3,
    fixLog: [
      {
        timestamp: '2026-02-08T10:00:00Z',
        testName: 'T01',
        errorType: 'API_NOT_FOUND',
        fixAction: 'cache_cleared',
        success: true,
        duration: 100
      },
      {
        timestamp: '2026-02-08T10:01:00Z',
        testName: 'T01',
        errorType: 'TIMEOUT',
        fixAction: 'retry_with_backoff',
        success: true,
        duration: 200
      },
      {
        timestamp: '2026-02-08T10:02:00Z',
        testName: 'T01',
        errorType: 'SELECTOR_NOT_FOUND',
        fixAction: 'wait_for_selector',
        success: true,
        duration: 300
      }
    ],
    duration: 3000
  });

  const html = reporter.generateHTML();

  expect(html).toContain('Fix Log (3 entries)');
  expect(html).toContain('cache_cleared');
  expect(html).toContain('retry_with_backoff');
  expect(html).toContain('wait_for_selector');
});
