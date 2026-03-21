/**
 * Date formatting utilities
 */

/**
 * Format date to string
 */
export function formatDate(date: Date | null, format: string = 'YYYY-MM-DD'): string {
  if (!date) return '';
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes);
}

/**
 * Parse date string to Date object
 */
export function parseDate(dateString: string, format: string = 'YYYY-MM-DD'): Date | null {
  if (!dateString) return null;
  
  try {
    // Simple parsing for YYYY-MM-DD format
    const parts = dateString.split('-');
    if (parts.length === 3) {
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1;
      const day = parseInt(parts[2], 10);
      return new Date(year, month, day);
    }
    return new Date(dateString);
  } catch {
    return null;
  }
}

/**
 * Get number of days in month
 */
export function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month + 1, 0).getDate();
}

/**
 * Get first day of month
 */
export function getFirstDayOfMonth(year: number, month: number, firstDayOfWeek: number = 0): number {
  const day = new Date(year, month, 1).getDay();
  return (day - firstDayOfWeek + 7) % 7;
}

/**
 * Check if two dates are the same day
 */
export function isSameDay(date1: Date, date2: Date): boolean {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
}

/**
 * Check if date is in range
 */
export function isDateInRange(date: Date, minDate?: Date, maxDate?: Date): boolean {
  if (minDate && date < minDate) return false;
  if (maxDate && date > maxDate) return false;
  return true;
}
