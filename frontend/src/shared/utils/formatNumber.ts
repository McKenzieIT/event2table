export interface FormatNumberOptions {
  locale?: string;
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
  compact?: boolean;
  suffix?: string;
}

export function formatNumber(value: unknown, options: FormatNumberOptions = {}): string {
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  
  const num = Number(value);
  if (isNaN(num)) {
    return String(value);
  }

  const {
    locale = 'zh-CN',
    minimumFractionDigits = 0,
    maximumFractionDigits = 0,
    compact = false,
    suffix = '',
  } = options;

  if (compact) {
    if (num >= 100000000) {
      return (num / 100000000).toFixed(1) + '亿' + suffix;
    }
    if (num >= 10000) {
      return (num / 10000).toFixed(1) + '万' + suffix;
    }
  }

  const formatted = num.toLocaleString(locale, {
    minimumFractionDigits,
    maximumFractionDigits,
  });

  return suffix ? formatted + suffix : formatted;
}

export function formatPercent(value: number, total: number, options: FormatNumberOptions = {}): string {
  if (!total || total === 0) {
    return '0%';
  }
  
  const percent = (value / total) * 100;
  return formatNumber(percent, { maximumFractionDigits: 1 }) + '%';
}

export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
}
