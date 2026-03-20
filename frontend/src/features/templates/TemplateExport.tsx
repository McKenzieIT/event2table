// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React, { useState } from "react";
import { useToast } from "@shared/ui";

/**
 * Template Export Component
 * 模板导出组件 - 导出模板为JSON文件
 */
interface TemplateExportProps {
  template: any;
  onClose: () => void;
}

function TemplateExport({ template, onClose }: TemplateExportProps) {
  const { success, error } = useToast();
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = () => {
    try {
      setIsExporting(true);
      
      // 准备导出数据
      const exportData = {
        name: template.name,
        display_name: template.display_name,
        category: template.category,
        subcategory: template.subcategory,
        hql_content: template.hql_content,
        variables: JSON.parse(template.variables || '{}'),
        description: template.description,
        tags: JSON.parse(template.tags || '[]'),
        game_gid: template.game_gid,
        is_featured: template.is_featured === 1,
        is_system: template.is_system === 1
      };
      
      // 创建Blob并下载
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${template.name}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      success("模板导出成功");
      onClose();
    } catch (err) {
      console.error("Failed to export template:", err);
      error("导出失败");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="template-export">
      <div className="template-export__header">
        <h2 className="template-export__title">导出模板</h2>
        <button
          type="button"
          className="template-export__close-btn"
          onClick={onClose}
        >
          ×
        </button>
      </div>

      <div className="template-export__body">
        <div className="template-export__info">
          <h3>{template.display_name}</h3>
          <p className="template-export__category">{template.category}</p>
          {template.description && (
            <p className="template-export__description">{template.description}</p>
          )}
        </div>

        <div className="template-export__actions">
          <button
            type="button"
            className="template-export__btn template-export__btn--primary"
            onClick={handleExport}
            disabled={isExporting}
          >
            {isExporting ? '导出中...' : '导出为JSON'}
          </button>
          <button
            type="button"
            className="template-export__btn template-export__btn--secondary"
            onClick={onClose}
            disabled={isExporting}
          >
            取消
          </button>
        </div>
      </div>
    </div>
  );
}

export default TemplateExport;
