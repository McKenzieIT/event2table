/**
 * 快速编辑模态框组件
 * Quick Edit Modal Component
 *
 * @description 快速编辑事件节点的基本信息（名称、描述）
 */

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { eventNodesApi } from "@shared/api/eventNodes";
import type { EventNode } from "@shared/types/eventNodes";
import { BaseModal } from "@shared/ui/BaseModal";
import { Button } from "@shared/ui/Button";

/**
 * Zod验证schema
 */
const schema = z.object({
  name_en: z
    .string()
    .min(1, "英文名称不能为空")
    .regex(/^[a-z0-9_]+$/, "只能包含小写字母、数字和下划线"),
  name_cn: z.string().min(1, "中文名称不能为空").max(200, "最多200字符"),
  description: z.string().max(500, "描述最多500字符").optional(),
});

/**
 * 表单数据类型
 */
type FormData = z.infer<typeof schema>;

/**
 * Props接口
 */
interface QuickEditModalProps {
  show: boolean;
  nodeId: number | null;
  nodes: EventNode[];
  onClose: () => void;
  onUpdate: () => void;
}

/**
 * 快速编辑模态框组件
 */
export function QuickEditModal({
  show,
  nodeId,
  nodes,
  onClose,
  onUpdate,
}: QuickEditModalProps) {
  const [loading, setLoading] = useState(false);

  // Toast 辅助函数
  const success = (message: string) => toast.success(message);
  const error = (message: string) => toast.error(message);

  // 查找当前节点
  const currentNode = nodes.find((n) => n.id === nodeId);

  // React Hook Form
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty, dirtyFields },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name_en: "",
      name_cn: "",
      description: "",
    },
  });

  // 重置表单当节点改变或模态框关闭
  useEffect(() => {
    if (currentNode) {
      reset({
        name_en: currentNode.name_en || "", // ✅ 使用正确的字段名
        name_cn: currentNode.name_cn || "",
        description: currentNode.description || "",
      });
    }
  }, [currentNode, reset]);

  // 提交表单
  const onSubmit = async (data: FormData) => {
    if (!nodeId) return;

    setLoading(true);
    try {
      // 使用快速更新 API，发送正确的字段名
      await eventNodesApi.quickUpdate(nodeId, {
        name_en: data.name_en || undefined, // 英文名称可选
        name_cn: data.name_cn, // 中文名称必填
        description: data.description,
      });
      success("节点更新成功");
      onUpdate();
      onClose();
    } catch (err) {
      console.error("Failed to update node:", err);
      error("更新失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  if (!show || !currentNode) {
    return null;
  }

  // 关闭前确认逻辑
  const handleBeforeClose = () => {
    // 如果表单有修改，返回false显示确认对话框
    if (isDirty) {
      return false;
    }
    // 没有修改，直接关闭
    return true;
  };

  return (
    <BaseModal
      isOpen={show}
      onClose={onClose}
      enableEscClose={true}
      onBeforeClose={handleBeforeClose}
      confirmConfig={{
        title: "确认关闭",
        message: "有未保存的修改，确定要关闭吗？",
        confirmText: "放弃修改",
        cancelText: "继续编辑",
      }}
    >
      <div
        className={`modal fade ${show ? "show" : ""}`}
        style={{
          display: "block",
          backgroundColor: "transparent",
        }}
        tabIndex={-1}
        role="dialog"
        aria-labelledby="quickEditModalLabel"
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            {/* 模态框头部 */}
            <div className="modal-header">
              <h5 className="modal-title" id="quickEditModalLabel">
                <i className="bi bi-pencil text-warning me-2"></i>
                快速编辑节点
              </h5>
              <button
                type="button"
                className="btn-close"
                onClick={onClose}
                aria-label="关闭"
              ></button>
            </div>

            {/* 模态框内容 - 表单 */}
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="modal-body">
                {/* 节点ID（只读） */}
                <div className="mb-3">
                  <label className="form-label text-muted">节点ID</label>
                  <input
                    type="text"
                    className="form-control"
                    value={currentNode.id}
                    disabled
                    style={{ backgroundColor: "#f8f9fa" }}
                  />
                </div>

                {/* 英文名称 */}
                <div className="mb-3">
                  <label htmlFor="name_en" className="form-label">
                    节点名称（英文） <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.name_en ? "is-invalid" : ""}`}
                    id="name_en"
                    {...register("name_en")}
                    placeholder="例如: user_login"
                  />
                  {errors.name_en && (
                    <div className="invalid-feedback">
                      {errors.name_en.message}
                    </div>
                  )}
                  <div className="form-text">
                    只能包含小写字母、数字和下划线
                  </div>
                </div>

                {/* 中文名称 */}
                <div className="mb-3">
                  <label htmlFor="name_cn" className="form-label">
                    节点名称（中文） <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.name_cn ? "is-invalid" : ""}`}
                    id="name_cn"
                    {...register("name_cn")}
                    placeholder="例如: 用户登录"
                  />
                  {errors.name_cn && (
                    <div className="invalid-feedback">
                      {errors.name_cn.message}
                    </div>
                  )}
                </div>

                {/* 描述 */}
                <div className="mb-3">
                  <label htmlFor="description" className="form-label">
                    描述
                  </label>
                  <textarea
                    className={`form-control ${errors.description ? "is-invalid" : ""}`}
                    id="description"
                    rows={4}
                    {...register("description")}
                    placeholder="简要描述该节点的用途..."
                  ></textarea>
                  {errors.description && (
                    <div className="invalid-feedback">
                      {errors.description.message}
                    </div>
                  )}
                  <div className="form-text">{`${(register("description").value || "").length}/500`}</div>
                </div>

                {/* 变更警告 */}
                {dirtyFields.name_en && (
                  <div className="alert alert-warning">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    <strong>警告：</strong>
                    修改英文名称可能会影响HQL生成和其他依赖此名称的功能。
                  </div>
                )}
              </div>

              {/* 模态框底部 */}
              <div className="modal-footer">
                <Button
                  variant="secondary"
                  onClick={onClose}
                  disabled={loading}
                >
                  取消
                </Button>
                <Button
                  variant="primary"
                  type="submit"
                  disabled={loading || !isDirty}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      保存中...
                    </>
                  ) : (
                    保存
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </BaseModal>
  );
}
