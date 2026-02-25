import React from 'react';
import { useNavigate, useParams, useSearchParams, useOutletContext } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Input,
  Select,
  Button,
  Card,
  Checkbox,
  Spinner,
  useToast,
  SelectGamePrompt
} from '@shared/ui';
import './EventForm.css';

/**
 * Event Form Component
 * Supports creating and editing events
 * Requires game context
 */
function EventForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { currentGame } = useOutletContext();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();  // ✅ Fix: Add useQueryClient for cache invalidation
  const { success, error: showError } = useToast();

  const isEdit = !!id;

  // Get game_gid from query params (create mode) or use currentGame
  const gameGidFromQuery = searchParams.get('game_gid');
  const effectiveGameGid = gameGidFromQuery || currentGame?.gid;

  // Game context check - show prompt if no game selected (and not in edit mode)
  if (!currentGame && !gameGidFromQuery) {
    return <SelectGamePrompt message="创建事件需要先选择游戏" />;
  }

  const [formData, setFormData] = React.useState({
    event_name: '',
    event_name_cn: '',
    category_id: '',
    game_gid: effectiveGameGid || '',
    include_in_common_params: 1
  });

  const [errors, setErrors] = React.useState({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  // Fetch categories for dropdown (requires game_gid)
  const gameGid = searchParams.get('game_gid');
  const { data: categoriesData } = useQuery({
    queryKey: ['categories', gameGid],
    queryFn: async () => {
      if (!gameGid) {
        // Return empty categories if no game selected
        return { data: [] };
      }

      const response = await fetch(`/api/categories?game_gid=${gameGid}`);
      if (!response.ok) throw new Error('获取分类失败');
      const result = await response.json();
      return result;
    },
    enabled: !!gameGid // Only run query if gameGid exists
  });

  // Fetch event data (edit mode)
  const { data: eventData, isLoading } = useQuery({
    queryKey: ['event', id],
    queryFn: async () => {
      if (!isEdit) return null;
      const gameGid = searchParams.get('game_gid');
      const params = gameGid ? `?game_gid=${gameGid}` : '';
      const response = await fetch(`/api/events/${id}${params}`);
      if (!response.ok) throw new Error('获取事件失败');
      const result = await response.json();
      return result;
    },
    enabled: isEdit,
  });

  // When event data loads successfully, populate form
  React.useEffect(() => {
    if (eventData?.data && isEdit) {
      const event = eventData.data;
      setFormData({
        event_name: event.event_name || '',
        event_name_cn: event.event_name_cn || '',
        category_id: event.category_id || '',
        game_gid: event.game_gid || '',
        include_in_common_params: event.include_in_common_params ?? 1
      });
    }
  }, [eventData, isEdit]);

  // Handle form input changes
  const handleChange = React.useCallback((e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? (checked ? 1 : 0) : value;
    setFormData(prev => ({ ...prev, [name]: newValue }));
    // Clear field error
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  }, [errors]);

  // Handle category selection (Select component uses value directly, not event)
  const handleCategoryChange = React.useCallback((value) => {
    setFormData(prev => ({ ...prev, category_id: value }));
    // Clear field error
    if (errors.category_id) {
      setErrors(prev => ({ ...prev, category_id: null }));
    }
  }, [errors]);

  // Handle cancel button click
  const handleCancel = React.useCallback(() => {
    navigate('/events');
  }, [navigate]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    const newErrors = {};
    if (!formData.event_name.trim()) newErrors.event_name = '事件名称不能为空';
    if (!formData.event_name_cn.trim()) newErrors.event_name_cn = '事件中文名不能为空';
    // Category is now optional - will default to "未分类" if not selected
    if (!formData.game_gid) newErrors.game_gid = '游戏GID不能为空';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      // Show toast for validation errors
      const firstError = Object.values(newErrors)[0];
      showError(firstError);
      return;
    }

    setIsSubmitting(true);

    try {
      const url = isEdit ? `/api/events/${id}` : '/api/events';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || (isEdit ? '更新失败' : '创建失败'));
      }

      // Show success toast
      success(isEdit ? '事件更新成功' : '事件创建成功');

      // ✅ Fix: Invalidate events cache to refresh the list
      const gameGid = searchParams.get('game_gid') || currentGame?.gid;
      if (gameGid) {
        queryClient.invalidateQueries({
          queryKey: ['events', parseInt(gameGid)]
        });
      }

      // Navigate back to events list
      navigate('/events', { replace: true });
    } catch (err) {
      // Show error toast
      showError(err.message);
      setErrors({ submit: err.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="event-form-container">
        <div className="loading-container">
          <Spinner size="lg" label="加载中..." />
        </div>
      </div>
    );
  }

  const categories = categoriesData?.data || [];

  // Prepare category options for Select component
  const categoryOptions = [
    { value: '', label: '未分类（默认）' },
    ...categories.map(category => ({
      value: category.id,
      label: category.name
    }))
  ];

  return (
    <div className="event-form-container">
      <div className="page-header">
        <h1>{isEdit ? '编辑事件' : '添加事件'}</h1>
        <Button
          variant="ghost"
          onClick={handleCancel}
        >
          返回事件列表
        </Button>
      </div>

      <Card className="event-form-card" padding="reset">
        <form onSubmit={handleSubmit} className="event-form">
          {errors.submit && (
            <div className="form-error-alert">
              <i className="bi bi-exclamation-triangle"></i>
              {errors.submit}
            </div>
          )}

          {/* Game GID Field (read-only in edit mode) */}
          <Input
            id="game_gid"
            name="game_gid"
            label="游戏GID"
            type="number"
            value={formData.game_gid}
            onChange={handleChange}
            disabled={isSubmitting || isEdit}
            placeholder="例如: 10000147"
            required
            error={errors.game_gid}
            helperText={`事件所属游戏的业务GID，${isEdit ? '编辑时不可修改' : '创建后不可修改，请谨慎填写'}`}
            icon="bi-hash"
          />

          {/* Event Name Field */}
          <Input
            id="event_name"
            name="event_name"
            label="事件名称"
            type="text"
            value={formData.event_name}
            onChange={handleChange}
            disabled={isSubmitting}
            placeholder="例如: game.role.login"
            required
            error={errors.event_name}
            helperText="事件的英文名称，通常使用点号分隔的命名方式"
            icon="bi-code-slash"
          />

          {/* Event Name Chinese Field */}
          <Input
            id="event_name_cn"
            name="event_name_cn"
            label="事件中文名"
            type="text"
            value={formData.event_name_cn}
            onChange={handleChange}
            disabled={isSubmitting}
            placeholder="例如: 角色登录"
            required
            error={errors.event_name_cn}
            icon="bi-translate"
          />

          {/* Category Field */}
          <Select
            id="category_id"
            label="事件分类"
            value={formData.category_id}
            onChange={handleCategoryChange}
            disabled={isSubmitting}
            options={categoryOptions}
            error={errors.category_id}
            helperText="可选，未选择时将自动归类为'未分类'"
          />

          {/* Include in Common Params Checkbox */}
          <div className="form-group checkbox-group">
            <Checkbox
              id="include_in_common_params"
              name="include_in_common_params"
              label="包含在公共参数中"
              checked={formData.include_in_common_params === 1}
              onChange={handleChange}
              disabled={isSubmitting}
            />
            <span className="form-hint">
              <i className="bi bi-info-circle"></i>
              是否将此事件的参数包含在公共参数配置中
            </span>
          </div>

          {/* Action Buttons */}
          <div className="form-actions">
            <Button
              type="submit"
              variant={isEdit ? 'warning' : 'success'}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Spinner size="sm" className="me-2" />
                  提交中...
                </>
              ) : (
                isEdit ? '保存修改' : '创建事件'
              )}
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              取消
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

// Export with React.memo for performance optimization
export default React.memo(EventForm);
