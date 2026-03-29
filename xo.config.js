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
      // Additional strict JSDoc rules - convert warnings to errors
      "jsdoc/require-param-description": "error",
      "jsdoc/require-returns-description": "error",
      "jsdoc/require-description-complete-sentence": "error",
      "jsdoc/require-hyphen-before-param-description": "error",
      "jsdoc/check-line-alignment": "error",
      "jsdoc/check-syntax": "error",
      "jsdoc/check-types": "error",
      "jsdoc/check-values": "error",
      "jsdoc/empty-tags": "error",
      "jsdoc/implements-on-classes": "error",
      "jsdoc/multiline-blocks": "error",
      "jsdoc/no-bad-blocks": "error",
      "jsdoc/no-defaults": "error",
      "jsdoc/no-multi-asterisks": "error",
      "jsdoc/no-undefined-types": "error",
      "jsdoc/require-asterisk-prefix": "error",
      "jsdoc/require-example": "error",
      "jsdoc/require-param-name": "error",
      "jsdoc/require-param-type": "error",
      "jsdoc/require-property": "error",
      "jsdoc/require-property-description": "error",
      "jsdoc/require-property-name": "error",
      "jsdoc/require-property-type": "error",
      "jsdoc/require-returns-check": "error",
      "jsdoc/require-returns-type": "error",
      "jsdoc/require-throws": "error",
      "jsdoc/tag-lines": "error",
      "jsdoc/valid-types": "error",
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
