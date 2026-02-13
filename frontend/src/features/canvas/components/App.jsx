import React, { useState } from "react";
import { ReactFlowProvider } from "reactflow";
import CanvasFlow from "./CanvasFlow";
import "./App.css";

function App() {
  const [gameData] = useState({
    id: window.gameData?.id || 8,
    gid: window.gameData?.gid || 10000147,
    name: window.gameData?.name || "测试游戏",
    ods_db: window.gameData?.ods_db || "ieu_ods",
  });

  return (
    <ReactFlowProvider>
      <div className="app">
        {/* Header removed - using base.html header instead */}
        <main className="app-main" style={{ height: "100vh" }}>
          <CanvasFlow gameData={gameData} />
        </main>
      </div>
    </ReactFlowProvider>
  );
}

export default App;
