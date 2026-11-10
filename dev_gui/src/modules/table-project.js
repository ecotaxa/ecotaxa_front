import {
  models,
  css,
  typeimport, domselectors
} from '../modules/modules-config.js';

import equal from 'deep-equal';
import {create_box, unescape_html, fetchSettings} from "./utils";
import {AlertBox} from "./alert-box";
css.lastused = "last-used";
css.small = "tdsmall";

export const initImport = async (state) => {
  function itemRemove(value, item) {
    if (state.params.import) {
      switch (state.params.import) {
        case typeimport.project:
          function remove_from_imports(name, value) {
            const idx = state.dataImport.imports[name].indexOf(value);
            if (idx > -1) state.dataImport.imports[name].splice(idx, 1);
          }
          //const selector = state.dom.querySelector('[' + state.dataImport.selector + '="' + value + '"]');
          break;
      }
    }
  }
  const {
    DataImport
  } = await import('../modules/data-import.js');
  state.dataImport = new DataImport(state);

  // override import functions
  if (state.params.import==typeimport.renamingrules) {
    state.params.cellid=state.cellidname='recast_id';
    state.params.from='prjtaxorecast';
    state.dataImport.replacebutton=null;
    state.dataImport.addResetButton= function() {return;}
    state.dataImport.populateImportZone= function(add, items,what=null) {
      if (!state.dataImport.importzone) return;
      const importzone=state.dataImport.importzone;
      importzone.classList.remove(css.hide);
      const sort_func=(a, b) => {
        let x = a[1];
        let y = b[1];
        return +(x > y) || -(y > x);
      }
    let objitems={};
    if (importzone.innerHTML.trim()!==``) objitems=JSON.parse(importzone.innerHTML);
    if (add) {
       objitems = {...objitems,...items};
       Object.entries(objitems).sort(sort_func);
    }
      else {
        Object.entries(items).forEach(([key, value]) => {
        if (objitems[key]!==undefined)  delete objitems[key];
      });
    }
      importzone.innerHTML=JSON.stringify(objitems);
  }

  state.dataImport.importRenamingRules = async function() {
    let items = {};
    state.dataImport.imports[state.params.cellid].forEach(item => {
      items = {...items, ...item};
    });
    const importzone = state.dataImport.importzone;
    const source = importzone.dataset.source;
    const target = importzone.dataset.target;
    if (source === undefined || target === undefined) return;
     items={...items,...{"lauderia annulata":[50328,"Copelatus"]}};
    const importcontainer = document.getElementById((importzone.dataset.origin) ? importzone.dataset.origin : importzone.dataset.type);
    importcontainer.querySelectorAll('[id^="' + source + '"]').forEach(el => {
      if (items[el.value] === undefined) return;
      const idx = new String(el.id).replace(source, '');
      const rep = importcontainer.querySelector('[id="' + target + idx + '"]');
      if (rep !== null) {
        if (rep.tomselect) {
          const ts = rep.tomselect;
           if (ts.getItem(items[el.value][0]) === null) {
          if (ts.getOption(items[el.value][0]) === null) {
            let obj = {};
            obj[ts.settings.valueField] = items[el.value][0];
            obj[ts.settings.labelField] = unescape_html(items[el.value][1]);
            ts.addOption(obj);
          }
          ts.addItem(items[el.value][0]);
        }
        } else {
          const option = document.createElement('option');
          option.value = items[el.value][0];
          option.text = items[el.value][1];
          option.selected = true;
          rep.insertAdjacentElement(option);
        }
      }

    });
    return true;
  }
  }
  // virtual scroll destroys and recreates <tr>/<td> on every scroll, so the import
  // buttons/inputs on rows scrolled into view later need their handlers re-bound too.
  state.onRowsRendered(() => state.dataImport.rebindSelectors());
  if (state.params.import === typeimport.taxo) initTaxoLazyLoad(state);
  state.importfields = state.grid.columns.filter(column => (column.hasOwnProperty('selectcells')));
  state.importfields = (state.importfields.length) ? state.importfields[0].selectcells : null;
  state.dataImport.itemRemove = itemRemove;
  if (state.params.import && [typeimport.project].indexOf(state.params.import)>-1) {
    const {
      ImportList
    } = await import('../modules/table-projects-tools.js');
    ImportList(state, state.dataImport);
  }
  if (state.dataImport.initList) state.dataImport.initList();
  state.waitdiv.remove();
}

// "pick taxonomy from other project": the list comes without the taxa (too costly for all projects),
// preset & extra taxa are fetched, by small batches, for the rows which get displayed.
const taxolazy = {
  url: '/gui/prj/importtaxo',
  presetids: 'initclassiflist',
  batch: 40,
  delay: 150,
};

function initTaxoLazyLoad(state) {
  const tbody = state.dom.tBodies[0];
  if (!tbody) return;
  const presetcell = state.getCellId('preset');
  const extracell = state.getCellId('objtaxonnotinpreset');
  if (presetcell < 0 || extracell < 0) return;
  const pending = new Map(); // rowindex -> promise of the batch loading it
  let queue = new Set();
  let timer = null;

  const isLoaded = (rowindex) => (state.grid.data[rowindex] && state.grid.data[rowindex][presetcell] !== null);

  const rerenderRow = (rowindex, oldtr = null) => {
    oldtr = oldtr || tbody.querySelector('tr[data-rowindex="' + rowindex + '"]');
    if (!oldtr || !oldtr.isConnected) return null;
    const newtr = state.createTableRow(state.grid.data[rowindex], rowindex);
    if (oldtr.hidden) newtr.hidden = true;
    oldtr.replaceWith(newtr);
    if (state.dataImport) state.dataImport.rebindSelectors(newtr);
    return newtr;
  };

  const loadRows = (rowindexes) => {
    const body = {};
    const byprj = {};
    rowindexes.forEach(rowindex => {
      const projid = state.getCellData(rowindex, models.projid);
      if (projid === null) return;
      body[projid] = state.getCellData(rowindex, taxolazy.presetids) || '';
      byprj[projid] = rowindex;
    });
    const promise = fetch(taxolazy.url, fetchSettings({
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    })).then(response => {
      if (!response.ok) throw new Error(response.statusText);
      return response.json();
    }).then(details => {
      Object.entries(byprj).forEach(([projid, rowindex]) => {
        const detail = details[projid] || {};
        state.grid.data[rowindex][presetcell] = detail.preset || {};
        state.grid.data[rowindex][extracell] = detail.objtaxonnotinpreset || {};
        pending.delete(rowindex);
        rerenderRow(rowindex);
      });
    }).catch(err => {
      // leave the rows unloaded, they will be retried when displayed again
      rowindexes.forEach(rowindex => pending.delete(rowindex));
      AlertBox.addAlert({
        type: AlertBox.alertconfig.types.danger,
        content: String(err),
        dismissible: true,
      });
    });
    rowindexes.forEach(rowindex => pending.set(rowindex, promise));
    return promise;
  };

  const flush = () => {
    timer = null;
    const todo = Array.from(queue).filter(rowindex => !isLoaded(rowindex) && !pending.has(rowindex));
    queue = new Set();
    for (let i = 0; i < todo.length; i += taxolazy.batch) loadRows(todo.slice(i, i + taxolazy.batch));
  };

  const enqueue = (rowindex) => {
    if (isLoaded(rowindex) || pending.has(rowindex)) return;
    queue.add(rowindex);
    if (timer === null) timer = setTimeout(flush, taxolazy.delay);
  };

  // rows are rendered asynchronously (batches or virtual scroll window), watch which get on screen
  const visible = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      visible.unobserve(entry.target);
      const rowindex = parseInt(entry.target.dataset.rowindex, 10);
      if (!isNaN(rowindex)) enqueue(rowindex);
    });
  });
  const observeRows = (trs) => trs.forEach(tr => {
    if (tr.tagName !== 'TR' || tr.dataset.rowindex === undefined) return;
    if (!isLoaded(parseInt(tr.dataset.rowindex, 10))) visible.observe(tr);
  });
  new MutationObserver(mutations => {
    mutations.forEach(mutation => observeRows(Array.from(mutation.addedNodes)));
  }).observe(tbody, {childList: true});
  observeRows(Array.from(tbody.rows));

  // clicked before its batch came back: wait for it, or load this row alone
  state.ensureTaxa = async (rowindex, tr) => {
    if (isLoaded(rowindex)) return null;
    const promise = pending.get(rowindex) || loadRows([rowindex]);
    await promise;
    if (!isLoaded(rowindex)) return null;
    // the batch re-rendered the row if it was still in the DOM
    const current = tbody.querySelector('tr[data-rowindex="' + rowindex + '"]');
    return current || rerenderRow(rowindex, tr);
  };
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
      let nodecontact=null;
      if (contact) {
        nodecontact = {
          nodename: "A",
          attributes: {
            href: `mailto:${contact.email}`,
            class: "contact",
            target: "_blank"
          },
          childnodes: [state.setTextNode(contact.name)]
        };
        if (iscontact) nodecontact.attributes["data-contact"] = iscontact;
        node = [state.setTextNode(value),nodecontact];
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
            childnodes: node,
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
              // null: not loaded yet (lazy-load), keep it clickable
              impid = (impid !== null && equal(impid, {})) ? ` disabled` : ``;
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
          case models.project:
          case models.renamingrules:
            btns.push({
              nodename: "INPUT",
              attributes: {
                type: "checkbox",
                name: `${column.what}[]`,
                class: "form-checkbox",
                value: id
              },
            });
            break;
          case models.settings:
          case models.privileges:
          case models.fields:
          case models.formulae:
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
    access:(value, rowIndex, cellIndex, td = {}) => {
      const possible_access={"0":"Private","1":"Public","2":"Open"}
      td.html = possible_access[value];
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
      if (value === null) {
        // not loaded yet (lazy-load)
        td.childnodes = [state.setTextNode(`…`)];
        return td;
      }
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
    },
    jsonb:  (value, rowIndex, cellIndex, td = {}) => {
      if (!value || value === ``) td.childnodes = [state.setTextNode(``)];
     td.childnodes = [{
            nodename: "DIV",
            attributes: {
              class: "text",
            },
            childnodes: [state.setTextNode(JSON.stringify(value))]          }];
    return td;}
  }

}