/** 从MainLayout传递的上下文类型 */
export interface LayoutContext {
  currentGame: {
    id: number;
    gid: number;
    name: string;
    ods_db: string;
  } | null;
  setCurrentGame: (game: any) => void;
}

/** 事件数据类型（从API获取） */
export interface EventData {
  id: number;
  event_name: string;
  event_name_cn: string;
  game_name: string;
  gid: number;
  game_id: number;
  game_gid: number;
  category_name?: string;
  category_id?: number;
  param_count?: number;
  source_table?: string;
  target_table?: string;
  created_at?: string;
  updated_at?: string;
}

/** 分页信息类型 */
export interface PaginationInfo {
  total: number;
  total_pages: number;
  page: number;
  per_page: number;
}

/** API响应数据类型 */
export interface EventsListResponse {
  events: EventData[];
  pagination: PaginationInfo;
}

/** 确认对话框状态类型 */
export interface ConfirmState {
  open: boolean;
  onConfirm: () => void;
  title: string;
  message: string;
}

/** 占位数据类型（无游戏上下文时使用） */
export interface PlaceholderData {
  events: EventData[];
  pagination: PaginationInfo;
}

/** 页面大小选项类型 */
export interface PageSizeOption {
  value: string;
  label: string;
}

/** EventsListHeader 组件 Props */
export interface EventsListHeaderProps {
  selectedCount: number;
  onBatchEdit: () => void;
  onBatchValidate: () => void;
  onBatchDelete: () => void;
  onCreateEvent: () => void;
  onImportEvents: () => void;
}

/** EventsStats 组件 Props */
export interface EventsStatsProps {
  total: number;
  categorizedCount: number;
  uncategorizedCount: number;
}

/** EventsFilters 组件 Props */
export interface EventsFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedCount: number;
  totalCount: number;
  onSelectAll: () => void;
  onClearSelection: () => void;
}

/** EventsVirtualTable 组件 Props */
export interface EventsVirtualTableProps {
  events: EventData[];
  selectedEvents: number[];
  onToggleSelect: (eventId: number) => void;
  onViewEvent: (eventId: number) => void;
  onEditEvent: (eventId: number) => void;
  onDeleteEvent: (eventId: number, eventName: string) => void;
  isLoading: boolean;
}
