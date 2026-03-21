/**
 * Toast notification types
 */
export type ToastType = 'info' | 'success' | 'error' | 'warning';

/**
 * Show toast notification
 * @param message - The message to display
 * @param type - The type of toast
 * @param duration - Duration in milliseconds
 */
export function showToastNotification(
  message: string,
  type: ToastType = 'info',
  duration: number = 3000
): void {
  // Create toast element
  const toast = document.createElement('div');
  toast.className = `hql-toast hql-toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  // Trigger animation
  setTimeout(() => toast.classList.add('hql-toast-show'), 10);

  // Auto remove
  setTimeout(() => {
    toast.classList.remove('hql-toast-show');
    setTimeout(() => document.body.removeChild(toast), 300);
  }, duration);
}

/**
 * Copy text to clipboard
 * @param text - Text to copy
 * @returns Promise that resolves when copied
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback method
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return success;
    } catch (e) {
      document.body.removeChild(textarea);
      return false;
    }
  }
}

/**
 * Download text as file
 * @param text - Text content
 * @param filename - File name
 */
export function downloadAsFile(text: string, filename: string): void {
  try {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Download failed:', err);
  }
}
