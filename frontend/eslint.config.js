import html from "@html-eslint/eslint-plugin";
import htmlParser from "@html-eslint/parser";

export default [
  {
    files: ["**/*.html"],
    languageOptions: { parser: htmlParser },
    plugins: { "@html-eslint": html },
    rules: {
      "@html-eslint/indent": ["error", 2],
      "@html-eslint/quotes": ["error", "double"],
      "@html-eslint/no-duplicate-id": "error",
      "@html-eslint/require-closing-tags": "error"
    }
  }
];
