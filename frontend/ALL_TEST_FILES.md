# 前端测试文件清单

**统计时间**: 2026-03-21  
**总文件数**: 100个  
**分批策略**: 34个轮次，每轮次3个subagent并行测试

---

## 测试文件列表（按轮次分组）

### 轮次1 (文件 1-3)
1. `frontend/src/__tests__/graphql/hooks.test.tsx`
2. `frontend/src/__tests__/graphql/integration.test.tsx`
3. `frontend/src/__tests__/performance/ReactPerformance.test.tsx`

### 轮次2 (文件 4-6)
4. `frontend/src/analytics/components/categories/CategoryManagementModal.test.tsx`
5. `frontend/src/analytics/pages/__tests__/DashboardGraphQL.test.tsx`
6. `frontend/src/analytics/pages/__tests__/EventsListGraphQL.performance.test.tsx`

### 轮次3 (文件 7-9)
7. `frontend/src/analytics/pages/__tests__/EventsListGraphQL.test.tsx`
8. `frontend/src/analytics/pages/__tests__/GamesListGraphQL.performance.test.tsx`
9. `frontend/src/analytics/pages/__tests__/ParametersListGraphQL.debug.test.tsx`

### 轮次4 (文件 10-12)
10. `frontend/src/analytics/pages/__tests__/ParametersListGraphQL.simple.test.tsx`
11. `frontend/src/analytics/pages/__tests__/ParametersListGraphQL.test.tsx`
12. `frontend/src/analytics/pages/__tests__/ParametersListGraphQL.VirtualList.simple.test.tsx`

### 轮次5 (文件 13-15)
13. `frontend/src/analytics/pages/__tests__/ParametersListGraphQL.VirtualList.test.tsx`
14. `frontend/src/event-builder/__tests__/components/ParamSelector.test.tsx`
15. `frontend/src/event-builder/components/modals/__tests__/NodeConfigModal.test.tsx`

### 轮次6 (文件 16-18)
16. `frontend/src/event-builder/components/WhereBuilder/FieldSelectorEnhanced.test.tsx`
17. `frontend/src/event-builder/components/WhereBuilder/WhereBuilderModal.test.tsx`
18. `frontend/src/event-builder/pages/EventNodeBuilder.test.tsx`

### 轮次7 (文件 19-21)
19. `frontend/src/features/async-tasks/api/__tests__/taskApi.test.ts`
20. `frontend/src/features/async-tasks/components/__tests__/TaskFilters.test.tsx`
21. `frontend/src/features/async-tasks/components/__tests__/TaskList.test.tsx`

### 轮次8 (文件 22-24)
22. `frontend/src/features/async-tasks/components/__tests__/TaskProgress.test.tsx`
23. `frontend/src/features/events/__tests__/FieldRecommendation.test.tsx`
24. `frontend/src/features/events/__tests__/fieldRecommendationApi.test.ts`

### 轮次9 (文件 25-27)
25. `frontend/src/features/events/__tests__/useFieldRecommendations.test.ts`
26. `frontend/src/features/events/hooks/useBatchOperations.test.ts`
27. `frontend/src/features/games/__tests__/AddGameModalGraphQL.type.test.ts`

### 轮次10 (文件 28-30)
28. `frontend/src/features/games/__tests__/AddGameModalGraphQL.type.test.tsx`
29. `frontend/src/features/games/__tests__/GameManagementModalGraphQL.performance.test.tsx`
30. `frontend/src/features/games/__tests__/GamesPageGraphQL.route.test.tsx`

### 轮次11 (文件 31-33)
31. `frontend/src/features/games/GameManagementModal.test.tsx`
32. `frontend/src/features/games/GameManagementModalGraphQL.smoke.test.tsx`
33. `frontend/src/features/games/GameManagementModalGraphQL.test.tsx`

### 轮次12 (文件 34-36)
34. `frontend/src/features/monitoring/__tests__/CacheStats.test.tsx`
35. `frontend/src/features/monitoring/__tests__/hooks.test.tsx`
36. `frontend/src/features/monitoring/__tests__/MetricCard.test.tsx`

### 轮次13 (文件 37-39)
37. `frontend/src/features/monitoring/__tests__/monitoringApi.test.ts`
38. `frontend/src/monitoring/__tests__/CoordinationDashboard.test.tsx`
39. `frontend/src/monitoring/__tests__/PerformanceMonitor.test.ts`

### 轮次14 (文件 40-42)
40. `frontend/src/shared/components/VirtualList/__tests__/VirtualList.test.tsx`
41. `frontend/src/shared/hooks/__tests__/useGameContext.test.ts`
42. `frontend/src/shared/hooks/useRetry.test.ts`

### 轮次15 (文件 43-45)
43. `frontend/src/shared/popup/__tests__/PopupProvider.integration.test.tsx`
44. `frontend/src/shared/popup/__tests__/useFocusManager.test.ts`
45. `frontend/src/shared/popup/__tests__/useUnifiedEscHandler.test.ts`

### 轮次16 (文件 46-48)
46. `frontend/src/shared/popup/__tests__/ZIndexManager.test.ts`
47. `frontend/src/shared/ui/Badge/Badge.test.tsx`
48. `frontend/src/shared/ui/Breadcrumb/Breadcrumb.test.tsx`

### 轮次17 (文件 49-51)
49. `frontend/src/shared/ui/Button/Button.test.tsx`
50. `frontend/src/shared/ui/Card/Card.test.tsx`
51. `frontend/src/shared/ui/Checkbox/Checkbox.test.tsx`

### 轮次18 (文件 52-54)
52. `frontend/src/shared/ui/components/__tests__/FormTable.integration.test.tsx`
53. `frontend/src/shared/ui/components/__tests__/ModalForm.integration.test.tsx`
54. `frontend/src/shared/ui/components/DatePicker/DatePicker.test.tsx`

### 轮次19 (文件 55-57)
55. `frontend/src/shared/ui/components/Form/__tests__/FormDatePicker.test.tsx`
56. `frontend/src/shared/ui/components/Form/__tests__/FormRichText.test.tsx`
57. `frontend/src/shared/ui/components/Form/__tests__/FormUpload.test.tsx`

### 轮次20 (文件 58-60)
58. `frontend/src/shared/ui/components/Form/Form.test.tsx`
59. `frontend/src/shared/ui/components/Modal/__tests__/Modal.drag.test.tsx`
60. `frontend/src/shared/ui/components/Modal/Modal.migration.test.tsx`

### 轮次21 (文件 61-63)
61. `frontend/src/shared/ui/components/Modal/Modal.test.tsx`
62. `frontend/src/shared/ui/components/Select/Select.test.tsx`
63. `frontend/src/shared/ui/components/Table/__tests__/Table.grouping.test.tsx`

### 轮次22 (文件 64-66)
64. `frontend/src/shared/ui/components/Table/__tests__/Table.performance.test.tsx`
65. `frontend/src/shared/ui/components/Table/Table.migration.test.tsx`
66. `frontend/src/shared/ui/ConfirmDialog/ConfirmDialog.test.tsx`

### 轮次23 (文件 67-69)
67. `frontend/src/shared/ui/EmptyState/EmptyState.test.tsx`
68. `frontend/src/shared/ui/ErrorState/ErrorState.test.tsx`
69. `frontend/src/shared/ui/ErrorToast/ErrorToast.test.tsx`

### 轮次24 (文件 70-72)
70. `frontend/src/shared/ui/Input/Input.test.tsx`
71. `frontend/src/shared/ui/Loading.test.tsx`
72. `frontend/src/shared/ui/PageLoader/PageLoader.test.tsx`

### 轮次25 (文件 73-75)
73. `frontend/src/shared/ui/Radio/Radio.test.tsx`
74. `frontend/src/shared/ui/SearchInput/SearchInput.test.tsx`
75. `frontend/src/shared/ui/Select/Select.test.tsx`

### 轮次26 (文件 76-78)
76. `frontend/src/shared/ui/Spinner/Spinner.test.tsx`
77. `frontend/src/shared/ui/Switch/Switch.test.tsx`
78. `frontend/src/shared/ui/Table/Table.test.tsx`

### 轮次27 (文件 79-81)
79. `frontend/src/shared/ui/TextArea/TextArea.test.tsx`
80. `frontend/src/shared/ui/Toast/Toast.test.tsx`
81. `frontend/src/shared/utils/apiValidator.test.ts`

### 轮次28 (文件 82-84)
82. `frontend/src/shared/utils/canvasPerformanceMonitor.test.ts`
83. `frontend/src/shared/utils/componentUtils.test.ts`
84. `frontend/src/shared/utils/errorHandler.test.ts`

### 轮次29 (文件 85-87)
85. `frontend/src/shared/utils/fieldBuilder.test.ts`
86. `frontend/src/shared/utils/formatNumber.test.ts`
87. `frontend/src/shared/utils/graphqlPerformanceMonitor.test.ts`

### 轮次30 (文件 88-90)
88. `frontend/src/shared/utils/graphqlQueryOptimizer.test.ts`
89. `frontend/src/shared/utils/hiveLinter.test.ts`
90. `frontend/src/shared/utils/sqlFormatter.test.ts`

### 轮次31 (文件 91-93)
91. `frontend/src/shared/utils/typeGuards.test.ts`
92. `frontend/src/shared/utils/validationUtils.test.ts`
93. `frontend/src/shared/utils/whereGenerator.test.ts`

### 轮次32 (文件 94-96)
94. `frontend/src/test/performance/react-components-performance.test.tsx`
95. `frontend/src/test/performance/VirtualScroll.benchmark.test.ts`
96. (备用)

### 轮次33 (文件 97-99)
97. (备用)
98. (备用)
99. (备用)

### 轮次34 (文件 100)
100. (备用)

---

## 执行状态

- [x] 统计测试文件
- [ ] 轮次1-34: 并行测试
- [ ] 统计失败测试
- [ ] 分析失败原因
- [ ] 修复所有失败测试
