import React, { useState, useRef, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Card, useToast } from "@shared/ui";
import { useGameContext } from "@shared/hooks/useGameContext";
import { ImportPreviewModal } from "../components/ImportPreviewModal";
import "./ImportEvents.css";

/**
 * 导入事件页面
 * 迁移自: templates/import_events.html
 *
 * 支持参数库匹配预览功能
 */
function ImportEvents() {
  const [file, setFile] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [parameters, setParameters] = useState([]);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const { success, error } = useToast();
  const { currentGameGid } = useGameContext();

  // 使用 useCallback 优化事件处理
  const handleFileChange = useCallback((e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  }, []);

  const handlePreview = useCallback(async () => {
    if (!file) {
      error("请先选择文件");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("header_row", 0);
    formData.append("data_start_row", 1);
    formData.append("preview_rows", 10);

    try {
      const response = await fetch("/api/preview-excel", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        // 转换后端数据格式为组件所需的格式
        const eventData = result.data.rows || [];
        const parameters = eventData.map((row, index) => ({
          param_name: row[0] || `param_${index}`,
          template_id: row[3] || 1,
          libraryParam: result.data.suggested_mappings?.[row[0]]
            ? { id: index, param_name: row[0], usage_count: 0 }
            : null,
        }));

        setParameters(parameters);
        setShowPreview(true);
        success(`成功解析 ${parameters.length} 个参数`);
      } else {
        error(result.error || "预览失败");
      }
    } catch (err) {
      console.error("Preview error:", err);
      error(
        `预览失败: ${err instanceof Error ? err.message : "未知错误"}`,
      );
    }
  }, [file, success, error]);

  const handleConfirm = useCallback(async (selectedMatches) => {
    if (!file) {
      error("请先选择文件");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Priority: useGameContext > localStorage
    const gameGid = currentGameGid || localStorage.getItem("selectedGameGid") || "10000147";
    formData.append("game_gid", gameGid);

    try {
      const response = await fetch("/api/events/import", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        const importedCount =
          result.data?.imported_count || selectedMatches.size;
        success(`成功导入 ${importedCount} 个事件`);
        setShowPreview(false);
        // 重置表单
        setFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        // 跳转到事件列表页
        navigate("/events");
      } else {
        error(result.error || "导入失败");
      }
    } catch (err) {
      console.error("Import error:", err);
      error(
        `导入失败: ${err instanceof Error ? err.message : "未知错误"}`,
      );
    }
  }, [file, error, success]);

  const handleCancel = useCallback(() => {
    setShowPreview(false);
  }, []);

  return (
    <div className="import-events-container">
      <Card className="page-header glass-card">
        <Card.Body>
          <div className="header-content">
            <div className="icon-box">
              <span>📤</span>
            </div>
            <div>
              <h1>导入事件</h1>
              <p>批量导入事件配置</p>
            </div>
          </div>
          <Link to="/events">
            <Button variant="ghost">返回</Button>
          </Link>
        </Card.Body>
      </Card>

      <Card className="upload-card glass-card">
        <Card.Body>
          <h2>选择Excel文件</h2>
          <div className="upload-area">
            <span>📊</span>
            <p>拖拽Excel文件到此处，或点击选择文件</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
            />
          </div>
          {file && <div className="selected-file">已选择: {file.name}</div>}
          <div className="button-group">
            <Button variant="secondary" onClick={handlePreview} disabled={!file}>
              预览匹配
            </Button>
            <Button variant="primary" disabled={!file}>
              开始导入
            </Button>
          </div>
        </Card.Body>
      </Card>

      {showPreview && (
        <ImportPreviewModal
          parameters={parameters}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
}

export default React.memo(ImportEvents);
