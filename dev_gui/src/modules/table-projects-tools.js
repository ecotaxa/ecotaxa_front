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

  async function compileProjectRecords() {
    const ts = state.dataImport.importzone.tomselect;
    const ids = (ts) ? ts.items : Array.from(state.dataImport.importzone.selectedOptions).map(option => option.value);
    if (ids.length === 0) return null;
    const url = '/gui/collection/aggregated' + '?' + new URLSearchParams({
      project_ids: ids.join(',')
    });
    const response = await fetch(url, fetchSettings({
      method: 'GET',
    }))
    let results = await response.json();
    results = results.aggregated;
    const collator = new Intl.Collator(undefined, {
      numeric: true,
      sensitivity: 'base'
    })

    if (Object.keys(results).indexOf("creator_users") >= 0) {
      results.creator_organisations = results.creator_users.map(u => u.organisation);
      results.creator_organisations.sort();
      const creator_users = results.creator_users.map(u => ({
        key: u.id,
        value: u.name,
        text: u.name + ' ' + u.email
      }));
      results.creator_users = creator_users
      results.creator_users.sort((a, b) => {
        return collator.compare(a.value, b.value)
      });
    }

    return results;
  }

  function filterByRecord(record, recordindex) {
    // display only lines with fields values equals to record fields values - criteria is a list of cellnames
    const criteria_names = ['instrument', 'visible'];
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
  } else return {
    filterByRecord,
    resetFilter,
  }

}
export {
  ImportList
}