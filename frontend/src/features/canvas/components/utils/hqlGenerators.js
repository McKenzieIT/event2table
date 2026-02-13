/**
 * HQL生成器模块
 * 复用原node-executor.js的HQL生成逻辑
 */

export class HQLGenerators {
  /**
   * 事件节点HQL生成
   * @param {Object} eventConfig - 事件配置
   * @param {Object} gameData - 游戏数据
   * @returns {string} HQL语句
   */
  static generateEventHQL(eventConfig, gameData) {
    // 🔧 v1.0.25.2: 添加调试日志
    console.log("[HQLGenerators] generateEventHQL called");
    console.log(
      "[HQLGenerators] eventConfig keys:",
      Object.keys(eventConfig || {}),
    );
    console.log(
      "[HQLGenerators] eventConfig.base_fields:",
      eventConfig.base_fields,
    );
    console.log(
      "[HQLGenerators] eventConfig.baseFields:",
      eventConfig.baseFields,
    );
    console.log(
      "[HQLGenerators] base_fields length:",
      eventConfig.base_fields?.length || 0,
    );
    console.log(
      "[HQLGenerators] baseFields length:",
      eventConfig.baseFields?.length || 0,
    );

    // Validate required parameters
    if (!gameData || !gameData.ods_db || !gameData.gid) {
      throw new Error(
        "Invalid gameData: missing required fields (ods_db, gid)",
      );
    }

    if (!eventConfig || !eventConfig.event_name) {
      throw new Error("Invalid eventConfig: missing event_name");
    }

    // 🔧 v1.0.25.2: 优先使用 base_fields (API返回的字段名)，然后 baseFields
    let baseFields = eventConfig.base_fields || eventConfig.baseFields || [];

    console.log("[HQLGenerators] Selected baseFields:", baseFields);
    console.log("[HQLGenerators] baseFields length:", baseFields.length);

    // 🔧 v1.0.25.2: 如果仍然为空，使用默认字段
    if (baseFields.length === 0) {
      console.warn(
        "[HQLGenerators] ⚠️ baseFields/base_fields 均为空，使用默认字段",
      );
      baseFields = [
        { field_name: "ds", field_type: "column", alias: "ds" },
        { field_name: "role_id", field_type: "column", alias: "role_id" },
        { field_name: "account_id", field_type: "column", alias: "account_id" },
        { field_name: "utdid", field_type: "column", alias: "utdid" },
        { field_name: "envinfo", field_type: "column", alias: "envinfo" },
        { field_name: "tm", field_type: "column", alias: "tm" },
        { field_name: "ts", field_type: "column", alias: "ts" },
      ];
      console.log(
        "[HQLGenerators] 使用默认字段:",
        baseFields.map((f) => f.field_name),
      );
    }

    const hqlFields = baseFields
      .map((f) => {
        // 🔧 v1.0.25.2: 兼容多种字段命名格式
        // 新格式 (event_node_configs): fieldName, fieldType, alias
        // 旧格式: field_name, field_type, alias
        const fieldName = f.fieldName || f.field_name;
        const fieldType = f.fieldType || f.field_type;
        const alias = f.alias;

        if (!fieldName) {
          console.warn("[HQLGenerators] ⚠️ 字段缺少fieldName/field_name:", f);
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

    console.log("[HQLGenerators] Generated HQL length:", hql.length);
    console.log("[HQLGenerators] HQL preview:", hql.substring(0, 200) + "...");

    return hql;
  }

  /**
   * UNION ALL HQL生成
   * @param {Array} inputSources - 输入源数组
   * @returns {string} HQL语句
   */
  static generateUnionAllHQL(inputSources) {
    return inputSources
      .map((source, index) => {
        return `-- Input ${index + 1}: ${source.type}\n${source.hql}`;
      })
      .join("\n\nUNION ALL\n\n");
  }

  /**
   * JOIN HQL生成
   * @param {Object} config - JOIN配置
   * @param {Object} leftInput - 左侧输入
   * @param {Object} rightInput - 右侧输入
   * @returns {string} HQL语句
   */
  static generateJoinHQL(config, leftInput, rightInput) {
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
   * @param {Object} config - 过滤配置
   * @param {Object} inputSource - 输入源
   * @returns {string} HQL语句
   */
  static generateFilterHQL(config, inputSource) {
    const whereClause =
      config.conditions && config.conditions.length > 0
        ? config.conditions.join(" AND ")
        : "1=1";

    return `-- Filter\nSELECT * FROM (\n    ${inputSource.hql}\n) t\nWHERE ${whereClause}`;
  }

  /**
   * Aggregate HQL生成
   * @param {Object} config - 聚合配置
   * @param {Object} inputSource - 输入源
   * @returns {string} HQL语句
   */
  static generateAggregateHQL(config, inputSource) {
    const groupByFields = config.group_by || [];
    const aggregations = config.aggregations || [];

    const selectList = [
      ...groupByFields.map((f) => `    ${f}`),
      ...aggregations.map(
        (agg) => `    ${agg.function}(${agg.field}) AS ${agg.alias}`,
      ),
    ].join(",\n");

    const groupByClause =
      groupByFields.length > 0 ? `GROUP BY ${groupByFields.join(", ")}` : "";

    return `-- Aggregate\nSELECT\n${selectList}\nFROM (\n    ${inputSource.hql}\n) t\n${groupByClause}`;
  }

  /**
   * Output HQL生成
   * @param {Object} config - 输出配置
   * @param {Object} inputSource - 输入源
   * @param {Object} gameData - 游戏数据
   * @returns {string} HQL语句
   */
  static generateOutputHQL(config, inputSource, gameData) {
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
