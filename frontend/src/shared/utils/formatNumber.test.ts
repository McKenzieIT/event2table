// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * Format Number Utilities Tests
 * 测试数字格式化工具函数的所有功能
 */

import { describe, it, expect } from 'vitest';

import {
  formatNumber,
  formatPercent,
  formatBytes,
  type FormatNumberOptions,
} from './formatNumber';

describe('formatNumber', () => {
  describe('with null/undefined/empty values', () => {
    it('should return "-" for null', () => {
      expect(formatNumber(null)).toBe('-');
    });

    it('should return "-" for undefined', () => {
      expect(formatNumber(undefined)).toBe('-');
    });

    it('should return "-" for empty string', () => {
      expect(formatNumber('')).toBe('-');
    });
  });

  describe('with numeric values', () => {
    it('should format integer with default locale', () => {
      expect(formatNumber(1234)).toBe('1,234');
    });

    it('should format large number', () => {
      expect(formatNumber(1234567)).toBe('1,234,567');
    });

    it('should format decimal with default options', () => {
      expect(formatNumber(1234.56)).toBe('1,235'); // Rounds due to maximumFractionDigits: 0
    });

    it('should format zero', () => {
      expect(formatNumber(0)).toBe('0');
    });

    it('should format negative number', () => {
      expect(formatNumber(-1234)).toBe('-1,234');
    });
  });

  describe('with string numeric values', () => {
    it('should parse and format string number', () => {
      expect(formatNumber('1234')).toBe('1,234');
    });

    it('should parse and format decimal string', () => {
      expect(formatNumber('1234.56')).toBe('1,235'); // Rounds due to maximumFractionDigits: 0
    });

    it('should handle string with spaces', () => {
      expect(formatNumber(' 1234 ')).toBe('1,234');
    });
  });

  describe('with non-numeric values', () => {
    it('should return original string for non-numeric', () => {
      expect(formatNumber('abc')).toBe('abc');
    });

    it('should return original string for mixed alphanumeric', () => {
      expect(formatNumber('123abc')).toBe('123abc');
    });
  });

  describe('with custom options', () => {
    it('should respect minimumFractionDigits', () => {
      const options: FormatNumberOptions = { minimumFractionDigits: 2 };
      expect(formatNumber(1234, options)).toBe('1,234.00');
    });

    it('should respect maximumFractionDigits', () => {
      const options: FormatNumberOptions = { maximumFractionDigits: 2 };
      expect(formatNumber(1234.5678, options)).toBe('1,234.57');
    });

    it('should respect both min and max fraction digits', () => {
      const options: FormatNumberOptions = {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      };
      expect(formatNumber(1234, options)).toBe('1,234.00');
      expect(formatNumber(1234.567, options)).toBe('1,234.57');
    });

    it('should add suffix', () => {
      const options: FormatNumberOptions = { suffix: ' 元' };
      expect(formatNumber(1234, options)).toBe('1,234 元');
    });

    it('should use custom locale', () => {
      const options: FormatNumberOptions = { locale: 'en-US', maximumFractionDigits: 2 };
      expect(formatNumber(1234.56, options)).toBe('1,234.56');
    });
  });

  describe('compact format', () => {
    it('should format numbers in thousands as 万', () => {
      const options: FormatNumberOptions = { compact: true };
      expect(formatNumber(10000, options)).toBe('1.0万');
      expect(formatNumber(50000, options)).toBe('5.0万');
    });

    it('should format numbers in hundred millions as 亿', () => {
      const options: FormatNumberOptions = { compact: true };
      expect(formatNumber(100000000, options)).toBe('1.0亿');
      expect(formatNumber(500000000, options)).toBe('5.0亿');
    });

    it('should not format small numbers in compact mode', () => {
      const options: FormatNumberOptions = { compact: true };
      expect(formatNumber(9999, options)).toBe('9,999');
    });

    it('should combine compact with suffix', () => {
      const options: FormatNumberOptions = { compact: true, suffix: ' 次' };
      expect(formatNumber(15000, options)).toBe('1.5万 次');
    });

    it('should handle boundary values', () => {
      const options: FormatNumberOptions = { compact: true };
      expect(formatNumber(9999, options)).toBe('9,999');
      expect(formatNumber(10000, options)).toBe('1.0万');
      // 99999999 / 10000 = 9999.9999, toFixed(1) = 10000.0
      expect(formatNumber(99999999, options)).toBe('10000.0万');
      expect(formatNumber(100000000, options)).toBe('1.0亿');
    });
  });

  describe('edge cases', () => {
    it('should handle very large numbers', () => {
      expect(formatNumber(999999999999)).toBe('999,999,999,999');
    });

    it('should handle very small decimals', () => {
      const options: FormatNumberOptions = { maximumFractionDigits: 6 };
      // 0.000001 has 6 decimal places, should display as is
      expect(formatNumber(0.000001, options)).toBe('0.000001');
    });

    it('should handle NaN from string', () => {
      expect(formatNumber('not a number')).toBe('not a number');
    });
  });
});

describe('formatPercent', () => {
  describe('with valid values', () => {
    it('should calculate percentage', () => {
      expect(formatPercent(50, 100)).toBe('50%');
    });

    it('should calculate percentage with decimals', () => {
      expect(formatPercent(33.33, 100)).toBe('33.3%');
    });

    it('should calculate 0%', () => {
      expect(formatPercent(0, 100)).toBe('0%');
    });

    it('should calculate 100%', () => {
      expect(formatPercent(100, 100)).toBe('100%');
    });

    it('should calculate >100%', () => {
      expect(formatPercent(150, 100)).toBe('150%');
    });

    it('should calculate <1%', () => {
      expect(formatPercent(0.5, 100)).toBe('0.5%');
    });
  });

  describe('with edge cases', () => {
    it('should return 0% when total is 0', () => {
      expect(formatPercent(50, 0)).toBe('0%');
    });

    it('should return 0% when total is null/undefined', () => {
      expect(formatPercent(50, null as any)).toBe('0%');
      expect(formatPercent(50, undefined as any)).toBe('0%');
    });

    it('should handle value of 0', () => {
      expect(formatPercent(0, 100)).toBe('0%');
    });

    it('should format large percentages', () => {
      expect(formatPercent(12345.67, 100)).toBe('12,345.7%');
    });
  });

  describe('with custom options', () => {
    it('should respect minimumFractionDigits', () => {
      const options: FormatNumberOptions = { minimumFractionDigits: 2 };
      expect(formatPercent(50, 100, options)).toBe('50.00%');
    });

    it('should respect maximumFractionDigits', () => {
      const options: FormatNumberOptions = { maximumFractionDigits: 0 };
      expect(formatPercent(33.33, 100, options)).toBe('33%');
    });
  });
});

describe('formatBytes', () => {
  describe('with zero', () => {
    it('should return "0 Bytes"', () => {
      expect(formatBytes(0)).toBe('0 Bytes');
    });
  });

  describe('with bytes', () => {
    it('should format bytes', () => {
      expect(formatBytes(512)).toBe('512 Bytes');
      expect(formatBytes(1023)).toBe('1,023 Bytes');
    });
  });

  describe('with kilobytes', () => {
    it('should format KB', () => {
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1536)).toBe('1.5 KB');
      expect(formatBytes(10240)).toBe('10 KB');
    });
  });

  describe('with megabytes', () => {
    it('should format MB', () => {
      expect(formatBytes(1048576)).toBe('1 MB');
      expect(formatBytes(1572864)).toBe('1.5 MB');
      expect(formatBytes(10485760)).toBe('10 MB');
    });
  });

  describe('with gigabytes', () => {
    it('should format GB', () => {
      expect(formatBytes(1073741824)).toBe('1 GB');
      expect(formatBytes(1610612736)).toBe('1.5 GB');
      expect(formatBytes(10737418240)).toBe('10 GB');
    });
  });

  describe('with terabytes', () => {
    it('should format TB', () => {
      expect(formatBytes(1099511627776)).toBe('1 TB');
      expect(formatBytes(1649267441664)).toBe('1.5 TB');
    });
  });

  describe('with custom decimals', () => {
    it('should respect decimals parameter', () => {
      expect(formatBytes(1536, 0)).toBe('2 KB');
      expect(formatBytes(1536, 1)).toBe('1.5 KB');
      expect(formatBytes(1536, 2)).toBe('1.5 KB');
      expect(formatBytes(1536, 3)).toBe('1.5 KB');
    });

    it('should handle different decimal values', () => {
      expect(formatBytes(1234567, 0)).toBe('1 MB');
      expect(formatBytes(1234567, 2)).toBe('1.18 MB');
      expect(formatBytes(1234567, 4)).toBe('1.1774 MB');
    });
  });

  describe('edge cases', () => {
    it('should handle very large numbers', () => {
      expect(formatBytes(12345678901234)).toBe('11.23 TB');
    });

    it('should handle fractional values', () => {
      // formatBytes uses toFixed(2) by default, so 0.5 becomes "0.50 Bytes"
      expect(formatBytes(0.5)).toBe('0.50 Bytes');
    });
  });
});

describe('Integration Tests', () => {
  it('should format various number scenarios consistently', () => {
    // Compact format for large numbers
    expect(formatNumber(123456789, { compact: true })).toBe('1.2亿');

    // Regular format for smaller numbers
    expect(formatNumber(1234.567, { maximumFractionDigits: 2 })).toBe('1,234.57');

    // Percentage calculation: 1234567 / 10000000 * 100 = 12.34567%
    expect(formatPercent(1234567, 10000000)).toBe('12.3%');
  });

  it('should handle formatting in data display context', () => {
    const userCount = 15234;
    const totalUsers = 20000;
    const percentage = formatPercent(userCount, totalUsers);
    const compactCount = formatNumber(userCount, { compact: true });

    // 15234 / 20000 * 100 = 76.17%, rounds to 76.2%
    expect(percentage).toBe('76.2%');
    expect(compactCount).toBe('1.5万');
  });

  it('should format file sizes correctly', () => {
    const fileSize = 1572864; // 1.5 MB
    expect(formatBytes(fileSize)).toBe('1.5 MB');

    const largeFileSize = 10737418240; // 10 GB
    expect(formatBytes(largeFileSize)).toBe('10 GB');
  });

  it('should handle edge case combinations', () => {
    // Very small percentage: 1 / 1000000 * 100 = 0.0001%, rounds to 0%
    expect(formatPercent(1, 1000000)).toBe('0%');

    // Very large compact number: 999999999999 / 100000000 = 9999.9999999, toFixed(1) = 10000.0
    expect(formatNumber(999999999999, { compact: true })).toBe('10000.0亿');

    // File size with custom decimals
    expect(formatBytes(1234567, 1)).toBe('1.2 MB');
  });
});
