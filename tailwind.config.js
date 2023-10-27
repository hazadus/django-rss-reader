const plugin = require('tailwindcss/plugin');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      './templates/**/*.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    // Reference: https://stackoverflow.com/questions/66416614/how-to-create-scrollable-element-in-tailwind-without-a-scrollbar
    plugin(function({ addUtilities }) {
      addUtilities({
        '.hide-scrollbar::-webkit-scrollbar': {
          'display': 'none',
        },
        '.hide-scrollbar': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
        },
      })
    })
  ],
}