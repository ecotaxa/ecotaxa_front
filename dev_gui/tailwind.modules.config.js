// Tailwind config for the CSS imported by JS modules (tom-select.css, js-tree.css).
// Tailwind shares one context between all files built with the same config (keyed on its hash),
// and the @layer rules of style.css registered in it end up in the @apply of the module CSS when
// style.css happens to be processed first: the output changed from one build to the other.
// The extra key gives the modules a context of their own.
module.exports = { ...require('./tailwind.config.js'), context: 'modules' };
