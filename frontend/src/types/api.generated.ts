import { DocumentNode } from 'graphql';
import * as Apollo from '@apollo/client';
export type Maybe<T> = T | null | undefined;
export type InputMaybe<T> = T | null | undefined;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

/**
 * Auto Sync Common Parameters Mutation
 *
 * Automatically detects and syncs common parameters across all events in a game.
 */
export type AutoSyncCommonParametersMutation = {
  __typename?: 'AutoSyncCommonParametersMutation';
  /** 结果消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 批量操作结果 */
  result?: Maybe<BatchOperationResultType>;
  /** 操作是否成功 */
  success?: Maybe<Scalars['Boolean']['output']>;
};

/**
 * Batch Add Fields to Canvas Mutation
 *
 * Adds multiple fields to a Canvas node configuration.
 */
export type BatchAddFieldsToCanvasMutation = {
  __typename?: 'BatchAddFieldsToCanvasMutation';
  /** 结果消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 批量操作结果 */
  result?: Maybe<BatchOperationResultType>;
  /** 操作是否成功 */
  success?: Maybe<Scalars['Boolean']['output']>;
};

/** 批量操作结果 */
export type BatchOperationResultType = {
  __typename?: 'BatchOperationResultType';
  /** 错误列表 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 失败数量 */
  failedCount?: Maybe<Scalars['Int']['output']>;
  /** 结果消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  success: Scalars['Boolean']['output'];
  /** 成功数量 */
  successCount?: Maybe<Scalars['Int']['output']>;
  /** 总数量 */
  totalCount?: Maybe<Scalars['Int']['output']>;
};

/** 事件分类实体 */
export type CategoryType = {
  __typename?: 'CategoryType';
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 分类描述 */
  description?: Maybe<Scalars['String']['output']>;
  /** 事件数量 */
  eventCount?: Maybe<Scalars['Int']['output']>;
  /** 分类ID */
  id: Scalars['Int']['output'];
  /** 分类名称 */
  name: Scalars['String']['output'];
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
};

/**
 * Change Parameter Type Mutation
 *
 * Updates the data type of an existing parameter.
 */
export type ChangeParameterTypeMutation = {
  __typename?: 'ChangeParameterTypeMutation';
  /** 结果消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 更新后的参数 */
  parameter?: Maybe<ParameterManagementType>;
  /** 操作是否成功 */
  success?: Maybe<Scalars['Boolean']['output']>;
};

/** 公共参数 */
export type CommonParameterType = {
  __typename?: 'CommonParameterType';
  /** 公共性评分（0-1） */
  commonalityScore?: Maybe<Scalars['Float']['output']>;
  /** 使用该参数的事件代码列表 */
  eventCodes?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 是否为公共参数（超过阈值） */
  isCommon?: Maybe<Scalars['Boolean']['output']>;
  /** 出现次数（事件数） */
  occurrenceCount: Scalars['Int']['output'];
  /** 参数描述 */
  paramDescription?: Maybe<Scalars['String']['output']>;
  /** 参数名称 */
  paramName: Scalars['String']['output'];
  /** 参数类型 */
  paramType?: Maybe<Scalars['String']['output']>;
  /** 公共参数阈值（百分比） */
  threshold?: Maybe<Scalars['Float']['output']>;
  /** 游戏总事件数 */
  totalEvents: Scalars['Int']['output'];
};

/** Create a new category */
export type CreateCategory = {
  __typename?: 'CreateCategory';
  /** 创建的分类 */
  category?: Maybe<CategoryType>;
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Create a new event */
export type CreateEvent = {
  __typename?: 'CreateEvent';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 创建的事件 */
  event?: Maybe<EventType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Create a new flow */
export type CreateFlow = {
  __typename?: 'CreateFlow';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 创建的流程 */
  flow?: Maybe<FlowType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Create a new game */
export type CreateGame = {
  __typename?: 'CreateGame';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 创建的游戏 */
  game?: Maybe<GameType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Create a new join config */
export type CreateJoinConfig = {
  __typename?: 'CreateJoinConfig';
  /** 创建的配置 */
  config?: Maybe<JoinConfigType>;
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Create a new node */
export type CreateNode = {
  __typename?: 'CreateNode';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 创建的节点 */
  node?: Maybe<NodeType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Create a new parameter */
export type CreateParameter = {
  __typename?: 'CreateParameter';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 创建的参数 */
  parameter?: Maybe<ParameterType>;
};

/** Create a new template */
export type CreateTemplate = {
  __typename?: 'CreateTemplate';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 创建的模板 */
  template?: Maybe<TemplateType>;
};

/** Create a validation rule for a parameter */
export type CreateValidationRule = {
  __typename?: 'CreateValidationRule';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 创建的规则 */
  rule?: Maybe<ValidationRuleType>;
};

/** 仪表盘统计数据 */
export type DashboardStatsType = {
  __typename?: 'DashboardStatsType';
  /** 最近7天新增事件数 */
  eventsLast7Days?: Maybe<Scalars['Int']['output']>;
  /** 最近7天新增参数数 */
  parametersLast7Days?: Maybe<Scalars['Int']['output']>;
  /** 分类总数 */
  totalCategories?: Maybe<Scalars['Int']['output']>;
  /** 事件总数 */
  totalEvents?: Maybe<Scalars['Int']['output']>;
  /** 游戏总数 */
  totalGames?: Maybe<Scalars['Int']['output']>;
  /** 参数总数 */
  totalParameters?: Maybe<Scalars['Int']['output']>;
};

/** Delete a category */
export type DeleteCategory = {
  __typename?: 'DeleteCategory';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete an event */
export type DeleteEvent = {
  __typename?: 'DeleteEvent';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete an event parameter */
export type DeleteEventParameter = {
  __typename?: 'DeleteEventParameter';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete a flow */
export type DeleteFlow = {
  __typename?: 'DeleteFlow';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete a game */
export type DeleteGame = {
  __typename?: 'DeleteGame';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete an HQL template */
export type DeleteHqlTemplate = {
  __typename?: 'DeleteHQLTemplate';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete a join config */
export type DeleteJoinConfig = {
  __typename?: 'DeleteJoinConfig';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete a node */
export type DeleteNode = {
  __typename?: 'DeleteNode';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete a parameter (soft delete by setting is_active = 0) */
export type DeleteParameter = {
  __typename?: 'DeleteParameter';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Delete a template */
export type DeleteTemplate = {
  __typename?: 'DeleteTemplate';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作消息 */
  message?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** 扩展事件参数 */
export type EventParameterExtendedType = {
  __typename?: 'EventParameterExtendedType';
  /** 参数配置 */
  config?: Maybe<ParamConfigType>;
  /** 事件ID */
  eventId: Scalars['Int']['output'];
  /** 参数ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** JSON路径 */
  jsonPath?: Maybe<Scalars['String']['output']>;
  /** 最新版本 */
  latestVersion?: Maybe<ParamVersionType>;
  /** 参数英文名 */
  paramName: Scalars['String']['output'];
  /** 参数中文名 */
  paramNameCn?: Maybe<Scalars['String']['output']>;
  /** 参数类型 */
  paramType?: Maybe<Scalars['String']['output']>;
  /** 版本号 */
  version?: Maybe<Scalars['Int']['output']>;
};

/** 事件实体 */
export type EventType = {
  __typename?: 'EventType';
  /** 分类ID */
  categoryId?: Maybe<Scalars['Int']['output']>;
  /** 分类名称 */
  categoryName?: Maybe<Scalars['String']['output']>;
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 事件英文名 */
  eventName: Scalars['String']['output'];
  /** 事件中文名 */
  eventNameCn: Scalars['String']['output'];
  /** 游戏GID */
  gameGid: Scalars['Int']['output'];
  /** 事件ID */
  id: Scalars['Int']['output'];
  /** 是否包含在公共参数中 */
  includeInCommonParams?: Maybe<Scalars['Boolean']['output']>;
  /** 参数数量 */
  paramCount?: Maybe<Scalars['Int']['output']>;
  /** 源表名 */
  sourceTable?: Maybe<Scalars['String']['output']>;
  /** 目标表名 */
  targetTable?: Maybe<Scalars['String']['output']>;
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
};

/** 字段类型分类 */
export type FieldTypeEnum =
  | 'ALL'
  | 'BASE'
  | 'COMMON'
  | 'NON_COMMON'
  | 'PARAMS';

/** 事件字段 */
export type FieldTypeType = {
  __typename?: 'FieldTypeType';
  /** 字段分类（base, common, param） */
  category?: Maybe<Scalars['String']['output']>;
  /** 数据类型（int, string, array, boolean, map） */
  dataType?: Maybe<Scalars['String']['output']>;
  /** 显示名称 */
  displayName?: Maybe<Scalars['String']['output']>;
  /** 是否为公共字段 */
  isCommon?: Maybe<Scalars['Boolean']['output']>;
  /** JSON路径（用于参数字段） */
  jsonPath?: Maybe<Scalars['String']['output']>;
  /** 字段名称 */
  name: Scalars['String']['output'];
  /** 字段类型 */
  type?: Maybe<FieldTypeEnum>;
  /** 使用次数 */
  usageCount?: Maybe<Scalars['Int']['output']>;
};

/** 画布流程配置 */
export type FlowType = {
  __typename?: 'FlowType';
  /** 流程配置JSON */
  config?: Maybe<Scalars['String']['output']>;
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 流程描述 */
  description?: Maybe<Scalars['String']['output']>;
  /** 边数据JSON */
  edges?: Maybe<Scalars['String']['output']>;
  /** 流程类型 */
  flowType?: Maybe<Scalars['String']['output']>;
  /** 关联游戏GID */
  gameGid?: Maybe<Scalars['Int']['output']>;
  /** 流程ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** 流程名称 */
  name: Scalars['String']['output'];
  /** 节点数据JSON */
  nodes?: Maybe<Scalars['String']['output']>;
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
  /** 版本号 */
  version?: Maybe<Scalars['Int']['output']>;
};

/** 游戏统计数据 */
export type GameStatsType = {
  __typename?: 'GameStatsType';
  /** 分类数量 */
  categoryCount?: Maybe<Scalars['Int']['output']>;
  /** 事件数量 */
  eventCount?: Maybe<Scalars['Int']['output']>;
  /** 游戏GID */
  gameGid: Scalars['Int']['output'];
  /** 游戏名称 */
  gameName?: Maybe<Scalars['String']['output']>;
  /** 参数数量 */
  parameterCount?: Maybe<Scalars['Int']['output']>;
};

/** 游戏实体 */
export type GameType = {
  __typename?: 'GameType';
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 事件数量 */
  eventCount?: Maybe<Scalars['Int']['output']>;
  /** 事件节点数量 */
  eventNodeCount?: Maybe<Scalars['Int']['output']>;
  /** 流程模板数量 */
  flowTemplateCount?: Maybe<Scalars['Int']['output']>;
  /** 游戏业务GID */
  gid: Scalars['Int']['output'];
  /** 游戏图标路径 */
  iconPath?: Maybe<Scalars['String']['output']>;
  /** 数据库ID */
  id: Scalars['Int']['output'];
  /** 游戏名称 */
  name: Scalars['String']['output'];
  /** ODS数据库名称 */
  odsDb: Scalars['String']['output'];
  /** 参数数量 */
  parameterCount?: Maybe<Scalars['Int']['output']>;
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
};

/** Generate HQL from events */
export type GenerateHql = {
  __typename?: 'GenerateHQL';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 生成的HQL语句 */
  hql?: Maybe<Scalars['String']['output']>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Join配置 */
export type JoinConfigType = {
  __typename?: 'JoinConfigType';
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 关联游戏ID */
  gameId?: Maybe<Scalars['Int']['output']>;
  /** 配置ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** 连接条件JSON */
  joinConditions?: Maybe<Scalars['String']['output']>;
  /** 连接类型(union_all/join/where_in) */
  joinType?: Maybe<Scalars['String']['output']>;
  /** 配置名称 */
  name: Scalars['String']['output'];
  /** 输出字段JSON */
  outputFields?: Maybe<Scalars['String']['output']>;
  /** 输出表名 */
  outputTable?: Maybe<Scalars['String']['output']>;
  /** 源事件JSON */
  sourceEvents?: Maybe<Scalars['String']['output']>;
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
};

/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type Mutation = {
  __typename?: 'Mutation';
  /** 自动同步公共参数 */
  autoSyncCommonParameters?: Maybe<AutoSyncCommonParametersMutation>;
  /** 批量添加字段到画布 */
  batchAddFieldsToCanvas?: Maybe<BatchAddFieldsToCanvasMutation>;
  /** 修改参数类型 */
  changeParameterType?: Maybe<ChangeParameterTypeMutation>;
  /** Create a new category */
  createCategory?: Maybe<CreateCategory>;
  /** Create a new event */
  createEvent?: Maybe<CreateEvent>;
  /** Create a new flow */
  createFlow?: Maybe<CreateFlow>;
  /** Create a new game */
  createGame?: Maybe<CreateGame>;
  /** Create a new join config */
  createJoinConfig?: Maybe<CreateJoinConfig>;
  /** Create a new node */
  createNode?: Maybe<CreateNode>;
  /** Create a new parameter */
  createParameter?: Maybe<CreateParameter>;
  /** Create a new template */
  createTemplate?: Maybe<CreateTemplate>;
  /** Create a validation rule for a parameter */
  createValidationRule?: Maybe<CreateValidationRule>;
  /** Delete a category */
  deleteCategory?: Maybe<DeleteCategory>;
  /** Delete an event */
  deleteEvent?: Maybe<DeleteEvent>;
  /** Delete an event parameter */
  deleteEventParameter?: Maybe<DeleteEventParameter>;
  /** Delete a flow */
  deleteFlow?: Maybe<DeleteFlow>;
  /** Delete a game */
  deleteGame?: Maybe<DeleteGame>;
  /** Delete an HQL template */
  deleteHqlTemplate?: Maybe<DeleteHqlTemplate>;
  /** Delete a join config */
  deleteJoinConfig?: Maybe<DeleteJoinConfig>;
  /** Delete a node */
  deleteNode?: Maybe<DeleteNode>;
  /** Delete a parameter (soft delete by setting is_active = 0) */
  deleteParameter?: Maybe<DeleteParameter>;
  /** Delete a template */
  deleteTemplate?: Maybe<DeleteTemplate>;
  /** Generate HQL from events */
  generateHql?: Maybe<GenerateHql>;
  /** Rollback parameter to a previous version */
  rollbackEventParameter?: Maybe<RollbackEventParameter>;
  /** Save HQL as a template */
  saveHqlTemplate?: Maybe<SaveHqlTemplate>;
  /** Set parameter configuration */
  setParamConfig?: Maybe<SetParamConfig>;
  /** Update an existing category */
  updateCategory?: Maybe<UpdateCategory>;
  /** Update an existing event */
  updateEvent?: Maybe<UpdateEvent>;
  /** Update an event parameter */
  updateEventParameter?: Maybe<UpdateEventParameter>;
  /** Update an existing flow */
  updateFlow?: Maybe<UpdateFlow>;
  /** Update an existing game */
  updateGame?: Maybe<UpdateGame>;
  /** Update an existing join config */
  updateJoinConfig?: Maybe<UpdateJoinConfig>;
  /** Update an existing node */
  updateNode?: Maybe<UpdateNode>;
  /** Update an existing parameter */
  updateParameter?: Maybe<UpdateParameter>;
  /** Update an existing template */
  updateTemplate?: Maybe<UpdateTemplate>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationAutoSyncCommonParametersArgs = {
  gameGid: Scalars['Int']['input'];
  threshold?: InputMaybe<Scalars['Float']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationBatchAddFieldsToCanvasArgs = {
  eventId: Scalars['Int']['input'];
  fieldType: FieldTypeEnum;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationChangeParameterTypeArgs = {
  newType: ParameterTypeEnum;
  parameterId: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateCategoryArgs = {
  name: Scalars['String']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateEventArgs = {
  categoryId: Scalars['Int']['input'];
  eventName: Scalars['String']['input'];
  eventNameCn: Scalars['String']['input'];
  gameGid: Scalars['Int']['input'];
  includeInCommonParams?: InputMaybe<Scalars['Boolean']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateFlowArgs = {
  config?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  edges?: InputMaybe<Scalars['String']['input']>;
  flowType?: InputMaybe<Scalars['String']['input']>;
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  name: Scalars['String']['input'];
  nodes?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateGameArgs = {
  gid: Scalars['Int']['input'];
  name: Scalars['String']['input'];
  odsDb: Scalars['String']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateJoinConfigArgs = {
  gameId?: InputMaybe<Scalars['Int']['input']>;
  joinConditions?: InputMaybe<Scalars['String']['input']>;
  joinType?: InputMaybe<Scalars['String']['input']>;
  name: Scalars['String']['input'];
  outputFields?: InputMaybe<Scalars['String']['input']>;
  outputTable?: InputMaybe<Scalars['String']['input']>;
  sourceEvents?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateNodeArgs = {
  config?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  name: Scalars['String']['input'];
  nodeType?: InputMaybe<Scalars['String']['input']>;
  positionX?: InputMaybe<Scalars['Float']['input']>;
  positionY?: InputMaybe<Scalars['Float']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateParameterArgs = {
  eventId: Scalars['Int']['input'];
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  jsonPath?: InputMaybe<Scalars['String']['input']>;
  paramName: Scalars['String']['input'];
  paramNameCn?: InputMaybe<Scalars['String']['input']>;
  templateId?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateTemplateArgs = {
  category?: InputMaybe<Scalars['String']['input']>;
  config?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  name: Scalars['String']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationCreateValidationRuleArgs = {
  errorMessage?: InputMaybe<Scalars['String']['input']>;
  paramId: Scalars['Int']['input'];
  ruleConfig?: InputMaybe<Scalars['String']['input']>;
  ruleType: Scalars['String']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteCategoryArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteEventArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteEventParameterArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteFlowArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteGameArgs = {
  confirm?: InputMaybe<Scalars['Boolean']['input']>;
  gid: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteHqlTemplateArgs = {
  templateId: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteJoinConfigArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteNodeArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteParameterArgs = {
  hardDelete?: InputMaybe<Scalars['Boolean']['input']>;
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationDeleteTemplateArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationGenerateHqlArgs = {
  eventIds: Array<InputMaybe<Scalars['Int']['input']>>;
  mode?: InputMaybe<Scalars['String']['input']>;
  options?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationRollbackEventParameterArgs = {
  id: Scalars['Int']['input'];
  version: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationSaveHqlTemplateArgs = {
  category?: InputMaybe<Scalars['String']['input']>;
  content: Scalars['String']['input'];
  description?: InputMaybe<Scalars['String']['input']>;
  name: Scalars['String']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationSetParamConfigArgs = {
  arrayExpand?: InputMaybe<Scalars['Boolean']['input']>;
  customHqlTemplate?: InputMaybe<Scalars['String']['input']>;
  mapExpand?: InputMaybe<Scalars['Boolean']['input']>;
  outputFieldName?: InputMaybe<Scalars['String']['input']>;
  paramId: Scalars['Int']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateCategoryArgs = {
  id: Scalars['Int']['input'];
  name: Scalars['String']['input'];
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateEventArgs = {
  categoryId?: InputMaybe<Scalars['Int']['input']>;
  eventNameCn?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['Int']['input'];
  includeInCommonParams?: InputMaybe<Scalars['Boolean']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateEventParameterArgs = {
  id: Scalars['Int']['input'];
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  jsonPath?: InputMaybe<Scalars['String']['input']>;
  paramName?: InputMaybe<Scalars['String']['input']>;
  paramNameCn?: InputMaybe<Scalars['String']['input']>;
  paramType?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateFlowArgs = {
  config?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  edges?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['Int']['input'];
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  nodes?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateGameArgs = {
  gid: Scalars['Int']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  odsDb?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateJoinConfigArgs = {
  gameId?: InputMaybe<Scalars['Int']['input']>;
  id: Scalars['Int']['input'];
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  joinConditions?: InputMaybe<Scalars['String']['input']>;
  joinType?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  outputFields?: InputMaybe<Scalars['String']['input']>;
  outputTable?: InputMaybe<Scalars['String']['input']>;
  sourceEvents?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateNodeArgs = {
  config?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['Int']['input'];
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  positionX?: InputMaybe<Scalars['Float']['input']>;
  positionY?: InputMaybe<Scalars['Float']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateParameterArgs = {
  id: Scalars['Int']['input'];
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  jsonPath?: InputMaybe<Scalars['String']['input']>;
  paramNameCn?: InputMaybe<Scalars['String']['input']>;
  templateId?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Mutation Root Type
 *
 * Provides all mutation operations for the API.
 */
export type MutationUpdateTemplateArgs = {
  category?: InputMaybe<Scalars['String']['input']>;
  config?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  id: Scalars['Int']['input'];
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

/** 画布节点配置 */
export type NodeType = {
  __typename?: 'NodeType';
  /** 节点配置JSON */
  config?: Maybe<Scalars['String']['output']>;
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 节点描述 */
  description?: Maybe<Scalars['String']['output']>;
  /** 关联游戏GID */
  gameGid?: Maybe<Scalars['Int']['output']>;
  /** 节点ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** 节点名称 */
  name: Scalars['String']['output'];
  /** 节点类型 */
  nodeType?: Maybe<Scalars['String']['output']>;
  /** X坐标 */
  positionX?: Maybe<Scalars['Float']['output']>;
  /** Y坐标 */
  positionY?: Maybe<Scalars['Float']['output']>;
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
  /** 版本号 */
  version?: Maybe<Scalars['Int']['output']>;
};

/** 参数配置 */
export type ParamConfigType = {
  __typename?: 'ParamConfigType';
  /** 是否展开数组 */
  arrayExpand?: Maybe<Scalars['Boolean']['output']>;
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 自定义HQL模板 */
  customHqlTemplate?: Maybe<Scalars['String']['output']>;
  /** 配置ID */
  id: Scalars['Int']['output'];
  /** 是否展开Map */
  mapExpand?: Maybe<Scalars['Boolean']['output']>;
  /** 输出字段名 */
  outputFieldName?: Maybe<Scalars['String']['output']>;
  /** 参数ID */
  paramId: Scalars['Int']['output'];
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
};

/** 参数版本历史 */
export type ParamVersionType = {
  __typename?: 'ParamVersionType';
  /** 变更人 */
  changedBy?: Maybe<Scalars['String']['output']>;
  /** 变更内容JSON */
  changes?: Maybe<Scalars['String']['output']>;
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 版本ID */
  id: Scalars['Int']['output'];
  /** 参数ID */
  paramId: Scalars['Int']['output'];
  /** 版本号 */
  version?: Maybe<Scalars['Int']['output']>;
};

/** 参数变更记录 */
export type ParameterChangeType = {
  __typename?: 'ParameterChangeType';
  /** 变更类型（create, update, delete） */
  changeType?: Maybe<Scalars['String']['output']>;
  /** 变更时间 */
  changedAt?: Maybe<Scalars['String']['output']>;
  /** 变更者 */
  changedBy?: Maybe<Scalars['String']['output']>;
  /** 变更字段 */
  changedField?: Maybe<Scalars['String']['output']>;
  /** 变更记录ID */
  id: Scalars['Int']['output'];
  /** 新值 */
  newValue?: Maybe<Scalars['String']['output']>;
  /** 旧值 */
  oldValue?: Maybe<Scalars['String']['output']>;
  /** 参数名称 */
  paramName: Scalars['String']['output'];
  /** 参数ID */
  parameterId: Scalars['Int']['output'];
};

/** 参数过滤模式 */
export type ParameterFilterModeEnum =
  | 'ALL'
  | 'COMMON'
  | 'NON_COMMON';

/** 事件参数（管理类型） */
export type ParameterManagementType = {
  __typename?: 'ParameterManagementType';
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 事件代码 */
  eventCode?: Maybe<Scalars['String']['output']>;
  /** 事件ID */
  eventId: Scalars['Int']['output'];
  /** 事件名称 */
  eventName?: Maybe<Scalars['String']['output']>;
  /** 关联事件数量 */
  eventsCount?: Maybe<Scalars['Int']['output']>;
  /** 游戏GID */
  gameGid?: Maybe<Scalars['Int']['output']>;
  /** 参数ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** 是否为公共参数 */
  isCommon?: Maybe<Scalars['Boolean']['output']>;
  /** JSON路径 */
  jsonPath?: Maybe<Scalars['String']['output']>;
  /** 参数描述 */
  paramDescription?: Maybe<Scalars['String']['output']>;
  /** 参数英文名 */
  paramName: Scalars['String']['output'];
  /** 参数中文名 */
  paramNameCn?: Maybe<Scalars['String']['output']>;
  /** 参数类型 */
  paramType?: Maybe<ParameterTypeEnum>;
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
  /** 使用次数（跨事件） */
  usageCount?: Maybe<Scalars['Int']['output']>;
  /** 版本号 */
  version?: Maybe<Scalars['Int']['output']>;
};

/** 事件参数 */
export type ParameterType = {
  __typename?: 'ParameterType';
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 事件ID */
  eventId: Scalars['Int']['output'];
  /** 参数ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** JSON路径 */
  jsonPath?: Maybe<Scalars['String']['output']>;
  /** 参数描述 */
  paramDescription?: Maybe<Scalars['String']['output']>;
  /** 参数英文名 */
  paramName: Scalars['String']['output'];
  /** 参数中文名 */
  paramNameCn?: Maybe<Scalars['String']['output']>;
  /** 参数类型 */
  paramType?: Maybe<Scalars['String']['output']>;
  /** 参数模板ID */
  templateId?: Maybe<Scalars['Int']['output']>;
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
  /** 版本号 */
  version?: Maybe<Scalars['Int']['output']>;
};

/** 参数数据类型 */
export type ParameterTypeEnum =
  | 'ARRAY'
  | 'BOOLEAN'
  | 'INT'
  | 'MAP'
  | 'STRING';

/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type Query = {
  __typename?: 'Query';
  /** 获取所有游戏的统计数据 */
  allGameStats?: Maybe<Array<Maybe<GameStatsType>>>;
  /** 查询分类列表（支持分页） */
  categories?: Maybe<Array<Maybe<CategoryType>>>;
  /** 根据ID查询单个分类 */
  category?: Maybe<CategoryType>;
  /** 查询公共参数列表 */
  commonParameters?: Maybe<Array<Maybe<CommonParameterType>>>;
  /** 获取仪表盘统计数据 */
  dashboardStats?: Maybe<DashboardStatsType>;
  /** 根据ID查询单个事件 */
  event?: Maybe<EventType>;
  /** 查询事件字段列表 */
  eventFields?: Maybe<Array<Maybe<FieldTypeType>>>;
  /** 查询扩展事件参数 */
  eventParameterExtended?: Maybe<EventParameterExtendedType>;
  /** 查询游戏的事件列表（支持过滤和分页） */
  events?: Maybe<Array<Maybe<EventType>>>;
  /** 根据ID查询单个流程 */
  flow?: Maybe<FlowType>;
  /** 查询流程列表 */
  flows?: Maybe<Array<Maybe<FlowType>>>;
  /** 根据GID查询单个游戏 */
  game?: Maybe<GameType>;
  /** 获取指定游戏的统计数据 */
  gameStats?: Maybe<GameStatsType>;
  /** 查询游戏列表（支持分页） */
  games?: Maybe<Array<Maybe<GameType>>>;
  /** 根据ID查询单个Join配置 */
  joinConfig?: Maybe<JoinConfigType>;
  /** 查询Join配置列表 */
  joinConfigs?: Maybe<Array<Maybe<JoinConfigType>>>;
  /** 根据ID查询单个节点 */
  node?: Maybe<NodeType>;
  /** 查询节点列表 */
  nodes?: Maybe<Array<Maybe<NodeType>>>;
  /** 查询参数配置 */
  paramConfig?: Maybe<ParamConfigType>;
  /** 查询参数版本历史 */
  paramHistory?: Maybe<Array<Maybe<ParamVersionType>>>;
  /** 根据ID查询单个参数 */
  parameter?: Maybe<ParameterType>;
  /** 查询参数变更记录 */
  parameterChanges?: Maybe<Array<Maybe<ParameterChangeType>>>;
  /** 查询事件的参数列表 */
  parameters?: Maybe<Array<Maybe<ParameterType>>>;
  /** 查询参数列表（支持过滤和统计） */
  parametersManagement?: Maybe<Array<Maybe<ParameterManagementType>>>;
  /** 搜索分类 */
  searchCategories?: Maybe<Array<Maybe<CategoryType>>>;
  /** 搜索事件 */
  searchEvents?: Maybe<Array<Maybe<EventType>>>;
  /** 搜索游戏 */
  searchGames?: Maybe<Array<Maybe<GameType>>>;
  /** 搜索参数 */
  searchParameters?: Maybe<Array<Maybe<ParameterType>>>;
  /** 搜索模板 */
  searchTemplates?: Maybe<Array<Maybe<TemplateType>>>;
  /** 根据ID查询单个模板 */
  template?: Maybe<TemplateType>;
  /** 查询模板列表 */
  templates?: Maybe<Array<Maybe<TemplateType>>>;
  /** 查询参数验证规则 */
  validationRules?: Maybe<Array<Maybe<ValidationRuleType>>>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryAllGameStatsArgs = {
  limit?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryCategoriesArgs = {
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryCategoryArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryCommonParametersArgs = {
  gameGid: Scalars['Int']['input'];
  threshold?: InputMaybe<Scalars['Float']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryEventArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryEventFieldsArgs = {
  eventId: Scalars['Int']['input'];
  fieldType?: InputMaybe<FieldTypeEnum>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryEventParameterExtendedArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryEventsArgs = {
  category?: InputMaybe<Scalars['String']['input']>;
  gameGid: Scalars['Int']['input'];
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryFlowArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryFlowsArgs = {
  flowType?: InputMaybe<Scalars['String']['input']>;
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryGameArgs = {
  gid: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryGameStatsArgs = {
  gameGid: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryGamesArgs = {
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryJoinConfigArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryJoinConfigsArgs = {
  gameId?: InputMaybe<Scalars['Int']['input']>;
  joinType?: InputMaybe<Scalars['String']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryNodeArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryNodesArgs = {
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  nodeType?: InputMaybe<Scalars['String']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryParamConfigArgs = {
  paramId: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryParamHistoryArgs = {
  limit?: InputMaybe<Scalars['Int']['input']>;
  paramId: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryParameterArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryParameterChangesArgs = {
  gameGid: Scalars['Int']['input'];
  limit?: InputMaybe<Scalars['Int']['input']>;
  parameterId?: InputMaybe<Scalars['Int']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryParametersArgs = {
  activeOnly?: InputMaybe<Scalars['Boolean']['input']>;
  eventId: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryParametersManagementArgs = {
  eventId?: InputMaybe<Scalars['Int']['input']>;
  gameGid: Scalars['Int']['input'];
  mode?: InputMaybe<ParameterFilterModeEnum>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QuerySearchCategoriesArgs = {
  query: Scalars['String']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QuerySearchEventsArgs = {
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  query: Scalars['String']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QuerySearchGamesArgs = {
  query: Scalars['String']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QuerySearchParametersArgs = {
  eventId?: InputMaybe<Scalars['Int']['input']>;
  query: Scalars['String']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QuerySearchTemplatesArgs = {
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  query: Scalars['String']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryTemplateArgs = {
  id: Scalars['Int']['input'];
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryTemplatesArgs = {
  category?: InputMaybe<Scalars['String']['input']>;
  gameGid?: InputMaybe<Scalars['Int']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
};


/**
 * GraphQL Query Root Type
 *
 * Provides all query operations for the API.
 */
export type QueryValidationRulesArgs = {
  paramId: Scalars['Int']['input'];
};

/** Rollback parameter to a previous version */
export type RollbackEventParameter = {
  __typename?: 'RollbackEventParameter';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 回滚后的参数 */
  parameter?: Maybe<EventParameterExtendedType>;
};

/** Save HQL as a template */
export type SaveHqlTemplate = {
  __typename?: 'SaveHQLTemplate';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 模板ID */
  templateId?: Maybe<Scalars['Int']['output']>;
};

/** Set parameter configuration */
export type SetParamConfig = {
  __typename?: 'SetParamConfig';
  /** 配置 */
  config?: Maybe<ParamConfigType>;
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** 画布流程模板 */
export type TemplateType = {
  __typename?: 'TemplateType';
  /** 模板分类 */
  category?: Maybe<Scalars['String']['output']>;
  /** 模板配置JSON */
  config?: Maybe<Scalars['String']['output']>;
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 模板描述 */
  description?: Maybe<Scalars['String']['output']>;
  /** 关联游戏GID */
  gameGid?: Maybe<Scalars['Int']['output']>;
  /** 模板ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** 模板名称 */
  name: Scalars['String']['output'];
  /** 更新时间 */
  updatedAt?: Maybe<Scalars['String']['output']>;
  /** 版本号 */
  version?: Maybe<Scalars['Int']['output']>;
};

/** Update an existing category */
export type UpdateCategory = {
  __typename?: 'UpdateCategory';
  /** 更新的分类 */
  category?: Maybe<CategoryType>;
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Update an existing event */
export type UpdateEvent = {
  __typename?: 'UpdateEvent';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 更新的事件 */
  event?: Maybe<EventType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Update an event parameter */
export type UpdateEventParameter = {
  __typename?: 'UpdateEventParameter';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 更新的参数 */
  parameter?: Maybe<EventParameterExtendedType>;
};

/** Update an existing flow */
export type UpdateFlow = {
  __typename?: 'UpdateFlow';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 更新的流程 */
  flow?: Maybe<FlowType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Update an existing game */
export type UpdateGame = {
  __typename?: 'UpdateGame';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 更新的游戏 */
  game?: Maybe<GameType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Update an existing join config */
export type UpdateJoinConfig = {
  __typename?: 'UpdateJoinConfig';
  /** 更新的配置 */
  config?: Maybe<JoinConfigType>;
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Update an existing node */
export type UpdateNode = {
  __typename?: 'UpdateNode';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 更新的节点 */
  node?: Maybe<NodeType>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
};

/** Update an existing parameter */
export type UpdateParameter = {
  __typename?: 'UpdateParameter';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 更新的参数 */
  parameter?: Maybe<ParameterType>;
};

/** Update an existing template */
export type UpdateTemplate = {
  __typename?: 'UpdateTemplate';
  /** 错误信息 */
  errors?: Maybe<Array<Maybe<Scalars['String']['output']>>>;
  /** 操作是否成功 */
  ok?: Maybe<Scalars['Boolean']['output']>;
  /** 更新的模板 */
  template?: Maybe<TemplateType>;
};

/** 参数验证规则 */
export type ValidationRuleType = {
  __typename?: 'ValidationRuleType';
  /** 创建时间 */
  createdAt?: Maybe<Scalars['String']['output']>;
  /** 错误消息 */
  errorMessage?: Maybe<Scalars['String']['output']>;
  /** 规则ID */
  id: Scalars['Int']['output'];
  /** 是否活跃 */
  isActive?: Maybe<Scalars['Boolean']['output']>;
  /** 参数ID */
  paramId: Scalars['Int']['output'];
  /** 规则配置JSON */
  ruleConfig?: Maybe<Scalars['String']['output']>;
  /** 规则类型 */
  ruleType?: Maybe<Scalars['String']['output']>;
};

export type CreateGameMutationVariables = Exact<{
  gid: Scalars['Int']['input'];
  name: Scalars['String']['input'];
  odsDb: Scalars['String']['input'];
}>;


export type CreateGameMutation = { __typename?: 'Mutation', createGame?: { __typename?: 'CreateGame', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, game?: { __typename?: 'GameType', gid: number, name: string, odsDb: string } | null | undefined } | null | undefined };

export type UpdateGameMutationVariables = Exact<{
  gid: Scalars['Int']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  odsDb?: InputMaybe<Scalars['String']['input']>;
}>;


export type UpdateGameMutation = { __typename?: 'Mutation', updateGame?: { __typename?: 'UpdateGame', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, game?: { __typename?: 'GameType', gid: number, name: string, odsDb: string } | null | undefined } | null | undefined };

export type DeleteGameMutationVariables = Exact<{
  gid: Scalars['Int']['input'];
  confirm?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type DeleteGameMutation = { __typename?: 'Mutation', deleteGame?: { __typename?: 'DeleteGame', ok?: boolean | null | undefined, message?: string | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined };

export type CreateEventMutationVariables = Exact<{
  gameGid: Scalars['Int']['input'];
  eventName: Scalars['String']['input'];
  eventNameCn: Scalars['String']['input'];
  categoryId: Scalars['Int']['input'];
  includeInCommonParams?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type CreateEventMutation = { __typename?: 'Mutation', createEvent?: { __typename?: 'CreateEvent', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, event?: { __typename?: 'EventType', id: number, eventName: string, eventNameCn: string } | null | undefined } | null | undefined };

export type UpdateEventMutationVariables = Exact<{
  id: Scalars['Int']['input'];
  eventNameCn?: InputMaybe<Scalars['String']['input']>;
  categoryId?: InputMaybe<Scalars['Int']['input']>;
  includeInCommonParams?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type UpdateEventMutation = { __typename?: 'Mutation', updateEvent?: { __typename?: 'UpdateEvent', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, event?: { __typename?: 'EventType', id: number, eventNameCn: string } | null | undefined } | null | undefined };

export type DeleteEventMutationVariables = Exact<{
  id: Scalars['Int']['input'];
}>;


export type DeleteEventMutation = { __typename?: 'Mutation', deleteEvent?: { __typename?: 'DeleteEvent', ok?: boolean | null | undefined, message?: string | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined };

export type CreateParameterMutationVariables = Exact<{
  eventId: Scalars['Int']['input'];
  paramName: Scalars['String']['input'];
  paramNameCn?: InputMaybe<Scalars['String']['input']>;
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  jsonPath?: InputMaybe<Scalars['String']['input']>;
  templateId?: InputMaybe<Scalars['Int']['input']>;
}>;


export type CreateParameterMutation = { __typename?: 'Mutation', createParameter?: { __typename?: 'CreateParameter', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, parameter?: { __typename?: 'ParameterType', id: number, eventId: number, paramName: string, paramNameCn?: string | null | undefined, isActive?: boolean | null | undefined, jsonPath?: string | null | undefined } | null | undefined } | null | undefined };

export type UpdateParameterMutationVariables = Exact<{
  id: Scalars['Int']['input'];
  paramNameCn?: InputMaybe<Scalars['String']['input']>;
  isActive?: InputMaybe<Scalars['Boolean']['input']>;
  jsonPath?: InputMaybe<Scalars['String']['input']>;
  templateId?: InputMaybe<Scalars['Int']['input']>;
}>;


export type UpdateParameterMutation = { __typename?: 'Mutation', updateParameter?: { __typename?: 'UpdateParameter', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, parameter?: { __typename?: 'ParameterType', id: number, paramNameCn?: string | null | undefined, isActive?: boolean | null | undefined, jsonPath?: string | null | undefined } | null | undefined } | null | undefined };

export type DeleteParameterMutationVariables = Exact<{
  id: Scalars['Int']['input'];
}>;


export type DeleteParameterMutation = { __typename?: 'Mutation', deleteParameter?: { __typename?: 'DeleteParameter', ok?: boolean | null | undefined, message?: string | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined };

export type CreateCategoryMutationVariables = Exact<{
  name: Scalars['String']['input'];
}>;


export type CreateCategoryMutation = { __typename?: 'Mutation', createCategory?: { __typename?: 'CreateCategory', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, category?: { __typename?: 'CategoryType', id: number, name: string } | null | undefined } | null | undefined };

export type UpdateCategoryMutationVariables = Exact<{
  id: Scalars['Int']['input'];
  name: Scalars['String']['input'];
}>;


export type UpdateCategoryMutation = { __typename?: 'Mutation', updateCategory?: { __typename?: 'UpdateCategory', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined, category?: { __typename?: 'CategoryType', id: number, name: string } | null | undefined } | null | undefined };

export type DeleteCategoryMutationVariables = Exact<{
  id: Scalars['Int']['input'];
}>;


export type DeleteCategoryMutation = { __typename?: 'Mutation', deleteCategory?: { __typename?: 'DeleteCategory', ok?: boolean | null | undefined, message?: string | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined };

export type GenerateHqlMutationVariables = Exact<{
  eventIds: Array<Scalars['Int']['input']> | Scalars['Int']['input'];
  mode?: InputMaybe<Scalars['String']['input']>;
  options?: InputMaybe<Scalars['String']['input']>;
}>;


export type GenerateHqlMutation = { __typename?: 'Mutation', generateHql?: { __typename?: 'GenerateHQL', ok?: boolean | null | undefined, hql?: string | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined };

export type SaveHqlTemplateMutationVariables = Exact<{
  name: Scalars['String']['input'];
  content: Scalars['String']['input'];
  category?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
}>;


export type SaveHqlTemplateMutation = { __typename?: 'Mutation', saveHqlTemplate?: { __typename?: 'SaveHQLTemplate', ok?: boolean | null | undefined, templateId?: number | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined };

export type DeleteHqlTemplateMutationVariables = Exact<{
  templateId: Scalars['Int']['input'];
}>;


export type DeleteHqlTemplateMutation = { __typename?: 'Mutation', deleteHqlTemplate?: { __typename?: 'DeleteHQLTemplate', ok?: boolean | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined };

export type BatchAddFieldsToCanvasMutationVariables = Exact<{
  eventId: Scalars['Int']['input'];
  fieldType: FieldTypeEnum;
}>;


export type BatchAddFieldsToCanvasMutation = { __typename?: 'Mutation', batchAddFieldsToCanvas?: { __typename?: 'BatchAddFieldsToCanvasMutation', success?: boolean | null | undefined, message?: string | null | undefined, result?: { __typename?: 'BatchOperationResultType', success: boolean, message?: string | null | undefined, totalCount?: number | null | undefined, successCount?: number | null | undefined, failedCount?: number | null | undefined, errors?: Array<string | null | undefined> | null | undefined } | null | undefined } | null | undefined };

export type ChangeParameterTypeMutationVariables = Exact<{
  parameterId: Scalars['Int']['input'];
  newType: ParameterTypeEnum;
}>;


export type ChangeParameterTypeMutation = { __typename?: 'Mutation', changeParameterType?: { __typename?: 'ChangeParameterTypeMutation', success?: boolean | null | undefined, message?: string | null | undefined, parameter?: { __typename?: 'ParameterManagementType', id: number, paramName: string, paramNameCn?: string | null | undefined, paramType?: ParameterTypeEnum | null | undefined } | null | undefined } | null | undefined };

export type GetGamesQueryVariables = Exact<{
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetGamesQuery = { __typename?: 'Query', games?: Array<{ __typename?: 'GameType', gid: number, name: string, odsDb: string, eventCount?: number | null | undefined, parameterCount?: number | null | undefined } | null | undefined> | null | undefined };

export type GetGameQueryVariables = Exact<{
  gid: Scalars['Int']['input'];
}>;


export type GetGameQuery = { __typename?: 'Query', game?: { __typename?: 'GameType', gid: number, name: string, odsDb: string, eventCount?: number | null | undefined, parameterCount?: number | null | undefined } | null | undefined };

export type SearchGamesQueryVariables = Exact<{
  query: Scalars['String']['input'];
}>;


export type SearchGamesQuery = { __typename?: 'Query', searchGames?: Array<{ __typename?: 'GameType', gid: number, name: string, odsDb: string } | null | undefined> | null | undefined };

export type GetEventsQueryVariables = Exact<{
  gameGid: Scalars['Int']['input'];
  category?: InputMaybe<Scalars['String']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetEventsQuery = { __typename?: 'Query', events?: Array<{ __typename?: 'EventType', id: number, eventName: string, eventNameCn: string, categoryName?: string | null | undefined, paramCount?: number | null | undefined } | null | undefined> | null | undefined };

export type GetEventQueryVariables = Exact<{
  id: Scalars['Int']['input'];
}>;


export type GetEventQuery = { __typename?: 'Query', event?: { __typename?: 'EventType', id: number, gameGid: number, eventName: string, eventNameCn: string, categoryId?: number | null | undefined, categoryName?: string | null | undefined, sourceTable?: string | null | undefined, targetTable?: string | null | undefined, paramCount?: number | null | undefined } | null | undefined };

export type SearchEventsQueryVariables = Exact<{
  query: Scalars['String']['input'];
  gameGid?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SearchEventsQuery = { __typename?: 'Query', searchEvents?: Array<{ __typename?: 'EventType', id: number, eventName: string, eventNameCn: string, gameGid: number } | null | undefined> | null | undefined };

export type GetCategoriesQueryVariables = Exact<{
  limit?: InputMaybe<Scalars['Int']['input']>;
  offset?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetCategoriesQuery = { __typename?: 'Query', categories?: Array<{ __typename?: 'CategoryType', id: number, name: string, eventCount?: number | null | undefined } | null | undefined> | null | undefined };

export type GetCategoryQueryVariables = Exact<{
  id: Scalars['Int']['input'];
}>;


export type GetCategoryQuery = { __typename?: 'Query', category?: { __typename?: 'CategoryType', id: number, name: string, eventCount?: number | null | undefined } | null | undefined };

export type SearchCategoriesQueryVariables = Exact<{
  query: Scalars['String']['input'];
}>;


export type SearchCategoriesQuery = { __typename?: 'Query', searchCategories?: Array<{ __typename?: 'CategoryType', id: number, name: string, eventCount?: number | null | undefined } | null | undefined> | null | undefined };

export type GetParametersQueryVariables = Exact<{
  eventId: Scalars['Int']['input'];
  activeOnly?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type GetParametersQuery = { __typename?: 'Query', parameters?: Array<{ __typename?: 'ParameterType', id: number, eventId: number, paramName: string, paramNameCn?: string | null | undefined, paramType?: string | null | undefined, paramDescription?: string | null | undefined, jsonPath?: string | null | undefined, isActive?: boolean | null | undefined, version?: number | null | undefined } | null | undefined> | null | undefined };

export type GetParameterQueryVariables = Exact<{
  id: Scalars['Int']['input'];
}>;


export type GetParameterQuery = { __typename?: 'Query', parameter?: { __typename?: 'ParameterType', id: number, eventId: number, paramName: string, paramNameCn?: string | null | undefined, paramType?: string | null | undefined, paramDescription?: string | null | undefined, jsonPath?: string | null | undefined, isActive?: boolean | null | undefined, version?: number | null | undefined } | null | undefined };

export type SearchParametersQueryVariables = Exact<{
  query: Scalars['String']['input'];
  eventId?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SearchParametersQuery = { __typename?: 'Query', searchParameters?: Array<{ __typename?: 'ParameterType', id: number, eventId: number, paramName: string, paramNameCn?: string | null | undefined, paramType?: string | null | undefined } | null | undefined> | null | undefined };

export type GetEventFieldsQueryVariables = Exact<{
  eventId: Scalars['Int']['input'];
  fieldType?: InputMaybe<FieldTypeEnum>;
}>;


export type GetEventFieldsQuery = { __typename?: 'Query', eventFields?: Array<{ __typename?: 'FieldTypeType', name: string, displayName?: string | null | undefined, type?: FieldTypeEnum | null | undefined, category?: string | null | undefined, isCommon?: boolean | null | undefined, dataType?: string | null | undefined, jsonPath?: string | null | undefined, usageCount?: number | null | undefined } | null | undefined> | null | undefined };

export type GetCommonParametersQueryVariables = Exact<{
  gameGid: Scalars['Int']['input'];
  threshold?: InputMaybe<Scalars['Float']['input']>;
}>;


export type GetCommonParametersQuery = { __typename?: 'Query', commonParameters?: Array<{ __typename?: 'CommonParameterType', paramName: string, paramType?: string | null | undefined, paramDescription?: string | null | undefined, occurrenceCount: number, totalEvents: number, threshold?: number | null | undefined, eventCodes?: Array<string | null | undefined> | null | undefined, isCommon?: boolean | null | undefined, commonalityScore?: number | null | undefined } | null | undefined> | null | undefined };

export type GetParametersManagementQueryVariables = Exact<{
  gameGid: Scalars['Int']['input'];
  mode?: InputMaybe<ParameterFilterModeEnum>;
  eventId?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetParametersManagementQuery = { __typename?: 'Query', parametersManagement?: Array<{ __typename?: 'ParameterManagementType', id: number, eventId: number, paramName: string, paramNameCn?: string | null | undefined, paramType?: ParameterTypeEnum | null | undefined, paramDescription?: string | null | undefined, jsonPath?: string | null | undefined, isActive?: boolean | null | undefined, version?: number | null | undefined, usageCount?: number | null | undefined, eventsCount?: number | null | undefined, isCommon?: boolean | null | undefined, eventCode?: string | null | undefined, eventName?: string | null | undefined, gameGid?: number | null | undefined, createdAt?: string | null | undefined, updatedAt?: string | null | undefined } | null | undefined> | null | undefined };

export type GetParameterChangesQueryVariables = Exact<{
  gameGid: Scalars['Int']['input'];
  parameterId?: InputMaybe<Scalars['Int']['input']>;
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetParameterChangesQuery = { __typename?: 'Query', parameterChanges?: Array<{ __typename?: 'ParameterChangeType', id: number, parameterId: number, changeType?: string | null | undefined, oldValue?: string | null | undefined, newValue?: string | null | undefined, changedBy?: string | null | undefined, changedAt?: string | null | undefined } | null | undefined> | null | undefined };

export type GetDashboardStatsQueryVariables = Exact<{ [key: string]: never; }>;


export type GetDashboardStatsQuery = { __typename?: 'Query', dashboardStats?: { __typename?: 'DashboardStatsType', totalGames?: number | null | undefined, totalEvents?: number | null | undefined, totalParameters?: number | null | undefined, totalCategories?: number | null | undefined, eventsLast7Days?: number | null | undefined, parametersLast7Days?: number | null | undefined } | null | undefined };

export type GetGameStatsQueryVariables = Exact<{
  gameGid: Scalars['Int']['input'];
}>;


export type GetGameStatsQuery = { __typename?: 'Query', gameStats?: { __typename?: 'GameStatsType', gameGid: number, gameName?: string | null | undefined, eventCount?: number | null | undefined, parameterCount?: number | null | undefined, categoryCount?: number | null | undefined } | null | undefined };

export type GetAllGameStatsQueryVariables = Exact<{
  limit?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetAllGameStatsQuery = { __typename?: 'Query', allGameStats?: Array<{ __typename?: 'GameStatsType', gameGid: number, gameName?: string | null | undefined, eventCount?: number | null | undefined, parameterCount?: number | null | undefined, categoryCount?: number | null | undefined } | null | undefined> | null | undefined };


export const CreateGameDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateGame"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"odsDb"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createGame"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gid"}}},{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}},{"kind":"Argument","name":{"kind":"Name","value":"odsDb"},"value":{"kind":"Variable","name":{"kind":"Name","value":"odsDb"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"game"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"odsDb"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type CreateGameMutationFn = Apollo.MutationFunction<CreateGameMutation, CreateGameMutationVariables>;

/**
 * __useCreateGameMutation__
 *
 * To run a mutation, you first call `useCreateGameMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateGameMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createGameMutation, { data, loading, error }] = useCreateGameMutation({
 *   variables: {
 *      gid: // value for 'gid'
 *      name: // value for 'name'
 *      odsDb: // value for 'odsDb'
 *   },
 * });
 */
export function useCreateGameMutation(baseOptions?: Apollo.MutationHookOptions<CreateGameMutation, CreateGameMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateGameMutation, CreateGameMutationVariables>(CreateGameDocument, options);
      }
export type CreateGameMutationHookResult = ReturnType<typeof useCreateGameMutation>;
export type CreateGameMutationResult = Apollo.MutationResult<CreateGameMutation>;
export type CreateGameMutationOptions = Apollo.BaseMutationOptions<CreateGameMutation, CreateGameMutationVariables>;
export const UpdateGameDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateGame"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"odsDb"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateGame"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gid"}}},{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}},{"kind":"Argument","name":{"kind":"Name","value":"odsDb"},"value":{"kind":"Variable","name":{"kind":"Name","value":"odsDb"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"game"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"odsDb"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type UpdateGameMutationFn = Apollo.MutationFunction<UpdateGameMutation, UpdateGameMutationVariables>;

/**
 * __useUpdateGameMutation__
 *
 * To run a mutation, you first call `useUpdateGameMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateGameMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateGameMutation, { data, loading, error }] = useUpdateGameMutation({
 *   variables: {
 *      gid: // value for 'gid'
 *      name: // value for 'name'
 *      odsDb: // value for 'odsDb'
 *   },
 * });
 */
export function useUpdateGameMutation(baseOptions?: Apollo.MutationHookOptions<UpdateGameMutation, UpdateGameMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateGameMutation, UpdateGameMutationVariables>(UpdateGameDocument, options);
      }
export type UpdateGameMutationHookResult = ReturnType<typeof useUpdateGameMutation>;
export type UpdateGameMutationResult = Apollo.MutationResult<UpdateGameMutation>;
export type UpdateGameMutationOptions = Apollo.BaseMutationOptions<UpdateGameMutation, UpdateGameMutationVariables>;
export const DeleteGameDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteGame"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"confirm"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteGame"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gid"}}},{"kind":"Argument","name":{"kind":"Name","value":"confirm"},"value":{"kind":"Variable","name":{"kind":"Name","value":"confirm"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type DeleteGameMutationFn = Apollo.MutationFunction<DeleteGameMutation, DeleteGameMutationVariables>;

/**
 * __useDeleteGameMutation__
 *
 * To run a mutation, you first call `useDeleteGameMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteGameMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteGameMutation, { data, loading, error }] = useDeleteGameMutation({
 *   variables: {
 *      gid: // value for 'gid'
 *      confirm: // value for 'confirm'
 *   },
 * });
 */
export function useDeleteGameMutation(baseOptions?: Apollo.MutationHookOptions<DeleteGameMutation, DeleteGameMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteGameMutation, DeleteGameMutationVariables>(DeleteGameDocument, options);
      }
export type DeleteGameMutationHookResult = ReturnType<typeof useDeleteGameMutation>;
export type DeleteGameMutationResult = Apollo.MutationResult<DeleteGameMutation>;
export type DeleteGameMutationOptions = Apollo.BaseMutationOptions<DeleteGameMutation, DeleteGameMutationVariables>;
export const CreateEventDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateEvent"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventName"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventNameCn"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"categoryId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"includeInCommonParams"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createEvent"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gameGid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}}},{"kind":"Argument","name":{"kind":"Name","value":"eventName"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventName"}}},{"kind":"Argument","name":{"kind":"Name","value":"eventNameCn"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventNameCn"}}},{"kind":"Argument","name":{"kind":"Name","value":"categoryId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"categoryId"}}},{"kind":"Argument","name":{"kind":"Name","value":"includeInCommonParams"},"value":{"kind":"Variable","name":{"kind":"Name","value":"includeInCommonParams"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"event"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventName"}},{"kind":"Field","name":{"kind":"Name","value":"eventNameCn"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type CreateEventMutationFn = Apollo.MutationFunction<CreateEventMutation, CreateEventMutationVariables>;

/**
 * __useCreateEventMutation__
 *
 * To run a mutation, you first call `useCreateEventMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateEventMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createEventMutation, { data, loading, error }] = useCreateEventMutation({
 *   variables: {
 *      gameGid: // value for 'gameGid'
 *      eventName: // value for 'eventName'
 *      eventNameCn: // value for 'eventNameCn'
 *      categoryId: // value for 'categoryId'
 *      includeInCommonParams: // value for 'includeInCommonParams'
 *   },
 * });
 */
export function useCreateEventMutation(baseOptions?: Apollo.MutationHookOptions<CreateEventMutation, CreateEventMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateEventMutation, CreateEventMutationVariables>(CreateEventDocument, options);
      }
export type CreateEventMutationHookResult = ReturnType<typeof useCreateEventMutation>;
export type CreateEventMutationResult = Apollo.MutationResult<CreateEventMutation>;
export type CreateEventMutationOptions = Apollo.BaseMutationOptions<CreateEventMutation, CreateEventMutationVariables>;
export const UpdateEventDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateEvent"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventNameCn"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"categoryId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"includeInCommonParams"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateEvent"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}},{"kind":"Argument","name":{"kind":"Name","value":"eventNameCn"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventNameCn"}}},{"kind":"Argument","name":{"kind":"Name","value":"categoryId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"categoryId"}}},{"kind":"Argument","name":{"kind":"Name","value":"includeInCommonParams"},"value":{"kind":"Variable","name":{"kind":"Name","value":"includeInCommonParams"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"event"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventNameCn"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type UpdateEventMutationFn = Apollo.MutationFunction<UpdateEventMutation, UpdateEventMutationVariables>;

/**
 * __useUpdateEventMutation__
 *
 * To run a mutation, you first call `useUpdateEventMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateEventMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateEventMutation, { data, loading, error }] = useUpdateEventMutation({
 *   variables: {
 *      id: // value for 'id'
 *      eventNameCn: // value for 'eventNameCn'
 *      categoryId: // value for 'categoryId'
 *      includeInCommonParams: // value for 'includeInCommonParams'
 *   },
 * });
 */
export function useUpdateEventMutation(baseOptions?: Apollo.MutationHookOptions<UpdateEventMutation, UpdateEventMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateEventMutation, UpdateEventMutationVariables>(UpdateEventDocument, options);
      }
export type UpdateEventMutationHookResult = ReturnType<typeof useUpdateEventMutation>;
export type UpdateEventMutationResult = Apollo.MutationResult<UpdateEventMutation>;
export type UpdateEventMutationOptions = Apollo.BaseMutationOptions<UpdateEventMutation, UpdateEventMutationVariables>;
export const DeleteEventDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteEvent"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteEvent"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type DeleteEventMutationFn = Apollo.MutationFunction<DeleteEventMutation, DeleteEventMutationVariables>;

/**
 * __useDeleteEventMutation__
 *
 * To run a mutation, you first call `useDeleteEventMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteEventMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteEventMutation, { data, loading, error }] = useDeleteEventMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useDeleteEventMutation(baseOptions?: Apollo.MutationHookOptions<DeleteEventMutation, DeleteEventMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteEventMutation, DeleteEventMutationVariables>(DeleteEventDocument, options);
      }
export type DeleteEventMutationHookResult = ReturnType<typeof useDeleteEventMutation>;
export type DeleteEventMutationResult = Apollo.MutationResult<DeleteEventMutation>;
export type DeleteEventMutationOptions = Apollo.BaseMutationOptions<DeleteEventMutation, DeleteEventMutationVariables>;
export const CreateParameterDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateParameter"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"paramName"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"paramNameCn"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"isActive"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"jsonPath"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"templateId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createParameter"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"eventId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}}},{"kind":"Argument","name":{"kind":"Name","value":"paramName"},"value":{"kind":"Variable","name":{"kind":"Name","value":"paramName"}}},{"kind":"Argument","name":{"kind":"Name","value":"paramNameCn"},"value":{"kind":"Variable","name":{"kind":"Name","value":"paramNameCn"}}},{"kind":"Argument","name":{"kind":"Name","value":"isActive"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isActive"}}},{"kind":"Argument","name":{"kind":"Name","value":"jsonPath"},"value":{"kind":"Variable","name":{"kind":"Name","value":"jsonPath"}}},{"kind":"Argument","name":{"kind":"Name","value":"templateId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"templateId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"parameter"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventId"}},{"kind":"Field","name":{"kind":"Name","value":"paramName"}},{"kind":"Field","name":{"kind":"Name","value":"paramNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"jsonPath"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type CreateParameterMutationFn = Apollo.MutationFunction<CreateParameterMutation, CreateParameterMutationVariables>;

/**
 * __useCreateParameterMutation__
 *
 * To run a mutation, you first call `useCreateParameterMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateParameterMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createParameterMutation, { data, loading, error }] = useCreateParameterMutation({
 *   variables: {
 *      eventId: // value for 'eventId'
 *      paramName: // value for 'paramName'
 *      paramNameCn: // value for 'paramNameCn'
 *      isActive: // value for 'isActive'
 *      jsonPath: // value for 'jsonPath'
 *      templateId: // value for 'templateId'
 *   },
 * });
 */
export function useCreateParameterMutation(baseOptions?: Apollo.MutationHookOptions<CreateParameterMutation, CreateParameterMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateParameterMutation, CreateParameterMutationVariables>(CreateParameterDocument, options);
      }
export type CreateParameterMutationHookResult = ReturnType<typeof useCreateParameterMutation>;
export type CreateParameterMutationResult = Apollo.MutationResult<CreateParameterMutation>;
export type CreateParameterMutationOptions = Apollo.BaseMutationOptions<CreateParameterMutation, CreateParameterMutationVariables>;
export const UpdateParameterDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateParameter"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"paramNameCn"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"isActive"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"jsonPath"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"templateId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateParameter"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}},{"kind":"Argument","name":{"kind":"Name","value":"paramNameCn"},"value":{"kind":"Variable","name":{"kind":"Name","value":"paramNameCn"}}},{"kind":"Argument","name":{"kind":"Name","value":"isActive"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isActive"}}},{"kind":"Argument","name":{"kind":"Name","value":"jsonPath"},"value":{"kind":"Variable","name":{"kind":"Name","value":"jsonPath"}}},{"kind":"Argument","name":{"kind":"Name","value":"templateId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"templateId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"parameter"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"paramNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"jsonPath"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type UpdateParameterMutationFn = Apollo.MutationFunction<UpdateParameterMutation, UpdateParameterMutationVariables>;

/**
 * __useUpdateParameterMutation__
 *
 * To run a mutation, you first call `useUpdateParameterMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateParameterMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateParameterMutation, { data, loading, error }] = useUpdateParameterMutation({
 *   variables: {
 *      id: // value for 'id'
 *      paramNameCn: // value for 'paramNameCn'
 *      isActive: // value for 'isActive'
 *      jsonPath: // value for 'jsonPath'
 *      templateId: // value for 'templateId'
 *   },
 * });
 */
export function useUpdateParameterMutation(baseOptions?: Apollo.MutationHookOptions<UpdateParameterMutation, UpdateParameterMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateParameterMutation, UpdateParameterMutationVariables>(UpdateParameterDocument, options);
      }
export type UpdateParameterMutationHookResult = ReturnType<typeof useUpdateParameterMutation>;
export type UpdateParameterMutationResult = Apollo.MutationResult<UpdateParameterMutation>;
export type UpdateParameterMutationOptions = Apollo.BaseMutationOptions<UpdateParameterMutation, UpdateParameterMutationVariables>;
export const DeleteParameterDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteParameter"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteParameter"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type DeleteParameterMutationFn = Apollo.MutationFunction<DeleteParameterMutation, DeleteParameterMutationVariables>;

/**
 * __useDeleteParameterMutation__
 *
 * To run a mutation, you first call `useDeleteParameterMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteParameterMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteParameterMutation, { data, loading, error }] = useDeleteParameterMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useDeleteParameterMutation(baseOptions?: Apollo.MutationHookOptions<DeleteParameterMutation, DeleteParameterMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteParameterMutation, DeleteParameterMutationVariables>(DeleteParameterDocument, options);
      }
export type DeleteParameterMutationHookResult = ReturnType<typeof useDeleteParameterMutation>;
export type DeleteParameterMutationResult = Apollo.MutationResult<DeleteParameterMutation>;
export type DeleteParameterMutationOptions = Apollo.BaseMutationOptions<DeleteParameterMutation, DeleteParameterMutationVariables>;
export const CreateCategoryDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateCategory"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createCategory"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"category"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type CreateCategoryMutationFn = Apollo.MutationFunction<CreateCategoryMutation, CreateCategoryMutationVariables>;

/**
 * __useCreateCategoryMutation__
 *
 * To run a mutation, you first call `useCreateCategoryMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateCategoryMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createCategoryMutation, { data, loading, error }] = useCreateCategoryMutation({
 *   variables: {
 *      name: // value for 'name'
 *   },
 * });
 */
export function useCreateCategoryMutation(baseOptions?: Apollo.MutationHookOptions<CreateCategoryMutation, CreateCategoryMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<CreateCategoryMutation, CreateCategoryMutationVariables>(CreateCategoryDocument, options);
      }
export type CreateCategoryMutationHookResult = ReturnType<typeof useCreateCategoryMutation>;
export type CreateCategoryMutationResult = Apollo.MutationResult<CreateCategoryMutation>;
export type CreateCategoryMutationOptions = Apollo.BaseMutationOptions<CreateCategoryMutation, CreateCategoryMutationVariables>;
export const UpdateCategoryDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateCategory"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateCategory"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}},{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"category"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type UpdateCategoryMutationFn = Apollo.MutationFunction<UpdateCategoryMutation, UpdateCategoryMutationVariables>;

/**
 * __useUpdateCategoryMutation__
 *
 * To run a mutation, you first call `useUpdateCategoryMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateCategoryMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateCategoryMutation, { data, loading, error }] = useUpdateCategoryMutation({
 *   variables: {
 *      id: // value for 'id'
 *      name: // value for 'name'
 *   },
 * });
 */
export function useUpdateCategoryMutation(baseOptions?: Apollo.MutationHookOptions<UpdateCategoryMutation, UpdateCategoryMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<UpdateCategoryMutation, UpdateCategoryMutationVariables>(UpdateCategoryDocument, options);
      }
export type UpdateCategoryMutationHookResult = ReturnType<typeof useUpdateCategoryMutation>;
export type UpdateCategoryMutationResult = Apollo.MutationResult<UpdateCategoryMutation>;
export type UpdateCategoryMutationOptions = Apollo.BaseMutationOptions<UpdateCategoryMutation, UpdateCategoryMutationVariables>;
export const DeleteCategoryDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteCategory"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteCategory"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type DeleteCategoryMutationFn = Apollo.MutationFunction<DeleteCategoryMutation, DeleteCategoryMutationVariables>;

/**
 * __useDeleteCategoryMutation__
 *
 * To run a mutation, you first call `useDeleteCategoryMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteCategoryMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteCategoryMutation, { data, loading, error }] = useDeleteCategoryMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useDeleteCategoryMutation(baseOptions?: Apollo.MutationHookOptions<DeleteCategoryMutation, DeleteCategoryMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteCategoryMutation, DeleteCategoryMutationVariables>(DeleteCategoryDocument, options);
      }
export type DeleteCategoryMutationHookResult = ReturnType<typeof useDeleteCategoryMutation>;
export type DeleteCategoryMutationResult = Apollo.MutationResult<DeleteCategoryMutation>;
export type DeleteCategoryMutationOptions = Apollo.BaseMutationOptions<DeleteCategoryMutation, DeleteCategoryMutationVariables>;
export const GenerateHqlDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"GenerateHQL"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventIds"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"mode"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"options"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"generateHql"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"eventIds"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventIds"}}},{"kind":"Argument","name":{"kind":"Name","value":"mode"},"value":{"kind":"Variable","name":{"kind":"Name","value":"mode"}}},{"kind":"Argument","name":{"kind":"Name","value":"options"},"value":{"kind":"Variable","name":{"kind":"Name","value":"options"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"hql"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type GenerateHqlMutationFn = Apollo.MutationFunction<GenerateHqlMutation, GenerateHqlMutationVariables>;

/**
 * __useGenerateHqlMutation__
 *
 * To run a mutation, you first call `useGenerateHqlMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useGenerateHqlMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [generateHqlMutation, { data, loading, error }] = useGenerateHqlMutation({
 *   variables: {
 *      eventIds: // value for 'eventIds'
 *      mode: // value for 'mode'
 *      options: // value for 'options'
 *   },
 * });
 */
export function useGenerateHqlMutation(baseOptions?: Apollo.MutationHookOptions<GenerateHqlMutation, GenerateHqlMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<GenerateHqlMutation, GenerateHqlMutationVariables>(GenerateHqlDocument, options);
      }
export type GenerateHqlMutationHookResult = ReturnType<typeof useGenerateHqlMutation>;
export type GenerateHqlMutationResult = Apollo.MutationResult<GenerateHqlMutation>;
export type GenerateHqlMutationOptions = Apollo.BaseMutationOptions<GenerateHqlMutation, GenerateHqlMutationVariables>;
export const SaveHqlTemplateDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SaveHQLTemplate"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"name"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"content"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"category"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"description"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"saveHqlTemplate"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"name"}}},{"kind":"Argument","name":{"kind":"Name","value":"content"},"value":{"kind":"Variable","name":{"kind":"Name","value":"content"}}},{"kind":"Argument","name":{"kind":"Name","value":"category"},"value":{"kind":"Variable","name":{"kind":"Name","value":"category"}}},{"kind":"Argument","name":{"kind":"Name","value":"description"},"value":{"kind":"Variable","name":{"kind":"Name","value":"description"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"templateId"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type SaveHqlTemplateMutationFn = Apollo.MutationFunction<SaveHqlTemplateMutation, SaveHqlTemplateMutationVariables>;

/**
 * __useSaveHqlTemplateMutation__
 *
 * To run a mutation, you first call `useSaveHqlTemplateMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSaveHqlTemplateMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [saveHqlTemplateMutation, { data, loading, error }] = useSaveHqlTemplateMutation({
 *   variables: {
 *      name: // value for 'name'
 *      content: // value for 'content'
 *      category: // value for 'category'
 *      description: // value for 'description'
 *   },
 * });
 */
export function useSaveHqlTemplateMutation(baseOptions?: Apollo.MutationHookOptions<SaveHqlTemplateMutation, SaveHqlTemplateMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SaveHqlTemplateMutation, SaveHqlTemplateMutationVariables>(SaveHqlTemplateDocument, options);
      }
export type SaveHqlTemplateMutationHookResult = ReturnType<typeof useSaveHqlTemplateMutation>;
export type SaveHqlTemplateMutationResult = Apollo.MutationResult<SaveHqlTemplateMutation>;
export type SaveHqlTemplateMutationOptions = Apollo.BaseMutationOptions<SaveHqlTemplateMutation, SaveHqlTemplateMutationVariables>;
export const DeleteHqlTemplateDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteHQLTemplate"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"templateId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteHqlTemplate"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"templateId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"templateId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"ok"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode;
export type DeleteHqlTemplateMutationFn = Apollo.MutationFunction<DeleteHqlTemplateMutation, DeleteHqlTemplateMutationVariables>;

/**
 * __useDeleteHqlTemplateMutation__
 *
 * To run a mutation, you first call `useDeleteHqlTemplateMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteHqlTemplateMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteHqlTemplateMutation, { data, loading, error }] = useDeleteHqlTemplateMutation({
 *   variables: {
 *      templateId: // value for 'templateId'
 *   },
 * });
 */
export function useDeleteHqlTemplateMutation(baseOptions?: Apollo.MutationHookOptions<DeleteHqlTemplateMutation, DeleteHqlTemplateMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<DeleteHqlTemplateMutation, DeleteHqlTemplateMutationVariables>(DeleteHqlTemplateDocument, options);
      }
export type DeleteHqlTemplateMutationHookResult = ReturnType<typeof useDeleteHqlTemplateMutation>;
export type DeleteHqlTemplateMutationResult = Apollo.MutationResult<DeleteHqlTemplateMutation>;
export type DeleteHqlTemplateMutationOptions = Apollo.BaseMutationOptions<DeleteHqlTemplateMutation, DeleteHqlTemplateMutationVariables>;
export const BatchAddFieldsToCanvasDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"BatchAddFieldsToCanvas"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"fieldType"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"FieldTypeEnum"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"batchAddFieldsToCanvas"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"eventId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}}},{"kind":"Argument","name":{"kind":"Name","value":"fieldType"},"value":{"kind":"Variable","name":{"kind":"Name","value":"fieldType"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"result"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"totalCount"}},{"kind":"Field","name":{"kind":"Name","value":"successCount"}},{"kind":"Field","name":{"kind":"Name","value":"failedCount"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]}}]} as unknown as DocumentNode;
export type BatchAddFieldsToCanvasMutationFn = Apollo.MutationFunction<BatchAddFieldsToCanvasMutation, BatchAddFieldsToCanvasMutationVariables>;

/**
 * __useBatchAddFieldsToCanvasMutation__
 *
 * To run a mutation, you first call `useBatchAddFieldsToCanvasMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useBatchAddFieldsToCanvasMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [batchAddFieldsToCanvasMutation, { data, loading, error }] = useBatchAddFieldsToCanvasMutation({
 *   variables: {
 *      eventId: // value for 'eventId'
 *      fieldType: // value for 'fieldType'
 *   },
 * });
 */
export function useBatchAddFieldsToCanvasMutation(baseOptions?: Apollo.MutationHookOptions<BatchAddFieldsToCanvasMutation, BatchAddFieldsToCanvasMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<BatchAddFieldsToCanvasMutation, BatchAddFieldsToCanvasMutationVariables>(BatchAddFieldsToCanvasDocument, options);
      }
export type BatchAddFieldsToCanvasMutationHookResult = ReturnType<typeof useBatchAddFieldsToCanvasMutation>;
export type BatchAddFieldsToCanvasMutationResult = Apollo.MutationResult<BatchAddFieldsToCanvasMutation>;
export type BatchAddFieldsToCanvasMutationOptions = Apollo.BaseMutationOptions<BatchAddFieldsToCanvasMutation, BatchAddFieldsToCanvasMutationVariables>;
export const ChangeParameterTypeDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ChangeParameterType"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"parameterId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"newType"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ParameterTypeEnum"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"changeParameterType"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"parameterId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"parameterId"}}},{"kind":"Argument","name":{"kind":"Name","value":"newType"},"value":{"kind":"Variable","name":{"kind":"Name","value":"newType"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"parameter"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"paramName"}},{"kind":"Field","name":{"kind":"Name","value":"paramNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"paramType"}}]}}]}}]}}]} as unknown as DocumentNode;
export type ChangeParameterTypeMutationFn = Apollo.MutationFunction<ChangeParameterTypeMutation, ChangeParameterTypeMutationVariables>;

/**
 * __useChangeParameterTypeMutation__
 *
 * To run a mutation, you first call `useChangeParameterTypeMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useChangeParameterTypeMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [changeParameterTypeMutation, { data, loading, error }] = useChangeParameterTypeMutation({
 *   variables: {
 *      parameterId: // value for 'parameterId'
 *      newType: // value for 'newType'
 *   },
 * });
 */
export function useChangeParameterTypeMutation(baseOptions?: Apollo.MutationHookOptions<ChangeParameterTypeMutation, ChangeParameterTypeMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ChangeParameterTypeMutation, ChangeParameterTypeMutationVariables>(ChangeParameterTypeDocument, options);
      }
export type ChangeParameterTypeMutationHookResult = ReturnType<typeof useChangeParameterTypeMutation>;
export type ChangeParameterTypeMutationResult = Apollo.MutationResult<ChangeParameterTypeMutation>;
export type ChangeParameterTypeMutationOptions = Apollo.BaseMutationOptions<ChangeParameterTypeMutation, ChangeParameterTypeMutationVariables>;
export const GetGamesDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetGames"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"limit"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"offset"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"games"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"limit"},"value":{"kind":"Variable","name":{"kind":"Name","value":"limit"}}},{"kind":"Argument","name":{"kind":"Name","value":"offset"},"value":{"kind":"Variable","name":{"kind":"Name","value":"offset"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"odsDb"}},{"kind":"Field","name":{"kind":"Name","value":"eventCount"}},{"kind":"Field","name":{"kind":"Name","value":"parameterCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetGamesQuery__
 *
 * To run a query within a React component, call `useGetGamesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetGamesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetGamesQuery({
 *   variables: {
 *      limit: // value for 'limit'
 *      offset: // value for 'offset'
 *   },
 * });
 */
export function useGetGamesQuery(baseOptions?: Apollo.QueryHookOptions<GetGamesQuery, GetGamesQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetGamesQuery, GetGamesQueryVariables>(GetGamesDocument, options);
      }
export function useGetGamesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetGamesQuery, GetGamesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetGamesQuery, GetGamesQueryVariables>(GetGamesDocument, options);
        }
// @ts-ignore
export function useGetGamesSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetGamesQuery, GetGamesQueryVariables>): Apollo.UseSuspenseQueryResult<GetGamesQuery, GetGamesQueryVariables>;
export function useGetGamesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetGamesQuery, GetGamesQueryVariables>): Apollo.UseSuspenseQueryResult<GetGamesQuery | undefined, GetGamesQueryVariables>;
export function useGetGamesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetGamesQuery, GetGamesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetGamesQuery, GetGamesQueryVariables>(GetGamesDocument, options);
        }
export type GetGamesQueryHookResult = ReturnType<typeof useGetGamesQuery>;
export type GetGamesLazyQueryHookResult = ReturnType<typeof useGetGamesLazyQuery>;
export type GetGamesSuspenseQueryHookResult = ReturnType<typeof useGetGamesSuspenseQuery>;
export type GetGamesQueryResult = Apollo.QueryResult<GetGamesQuery, GetGamesQueryVariables>;
export const GetGameDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetGame"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"game"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gid"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"odsDb"}},{"kind":"Field","name":{"kind":"Name","value":"eventCount"}},{"kind":"Field","name":{"kind":"Name","value":"parameterCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetGameQuery__
 *
 * To run a query within a React component, call `useGetGameQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetGameQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetGameQuery({
 *   variables: {
 *      gid: // value for 'gid'
 *   },
 * });
 */
export function useGetGameQuery(baseOptions: Apollo.QueryHookOptions<GetGameQuery, GetGameQueryVariables> & ({ variables: GetGameQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetGameQuery, GetGameQueryVariables>(GetGameDocument, options);
      }
export function useGetGameLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetGameQuery, GetGameQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetGameQuery, GetGameQueryVariables>(GetGameDocument, options);
        }
// @ts-ignore
export function useGetGameSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetGameQuery, GetGameQueryVariables>): Apollo.UseSuspenseQueryResult<GetGameQuery, GetGameQueryVariables>;
export function useGetGameSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetGameQuery, GetGameQueryVariables>): Apollo.UseSuspenseQueryResult<GetGameQuery | undefined, GetGameQueryVariables>;
export function useGetGameSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetGameQuery, GetGameQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetGameQuery, GetGameQueryVariables>(GetGameDocument, options);
        }
export type GetGameQueryHookResult = ReturnType<typeof useGetGameQuery>;
export type GetGameLazyQueryHookResult = ReturnType<typeof useGetGameLazyQuery>;
export type GetGameSuspenseQueryHookResult = ReturnType<typeof useGetGameSuspenseQuery>;
export type GetGameQueryResult = Apollo.QueryResult<GetGameQuery, GetGameQueryVariables>;
export const SearchGamesDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchGames"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"searchGames"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gid"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"odsDb"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useSearchGamesQuery__
 *
 * To run a query within a React component, call `useSearchGamesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchGamesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchGamesQuery({
 *   variables: {
 *      query: // value for 'query'
 *   },
 * });
 */
export function useSearchGamesQuery(baseOptions: Apollo.QueryHookOptions<SearchGamesQuery, SearchGamesQueryVariables> & ({ variables: SearchGamesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchGamesQuery, SearchGamesQueryVariables>(SearchGamesDocument, options);
      }
export function useSearchGamesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchGamesQuery, SearchGamesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchGamesQuery, SearchGamesQueryVariables>(SearchGamesDocument, options);
        }
// @ts-ignore
export function useSearchGamesSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<SearchGamesQuery, SearchGamesQueryVariables>): Apollo.UseSuspenseQueryResult<SearchGamesQuery, SearchGamesQueryVariables>;
export function useSearchGamesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchGamesQuery, SearchGamesQueryVariables>): Apollo.UseSuspenseQueryResult<SearchGamesQuery | undefined, SearchGamesQueryVariables>;
export function useSearchGamesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchGamesQuery, SearchGamesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchGamesQuery, SearchGamesQueryVariables>(SearchGamesDocument, options);
        }
export type SearchGamesQueryHookResult = ReturnType<typeof useSearchGamesQuery>;
export type SearchGamesLazyQueryHookResult = ReturnType<typeof useSearchGamesLazyQuery>;
export type SearchGamesSuspenseQueryHookResult = ReturnType<typeof useSearchGamesSuspenseQuery>;
export type SearchGamesQueryResult = Apollo.QueryResult<SearchGamesQuery, SearchGamesQueryVariables>;
export const GetEventsDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetEvents"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"category"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"limit"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"offset"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"events"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gameGid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}}},{"kind":"Argument","name":{"kind":"Name","value":"category"},"value":{"kind":"Variable","name":{"kind":"Name","value":"category"}}},{"kind":"Argument","name":{"kind":"Name","value":"limit"},"value":{"kind":"Variable","name":{"kind":"Name","value":"limit"}}},{"kind":"Argument","name":{"kind":"Name","value":"offset"},"value":{"kind":"Variable","name":{"kind":"Name","value":"offset"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventName"}},{"kind":"Field","name":{"kind":"Name","value":"eventNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"categoryName"}},{"kind":"Field","name":{"kind":"Name","value":"paramCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetEventsQuery__
 *
 * To run a query within a React component, call `useGetEventsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetEventsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetEventsQuery({
 *   variables: {
 *      gameGid: // value for 'gameGid'
 *      category: // value for 'category'
 *      limit: // value for 'limit'
 *      offset: // value for 'offset'
 *   },
 * });
 */
export function useGetEventsQuery(baseOptions: Apollo.QueryHookOptions<GetEventsQuery, GetEventsQueryVariables> & ({ variables: GetEventsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetEventsQuery, GetEventsQueryVariables>(GetEventsDocument, options);
      }
export function useGetEventsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetEventsQuery, GetEventsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetEventsQuery, GetEventsQueryVariables>(GetEventsDocument, options);
        }
// @ts-ignore
export function useGetEventsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetEventsQuery, GetEventsQueryVariables>): Apollo.UseSuspenseQueryResult<GetEventsQuery, GetEventsQueryVariables>;
export function useGetEventsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetEventsQuery, GetEventsQueryVariables>): Apollo.UseSuspenseQueryResult<GetEventsQuery | undefined, GetEventsQueryVariables>;
export function useGetEventsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetEventsQuery, GetEventsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetEventsQuery, GetEventsQueryVariables>(GetEventsDocument, options);
        }
export type GetEventsQueryHookResult = ReturnType<typeof useGetEventsQuery>;
export type GetEventsLazyQueryHookResult = ReturnType<typeof useGetEventsLazyQuery>;
export type GetEventsSuspenseQueryHookResult = ReturnType<typeof useGetEventsSuspenseQuery>;
export type GetEventsQueryResult = Apollo.QueryResult<GetEventsQuery, GetEventsQueryVariables>;
export const GetEventDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetEvent"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"event"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"gameGid"}},{"kind":"Field","name":{"kind":"Name","value":"eventName"}},{"kind":"Field","name":{"kind":"Name","value":"eventNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"categoryId"}},{"kind":"Field","name":{"kind":"Name","value":"categoryName"}},{"kind":"Field","name":{"kind":"Name","value":"sourceTable"}},{"kind":"Field","name":{"kind":"Name","value":"targetTable"}},{"kind":"Field","name":{"kind":"Name","value":"paramCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetEventQuery__
 *
 * To run a query within a React component, call `useGetEventQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetEventQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetEventQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetEventQuery(baseOptions: Apollo.QueryHookOptions<GetEventQuery, GetEventQueryVariables> & ({ variables: GetEventQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetEventQuery, GetEventQueryVariables>(GetEventDocument, options);
      }
export function useGetEventLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetEventQuery, GetEventQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetEventQuery, GetEventQueryVariables>(GetEventDocument, options);
        }
// @ts-ignore
export function useGetEventSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetEventQuery, GetEventQueryVariables>): Apollo.UseSuspenseQueryResult<GetEventQuery, GetEventQueryVariables>;
export function useGetEventSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetEventQuery, GetEventQueryVariables>): Apollo.UseSuspenseQueryResult<GetEventQuery | undefined, GetEventQueryVariables>;
export function useGetEventSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetEventQuery, GetEventQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetEventQuery, GetEventQueryVariables>(GetEventDocument, options);
        }
export type GetEventQueryHookResult = ReturnType<typeof useGetEventQuery>;
export type GetEventLazyQueryHookResult = ReturnType<typeof useGetEventLazyQuery>;
export type GetEventSuspenseQueryHookResult = ReturnType<typeof useGetEventSuspenseQuery>;
export type GetEventQueryResult = Apollo.QueryResult<GetEventQuery, GetEventQueryVariables>;
export const SearchEventsDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchEvents"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"searchEvents"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"gameGid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventName"}},{"kind":"Field","name":{"kind":"Name","value":"eventNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"gameGid"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useSearchEventsQuery__
 *
 * To run a query within a React component, call `useSearchEventsQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchEventsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchEventsQuery({
 *   variables: {
 *      query: // value for 'query'
 *      gameGid: // value for 'gameGid'
 *   },
 * });
 */
export function useSearchEventsQuery(baseOptions: Apollo.QueryHookOptions<SearchEventsQuery, SearchEventsQueryVariables> & ({ variables: SearchEventsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchEventsQuery, SearchEventsQueryVariables>(SearchEventsDocument, options);
      }
export function useSearchEventsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchEventsQuery, SearchEventsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchEventsQuery, SearchEventsQueryVariables>(SearchEventsDocument, options);
        }
// @ts-ignore
export function useSearchEventsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<SearchEventsQuery, SearchEventsQueryVariables>): Apollo.UseSuspenseQueryResult<SearchEventsQuery, SearchEventsQueryVariables>;
export function useSearchEventsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchEventsQuery, SearchEventsQueryVariables>): Apollo.UseSuspenseQueryResult<SearchEventsQuery | undefined, SearchEventsQueryVariables>;
export function useSearchEventsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchEventsQuery, SearchEventsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchEventsQuery, SearchEventsQueryVariables>(SearchEventsDocument, options);
        }
export type SearchEventsQueryHookResult = ReturnType<typeof useSearchEventsQuery>;
export type SearchEventsLazyQueryHookResult = ReturnType<typeof useSearchEventsLazyQuery>;
export type SearchEventsSuspenseQueryHookResult = ReturnType<typeof useSearchEventsSuspenseQuery>;
export type SearchEventsQueryResult = Apollo.QueryResult<SearchEventsQuery, SearchEventsQueryVariables>;
export const GetCategoriesDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetCategories"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"limit"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"offset"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"categories"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"limit"},"value":{"kind":"Variable","name":{"kind":"Name","value":"limit"}}},{"kind":"Argument","name":{"kind":"Name","value":"offset"},"value":{"kind":"Variable","name":{"kind":"Name","value":"offset"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"eventCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetCategoriesQuery__
 *
 * To run a query within a React component, call `useGetCategoriesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetCategoriesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetCategoriesQuery({
 *   variables: {
 *      limit: // value for 'limit'
 *      offset: // value for 'offset'
 *   },
 * });
 */
export function useGetCategoriesQuery(baseOptions?: Apollo.QueryHookOptions<GetCategoriesQuery, GetCategoriesQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetCategoriesQuery, GetCategoriesQueryVariables>(GetCategoriesDocument, options);
      }
export function useGetCategoriesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetCategoriesQuery, GetCategoriesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetCategoriesQuery, GetCategoriesQueryVariables>(GetCategoriesDocument, options);
        }
// @ts-ignore
export function useGetCategoriesSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetCategoriesQuery, GetCategoriesQueryVariables>): Apollo.UseSuspenseQueryResult<GetCategoriesQuery, GetCategoriesQueryVariables>;
export function useGetCategoriesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCategoriesQuery, GetCategoriesQueryVariables>): Apollo.UseSuspenseQueryResult<GetCategoriesQuery | undefined, GetCategoriesQueryVariables>;
export function useGetCategoriesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCategoriesQuery, GetCategoriesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetCategoriesQuery, GetCategoriesQueryVariables>(GetCategoriesDocument, options);
        }
export type GetCategoriesQueryHookResult = ReturnType<typeof useGetCategoriesQuery>;
export type GetCategoriesLazyQueryHookResult = ReturnType<typeof useGetCategoriesLazyQuery>;
export type GetCategoriesSuspenseQueryHookResult = ReturnType<typeof useGetCategoriesSuspenseQuery>;
export type GetCategoriesQueryResult = Apollo.QueryResult<GetCategoriesQuery, GetCategoriesQueryVariables>;
export const GetCategoryDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetCategory"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"category"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"eventCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetCategoryQuery__
 *
 * To run a query within a React component, call `useGetCategoryQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetCategoryQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetCategoryQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetCategoryQuery(baseOptions: Apollo.QueryHookOptions<GetCategoryQuery, GetCategoryQueryVariables> & ({ variables: GetCategoryQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetCategoryQuery, GetCategoryQueryVariables>(GetCategoryDocument, options);
      }
export function useGetCategoryLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetCategoryQuery, GetCategoryQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetCategoryQuery, GetCategoryQueryVariables>(GetCategoryDocument, options);
        }
// @ts-ignore
export function useGetCategorySuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetCategoryQuery, GetCategoryQueryVariables>): Apollo.UseSuspenseQueryResult<GetCategoryQuery, GetCategoryQueryVariables>;
export function useGetCategorySuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCategoryQuery, GetCategoryQueryVariables>): Apollo.UseSuspenseQueryResult<GetCategoryQuery | undefined, GetCategoryQueryVariables>;
export function useGetCategorySuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCategoryQuery, GetCategoryQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetCategoryQuery, GetCategoryQueryVariables>(GetCategoryDocument, options);
        }
export type GetCategoryQueryHookResult = ReturnType<typeof useGetCategoryQuery>;
export type GetCategoryLazyQueryHookResult = ReturnType<typeof useGetCategoryLazyQuery>;
export type GetCategorySuspenseQueryHookResult = ReturnType<typeof useGetCategorySuspenseQuery>;
export type GetCategoryQueryResult = Apollo.QueryResult<GetCategoryQuery, GetCategoryQueryVariables>;
export const SearchCategoriesDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchCategories"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"searchCategories"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"eventCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useSearchCategoriesQuery__
 *
 * To run a query within a React component, call `useSearchCategoriesQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchCategoriesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchCategoriesQuery({
 *   variables: {
 *      query: // value for 'query'
 *   },
 * });
 */
export function useSearchCategoriesQuery(baseOptions: Apollo.QueryHookOptions<SearchCategoriesQuery, SearchCategoriesQueryVariables> & ({ variables: SearchCategoriesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchCategoriesQuery, SearchCategoriesQueryVariables>(SearchCategoriesDocument, options);
      }
export function useSearchCategoriesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchCategoriesQuery, SearchCategoriesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchCategoriesQuery, SearchCategoriesQueryVariables>(SearchCategoriesDocument, options);
        }
// @ts-ignore
export function useSearchCategoriesSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<SearchCategoriesQuery, SearchCategoriesQueryVariables>): Apollo.UseSuspenseQueryResult<SearchCategoriesQuery, SearchCategoriesQueryVariables>;
export function useSearchCategoriesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchCategoriesQuery, SearchCategoriesQueryVariables>): Apollo.UseSuspenseQueryResult<SearchCategoriesQuery | undefined, SearchCategoriesQueryVariables>;
export function useSearchCategoriesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchCategoriesQuery, SearchCategoriesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchCategoriesQuery, SearchCategoriesQueryVariables>(SearchCategoriesDocument, options);
        }
export type SearchCategoriesQueryHookResult = ReturnType<typeof useSearchCategoriesQuery>;
export type SearchCategoriesLazyQueryHookResult = ReturnType<typeof useSearchCategoriesLazyQuery>;
export type SearchCategoriesSuspenseQueryHookResult = ReturnType<typeof useSearchCategoriesSuspenseQuery>;
export type SearchCategoriesQueryResult = Apollo.QueryResult<SearchCategoriesQuery, SearchCategoriesQueryVariables>;
export const GetParametersDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetParameters"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"activeOnly"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"parameters"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"eventId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}}},{"kind":"Argument","name":{"kind":"Name","value":"activeOnly"},"value":{"kind":"Variable","name":{"kind":"Name","value":"activeOnly"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventId"}},{"kind":"Field","name":{"kind":"Name","value":"paramName"}},{"kind":"Field","name":{"kind":"Name","value":"paramNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"paramType"}},{"kind":"Field","name":{"kind":"Name","value":"paramDescription"}},{"kind":"Field","name":{"kind":"Name","value":"jsonPath"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"version"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetParametersQuery__
 *
 * To run a query within a React component, call `useGetParametersQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetParametersQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetParametersQuery({
 *   variables: {
 *      eventId: // value for 'eventId'
 *      activeOnly: // value for 'activeOnly'
 *   },
 * });
 */
export function useGetParametersQuery(baseOptions: Apollo.QueryHookOptions<GetParametersQuery, GetParametersQueryVariables> & ({ variables: GetParametersQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetParametersQuery, GetParametersQueryVariables>(GetParametersDocument, options);
      }
export function useGetParametersLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetParametersQuery, GetParametersQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetParametersQuery, GetParametersQueryVariables>(GetParametersDocument, options);
        }
// @ts-ignore
export function useGetParametersSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetParametersQuery, GetParametersQueryVariables>): Apollo.UseSuspenseQueryResult<GetParametersQuery, GetParametersQueryVariables>;
export function useGetParametersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParametersQuery, GetParametersQueryVariables>): Apollo.UseSuspenseQueryResult<GetParametersQuery | undefined, GetParametersQueryVariables>;
export function useGetParametersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParametersQuery, GetParametersQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetParametersQuery, GetParametersQueryVariables>(GetParametersDocument, options);
        }
export type GetParametersQueryHookResult = ReturnType<typeof useGetParametersQuery>;
export type GetParametersLazyQueryHookResult = ReturnType<typeof useGetParametersLazyQuery>;
export type GetParametersSuspenseQueryHookResult = ReturnType<typeof useGetParametersSuspenseQuery>;
export type GetParametersQueryResult = Apollo.QueryResult<GetParametersQuery, GetParametersQueryVariables>;
export const GetParameterDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetParameter"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"parameter"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventId"}},{"kind":"Field","name":{"kind":"Name","value":"paramName"}},{"kind":"Field","name":{"kind":"Name","value":"paramNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"paramType"}},{"kind":"Field","name":{"kind":"Name","value":"paramDescription"}},{"kind":"Field","name":{"kind":"Name","value":"jsonPath"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"version"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetParameterQuery__
 *
 * To run a query within a React component, call `useGetParameterQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetParameterQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetParameterQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useGetParameterQuery(baseOptions: Apollo.QueryHookOptions<GetParameterQuery, GetParameterQueryVariables> & ({ variables: GetParameterQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetParameterQuery, GetParameterQueryVariables>(GetParameterDocument, options);
      }
export function useGetParameterLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetParameterQuery, GetParameterQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetParameterQuery, GetParameterQueryVariables>(GetParameterDocument, options);
        }
// @ts-ignore
export function useGetParameterSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetParameterQuery, GetParameterQueryVariables>): Apollo.UseSuspenseQueryResult<GetParameterQuery, GetParameterQueryVariables>;
export function useGetParameterSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParameterQuery, GetParameterQueryVariables>): Apollo.UseSuspenseQueryResult<GetParameterQuery | undefined, GetParameterQueryVariables>;
export function useGetParameterSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParameterQuery, GetParameterQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetParameterQuery, GetParameterQueryVariables>(GetParameterDocument, options);
        }
export type GetParameterQueryHookResult = ReturnType<typeof useGetParameterQuery>;
export type GetParameterLazyQueryHookResult = ReturnType<typeof useGetParameterLazyQuery>;
export type GetParameterSuspenseQueryHookResult = ReturnType<typeof useGetParameterSuspenseQuery>;
export type GetParameterQueryResult = Apollo.QueryResult<GetParameterQuery, GetParameterQueryVariables>;
export const SearchParametersDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchParameters"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"searchParameters"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"eventId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventId"}},{"kind":"Field","name":{"kind":"Name","value":"paramName"}},{"kind":"Field","name":{"kind":"Name","value":"paramNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"paramType"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useSearchParametersQuery__
 *
 * To run a query within a React component, call `useSearchParametersQuery` and pass it any options that fit your needs.
 * When your component renders, `useSearchParametersQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSearchParametersQuery({
 *   variables: {
 *      query: // value for 'query'
 *      eventId: // value for 'eventId'
 *   },
 * });
 */
export function useSearchParametersQuery(baseOptions: Apollo.QueryHookOptions<SearchParametersQuery, SearchParametersQueryVariables> & ({ variables: SearchParametersQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<SearchParametersQuery, SearchParametersQueryVariables>(SearchParametersDocument, options);
      }
export function useSearchParametersLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<SearchParametersQuery, SearchParametersQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<SearchParametersQuery, SearchParametersQueryVariables>(SearchParametersDocument, options);
        }
// @ts-ignore
export function useSearchParametersSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<SearchParametersQuery, SearchParametersQueryVariables>): Apollo.UseSuspenseQueryResult<SearchParametersQuery, SearchParametersQueryVariables>;
export function useSearchParametersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchParametersQuery, SearchParametersQueryVariables>): Apollo.UseSuspenseQueryResult<SearchParametersQuery | undefined, SearchParametersQueryVariables>;
export function useSearchParametersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<SearchParametersQuery, SearchParametersQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<SearchParametersQuery, SearchParametersQueryVariables>(SearchParametersDocument, options);
        }
export type SearchParametersQueryHookResult = ReturnType<typeof useSearchParametersQuery>;
export type SearchParametersLazyQueryHookResult = ReturnType<typeof useSearchParametersLazyQuery>;
export type SearchParametersSuspenseQueryHookResult = ReturnType<typeof useSearchParametersSuspenseQuery>;
export type SearchParametersQueryResult = Apollo.QueryResult<SearchParametersQuery, SearchParametersQueryVariables>;
export const GetEventFieldsDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetEventFields"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"fieldType"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"FieldTypeEnum"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"eventFields"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"eventId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}}},{"kind":"Argument","name":{"kind":"Name","value":"fieldType"},"value":{"kind":"Variable","name":{"kind":"Name","value":"fieldType"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"category"}},{"kind":"Field","name":{"kind":"Name","value":"isCommon"}},{"kind":"Field","name":{"kind":"Name","value":"dataType"}},{"kind":"Field","name":{"kind":"Name","value":"jsonPath"}},{"kind":"Field","name":{"kind":"Name","value":"usageCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetEventFieldsQuery__
 *
 * To run a query within a React component, call `useGetEventFieldsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetEventFieldsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetEventFieldsQuery({
 *   variables: {
 *      eventId: // value for 'eventId'
 *      fieldType: // value for 'fieldType'
 *   },
 * });
 */
export function useGetEventFieldsQuery(baseOptions: Apollo.QueryHookOptions<GetEventFieldsQuery, GetEventFieldsQueryVariables> & ({ variables: GetEventFieldsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetEventFieldsQuery, GetEventFieldsQueryVariables>(GetEventFieldsDocument, options);
      }
export function useGetEventFieldsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetEventFieldsQuery, GetEventFieldsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetEventFieldsQuery, GetEventFieldsQueryVariables>(GetEventFieldsDocument, options);
        }
// @ts-ignore
export function useGetEventFieldsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetEventFieldsQuery, GetEventFieldsQueryVariables>): Apollo.UseSuspenseQueryResult<GetEventFieldsQuery, GetEventFieldsQueryVariables>;
export function useGetEventFieldsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetEventFieldsQuery, GetEventFieldsQueryVariables>): Apollo.UseSuspenseQueryResult<GetEventFieldsQuery | undefined, GetEventFieldsQueryVariables>;
export function useGetEventFieldsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetEventFieldsQuery, GetEventFieldsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetEventFieldsQuery, GetEventFieldsQueryVariables>(GetEventFieldsDocument, options);
        }
export type GetEventFieldsQueryHookResult = ReturnType<typeof useGetEventFieldsQuery>;
export type GetEventFieldsLazyQueryHookResult = ReturnType<typeof useGetEventFieldsLazyQuery>;
export type GetEventFieldsSuspenseQueryHookResult = ReturnType<typeof useGetEventFieldsSuspenseQuery>;
export type GetEventFieldsQueryResult = Apollo.QueryResult<GetEventFieldsQuery, GetEventFieldsQueryVariables>;
export const GetCommonParametersDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetCommonParameters"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"threshold"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"commonParameters"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gameGid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}}},{"kind":"Argument","name":{"kind":"Name","value":"threshold"},"value":{"kind":"Variable","name":{"kind":"Name","value":"threshold"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"paramName"}},{"kind":"Field","name":{"kind":"Name","value":"paramType"}},{"kind":"Field","name":{"kind":"Name","value":"paramDescription"}},{"kind":"Field","name":{"kind":"Name","value":"occurrenceCount"}},{"kind":"Field","name":{"kind":"Name","value":"totalEvents"}},{"kind":"Field","name":{"kind":"Name","value":"threshold"}},{"kind":"Field","name":{"kind":"Name","value":"eventCodes"}},{"kind":"Field","name":{"kind":"Name","value":"isCommon"}},{"kind":"Field","name":{"kind":"Name","value":"commonalityScore"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetCommonParametersQuery__
 *
 * To run a query within a React component, call `useGetCommonParametersQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetCommonParametersQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetCommonParametersQuery({
 *   variables: {
 *      gameGid: // value for 'gameGid'
 *      threshold: // value for 'threshold'
 *   },
 * });
 */
export function useGetCommonParametersQuery(baseOptions: Apollo.QueryHookOptions<GetCommonParametersQuery, GetCommonParametersQueryVariables> & ({ variables: GetCommonParametersQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetCommonParametersQuery, GetCommonParametersQueryVariables>(GetCommonParametersDocument, options);
      }
export function useGetCommonParametersLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetCommonParametersQuery, GetCommonParametersQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetCommonParametersQuery, GetCommonParametersQueryVariables>(GetCommonParametersDocument, options);
        }
// @ts-ignore
export function useGetCommonParametersSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetCommonParametersQuery, GetCommonParametersQueryVariables>): Apollo.UseSuspenseQueryResult<GetCommonParametersQuery, GetCommonParametersQueryVariables>;
export function useGetCommonParametersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCommonParametersQuery, GetCommonParametersQueryVariables>): Apollo.UseSuspenseQueryResult<GetCommonParametersQuery | undefined, GetCommonParametersQueryVariables>;
export function useGetCommonParametersSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetCommonParametersQuery, GetCommonParametersQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetCommonParametersQuery, GetCommonParametersQueryVariables>(GetCommonParametersDocument, options);
        }
export type GetCommonParametersQueryHookResult = ReturnType<typeof useGetCommonParametersQuery>;
export type GetCommonParametersLazyQueryHookResult = ReturnType<typeof useGetCommonParametersLazyQuery>;
export type GetCommonParametersSuspenseQueryHookResult = ReturnType<typeof useGetCommonParametersSuspenseQuery>;
export type GetCommonParametersQueryResult = Apollo.QueryResult<GetCommonParametersQuery, GetCommonParametersQueryVariables>;
export const GetParametersManagementDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetParametersManagement"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"mode"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"ParameterFilterModeEnum"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"parametersManagement"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gameGid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}}},{"kind":"Argument","name":{"kind":"Name","value":"mode"},"value":{"kind":"Variable","name":{"kind":"Name","value":"mode"}}},{"kind":"Argument","name":{"kind":"Name","value":"eventId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"eventId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"eventId"}},{"kind":"Field","name":{"kind":"Name","value":"paramName"}},{"kind":"Field","name":{"kind":"Name","value":"paramNameCn"}},{"kind":"Field","name":{"kind":"Name","value":"paramType"}},{"kind":"Field","name":{"kind":"Name","value":"paramDescription"}},{"kind":"Field","name":{"kind":"Name","value":"jsonPath"}},{"kind":"Field","name":{"kind":"Name","value":"isActive"}},{"kind":"Field","name":{"kind":"Name","value":"version"}},{"kind":"Field","name":{"kind":"Name","value":"usageCount"}},{"kind":"Field","name":{"kind":"Name","value":"eventsCount"}},{"kind":"Field","name":{"kind":"Name","value":"isCommon"}},{"kind":"Field","name":{"kind":"Name","value":"eventCode"}},{"kind":"Field","name":{"kind":"Name","value":"eventName"}},{"kind":"Field","name":{"kind":"Name","value":"gameGid"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetParametersManagementQuery__
 *
 * To run a query within a React component, call `useGetParametersManagementQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetParametersManagementQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetParametersManagementQuery({
 *   variables: {
 *      gameGid: // value for 'gameGid'
 *      mode: // value for 'mode'
 *      eventId: // value for 'eventId'
 *   },
 * });
 */
export function useGetParametersManagementQuery(baseOptions: Apollo.QueryHookOptions<GetParametersManagementQuery, GetParametersManagementQueryVariables> & ({ variables: GetParametersManagementQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetParametersManagementQuery, GetParametersManagementQueryVariables>(GetParametersManagementDocument, options);
      }
export function useGetParametersManagementLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetParametersManagementQuery, GetParametersManagementQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetParametersManagementQuery, GetParametersManagementQueryVariables>(GetParametersManagementDocument, options);
        }
// @ts-ignore
export function useGetParametersManagementSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetParametersManagementQuery, GetParametersManagementQueryVariables>): Apollo.UseSuspenseQueryResult<GetParametersManagementQuery, GetParametersManagementQueryVariables>;
export function useGetParametersManagementSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParametersManagementQuery, GetParametersManagementQueryVariables>): Apollo.UseSuspenseQueryResult<GetParametersManagementQuery | undefined, GetParametersManagementQueryVariables>;
export function useGetParametersManagementSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParametersManagementQuery, GetParametersManagementQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetParametersManagementQuery, GetParametersManagementQueryVariables>(GetParametersManagementDocument, options);
        }
export type GetParametersManagementQueryHookResult = ReturnType<typeof useGetParametersManagementQuery>;
export type GetParametersManagementLazyQueryHookResult = ReturnType<typeof useGetParametersManagementLazyQuery>;
export type GetParametersManagementSuspenseQueryHookResult = ReturnType<typeof useGetParametersManagementSuspenseQuery>;
export type GetParametersManagementQueryResult = Apollo.QueryResult<GetParametersManagementQuery, GetParametersManagementQueryVariables>;
export const GetParameterChangesDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetParameterChanges"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"parameterId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"limit"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"parameterChanges"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gameGid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}}},{"kind":"Argument","name":{"kind":"Name","value":"parameterId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"parameterId"}}},{"kind":"Argument","name":{"kind":"Name","value":"limit"},"value":{"kind":"Variable","name":{"kind":"Name","value":"limit"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"parameterId"}},{"kind":"Field","name":{"kind":"Name","value":"changeType"}},{"kind":"Field","name":{"kind":"Name","value":"oldValue"}},{"kind":"Field","name":{"kind":"Name","value":"newValue"}},{"kind":"Field","name":{"kind":"Name","value":"changedBy"}},{"kind":"Field","name":{"kind":"Name","value":"changedAt"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetParameterChangesQuery__
 *
 * To run a query within a React component, call `useGetParameterChangesQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetParameterChangesQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetParameterChangesQuery({
 *   variables: {
 *      gameGid: // value for 'gameGid'
 *      parameterId: // value for 'parameterId'
 *      limit: // value for 'limit'
 *   },
 * });
 */
export function useGetParameterChangesQuery(baseOptions: Apollo.QueryHookOptions<GetParameterChangesQuery, GetParameterChangesQueryVariables> & ({ variables: GetParameterChangesQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetParameterChangesQuery, GetParameterChangesQueryVariables>(GetParameterChangesDocument, options);
      }
export function useGetParameterChangesLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetParameterChangesQuery, GetParameterChangesQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetParameterChangesQuery, GetParameterChangesQueryVariables>(GetParameterChangesDocument, options);
        }
// @ts-ignore
export function useGetParameterChangesSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetParameterChangesQuery, GetParameterChangesQueryVariables>): Apollo.UseSuspenseQueryResult<GetParameterChangesQuery, GetParameterChangesQueryVariables>;
export function useGetParameterChangesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParameterChangesQuery, GetParameterChangesQueryVariables>): Apollo.UseSuspenseQueryResult<GetParameterChangesQuery | undefined, GetParameterChangesQueryVariables>;
export function useGetParameterChangesSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetParameterChangesQuery, GetParameterChangesQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetParameterChangesQuery, GetParameterChangesQueryVariables>(GetParameterChangesDocument, options);
        }
export type GetParameterChangesQueryHookResult = ReturnType<typeof useGetParameterChangesQuery>;
export type GetParameterChangesLazyQueryHookResult = ReturnType<typeof useGetParameterChangesLazyQuery>;
export type GetParameterChangesSuspenseQueryHookResult = ReturnType<typeof useGetParameterChangesSuspenseQuery>;
export type GetParameterChangesQueryResult = Apollo.QueryResult<GetParameterChangesQuery, GetParameterChangesQueryVariables>;
export const GetDashboardStatsDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetDashboardStats"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dashboardStats"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalGames"}},{"kind":"Field","name":{"kind":"Name","value":"totalEvents"}},{"kind":"Field","name":{"kind":"Name","value":"totalParameters"}},{"kind":"Field","name":{"kind":"Name","value":"totalCategories"}},{"kind":"Field","name":{"kind":"Name","value":"eventsLast7Days"}},{"kind":"Field","name":{"kind":"Name","value":"parametersLast7Days"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetDashboardStatsQuery__
 *
 * To run a query within a React component, call `useGetDashboardStatsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetDashboardStatsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetDashboardStatsQuery({
 *   variables: {
 *   },
 * });
 */
export function useGetDashboardStatsQuery(baseOptions?: Apollo.QueryHookOptions<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>(GetDashboardStatsDocument, options);
      }
export function useGetDashboardStatsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>(GetDashboardStatsDocument, options);
        }
// @ts-ignore
export function useGetDashboardStatsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>): Apollo.UseSuspenseQueryResult<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>;
export function useGetDashboardStatsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>): Apollo.UseSuspenseQueryResult<GetDashboardStatsQuery | undefined, GetDashboardStatsQueryVariables>;
export function useGetDashboardStatsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>(GetDashboardStatsDocument, options);
        }
export type GetDashboardStatsQueryHookResult = ReturnType<typeof useGetDashboardStatsQuery>;
export type GetDashboardStatsLazyQueryHookResult = ReturnType<typeof useGetDashboardStatsLazyQuery>;
export type GetDashboardStatsSuspenseQueryHookResult = ReturnType<typeof useGetDashboardStatsSuspenseQuery>;
export type GetDashboardStatsQueryResult = Apollo.QueryResult<GetDashboardStatsQuery, GetDashboardStatsQueryVariables>;
export const GetGameStatsDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetGameStats"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gameStats"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"gameGid"},"value":{"kind":"Variable","name":{"kind":"Name","value":"gameGid"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gameGid"}},{"kind":"Field","name":{"kind":"Name","value":"gameName"}},{"kind":"Field","name":{"kind":"Name","value":"eventCount"}},{"kind":"Field","name":{"kind":"Name","value":"parameterCount"}},{"kind":"Field","name":{"kind":"Name","value":"categoryCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetGameStatsQuery__
 *
 * To run a query within a React component, call `useGetGameStatsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetGameStatsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetGameStatsQuery({
 *   variables: {
 *      gameGid: // value for 'gameGid'
 *   },
 * });
 */
export function useGetGameStatsQuery(baseOptions: Apollo.QueryHookOptions<GetGameStatsQuery, GetGameStatsQueryVariables> & ({ variables: GetGameStatsQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetGameStatsQuery, GetGameStatsQueryVariables>(GetGameStatsDocument, options);
      }
export function useGetGameStatsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetGameStatsQuery, GetGameStatsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetGameStatsQuery, GetGameStatsQueryVariables>(GetGameStatsDocument, options);
        }
// @ts-ignore
export function useGetGameStatsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetGameStatsQuery, GetGameStatsQueryVariables>): Apollo.UseSuspenseQueryResult<GetGameStatsQuery, GetGameStatsQueryVariables>;
export function useGetGameStatsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetGameStatsQuery, GetGameStatsQueryVariables>): Apollo.UseSuspenseQueryResult<GetGameStatsQuery | undefined, GetGameStatsQueryVariables>;
export function useGetGameStatsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetGameStatsQuery, GetGameStatsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetGameStatsQuery, GetGameStatsQueryVariables>(GetGameStatsDocument, options);
        }
export type GetGameStatsQueryHookResult = ReturnType<typeof useGetGameStatsQuery>;
export type GetGameStatsLazyQueryHookResult = ReturnType<typeof useGetGameStatsLazyQuery>;
export type GetGameStatsSuspenseQueryHookResult = ReturnType<typeof useGetGameStatsSuspenseQuery>;
export type GetGameStatsQueryResult = Apollo.QueryResult<GetGameStatsQuery, GetGameStatsQueryVariables>;
export const GetAllGameStatsDocument = /*#__PURE__*/ {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetAllGameStats"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"limit"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"allGameStats"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"limit"},"value":{"kind":"Variable","name":{"kind":"Name","value":"limit"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"gameGid"}},{"kind":"Field","name":{"kind":"Name","value":"gameName"}},{"kind":"Field","name":{"kind":"Name","value":"eventCount"}},{"kind":"Field","name":{"kind":"Name","value":"parameterCount"}},{"kind":"Field","name":{"kind":"Name","value":"categoryCount"}}]}}]}}]} as unknown as DocumentNode;

/**
 * __useGetAllGameStatsQuery__
 *
 * To run a query within a React component, call `useGetAllGameStatsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetAllGameStatsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetAllGameStatsQuery({
 *   variables: {
 *      limit: // value for 'limit'
 *   },
 * });
 */
export function useGetAllGameStatsQuery(baseOptions?: Apollo.QueryHookOptions<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>(GetAllGameStatsDocument, options);
      }
export function useGetAllGameStatsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>(GetAllGameStatsDocument, options);
        }
// @ts-ignore
export function useGetAllGameStatsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>): Apollo.UseSuspenseQueryResult<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>;
export function useGetAllGameStatsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>): Apollo.UseSuspenseQueryResult<GetAllGameStatsQuery | undefined, GetAllGameStatsQueryVariables>;
export function useGetAllGameStatsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>(GetAllGameStatsDocument, options);
        }
export type GetAllGameStatsQueryHookResult = ReturnType<typeof useGetAllGameStatsQuery>;
export type GetAllGameStatsLazyQueryHookResult = ReturnType<typeof useGetAllGameStatsLazyQuery>;
export type GetAllGameStatsSuspenseQueryHookResult = ReturnType<typeof useGetAllGameStatsSuspenseQuery>;
export type GetAllGameStatsQueryResult = Apollo.QueryResult<GetAllGameStatsQuery, GetAllGameStatsQueryVariables>;