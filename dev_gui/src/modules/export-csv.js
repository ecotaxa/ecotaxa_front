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
        console.log('obj.name',label)
        if (!label) label = 'C' + column.index;
        row.push(text_convert(label));
        columns.push(obj);
    }
     if (!column.hidden ) j++;
  });
  rows.push(make_line(row));
  const trs = state.dom.querySelectorAll('tbody tr');

  for (let i = 0; i < trs.length; i++) {
    row = [];
    j=0;
    const tds = trs[i].querySelectorAll('th,td');
    state.grid.columns.forEach((column) => {
      const index = column.index;
      if ((hidden === true || !column.hidden) && (options.skipcolumns.length === 0 || options.skipcolumns.indexOf(index) < 0)) {
        const value = (column.hidden) ? state.grid.data[i][index] : (tds[j]) ? tds[j].innerText : 'None';
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
    link = document.createElement("a")
    link.href = encodeURI(`data:text/csv;charset=utf-8,${str}`)
    link.download = `${options.filename || "datatable_export"}.csv`
    // Append the link
    document.body.appendChild(link);
    // Trigger the download
    link.click();
    // Remove the link
    document.body.removeChild(link);
  }
  return str;
}