const path = require('path');
// style.css is the tailwind entry, the module CSS gets its own tailwind context (see tailwind.modules.config.js)
module.exports = ({ file }) => ({
  plugins: {
    'postcss-preset-env': {},
    tailwindcss: {
      config: path.join(__dirname, path.basename(file) === 'style.css' ? 'tailwind.config.js' : 'tailwind.modules.config.js'),
    },
    autoprefixer: {},
  },
});
