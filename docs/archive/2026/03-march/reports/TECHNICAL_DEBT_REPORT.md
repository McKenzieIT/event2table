# Technical Debt Report

**Generated**: 2026-02-25

## Summary
- **Total Debt Items**: 3337
- **Critical**: 0
- **High**: 0
- **Medium**: 30
- **Low**: 3307

## Migration Impact
- **REST API Usage**: 18 files
- **GraphQL Usage**: 6 files
- **Mixed Usage**: 24 files

## Critical Issues

## High Priority Issues

## REST API Dependencies
- games: 4 usages
- _hql_helpers: 2 usages
- hql_preview_v2: 2 usages
- _param_helpers: 1 usages
- cache: 1 usages
- events: 1 usages

## GraphQL Dependencies
- types: 52 usages
- queries: 9 usages
- mutations: 9 usages
- schema: 7 usages
- resolvers: 7 usages
- middleware: 4 usages
- dataloaders: 2 usages
- schema_parameter_management: 2 usages

## Mixed Usage Files (Potential Refactoring Needed)
- frontend/src/analytics/pages/CategoryForm.jsx
- frontend/src/analytics/pages/ParametersEnhanced.jsx
- frontend/src/analytics/pages/HqlManage.jsx
- frontend/src/analytics/pages/CategoriesList.jsx
- frontend/src/analytics/pages/EventDetail.jsx
- frontend/src/analytics/pages/CommonParamsList.jsx
- frontend/src/analytics/pages/FlowsList.jsx
- frontend/src/analytics/pages/EventsList.jsx
- frontend/src/analytics/pages/Dashboard.jsx
- frontend/src/analytics/pages/HqlResults.jsx