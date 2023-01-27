import DOMPurify from 'dompurify';
import {
  ProjectPrivileges
} from "../modules/project-privileges.js";
import {
  JsTomSelect

} from "../modules/js-tom-select.js";
import {
  fetchSettings,
  unescape_html
} from '../modules/utils.js';
import {
  models,
  typeimport,
  css,
  defined_privileges
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
  doc = null;
  constructor(grid, what = '', selector = null) {
    if (!grid) return;
    grid = grid instanceof HTMLElement ? null : ((typeof(grid) === 'object') ? grid : null);
    const doc = grid instanceof HTMLElement ? grid : ((typeof(grid) === 'object') ? grid.table : document.querySelector(grid));
    what = DOMPurify.sanitize(what);
    if (!instance || instance.doc !== doc) {
      // defaultoptions - keep like that
      const options = {
        importcontainer: '#data-import-' + what,
        btns: '.btns-imports',
        button: '#add-import-' + what,
        replacebutton: '#replace-import-' + what,
        clearbutton: "#clear-import-" + what,
        selector: 'data-id',

      };
      this.doc = doc;
      this.selector = (selector) ? selector : options.selector;
      this.importcontainer = options.importcontainer instanceof HTMLElement ? options.importcontainer : document.querySelector(options.importcontainer);
      this.form = (options.form) ? ((options.form) instanceof HTMLElement ? options.form : document.querySelector(options.form)) : this.doc.closest('form');
      this.button = options.button instanceof HTMLElement ? options.button : document.querySelector(options.button);
      this.replacebutton = options.replacebutton instanceof HTMLElement ? options.replacebutton : document.querySelector(options.replacebutton);
      this.clearbutton = options.clearbutton instanceof HTMLElement ? options.clearbutton : document.querySelector(options.clearbutton);
      this.init(grid, options);
      instance = this;
    }
    return instance;
  }

  init(grid, options) {

    // hide importzone
    this.showImport(false);
    // remove line of target proj

    let projid = this.form.querySelector('#projid');
    if (projid && projid.value) {
      projid = this.doc.querySelector('[' + this.selector + '="' + projid.value + '"]');
      if (projid) projid.classList.add(css.hide);

    }
    this.selectors = this.doc.querySelectorAll('[' + this.selector + '] button, [' + this.selector + '] input');
    this.selectors.forEach(selector => {
      // checkbox possible
      const evt = (selector.tagName.toLowerCase() === 'input') ? 'change' : 'click';
      const apply_selection = (e) => {
        const target = e.currentTarget;
        const index = Array.from(target.parentElement.children).indexOf((target));
        target.disabled = true;
        this.toImport(grid, target.parentElement, index);
      };
      selector.removeEventListener(evt, apply_selection, false);
      selector.addEventListener(evt, apply_selection, false);
    });

    if (this.button) this.showImport(false);
  }

  toImport(grid, col, whatpart = 0) {
    const thcells = (grid === null) ? this.doc.querySelectorAll('thead th') : grid.headings;
    const rows = (grid === null) ? this.doc.querySelectorAll('tbody tr') : grid.data;
    const datajson = grid.options.data.data; // cell values in json  - no parse
    if (col.tagName.toLowerCase() !== 'td') col = col.closest('td');
    const rowindex = (col.closest('tr')) ? col.closest('tr').dataIndex : null;
    if (rowindex === null) return;
    let showbtns = true;
    const cellindex = col.cellIndex; // change cellIndex to TableColIndex if no table component
    const th = thcells[cellindex];
    const cols = rows[rowindex].cells;
    const what = th.dataset.what;
    if (!what) return;
    const parts = (th.dataset.parts) ? th.dataset.parts.split(',') : null;
    let contact = null;
    const selectcells = (th.dataset.selectcells) ? ((th.dataset.parts) ? [th.dataset.parts.split(',')[whatpart]] : th.dataset.selectcells.split(',')) : null;
    if (!selectcells) return;
    if (what === typeimport.settings) this.imports[models.contact] = this.findContact(thcells, datajson[rowindex]);
    const importzone = (what === typeimport.taxo || what === typeimport.privileges) ? this.createImportzone(what) : null;
    selectcells.forEach((name, index) => {
      index = null;
      thcells.every((t, idx) => {
        if (t.dataset.name === name) {
          index = idx;
          return false;
        }
        return true;
      });

      if (index !== null) {
        // show import buttons if importzone

        const cell = rows[rowindex].cells[index];
        const celldata = datajson[rowindex][index];
        cell.classList.add(css.selected);
        const thcell = thcells[index];
        switch (what) {
          case typeimport.taxo:
            // accumulate and show in import win - move the form field in modal win to view the changes and benefit of tom-select component functs...
            const ts = importzone.tomselect;
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
            const resetpriv = ((importzone.tomselect && importzone.tomselect.items.length > 0) || (importzone.selectedIndex > 0));

            if (!importzone.dataset.init) {
              Object.keys(privs).forEach(priv => {
                importzone.insertAdjacentHTML('afterbegin', `<optgroup value="${priv}" label="${priv}"></optgroup>`);
              });
              const jsTomSelect = new JsTomSelect();
              jsTomSelect.apply(importzone);
              importzone.dataset.init = true;
            }

            if (importzone.tomselect) {
              // add members grouped by priv
              const members = [...importzone.tomselect.items];
              members.forEach(member => {
                member = importzone.tomselect.options[member];
                if (member) {
                  const priv = (resetpriv) ? key_privileges.viewers : member.optgroup;

                  privs[priv].push({
                    id: member.id,
                    name: member.name
                  });
                } else this.messageZone(member);
              });

              importzone.tomselect.clear();
              importzone.tomselect.refreshOptions();

              Object.entries(privs).forEach(([priv, members]) => {
                members.sort((a, b) => {
                  return (b.name > a.name);
                });
                members.forEach(member => {
                  const newpriv = (resetpriv) ? key_privileges.viewers : priv; // viewer if more than one project imported
                  const optgroup = importzone.querySelector('[value="' + newpriv + '"]');
                  if (importzone.querySelector('option[value="' + member.id + '"]') === null) {
                    optgroup.insertAdjacentHTML('afterbegin', `<option value="${member.id}" data-optgroup=${newpriv} selected="selected">${member.name}</option>`);
                    if (importzone.tomselect && !importzone.tomselect.getOption(member.id)) {
                      importzone.tomselect.addOption({
                        id: member.id,
                        name: unescape_html(member.name),
                        optgroup: newpriv
                      });
                    }
                  }
                  importzone.tomselect.addItem(member.id);
                });

              });

              showbtns = (importzone.tomselect.items.length > 0);
            }
            /*else {
                                     importzone.options.forEach(option => {
                                       if (option.selected) {
                                         privs[item.optgroup].push({
                                           id: option.value,
                                           name: option.text,
                                           optgroup: option.dataset.optgroup
                                         });
                                         option.selected = false;
                                       }
                                     });

                                   }*/
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
                el = datajson[rowindex][el];

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
    this.clearbutton.addEventListener('click', (e) => {
      if (!this.importcontainer) return;
      const field = this.importcontainer.querySelector('#' + this.importid);
      if (field) {
        if (field.tomselect) {
          field.tomselect.clear();
          field.tomselect.refreshOptions();
        } else field.value = '';
      }
      this.selectors.forEach(selector => {
        if (selector.disabled) {
          selector.disabled = false;
          selector.closest('tr').querySelectorAll('.selected').forEach(el => {
            el.classList.remove(css.selected);
          });
        }
      });
      this.button.disabled = false;
      this.replacebutton.disabled = false;
      //this.showImport(false);
    });
    this.button.dataset.activated = true;
    this.replacebutton.dataset.activated = true;
  }

  findContact(thcells, cols) {
    let contact = null;
    thcells.every((t, idx) => {
      if (t.dataset.name && t.dataset.name === models.contact) {
        contact = idx;
        return false;
      }
      return true;
    });
    //if (contact) contact = cols[contact] ? JSON.parse(cols[contact].data.trim()) : 0;
    if (contact) contact = cols[contact] ? cols[contact] : 0;

    return contact;
  }

  renderPrivileges(importzone, clear = false) {
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

    if (this.importPrivileges(privileges, clear)) {
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
          jsTomSelect.apply(importzone);

        }
      }
    }
    return importzone;

  }

  makeImport(btn, selectcells, what, close = false) {
    let done = false;
    const importzone = (this.importcontainer) ? this.importcontainer.querySelector('#' + this.importid) : null;
    switch (what) {
      case typeimport.taxo:

        if (!importzone) return false;
        const import_target = this.form.querySelector('#' + importzone.dataset.origin);

        if (!import_target) return false;
        const ts = import_target.tomselect;
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
            const ts = input.tomselect;

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
              el[ts.settings.valueField] = this.imports[name]['key'];
              el[ts.settings.searchField] = unescape_html(this.imports[name]['value']);
              ts.addOption(el);
              ts.addItem(el[input.tomselect.settings.valueField]);
              ts.refreshOptions();
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
          } else if (name === 'privileges') {
            done = this.importPrivileges(this.imports[name], false);
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
    const container = this.doc.closest('details');
    if (container) {
      container.open = false;
      if (clear === true) container.querySelector(this.content_selector).innerHTML = ``;
    }

  }
  // show / hide importzone and buttons
  showImport(show) {
    if (!this.button) return;

    if (show === false) {
      this.button.classList.add(css.hide);
      this.replacebutton.classList.add(css.hide);
      this.clearbutton.classList.add(css.hide);
      this.importcontainer.classList.add(css.hide);
    } else {
      this.button.classList.remove(css.hide);
      this.replacebutton.classList.remove(css.hide);
      this.clearbutton.classList.remove(css.hide);
      this.importcontainer.classList.remove(css.hide);
      this.button.disabled = this.clearbutton.disabled = false;
    }
  }
  // htmlentities  for taxo tags - no usage
  htmlEntities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
}