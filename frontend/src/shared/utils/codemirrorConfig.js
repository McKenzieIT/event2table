import { sql, SQLDialect } from '@codemirror/lang-sql';
import { EditorView } from '@codemirror/view';
import { EditorState } from '@codemirror/state';
import { linter, diagnosticCount } from '@codemirror/lint';
import { createHiveLinter } from './hiveLinter';

/**
 * CodeMirror编辑器配置
 * 提供Hive SQL语法高亮和深色主题
 *
 * @module codemirrorConfig
 */

/**
 * Hive SQL关键字列表
 */
const hiveKeywords = [
  // 标准SQL关键字
  'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'FULL',
  'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'IS', 'NULL', 'LIKE', 'BETWEEN',
  'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'OFFSET', 'UNION', 'ALL',
  'DISTINCT', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
  'ASC', 'DESC', 'WITH',
  // Hive特有关键字
  'ARRAY', 'MAP', 'STRUCT', 'UNIONTYPE',
  'LATERAL', 'VIEW', 'EXPLODE', 'POSEXPLODE',
  'CLUSTER', 'DISTRIBUTE', 'SORT',
  'OVER', 'PARTITION', 'RANK', 'ROW_NUMBER',
  'DENSE_RANK', 'PERCENT_RANK', 'NTILE',
  'LEAD', 'LAG', 'FIRST_VALUE', 'LAST_VALUE',
  // Hive数据类型
  'BIGINT', 'BINARY', 'BOOLEAN', 'DECIMAL', 'DOUBLE',
  'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'TINYINT',
  'VARCHAR', 'STRING', 'DATE'
];

/**
 * Hive SQL函数列表
 */
const hiveFunctions = [
  // Hive内置函数
  'get_json_object', 'nvl', 'coalesce',
  'concat', 'substr', 'substring', 'trim',
  'upper', 'lower', 'length', 'split',
  'to_date', 'date_format', 'from_unixtime',
  'unix_timestamp', 'year', 'month', 'day',
  'hour', 'minute', 'second',
  'cast', 'if', 'case', 'when',
  'isnull', 'isnotnull', 'count', 'sum', 'avg', 'max', 'min'
];

/**
 * Hive SQL方言定义
 * 支持Hive SQL关键字和函数
 *
 * @constant {SQLDialect}
 */
const hiveSQL = SQLDialect.define({
  keywords: hiveKeywords.join(' '),
  types: "BIGINT BINARY BOOLEAN DECIMAL DOUBLE FLOAT INT SMALLINT TIMESTAMP TINYINT VARCHAR STRING DATE"
});

/**
 * 深色主题配置
 * 匹配项目OLED玻璃态风格
 *
 * @constant {Extension}
 */
const darkTheme = EditorView.theme({
  '&': {
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    fontSize: '14px',
    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", Consolas, monospace'
  },
  '.cm-content': {
    padding: '12px',
    minHeight: '200px'
  },
  '.cm-line': {
    padding: '0 2px'
  },
  '.cm-focused': {
    outline: 'none'
  },
  // 选中文本背景色
  '&.cm-focused .cm-selectionBackground, ::selection': {
    backgroundColor: '#00968833'
  },
  '.cm-selectionMatch': {
    backgroundColor: '#00968822'
  },
  // 语法高亮颜色（Material Dark Palenight风格）
  '.cm-keyword': {
    color: '#c792ea',
    fontWeight: 'bold'
  },
  '.cm-string': {
    color: '#c3e88d'
  },
  '.cm-number': {
    color: '#f78c6c'
  },
  '.cm-comment': {
    color: '#546e7a',
    fontStyle: 'italic'
  },
  '.cm-variableName': {
    color: '#82aaff'
  },
  '.cm-property': {
    color: '#ffcb6b'
  },
  '.cm-operator': {
    color: '#89ddff'
  },
  '.cm-def': {
    color: '#82aaff'
  },
  '.cm-variableName': {
    color: '#e0e0e0'
  },
  '.cm-qualifier': {
    color: '#decb6b'
  },
  // 行号样式
  '.cm-lineNumbers .cm-gutterElement': {
    color: '#546e7a',
    fontSize: '12px'
  },
  '.cm-activeLineGutter': {
    color: '#e0e0e0',
    fontWeight: 'bold'
  },
  // 滚动条样式
  '.cm-scroller': {
    fontFamily: 'inherit'
  },
  // 匹配括号
  '.cm-matchingBracket': {
    color: '#009688',
    fontWeight: 'bold'
  },
  '.cm-nonmatchingBracket': {
    color: '#ff5252'
  }
});

/**
 * 获取Hive SQL扩展
 *
 * @returns {Extension} SQL语言扩展
 *
 * @example
 * const extensions = [getHiveSQLExtension()];
 */
export function getHiveSQLExtension() {
  return sql({
    dialect: hiveSQL
  });
}

/**
 * 获取只读扩展
 *
 * @returns {Array<Extension>} 只读扩展数组
 *
 * @example
 * const extensions = [...getReadOnlyExtension()];
 */
export function getReadOnlyExtension() {
  return [
    EditorState.readOnly.of(true),
    EditorView.editable.of(false)
  ];
}

/**
 * 获取基础编辑器扩展
 *
 * @param {boolean} [readonly=false] - 是否只读模式
 * @returns {Array<Extension>} 编辑器扩展数组
 *
 * @example
 * const extensions = getBasicExtensions(false);
 */
export function getBasicExtensions(readonly = false) {
  const extensions = [
    darkTheme,
    getHiveSQLExtension(),
    EditorView.lineWrapping
  ];

  // 只在非只读模式下启用 Linter
  if (!readonly) {
    extensions.push(
      linter(createHiveLinter(), {
        delay: 500 // 500ms 防抖延迟
      })
    );
  } else {
    extensions.push(...getReadOnlyExtension());
  }

  return extensions;
}

/**
 * 获取编辑器状态配置
 *
 * @param {string} value - 编辑器初始内容
 * @param {boolean} [readonly=false] - 是否只读模式
 * @param {Function} [onChange] - 内容变化回调函数
 * @returns {EditorState} 编辑器状态
 *
 * @example
 * const state = getEditorConfig('-- HQL here', false, (value) => {
 *   // handle content change
 * });
 */
export function getEditorConfig(value, readonly = false, onChange) {
  const extensions = getBasicExtensions(readonly).concat([
    EditorView.updateListener.of((update) => {
      if (update.docChanged && onChange) {
        onChange(update.state.doc.toString());
      }
    })
  ]);

  return EditorState.create({
    doc: value,
    extensions
  });
}
