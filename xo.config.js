import jsdocPlugin from "eslint-plugin-jsdoc";

export default [
  {
    space: true,
    prettier: true,
    semicolon: true,
    ignores: ["src/"],
    plugins: {
      jsdoc: jsdocPlugin,
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
      // Additional JSDoc rules for better documentation quality (strict level)
      "jsdoc/check-alignment": "error",
      "jsdoc/check-syntax": "error",
      "jsdoc/check-tag-names": "error",
      "jsdoc/check-types": "error",
      "jsdoc/empty-tags": "error",
      "jsdoc/multiline-blocks": "error",
      "jsdoc/no-undefined-types": "error",
      "jsdoc/require-asterisk-prefix": "error",
      "jsdoc/require-param-description": "error",
      "jsdoc/require-returns-description": "error",
      // Disable no-await-in-loop to allow sequential actor processing
      "no-await-in-loop": "off",
      // Disable prefer-top-level-await to allow IIFE pattern
      "unicorn/prefer-top-level-await": "off",
      "complexity": ["error", 20],
      "max-depth": ["error", 4],
    },
  },
  {
    files: ["ts/*.d.ts"],
    rules: {
      "unicorn/no-keyword-prefix": "error",
    },
  },
];
