/**
 * QuickFieldTools Component
 * 快速字段工具 - 批量添加基础字段（仅显示批操作按钮）
 */
import React from "react";
import PropTypes from "prop-types";

export default function QuickFieldTools({ onQuickAdd }) {
  return (
    <div className="quick-field-tools">
      <div className="quick-tools-batch">
        <button
          className="quick-tool-batch-btn"
          onClick={() => onQuickAdd("common")}
          title="添加常用字段（ds, role_id, account_id, tm）"
          type="button"
        >
          <i className="bi bi-bolt"></i>
          <span>常用</span>
        </button>
        <button
          className="quick-tool-batch-btn"
          onClick={() => onQuickAdd("all")}
          title="添加所有基础字段"
          type="button"
        >
          <i className="bi bi-list-check"></i>
          <span>全部</span>
        </button>
      </div>
    </div>
  );
}

QuickFieldTools.propTypes = {
  onQuickAdd: PropTypes.func.isRequired,
};
