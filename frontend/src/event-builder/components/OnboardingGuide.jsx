/**
 * OnboardingGuide Component
 * 首次访问引导组件 - 显示快速上手指南
 */
import React, { useEffect, useState, useCallback } from "react";
import PropTypes from "prop-types";
import "./OnboardingGuide.css";

const GUIDE_STORAGE_KEY = "event-builder-guide-seen";
const GUIDE_DISMISSED_KEY = "event-builder-guide-dismissed";

export default function OnboardingGuide({ onComplete }) {
  const [showGuide, setShowGuide] = useState(false);

  useEffect(() => {
    // Check if user has seen the guide
    const hasSeenGuide = localStorage.getItem(GUIDE_STORAGE_KEY);
    const hasDismissed = localStorage.getItem(GUIDE_DISMISSED_KEY);

    if (!hasSeenGuide && !hasDismissed) {
      // Delay showing guide to let page settle
      const timer = setTimeout(() => {
        setShowGuide(true);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleDismiss = useCallback(() => {
    localStorage.setItem(GUIDE_DISMISSED_KEY, "true");
    setShowGuide(false);
    onComplete?.();
  }, [onComplete]);

  const handleComplete = useCallback(() => {
    localStorage.setItem(GUIDE_STORAGE_KEY, "true");
    setShowGuide(false);
    onComplete?.();
  }, [onComplete]);

  if (!showGuide) return null;

  return (
    <div className="onboarding-guide-overlay" onClick={handleDismiss}>
      <div className="onboarding-guide" onClick={(e) => e.stopPropagation()}>
        <div className="guide-header">
          <h2>
            <i className="bi bi-lightbulb"></i>
            欢迎使用事件节点构建器
          </h2>
          <button
            className="btn-close-guide"
            onClick={handleDismiss}
            title="不再显示"
          >
            <i className="bi bi-x"></i>
          </button>
        </div>

        <div className="guide-content">
          <p className="guide-intro">快速上手指南：</p>

          <div className="guide-section">
            <div className="guide-item">
              <span className="guide-icon">🖱️</span>
              <div className="guide-text">
                <strong>鼠标移到底部边缘</strong>
                <p>工具栏会自动滑入</p>
              </div>
            </div>
          </div>

          <div className="guide-section">
            <div className="guide-item">
              <span className="guide-icon">⚡</span>
              <div className="guide-text">
                <strong>快速添加常用字段</strong>
                <p>点击"快速"按钮，一键添加常用字段</p>
              </div>
            </div>
          </div>

          <div className="guide-section">
            <div className="guide-item">
              <span className="guide-icon">🖱️</span>
              <div className="guide-text">
                <strong>右键显示更多选项</strong>
                <p>在画布空白处右键显示上下文菜单</p>
              </div>
            </div>
          </div>

          <div className="guide-section">
            <div className="guide-item">
              <span className="guide-icon">⌨️</span>
              <div className="guide-text">
                <strong>快捷键支持</strong>
                <p>Cmd+N 添加字段 | Cmd+Shift+B 常用字段</p>
              </div>
            </div>
          </div>
        </div>

        <div className="guide-footer">
          <button className="btn-guide-secondary" onClick={handleDismiss}>
            稍后再看
          </button>
          <button className="btn-guide-primary" onClick={handleComplete}>
            我知道了
          </button>
        </div>
      </div>
    </div>
  );
}

OnboardingGuide.propTypes = {
  onComplete: PropTypes.func,
};
