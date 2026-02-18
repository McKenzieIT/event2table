import { useEffect, useCallback } from 'react';

interface HotkeyConfig {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  handler: (event: KeyboardEvent) => void;
  description?: string;
}

interface UseHotkeyOptions {
  enabled?: boolean;
  preventDefault?: boolean;
}

export function useHotkey(
  hotkeys: HotkeyConfig[],
  options: UseHotkeyOptions = {}
) {
  const { enabled = true, preventDefault = true } = options;

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    const target = event.target as HTMLElement;
    const isInput = target.tagName === 'INPUT' || 
                   target.tagName === 'TEXTAREA' || 
                   target.isContentEditable;

    for (const hotkey of hotkeys) {
      const keyMatch = event.key.toLowerCase() === hotkey.key.toLowerCase() ||
                      event.code.toLowerCase() === hotkey.key.toLowerCase();
      const ctrlMatch = !!hotkey.ctrl === (event.ctrlKey || event.metaKey);
      const shiftMatch = !!hotkey.shift === event.shiftKey;
      const altMatch = !!hotkey.alt === event.altKey;

      if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
        if (preventDefault) {
          event.preventDefault();
        }

        if (!isInput || hotkey.key === 'Escape') {
          hotkey.handler(event);
          break;
        }
      }
    }
  }, [hotkeys, enabled, preventDefault]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}

export function useGlobalShortcuts() {
  useHotkey([
    { key: 's', ctrl: true, handler: () => {}, description: 'Save (Ctrl+S)' },
    { key: 'n', ctrl: true, handler: () => {}, description: 'New (Ctrl+N)' },
    { key: 'f', ctrl: true, handler: () => {}, description: 'Find (Ctrl+F)' },
    { key: 'Escape', handler: () => {}, description: 'Close modal (Esc)' },
    { key: 'ArrowLeft', handler: () => {}, description: 'Previous (←)' },
    { key: 'ArrowRight', handler: () => {}, description: 'Next (→)' },
    { key: 'ArrowUp', handler: () => {}, description: 'Up (↑)' },
    { key: 'ArrowDown', handler: () => {}, description: 'Down (↓)' },
  ], { enabled: false });
}

export default useHotkey;
