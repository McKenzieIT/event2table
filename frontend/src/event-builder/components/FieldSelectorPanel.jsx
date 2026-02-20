/**
 * FieldSelectorPanel Component
 * 基础字段选择面板 - 从底部向上弹出
 */
import React, { useCallback, useMemo } from "react";
import PropTypes from "prop-types";
import "./FieldSelectorPanel.css";

export default function FieldSelectorPanel({
  isVisible,
  canvasFields = [],
  onAddField,
  onClose,
}) {
  // Base field definitions
  const baseFields = useMemo(
    () => [
      {
        fieldName: "ds",
        displayName: "分区",
        dataType: "STRING",
        icon: "bi-calendar3",
      },
      {
        fieldName: "role_id",
        displayName: "角色ID",
        dataType: "BIGINT",
        icon: "bi-person",
      },
      {
        fieldName: "account_id",
        displayName: "账号ID",
        dataType: "BIGINT",
        icon: "bi-person-badge",
      },
      {
        fieldName: "tm",
        displayName: "上报时间",
        dataType: "STRING",
        icon: "bi-clock",
      },
      {
        fieldName: "utdid",
        displayName: "设备ID",
        dataType: "STRING",
        icon: "bi-phone",
      },
      {
        fieldName: "ts",
        displayName: "上报时间戳",
        dataType: "BIGINT",
        icon: "bi-stopwatch",
      },
      {
        fieldName: "envinfo",
        displayName: "环境信息",
        dataType: "STRING",
        icon: "bi-info-circle",
      },
    ],
    [],
  );

  // Check if field is already added
  const isFieldAdded = useCallback(
    (fieldName) => {
      return canvasFields.some(
        (f) => f.fieldType === "base" && f.fieldName === fieldName,
      );
    },
    [canvasFields],
  );

  // Handle field selection
  const handleFieldClick = useCallback(
    (field) => {
      if (!isFieldAdded(field.fieldName)) {
        onAddField({
          fieldType: "base",
          fieldName: field.fieldName,
          displayName: field.displayName,
          dataType: field.dataType,
        });
      }
    },
    [isFieldAdded, onAddField],
  );

  if (!isVisible) return null;

  return (
    <div className="field-selector-overlay" onClick={onClose}>
      <div
        className="field-selector-panel"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="selector-header">
          <h3>
            <i className="bi bi-list-check"></i>
            选择基础字段
          </h3>
          <button
            className="btn-close-selector"
            onClick={onClose}
            title="关闭"
            type="button"
          >
            <i className="bi bi-x"></i>
          </button>
        </div>

        {/* Field Grid */}
        <div className="field-grid">
          {baseFields.map((field) => {
            const added = isFieldAdded(field.fieldName);

            return (
              <button
                key={field.fieldName}
                className={`field-card ${added ? "added" : ""}`}
                onClick={() => handleFieldClick(field)}
                disabled={added}
                type="button"
              >
                <div className="field-icon">
                  <i className={`bi ${field.icon}`}></i>
                </div>
                <div className="field-info">
                  <span className="field-name">{field.displayName}</span>
                  <span className="field-meta">
                    {field.fieldName} · {field.dataType}
                  </span>
                </div>
                {added && (
                  <div className="field-status">
                    <i className="bi bi-check-circle-fill"></i>
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Footer Hint */}
        <div className="selector-footer">
          <span className="footer-hint">
            <i className="bi bi-info-circle"></i>
            点击字段添加到画布，已添加字段不可重复
          </span>
        </div>
      </div>
    </div>
  );
}

FieldSelectorPanel.propTypes = {
  isVisible: PropTypes.bool.isRequired,
  canvasFields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      fieldType: PropTypes.string.isRequired,
      fieldName: PropTypes.string,
      name: PropTypes.string.isRequired,
      displayName: PropTypes.string,
      alias: PropTypes.string,
      dataType: PropTypes.string.isRequired,
    }),
  ),
  onAddField: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};
