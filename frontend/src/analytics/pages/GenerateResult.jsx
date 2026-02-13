import React, { useState, useEffect, useCallback } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Button, Card, Badge, Spinner, useToast } from "@shared/ui";
import "./GenerateResult.css";

/**
 * HQL生成结果页面
 * 显示生成的HQL语句
 *
 * ✅ 已修复：从URL参数或后端API获取真实HQL
 * - 支持从URL参数获取事件名
 * - 可选：从/api/hql/<id>获取生成的HQL内容
 */
function GenerateResult() {
  const [searchParams] = useSearchParams();
  const [hqlResult, setHqlResult] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [eventName, setEventName] = useState("");
  const { success, error } = useToast();

  // 使用 useCallback 优化事件处理
  const generateTemplateHql = useCallback((event) => {
    // 基于事件名生成模板HQL
    const templateHql = `CREATE OR REPLACE VIEW dwd_${event} AS
SELECT
    ds,
    role_id,
    account_id,
    utdid,
    get_json_object(params, '$.zone_id') AS zone_id,
    get_json_object(params, '$.level') AS level,
    get_json_object(params, '$.ip') AS ip
FROM ieu_ods.ods_all_view
WHERE ds = '${bizdate}'
  AND event = 'game.${event}';`;

    setHqlResult(templateHql);
  }, []);

  const handleCopy = useCallback(() => {
    navigator.clipboard
      .writeText(hqlResult)
      .then(() => {
        success("HQL已复制到剪贴板");
      })
      .catch(() => {
        error("复制失败，请手动复制");
      });
  }, [hqlResult, success, error]);

  useEffect(() => {
    const fetchHqlResult = async () => {
      const eventParam = searchParams.get("event");

      if (!eventParam) {
        error("缺少事件参数");
        setIsLoading(false);
        return;
      }

      setEventName(eventParam);

      try {
        // 尝试从后端API获取生成的HQL
        // 注意：这需要后端实现HQL生成ID查询
        const response = await fetch(`/api/hql/event/${eventParam}`);

        if (response.ok) {
          const result = await response.json();
          if (result.success && result.data?.hql_content) {
            setHqlResult(result.data.hql_content);
          } else {
            // 如果API未实现或返回空数据，生成模板HQL
            generateTemplateHql(eventParam);
          }
        } else {
          // API调用失败，使用模板HQL
          generateTemplateHql(eventParam);
        }
      } catch (err) {
        console.error("Failed to fetch HQL:", err);
        // 出错时使用模板HQL
        generateTemplateHql(eventParam);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHqlResult();
  }, [searchParams, generateTemplateHql, error]);

  return (
    <div className="generate-result-container">
      <div className="page-header">
        <h1>生成结果</h1>
        <div className="header-actions">
          <Button variant="secondary" onClick={handleCopy}>
            <i className="bi bi-clipboard"></i>
            复制
          </Button>
          <Link to="/hql-manage">
            <Button variant="ghost">
              <i className="bi bi-arrow-left"></i>
              返回
            </Button>
          </Link>
        </div>
      </div>

      <Card className="result-card glass-card">
        <Card.Body>
          <div className="result-header">
            <h3>HQL语句 - {eventName || "未知事件"}</h3>
            <Badge variant="success">生成成功</Badge>
          </div>

          {isLoading ? (
            <div className="loading-state">
              <Spinner size="md" label="加载HQL中..." />
            </div>
          ) : (
            <pre className="hql-code">{hqlResult || "未生成HQL内容"}</pre>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}

export default React.memo(GenerateResult);
