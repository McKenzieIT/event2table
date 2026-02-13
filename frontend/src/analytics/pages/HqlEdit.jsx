import React from 'react';
import { Link } from 'react-router-dom';
import './HqlEdit.css';

/**
 * HQL编辑页面
 * 编辑HQL语句
 */
function HqlEdit() {
  return (
    <div className="hql-edit-container">
      <div className="page-header glass-card">
        <h1>编辑HQL</h1>
        <Link to="/hql-manage" className="btn btn-outline-secondary">
          返回
        </Link>
      </div>
      <div className="editor-card glass-card">
        <p>HQL编辑器功能</p>
      </div>
    </div>
  );
}
export default HqlEdit;
