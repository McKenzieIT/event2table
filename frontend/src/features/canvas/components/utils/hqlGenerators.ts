/**
 * HQL生成器模块
 * 复用原node-executor.js的HQL生成逻辑
 */

// ============================================
// Type Definitions
// ============================================

export interface GameData {
  ods_db: string;
  gid: string | number;
  name?: string;
  [key: string]: unknown;
}

export interface BaseField {
  fieldName?: string;
  field_name?: string;
  fieldType?: string;
  field_type?: string;
  alias?: string;
}

export interface EventConfig {
  event_name: string;
  event_name_cn?: string;
  base_fields?: BaseField[];
  baseFields?: BaseField[];
  [key: string]: unknown;
}

export interface JoinCondition {
  left_table: string;
  left_field: string;
  right_table: string;
  right_field: string;
}

export interface JoinConfig {
  join_type?: string;
  conditions?: JoinCondition[];
}

export interface FilterConfig {
  conditions?: string[];
}

export interface Aggregation {
  function: string;
  field: string;
  alias: string;
}

export interface AggregateConfig {
  group_by?: string[];
  aggregations?: Aggregation[];
}

export interface OutputConfig {
  view_name?: string;
}

export interface InputSource {
  type: string;
  hql: string;
}

// ============================================
// HQL Generator Class
// ============================================

export class HQLGenerators {
  /**
   * 事件节点HQL生成
   * @param eventConfig - 事件配置
   * @param gameData - 游戏数据
   * @returns HQL语句
   */
  static generateEventHQL(eventConfig: EventConfig, gameData: GameData): string {
    if (!gameData || !gameData.ods_db || !gameData.gid) {
      throw new Error(
        "Invalid gameData: missing required fields (ods_db, gid)"
      );
    }

    if (!eventConfig || !eventConfig.event_name) {
      throw new Error("Invalid eventConfig: missing event_name");
    }

    let baseFields = eventConfig.base_fields || eventConfig.baseFields || [];

    if (baseFields.length === 0) {
      baseFields = [
        { fieldName: "ds", fieldType: "column", alias: "ds" },
        { fieldName: "role_id", fieldType: "column", alias: "role_id" },
        { fieldName: "account_id", fieldType: "column", alias: "account_id" },
        { fieldName: "utdid", fieldType: "column", alias: "utdid" },
        { fieldName: "envinfo", fieldType: "column", alias: "envinfo" },
        { fieldName: "tm", fieldType: "column", alias: "tm" },
        { fieldName: "ts", fieldType: "column", alias: "ts" },
      ];
    }

    const hqlFields = baseFields
      .map((f) => {
        const fieldName = f.fieldName || f.field_name;
        const fieldType = f.fieldType || f.field_type;
        const alias = f.alias;

        if (!fieldName) {
          return "";
        }

        if (fieldType === "param") {
          return `    get_json_object(params, '$.${fieldName}') AS ${alias || fieldName}`;
        } else {
          return `    ${fieldName} AS ${alias || fieldName}`;
        }
      })
      .filter((f) => f)
      .join(",\n");

    const tableName = `${gameData.ods_db}.ods_${gameData.gid}_all_view`;

    const hql = `-- ${eventConfig.event_name_cn || eventConfig.event_name}\nSELECT\n${hqlFields}\nFROM ${tableName}\nWHERE event = '${eventConfig.event_name}';`;

    return hql;
  }

  /**
   * UNION ALL HQL生成
   * @param inputSources - 输入源数组
   * @returns HQL语句
   */
  static generateUnionAllHQL(inputSources: InputSource[]): string {
    return inputSources
      .map((source, index) => {
        return `-- Input ${index + 1}: ${source.type}\n${source.hql}`;
      })
      .join("\n\nUNION ALL\n\n");
  }

  /**
   * JOIN HQL生成
   * @param config - JOIN配置
   * @param leftInput - 左侧输入
   * @param rightInput - 右侧输入
   * @returns HQL语句
   */
  static generateJoinHQL(
    config: JoinConfig,
    leftInput: InputSource,
    rightInput: InputSource
  ): string {
    const joinType = config.join_type || "INNER";
    const conditions = config.conditions || [];

    if (conditions.length === 0) {
      throw new Error("JOIN节点缺少连接条件");
    }

    const onClause = conditions
      .map((cond) => {
        return `    ${cond.left_table}.${cond.left_field} = ${cond.right_table}.${cond.right_field}`;
      })
      .join("\n    AND ");

    return `-- Join\n${leftInput.hql}\n${joinType} JOIN\n${rightInput.hql}\nON\n${onClause}`;
  }

  /**
   * Filter HQL生成
   * @param config - 过滤配置
   * @param inputSource - 输入源
   * @returns HQL语句
   */
  static generateFilterHQL(config: FilterConfig, inputSource: InputSource): string {
    const whereClause =
      config.conditions && config.conditions.length > 0
        ? config.conditions.join(" AND ")
        : "1=1";

    return `-- Filter\nSELECT * FROM (\n    ${inputSource.hql}\n) t\nWHERE ${whereClause}`;
  }

  /**
   * Aggregate HQL生成
   * @param config - 聚合配置
   * @param inputSource - 输入源
   * @returns HQL语句
   */
  static generateAggregateHQL(
    config: AggregateConfig,
    inputSource: InputSource
  ): string {
    const groupByFields = config.group_by || [];
    const aggregations = config.aggregations || [];

    const selectList = [
      ...groupByFields.map((f) => `    ${f}`),
      ...aggregations.map(
        (agg) => `    ${agg.function}(${agg.field}) AS ${agg.alias}`
      ),
    ].join(",\n");

    const groupByClause =
      groupByFields.length > 0 ? `GROUP BY ${groupByFields.join(", ")}` : "";

    return `-- Aggregate\nSELECT\n${selectList}\nFROM (\n    ${inputSource.hql}\n) t\n${groupByClause}`;
  }

  /**
   * Output HQL生成
   * @param config - 输出配置
   * @param inputSource - 输入源
   * @param gameData - 游戏数据
   * @returns HQL语句
   */
  static generateOutputHQL(
    config: OutputConfig,
    inputSource: InputSource,
    gameData: GameData
  ): string {
    if (!gameData || !gameData.gid) {
      throw new Error("Invalid gameData: missing required field (gid)");
    }

    if (!config || !config.view_name) {
      throw new Error("Invalid config: missing view_name");
    }

    if (!inputSource || !inputSource.hql) {
      throw new Error("Invalid inputSource: missing hql");
    }

    const viewName = config.view_name || "dwd_output";
    const dwdPrefix = `dwd_${gameData.gid}`;

    return `-- Output: ${viewName}\nCREATE OR REPLACE VIEW ${dwdPrefix}.${viewName} AS\n${inputSource.hql}`;
  }
}
