const autoprefixer = require('autoprefixer')();
const purgecss = require('@fullhuman/postcss-purgecss')({
  content: [
    './layouts/**/*.html',
    './content/**/*.md'
  ],
  safelist: {
    // standard: [],
    // deep: [],
    greedy: []
  }
});



module.exports = {
  plugins: [
    ...process.env.HUGO_ENVIRONMENT === 'development'
    ? [null]
    : [autoprefixer, purgecss]
  ]
}