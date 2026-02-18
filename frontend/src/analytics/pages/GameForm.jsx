import React, { useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Button, Input, Card, Spinner, useToast } from '@shared/ui';
import './GameForm.css';

/**
 * 游戏表单组件
 * 支持创建和编辑游戏
 */
function GameForm() {
  const navigate = useNavigate();
  const { gid } = useParams();
  const isEdit = !!gid;
  const { success, error: showError } = useToast();

  const [formData, setFormData] = React.useState({
    name: '',
    gid: '',
    ods_db: 'ieu_ods'
  });

  const [errors, setErrors] = React.useState({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [gameDbId, setGameDbId] = React.useState(null); // 存储数据库ID用于验证

  // 获取游戏数据（编辑模式）
  const { data: gameData, isLoading } = useQuery({
    queryKey: ['game', gid],
    queryFn: async () => {
      if (!isEdit) return null;
      // 使用新的 by-gid 端点，通过业务GID查询游戏
      const response = await fetch(`/api/games/by-gid/${gid}`);
      if (!response.ok) throw new Error('获取游戏失败');
      const result = await response.json();
      return result;
    },
    enabled: isEdit,
  });

  // 当游戏数据加载成功后，填充表单
  React.useEffect(() => {
    if (gameData?.data && isEdit) {
      const game = gameData.data;
      // 保存数据库ID用于可能的后续使用
      setGameDbId(game.id);
      setFormData({
        name: game.name || '',
        gid: game.gid || '',
        ods_db: game.ods_db || 'ieu_ods'
      });
    }
  }, [gameData, isEdit]);

  // 创建/更新游戏
  const mutation = useMutation({
    mutationFn: async (data) => {
      // 确保gid转换为整数（后端API要求整数类型）
      const payload = {
        ...data,
        gid: parseInt(data.gid, 10)
      };

      // 编辑模式：使用业务GID调用API（后端API路由使用GID而非数据库ID）
      if (isEdit) {
        if (!data.gid) {
          throw new Error('游戏GID未找到，请刷新页面重试');
        }

        const response = await fetch(`/api/games/${data.gid}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const result = await response.json();
          throw new Error(result.message || '更新失败');
        }

        return response.json();
      } else {
        // 创建模式
        const response = await fetch('/api/games', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const result = await response.json();
          throw new Error(result.message || '创建失败');
        }

        return response.json();
      }
    },
    onSuccess: () => {
      // 显示成功提示
      success(isEdit ? '游戏更新成功' : '游戏创建成功');
      // 导航回列表页，并传递refresh标志以刷新列表
      navigate('/games', {
        replace: true,
        state: { refresh: true }
      });
    },
    onError: (error) => {
      const errorMessage = error.message || (isEdit ? '更新失败' : '创建失败');
      showError(errorMessage);
      setErrors({ submit: errorMessage });
      setIsSubmitting(false);
    }
  });

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // 清除该字段的错误
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  }, [errors]);

  const handleODSTypeChange = useCallback((odsType) => {
    const odsDb = odsType === 'domestic' ? 'ieu_ods' : 'hdy_data_sg';
    setFormData(prev => ({ ...prev, ods_db: odsDb }));
  }, []);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();

    // 验证
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = '游戏名称不能为空';
    if (!formData.gid.trim()) newErrors.gid = 'GID不能为空';
    if (!formData.ods_db.trim()) newErrors.ods_db = 'ODS数据库不能为空';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    mutation.mutate(formData);
  }, [formData, mutation]);

  const handleCancel = useCallback(() => {
    navigate('/games');
  }, [navigate]);

  if (isLoading) {
    return (
      <div className="game-form-container">
        <div className="loading-container">
          <Spinner size="lg" label="加载中..." />
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  const isDomestic = formData.ods_db === 'ieu_ods';

  return (
    <div className="game-form-container">
      <div className="page-header">
        <h1>{isEdit ? '编辑游戏' : '添加游戏'}</h1>
        <Button
          variant="ghost"
          onClick={handleCancel}
        >
          返回游戏列表
        </Button>
      </div>

      <Card className="game-form glass-card" padding="reset">
        <form onSubmit={handleSubmit}>
          {errors.submit && (
            <div className="alert alert-danger">
              <i className="bi bi-exclamation-triangle"></i>
              {errors.submit}
            </div>
          )}

          {/* Game ID Field */}
          <div className="form-group">
            <label htmlFor="gid" className="form-label">
              <i className="bi bi-tag"></i>
              游戏ID
              <span className="required-indicator">*</span>
            </label>
            <Input
              type="text"
              id="gid"
              name="gid"
              label=""
              icon="bi-hash"
              value={formData.gid}
              onChange={handleChange}
              disabled={isSubmitting || isEdit}
              placeholder="例如: 10000147"
              error={errors.gid}
            />
            <span className="form-hint">
              <i className="bi bi-info-circle"></i>
              游戏唯一标识符，{isEdit ? '创建后不可修改' : '创建后不可修改，请谨慎填写'}
            </span>
          </div>

          {/* Game Name Field */}
          <div className="form-group">
            <label htmlFor="name" className="form-label">
              <i className="bi bi-type"></i>
              游戏名称
              <span className="required-indicator">*</span>
            </label>
            <Input
              type="text"
              id="name"
              name="name"
              label=""
              icon="bi-controller"
              value={formData.name}
              onChange={handleChange}
              disabled={isSubmitting}
              placeholder="例如: 我的游戏"
              error={errors.name}
            />
          </div>

        {/* ODS Database Type */}
        <div className="form-group">
          <label className="form-label">
            <i className="bi bi-database"></i>
            ODS数据库类型
            <span className="required-indicator">*</span>
          </label>
          <div className="ods-options">
            {/* Domestic Option */}
            <div
              className={`option-card ${isDomestic ? 'selected' : ''}`}
              onClick={() => !isSubmitting && handleODSTypeChange('domestic')}
              data-testid="ods-type-domestic"
            >
              <div className="option-card-content">
                <input
                  className="form-check-input mt-1"
                  type="radio"
                  id="ods_type_domestic"
                  name="ods_type"
                  checked={isDomestic}
                  onChange={() => handleODSTypeChange('domestic')}
                  disabled={isSubmitting}
                />
                <div style={{ flex: 1 }}>
                  <div className="option-card-title">
                    <i className="bi bi-house option-card-icon option-card-icon-blue"></i>
                    国内 (ieu_ods)
                  </div>
                  <p className="option-card-description">用于国内服务器，使用 ieu_ods 数据库</p>
                </div>
              </div>
            </div>

            {/* Overseas Option */}
            <div
              className={`option-card ${!isDomestic ? 'selected-green' : ''}`}
              onClick={() => !isSubmitting && handleODSTypeChange('overseas')}
              data-testid="ods-type-overseas"
            >
              <div className="option-card-content">
                <input
                  className="form-check-input mt-1"
                  type="radio"
                  id="ods_type_overseas"
                  name="ods_type"
                  checked={!isDomestic}
                  onChange={() => handleODSTypeChange('overseas')}
                  disabled={isSubmitting}
                />
                <div style={{ flex: 1 }}>
                  <div className="option-card-title">
                    <i className="bi bi-globe option-card-icon option-card-icon-green"></i>
                    海外 (hdy_data_sg)
                  </div>
                  <p className="option-card-description">用于海外服务器，使用 hdy_data_sg 数据库</p>
                </div>
              </div>
            </div>
          </div>
          <span className="form-hint">
            <i className="bi bi-info-circle"></i>
            选择ODS数据库类型，用于生成源表路径
          </span>
          {errors.ods_db && <div className="invalid-feedback">{errors.ods_db}</div>}
        </div>

          {/* Action Buttons */}
          <div className="form-actions">
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting}
              loading={isSubmitting}
            >
              {isEdit ? '保存修改' : '创建游戏'}
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

export default React.memo(GameForm);
