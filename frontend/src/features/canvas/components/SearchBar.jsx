import React, { useState } from 'react';
import { Button, Input } from '@shared/ui';
import './SearchBar.css';

/**
 * 搜索栏组件
 * 可折叠的搜索输入框
 *
 * @param {Function} onSearch - 搜索回调函数，接收搜索词作为参数
 *
 * @example
 * <SearchBar onSearch={(term) => console.log(term)} />
 */
export default function SearchBar({ onSearch }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    onSearch(value);
  };

  return (
    <div className={`search-bar ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <Button
        variant="ghost"
        size="sm"
        className="search-toggle"
        onClick={handleToggle}
        title="搜索节点"
        type="button"
      >
        🔍
      </Button>
      {isExpanded && (
        <Input
          type="text"
          className="search-input"
          placeholder="搜索中文名称或英文名称..."
          value={searchTerm}
          onChange={handleInputChange}
          autoFocus
        />
      )}
    </div>
  );
}
