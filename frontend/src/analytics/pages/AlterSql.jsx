import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import './AlterSql.css';

/**
 * ALTER SQL 页面（后端集成版本）
 * 展示为公参字段生成的 ALTER TABLE 语句
 *
 * 迁移自: templates/alter_sql.html
 *
 * 功能:
 * - 从 URL 参数获取 param_id
 * - 调用后端 API 获取 ALTER TABLE 语句
 * - 展示参数详情和生成的 SQL
 * - 支持复制 SQL 到剪贴板
 */
function AlterSql() {
  const { paramId } = useParams();
  const [param, setParam] = useState(null);
  const [alterSql, setAlterSql] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAlterSql = async () => {
      if (!paramId) {
        setError('缺少参数 ID');
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`/api/alter-table/${paramId}`);

        if (!response.ok) {
          if (response.status === 404) {
            setError('参数未找到');
          } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          setIsLoading(false);
          return;
        }

        const result = await response.json();

        if (result.success) {
          setParam(result.data.param);
          setAlterSql(result.data.alter_sql);
        } else {
          setError(result.error || '获取 ALTER SQL 失败');
        }
      } catch (err) {
        console.error('Failed to fetch ALTER SQL:', err);
        setError(`获取失败: ${err instanceof Error ? err.message : '未知错误'}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlterSql();
  }, [paramId]);

  const handleCopy = () => {
    navigator.clipboard
      .writeText(alterSql)
      .then(() => {
        toast.success('SQL 已复制到剪贴板');
      })
      .catch(() => {
        toast.error('复制失败，请手动复制');
      });
  };

  return (
    <div className="alter-sql-container">
      <div className="page-header">
        <div>
          <h1>ALTER TABLE 语句</h1>
          <p>为公参字段生成 ALTER TABLE 语句</p>
        </div>
        <Link to="/parameters" className="btn btn-outline-secondary">
          <i className="bi bi-arrow-left"></i>
          返回公参列表
        </Link>
      </div>

      {isLoading ? (
        <div className="loading-state">
          <i className="bi bi-arrow-repeat spin-icon"></i>
          <span>加载中...</span>
        </div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{ color: 'var(--color-error)', marginBottom: '1rem' }}>
            <i className="bi bi-exclamation-triangle"></i>
            {error}
          </div>
          <Link to="/parameters" className="btn btn-outline-primary">
            返回公参列表
          </Link>
        </div>
      ) : (
        <>
          {/* Info Alert */}
          <div
            className="glass-card"
            style={{
              padding: '1rem',
              marginBottom: '1.5rem',
              background: 'rgba(0, 113, 227, 0.15)',
              borderLeft: '4px solid var(--brand-primary)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <i className="bi bi-info-circle" style={{ color: 'var(--brand-primary)' }}></i>
              <span style={{ color: 'var(--text-secondary)' }}>
                以下是为新公参字段生成的 ALTER TABLE 语句，请在 Hive 中执行以添加新字段到公参表。
              </span>
            </div>
          </div>

          {/* Table Info */}
          <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
            <h5 className="mb-3" style={{ color: 'var(--color-primary)' }}>
              表信息
            </h5>
            <table className="oled-table">
              <tbody>
                <tr>
                  <th style={{ width: '30%', color: 'var(--text-primary)' }}>表名</th>
                  <td style={{ color: 'var(--text-secondary)' }}>
                    <code
                      style={{
                        background: 'rgba(0, 0, 0, 0.5)',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                      }}
                    >
                      {param?.table_name}
                    </code>
                  </td>
                </tr>
                <tr>
                  <th style={{ color: 'var(--text-primary)' }}>参数名</th>
                  <td style={{ color: 'var(--text-secondary)', fontWeight: 'bold' }}>
                    {param?.param_name}
                  </td>
                </tr>
                <tr>
                  <th style={{ color: 'var(--text-primary)' }}>参数中文名</th>
                  <td style={{ color: 'var(--text-secondary)' }}>{param?.param_name_cn}</td>
                </tr>
                <tr>
                  <th style={{ color: 'var(--text-primary)' }}>参数类型</th>
                  <td style={{ color: 'var(--text-secondary)' }}>
                    <code
                      style={{
                        background: 'rgba(0, 0, 0, 0.5)',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                      }}
                    >
                      {param?.param_type}
                    </code>
                  </td>
                </tr>
                <tr>
                  <th style={{ color: 'var(--text-primary)' }}>所属游戏</th>
                  <td style={{ color: 'var(--text-secondary)' }}>
                    {param?.game_name} ({param?.gid})
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* ALTER TABLE Statement */}
          <div
            className="glass-card"
            style={{
              padding: '1.5rem',
              marginBottom: '1.5rem',
            }}
          >
            <h5 className="mb-3" style={{ color: 'var(--color-primary)' }}>
              ALTER TABLE 语句
            </h5>
            <div
              style={{
                background: 'rgba(0, 0, 0, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  padding: '0.75rem',
                  background: 'rgba(0, 0, 0, 0.6)',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-tertiary)' }}>
                  SQL 语句
                </span>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-primary"
                  onClick={handleCopy}
                  style={{ fontSize: 'var(--text-sm)', padding: '0.25rem 0.75rem' }}
                >
                  <span>复制</span>
                </button>
              </div>
              <pre
                className="code-block-display"
                style={{
                  background: 'transparent',
                  border: 'none',
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {alterSql}
              </pre>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button type="button" className="btn btn-outline-primary" onClick={handleCopy}>
              <span>复制 SQL</span>
            </button>
            <Link to="/parameters" className="btn btn-outline-secondary">
              <span>返回公参列表</span>
            </Link>
          </div>
        </>
      )}
    </div>
  );
}

export default AlterSql;
