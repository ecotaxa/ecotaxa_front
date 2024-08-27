import DOMPurify from 'dompurify';
import {
  JsTomSelect
} from "../modules/module-tom-select.js";
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
  importzoneid;
  importid = 'importzone';
  selectors;
  button;
  clearbutton;
  replacebutton;
  tabbutton;
  tbl = null;
  constructor(tbl, what = null, selector = null) {
    if (!tbl) return;
    // tbl is a TableComponent  ?
    this.tbl = (typeof(tbl) === 'object') ? tbl : null;
    selector = (selector === null) ? ((this.tbl.cellidname) ? "data-" + this.tbl.cellidname : "data-id") : selector;
    // get the table from table component or html table element id
    this.dom = (this.tbl) ? this.tbl.dom : document.getElementById(tbl);
    if (!this.dom) return;
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
      if (indextocheck && selector.closest('tr').children[indextocheck[index]].innerHTML === '') selector.disabled = true;
      else {
        const evt = (selector.tagName.toLowerCase() === 'input') ? 'change' : 'click';
        const apply_selection = (e) => {
          e.preventDefault();
          e.stopImmediatePropagation();
          const target = e.currentTarget;
          target.disabled = true;
          this.toImport(target.parentElement, index);
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
  columnProperty(name, index, th) {
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
  rowIndex(td, trs) {
    const ref = (td.parentElement) ? td.parentElement : null;
    if (!ref) return null;
    return trs.findIndex(tr => (tr === ref));
  }
  toImport(td, whatpart = 0) {
    const grid = (this.tbl) ? this.tbl.grid : null;
    const thcells = Array.from(this.dom.querySelectorAll('thead th'));
    const trs = Array.from(this.dom.querySelectorAll('tbody tr'));
    const datas = (grid) ? grid.data : trs.map(tr => {
      return Array.from(tr.childNodes).forEach(cell => {
        return cell.innerText;
      });
    }); // cell values in json  - no parse
    if (td.tagName.toLowerCase() !== 'td') td = td.closest('td');
    const rowindex = this.rowIndex(td, trs);
    if (rowindex === null) return;
    let showbtns = true;
    const cellindex = td.cellIndex;
    const th = thcells[cellindex];
    const tds = trs[rowindex];
    const what = this.columnProperty('what', cellindex, th);
    if (!what) return;
    const parts = this.columnProperty('parts', cellindex, th);
    let contact = null;
    let selectcells = this.columnProperty('selectcells', cellindex, th);
    selectcells = (selectcells) ? ((parts) ? [parts[whatpart]] : selectcells) : null;
    if (!selectcells) return;
    if (what === typeimport.settings || what === typeimport.privileges) this.imports[models.contact] = this.findContact(datas[rowindex]);
    const importzone = (what === typeimport.taxo || what === typeimport.privileges) ? this.createImportzone(what) : null;

    this.addResetButton();
    let ts = null;
    selectcells.forEach((name, index) => {
      index = this.gridColumnIndex('name', name);
      if (index >= 0) {
        const tdindex = this.columnIndex('name', name);
        // show import buttons if importzone
        const cell = (tdindex >= 0) ? trs[rowindex].cells[tdindex] : null;
        if (cell) cell.classList.add(css.selected);
        const celldata = datas[rowindex][index];
        const thcell = (tdindex >= 0) ? thcells[tdindex] : null;
        switch (what) {
          case typeimport.taxo:
            if (!importzone) return;
            // accumulate and show in import win - move the form field in modal win to view the changes and benefit of tom-select component functs...
            ts = importzone.tomselect;
            let taxons = celldata;
            if (taxons) {
              if (ts) {
                // merge taxons and options - unique
                Object.values(ts.options).forEach((opt) => {
                  let obj = {};
                  obj[opt[ts.settings.valueField]] = opt[ts.settings.labelField];
                  if (!taxons[opt[ts.settings.valueField]]) taxons = Object.assign(taxons, obj);
                });
                taxons = Object.entries(taxons);
                // sort taxons
                taxons.sort((a, b) => {
                  let x = a[1];
                  let y = b[1];
                  return +(x > y) || -(y > x);
                });
                ts.clear();
                ts.clearOptions();
                // add taxons items
                taxons.forEach(([key, text]) => {
                  if (!ts.getItem(key)) {
                    if (!ts.getOption(key)) {
                      let obj = {};
                      obj[ts.settings.valueField] = key;
                      obj[ts.settings.labelField] = unescape_html(text.trim());
                      ts.addOption(obj);
                    }
                    ts.addItem(key);
                  }
                });
              } else {
                Object.values(importzone.options).forEach(opt => {
                  let obj = {};
                  obj[opt.value] = opt.text;
                  if (!taxons[opt.value]) taxons = Object.assign(taxons, obj);
                });
                taxons = Object.entries(taxons);
                taxons.sort((a, b) => {
                  let x = a[1];
                  let y = b[1];
                  return +(x > y) || -(y > x);
                });
                importzone.innerHTML = ``;
                taxons.forEach(([key, text]) => {
                  if (!importzone.querySelector('option[value="' + key + '"]')) {
                    const o = create_box('option', {
                      value: key,
                      selected: 'selected',
                      text: text
                    }, importzone);
                  }
                });
              }
              showbtns = (taxons.length > 0);
              taxons = null;
            }

            break;
          case typeimport.privileges:
            const privs = celldata;
            // set everybody to 'view' if more than one project imported
            const resetpriv = ((ts && ts.items.length > 0) || (importzone.selectedIndex > 0));
            if (!importzone.tomselect) {
              importzone.currentlist = {};
              const jsTomSelect = JsTomSelect();
              jsTomSelect.applyTo(importzone);
            }
            ts = importzone.tomselect;
            Object.entries(privs).forEach(([priv, members]) => {
              members.sort((a, b) => {
                return (b.name > a.name);
              });
              members.forEach(member => {
                const newpriv = (resetpriv) ? key_privileges.viewers : priv; // viewer if more than one project imported
                let opt;
                if (!importzone.currentlist || !importzone.currentlist[member.id]) {
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
                    opt = importzone.querySelector('option[value="' + member.id + '"]');
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
                      /*  opt = document.createElement('option');
                        opt.value = member.id;
                        opt.dataset.optgroup = newpriv;
                        opt.selected = opt.defaultSelected = true;
                        opt.text = member.name;*/
                      importzone.add(opt);
                    } else opt.dataset.optgroup = newpriv;
                  }
                }
              });
              if (ts) ts.refreshOptions(true);
            });

            showbtns = (((ts) ? ts.items.length : importzone.selectedIndex + 1) > 0);


            break;
          default:
            this.imports[name] = celldata;
            if (cell !== null) {
              if (cell.dataset.autocomplete) {
                // select elements where key / value in different columns
                this.imports[name] = {
                  value: celldata,
                  key: null
                };
                let el = null;
                thcells.every((t, idx) => {
                  if (t.dataset.name == thcell.dataset.autocomplete) {
                    el = idx;
                    return false;
                  }
                  return true;
                });
                if (el !== null) {
                  el = datas[rowindex][el];

                  this.imports[name].key = el;
                }
              } else if (cell.dataset.value) this.imports[name] = cell.dataset.value;

            }

            break;
        }
      };
    });

    if (thcells.length) {
      if (this.button) {
        const activate = (!this.button.dataset.activated && (what === typeimport.taxo || what === typeimport.privileges));
        this.showImport(showbtns);
        if (activate) this.activateButtons(what, selectcells);
      } else this.makeImport(null, selectcells, what, true);
    }
    //

  }
  messageZone(item) {
    console.log('itemmessage', item);
  }
  activateButtons(what, selectcells) {

    this.button.addEventListener('click', (e) => {
      e.stopImmediatePropagation();
      e.preventDefault();
      this.makeImport(e.currentTarget, selectcells, what, true);

    });
    this.replacebutton.addEventListener('click', (e) => {
      e.stopImmediatePropagation();
      e.preventDefault();
      this.makeImport(e.currentTarget, selectcells, what, true);

    });

    this.button.dataset.activated = true;
    this.replacebutton.dataset.activated = true;
  }

  findContact(tds, name = 'contact') {
    const index = this.gridColumnIndex('name', name);
    if (index >= 0) return tds[index] ? tds[index] : null;

    return null;
  }

  renderPrivileges(importzone, replace = false) {
    let privileges = {};
    const tzone = importzone.tomselect;

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
      importzone.options.forEach(member => {
        if (member.selected) pushpriv(member, member.dataset.optgroup);
      })
    }

    if (this.importPrivileges(privileges, replace)) {
      if (tzone) {
        tzone.clear();
        tzone.clearOptions();
      } else importzone.innerHTML = ``;

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

  resetSelectors() {
    this.selectors.forEach((selector, i) => {
      if (selector.disabled) selector.disabled = false;
    });
    this.dom.querySelectorAll('td.' + css.selected).forEach(td => {
      td.classList.remove(css.selected);
    });
  }

  activateClear() {
    const clearbutton = document.getElementById('clear-' + this.importid);
    if (!clearbutton) return;
    clearbutton.addEventListener('click', (e) => {
      e.stopImmediatePropagation();
      e.preventDefault();
      if (!this.importcontainer) return;
      this.resetSelectors();
      this.button.disabled = false;
      this.replacebutton.disabled = false;
      this.showImport(false);
    });
  }
  createImportzone(name) {
    let importzone = this.showImport(true),
      ts = false;
    if (!importzone) {
      if (name === typeimport.privileges) {
        importzone = create_box('select', {
          id: this.importid,
          dataset: {
            type: models.user,
            priv: true,
          },
          multiple: true
        }, this.importcontainer);
        importzone = document.getElementById(this.importid);
        ts = true;
      } else {
        const import_target = (this.form.querySelector('[name="' + name + '"]')) ? this.form.querySelector('[name="' + name + '"]') : this.form.querySelector('[data-importfield="' + name + '"]');
        if (!import_target) return;
        ts = import_target.tomselect;
        this.importzoneid = import_target.id;
        // tomselect ?
        importzone = import_target.cloneNode();
        importzone.classList.remove(css.tomselected);
        importzone.classList.remove(css.hiddenaccessible);
        // keep original id to replace data on apply import
        importzone.dataset.origin = importzone.id;
        importzone.id = this.importid;
        importzone.name = this.importid + '_' + importzone.name;
        this.importcontainer.prepend(importzone);
        if (ts) {
          const jsTomSelect = JsTomSelect();
          jsTomSelect.applyTo(importzone);
        }
        this.activateClear();
      }

    }
    return importzone;

  }

  makeImport(btn, selectcells, what, close = false) {
    let done = true,
      ts = null;
    const importzone = (this.importcontainer) ? this.importcontainer.querySelector('#' + this.importid) : null;

    switch (what) {
      case typeimport.taxo:

        if (!importzone) return false;
        const import_target = this.form.querySelector('#' + importzone.dataset.origin);

        if (!import_target) return false;
        ts = import_target.tomselect;
        if (ts) {
          // only if replace specified
          if (btn.dataset.replace && btn.dataset.replace === 'replace') {
            ts.clear();
            ts.clearOptions();
          }
          const tzone = importzone.tomselect;
          const items = [...tzone.items];
          const options = Object.assign({}, tzone.options);
          items.forEach((e, i) => {
            let el = {};
            el[ts.settings.valueField] = e;
            el[ts.settings.searchField] = unescape_html(options[e][ts.settings.searchField]);
            if (!ts.getOption(e)) ts.addOption(el);
            ts.addItem(e);
          });
          tzone.clear();
          tzone.clearOptions();
        } else {
          if (btn.dataset.replace && btn.dataset.replace === 'replace') import_target.innerHTML = ``;
          import_target.innerHTML = DOMPurify.sanitize(importzone.innerHTML);
          importzone.innerHTML = ``;
        }
        done = true;
        break;
      case typeimport.privileges:
        if (!importzone) return false;
        done = this.renderPrivileges(importzone, (btn.dataset.replace && btn.dataset.replace === 'replace'));
        if (importzone.currentlist) importzone.currentlist = {};
        break;
      default:
        const ts_add_select_item = function(ts, data) {
          const el = {};
          if (typeof(data) == 'string') {
            el[ts.settings.labelField] = data;
            el[ts.settings.valueField] = data;
            el[ts.settings.searchField] = unescape_html(data);
          } else {
            el[ts.settings.labelField] = data.key;
            el[ts.settings.valueField] = data.key;
            el[ts.settings.searchField] = unescape_html(data.value);
          }
          if (!ts.getOption(el[ts.settings.valueField])) ts.addOption(el);
          if (!ts.getItem(el[ts.settings.valueField])) ts.addItem(el[ts.settings.valueField]);
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
            if (name === 'init_classif_list') {
              let ids = this.imports[name];
              if (Array.isArray(ids)) ids = ids.join(',');
              else ids = ids.replace('[', '').replace(']', '').replaceAll(' ', '');
              if (ts) {
                ts.wrapper.classList.add('wait-for-results');
                ts.clear(false);
                ts.clearOptions();
              }
              if (ids !== '') {
                if (ts) ts.wrapper.classList.add('wait-for-results');
                const formData = new FormData();
                formData.append('idlist', ids);
                const url = '/search/taxoresolve' //+ new URLSearchParams({'idlist': ids});
                fetch(url, fetchSettings({
                  'method': 'POST',
                  'body': formData
                })).then(response =>
                  response.json()
                ).then(results => {
                  const ts = input.tomselect;
                  if (ts) {

                    Object.entries(results).forEach(([key, text]) => {
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
              ts_add_select_item(ts, this.imports[name]);
              this.setImportedTag(input);
            } else {
              switch (type) {
                case 'radio':
                case 'checkbox':
                  input = this.form.querySelector('[name="' + name + '"][value="' + this.imports[name] + '"]');
                  if (input) input.checked = true;
                  break;
                case 'select':
                  if (input.multiple) this.imports[name].forEach(data => {
                    add_select_option(input, data)
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
            // set imported tag to fieldbox


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
    let el = (selector === null) ? input : (input.closest(selector) ? input.closest(selector) : input.closest('fieldset'));
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
      /*  resetbtn = document.createElement('a');
        resetbtn.classList.add(domselectors.resetbutton.substr(1));
        resetbtn.textContent = this.tbl.params.reset;
        this.dom.parentElement.firstChild.prepend(resetbtn);*/
    }
    resetbtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopImmediatePropagation();
      const selectors = this.selectors = this.dom.querySelectorAll('[' + this.selector + '] button:disabled, [' + this.selector + '] input:disabled');
      selectors.forEach(selector => {
        selector.disabled = false;
        const sel = selector.closest('tr').querySelector('.' + css.selected);
        if (sel) sel.classList.remove(css.selected);
      });
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
      const importzone = this.importcontainer.querySelector('#' + this.importid);
      if (importzone) {
        //  const offseth = importzone.tomselect.control.offsetHeight;
        //  const scrollh = importzone.tomselect.control.scrollHeight;
        this.button.classList.remove(css.hide);
        this.replacebutton.classList.remove(css.hide);
        this.importcontainer.classList.remove(css.hide);
        this.button.disabled = false;
        if (this.tabbutton) {
          this.tabbutton.classList.remove(css.hide);
          if (importzone.tomselect) {
            this.tabbutton.disabled = false;
          } else this.tabbutton.disabled = true;
        }
      }
      return importzone;
    }
    return null;
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