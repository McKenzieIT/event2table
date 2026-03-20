// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Badge, Spinner, useToast } from "@shared/ui";
import "./TemplateGallery.css";

/**
 * TypeScript interfaces for Template Gallery
 */
interface Template {
  id: number;
  name: string;
  display_name: string;
  category: string;
  subcategory?: string;
  description?: string;
  hql_content: string;
  tags: string[];
  usage_count: number;
  is_featured: boolean;
  created_at: string;
}

interface Category {
  category: string;
  template_count: number;
  total_usage: number;
}

/**
 * Template Gallery Component
 * HQL模板库主页面 - 展示所有模板,支持分类浏览和搜索
 */
function TemplateGallery() {
  const navigate = useNavigate();
  const { success, error } = useToast();

  // State
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [showImportModal, setShowImportModal] = useState(false);

  // Fetch templates
  const fetchTemplates = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const searchParams: any = {
        limit: 50,
        offset: 0
      };
      
      if (selectedCategory) {
        searchParams.category = selectedCategory;
      }
      
      if (searchKeyword) {
        searchParams.keyword = searchKeyword;
      }
      
      const response = await fetch('/api/templates/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchParams)
      });
      
      const result = await response.json();
      
      if (result.success && result.data) {
        setTemplates(result.data.templates || []);
      } else {
        error("Failed to fetch templates");
      }
    } catch (err) {
      console.error("Failed to fetch templates:", err);
      error("Failed to fetch templates");
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory, searchKeyword, error]);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const response = await fetch('/api/templates/categories');
      const result = await response.json();
      
      if (result.success && result.data) {
        setCategories(result.data);
      }
    } catch (err) {
      console.error("Failed to fetch categories:", err);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchCategories();
    fetchTemplates();
  }, [fetchCategories, fetchTemplates]);

  // Handle template click
  const handleTemplateClick = (template: Template) => {
    navigate(`/templates/${template.id}`);
  };

  // Handle search
  const handleSearch = (keyword: string) => {
    setSearchKeyword(keyword);
  };

  // Handle import
  const handleImport = () => {
    setShowImportModal(true);
  };

  // Render template card
  const renderTemplateCard = (template: Template) => (
    <Card
      key={template.id}
      className="template-card"
      onClick={() => handleTemplateClick(template)}
    >
      <div className="template-card__header">
        <h3 className="template-card__title">{template.display_name}</h3>
        {template.is_featured && (
          <Badge variant="featured" className="template-card__badge">
            精选
          </Badge>
        )}
      </div>
      
      <div className="template-card__meta">
        <Badge variant="category">{template.category}</Badge>
        {template.subcategory && (
          <Badge variant="subcategory">{template.subcategory}</Badge>
        )}
      </div>
      
      {template.description && (
        <p className="template-card__description">
          {template.description}
        </p>
      )}
      
      <div className="template-card__footer">
        <div className="template-card__stats">
          <span className="template-card__usage">
            使用次数: {template.usage_count}
          </span>
        </div>
        
        {template.tags && template.tags.length > 0 && (
          <div className="template-card__tags">
            {template.tags.slice(0, 3).map((tag, index) => (
              <Badge key={index} variant="tag" size="small">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </Card>
  );

  return (
    <div className="template-gallery">
      <div className="template-gallery__header">
        <h1 className="template-gallery__title">HQL模板库</h1>
        <p className="template-gallery__subtitle">
          浏览和搜索常用的HQL模板,快速构建数据查询
        </p>
        
        <div className="template-gallery__actions">
          <Button variant="primary" onClick={handleImport}>
            导入模板
          </Button>
        </div>
      </div>

      <div className="template-gallery__content">
        {/* Categories Sidebar */}
        <aside className="template-gallery__sidebar">
          <h2 className="template-gallery__sidebar-title">分类</h2>
          <div className="template-gallery__categories">
            <button
              className={`template-gallery__category-item ${
                selectedCategory === null ? 'active' : ''
              }`}
              onClick={() => setSelectedCategory(null)}
            >
              全部模板
            </button>
            
            {categories.map((cat) => (
              <button
                key={cat.category}
                className={`template-gallery__category-item ${
                  selectedCategory === cat.category ? 'active' : ''
                }`}
                onClick={() => setSelectedCategory(cat.category)}
              >
                <span className="template-gallery__category-name">
                  {cat.category}
                </span>
                <span className="template-gallery__category-count">
                  {cat.template_count}
                </span>
              </button>
            ))}
          </div>
        </aside>

        {/* Templates Grid */}
        <main className="template-gallery__main">
          {/* Search Bar */}
          <div className="template-gallery__search">
            <input
              type="text"
              className="template-gallery__search-input"
              placeholder="搜索模板..."
              value={searchKeyword}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>

          {/* Templates */}
          {isLoading ? (
            <div className="template-gallery__loading">
              <Spinner />
              <p>加载中...</p>
            </div>
          ) : templates.length === 0 ? (
            <div className="template-gallery__empty">
              <p>没有找到匹配的模板</p>
            </div>
          ) : (
            <div className="template-gallery__grid">
              {templates.map(renderTemplateCard)}
            </div>
          )}
        </main>
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <div className="template-gallery__modal">
          <div className="template-gallery__modal-content">
            <h2>导入模板</h2>
            <p>选择要导入的模板文件 (JSON格式)</p>
            <Button onClick={() => setShowImportModal(false)}>关闭</Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default TemplateGallery;
