export default {
  importOrderParserPlugins: ['typescript', 'jsx', 'decorators-legacy'],
  experimentalBabelParserPluginsList: ['classProperties', 'jsx', 'decorators-legacy'],
  printWidth: 100,
  singleQuote: true,
  trailingComma: 'es5',

  plugins: ['@trivago/prettier-plugin-sort-imports'],
  importOrder: [
    '^(react|redux|prop)(.*)$',
    '^classnames.*$',
    '^\\.\\.?\\/((?!scss).)*$',
    '^(.*)\\.scss$',
  ],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
  importOrderCaseInsensitive: true,
  arrowParens: 'always',
};
