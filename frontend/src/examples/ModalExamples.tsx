/**
 * Modal Component Examples
 * 
 * 展示 Modal 组件的各种用法
 */

import React, { useState } from 'react';
import { Modal, Button, Input } from '@shared/ui';

export function ModalBasicExample() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="example-section">
      <h3>基础用法</h3>
      <Button onClick={() => setIsOpen(true)}>打开对话框</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="基础对话框"
      >
        <p>这是一个基础的模态对话框示例。</p>
        <p>点击遮罩层或关闭按钮可以关闭对话框。</p>
      </Modal>
    </div>
  );
}

export function ModalSizeExample() {
  const [smallOpen, setSmallOpen] = useState(false);
  const [mediumOpen, setMediumOpen] = useState(false);
  const [largeOpen, setLargeOpen] = useState(false);

  return (
    <div className="example-section">
      <h3>不同尺寸</h3>
      <div className="button-group">
        <Button onClick={() => setSmallOpen(true)}>小尺寸</Button>
        <Button onClick={() => setMediumOpen(true)}>中尺寸</Button>
        <Button onClick={() => setLargeOpen(true)}>大尺寸</Button>
      </div>

      <Modal
        isOpen={smallOpen}
        onClose={() => setSmallOpen(false)}
        title="小尺寸对话框"
        size="sm"
      >
        <p>这是一个小尺寸的对话框。</p>
      </Modal>

      <Modal
        isOpen={mediumOpen}
        onClose={() => setMediumOpen(false)}
        title="中尺寸对话框"
        size="md"
      >
        <p>这是一个中尺寸的对话框，适用于大多数场景。</p>
      </Modal>

      <Modal
        isOpen={largeOpen}
        onClose={() => setLargeOpen(false)}
        title="大尺寸对话框"
        size="lg"
      >
        <p>这是一个大尺寸的对话框，适合展示大量内容。</p>
      </Modal>
    </div>
  );
}

export function ModalFullScreenExample() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="example-section">
      <h3>全屏对话框</h3>
      <Button onClick={() => setIsOpen(true)}>打开全屏对话框</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="全屏对话框"
        fullScreen
      >
        <p>这是一个全屏对话框，适合编辑复杂表单或展示大量内容。</p>
      </Modal>
    </div>
  );
}

export function ModalAnimationExample() {
  const [slideUpOpen, setSlideUpOpen] = useState(false);
  const [fadeInOpen, setFadeInOpen] = useState(false);
  const [zoomOpen, setZoomOpen] = useState(false);

  return (
    <div className="example-section">
      <h3>不同动画效果</h3>
      <div className="button-group">
        <Button onClick={() => setSlideUpOpen(true)}>滑入动画</Button>
        <Button onClick={() => setFadeInOpen(true)}>淡入动画</Button>
        <Button onClick={() => setZoomOpen(true)}>缩放动画</Button>
      </div>

      <Modal
        isOpen={slideUpOpen}
        onClose={() => setSlideUpOpen(false)}
        title="滑入动画"
        animation="slideUp"
      >
        <p>对话框从下方滑入。</p>
      </Modal>

      <Modal
        isOpen={fadeInOpen}
        onClose={() => setFadeInOpen(false)}
        title="淡入动画"
        animation="fadeIn"
      >
        <p>对话框淡入显示。</p>
      </Modal>

      <Modal
        isOpen={zoomOpen}
        onClose={() => setZoomOpen(false)}
        title="缩放动画"
        animation="scale"
      >
        <p>对话框缩放显示。</p>
      </Modal>
    </div>
  );
}

export function ModalFormExample() {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '' });

  const handleSubmit = () => {
    console.log('表单提交:', formData);
    setIsOpen(false);
  };

  return (
    <div className="example-section">
      <h3>表单对话框</h3>
      <Button onClick={() => setIsOpen(true)}>打开表单</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="用户信息"
        size="md"
        showFooter
        footer={
          <div className="modal-footer-actions">
            <Button variant="ghost" onClick={() => setIsOpen(false)}>
              取消
            </Button>
            <Button variant="primary" onClick={handleSubmit}>
              提交
            </Button>
          </div>
        }
      >
        <div className="modal-form">
          <Input
            type="text"
            label="姓名"
            placeholder="请输入姓名"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <Input
            type="email"
            label="邮箱"
            placeholder="请输入邮箱"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>
      </Modal>
    </div>
  );
}

export function ModalConfirmExample() {
  const [isOpen, setIsOpen] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  return (
    <div className="example-section">
      <h3>确认对话框</h3>
      <div className="button-group">
        <Button onClick={() => setIsOpen(true)}>打开对话框</Button>
        <Button onClick={() => setHasUnsavedChanges(!hasUnsavedChanges)}>
          {hasUnsavedChanges ? '有未保存更改' : '无未保存更改'}
        </Button>
      </div>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="编辑内容"
        onBeforeClose={async () => {
          if (hasUnsavedChanges) {
            return false; // 显示确认对话框
          }
          return true; // 直接关闭
        }}
        confirmConfig={{
          title: '确认关闭',
          message: '您有未保存的更改，确定要关闭吗？',
          confirmText: '放弃更改',
          cancelText: '继续编辑',
        }}
      >
        <p>编辑一些内容...</p>
        {hasUnsavedChanges && (
          <p style={{ color: 'orange' }}>⚠️ 您有未保存的更改</p>
        )}
      </Modal>
    </div>
  );
}

export function ModalDraggableExample() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="example-section">
      <h3>可拖拽对话框</h3>
      <Button onClick={() => setIsOpen(true)}>打开可拖拽对话框</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="可拖拽对话框"
        draggable={true}
      >
        <p>拖拽标题栏可以移动对话框位置。</p>
        <p>这个功能对于需要同时查看多个对话框的场景很有用。</p>
      </Modal>
    </div>
  );
}

export function ModalNestedExample() {
  const [parentOpen, setParentOpen] = useState(false);
  const [childOpen, setChildOpen] = useState(false);

  return (
    <div className="example-section">
      <h3>嵌套对话框</h3>
      <Button onClick={() => setParentOpen(true)}>打开父对话框</Button>
      
      <Modal
        isOpen={parentOpen}
        onClose={() => setParentOpen(false)}
        title="父对话框"
      >
        <p>这是父对话框的内容。</p>
        <Button onClick={() => setChildOpen(true)}>打开子对话框</Button>
        
        <Modal
          isOpen={childOpen}
          onClose={() => setChildOpen(false)}
          title="子对话框"
        >
          <p>这是子对话框的内容。</p>
          <p>子对话框的 z-index 会高于父对话框。</p>
        </Modal>
      </Modal>
    </div>
  );
}

export function ModalCustomHeaderExample() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="example-section">
      <h3>自定义头部</h3>
      <Button onClick={() => setIsOpen(true)}>打开对话框</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="自定义头部"
        showHeader={true}
      >
        <p>对话框带有标准的头部，包含标题和关闭按钮。</p>
      </Modal>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        showHeader={false}
      >
        <div style={{ padding: '20px' }}>
          <h3>无头部对话框</h3>
          <p>这个对话框没有头部，适合简单的提示或确认场景。</p>
          <Button onClick={() => setIsOpen(false)}>关闭</Button>
        </div>
      </Modal>
    </div>
  );
}

export function ModalBestPractices() {
  return (
    <div className="example-section">
      <h3>最佳实践</h3>
      <div className="best-practices">
        <div className="practice-item">
          <h4>1. 为对话框提供清晰的标题</h4>
          <Button onClick={() => {}}>示例</Button>
        </div>
        <div className="practice-item">
          <h4>2. 表单对话框提供明确的操作按钮</h4>
          <Button onClick={() => {}}>打开表单</Button>
        </div>
        <div className="practice-item">
          <h4>3. 有未保存更改时显示确认对话框</h4>
          <Button onClick={() => {}}>编辑内容</Button>
        </div>
        <div className="practice-item">
          <h4>4. 根据内容选择合适的尺寸</h4>
          <div className="button-group">
            <Button onClick={() => {}}>小</Button>
            <Button onClick={() => {}}>中</Button>
            <Button onClick={() => {}}>大</Button>
          </div>
        </div>
        <div className="practice-item">
          <h4>5. 复杂内容使用全屏对话框</h4>
          <Button onClick={() => {}}>全屏</Button>
        </div>
      </div>
    </div>
  );
}

export default function ModalExamples() {
  return (
    <div className="examples-container">
      <h2>Modal 组件示例</h2>
      <ModalBasicExample />
      <ModalSizeExample />
      <ModalFullScreenExample />
      <ModalAnimationExample />
      <ModalFormExample />
      <ModalConfirmExample />
      <ModalDraggableExample />
      <ModalNestedExample />
      <ModalCustomHeaderExample />
      <ModalBestPractices />
    </div>
  );
}
