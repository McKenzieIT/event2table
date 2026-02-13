/**
 * HQLPreviewModal Component
 * HQL预览全屏模态框（支持编辑和多模式切换）
 */
import React, { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './HQLPreviewModal.css';
import { BaseModal } from '@shared/ui/BaseModal';
import PerformanceIndicator from '../HQLPreviewV2/PerformanceIndicator';
import DebugViewer from '../HQLPreviewV2/DebugViewer';

export default function HQLPreviewModal({
  isOpen,
  onClose,
  canvasFields,
  whereConditions,
  gameData,
  selectedEvent,
  useV2API = false
}) {
  const [activeTab, setActiveTab] = useState('SELECT');
  const [isEditing, setIsEditing] = useState(false);
  const [hqlOutputs, setHqlOutputs] = useState({});
  const [currentHQL, setCurrentHQL] = useState('');
  const [showConflict, setShowConflict] = useState(false);

  // V2 API 特有状态
  const [performanceReport, setPerformanceReport] = useState(null);
  const [debugTrace, setDebugTrace] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  // 生成所有模式的HQL（带防抖优化 - 500ms）
  useEffect(() => {
    if (!isOpen || !canvasFields.length) return;

    const timeoutId = setTimeout(async () => {
      if (useV2API) {
        // 使用 V2 API 生成 HQL
        await generateHQLWithV2API();
      } else {
        // 使用 V1 前端生成（原有逻辑）
        const mockHQL = {
          SELECT: generateSELECTHQL(canvasFields, whereConditions, gameData, selectedEvent),
          CREATE_TABLE: generateCREATEHQL(canvasFields, whereConditions, gameData, selectedEvent, 'table'),
          CREATE_VIEW: generateCREATEHQL(canvasFields, whereConditions, gameData, selectedEvent, 'view'),
          INSERT: generateINSERTHQL(canvasFields, whereConditions, gameData, selectedEvent)
        };

        setHqlOutputs(mockHQL);
        if (!isEditing) {
          setCurrentHQL(mockHQL[activeTab]);
        }
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [isOpen, canvasFields, whereConditions, activeTab, isEditing, gameData, selectedEvent, useV2API]);

  // V2 API 调用函数
  const generateHQLWithV2API = async () => {
    setIsLoading(true);
    setApiError(null);

    try {
      // 转换字段格式为V2 API期望的格式
      const v2Fields = canvasFields.map(field => ({
        fieldName: field.field_name || field.name,
        fieldType: field.field_type || field.type || 'base',
        jsonPath: field.json_path,
        customExpression: field.custom_expression,
        alias: field.alias
      }));

      const requestData = {
        events: [{
          game_gid: gameData.gid,
          event_id: selectedEvent.id
        }],
        fields: v2Fields,
        where_conditions: whereConditions.map(cond => ({
          field: cond.field,
          operator: cond.operator,
          value: cond.value,
          logicalOp: cond.logicalOp || 'AND'
        })),
        options: {
          mode: 'single',
          include_performance: true,
          debug: true
        }
      };

      // 调用 V2 API
      const response = await fetch('/hql-preview-v2/api/generate-debug', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Failed to generate HQL');
      }

      // 提取数据
      const hql = result.data.hql;
      const performance = result.data.performance;
      const steps = result.data.steps;

      // 更新状态
      setHqlOutputs({ SELECT: hql });
      setCurrentHQL(hql);
      setPerformanceReport(performance);
      setDebugTrace(steps);

    } catch (error) {
      console.error('V2 API Error:', error);
      setApiError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // 切换Tab
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (!isEditing) {
      setCurrentHQL(hqlOutputs[tab]);
    }
  };

  // 启用编辑
  const handleEnableEdit = () => {
    setIsEditing(true);
  };

  // 重新生成
  const handleRegenerate = () => {
    setIsEditing(false);
    setShowConflict(false);
  };

  // 保留编辑
  const handleKeepEdit = () => {
    setShowConflict(false);
    // 更新原始哈希
  };

  if (!isOpen) return null;

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      enableEscClose={true}
      overlayClassName="hql-preview-modal-overlay"
      contentClassName="glass-card hql-preview-modal"
      zIndex={1200}
    >
      <div className="modal-content glass-card hql-preview-modal" style={{ backgroundColor: 'transparent', width: '95vw', maxWidth: '1200px', height: '90vh', display: 'flex', flexDirection: 'column' }}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="header-left">
            <h3>
              <i className="bi bi-code-square"></i>
              HQL预览 - {activeTab.replace('_', ' ')}
            </h3>
            {isEditing && (
              <span className="badge badge-warning">编辑模式</span>
            )}
          </div>

          <div className="header-center">
            <div className="tab-switcher">
              {['SELECT', 'CREATE_TABLE', 'CREATE_VIEW', 'INSERT'].map(tab => (
                <button
                  key={tab}
                  className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => handleTabChange(tab)}
                >
                  {tab.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <button className="modal-close" onClick={onClose}>
            <i className="bi bi-x"></i>
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* 工具栏 */}
          <div className="editor-toolbar">
            <button className="btn btn-sm btn-outline-primary" onClick={() => {
              navigator.clipboard.writeText(currentHQL);
              alert('已复制到剪贴板');
            }}>
              <i className="bi bi-clipboard"></i> 复制
            </button>
            <button className="btn btn-sm btn-outline-secondary" onClick={() => {
              // 格式化HQL（简化实现）
            }}>
              <i className="bi bi-code-square"></i> 格式化
            </button>
            <button
              className={`btn btn-sm ${isEditing ? 'btn-warning' : 'btn-outline-primary'}`}
              onClick={isEditing ? handleRegenerate : handleEnableEdit}
            >
              <i className={isEditing ? 'bi bi-arrow-clockwise' : 'bi bi-pencil'}></i>
              {isEditing ? '重新生成' : '编辑'}
            </button>
          </div>

          {/* 冲突提示 */}
          {showConflict && (
            <div className="conflict-alert">
              <div className="alert alert-warning">
                <i className="bi bi-exclamation-triangle"></i>
                <div>
                  <strong>字段已变化</strong>
                  <p>HQL基于旧的字段配置生成，但画布字段已修改。是否重新生成HQL？</p>
                  <div className="conflict-actions">
                    <button className="btn btn-sm btn-danger" onClick={handleRegenerate}>
                      <i className="bi bi-arrow-clockwise"></i> 重新生成
                    </button>
                    <button className="btn btn-sm btn-primary" onClick={handleKeepEdit}>
                      <i className="bi bi-check"></i> 保留编辑
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 编辑器 */}
          <div className="editor-container">
            <div className="line-numbers">
              {currentHQL.split('\n').map((_, i) => (
                <div key={i}>{i + 1}</div>
              ))}
            </div>
            <div className="code-editor">
              {isEditing ? (
                <textarea
                  className="code-textarea"
                  value={currentHQL}
                  onChange={(e) => setCurrentHQL(e.target.value)}
                  spellCheck={false}
                />
              ) : (
                <div className="code-display">
                  <SyntaxHighlighter
                    language="sql"
                    style={vscDarkPlus}
                    showLineNumbers={false}
                    customStyle={{
                      background: 'transparent',
                      padding: 0,
                      margin: 0,
                      fontSize: '0.875rem',
                      fontFamily: "'JetBrains Mono', 'Courier New', monospace"
                    }}
                  >
                    {currentHQL}
                  </SyntaxHighlighter>
                </div>
              )}
            </div>
          </div>

          {/* 字段映射表 */}
          <div className="field-mapping">
            <h4>字段映射</h4>
            <table className="mapping-table">
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>来源</th>
                </tr>
              </thead>
              <tbody>
                {canvasFields.map(field => (
                  <tr key={field.id}>
                    <td>{field.fieldName}</td>
                    <td>{field.dataType || 'string'}</td>
                    <td>{field.fieldType === 'base' ? '基础字段' : '参数字段'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* V2 API 特性展示 */}
          {useV2API && (
            <div className="v2-features-section">
              {/* 加载状态 */}
              {isLoading && (
                <div className="v2-loading">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">加载中...</span>
                  </div>
                  <p>正在生成HQL并分析性能...</p>
                </div>
              )}

              {/* API错误 */}
              {apiError && (
                <div className="v2-error alert alert-danger">
                  <i className="bi bi-exclamation-triangle"></i>
                  <div>
                    <strong>API调用失败</strong>
                    <p>{apiError}</p>
                  </div>
                </div>
              )}

              {/* 性能分析 */}
              {!isLoading && !apiError && performanceReport && (
                <PerformanceIndicator performance={performanceReport} />
              )}

              {/* 调试模式 */}
              {!isLoading && !apiError && debugTrace && (
                <DebugViewer debugTrace={debugTrace} />
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <div className="footer-left">
            <span>{canvasFields.length} 个字段</span>
            <span>•</span>
            <span>{whereConditions.length} 个条件</span>
          </div>
          <div className="footer-right">
            <button className="btn btn-secondary" onClick={onClose}>
              关闭
            </button>
            <button className="btn btn-primary" onClick={() => {
              // 应用HQL
              onClose();
            }}>
              <i className="bi bi-check"></i> 应用
            </button>
          </div>
        </div>
      </div>
    </BaseModal>
  );
}

// HQL生成器（临时实现，后续替换为实际API调用）
function generateSELECTHQL(fields, whereConditions, gameData, event) {
  const fieldList = fields.map(f => `  ${f.fieldName}`).join(',\n');
  const whereClause = whereConditions.length > 0
    ? `WHERE\n  ${generateWhereClause(whereConditions)}`
    : '';

  return `SELECT\n${fieldList}\nFROM ${gameData?.ods_db || 'ieu_ods'}.ods_${gameData?.gid || '10000147'}_all_view\n${whereClause};`;
}

function generateCREATEHQL(fields, whereConditions, gameData, event, type) {
  const fieldList = fields.map(f => `  ${f.fieldName}`).join(',\n');
  const tableName = `dwd_${event?.event_name || 'event'}_di`;

  return `CREATE ${type} IF NOT EXISTS ${tableName} AS\nSELECT\n${fieldList}\nFROM ${gameData?.ods_db || 'ieu_ods'}.ods_${gameData?.gid || '10000147'}_all_view;`;
}

function generateINSERTHQL(fields, whereConditions, gameData, event) {
  const fieldList = fields.map(f => f.fieldName).join(', ');
  const tableName = `dwd_${event?.event_name || 'event'}_di`;
  const whereClause = whereConditions.length > 0
    ? `WHERE ${generateWhereClause(whereConditions)}`
    : '';

  return `INSERT OVERWRITE TABLE ${tableName}\nSELECT ${fieldList}\nFROM ${gameData?.ods_db || 'ieu_ods'}.ods_${gameData?.gid || '10000147'}_all_view\n${whereClause};`;
}

function generateWhereClause(conditions) {
  // 简化实现，实际应使用whereGenerator
  return conditions.map(c => `${c.field} ${c.operator} '${c.value}'`).join(' AND ');
}
