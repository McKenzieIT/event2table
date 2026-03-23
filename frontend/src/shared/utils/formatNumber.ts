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
    compact = false,
    suffix = '',
  } = options;

  // Ensure maximumFractionDigits >= minimumFractionDigits to avoid RangeError
  const maxFrac = options.maximumFractionDigits ?? Math.max(minimumFractionDigits, 0);
  const maximumFractionDigits = Math.max(maxFrac, minimumFractionDigits);

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
  // Merge provided options with default maximumFractionDigits: 1
  const mergedOptions: FormatNumberOptions = {
    maximumFractionDigits: 1,
    ...options,
  };
  return formatNumber(percent, mergedOptions) + '%';
}

export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';
  
  // Handle fractional bytes (0 < bytes < 1)
  if (bytes > 0 && bytes < 1) {
    return bytes.toFixed(decimals) + ' Bytes';
  }
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  // Format with thousand separators for Bytes, or use toFixed for larger units
  if (i === 0) {
    // For bytes, use toLocaleString for thousand separators
    return bytes.toLocaleString('zh-CN') + ' Bytes';
  }
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
}
