/**
 * BindToLibraryButton 组件 - 绑定到库按钮
 *
 * 为未绑定参数库的参数提供绑定按钮
 * 点击按钮打开 BindToLibraryModal 进行选择
 *
 * @example
 * <BindToLibraryButton
 *   paramId={123}
 *   paramName="accountId"
 *   templateId={1}
 * />
 *
 * Props:
 * @param {number} paramId - 参数ID
 * @param {string} paramName - 参数名
 * @param {number} templateId - 类型ID
 */

import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { BindToLibraryModal } from './BindToLibraryModal';

export function BindToLibraryButton({ paramId, paramName, templateId }) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <Button
        variant="outline-primary"
        size="sm"
        onClick={() => setShowModal(true)}
      >
        绑定到库
      </Button>
      {showModal && (
        <BindToLibraryModal
          paramId={paramId}
          paramName={paramName}
          templateId={templateId}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}
