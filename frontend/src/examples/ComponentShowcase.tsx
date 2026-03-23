/**
 * Component Showcase Page
 * 
 * 组件展示页面 - 集中展示所有组件示例
 */

import React, { useState } from 'react';

import ButtonExamples from './ButtonExamples';
import InputExamples from './InputExamples';
import ModalExamples from './ModalExamples';
import SelectExamples from './SelectExamples';
import TableExamples from './TableExamples';
import './ComponentShowcase.css';

type ComponentType = 'button' | 'input' | 'select' | 'table' | 'modal';

const COMPONENTS: { id: ComponentType; name: string; description: string }[] = [
  { id: 'button', name: 'Button', description: '按钮组件' },
  { id: 'input', name: 'Input', description: '输入框组件' },
  { id: 'select', name: 'Select', description: '下拉选择组件' },
  { id: 'table', name: 'Table', description: '表格组件' },
  { id: 'modal', name: 'Modal', description: '模态框组件' },
];

export default function ComponentShowcase() {
  const [activeComponent, setActiveComponent] = useState<ComponentType>('button');

  const renderComponent = () => {
    switch (activeComponent) {
      case 'button':
        return <ButtonExamples />;
      case 'input':
        return <InputExamples />;
      case 'select':
        return <SelectExamples />;
      case 'table':
        return <TableExamples />;
      case 'modal':
        return <ModalExamples />;
      default:
        return null;
    }
  };

  return (
    <div className="component-showcase">
      {/* Header */}
      <header className="showcase-header">
        <h1>Event2Table 组件库展示</h1>
        <p className="showcase-subtitle">
          Cyberpunk Lab Theme - Production-Ready Components
        </p>
      </header>

      {/* Navigation */}
      <nav className="showcase-nav">
        {COMPONENTS.map((component) => (
          <button
            key={component.id}
            className={`nav-item ${activeComponent === component.id ? 'active' : ''}`}
            onClick={() => setActiveComponent(component.id)}
          >
            <span className="nav-item-name">{component.name}</span>
            <span className="nav-item-desc">{component.description}</span>
          </button>
        ))}
      </nav>

      {/* Content */}
      <main className="showcase-content">
        {renderComponent()}
      </main>

      {/* Footer */}
      <footer className="showcase-footer">
        <p>
          Event2Table Component Library - Task 6.3: Examples and Demo
        </p>
        <p className="footer-note">
          所有示例均展示基础用法、进阶用法、组合使用和最佳实践
        </p>
      </footer>
    </div>
  );
}
