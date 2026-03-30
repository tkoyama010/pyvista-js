/** @type {import('xo').FlatXoConfig} */
import jsdocPlugin from "eslint-plugin-jsdoc";
import promisePlugin from "eslint-plugin-promise";
import regexpPlugin from "eslint-plugin-regexp";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import sonarjsPlugin from "eslint-plugin-sonarjs";

export default [
  {
    ignores: ["src/", "_build/"],
  },
  {
    space: true,
    prettier: true,
    semicolon: true,
    plugins: {
      "jsdoc": jsdocPlugin,
      "sonarjs": sonarjsPlugin,
      "promise": promisePlugin,
      "regexp": regexpPlugin,
      "simple-import-sort": simpleImportSort,
    },
    rules: {
      // VTK.js bridges require assertions between its untyped API and our typed interfaces
      "@typescript-eslint/no-unsafe-type-assertion": "off",
      "jsdoc/require-jsdoc": [
        "error",
        {
          require: {
            FunctionDeclaration: true,
            MethodDefinition: true,
            ClassDeclaration: true,
          },
          contexts: ["TSInterfaceDeclaration", "TSTypeAliasDeclaration"],
        },
      ],
      "jsdoc/require-description": "error",
      "jsdoc/no-blank-blocks": "error",
      "jsdoc/no-blank-block-descriptions": "error",
      "jsdoc/require-param": "error",
      "jsdoc/require-returns": "error",
      "complexity": ["error", 20],
      "max-depth": ["error", 4],
      "max-lines-per-function": ["error", { max: 150, skipBlankLines: true, skipComments: true }],
      "max-params": ["error", 4],
      "sonarjs/cognitive-complexity": ["error", 20],
      "sonarjs/no-duplicate-string": ["error", { threshold: 3 }],
      "sonarjs/no-identical-functions": "error",
      "sonarjs/no-collapsible-if": "error",
      "sonarjs/prefer-immediate-return": "error",
      "sonarjs/no-redundant-jump": "error",
      "promise/always-return": "error",
      "promise/no-return-wrap": "error",
      "promise/param-names": "error",
      "promise/catch-or-return": "error",
      "promise/no-nesting": "warn",
      "promise/no-promise-in-callback": "warn",
      "promise/no-callback-in-promise": "warn",
      "promise/no-return-in-finally": "error",
      "promise/no-multiple-resolved": "error",
      "regexp/no-super-linear-backtracking": "error",
      "regexp/no-misleading-unicode-character": "error",
      "regexp/no-useless-flag": "error",
      "regexp/prefer-named-capture-group": "warn",
      "simple-import-sort/imports": "error",
      "simple-import-sort/exports": "error",
    },
  },
  {
    files: ["ts/*.d.ts"],
    rules: {
      "unicorn/no-keyword-prefix": "error",
    },
  },
];
