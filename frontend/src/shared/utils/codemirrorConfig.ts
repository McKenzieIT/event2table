import { sql, SQLDialect } from '@codemirror/lang-sql';
import { EditorView, Extension } from '@codemirror/view';
import { EditorState } from '@codemirror/state';
import { linter } from '@codemirror/lint';
import { createHiveLinter } from './hiveLinter';

const hiveKeywords = [
  'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'FULL',
  'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'IS', 'NULL', 'LIKE', 'BETWEEN',
  'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'OFFSET', 'UNION', 'ALL',
  'DISTINCT', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
  'ASC', 'DESC', 'WITH',
  'ARRAY', 'MAP', 'STRUCT', 'UNIONTYPE',
  'LATERAL', 'VIEW', 'EXPLODE', 'POSEXPLODE',
  'CLUSTER', 'DISTRIBUTE', 'SORT',
  'OVER', 'PARTITION', 'RANK', 'ROW_NUMBER',
  'DENSE_RANK', 'PERCENT_RANK', 'NTILE',
  'LEAD', 'LAG', 'FIRST_VALUE', 'LAST_VALUE',
  'BIGINT', 'BINARY', 'BOOLEAN', 'DECIMAL', 'DOUBLE',
  'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'TINYINT',
  'VARCHAR', 'STRING', 'DATE'
];

const hiveFunctions = [
  'get_json_object', 'nvl', 'coalesce',
  'concat', 'substr', 'substring', 'trim',
  'upper', 'lower', 'length', 'split',
  'to_date', 'date_format', 'from_unixtime',
  'unix_timestamp', 'year', 'month', 'day',
  'hour', 'minute', 'second',
  'cast', 'if', 'case', 'when',
  'isnull', 'isnotnull', 'count', 'sum', 'avg', 'max', 'min'
];

const hiveSQL = SQLDialect.define({
  keywords: hiveKeywords.join(' '),
  types: "BIGINT BINARY BOOLEAN DECIMAL DOUBLE FLOAT INT SMALLINT TIMESTAMP TINYINT VARCHAR STRING DATE"
});

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
  '&.cm-focused .cm-selectionBackground, ::selection': {
    backgroundColor: '#00968833'
  },
  '.cm-selectionMatch': {
    backgroundColor: '#00968822'
  },
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
  '.cm-qualifier': {
    color: '#decb6b'
  },
  '.cm-lineNumbers .cm-gutterElement': {
    color: '#546e7a',
    fontSize: '12px'
  },
  '.cm-activeLineGutter': {
    color: '#e0e0e0',
    fontWeight: 'bold'
  },
  '.cm-scroller': {
    fontFamily: 'inherit'
  },
  '.cm-matchingBracket': {
    color: '#009688',
    fontWeight: 'bold'
  },
  '.cm-nonmatchingBracket': {
    color: '#ff5252'
  }
});

export function getHiveSQLExtension(): Extension {
  return sql({
    dialect: hiveSQL
  });
}

export function getReadOnlyExtension(): Extension[] {
  return [
    EditorState.readOnly.of(true),
    EditorView.editable.of(false)
  ];
}

export function getBasicExtensions(readonly: boolean = false): Extension[] {
  const extensions: Extension[] = [
    darkTheme,
    getHiveSQLExtension(),
    EditorView.lineWrapping
  ];

  if (!readonly) {
    extensions.push(
      linter(createHiveLinter(), {
        delay: 500
      })
    );
  } else {
    extensions.push(...getReadOnlyExtension());
  }

  return extensions;
}

export function getEditorConfig(
  value: string,
  readonly: boolean = false,
  onChange?: (value: string) => void
): EditorState {
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
