// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useState, useEffect } from "react";

/**
 * Template Categories Component
 * 模板分类组件 - 展示和选择模板分类
 */
interface TemplateCategoriesProps {
  onCategorySelect: (category: string | null) => void;
  selectedCategory: string | null;
}

interface Category {
  category: string;
  template_count: number;
  total_usage: number;
}

function TemplateCategories({ onCategorySelect, selectedCategory }: TemplateCategoriesProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/templates/categories');
      const result = await response.json();
      
      if (result.success && result.data) {
        setCategories(result.data);
      }
    } catch (err) {
      console.error("Failed to fetch categories:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="template-categories">
      <h3 className="template-categories__title">模板分类</h3>
      
      <div className="template-categories__list">
        <button
          className={`template-categories__item ${
            selectedCategory === null ? 'active' : ''
          }`}
          onClick={() => onCategorySelect(null)}
        >
          <span className="template-categories__name">全部模板</span>
          <span className="template-categories__count">
            {categories.reduce((sum, cat) => sum + cat.template_count, 0)}
          </span>
        </button>
        
        {isLoading ? (
          <div className="template-categories__loading">加载中...</div>
        ) : (
          categories.map((cat) => (
            <button
              key={cat.category}
              className={`template-categories__item ${
                selectedCategory === cat.category ? 'active' : ''
              }`}
              onClick={() => onCategorySelect(cat.category)}
            >
              <span className="template-categories__name">{cat.category}</span>
              <span className="template-categories__count">{cat.template_count}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

export default TemplateCategories;
