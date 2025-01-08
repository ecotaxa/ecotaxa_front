import DOMPurify from 'dompurify';
import {
  JsTomSelect
} from "../modules/js-tom-select.js";
import {
  ProjectPrivileges
} from '../modules/project-privileges.js';
import {
  fetchSettings,
  unescape_html,
  create_box
} from '../modules/utils.js';

import {
  models,
  typeimport,
  css,
  defined_privileges,
  domselectors
} from '../modules/modules-config.js';
const key_privileges = Object.keys(defined_privileges).reduce(function(result, key) {
  result[key] = key;
  return result;
}, {});
let instance;
css.imported = 'imported';
css.tomselected = 'tomselected';
css.hiddenaccessible = 'ts-hidden-accessible';
css.arrowout = 'icon-arrow-pointing-out';
css.arrowin = 'icon-arrow-pointing-in';
domselectors.resetbutton = '.import-list-reset';
export class DataImport {
  content_selector = '.modal-content';
  imports = [];
  taxos = ["preset", "extra"];
  importcontainer;
  importzoneid; // target element to add/replace datasto import
  importid = 'importzone'; // importzone built to display data to import
  importzone = null;
  selectors;
  button;
  clearbutton;
  replacebutton;
  tabbutton;
  dom;
  tbl = null;
  thcells = [];
  trs = [];
  datas;
  constructor(tbl, what = null, selector = null) {
    if (!tbl) return;
    // tbl is a TableComponent  ?
    this.tbl = (typeof(tbl) === 'object') ? tbl : null;
    selector = (selector === null) ? ((this.tbl.cellidname) ? "data-" + this.tbl.cellidname : "data-id") : selector;
    // get the table from table component or html table element id
    this.dom = (this.tbl) ? this.tbl.dom : document.getElementById(tbl);
    if (!this.dom) return;
    this.thcells = Array.from(this.dom.querySelectorAll('thead th'));
    this.trs = Array.from(this.dom.querySelectorAll('tbody tr'));
    const grid = (this.tbl) ? this.tbl.grid : null;
    this.datas = (grid) ? grid.data : this.trs.map(tr => {
      return Array.from(tr.childNodes).forEach(cell => {
        return cell.innerText;
      });
    });
    what = (what) ? DOMPurify.sanitize(what) : (tbl && tbl.params && tbl.params.import) ? tbl.params.import : (this.dom.dataset.import) ? DOMPurify.sanitize(this.dom.dataset.import) : null;
    if (!instance || instance.doc !== this.dom) {
      // defaultoptions - keep like that

      const options = {
        importcontainer: '#data-import-' + what,
        btns: '.btns-imports',
        button: '#add-import-' + what,
        replacebutton: '#replace-import-' + what,
        tabbutton: '#tab-import-' + what,
      };
      this.selector = selector;

      this.importcontainer = options.importcontainer instanceof HTMLElement ? options.importcontainer : document.querySelector(options.importcontainer);
      this.form = (options.form) ? ((options.form) instanceof HTMLElement ? options.form : document.querySelector(options.form)) : this.dom.closest('form');
      this.button = options.button instanceof HTMLElement ? options.button : document.querySelector(options.button);
      this.replacebutton = options.replacebutton instanceof HTMLElement ? options.replacebutton : document.querySelector(options.replacebutton);
      this.tabbutton = options.tabbutton instanceof HTMLElement ? options.tabbutton : document.querySelector(options.tabbutton);
      this.importid = this.importid + '_' + what;
      this.init(options);
      instance = this;

    }
    return instance;
  }

  init(options) {
    // hide importzone
    this.showImport(false);
    // remove line of target proj
    let projid = this.form.querySelector('#' + domselectors.projid);
    if (projid && projid.value) {
      projid = this.dom.querySelector('[' + this.selector + '="' + projid.value + '"]');
      if (projid) projid.hidden = true;
    }
    const indextocheck = this.indexToCheck();
    this.selectors = this.dom.querySelectorAll('[' + this.selector + '] button, [' + this.selector + '] input');
    this.selectors.forEach(selector => {
      // checkbox possible
      const index = Array.from(selector.parentElement.children).indexOf((selector));
      if (indextocheck && selector.closest('tr').children[indextocheck[index]].innerHTML === '') this.disableSelector(selector, false);
      else {
        const evt = (selector.tagName.toLowerCase() === 'input') ? 'change' : 'click';
        const apply_selection = (e) => {
          e.preventDefault();
          e.stopImmediatePropagation();

          const target = e.currentTarget;
          const add = (evt === 'click' || target.checked === true);
          this.disableSelector(target, add);
          this.toImport(target.parentElement, index, add);
        };
        selector.removeEventListener(evt, apply_selection, false);
        selector.addEventListener(evt, apply_selection, false);
      };
    });
    if (this.tabbutton) {
      this.tabbutton.addEventListener('click', (e) => {
        e.stopImmediatePropagation();
        e.preventDefault();
        this.resizeZone(e);
      });
    }
  }

  columnProperty(name, index) {
    const th = this.thcells[index];
    if (this.tbl) return (this.tbl.grid.columns[index].hasOwnProperty(name)) ? this.tbl.grid.columns[index][name] : null;
    else return (th.dataset[name]) ? th.dataset.name : null;
  }
  columnIndex(prop, value) {
    return Array.from(this.dom.querySelectorAll('thead th')).findIndex(th => (th.dataset[prop] && th.dataset[prop] === value));
  }
  gridColumnIndex(prop, value) {
    if (this.tbl) return this.tbl.grid.columns.findIndex(column => (column.hasOwnProperty(prop) && column[prop] === value));
    else return this.columnIndex(prop, value);
  }
  rowIndex(td) {
    const ref = (td.parentElement) ? td.parentElement : null;
    if (!ref) return null;
    return this.trs.findIndex(tr => (tr === ref));
  }
  disableSelector(selector, disable = true) {
    const type = selector.tagName.toLowerCase();
    if (type === "input") {
      if (selector.checked !== disable) selector.checked = disable;
    } // disable button but toggle checkbox
    else selector.disabled = disable;
  }

  getDataToImport(cell, celldata) {
    let toimport = celldata;
    if (cell !== null) {
      if (cell.dataset.autocomplete) {
        // select elements where key / value in different columns
        toimport = {
          value: celldata,
          key: null
        };
        let el = null;
        this.thcells.every((t, idx) => {
          if (t.dataset.name == thcell.dataset.autocomplete) {
            el = idx;
            return false;
          }
          return true;
        });
        if (el !== null) {
          el = this.datas[rowindex][el];

          toimport.key = el;
        }
      } else if (cell.dataset.value) toimport = cell.dataset.value;

    }
    return toimport;
  }
  getSelectCells(cellindex, whatpart) {
    const parts = this.columnProperty('parts', cellindex);
    let selectcells = this.columnProperty('selectcells', cellindex);
    selectcells = (selectcells) ? ((parts) ? [parts[whatpart]] : selectcells) : null;
    return selectcells;
  }

  populateImportZone(add, items) {

    if (!this.importzone) return;
    const ts = this.importzone.tomselect;
    if (ts) {
      Object.values(ts.options).forEach((opt) => {
        let obj = {};
        obj[opt[ts.settings.valueField]] = opt[ts.settings.labelField];
        if (!items[opt[ts.settings.valueField]]) items = Object.assign(items, obj);
      });
      items = Object.entries(items);
      // sort items
      items.sort((a, b) => {
        let x = a[1];
        let y = b[1];
        return +(x > y) || -(y > x);
      });
      //  ts.clear();
      //ts.clearOptions();
      // add ts items
      if (add) items.forEach(([key, text]) => {
        if (ts.getItem(key) === null) {
          if (ts.getOption(key) === null) {
            let obj = {};
            obj[ts.settings.valueField] = key;
            obj[ts.settings.labelField] = unescape_html(text.trim());
            ts.addOption(obj);
          }
          ts.addItem(key);
        }
      });
      else items.forEach(([key, text]) => {
        ts.removeItem(key);
      });
    } else {
      Object.values(this.importzone.options).forEach(opt => {
        let obj = {};
        obj[opt.value] = opt.text;
        if (!items[opt.value]) items = Object.assign(items, obj);
      });
      items = Object.entries(items);
      items.sort((a, b) => {
        let x = a[1];
        let y = b[1];
        return +(x > y) || -(y > x);
      });
      this.importzone.innerHTML = ``;
      if (add) items.forEach(([key, text]) => {
        const opt = this.importzone.querySelector('option[value="' + key + '"]');
        if (!opt) {
          const o = create_box('option', {
            value: key,
            selected: 'selected',
            text: text
          }, this.importzone);
        } else opt.selected = true;
      });
      else items.forEach(([key, text]) => {
        const opt = this.importzone.querySelector('option[value="' + key + '"]');
        if (opt) opt.remove(); // or opt.selected=false;
      });
    }
  }

  toImport(td, whatpart = 0, add = true) {
    // cell values in json  - no parse
    if (td.tagName.toLowerCase() !== 'td') td = td.closest('td');
    const rowindex = this.rowIndex(td);
    if (rowindex === null) return;
    let showbtns = true;
    let contact = null;
    const cellindex = td.cellIndex;
    const what = this.columnProperty('what', cellindex);
    if (!what) return;
    const parts = this.columnProperty('parts', cellindex);
    const selectcells = this.getSelectCells(cellindex, whatpart);
    if (!selectcells) return;
    if ([typeimport.settings, typeimport.privileges].indexOf(what) >= 0) this.imports[models.contact] = this.findContact(this.datas[rowindex]);
    if ([typeimport.project, typeimport.taxo, typeimport.privileges].indexOf(what) >= 0) this.createImportzone(what);
    this.addResetButton();
    let ts = null;
    selectcells.forEach((name, index) => {
      index = this.gridColumnIndex('name', name);
      if (index >= 0) {
        const tdindex = this.columnIndex('name', name);
        // show import buttons if importzone
        const cell = (tdindex >= 0) ? this.trs[rowindex].cells[tdindex] : null;
        if (cell) cell.classList.add(css.selected);
        const rowdata = this.datas[rowindex];
        const celldata = rowdata[index];
        const thcell = (tdindex >= 0) ? this.thcells[tdindex] : null;
        switch (what) {
          case typeimport.taxo:
            if (!this.importzone) return;
            // accumulate and show in import win - move the form field in modal win to view the changes and benefit of tom-select component functs...
            ts = this.importzone.tomselect;
            let taxons = celldata;
            if (taxons) {
              this.populateImportZone(add, taxons);
              showbtns = (Object.keys(taxons).length > 0);
              taxons = null;
            }
            break;
          case typeimport.privileges:
            const privs = celldata;
            // set everybody to 'view' if more than one project imported
            const resetpriv = ((ts && ts.items.length > 0) || (this.importzone.selectedIndex > 0));
            if (!this.importzone.tomselect) {
              this.importzone.currentlist = {};
              JsTomSelect.applyTo(this.importzone);
            }
            ts = this.importzone.tomselect;
            Object.entries(privs).forEach(([priv, members]) => {
              members.sort((a, b) => {
                return (b.name > a.name);
              });
              members.forEach(member => {
                const newpriv = (resetpriv) ? key_privileges.viewers : priv; // viewer if more than one project imported
                let opt;
                if (!this.importzone.currentlist || !this.importzone.currentlist[member.id]) {
                  if (ts) {
                    opt = ts.items.indexOf(member.id);
                    //TODO - test - opt should always be 0
                    if (opt >= 0) {
                      ts.removeItem(member.id);
                      ts.removeOption(member.id);
                    }
                    // addoption && addItem
                    opt = {
                      optgroup: newpriv
                    }
                    opt[ts.settings.valueField] = member.id;
                    opt[ts.settings.searchField] = member.name;
                    opt[ts.settings.labelField] = member.name;
                    ts.addOption(opt);
                    ts.addItem(member.id);
                  } else {
                    opt = this.importzone.querySelector('option[value="' + member.id + '"]');
                    if (opt === null) {
                      opt = create_box('option', {
                        value: member.id,
                        dataset: {
                          optgroup: newpriv
                        },
                        selected: true,
                        defaultSelected: true,
                        text: member.name
                      })
                      this.importzone.add(opt);
                    } else opt.dataset.optgroup = newpriv;
                  }
                }
              });
              if (ts) ts.refreshOptions(true);
            });
            showbtns = (((ts) ? ts.items.length : this.importzone.selectedIndex + 1) > 0);
            break;
          case typeimport.project:
            const ln = Object.keys(this.imports).length;

            if (!this.imports[name]) this.imports[name] = [];
            const data = this.getDataToImport(cell, celldata);
            if (add) this.imports[name].push(data);
            else {
              const idx = this.imports[name].indexOf(data);
              if (idx > -1) this.imports[name].splice(idx, 1);
            }
            if (name === models.projid) {
              const idx = this.columnIndex('name', 'title');
              // show import buttons if importzone
              const celllabel = (idx >= 0) ? this.trs[rowindex].cells[idx] : null;
              const datalabel = rowdata[idx];
              const label = (celllabel) ? this.getDataToImport(celllabel, datalabel) : data;
              const items = {};
              items[rowdata[this.tbl.getCellId(this.tbl.cellidname)]] = label;
              this.populateImportZone(add, items);
            }
            if (ln === 0) {
              console.log('filterbyrecord ', Object.keys(this.imports))
              if (add) this.filterByRecord(rowdata, rowindex);
              else this.resetFilter();
            }
            break;
          default:
            if (add) this.imports[name] = this.getDataToImport(cell, celldata);
            else {
              const idx = this.imports.indexOf(name);
              if (idx > -1) this.imports.splice(idx, 1);
            }
            break;
        }
      };
    });
    if (this.thcells.length) {
      if (this.button) {
        const activate = (!this.button.dataset.activated && ([typeimport.taxo, typeimport.privileges, typeimport.project].indexOf(what) >= 0));
        this.showImport(showbtns);
        if (activate) this.activateButtons(what, selectcells);
      } else this.makeImport(null, selectcells, what, true);
    }
  }
  messageZone(item) {
    console.log('itemmessage', item);
  }
  activateButtons(what, selectcells) {
    this.button.addEventListener('click', async (e) => {
      e.stopImmediatePropagation();
      e.preventDefault();
      await this.makeImport(e.currentTarget, selectcells, what, true);
    });
    this.replacebutton.addEventListener('click', async (e) => {
      e.stopImmediatePropagation();
      e.preventDefault();
      await this.makeImport(e.currentTarget, selectcells, what, true);
    });
    this.button.dataset.activated = true;
    this.replacebutton.dataset.activated = true;
  }

  findContact(tds, name = 'contact') {
    const index = this.gridColumnIndex('name', name);
    if (index >= 0) return tds[index] ? tds[index] : null;

    return null;
  }

  renderPrivileges(replace = false) {
    let privileges = {};
    const tzone = this.importzone.tomselect;
    const pushpriv = (member, priv) => {
      const obj = {
        id: member.id,
        name: member.name,
        priv: priv
      }
      if (privileges[priv]) privileges[priv].push(obj);
      else privileges[priv] = [obj];
    }

    if (tzone) {
      const members = [...tzone.items];
      const options = Object.assign({}, tzone.options);
      members.forEach(member => {
        member = options[member];
        if (member) pushpriv(member, member.optgroup);

      })
    } else {
      this.importzone.options.forEach(member => {
        if (member.selected) pushpriv(member, member.dataset.optgroup);
      })
    }

    if (this.importPrivileges(privileges, replace)) {
      if (tzone) {
        tzone.clear();
        tzone.clearOptions();
      } else this.importzone.innerHTML = ``;

    }

  }

  importPrivileges(privileges, clear = false) {
    const projectPrivileges = this.form.querySelector('.' + domselectors.component.privileges.ident);
    if (projectPrivileges === null || !projectPrivileges.jsprivileges) return;
    const importedtag = (input) => {
      this.setImportedTag(input, null);
    }
    const dismiss = () => {
      this.dismiss();
    }
    const contact = (clear === true && this.imports[models.contact]) ? this.imports[models.contact] : null;
    return (projectPrivileges.jsprivileges.importPrivileges(privileges, clear, contact, importedtag, dismiss));
  }

  resetSelector(tr) {
    const resets = {};
    const append_resets = (name, td, i) => {
      const rowindex = this.rowIndex(td);
      const celldata = this.datas[rowindex][i];
      const cell = this.trs[rowindex].cells[i];
      const data = this.getDataToImport(cell, celldata);
      if (!resets[name]) resets[name] = [data];
      else if (resets[name].indexOf(data) < 0) resets[name].push(data);
    }
    const selectors = tr.querySelectorAll('[' + this.selector + '] button, [' + this.selector + '] input');
    selectors.forEach((selector, i) => {
      if (selector.disabled) this.disableSelector(selector, false);
      const name = (selector.parentElement.dataset.name) ? selector.parentElement.dataset.name : null;
      append_resets(name, selector.parentElement, i);
    });
    tr.querySelectorAll('td.' + css.selected).forEach((td, i) => {
      td.classList.remove(css.selected);
      append_resets(name, td, i);
    });
    return resets;
  }

  resetSelectors() {
    this.selectors.forEach((selector, i) => {
      if (selector.disabled) this.disableSelector(selector, false);
    });
    this.dom.querySelectorAll('td.' + css.selected).forEach(td => {
      td.classList.remove(css.selected);
    });
  }
  resetImports() {
    this.imports = [];
    if (this.importzone) {
      if (this.importzone.currentlist) this.importzone.currentlist = {};
      if (this.importzone.tomselect) this.importzone.tomselect.clear();
      else switch (this.importzone.tagName.toLowerCase()) {
        case 'input':
          this.importzone.value = '';
          break;
        case 'select':
          this.importzone.selectedIndex = -1;
          break;
      }
    }
  }

  activateClear() {
    const clearbutton = document.getElementById('clear-' + this.importid);
    if (!clearbutton) return;
    clearbutton.addEventListener('click', (e) => {
      e.stopImmediatePropagation();
      e.preventDefault();
      if (!this.importcontainer) return;
      this.resetSelectors();
      this.resetImports();
      this.button.disabled = false;
      this.replacebutton.disabled = false;
      this.showImport(false);
    });
  }
  createImportzone(name) {
    this.showImport(true);
    let ts = false;
    if (!this.importzone) {
      if (name === typeimport.privileges) {
        this.importzone = create_box('select', {
          id: this.importid,
          dataset: {
            type: models.user,
            priv: true,
          },
          multiple: true
        }, this.importcontainer);
        ts = true;
      } else {
        const import_target = (this.form.querySelector('[name="' + name + '"]')) ? this.form.querySelector('[name="' + name + '"]') : this.form.querySelector('[data-type="' + name + '"]');
        if (!import_target) return;
        ts = import_target.tomselect;
        this.importzoneid = import_target.id;
        // tomselect ?
        const importzone = import_target.cloneNode();
        importzone.classList.remove(css.tomselected);
        importzone.classList.remove(css.hiddenaccessible);
        // keep original id to replace data on apply import
        importzone.dataset.origin = importzone.id;
        importzone.id = this.importid;
        importzone.name = this.importid + '_' + importzone.name;
        this.importcontainer.prepend(importzone);
        this.importzone = importzone;
        if (ts) {
          JsTomSelect.applyTo(this.importzone);
          ts = this.importzone.tomselect;
        }
        if (ts) {
          ts.on("item_remove", (value, item) => {
            this.itemRemove(value, item);
          });
        }
        this.activateClear();
      }

    }

  }
  cloneImport(btn) {
    const import_target = this.form.querySelector('#' + this.importzone.dataset.origin);
    if (!import_target) return false;
    const ts = import_target.tomselect;
    if (ts) {

      // only if replace specified
      if (btn.dataset.replace && btn.dataset.replace === 'replace') {
        ts.clear();
        ts.clearOptions();
      }
      const tzone = this.importzone.tomselect;
      const items = [...tzone.items];
      const options = Object.assign({}, tzone.options);
      items.forEach((e) => {
        let el = {};
        el[ts.settings.valueField] = e;
        el[ts.settings.labelField] = unescape_html(options[e][ts.settings.labelField]);
        el[ts.settings.searchField] = unescape_html(options[e][ts.settings.labelField]);
        if (ts.getOption(el[ts.settings.valueField]) === null) ts.addOption(el);
        if (ts.getItem(el[ts.settings.valueField]) === null) ts.addItem(el[ts.settings.valueField]);
        console.log('ts.items', ts.items)
      });
      //  tzone.clearOptions();
    } else {
      if (btn.dataset.replace && btn.dataset.replace === 'replace') import_target.innerHTML = ``;
      import_target.innerHTML = DOMPurify.sanitize(this.importzone.innerHTML);
      this.importzone.innerHTML = ``;
    }
    return true;
  }

  async makeImport(btn, selectcells, what, close = false) {
    let done = true,
      ts = null;

    switch (what) {
      case typeimport.taxo:
        if (!this.importzone) return false;
        done = this.cloneImport(btn);
        break;
      case typeimport.privileges:
        if (!this.importzone) return false;
        done = this.renderPrivileges((btn.dataset.replace && btn.dataset.replace === 'replace'));
        if (this.importzone.currentlist) this.importzone.currentlist = {};
        break;
      case typeimport.project:
        if (!this.importzone) return false;
        const results = await this.compileProjectRecords();
        done = this.cloneImport(btn);
        const idx = selectcells.indexOf(models.projid);
        if (idx >= 0) selectcells.splice(idx, 1);
        ["creator_users", "creator_organisations", "classiffieldlist", "privileges", "access", "status", "cnn_network_id"].forEach(result => {
          this.imports[result] = results[result];
        });
        this.imports["init_classif_list"] = results.initclassiflist;
      default:
        const ts_add_select_item = function(ts, data) {
          const el = {};
          if (typeof(data) == 'string') {
            el[ts.settings.labelField] = unescape_html(data);
            el[ts.settings.valueField] = unescape_html(data);
            el[ts.settings.searchField] = unescape_html(data);
          } else {
            el[ts.settings.labelField] = unescape_html(data.value);
            el[ts.settings.valueField] = data.key;
            el[ts.settings.searchField] = unescape_html(data.value);
          }
          if (ts.getOption(el[ts.settings.valueField]) === null) ts.addOption(el);
          if (ts.getItem(el[ts.settings.valueField]) === null) ts.addItem(el[ts.settings.valueField]);
        }
        const add_select_option = function(input, data) {
          let attr = {
            selected: true
          };
          if (typeof(data) === 'string') attr.value = attr.text = data;
          else {
            attr.value = data.key;
            attr.text = data.value;
          }
          const option = create_box('option', attr, input);
        }
        const add_input_option = function(input, data) {
          if (input.multiple) {
            let values = input.value.split(',');
            values.push(data.key);
            input.value = values.join(',');
          } else input.value = data;

        }
        selectcells.forEach((name, index) => {
          let input = ((this.form.querySelector('[data-importfield="' + name + '"]')) ? this.form.querySelector('[data-importfield="' + name + '"]') : this.form.querySelector('[name="' + name + '"]'));
          if (input && input.dataset.noimport) return;
          if (input && this.imports[name] !== undefined) {
            const type = (input.type) ? input.type : input.tagName.toLowerCase();
            ts = input.tomselect;
            if (['init_classif_list'].indexOf(name) >= 0) {
              let ids = this.imports[name];
              if (Array.isArray(ids)) ids = ids.join(',');
              else ids = ids.replace('[', '').replace(']', '').replaceAll(' ', '');
              if (ids !== '') {
                if (ts) ts.wrapper.classList.add('wait-for-results');
                let opts = fetchSettings(),
                  url = '';
                const formData = new FormData();
                formData.append('idlist', ids);
                url = '/search/taxoresolve' //+ new URLSearchParams({'idlist': ids});
                opts = fetchSettings({
                  'method': 'POST',
                  'body': formData
                });
                fetch(url, opts).then(response =>
                  response.json()
                ).then(results => {
                  const ts = input.tomselect;
                  if (ts) {
                    results = Object.entries(results);
                    results.forEach(([key, text]) => {
                      const el = {
                        key: DOMPurify.sanitize(key),
                        value: DOMPurify.sanitize(text)
                      }
                      ts_add_select_item(ts, el);
                    });
                    ts.wrapper.classList.remove('wait-for-results');
                  } else if (type.indexOf('select') === 0) {
                    input.querySelectorAll('option').forEach(option => {
                      option.remove();
                    });
                    Object.entries(results).forEach(([key, text]) => {
                      const el = {
                        key: DOMPurify.sanitize(key),
                        value: DOMPurify.sanitize(text)
                      }
                      add_input_option(input, el);
                    });

                  } else {
                    Object.entries(results).forEach(([key, text]) => {
                      const el = {
                        key: DOMPurify.sanitize(key),
                        value: DOMPurify.sanitize(text)
                      }
                      add_select_option(input, el);
                    });
                  }
                  results = null;
                  this.setImportedTag(input);
                });
              }
            } else if (ts) {
              if (input.multiple) this.imports[name].forEach(data => {
                console.log('data', data)
                ts_add_select_item(ts, data)
              });
              else ts_add_select_item(ts, this.imports[name]);
              this.setImportedTag(input);
            } else {
              switch (type) {
                case 'radio':
                case 'checkbox':
                  const tocheck = this.form.querySelector('[name="' + name + '"][value="' + this.imports[name] + '"]');
                  if (tocheck) tocheck.checked = true;
                  break;
                case 'select-multiple':
                case 'select':
                  if (input.multiple) this.imports[name].forEach(data => {
                    add_select_option(input, data);
                  });
                  else add_select_option(input, this.imports[name]);
                  break;
                default:
                  input.value = this.imports[name];
                  break;
              }
              this.setImportedTag(input);
            }
            if (what !== typeimport.settings) input.focus();
            done = done && true;


          } else if (name === typeimport.privileges) {
            //const clearprivileges = (what === typeimport.settings);
            const clearprivileges = false;
            done = done && this.importPrivileges(this.imports[name], clearprivileges);
          }
        });
        break;
    }
    if (done === true && close == true) {
      this.dismiss();
      if (this.form) this.form.dispatchEvent(new CustomEvent('validate'));
    }
  }

  setImportedTag(input, selector = domselectors.component.form.formbox) {
    if (input === null) return;
    let el = (selector === null) ? input : ((input.closest(selector)) ? input.closest(selector) : input.closest('fieldset'));
    if (!el) return;
    const removetag = (e) => {
      delete el.dataset.isimported;
      el.classList.remove(css.imported);
      input.removeEventListener('change', removetag);
    }
    el.dataset.isimported = this.form.dataset.isimported;
    el.classList.add(css.imported);
    if (input.dataset.unique !== undefined) {
      input.dataset.unique = input.value;
    }
    setTimeout(function() {
      input.addEventListener('change', removetag);
    }, 500);
  }

  dismiss(clear = false) {
    if (this.button) this.showImport(false);
    const container = this.dom.closest('details');
    if (container) {
      container.open = false;
      if (clear === true) container.querySelector(this.content_selector).innerHTML = ``;
    }

  }
  indexToCheck() {
    // index of cells to check if empty and disable row  import btn
    const grid = (this.tbl) ? this.tbl.grid : null;
    if (!grid) return [0];
    let index = grid.columns.findIndex(column => (column.what && column.what === typeimport.taxo));
    if (index === -1) return [0];
    const parts = (grid.columns[index].parts) ? grid.columns[index].parts : null;
    if (parts) {
      const indextocheck = grid.columns.filter((column, i) => {
        if (parts.indexOf(column.name) >= 0) return i;
      }).map(v => {
        return v.index;
      });
      return indextocheck;
    }

  }
  addResetButton() {
    if (!this.tbl || !this.tbl.params.hasOwnProperty("reset")) return;
    let resetbtn = this.dom.parentElement.querySelector(domselectors.resetbutton);
    if (resetbtn === null) {
      resetbtn = create_box('a', {
        class: domselectors.resetbutton.substr(1),
        text: this.tbl.params.reset
      }, this.dom.parentElement.firstChild);
    }
    resetbtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();
      this.resetSelectors();
      this.resetImports();
    });

  }
  // show / hide importzone and buttons
  showImport(show) {
    if (!this.button) return;
    if (show === false) {
      this.button.classList.add(css.hide);
      this.replacebutton.classList.add(css.hide);
      this.importcontainer.classList.add(css.hide);
      if (this.tabbutton) this.tabbutton.classList.add(css.hide);
    } else {
      if (this.importzone) {
        this.button.classList.remove(css.hide);
        this.replacebutton.classList.remove(css.hide);
        this.importcontainer.classList.remove(css.hide);
        this.button.disabled = false;
        if (this.tabbutton) {
          this.tabbutton.classList.remove(css.hide);
          if (this.importzone.tomselect) {
            this.tabbutton.disabled = false;
          } else this.tabbutton.disabled = true;
        }
      }
    }

  }
  // resize importzone
  resizeZone(e) {
    const div = this.importcontainer.closest(domselectors.component.import.zoneimport);
    if (!div) return;
    div.parentElement.classList.toggle(css.showfull);
    const icon = e.currentTarget.querySelector('i');
    if (icon) {
      icon.classList.toggle(css.arrowout);
      icon.classList.toggle(css.arrowin);
    }
  }
}