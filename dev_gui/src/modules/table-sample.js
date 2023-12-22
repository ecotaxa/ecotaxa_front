import {
  css
} from '../modules/modules-config.js';
export default function(state) {
  return {
    taxa: (value, rowIndex, cellIndex, td = {}) => {

      if (!Array.isArray(value)) td.childNodes = [];
      let html = [];
      value.forEach(v => {
        html.push(v[1]);
      });
      td.childnodes = [{
        nodename: 'DIV',
        attributes: {
          class: css.component.table.tip,
          "data-num": html.length
        },
        childnodes: [state.setTextNode(html.join(`, `))]
      }];
      return td;
    }

  }
}