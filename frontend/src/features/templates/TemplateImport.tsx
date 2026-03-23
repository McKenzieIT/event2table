// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import { useToast } from "@shared/ui";
import React, { useState, useCallback } from "react";

/**
 * Template Import Component
 * 模板导入组件 - 支持从JSON文件导入模板
 */
interface TemplateImportProps {
  onImport: (template: any) => void;
  onClose: () => void;
}

function TemplateImport({ onImport, onClose }: TemplateImportProps) {
  const { success, error } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleImport = useCallback(async () => {
    if (!file) {
      error("请选择要导入的文件");
      return;
    }

    setIsImporting(true);
    
    try {
      const text = await file.text();
      const templateData = JSON.parse(text);
      
      // 验证必需字段
      const requiredFields = ['name', 'display_name', 'category', 'hql_content'];
      const missingFields = requiredFields.filter(field => !templateData[field]);
      
      if (missingFields.length > 0) {
        error(`缺少必需字段: ${missingFields.join(', ')}`);
        return;
      }
      
      onImport(templateData);
      success("模板导入成功");
      onClose();
    } catch (err) {
      console.error("Failed to import template:", err);
      error("导入失败: 文件格式不正确");
    } finally {
      setIsImporting(false);
    }
  }, [file, onImport, onClose, success, error]);

  return (
    <div className="template-import">
      <div className="template-import__header">
        <h2 className="template-import__title">导入模板</h2>
        <button
          type="button"
          className="template-import__close-btn"
          onClick={onClose}
        >
          ×
        </button>
      </div>

      <div className="template-import__body">
        <p className="template-import__description">
          选择一个JSON格式的模板文件进行导入
        </p>

        <div className="template-import__upload">
          <input
            type="file"
            accept=".json"
            onChange={handleFileChange}
            className="template-import__file-input"
          />
          
          {file && (
            <div className="template-import__file-info">
              <span className="template-import__file-name">{file.name}</span>
              <span className="template-import__file-size">
                {(file.size / 1024).toFixed(2)} KB
              </span>
            </div>
          )}
        </div>

        <div className="template-import__actions">
          <button
            type="button"
            className="template-import__btn template-import__btn--primary"
            onClick={handleImport}
            disabled={!file || isImporting}
          >
            {isImporting ? '导入中...' : '导入'}
          </button>
          <button
            type="button"
            className="template-import__btn template-import__btn--secondary"
            onClick={onClose}
            disabled={isImporting}
          >
            取消
          </button>
        </div>
      </div>
    </div>
  );
}

export default TemplateImport;
