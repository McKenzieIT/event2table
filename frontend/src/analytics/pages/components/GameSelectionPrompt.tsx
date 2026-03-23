import { Button } from "@shared/ui";
import React from "react";
import { Link } from "react-router-dom";

/**
 * 游戏选择提示组件
 * 当用户未选择游戏时显示，引导用户前往游戏管理页面
 */
function GameSelectionPrompt() {
  return (
    <div className="glass-card text-center p-5 m-4">
      <i className="bi bi-controller display-4 text-primary mb-3 d-block"></i>
      <h3 className="mb-3">请先选择游戏</h3>
      <p className="text-muted mb-4">事件节点管理需要先选择一个游戏</p>
      <Link to="/games">
        <Button variant="primary">
          前往游戏管理
        </Button>
      </Link>
    </div>
  );
}

export default React.memo(GameSelectionPrompt);
