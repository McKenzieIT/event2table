/**
 * HQLPreviewContainer Component
 * HQL预览容器组件 - 连接API和HQLPreview组件
 */
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { previewHQL } from '@shared/api/eventNodeBuilder';
import HQLPreview from './HQLPreview';

export default function HQLPreviewContainer({
  gameGid,
  event = null,
  fields = [],
  whereConditions = [],
  onShowDetails
}) {
  const [hqlContent, setHqlContent] = useState('');
  const [sqlMode, setSqlMode] = useState('view');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 当事件、字段、条件或模式变化时重新生成HQL
  useEffect(() => {
    const generateHQLInternal = async () => {
      // Enhanced validation
      if (!gameGid) {
        console.error('[HQLPreviewContainer] Missing gameGid');
        return;
      }

      if (!event || !event.id) {
        console.error('[HQLPreviewContainer] Missing or invalid event');
        setHqlContent('-- 请选择事件');
        return;
      }

      if (!fields || fields.length === 0) {
        console.warn('[HQLPreviewContainer] No fields selected');
        setHqlContent('-- 请添加字段');
        return;
      }

      // Debug logging
      console.log('[HQLPreviewContainer] generateHQL called', {
        hasEvent: !!event,
        eventId: event?.id,
        fieldsCount: fields?.length || 0
      });

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
            field_name: f.fieldName || f.name || '',
            field_type: f.fieldType === 'basic' ? 'base' : (f.fieldType || f.type || 'base'),
            aggregate_func: f.aggregateFunc || '',
            is_primary: f.isPrimary || false,
            alias: f.alias || f.fieldName,
            json_path: f.jsonPath || f.jsonPath
          })).filter(f => f.field_name),
          filter_conditions: filterConditionsDict,
          sql_mode: sqlMode
        };

        const result = await previewHQL(requestData);

        // previewHQL返回response.data，可能是HQL字符串或包含hql字段的对象
        if (typeof result === 'string') {
          // 后端直接返回HQL字符串
          setHqlContent(result);
        } else if (result.hql) {
          // 后端返回包含hql字段的对象
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
    };

    generateHQLInternal();
  }, [gameGid, event, fields, whereConditions, sqlMode]);

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
      readOnly={true}  // ✅ 在事件节点构建器中隐藏View/Procedure按钮
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
    event_name: PropTypes.string,  // 英文事件名
    event_name_cn: PropTypes.string,  // 中文事件名
    display_name: PropTypes.string,  // 显示名称
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
