import {
  css
} from '../modules/modules-config.js';
export default function(state) {
  console.log('fromid', state.params.fromid)
  if (state.params.fromid) {
    state.afterLoad = () => {
      const tocheck = state.dom.querySelector('input[name="' + state.instanceid + 'select[]"][value="' + state.params.fromid + '"]');
      if (tocheck) tocheck.checked = true;
    }
  }
  return {
    selectmultiple: (value, rowIndex, cellIndex, td = {}) => {
      const column = state.grid.columns[cellIndex];
      value = (isNaN(value)) ? ((column.hasOwnProperty('field')) ? this.getCellData(rowIndex, column.field) : value) : value;
      td.childnodes = [{
        nodename: "INPUT",
        attributes: {
          type: "checkbox",
          name: `${state.instanceid}select[]`,
          value: String(value)
        }
      }];
      return td;
    },

  }
}