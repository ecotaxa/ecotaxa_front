import {
  css
} from '../modules/modules-config.js';
export default function(state) {
  return {
    taxa: (value, rowIndex, cellIndex, td = {}) => {

      if (!Array.isArray(value)) td.childNodes = [];
      let html = [];
      value.forEach(v => {
        if(v[1][1]=='D') html.push({
          nodename: "SPAN",
          attributes: {
            "class": css.deprecated
          },
          childnodes: [state.setTextNode(v[1][0])]});
        else  html.push(state.setTextNode(v[1][0]));
      });
      td.childnodes = [{
        nodename: 'DIV',
        attributes: {
          class: css.component.table.tip,
          "data-num": html.length
        },
        childnodes: html //[state.setTextNode(html.join(`, `))]
      }];
      return td;
    }

  }
}