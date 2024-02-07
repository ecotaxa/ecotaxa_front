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
        selector: 'data-id',

      };
      this.selector = (selector) ? selector : options.selector;
      this.importcontainer = options.importcontainer instanceof HTMLElement ? options.importcontainer : document.querySelector(options.importcontainer);
      this.form = (options.form) ? ((options.form) instanceof HTMLElement ? options.form : document.querySelector(options.form)) : this.dom.closest('form');
      this.button = options.button instanceof HTMLElement ? options.button : document.querySelector(options.button);
      this.replacebutton = options.replacebutton instanceof HTMLElement ? options.replacebutton : document.querySelector(options.replacebutton);
      this.tabbutton = options.tabbutton instanceof HTMLElement ? options.tabbutton : document.querySelector(options.tabbutton);
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
      if (projid) projid.classList.add(css.hide);

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
          const target = e.currentTarget;
          target.disabled = true;
          this.toImport(target.parentElement, index);
        };
        selector.removeEventListener(evt, apply_selection, false);
        selector.addEventListener(evt, apply_selection, false);
      };
    });
    if (this.button) {
      this.tabbutton.addEventListener('click', (e) => {
        this.resizeZone(e);
      });
      this.showImport(false);
    }
  }
  columnProperty(name, index, th) {
    if (this.tbl) return (this.tbl.grid.columns[index].hasOwnProperty(name)) ? this.tbl.grid.columns[index][name] : null;
    else return (th.dataset[name]) ? th.dataset.name : null;
  }
  columnIndex(prop, value) {
    if (this.tbl) return this.tbl.grid.columns.findIndex(column => (column.hasOwnProperty(prop) && column[prop] === value));
    else return Array.from(this.dom.querySelectorAll('thead th')).findIndex(th => (th.dataset[prop] && th.dataset[prop] === value));
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
    if (what === typeimport.settings) this.imports[models.contact] = this.findContact(thcells, datas[rowindex]);
    const importzone = (what === typeimport.taxo || what === typeimport.privileges) ? this.createImportzone(what) : null;

    let ts = null;
    selectcells.forEach((name, index) => {
      index = this.columnIndex('name', name);
      if (index >= 0) {
        // show import buttons if importzone
        const cell = trs[rowindex].cells[index];
        const celldata = datas[rowindex][index];
        cell.classList.add(css.selected);
        const thcell = thcells[index];
        switch (what) {
          case typeimport.taxo:
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
                  if (!importzone.querySelector('option[value="' + key + '"]')) importzone.insertAdjacentHTML('beforeend', '<option value="' + key + '" selected>' + text + '</option>');
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

            if (!importzone.dataset.init) {
              /*    const optgroups = [];
                  Object.keys(privs).forEach(priv => {
                    //  importzone.insertAdjacentHTML('afterbegin', `<optgroup value="${priv}" label="${priv}"></optgroup>`);
                    optgroups.push({
                      value: priv,
                      label: priv
                    });
                  });*/
              const jsTomSelect = new JsTomSelect();
              jsTomSelect.applyTo(importzone);
              importzone.dataset.init = true;
            }
            ts = importzone.tomselect;

            Object.entries(privs).forEach(([priv, members]) => {
              members.sort((a, b) => {
                return (b.name > a.name);
              });
              members.forEach(member => {
                const newpriv = (resetpriv) ? key_privileges.viewers : priv; // viewer if more than one project imported
                let opt;

                if (ts) {
                  opt = ts.items.indexOf(member.id);
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
                    opt = document.createElement('option');
                    opt.value = member.id;
                    opt.dataset.optgroup = newpriv;
                    opt.selected = opt.defaultSelected = true;
                    opt.text = member.name;
                    importzone.add(opt);

                  } else opt.dataset.optgroup = newpriv;
                }
              });
              importzone.tomselect.refreshOptions();
            });

            showbtns = (((ts) ? ts.items.length : importzone.selectedIndex + 1) > 0);


            break;
          default:

            if (thcell.dataset.autocomplete) {
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
            } else if (thcell.dataset.value) this.imports[name] = thcell.dataset.value;
            else this.imports[name] = celldata;

            break;
        }
      };
    });

    if (thcells.length) {
      if (this.button) {
        this.showImport(showbtns);
        if (!this.button.dataset.activated && (what === typeimport.taxo || what === typeimport.privileges)) this.activateButtons(what, selectcells);
      } else this.makeImport(null, selectcells, what, true);
      this.resetSelectors();
    }
    //

  }
  messageZone(item) {
    console.log('itemmessage', item);
  }
  activateButtons(what, selectcells) {

    this.button.addEventListener('click', (e) => {
      e.preventDefault();
      this.makeImport(e.currentTarget, selectcells, what, true);

    });
    this.replacebutton.addEventListener('click', (e) => {
      e.preventDefault();
      this.makeImport(e.currentTarget, selectcells, what, true);

    });

    this.button.dataset.activated = true;
    this.replacebutton.dataset.activated = true;
  }

  findContact(thcells, tds) {
    let contact = null;
    thcells.every((t, idx) => {
      if (t.dataset.name && t.dataset.name === models.contact) {
        contact = idx;
        return false;
      }
      return true;
    });
    if (contact) contact = tds[contact] ? tds[contact] : 0;

    return contact;
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
    const projectPrivileges = new ProjectPrivileges();
    const importedtag = (input) => {
      this.setImportedTag(input, null);
    }
    const dismiss = () => {
      this.dismiss();
    }
    const contact = ((this.imports[models.contact]) ? this.imports[models.contact] : null);
    return (projectPrivileges.importPrivileges(privileges, clear, contact, importedtag, dismiss));
  }
  resetSelectors() {
    this.selectors.forEach((selector, i) => {
      if (selector.disabled) {
        selector.disabled = false;
        const trs = Array.from(this.dom.querySelectorAll('tbody tr'));
        trs[i].querySelectorAll('.' + css.selected).forEach(el => {
          el.classList.remove(css.selected);
        });
      }
    });
  }
  activateClear() {
    const clearbutton = document.getElementById('clear-' + this.importid);
    if (!clearbutton) return;
    clearbutton.addEventListener('click', (e) => {
      if (!this.importcontainer) return;
      this.resetSelectors();
      this.button.disabled = false;
      this.replacebutton.disabled = false;
      this.showImport(false);
    });
  }
  createImportzone(name) {
    this.showImport(true);
    let importzone = this.importcontainer.querySelector('#' + this.importid);


    if (name === typeimport.privileges) {
      if (!importzone) {
        importzone = document.createElement('select');
        this.importid = importzone.id = this.importid + '-' + name;
        importzone.dataset.type = models.user;
        importzone.multiple = true;
        importzone.dataset.priv = true;
        this.importcontainer.append(importzone);

      }
    } else {
      const import_target = (this.form.querySelector('[name="' + name + '"]')) ? this.form.querySelector('[name="' + name + '"]') : this.form.querySelector('[data-importfield="' + name + '"]');
      const ts = import_target.tomselect;

      if (!importzone) {
        if (!import_target) return;
        this.importzoneid = import_target.id;
        // tomselect ?
        importzone = import_target.cloneNode();
        importzone.classList.remove('tomselected');
        importzone.classList.remove('ts-hidden-accessible');
        // keep original id to replace data on apply import
        importzone.dataset.origin = importzone.id;
        importzone.id = this.importid;
        importzone.name = this.importid + '_' + importzone.name;
        this.importcontainer.insertAdjacentHTML('afterbegin', importzone.outerHTML);
        if (ts) {
          importzone = this.importcontainer.querySelector('#' + this.importid);
          const jsTomSelect = new JsTomSelect();
          jsTomSelect.applyTo(importzone);

        }
        this.activateClear();

      }
    }

    return importzone;

  }

  makeImport(btn, selectcells, what, close = false) {
    let done = false,
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

        break;
      default:
        selectcells.forEach((name, index) => {
          let input = ((this.form.querySelector('[data-importfield="' + name + '"]')) ? this.form.querySelector('[data-importfield="' + name + '"]') : this.form.querySelector('[name="' + name + '"]'));

          if (input && this.imports[name] !== undefined) {
            ts = input.tomselect;

            if (name === 'init_classif_list') {
              let ids = this.imports[name];
              if (Array.isArray(ids)) ids = ids.join(',');
              else ids = ids.replace('[', '').replace(']', '').replaceAll(' ', '');
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
                  if (ts) {
                    Object.entries(results).forEach(([key, text]) => {
                      let el = {};
                      key = DOMPurify.sanitize(key);
                      text = DOMPurify.sanitize(text);
                      el[ts.settings.valueField] = key;
                      el[ts.settings.searchField] = unescape_html(text);

                      ts.addOption(el);
                      ts.addItem(el[ts.settings.valueField]);
                    });
                  } else {
                    let options = '';
                    Object.entries(results).forEach(([key, text]) => {
                      key = DOMPurify.sanitize(key);
                      text = DOMPurify.sanitize(text);
                      options += '<option value ="' + key + '" selected>' + text + '</option>';
                    });
                    input.innerHTML = options;
                    options = '';
                  }
                  results = null;
                  if (ts) ts.wrapper.classList.remove('wait-for-results');
                });
              }
            } else if (ts) {
              let el = {};
              if (typeof(this.imports[name]) == 'string') {
                el[ts.settings.labelField] = this.imports[name];
                el[ts.settings.valueField] = this.imports[name];
                el[ts.settings.searchField] = unescape_html(this.imports[name]);
              } else {
                el[ts.settings.labelField] = this.imports[name]['key'];
                el[ts.settings.valueField] = this.imports[name]['key'];
                el[ts.settings.searchField] = unescape_html(this.imports[name]['value']);
              }
              ts.addOption(el);
              ts.addItem(el[input.tomselect.settings.valueField]);
              //  ts.refreshOptions();
            } else {
              const type = (input.type) ? input.type : input.tagName.toLowerCase();
              switch (input.type) {
                case 'radio':
                case 'checkbox':
                  input = this.form.querySelector('[name="' + name + '"][value="' + this.imports[name] + '"]');
                  if (input) input.checked = true;
                  break;
                  /*case 'checkbox':
                    // TODO ( multiple selection )
                    this.form.querySelectorAll('[name="' + field + '"]').forEach(input => {
                      input.checked = (this.imports[name]['key'] === input.value);
                    });
                    break;*/
                case 'select':
                  // todo select multiple
                  let option;
                  if (this.imports[name]['key']) option = '<option value="' + this.imports[name]['key'] + '" selected >' + this.imports[name]['value'] + '</option>';
                  else option = '<option value="' + this.imports[name] + '" selected >' + this.imports[name] + '</option>'
                  input.insertAdjacentHTML('beforeend', option);
                  break;
                default:

                  input.value = this.imports[name];
                  break;
              }
            }
            if (what !== typeimport.settings) input.focus();
            done = true;
            // set imported tag to fieldbox
            this.setImportedTag(input);
          } else if (name === typeimport.privileges) {
            const clearprivileges = (what === typeimport.settings);
            done = this.importPrivileges(this.imports[name], clearprivileges);
          }
        });
        break;
    }
    if (done === true && close == true) this.dismiss();
  }

  setImportedTag(input, selector = '.form-box') {
    let el = (selector === null) ? input : (input.closest(selector) ? input.closest(selector) : input.closest('fieldset'));
    if (!el) return;
    el.dataset.isimported = this.form.dataset.isimported;
    el.classList.add('imported');
    const removetag = (e) => {
      el.removeAttribute('data-isimported');
      el.classList.remove('imported');
      input.removeEventListener('change keydown', removetag);
    }
    input.addEventListener('change keydown', removetag);
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
  // show / hide importzone and buttons
  showImport(show) {
    if (!this.button) return;

    if (show === false) {
      this.button.classList.add(css.hide);
      this.replacebutton.classList.add(css.hide);
      this.importcontainer.classList.add(css.hide);
      this.tabbutton.classList.add(css.hide);

    } else {
      this.button.classList.remove(css.hide);
      this.replacebutton.classList.remove(css.hide);

      this.importcontainer.classList.remove(css.hide);
      this.button.disabled = false;
      const importzone = this.importcontainer.querySelector('#' + this.importid);
      if (importzone) {
        this.tabbutton.classList.remove(css.hide);
        if (importzone.tomselect && importzone.tomselect.control.offsetHeight < importzone.tomselect.control.scrollHeight) {
          this.tabbutton.disabled = false;
        } else this.tabbutton.disabled = true;
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
      icon.classList.toggle('icon-arrow-pointing-out');
      icon.classList.toggle('icon-arrow-pointing-in');
    }
  }
}