/**
 * Button Component Examples
 * 
 * 展示 Button 组件的各种用法
 */

import React, { useState } from 'react';
import { Button } from '@shared/ui';

export function ButtonBasicExample() {
  return (
    <div className="example-section">
      <h3>基础用法</h3>
      <div className="button-group">
        <Button variant="primary">Primary Button</Button>
        <Button variant="secondary">Secondary Button</Button>
        <Button variant="ghost">Ghost Button</Button>
        <Button variant="danger">Danger Button</Button>
      </div>
    </div>
  );
}

export function ButtonSizeExample() {
  return (
    <div className="example-section">
      <h3>不同尺寸</h3>
      <div className="button-group">
        <Button size="small" variant="primary">Small</Button>
        <Button size="medium" variant="primary">Medium</Button>
        <Button size="large" variant="primary">Large</Button>
      </div>
    </div>
  );
}

export function ButtonStateExample() {
  const [loading, setLoading] = useState(false);

  const handleClick = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <div className="example-section">
      <h3>状态示例</h3>
      <div className="button-group">
        <Button disabled>Disabled</Button>
        <Button loading={loading} onClick={handleClick}>
          {loading ? 'Loading...' : 'Click to Load'}
        </Button>
      </div>
    </div>
  );
}

export function ButtonVariantExample() {
  return (
    <div className="example-section">
      <h3>所有变体</h3>
      <div className="button-group">
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="danger">Danger</Button>
        <Button variant="outline-primary">Outline Primary</Button>
        <Button variant="outline-danger">Outline Danger</Button>
        <Button variant="outline-secondary">Outline Secondary</Button>
        <Button variant="success">Success</Button>
        <Button variant="warning">Warning</Button>
        <Button variant="info">Info</Button>
        <Button variant="outline-success">Outline Success</Button>
        <Button variant="text">Text</Button>
      </div>
    </div>
  );
}

export function ButtonWithIconExample() {
  const SearchIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );

  const DownloadIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );

  return (
    <div className="example-section">
      <h3>带图标按钮</h3>
      <div className="button-group">
        <Button variant="primary" icon={SearchIcon}>
          Search
        </Button>
        <Button variant="secondary" icon={DownloadIcon}>
          Download
        </Button>
        <Button variant="ghost" icon={SearchIcon} />
      </div>
    </div>
  );
}

export function ButtonActionExample() {
  const [count, setCount] = useState(0);

  return (
    <div className="example-section">
      <h3>交互示例</h3>
      <div className="button-group">
        <Button onClick={() => setCount(count + 1)}>
          Clicked {count} times
        </Button>
        <Button variant="danger" onClick={() => setCount(0)}>
          Reset
        </Button>
      </div>
    </div>
  );
}

export function ButtonBestPractices() {
  return (
    <div className="example-section">
      <h3>最佳实践</h3>
      <div className="best-practices">
        <div className="practice-item">
          <h4>1. 主要操作使用 Primary 变体</h4>
          <Button variant="primary">提交表单</Button>
        </div>
        <div className="practice-item">
          <h4>2. 次要操作使用 Secondary 或 Ghost</h4>
          <Button variant="secondary">取消</Button>
          <Button variant="ghost">查看详情</Button>
        </div>
        <div className="practice-item">
          <h4>3. 危险操作使用 Danger 变体</h4>
          <Button variant="danger">删除</Button>
        </div>
        <div className="practice-item">
          <h4>4. 加载状态提供反馈</h4>
          <Button variant="primary" loading>
            处理中...
          </Button>
        </div>
        <div className="practice-item">
          <h4>5. 禁用不可用的操作</h4>
          <Button disabled>不可用</Button>
        </div>
      </div>
    </div>
  );
}

export default function ButtonExamples() {
  return (
    <div className="examples-container">
      <h2>Button 组件示例</h2>
      <ButtonBasicExample />
      <ButtonSizeExample />
      <ButtonStateExample />
      <ButtonVariantExample />
      <ButtonWithIconExample />
      <ButtonActionExample />
      <ButtonBestPractices />
    </div>
  );
}
