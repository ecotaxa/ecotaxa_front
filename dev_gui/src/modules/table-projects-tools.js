import {
  models,
  css,
} from '../modules/modules-config.js';
import {
  unescape_html,
  fetchSettings,
  exec_handlers
} from '../modules/utils.js';


function ImportList(state, attach = null) {
  const rowimported = -1;
  const selectimports=[];
  const importindexes=[];
  const cellid = state.getCellId(state.cellidname);
  // display only lines with fields values equals to record fields values - criteria is a list of cellnames
  const criteria_names = ['instrument', 'access'];
  const criteria_ids = [];
  criteria_names.forEach(colname => {
      const index = state.getCellId(colname);
      if (index > -1) criteria_ids.push(index);
    });
  state.toggle = function(tr, value, idx, filtered=false) {
   if (filtered) { if(value) tr.classList.add(css.hide);
     else {tr.classList.remove(css.hide);
    // state.dataImport.resetSelector(tr);
    }
     } else tr.hidden = value;
  }

  async function compileProjectRecords(newone = 0) {
    const ts = state.dataImport.importzone.tomselect;
    const ids = (ts) ? ts.items : Array.from(state.dataImport.importzone.selectedOptions).map(option => option.value);
    if (ids.length === 0) return null;
    const url = '/gui/collection/aggregated' + '?' + new URLSearchParams({
      project_ids: ids.join(','),
      simulate:"y"
    });
    const response = await fetch(url, fetchSettings({
      method: 'GET',
    }))
    let results = await response.json();
    const excluded = results.excluded;
    delete results.excluded;
    const collator = new Intl.Collator(undefined, {
      numeric: true,
      sensitivity: 'base'
    })
   const key='creator';
   if (newone === 0 && Object.keys(results).indexOf(key+"_users") >= 0) {
      const users = results[key+"_users"].map(u => ({
        key: u.id,
        value: u.name,
        text: u.name + ' ' + u.email
      }));
      results[key+"_persons"] = users
      delete results[key+"_users"];
      results[key+"_persons"].sort((a, b) => {
        return collator.compare(a.value, b.value)
      });
    };
    return results;
  }

  function initList() {
    if (!state.dataImport) return;
    const plugin = state.dataImport;
    if (plugin.targetimport) {
      let selected = null;
      if (plugin.targetimport.tagName.toLowerCase() === 'select') {
        selected = [...plugin.targetimport.options].filter(opt => opt.selected);
        selected = selected.map(opt => parseInt(opt.value));
      } else selected = plugin.targetimport.value;
      plugin.selectors.forEach(selector => {
        if (selected.indexOf(parseInt(selector.value)) >= 0) selector.click();
      });
    }
  }

  function filterByRecord(record, recordindex) {
    if (criteria_ids.length !== criteria_names.length) return;
    let datas = state.grid.data;
    selectimports.push(record[cellid]);
    datas = datas.filter((row, i) => {
      let compare = true;
      if (i !== recordindex) criteria_ids.forEach(idx => {
        compare = compare && (record[idx] === row[idx]);
      });
      const val = String(row[cellid])
      if (compare && importindexes.indexOf(val)===-1) importindexes.push(val);
      return compare;
    });
    state.displaySelected(criteria_ids, importindexes, cellid,true);
  }

  function resetFilter(record, recordindex) {
    let index = selectimports.indexOf(record[cellid]);
    if (index > -1)  selectimports.splice(index, 1);
    index = importindexes.indexOf(String(record[cellid]));
    if (index > -1)  importindexes.splice(index, 1);
    if (selectimports.length===0) state.displaySelected([],[], cellid, true);
    else state.displaySelected(criteria_ids, importindexes, cellid,true);
  }

  if (attach) {
    attach.filterByRecord = filterByRecord;
    attach.resetFilter = resetFilter;
    attach.compileProjectRecords = compileProjectRecords;
    attach.initList = initList;
  } else return {
    filterByRecord,
    resetFilter,
    initList
  }

}
export {
  ImportList
}