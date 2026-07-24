import {
  is_object
} from "../modules/utils.js"

/**
 * Export table to CSV
 * @param {TableComponent) TableComponent instance.

 * @return {Array}
 */

export function exportCSV(state, options = {}, hidden = true) {

  if (!state.grid.columns.length || (hidden === true && !state.grid.data.length)) return false;
  const defaults = {
    download: true,
    skipcolumns: [],
    linedelimiter: "\n",
    columndelimiter: ","
  }
  options = { ...defaults,
    ...options
  };

  function text_convert(text) {
     if (text === null || text === undefined) return null;
    const make_text=function(text) {
       text = text.trim();
       text = text.replace(/\s{2,}/g, " ");
       text = text.replace(/\n/g, "  ");
       text = text.replace(/"/g, "\"\"");
       //have to manually encode "#" as encodeURI leaves it as is.
       text = text.replace(/#/g, "%23");
       if (text.includes(",")) text = `"${text}"`
       return text;
    }
    if (typeof(text) ==='object') {
        const stringify= function(obj) {
        const txt=[];
        ['name','email','label'].forEach(k => {if(obj.hasOwnProperty(k)) txt.push(k+': '+obj[k]);});
         return txt.join(', ');}
         if (Array.isArray(text)) {
         const newtext=[];
         text.forEach((t,i)=> {newtext.push(stringify(t));});
         text=newtext.join('; ');  } else text=stringify(text);
        }
        text=make_text(text);

    return text;
  }

  function make_line(row) {
    row = row.join(options.columndelimiter);
    return row.trim();
  }
  let rows = [],
    row = [];
  const columns = [];
  const theads = state.dom.querySelectorAll('thead th');
  let j=0;
  state.grid.columns.forEach(column => {
    if ((hidden === true || !column.hasOwnProperty('hidden')) && (options.skipcolumns.length === 0 || options.skipcolumns.indexOf(column.index) < 0)) {
      const obj = {
        name: (column.hidden)?(column.name) ? column.name : ((column.label) ? column.label : String(column.index)):theads[j].textContent,
        hidden: (column.hasOwnProperty('hidden')) ? true : false,
        index: column.index
      };
      //headings
        let label =obj.name;
        if (!label) label = 'C' + column.index;
        row.push(text_convert(label));
        columns.push(obj);
    }
     if (!column.hidden ) j++;
  });
  rows.push(make_line(row));

  // Virtual scroll only keeps a moving window of <tr>s mounted in state.dom, so reading
  // rows straight from the live tbody silently dropped every row scrolled out of view.
  // Render each data row off-screen instead, reusing the table's own column renderers so
  // formatted values (numbers, checks, links...) still match what's shown on screen.
  // getVisibleRowCount/resolveRowIndex go through grid.filteredIndexes, so an active
  // search filter is respected the same way it is for on-screen rendering.
  const visibleRowCount = state.getVisibleRowCount();
  for (let pos = 0; pos < visibleRowCount; pos++) {
    const i = state.resolveRowIndex(pos);
    row = [];
    j=0;
    const tr = state.createTableRow(state.grid.data[i], i);
    const tds = tr.querySelectorAll('th,td');
    state.grid.columns.forEach((column) => {
      const index = column.index;
      if ((hidden === true || !column.hidden) && (options.skipcolumns.length === 0 || options.skipcolumns.indexOf(index) < 0)) {
        const value = (column.hidden) ? state.grid.data[i][index] : (tds[j]) ? tds[j].textContent : 'None';
        row.push(text_convert(value));
      }
      if(!column.hidden) j++;
    });
    rows.push(make_line(row));
  }

  const str = rows.join(options.linedelimiter);
  // Download
  if (options.download) {
    // Create a link to trigger the download
    const lnk = document.createElement("a")
    lnk.href = encodeURI(`data:text/csv;charset=utf-8,${str}`)
    lnk.download = `${options.filename || "datatable_export"}.csv`
    // Append the link
    document.body.appendChild(lnk);
    // Trigger the download
    lnk.click();
    // Remove the link
    document.body.removeChild(lnk);
  }
  return str;
}