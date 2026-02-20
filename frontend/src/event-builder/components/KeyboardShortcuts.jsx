/**
 * KeyboardShortcuts Component
 * 键盘快捷键系统 - 全局键盘事件监听和快捷键触发
 */
import React, { useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import './KeyboardShortcuts.css';

/**
 * 键盘快捷键映射
 */
const SHORTCUTS = {
  ADD_BASE_FIELD: 'b',
  ADD_CUSTOM_FIELD: 'c',
  ADD_FIXED_FIELD: 'f',
  QUICK_ADD_COMMON: 'q',
  QUICK_ADD_ALL: 'a',
  DELETE_FIELD: ['delete', 'backspace'],
  CLOSE_MODAL: 'escape',
  SAVE: 's',
  OPEN_WHERE: 'w',
  OPEN_HQL: 'h',
};

/**
 * 快捷键帮助信息
 */
const SHORTCUT_HELP = [
  { key: 'B', description: '添加基础字段', icon: 'bi-type' },
  { key: 'C', description: '添加自定义字段', icon: 'bi-code' },
  { key: 'F', description: '添加固定值', icon: 'bi-pin' },
  { key: 'Q', description: '快速添加常用字段', icon: 'bi-bolt' },
  { key: 'A', description: '添加所有基础字段', icon: 'bi-list-check' },
  { key: 'Del', description: '删除选中字段', icon: 'bi-trash' },
  { key: 'Esc', description: '关闭对话框', icon: 'bi-x-circle' },
  { key: 'W', description: '打开WHERE条件', icon: 'bi-funnel' },
  { key: 'H', description: '打开HQL预览', icon: 'bi-code-square' },
];

export default function KeyboardShortcuts({
  onAddBaseField,
  onAddCustomField,
  onAddFixedField,
  onQuickAddCommon,
  onQuickAddAll,
  onDeleteField,
  onCloseModal,
  onSave,
  onOpenWhere,
  onOpenHQL,
  onShowHelp,
  disabled = false,
  children,
}) {
  /**
   * 处理键盘事件
   */
  const handleKeyDown = useCallback((event) => {
    // 如果快捷键功能被禁用，不处理
    if (disabled) return;

    // 如果在输入框中，不处理快捷键（除了Escape）
    const target = event.target;
    const isInput = target.tagName === 'INPUT' ||
                     target.tagName === 'TEXTAREA' ||
                     target.contentEditable === 'true';

    if (isInput && event.key !== 'Escape') return;

    // 获取按键
    const key = event.key.toLowerCase();

    // 检查是否有修饰键（Ctrl/Cmd/Shift/Alt）
    const hasModifier = event.ctrlKey || event.metaKey || event.shiftKey || event.altKey;

    // 如果有修饰键，不处理（避免与浏览器快捷键冲突）
    if (hasModifier && key !== 's') return; // Ctrl+S 是保存快捷键

    // 处理各个快捷键
    switch (key) {
      case SHORTCUTS.ADD_BASE_FIELD:
        event.preventDefault();
        onAddBaseField?.();
        break;

      case SHORTCUTS.ADD_CUSTOM_FIELD:
        event.preventDefault();
        onAddCustomField?.();
        break;

      case SHORTCUTS.ADD_FIXED_FIELD:
        event.preventDefault();
        onAddFixedField?.();
        break;

      case SHORTCUTS.QUICK_ADD_COMMON:
        event.preventDefault();
        onQuickAddCommon?.();
        break;

      case SHORTCUTS.QUICK_ADD_ALL:
        event.preventDefault();
        onQuickAddAll?.();
        break;

      case 'delete':
      case 'backspace':
        if (!isInput) {
          event.preventDefault();
          onDeleteField?.();
        }
        break;

      case SHORTCUTS.CLOSE_MODAL:
        event.preventDefault();
        onCloseModal?.();
        break;

      case 's':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          onSave?.();
        }
        break;

      case SHORTCUTS.OPEN_WHERE:
        event.preventDefault();
        onOpenWhere?.();
        break;

      case SHORTCUTS.OPEN_HQL:
        event.preventDefault();
        onOpenHQL?.();
        break;

      case '?':
        event.preventDefault();
        onShowHelp?.();
        break;

      default:
        // 不处理其他按键
        break;
    }
  }, [
    disabled,
    onAddBaseField,
    onAddCustomField,
    onAddFixedField,
    onQuickAddCommon,
    onQuickAddAll,
    onDeleteField,
    onCloseModal,
    onSave,
    onOpenWhere,
    onOpenHQL,
    onShowHelp,
  ]);

  /**
   * 注册全局键盘事件监听器
   */
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  // 渲染子组件（快捷键系统不渲染任何UI）
  return children;
}

KeyboardShortcuts.propTypes = {
  onAddBaseField: PropTypes.func,
  onAddCustomField: PropTypes.func,
  onAddFixedField: PropTypes.func,
  onQuickAddCommon: PropTypes.func,
  onQuickAddAll: PropTypes.func,
  onDeleteField: PropTypes.func,
  onCloseModal: PropTypes.func,
  onSave: PropTypes.func,
  onOpenWhere: PropTypes.func,
  onOpenHQL: PropTypes.func,
  onShowHelp: PropTypes.func,
  disabled: PropTypes.bool,
  children: PropTypes.node,
};

/**
 * 快捷键帮助面板组件
 */
export function KeyboardShortcutsHelp({ onClose }) {
  return (
    <div className="keyboard-shortcuts-help-overlay" onClick={onClose}>
      <div className="keyboard-shortcuts-help" onClick={(e) => e.stopPropagation()}>
        <div className="help-header">
          <h2>
            <i className="bi bi-keyboard"></i>
            键盘快捷键
          </h2>
          <button className="btn-close-help" onClick={onClose}>
            <i className="bi bi-x"></i>
          </button>
        </div>

        <div className="help-content">
          <div className="help-section">
            <h3>添加字段</h3>
            <div className="help-items">
              {SHORTCUT_HELP.slice(0, 5).map((item) => (
                <div key={item.key} className="help-item">
                  <kbd className="help-key">
                    <i className={`bi ${item.icon}`}></i>
                    {item.key}
                  </kbd>
                  <span className="help-description">{item.description}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="help-section">
            <h3>编辑操作</h3>
            <div className="help-items">
              {SHORTCUT_HELP.slice(5).map((item) => (
                <div key={item.key} className="help-item">
                  <kbd className="help-key">
                    <i className={`bi ${item.icon}`}></i>
                    {item.key}
                  </kbd>
                  <span className="help-description">{item.description}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="help-section">
            <h3>系统操作</h3>
            <div className="help-items">
              <div className="help-item">
                <kbd className="help-key">
                  <i className="bi bi-save"></i>
                  Ctrl+S
                </kbd>
                <span className="help-description">保存配置</span>
              </div>
              <div className="help-item">
                <kbd className="help-key">
                  <i className="bi bi-question-circle"></i>
                  ?
                </kbd>
                <span className="help-description">显示帮助</span>
              </div>
            </div>
          </div>
        </div>

        <div className="help-footer">
          <button className="btn-help-close" onClick={onClose}>
            我知道了
          </button>
        </div>
      </div>
    </div>
  );
}

KeyboardShortcutsHelp.propTypes = {
  onClose: PropTypes.func.isRequired,
};

export { SHORTCUTS, SHORTCUT_HELP };
