import {
  format_license
} from '../modules/utils.js';
import {
  models,
  css
} from '../modules/modules-config.js';

import equal from 'deep-equal';
css.lastused = "last-used";
css.small = "tdsmall"
export const initImport = async (state) => {
  const {
    DataImport
  } = await import('../modules/data-import.js');
  state.importfields = state.grid.columns.filter(column => (column.selectcells));

  state.importfields = (state.importfields.length) ? state.importfields[0].selectcells : null;
  state.grid.columns.forEach((column, index) => {
    const key = column.name;
    const domheadings = state.dom.querySelectorAll('thead th');
    if (state.importfields.indexOf(key) >= 0) {
      domheadings[index].dataset.name = key;
    }
    // set headings dataset values for import module
    if (column.hasOwnProperty('selectcells')) {
      domheadings[index].dataset.selectcells = column.selectcells;

      if (column.what) domheadings[index].dataset.what = column.what;
    }

    ['autocomplete', 'parts', 'value'].forEach(prop => {
      if (column.hasOwnProperty(prop)) domheadings[index].dataset[prop] = column[prop];
    });

  });
  state.dataImport = new DataImport(state);
  state.waitdiv.remove();
}


export default function(state) {



  // get the css fixed length of progress bar

  let progressw = 0;
  if (document.styleSheets && document.styleSheets.length && document.styleSheets[0].cssRules) {
    Object.values(document.styleSheets[0].cssRules).forEach((rule, i) => {
      if (rule.selectorText && rule.selectorText.trim() === '.progress data') {
        progressw = rule.style.cssText.split(';');
        progressw.forEach(r => {
          r = r.split(':');
          if (r[0].trim() === 'max-width' && r.length > 1) {
            progressw = parseInt(r[1].trim());
            return;
          }
        });
      };
      if (progressw > 0) return;
    });
  }
  progressw = (progressw > 0) ? progressw : 64;
  state.cellidname = models.projid;

  state.initImport = initImport;
  if (state.params.lastused) {
    const lastused = JSON.parse(state.params.lastused);
    state.setRowAttributes = (state, tr, id) => {
      if (id && lastused.indexOf(id) >= 0) {
        tr.classList.add(css.lastused);
      }
      return tr;
    }
  }
  return {
    contact: (value, rowIndex, cellIndex, td = {}) => {
      const about = (Array.isArray(value)) ? Boolean(value[1]) : false;
      value = (Array.isArray(value)) ? String(value[0]).trim() : String(value).trim();
      if (value === null) value = ``;
      let node = [];
      //cell value is an array with title and  boolean which tells if about is autho or not
      // display stats and info about the project if ok
      const id = state.getCellData(rowIndex, models.projid);
      // contact
      let contact = state.getCellData(rowIndex, models.contact);
      let iscontact = false;
      if (contact === null) {
        contact = state.getCellData(rowIndex, models.managers);
        contact = (contact && contact.length) ? contact[0] : null;
      } else iscontact = true;

      if (contact) {
        const nodecontact = {
          nodename: "A",
          attributes: {
            href: `mailto:${contact.email}`,
            class: "contact",
            target: "_blank"
          },
          childnodes: [state.setTextNode(contact.name)]
        };
        if (iscontact) nodecontact.attributes["data-contact"] = iscontact;
        node = [state.setTextNode(value), nodecontact];
      } else node = [state.setTextNode(value)];
      if (about === true) {
        td.childnodes = [{
          nodename: "DETAILS",
          attributes: {
            "data-id": id,
            "data-what": models.about
          },
          childnodes: [{
            nodename: "SUMMARY",
            childnodes: node
          }]
        }];
      } else td.childnodes = node;
      return td;
    },
    imports: (value, rowIndex, cellIndex, td = {}) => {
      const id = state.getCellData(rowIndex, models.projid);
      const column = state.grid.columns[cellIndex];
      if (column.hasOwnProperty('selectcells')) {
        let btns = [],
          txt = (state.params.btn) ? state.params.btn : 'import';

        switch (column.what) {
          case models.taxo:
            ((column.parts) ? column.parts : column.selectcells).forEach((v, index) => {
              let impid = state.getCellData(rowIndex, v);
              impid = (impid === null || equal(impid, {})) ? ` disabled` : ``;
              if (index > 0) txt = (state.params.btn1) ? state.params.btn1 : 'extra';
              btns.push({
                nodename: "BUTTON",
                attributes: {
                  class: `btn is-preset${impid}`,
                  type: 'button'
                },
                childnodes: [{
                  nodename: "I",
                  attributes: {
                    class: `icon-md  ${((impid === ``)? `icon-plus-sm`:``)}`,
                    type: 'button'
                  },
                  childnodes: []
                }, state.setTextNode(txt)]
              });
            });
            break;
          case models.settings:
          case models.privileges:
          case models.fields:
            btns.push({
              nodename: "BUTTON",
              attributes: {
                class: `btn is-preset`,
                type: 'button'
              },
              childnodes: [state.setTextNode(txt)]
            });
            break;
        }
        td.childnodes = btns;
      } else td.childnodes = [];
      return td;
    },
    controls: (value, rowIndex, cellIndex, td = {}) => {
      let controls = [];
      const id = state.getCellData(rowIndex, models.projid);
      Object.entries(value).forEach(([key, action]) => {
        let node = {
          nodename: "A"
        };
        switch (key) {
          case "A":
            node.attributes = {
              class: "btn is-annotate order-1",
              href: `/prj/${id}`
            };
            break;
          case "V":
            node.attributes = {
              class: "btn is-view order-1",
              href: `/prj/${id}`
            };

            break;
          case "M":
            node.attributes = {
              class: "btn is-manage order-2",
              href: `/gui/prj/edit/${id}`
            };
            break;
          case "R":
            const contact = state.getCellData(rowIndex, models.contact);
            node.attributes = {
              class: "btn is-request order-2",
              href: `mailto:${contact.email}?${id}`
            };
            break;
        }

        node.childnodes = [state.setTextNode(action)];
        controls.push(node);
      });
      td.attributes = (td.hasOwnProperty('attributes')) ? td.attributes : {};
      td.attributes["class"] = (td.attributes["class"]) ? td.attributes["class"] + " " + css.component.table.controls : css.component.table.controls;
      td.childnodes = controls;
      return td;
    },
    progress: (value, rowIndex, cellIndex, td = {}) => {
      if (value === null) value = 0;
      // fixed in px  displays better than %
      value = (parseInt(value) - parseFloat(value).toFixed(2) == 0) ? parseInt(value) : parseFloat(value).toFixed(2);
      const pct = parseFloat(value * (progressw / 100)).toFixed(2)
      const node = {
        nodename: "DATA",
        attributes: {
          style: `width:${pct}px`,
          "data-w": `${pct}`
        },
      }

      td.attributes = (td.hasOwnProperty('attributes')) ? td.attributes : {};
      td.attributes["class"] = (td.attributes["class"]) ? td.attributes["class"] + " " + css.progress : css.progress;
      td.childnodes = [state.setTextNode(String(value) + '%'), node];
      return td;
    },
    license: (value, rowIndex, cellIndex, td = {}) => {
      td.html = format_license(value, true);
      return td;
    },
    status: (value, rowIndex, cellIndex, td = {}) => {
      td.attributes = (td.hasOwnProperty('attributes')) ? td.attributes : {};
      td.attributes["class"] = (td.attributes["class"]) ? td.attributes["class"] + css.small : css.small;
      td.html = value;
      return td;
    },
    privileges: (value, rowIndex, cellIndex, td = {}) => {

      if (!value || value === ``) td.childnodes = [state.setTextNode(``)];
      let rights = [];
      Object.entries(value).forEach(([right, members]) => {
        let mb = [];
        if (members.length) {
          members.forEach(member => {
            mb.push(member.name);
          });
          rights.push({
            nodename: "DIV",
            attributes: {
              class: "rights",
              "data-r": right
            },
            childnodes: [state.setTextNode(mb.join(`, `))]
          });
        }
      });
      td.childnodes = rights;
      return td;
    },
    taxons: (value, rowIndex, cellIndex, td = {}) => {
      if (value === null) td.childnodes = [state.setTextNode(``)];
      const num = Object.keys(value).length;
      if (num > 0) {
        value = Object.values(value).join(', ');
        td.childnodes = [{
          nodename: "DIV",
          attributes: {
            class: css.component.table.tip,
            "data-num": num
          },
          childnodes: [state.setTextNode(value)]
        }];
      } else td.childnodes = [state.setTextNode(``)];
      return td;
    }
  }

}