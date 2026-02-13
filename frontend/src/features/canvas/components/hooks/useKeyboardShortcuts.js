import React, { useCallback, useEffect } from "react";
import { useReactFlow } from "reactflow";

/**
 * 键盘快捷键Hook
 */
export function useKeyboardShortcuts({
  onDelete,
  onClear,
  onSave,
  onGenerate,
  onUndo,
  onRedo,
}) {
  const { getNodes } = useReactFlow();

  const handleKeyDown = useCallback(
    (event) => {
      // 忽略输入框中的快捷键
      if (
        event.target.tagName === "INPUT" ||
        event.target.tagName === "TEXTAREA" ||
        event.target.isContentEditable
      ) {
        return;
      }

      // Delete/Backspace: 删除选中节点
      if (event.key === "Delete" || event.key === "Backspace") {
        event.preventDefault();
        onDelete?.();
      }

      // Ctrl/Cmd + S: 保存
      if ((event.ctrlKey || event.metaKey) && event.key === "s") {
        event.preventDefault();
        onSave?.();
      }

      // Ctrl/Cmd + G: 生成HQL
      if ((event.ctrlKey || event.metaKey) && event.key === "g") {
        event.preventDefault();
        onGenerate?.();
      }

      // Ctrl/Cmd + D: 清空画布
      if ((event.ctrlKey || event.metaKey) && event.key === "d") {
        event.preventDefault();
        onClear?.();
      }

      // Ctrl/Cmd + Z: 撤销
      if ((event.ctrlKey || event.metaKey) && !event.shiftKey && event.key === "z") {
        event.preventDefault();
        onUndo?.();
      }

      // Ctrl/Cmd + Shift + Z 或 Ctrl/Cmd + Y: 重做
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
