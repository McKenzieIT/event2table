import React, { useState } from "react";
import { ReactFlowProvider } from "reactflow";
import CanvasFlow from "./CanvasFlow";
import "./App.css";
import type { AppProps, GameData } from "./types";

function App(): React.JSX.Element {
  const [gameData] = useState<GameData>({
    id: (window as any).gameData?.id || 8,
    gid: (window as any).gameData?.gid || 10000147,
    name: (window as any).gameData?.name || "测试游戏",
    ods_db: (window as any).gameData?.ods_db || "ieu_ods",
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
