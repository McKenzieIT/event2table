/**
 * Select Component Examples
 * 
 * 展示 Select 组件的各种用法
 */

import React, { useState } from 'react';
import { Select, type SelectOption } from '@shared/ui';

const basicOptions: SelectOption[] = [
  { value: 'apple', label: '苹果' },
  { value: 'banana', label: '香蕉' },
  { value: 'orange', label: '橙子' },
  { value: 'grape', label: '葡萄' },
  { value: 'mango', label: '芒果' },
];

const categoryOptions: SelectOption[] = [
  { value: 'fruits', label: '水果' },
  { value: 'vegetables', label: '蔬菜' },
  { value: 'meat', label: '肉类' },
  { value: 'dairy', label: '乳制品' },
  { value: 'grains', label: '谷物' },
];

export function SelectBasicExample() {
  const [value, setValue] = useState<string | undefined>();

  return (
    <div className="example-section">
      <h3>基础用法</h3>
      <div className="select-group">
        <Select
          label="选择水果"
          placeholder="请选择水果"
          options={basicOptions}
          value={value}
          onChange={setValue}
        />
        <div className="selected-value">
          <strong>已选择：</strong>
          <span>{value || '(未选择)'}</span>
        </div>
      </div>
    </div>
  );
}

export function SelectMultipleExample() {
  const [values, setValues] = useState<(string | number)[]>([]);

  return (
    <div className="example-section">
      <h3>多选模式</h3>
      <div className="select-group">
        <Select
          label="选择分类（多选）"
          placeholder="选择多个分类"
          options={categoryOptions}
          value={values}
          onChange={setValues}
          multiple
        />
        <div className="selected-value">
          <strong>已选择：</strong>
          <span>{values.length > 0 ? values.join(', ') : '(未选择)'}</span>
        </div>
      </div>
    </div>
  );
}

export function SelectSearchableExample() {
  const [value, setValue] = useState<string | undefined>();

  const largeOptions: SelectOption[] = [
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'python', label: 'Python' },
    { value: 'java', label: 'Java' },
    { value: 'csharp', label: 'C#' },
    { value: 'cpp', label: 'C++' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'ruby', label: 'Ruby' },
    { value: 'php', label: 'PHP' },
    { value: 'swift', label: 'Swift' },
    { value: 'kotlin', label: 'Kotlin' },
    { value: 'scala', label: 'Scala' },
    { value: 'haskell', label: 'Haskell' },
    { value: 'elixir', label: 'Elixir' },
  ];

  return (
    <div className="example-section">
      <h3>可搜索</h3>
      <div className="select-group">
        <Select
          label="编程语言"
          placeholder="搜索并选择编程语言"
          options={largeOptions}
          value={value}
          onChange={setValue}
          searchable
        />
        <div className="selected-value">
          <strong>已选择：</strong>
          <span>{value || '(未选择)'}</span>
        </div>
      </div>
    </div>
  );
}

export function SelectStatesExample() {
  const [value, setValue] = useState<string | undefined>();

  return (
    <div className="example-section">
      <h3>状态示例</h3>
      <div className="select-group">
        <Select
          label="禁用状态"
          placeholder="无法选择"
          options={basicOptions}
          value={value}
          onChange={setValue}
          disabled
        />
        <Select
          label="必填字段"
          placeholder="请选择"
          options={basicOptions}
          value={value}
          onChange={setValue}
          required
        />
        <Select
          label="错误状态"
          placeholder="请选择"
          options={basicOptions}
          value={value}
          onChange={setValue}
          error="请选择一个选项"
        />
      </div>
    </div>
  );
}

export function SelectWithHelperExample() {
  const [value, setValue] = useState<string | undefined>();

  return (
    <div className="example-section">
      <h3>辅助文本</h3>
      <div className="select-group">
        <Select
          label="选择水果"
          placeholder="请选择你喜欢的水果"
          options={basicOptions}
          value={value}
          onChange={setValue}
          helperText="选择后可以查看详细信息"
        />
        <Select
          label="选择分类"
          placeholder="请选择商品分类"
          options={categoryOptions}
          value={value}
          onChange={setValue}
          helperText="最多选择3个分类"
        />
      </div>
    </div>
  );
}

export function SelectSizeExample() {
  const [smallValue, setSmallValue] = useState<string | undefined>();
  const [mediumValue, setMediumValue] = useState<string | undefined>();
  const [largeValue, setLargeValue] = useState<string | undefined>();

  return (
    <div className="example-section">
      <h3>不同尺寸</h3>
      <div className="select-group">
        <Select
          label="小尺寸"
          size="small"
          placeholder="小尺寸选择器"
          options={basicOptions}
          value={smallValue}
          onChange={setSmallValue}
        />
        <Select
          label="中尺寸"
          size="medium"
          placeholder="中尺寸选择器"
          options={basicOptions}
          value={mediumValue}
          onChange={setMediumValue}
        />
        <Select
          label="大尺寸"
          size="large"
          placeholder="大尺寸选择器"
          options={basicOptions}
          value={largeValue}
          onChange={setLargeValue}
        />
      </div>
    </div>
  );
}

export function SelectDisabledOptionsExample() {
  const [value, setValue] = useState<string | undefined>();

  const optionsWithDisabled: SelectOption[] = [
    { value: 'option1', label: '选项 1' },
    { value: 'option2', label: '选项 2（禁用）', disabled: true },
    { value: 'option3', label: '选项 3' },
    { value: 'option4', label: '选项 4（禁用）', disabled: true },
    { value: 'option5', label: '选项 5' },
  ];

  return (
    <div className="example-section">
      <h3>禁用选项</h3>
      <div className="select-group">
        <Select
          label="选择选项"
          placeholder="请选择可用选项"
          options={optionsWithDisabled}
          value={value}
          onChange={setValue}
        />
      </div>
    </div>
  );
}

export function SelectControlledExample() {
  const [value, setValue] = useState<string | undefined>('apple');
  const [history, setHistory] = useState<string[]>([]);

  const handleChange = (newValue: string | number | (string | number)[]) => {
    const stringValue = String(newValue);
    setValue(stringValue as string);
    setHistory([...history, stringValue]);
  };

  return (
    <div className="example-section">
      <h3>受控组件</h3>
      <div className="select-group">
        <Select
          label="选择水果"
          placeholder="请选择水果"
          options={basicOptions}
          value={value}
          onChange={handleChange}
        />
        <div className="controlled-display">
          <strong>当前选择：</strong>
          <span>{value || '(未选择)'}</span>
        </div>
        <div className="history-display">
          <strong>选择历史：</strong>
          <ul>
            {history.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export function SelectBestPractices() {
  return (
    <div className="example-section">
      <h3>最佳实践</h3>
      <div className="best-practices">
        <div className="practice-item">
          <h4>1. 提供清晰的标签和占位符</h4>
          <Select
            label="选择水果"
            placeholder="请选择你喜欢的水果"
            options={basicOptions}
          />
        </div>
        <div className="practice-item">
          <h4>2. 为大量选项启用搜索功能</h4>
          <Select
            label="编程语言"
            placeholder="搜索并选择"
            options={basicOptions}
            searchable
          />
        </div>
        <div className="practice-item">
          <h4>3. 使用辅助文本提供额外信息</h4>
          <Select
            label="选择分类"
            placeholder="请选择"
            options={categoryOptions}
            helperText="可以选择多个分类"
          />
        </div>
        <div className="practice-item">
          <h4>4. 禁用不可用的选项</h4>
          <Select
            label="选择选项"
            placeholder="请选择"
            options={[
              { value: '1', label: '可用选项' },
              { value: '2', label: '禁用选项', disabled: true },
            ]}
          />
        </div>
        <div className="practice-item">
          <h4>5. 多选时明确提示用户</h4>
          <Select
            label="选择分类"
            placeholder="可以选择多个"
            options={categoryOptions}
            multiple
            helperText="按住 Ctrl/Cmd 可多选"
          />
        </div>
      </div>
    </div>
  );
}

export default function SelectExamples() {
  return (
    <div className="examples-container">
      <h2>Select 组件示例</h2>
      <SelectBasicExample />
      <SelectMultipleExample />
      <SelectSearchableExample />
      <SelectStatesExample />
      <SelectWithHelperExample />
      <SelectSizeExample />
      <SelectDisabledOptionsExample />
      <SelectControlledExample />
      <SelectBestPractices />
    </div>
  );
}
