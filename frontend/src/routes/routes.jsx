import { lazy } from "react";
import MainLayout from "@analytics/components/layouts/MainLayout";

// Lazy load page components for code splitting
// ============================================================================
// REACT QUERY PAGES (Direct Import - CRITICAL)
// Reason: React Query hooks are incompatible with React.lazy() + Suspense
// Impact: Prevents React Error #321, #310, and removeChild errors
// ============================================================================
import Dashboard from "@analytics/pages/Dashboard";
import CanvasPage from "@features/canvas/pages/CanvasPage";
import EventNodeBuilder from "@event-builder/pages/EventNodeBuilder";
import EventNodes from "@analytics/pages/EventNodes";
import GamesList from "@analytics/pages/GamesList";
import EventsList from "@analytics/pages/EventsList";
import FlowsList from "@analytics/pages/FlowsList";
import GameForm from "@analytics/pages/GameForm";
import EventForm from "@analytics/pages/EventForm";
import CategoriesList from "@analytics/pages/CategoriesList";
import CommonParamsList from "@analytics/pages/CommonParamsList";
import ParametersList from "@analytics/pages/ParametersList";
import HqlManage from "@analytics/pages/HqlManage";
import HqlResults from "@analytics/pages/HqlResults";
import LogForm from "@analytics/pages/LogForm";
import ParameterAnalysis from "@analytics/pages/ParameterAnalysis";
import ParameterCompare from "@analytics/pages/ParameterCompare";
import ParametersEnhanced from "@analytics/pages/ParametersEnhanced";
import EventDetail from "@analytics/pages/EventDetail";

// ============================================================================
// NON-REACT QUERY PAGES (Safe for Lazy Loading)
// Reason: Do not use React Query hooks, safe to lazy load
// Benefit: Reduced initial bundle size
// ============================================================================
const NotFound = lazy(() => import("@analytics/pages/NotFound"));
const HqlEdit = lazy(() => import("@analytics/pages/HqlEdit"));
const FlowBuilder = lazy(() => import("@features/canvas/pages/FlowBuilder"));
const ImportEvents = lazy(() => import("@analytics/pages/ImportEvents"));

// 🔧 FIX: 移除不必要的 lazy loading（修复加载超时问题）
// ApiDocs 和 ValidationRules 都是极简组件（<50行），lazy loading 的收益极小
// 但会导致双重 Suspense 嵌套问题，使页面卡在 "Loading Event2Table..." 状态
import ApiDocs from "@analytics/pages/ApiDocs";
import ValidationRules from "@analytics/pages/ValidationRules";

const BatchOperations = lazy(() => import("@analytics/pages/BatchOperations"));
const LogDetail = lazy(() => import("@analytics/pages/LogDetail"));

// 🔧 FIX: 移除不必要的 lazy loading（修复加载超时问题）
// Parameter 系列页面都是小型组件，lazy loading 会导致双重 Suspense 嵌套问题
import ParameterDashboard from "@analytics/pages/ParameterDashboard";
import ParameterUsage from "@analytics/pages/ParameterUsage";
import ParameterHistory from "@analytics/pages/ParameterHistory";
import ParameterNetwork from "@analytics/pages/ParameterNetwork";

const FieldBuilder = lazy(() => import("@event-builder/pages/FieldBuilder"));
const Generate = lazy(() => import("@analytics/pages/Generate"));
const GenerateResult = lazy(() => import("@analytics/pages/GenerateResult"));
// Direct import for AlterSql (uses fetch/hooks)
import AlterSql from "@analytics/pages/AlterSql";
// Lazy load AlterSqlBuilder (manual tool, no fetch)
const AlterSqlBuilder = lazy(() => import("@analytics/pages/AlterSqlBuilder"));

// Route configuration
// Note: More specific routes must come before general routes
export const routes = [
  {
    element: <MainLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "canvas", element: <CanvasPage /> },
      { path: "event-node-builder", element: <EventNodeBuilder /> },
      { path: "flows", element: <FlowsList /> },
      { path: "games/create", element: <GameForm /> },
      { path: "games/:gid/edit", element: <GameForm /> },
      { path: "games", element: <GamesList /> },
      { path: "categories", element: <CategoriesList /> },
      { path: "events/create", element: <EventForm /> },
      { path: "events/:id", element: <EventDetail /> },
      { path: "events/:id/edit", element: <EventForm /> },
      { path: "events", element: <EventsList /> },
      { path: "common-params", element: <CommonParamsList /> },
      { path: "parameters", element: <ParametersList /> },
      { path: "hql-manage", element: <HqlManage /> },
      { path: "import-events", element: <ImportEvents /> },
      { path: "api-docs", element: <ApiDocs /> },
      { path: "batch-operations", element: <BatchOperations /> },
      { path: "log-detail", element: <LogDetail /> },
      { path: "validation-rules", element: <ValidationRules /> },
      { path: "parameter-dashboard", element: <ParameterDashboard /> },
      { path: "parameter-usage", element: <ParameterUsage /> },
      { path: "parameter-history", element: <ParameterHistory /> },
      { path: "logs/create", element: <LogForm /> },
      { path: "logs/:id/edit", element: <LogForm /> },
      { path: "parameters/compare", element: <ParameterCompare /> },
      { path: "hql/:id/edit", element: <HqlEdit /> },
      { path: "flow-builder", element: <FlowBuilder /> },
      { path: "field-builder", element: <FieldBuilder /> },
      { path: "event-nodes", element: <EventNodes /> },
      { path: "generate", element: <Generate /> },
      { path: "generate/result", element: <GenerateResult /> },
      { path: "hql-results", element: <HqlResults /> },
      { path: "alter-sql/:paramId", element: <AlterSql /> },
      { path: "alter-sql-builder", element: <AlterSqlBuilder /> },
      { path: "parameter-analysis", element: <ParameterAnalysis /> },
      { path: "parameter-network", element: <ParameterNetwork /> },
      { path: "parameters/enhanced", element: <ParametersEnhanced /> },
      { path: "*", element: <NotFound /> }, // Catch-all 404 route
    ],
  },
];
