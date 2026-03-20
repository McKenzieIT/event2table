// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useState, useCallback } from "react";
import { useToast } from "@shared/ui";

/**
 * Template Search Component
 * 模板搜索组件 - 提供高级搜索功能
 */
interface TemplateSearchProps {
  onSearch: (filters: SearchFilters) => void;
}

interface SearchFilters {
  keyword?: string;
  category?: string;
  subcategory?: string;
  tags?: string[];
  game_gid?: number;
}

function TemplateSearch({ onSearch }: TemplateSearchProps) {
  const { success } = useToast();
  
  const [filters, setFilters] = useState<SearchFilters>({});
  const [tagInput, setTagInput] = useState("");

  const handleSearch = () => {
    onSearch(filters);
    success("搜索已更新");
  };

  const handleAddTag = () => {
    if (tagInput.trim()) {
      setFilters(prev => ({
        ...prev,
        tags: [...(prev.tags || []), tagInput.trim()]
      }));
      setTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove)
    }));
  };

  return (
    <div className="template-search">
      <div className="template-search__section">
        <label className="template-search__label">关键词</label>
        <input
          type="text"
          className="template-search__input"
          placeholder="搜索模板名称、描述..."
          value={filters.keyword || ""}
          onChange={(e) => setFilters(prev => ({ ...prev, keyword: e.target.value }))}
        />
      </div>

      <div className="template-search__section">
        <label className="template-search__label">分类</label>
        <select
          className="template-search__select"
          value={filters.category || ""}
          onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value || undefined }))}
        >
          <option value="">全部分类</option>
          <option value="登录事件">登录事件</option>
          <option value="充值付费">充值付费</option>
          <option value="任务系统">任务系统</option>
          <option value="装备系统">装备系统</option>
          <option value="社交系统">社交系统</option>
        </select>
      </div>

      <div className="template-search__section">
        <label className="template-search__label">标签</label>
        <div className="template-search__tags-input">
          <input
            type="text"
            className="template-search__input"
            placeholder="添加标签..."
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
          />
          <button
            type="button"
            className="template-search__add-tag-btn"
            onClick={handleAddTag}
          >
            添加
          </button>
        </div>
        
        {filters.tags && filters.tags.length > 0 && (
          <div className="template-search__tags">
            {filters.tags.map((tag, index) => (
              <span key={index} className="template-search__tag">
                {tag}
                <button
                  type="button"
                  className="template-search__tag-remove"
                  onClick={() => handleRemoveTag(tag)}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="template-search__actions">
        <button
          type="button"
          className="template-search__btn template-search__btn--primary"
          onClick={handleSearch}
        >
          搜索
        </button>
        <button
          type="button"
          className="template-search__btn template-search__btn--secondary"
          onClick={() => setFilters({})}
        >
          重置
        </button>
      </div>
    </div>
  );
}

export default TemplateSearch;
