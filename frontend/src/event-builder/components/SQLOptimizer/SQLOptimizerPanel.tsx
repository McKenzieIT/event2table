/**
 * SQLOptimizerPanel Component
 * SQL 优化器面板组件
 */

import React, { useState } from 'react';

/**
 * SQL 分析结果接口
 */
interface SQLAnalysisResult {
  performance_score: number;
  issues: Array<{
    type: string;
    severity: 'high' | 'medium' | 'low';
    message: string;
    location?: string;
  }>;
}

/**
 * SQL 优化建议接口
 */
interface SQLOptimizationSuggestion {
  id: string;
  type: 'partition' | 'index' | 'query' | 'other';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  code?: string;
}

/**
 * 组件 Props 接口
 */
export interface SQLOptimizerPanelProps {
  sql: string;
  onApplySuggestion?: (suggestion: SQLOptimizationSuggestion) => void;
  onOptimizedSQLChange?: (optimizedSQL: string) => void;
}

/**
 * SQLOptimizerPanel Component
 */
export default function SQLOptimizerPanel({
  sql,
  onApplySuggestion,
  onOptimizedSQLChange,
}: SQLOptimizerPanelProps) {
  const [analysisResult, setAnalysisResult] = useState<SQLAnalysisResult | null>(null);
  const [suggestions, setSuggestions] = useState<SQLOptimizationSuggestion[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<SQLOptimizationSuggestion | null>(null);

  /**
   * 分析 SQL
   */
  const analyzeSQL = async () => {
    setIsAnalyzing(true);
    try {
      // 这里应该调用后端 API 进行 SQL 分析
      // 暂时使用模拟数据
      await new Promise(resolve => setTimeout(resolve, 1000));

      // 模拟分析结果
      const mockResult: SQLAnalysisResult = {
        performance_score: 65,
        issues: [
          {
            type: 'missing_partition',
            severity: 'high',
            message: '缺少分区过滤，可能导致全表扫描',
            location: 'WHERE clause',
          },
          {
            type: 'missing_index',
            severity: 'medium',
            message: '建议为 user_id 字段添加索引',
            location: 'JOIN condition',
          },
        ],
      };

      // 模拟优化建议
      const mockSuggestions: SQLOptimizationSuggestion[] = [
        {
          id: '1',
          type: 'partition',
          title: '添加分区过滤',
          description: '在 WHERE 子句中添加 dt 分区过滤，避免全表扫描',
          impact: 'high',
          code: `AND dt = '${new Date().toISOString().split('T')[0]}'`,
        },
        {
          id: '2',
          type: 'index',
          title: '使用索引提示',
          description: '为 user_id 字段添加索引提示以优化 JOIN 性能',
          impact: 'medium',
          code: '/*+ INDEX(t user_id_idx) */',
        },
        {
          id: '3',
          type: 'query',
          title: '优化子查询',
          description: '将子查询转换为 JOIN 以提高性能',
          impact: 'medium',
        },
      ];

      setAnalysisResult(mockResult);
      setSuggestions(mockSuggestions);
    } catch (error) {
      console.error('SQL 分析失败:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  /**
   * 应用优化建议
   */
  const handleApplySuggestion = (suggestion: SQLOptimizationSuggestion) => {
    if (onApplySuggestion) {
      onApplySuggestion(suggestion);
    }
    setSelectedSuggestion(suggestion);
  };

  /**
   * 获取性能分数颜色
   */
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-success';
    if (score >= 60) return 'text-warning';
    return 'text-danger';
  };

  /**
   * 获取严重程度图标
   */
  const getSeverityIcon = (severity: string): string => {
    switch (severity) {
      case 'high':
        return 'bi-exclamation-triangle-fill text-danger';
      case 'medium':
        return 'bi-exclamation-circle-fill text-warning';
      case 'low':
        return 'bi-info-circle-fill text-info';
      default:
        return 'bi-circle-fill text-secondary';
    }
  };

  /**
   * 获取影响程度徽章样式
   */
  const getImpactBadgeClass = (impact: string): string => {
    switch (impact) {
      case 'high':
        return 'bg-danger';
      case 'medium':
        return 'bg-warning';
      case 'low':
        return 'bg-info';
      default:
        return 'bg-secondary';
    }
  };

  return (
    <div className="sql-optimizer-panel">
      <div className="optimizer-header">
        <h5 className="mb-0">
          <i className="bi bi-speedometer2 me-2"></i>
          SQL 优化器
        </h5>
        <button
          className="btn btn-primary btn-sm"
          onClick={analyzeSQL}
          disabled={isAnalyzing || !sql}
        >
          {isAnalyzing ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              分析中...
            </>
          ) : (
            <>
              <i className="bi bi-play-circle me-2"></i>
              分析 SQL
            </>
          )}
        </button>
      </div>

      {analysisResult && (
        <div className="optimizer-content mt-3">
          {/* 性能评分 */}
          <div className="card mb-3">
            <div className="card-body">
              <h6 className="card-title mb-3">性能评分</h6>
              <div className="d-flex align-items-center">
                <div className={`display-4 fw-bold ${getScoreColor(analysisResult.performance_score)}`}>
                  {analysisResult.performance_score}
                </div>
                <div className="ms-3">
                  <div className="progress" style={{ width: '200px' }}>
                    <div
                      className={`progress-bar ${getScoreColor(analysisResult.performance_score).replace('text-', 'bg-')}`}
                      role="progressbar"
                      style={{ width: `${analysisResult.performance_score}%` }}
                      aria-valuenow={analysisResult.performance_score}
                      aria-valuemin={0}
                      aria-valuemax={100}
                    ></div>
                  </div>
                  <small className="text-muted">满分 100 分</small>
                </div>
              </div>
            </div>
          </div>

          {/* 问题列表 */}
          {analysisResult.issues.length > 0 && (
            <div className="card mb-3">
              <div className="card-body">
                <h6 className="card-title mb-3">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  发现的问题 ({analysisResult.issues.length})
                </h6>
                <div className="list-group list-group-flush">
                  {analysisResult.issues.map((issue, index) => (
                    <div key={index} className="list-group-item d-flex align-items-start">
                      <i className={`bi ${getSeverityIcon(issue.severity)} me-3 mt-1`}></i>
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-center">
                          <h6 className="mb-1">{issue.type}</h6>
                          <span className={`badge ${getImpactBadgeClass(issue.severity)}`}>
                            {issue.severity.toUpperCase()}
                          </span>
                        </div>
                        <p className="mb-1 text-muted small">{issue.message}</p>
                        {issue.location && (
                          <small className="text-muted">
                            <i className="bi bi-geo-alt me-1"></i>
                            {issue.location}
                          </small>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 优化建议 */}
          {suggestions.length > 0 && (
            <div className="card">
              <div className="card-body">
                <h6 className="card-title mb-3">
                  <i className="bi bi-lightbulb me-2"></i>
                  优化建议 ({suggestions.length})
                </h6>
                <div className="list-group list-group-flush">
                  {suggestions.map((suggestion) => (
                    <div
                      key={suggestion.id}
                      className={`list-group-item ${selectedSuggestion?.id === suggestion.id ? 'active' : ''}`}
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleApplySuggestion(suggestion)}
                    >
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <div className="d-flex align-items-center mb-2">
                            <h6 className="mb-0 me-2">{suggestion.title}</h6>
                            <span className={`badge ${getImpactBadgeClass(suggestion.impact)}`}>
                              {suggestion.impact.toUpperCase()}
                            </span>
                          </div>
                          <p className="mb-2 small text-muted">{suggestion.description}</p>
                          {suggestion.code && (
                            <pre className="mb-0 small bg-light p-2 rounded">
                              <code>{suggestion.code}</code>
                            </pre>
                          )}
                        </div>
                        <button
                          className="btn btn-sm btn-outline-primary ms-3"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleApplySuggestion(suggestion);
                          }}
                        >
                          <i className="bi bi-check-circle"></i>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {!sql && (
        <div className="alert alert-info mt-3">
          <i className="bi bi-info-circle me-2"></i>
          请先输入 SQL 语句进行分析
        </div>
      )}
    </div>
  );
}
