const autoprefixer = require('autoprefixer')();
const purgecss = require('@fullhuman/postcss-purgecss')({
  content: [
    './layouts/**/*.html',
    './content/**/*.md'
  ],
  safelist: {
    // standard: [],
    deep: [/toc__nav$/],
    greedy: [/menu_show/]
  }
});



module.exports = {
  plugins: [
    ...process.env.HUGO_ENVIRONMENT === 'development'
    ? [null]
    : [autoprefixer, purgecss]
  ]
}