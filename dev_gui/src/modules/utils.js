// not in use when table component returns cellIndex
const tableColIndex = (col) => {
  return [...col.parentElement.children].indexOf(col);
}
const tableColHeader = (col) => {
  const index = tableColIndex(col);
  const th = col.closest('table').querySelector('thead > tr ');
  return th.querySelectorAll('th')[index];
}
const tableColHeaderRelIndex = (th, rel) => {
  const el = th.parentElement.querySelector(rel);
  if (el) return tableColIndex(el);
  return el;
}
const fetchSettings = (options) => {
  options = options || {};
  options.headers = options.headers || {};
  options.headers['X-Requested-With'] = 'XMLHttpRequest';
  if (!options.credentials) options.credentials = 'same-origin';
  return options;

}
const className = (selector) => {
  return selector.replace('.', '').replace('#', '');
}
const escape_html = (str) => {
  return (str + '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&amp;&amp;/g, '&amp;');
}
const unescape_html = (str) => {
  return (str + '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"');
}
export {
  tableColHeader,
  tableColIndex,
  tableColHeaderRelIndex,
  fetchSettings,
  unescape_html,
  className,
}