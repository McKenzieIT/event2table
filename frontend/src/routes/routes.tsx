import type { RouteObject } from "react-router-dom";
import MainLayout from "@analytics/components/layouts/MainLayout";

// ============================================================================
// ALL PAGES - Direct Import (FIX: Playwright test timeout issue)
// Reason: Removing all lazy loading to eliminate double Suspense nesting issues
// Impact: Slightly larger initial bundle, but pages load reliably
// ============================================================================
import Dashboard from "@analytics/pages/DashboardGraphQL";
import CanvasPage from "@features/canvas/pages/CanvasPage";
import EventNodeBuilder from "@event-builder/pages/EventNodeBuilder";
import EventNodes from "@analytics/pages/EventNodes";
import EventsList from "@analytics/pages/EventsListGraphQL";
import FlowsList from "@analytics/pages/FlowsList";
import GamesList from "@analytics/pages/GamesListGraphQL";
import EventForm from "@analytics/pages/EventForm";
import CategoriesList from "@analytics/pages/CategoriesListGraphQL";
import CommonParamsList from "@analytics/pages/CommonParamsList";
import ParametersList from "@analytics/pages/ParametersList";
import HqlManage from "@analytics/pages/HqlManage";
import HqlResults from "@analytics/pages/HqlResults";
import LogForm from "@analytics/pages/LogForm";
import ParameterAnalysis from "@analytics/pages/ParameterAnalysis";
import ParameterCompare from "@analytics/pages/ParameterCompare";
import ParametersEnhanced from "@analytics/pages/ParametersEnhancedGraphQL";
import EventDetail from "@analytics/pages/EventDetailGraphQL";

// Previously lazy-loaded components - now direct imports
import NotFound from "@analytics/pages/NotFound";
import HqlEdit from "@analytics/pages/HqlEdit";
import FlowBuilder from "@features/canvas/pages/FlowBuilder";
import ImportEvents from "@analytics/pages/ImportEvents";
import ApiDocs from "@analytics/pages/ApiDocs";
import ValidationRules from "@analytics/pages/ValidationRules";
import BatchOperations from "@analytics/pages/BatchOperations";
import LogDetail from "@analytics/pages/LogDetail";
import ParameterDashboard from "@analytics/pages/ParameterDashboard";
import ParameterUsage from "@analytics/pages/ParameterUsage";
import ParameterHistory from "@analytics/pages/ParameterHistory";
import ParameterNetwork from "@analytics/pages/ParameterNetwork";
import FieldBuilder from "@event-builder/pages/FieldBuilder";
import Generate from "@analytics/pages/Generate";
import GenerateResult from "@analytics/pages/GenerateResult";
import AlterSql from "@analytics/pages/AlterSql";
import { TaskManagementPage } from "@features/async-tasks/pages/TaskManagementPage";
import { PerformancePage } from "@features/monitoring/pages/PerformancePage";
// import AlterSqlBuilder from "@analytics/pages/AlterSqlBuilder";  // Temporarily disabled for debugging

// Route configuration
// Note: More specific routes must come before general routes
export const routes: RouteObject[] = [
  {
    element: <MainLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "canvas", element: <CanvasPage /> },
      { path: "event-node-builder", element: <EventNodeBuilder /> },
      { path: "flows", element: <FlowsList /> },
      { path: "games", element: <GamesList /> },
      { path: "categories", element: <CategoriesList /> },
      { path: "events/create", element: <EventForm /> },
      { path: "events/:id", element: <EventDetail /> },
      { path: "events/:id/edit", element: <EventForm /> },
      { path: "events", element: <EventsList /> },
      { path: "common-params", element: <CommonParamsList /> },
      // More specific parameter routes must come before general "parameters" route
      { path: "parameters/dashboard", element: <ParameterDashboard /> },
      { path: "parameters/compare", element: <ParameterCompare /> },
      { path: "parameters/enhanced", element: <ParametersEnhanced /> },
      { path: "parameters", element: <ParametersList /> },
      { path: "hql-manage", element: <HqlManage /> },
      { path: "import-events", element: <ImportEvents /> },
      { path: "api-docs", element: <ApiDocs /> },
      { path: "batch-operations", element: <BatchOperations /> },
      { path: "log-detail", element: <LogDetail /> },
      { path: "validation-rules", element: <ValidationRules /> },
      // Legacy root-level parameter-dashboard route (kept for backward compatibility)
      { path: "parameter-dashboard", element: <ParameterDashboard /> },
      { path: "parameter-usage", element: <ParameterUsage /> },
      { path: "parameter-history", element: <ParameterHistory /> },
      { path: "logs/create", element: <LogForm /> },
      { path: "logs/:id/edit", element: <LogForm /> },
      { path: "hql/:id/edit", element: <HqlEdit /> },
      { path: "flow-builder", element: <FlowBuilder /> },
      { path: "field-builder", element: <FieldBuilder /> },
      { path: "event-nodes", element: <EventNodes /> },
      { path: "generate", element: <Generate /> },
      { path: "generate/result", element: <GenerateResult /> },
      { path: "hql-results", element: <HqlResults /> },
      { path: "alter-sql/:paramId", element: <AlterSql /> },
      { path: "async-tasks", element: <TaskManagementPage /> },
      { path: "performance", element: <PerformancePage /> },
      // { path: "alter-sql-builder", element: <AlterSqlBuilder /> },  // Temporarily disabled for debugging
      { path: "parameter-analysis", element: <ParameterAnalysis /> },
      { path: "parameter-network", element: <ParameterNetwork /> },
      { path: "*", element: <NotFound /> }, // Catch-all 404 route
    ],
  },
];