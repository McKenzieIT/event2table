import { useCallback, useEffect } from "react";

interface KeyboardShortcutsOptions {
  onDelete?: () => void;
  onClear?: () => void;
  onSave?: () => void;
  onGenerate?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
}

export function useKeyboardShortcuts({
  onDelete,
  onClear,
  onSave,
  onGenerate,
  onUndo,
  onRedo,
}: KeyboardShortcutsOptions) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        (event.target instanceof HTMLElement && event.target.isContentEditable)
      ) {
        return;
      }

      if (event.key === "Delete" || event.key === "Backspace") {
        event.preventDefault();
        onDelete?.();
      }

      if ((event.ctrlKey || event.metaKey) && event.key === "s") {
        event.preventDefault();
        onSave?.();
      }

      if ((event.ctrlKey || event.metaKey) && event.key === "g") {
        event.preventDefault();
        onGenerate?.();
      }

      if ((event.ctrlKey || event.metaKey) && event.key === "d") {
        event.preventDefault();
        onClear?.();
      }

      if ((event.ctrlKey || event.metaKey) && !event.shiftKey && event.key === "z") {
        event.preventDefault();
        onUndo?.();
      }

      if (
        ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === "z") ||
        ((event.ctrlKey || event.metaKey) && event.key === "y")
      ) {
        event.preventDefault();
        onRedo?.();
      }
    },
    [onDelete, onClear, onSave, onGenerate, onUndo, onRedo],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);
}
