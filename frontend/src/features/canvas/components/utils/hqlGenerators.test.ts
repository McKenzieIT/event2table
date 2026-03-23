import { describe, it, expect } from 'vitest';

import { HQLGenerators } from './hqlGenerators';

describe('HQLGenerators Utility', () => {
  describe('事件节点 HQL 生成', () => {
    it('应该生成正确的事件节点 HQL', () => {
      const eventConfig = {
        event_name: 'test_event',
        event_name_cn: '测试事件',
        base_fields: [
          { fieldName: 'ds', fieldType: 'column', alias: 'ds' },
          { fieldName: 'role_id', fieldType: 'column', alias: 'role_id' }
        ]
      };

      const gameData = {
        ods_db: 'ods_test',
        gid: '10000147'
      };

      const hql = HQLGenerators.generateEventHQL(eventConfig, gameData);

      expect(hql).toContain('-- 测试事件');
      expect(hql).toContain('SELECT');
      expect(hql).toContain('ds AS ds');
      expect(hql).toContain('role_id AS role_id');
      expect(hql).toContain('FROM ods_test.ods_10000147_all_view');
      expect(hql).toContain("WHERE event = 'test_event'");
    });

    it('应该使用默认字段当 base_fields 为空时', () => {
      const eventConfig = {
        event_name: 'test_event'
      };

      const gameData = {
        ods_db: 'ods_test',
        gid: '10000147'
      };

      const hql = HQLGenerators.generateEventHQL(eventConfig, gameData);

      expect(hql).toContain('ds AS ds');
      expect(hql).toContain('role_id AS role_id');
      expect(hql).toContain('account_id AS account_id');
    });

    it('应该正确处理 param 类型的字段', () => {
      const eventConfig = {
        event_name: 'test_event',
        base_fields: [
          { fieldName: 'custom_param', fieldType: 'param', alias: 'custom_param' }
        ]
      };

      const gameData = {
        ods_db: 'ods_test',
        gid: '10000147'
      };

      const hql = HQLGenerators.generateEventHQL(eventConfig, gameData);

      expect(hql).toContain("get_json_object(params, '$.custom_param') AS custom_param");
    });

    it('应该在缺少必填字段时抛出错误', () => {
      const eventConfig = { event_name: 'test_event' };
      const gameData = { ods_db: '', gid: '' };

      expect(() => {
        HQLGenerators.generateEventHQL(eventConfig, gameData);
      }).toThrow('Invalid gameData');
    });

    it('应该在缺少 event_name 时抛出错误', () => {
      const eventConfig = {} as any;
      const gameData = { ods_db: 'ods_test', gid: '10000147' };

      expect(() => {
        HQLGenerators.generateEventHQL(eventConfig, gameData);
      }).toThrow('Invalid eventConfig');
    });
  });

  describe('UNION ALL HQL 生成', () => {
    it('应该生成正确的 UNION ALL HQL', () => {
      const inputSources = [
        { type: 'event', hql: 'SELECT * FROM table1' },
        { type: 'event', hql: 'SELECT * FROM table2' }
      ];

      const hql = HQLGenerators.generateUnionAllHQL(inputSources);

      expect(hql).toContain('-- Input 1: event');
      expect(hql).toContain('SELECT * FROM table1');
      expect(hql).toContain('UNION ALL');
      expect(hql).toContain('-- Input 2: event');
      expect(hql).toContain('SELECT * FROM table2');
    });

    it('应该处理多个输入源', () => {
      const inputSources = [
        { type: 'event1', hql: 'SELECT * FROM table1' },
        { type: 'event2', hql: 'SELECT * FROM table2' },
        { type: 'event3', hql: 'SELECT * FROM table3' }
      ];

      const hql = HQLGenerators.generateUnionAllHQL(inputSources);

      expect(hql).toContain('-- Input 1: event1');
      expect(hql).toContain('-- Input 2: event2');
      expect(hql).toContain('-- Input 3: event3');
      // 3个输入源 → 2个UNION ALL → split后得到3个部分
      expect(hql.split('UNION ALL')).toHaveLength(3);
    });
  });

  describe('JOIN HQL 生成', () => {
    it('应该生成正确的 INNER JOIN HQL', () => {
      const config = {
        join_type: 'INNER',
        conditions: [
          {
            left_table: 't1',
            left_field: 'role_id',
            right_table: 't2',
            right_field: 'role_id'
          }
        ]
      };

      const leftInput = { type: 'left', hql: 'SELECT * FROM t1' };
      const rightInput = { type: 'right', hql: 'SELECT * FROM t2' };

      const hql = HQLGenerators.generateJoinHQL(config, leftInput, rightInput);

      expect(hql).toContain('INNER JOIN');
      expect(hql).toContain('t1.role_id = t2.role_id');
    });

    it('应该生成 LEFT JOIN HQL', () => {
      const config = {
        join_type: 'LEFT',
        conditions: [
          {
            left_table: 't1',
            left_field: 'id',
            right_table: 't2',
            right_field: 'id'
          }
        ]
      };

      const leftInput = { type: 'left', hql: 'SELECT * FROM t1' };
      const rightInput = { type: 'right', hql: 'SELECT * FROM t2' };

      const hql = HQLGenerators.generateJoinHQL(config, leftInput, rightInput);

      expect(hql).toContain('LEFT JOIN');
    });

    it('应该处理多个连接条件', () => {
      const config = {
        join_type: 'INNER',
        conditions: [
          {
            left_table: 't1',
            left_field: 'role_id',
            right_table: 't2',
            right_field: 'role_id'
          },
          {
            left_table: 't1',
            left_field: 'account_id',
            right_table: 't2',
            right_field: 'account_id'
          }
        ]
      };

      const leftInput = { type: 'left', hql: 'SELECT * FROM t1' };
      const rightInput = { type: 'right', hql: 'SELECT * FROM t2' };

      const hql = HQLGenerators.generateJoinHQL(config, leftInput, rightInput);

      expect(hql).toContain('AND');
      expect(hql).toContain('t1.role_id = t2.role_id');
      expect(hql).toContain('t1.account_id = t2.account_id');
    });

    it('应该在缺少连接条件时抛出错误', () => {
      const config = { join_type: 'INNER', conditions: [] };
      const leftInput = { type: 'left', hql: 'SELECT * FROM t1' };
      const rightInput = { type: 'right', hql: 'SELECT * FROM t2' };

      expect(() => {
        HQLGenerators.generateJoinHQL(config, leftInput, rightInput);
      }).toThrow('JOIN节点缺少连接条件');
    });
  });

  describe('Filter HQL 生成', () => {
    it('应该生成正确的 Filter HQL', () => {
      const config = {
        conditions: ['role_id > 0', 'account_id IS NOT NULL']
      };

      const inputSource = { type: 'input', hql: 'SELECT * FROM t1' };

      const hql = HQLGenerators.generateFilterHQL(config, inputSource);

      expect(hql).toContain('-- Filter');
      expect(hql).toContain('role_id > 0 AND account_id IS NOT NULL');
    });

    it('应该在没有条件时使用默认条件', () => {
      const config = { conditions: [] };
      const inputSource = { type: 'input', hql: 'SELECT * FROM t1' };

      const hql = HQLGenerators.generateFilterHQL(config, inputSource);

      expect(hql).toContain('WHERE 1=1');
    });
  });

  describe('Aggregate HQL 生成', () => {
    it('应该生成正确的 Aggregate HQL', () => {
      const config = {
        group_by: ['role_id', 'account_id'],
        aggregations: [
          { function: 'COUNT', field: '*', alias: 'count' },
          { function: 'SUM', field: 'amount', alias: 'total_amount' }
        ]
      };

      const inputSource = { type: 'input', hql: 'SELECT * FROM t1' };

      const hql = HQLGenerators.generateAggregateHQL(config, inputSource);

      expect(hql).toContain('-- Aggregate');
      expect(hql).toContain('role_id');
      expect(hql).toContain('account_id');
      expect(hql).toContain('COUNT(*) AS count');
      expect(hql).toContain('SUM(amount) AS total_amount');
      expect(hql).toContain('GROUP BY');
    });

    it('应该在没有 group_by 时生成简单的聚合', () => {
      const config = {
        group_by: [],
        aggregations: [
          { function: 'COUNT', field: '*', alias: 'total' }
        ]
      };

      const inputSource = { type: 'input', hql: 'SELECT * FROM t1' };

      const hql = HQLGenerators.generateAggregateHQL(config, inputSource);

      expect(hql).toContain('COUNT(*) AS total');
      expect(hql).not.toContain('GROUP BY');
    });
  });

  describe('Output HQL 生成', () => {
    it('应该生成正确的 Output HQL', () => {
      const config = { view_name: 'test_view' };
      const inputSource = { type: 'input', hql: 'SELECT * FROM t1' };
      const gameData = { gid: '10000147' };

      const hql = HQLGenerators.generateOutputHQL(config, inputSource, gameData);

      expect(hql).toContain('-- Output: test_view');
      expect(hql).toContain('CREATE OR REPLACE VIEW dwd_10000147.test_view AS');
      expect(hql).toContain('SELECT * FROM t1');
    });

    it('应该在缺少 view_name 时抛出错误', () => {
      const config = {} as any;
      const inputSource = { type: 'input', hql: 'SELECT * FROM t1' };
      const gameData = { gid: '10000147' };

      expect(() => {
        HQLGenerators.generateOutputHQL(config, inputSource, gameData);
      }).toThrow('Invalid config');
    });

    it('应该在缺少 inputSource 时抛出错误', () => {
      const config = { view_name: 'test_view' };
      const inputSource = {} as any;
      const gameData = { gid: '10000147' };

      expect(() => {
        HQLGenerators.generateOutputHQL(config, inputSource, gameData);
      }).toThrow('Invalid inputSource');
    });
  });
});
