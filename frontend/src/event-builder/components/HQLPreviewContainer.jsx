/**
 * HQLPreviewContainer Component
 * HQL预览容器组件 - 连接API和HQLPreview组件
 */
import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { previewHQL } from '@shared/api/eventNodeBuilderApi';
import HQLPreview from './HQLPreview';

export default function HQLPreviewContainer({
  gameGid,
  event,
  fields = [],
  whereConditions = [],
  onShowDetails
}) {
  const [hqlContent, setHqlContent] = useState('');
  const [sqlMode, setSqlMode] = useState('view');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 生成HQL - 使用useCallback以稳定函数引用
  const generateHQL = useCallback(async () => {
    if (!event || !event.id) {
      setHqlContent('');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 转换 whereConditions 数组为后端期望的格式
      const filterConditionsDict = {
        custom_where: (whereConditions || []).length > 0
          ? (whereConditions || []).map(c => `${c.field || ''} ${c.operator || '='} '${c.value || ''}'`).join(' AND ')
          : '',
        conditions: whereConditions || []
      };

      const requestData = {
        game_gid: parseInt(gameGid, 10),  // 确保game_gid是数字
        event_id: event.id,
        fields: (fields || []).map(f => ({
          param_id: f.paramId,
          field_name: f.fieldName,
          field_type: f.fieldType,
          aggregate_func: f.aggregateFunc || '',
          is_primary: f.isPrimary || false,
          alias: f.alias
        })),
        filter_conditions: filterConditionsDict,
        sql_mode: sqlMode
      };

      const result = await previewHQL(requestData);

      // previewHQL返回的是response.data，直接是{ hql: "...", view: "..." }格式
      // 而不是完整的{ success: true, data: { hql: "..." } }格式
      if (result.hql) {
        setHqlContent(result.hql);
      } else {
        throw new Error(result.error || '生成HQL失败');
      }
    } catch (err) {
      console.error('[HQLPreviewContainer] Failed to generate HQL:', err);
      setError(err.message);
      setHqlContent(`-- 错误: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [gameGid, event, fields, whereConditions, sqlMode]); // useCallback依赖数组

  // 当事件、字段、条件或模式变化时重新生成HQL
  useEffect(() => {
    generateHQL();
  }, [generateHQL]); // 依赖generateHQL函数

  const handleModeChange = (newMode) => {
    setSqlMode(newMode);
  };

  const handleContentChange = (newContent) => {
    setHqlContent(newContent);
  };

  return (
    <HQLPreview
      hqlContent={hqlContent}
      sqlMode={sqlMode}
      onModeChange={handleModeChange}
      onContentChange={handleContentChange}
      fields={fields}
      isLoading={isLoading}
      onShowDetails={onShowDetails}
    />
  );
}

HQLPreviewContainer.propTypes = {
  gameGid: PropTypes.number.isRequired,
  event: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired
  }),
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      paramId: PropTypes.number,
      fieldName: PropTypes.string.isRequired,
      fieldType: PropTypes.string.isRequired,
      alias: PropTypes.string,  // 添加 alias 字段
      aggregateFunc: PropTypes.string,
      isPrimary: PropTypes.bool
    })
  ),
  whereConditions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      field: PropTypes.string.isRequired,
      operator: PropTypes.string.isRequired,
      value: PropTypes.any
    })
  ),
  onShowDetails: PropTypes.func
};

HQLPreviewContainer.defaultProps = {
  fields: [],
  whereConditions: [],
  event: null
};
