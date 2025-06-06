import {
  models,
  css,
} from '../modules/modules-config.js';
import {
  unescape_html,
  fetchSettings
} from '../modules/utils.js';


function ImportList(state, attach = null) {
  const rowimported = -1;
  const cellid = state.getCellId(state.cellidname);
  const toggle = function(tr, value, idx) {
    tr.hidden = value;
    /*  if (value === true) tr.classList.add(css.disabled);
      else {
        tr.classList.remove(css.disabled);
        state.dataImport.resetSelector(tr);
      }*/
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
    // display only lines with fields values equals to record fields values - criteria is a list of cellnames
    const criteria_names = ['instrument', 'access'];
    const criteria_ids = [];
    criteria_names.forEach(colname => {
      const index = state.getCellId(colname);
      if (index > -1) criteria_ids.push(index);
    });
    if (criteria_ids.length !== criteria_names.length) return;

    let datas = state.grid.data;
    const indexes = [];
    datas = datas.filter((row, i) => {
      let compare = true;
      if (i !== recordindex) criteria_ids.forEach(idx => {
        compare = compare && (record[idx] === row[idx]);
      });
      if (compare) indexes.push(String(row[cellid]));
      return compare;
    });
    state.displaySelected(criteria_ids, indexes, cellid, toggle);
  }

  function resetFilter() {
    state.displaySelected([], [], cellid, toggle);
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