/**
 * ValueInput Component
 * 值输入组件（支持多种类型）
 */
import React, { useState } from 'react';
import './ValueInput.css';

export default function ValueInput({ value, onChange, operator, field }) {
  const [inputValue, setInputValue] = useState(value || '');

  // 根据操作符决定输入类型
  const needsArray = ['IN', 'NOT IN'].includes(operator);
  const needsRange = ['BETWEEN', 'NOT BETWEEN'].includes(operator);
  const needsNothing = ['IS NULL', 'IS NOT NULL'].includes(operator);

  const handleChange = (newValue) => {
    setInputValue(newValue);
    onChange(newValue);
  };

  // 如果操作符需要null值
  React.useEffect(() => {
    if (needsNothing) {
      onChange(null);
    }
  }, [operator, onChange]);

  if (needsNothing) {
    return <span className="text-muted">-</span>;
  }

  if (needsArray) {
    return (
      <input
        type="text"
        className="value-input"
        placeholder="值1, 值2, 值3"
        value={Array.isArray(value) ? value.join(', ') : value}
        onChange={(e) => {
          const arr = e.target.value.split(',').map(s => s.trim());
          handleChange(arr);
        }}
      />
    );
  }

  if (needsRange) {
    return (
      <div className="value-range-input">
        <input
          type="text"
          className="value-input"
          placeholder="最小值"
          value={Array.isArray(value) ? value[0] : ''}
          onChange={(e) => {
            const arr = Array.isArray(value) ? [...value] : [];
            arr[0] = e.target.value;
            handleChange(arr);
          }}
        />
        <span>至</span>
        <input
          type="text"
          className="value-input"
          placeholder="最大值"
          value={Array.isArray(value) ? value[1] : ''}
          onChange={(e) => {
            const arr = Array.isArray(value) ? [...value] : [];
            arr[1] = e.target.value;
            handleChange(arr);
          }}
        />
      </div>
    );
  }

  return (
    <input
      type="text"
      className="value-input"
      placeholder="值"
      value={inputValue}
      onChange={(e) => handleChange(e.target.value)}
    />
  );
}
