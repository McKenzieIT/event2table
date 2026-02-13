import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './AlterSql.css';

/**
 * ALTER SQL页面
 * 用于生成ALTER TABLE语句
 */
function AlterSql() {
  const [tableName, setTableName] = useState('');
  const [ alterations, setAlterations ] = useState([
    { action: 'ADD', column: '', type: 'string' }
  ]);

  const addAlteration = () => {
    setAlterations([...alterations, { action: 'ADD', column: '', type: 'string' }]);
  };

  const removeAlteration = (index) => {
    setAlterations(alterations.filter((_, i) => i !== index));
  };

  const updateAlteration = (index, field, value) => {
    const newAlterations = [...alterations];
    newAlterations[index][field] = value;
    setAlterations(newAlterations);
  };

  const generateSQL = () => {
    return alterations
      .filter(a => a.column)
      .map(a => `ALTER TABLE ${tableName} ${a.action} COLUMN ${a.column} ${a.type};`)
      .join('\n');
  };

  return (
    <div className="alter-sql-container">
      <div className="page-header">
        <h1>ALTER SQL生成器</h1>
        <Link to="/hql-manage" className="btn btn-outline-secondary">
          <i className="bi bi-arrow-left"></i>
          返回
        </Link>
      </div>

      <div className="content-layout">
        <div className="config-panel glass-card">
          <h3>配置</h3>
          <div className="form-group">
            <label>表名</label>
            <input
              type="text"
              className="form-control"
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              placeholder="表名 (例如: dwd_event_login)"
            />
          </div>

          <div className="alterations-list">
            {alterations.map((alt, index) => (
              <div key={index} className="alteration-item">
                <select
                  className="form-control"
                  value={alt.action}
                  onChange={(e) => updateAlteration(index, 'action', e.target.value)}
                >
                  <option value="ADD">ADD</option>
                  <option value="DROP">DROP</option>
                  <option value="MODIFY">MODIFY</option>
                </select>
                <input
                  type="text"
                  className="form-control"
                  value={alt.column}
                  onChange={(e) => updateAlteration(index, 'column', e.target.value)}
                  placeholder="列名 (例如: zone_id)"
                />
                <select
                  className="form-control"
                  value={alt.type}
                  onChange={(e) => updateAlteration(index, 'type', e.target.value)}
                >
                  <option value="string">STRING</option>
                  <option value="int">INT</option>
                  <option value="bigint">BIGINT</option>
                  <option value="decimal(10,2)">DECIMAL(10,2)</option>
                </select>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => removeAlteration(index)}
                >
                  <i className="bi bi-trash"></i>
                </button>
              </div>
            ))}
          </div>

          <button className="btn btn-outline-primary" onClick={addAlteration}>
            <i className="bi bi-plus-circle"></i>
            添加列
          </button>
        </div>

        <div className="result-panel glass-card">
          <h3>生成的SQL</h3>
          <pre className="sql-output">{generateSQL() || 'SELECT配置...'}</pre>
        </div>
      </div>
    </div>
  );
}

export default AlterSql;
