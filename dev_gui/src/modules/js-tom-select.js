'use strict';
import tomSelectcss from "../css/tom-select.css";
import DOMPurify from 'dompurify';
import TomSelect from 'tom-select/dist/js/tom-select.base.min.js';
import TomSelect_remove_button from 'tom-select/dist/js/plugins/remove_button.js';
import TomSelect_clear_button from 'tom-select/dist/js/plugins/clear_button.js';
import TomSelect_caret_position from 'tom-select/dist/js/plugins/caret_position.js';
TomSelect.define('remove_button', TomSelect_remove_button);
TomSelect.define('clear_button', TomSelect_clear_button);
TomSelect.define('caret_position', TomSelect_caret_position);
import {
  fetchSettings
} from '../modules/utils.js';
import {
  models,
  domselectors,
  css,
} from '../modules/modules-config.js';
import {
  AlertBox
} from '../modules/alert-box.js';
let users_list = {};

function _get_label(el, labelfield, item = false) {
  if (!labelfield) return el.text;
  let label = [];
  if (Object.keys(el).indexOf(labelfield) >= 0) label.push(el[labelfield]);
  else if (labelfield.indexOf('+') > 0) {
    if (item === true) label.push(el[labelfield.split('+')[0]]);
    else labelfield.split('+').forEach(l => {
      if (l in el) label.push(el[l]);
    });
  }
  return label.join(` `);
}
// settings for autocomplete select component - users , instruments , taxons
function createJsTomSelect() {
  function applyTo(item, settings = {}, siblings = null) {
    const id = item.getAttribute('id');
    const multiple = item.hasAttribute('multiple');
    const type = item.dataset.type;
    let option = {
        url: '',
        settings: settings
      },
      init_canceltag = (tag) => {
        tag.addEventListener('click', (e) => {
          const v = e.currentTarget.closest(domselectors.component.tomselect.item).dataset.value;
          if (v) {
            e.stopImmediatePropagation();
            item.tomselect.removeItem(v);
          }
        })
      }
    if (item.dataset.create && item.dataset.create === 'true') {
      //  option.settings.create = true;
      //  option.settings.createOnBlur = true;
      option.settings.create = true;
      option.settings.addPrecedence = true;
    }
    if (item.dataset.empty && item.dataset.empty === 'true') {
      option.settings.allowEmptyOption = true;
    }
    if (item.dataset.maxitems) {
      option.settings.maxItems = parseInt(item.dataset.maxitems);
    }
    if (item.dataset.addoption) {
      option.settings.addoption = item.dataset.addoption.split(',');
    };

    switch (type) {
      case models.project:
        // for top navigation search and collections
        const maxitems = (multiple) ? null : 1;
        option.url = "/gui/prjlist/";
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            searchField: 'text',
            labelField: 'text',
            openOnFocus: false,
            maxItems: maxitems,
            allowEmptyOption: false,
          }
        };

        break;
      case models.organisation:
        option.url = "/api/organizations/search?name=";
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            searchField: 'text',
            labelField: 'text',
            openOnFocus: false,
            allowEmptyOption: false,
          }
        };

        break;
      case models.persons:
        option.url = "/api/users/search?all=y&by_name=";
      case models.user:
        option.url = "/api/users/search?by_name=";
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            searchField: 'name',
            labelField: 'name+email',
            onInitialize: function() {
              if (item.currentlist) users_list = item.currentlist;
              else item.tomselect.items.forEach(e => {
                if (e !== '' && parseInt(e) > 0) users_list[e] = true;
              });
            },
            onItemAdd: function(e) {
              if (e === "") return;
              if (users_list[e]) {
                //  if (multiple || !this.revertSettings || this.revertSettings.tabIndex < 0 || !item.options.length) return;
                AlertBox.addMessage({
                  type: AlertBox.alertconfig.types.danger,
                  parent: item,
                  content: AlertBox.i18nmessages.exists
                });
                setTimeout(() => {
                  this.removeOption(e);
                  if (this.revertSettings.tabIndex < 0 || !item.options.length || !this.revertSettings) {
                    this.removeItem(e);
                    users_list[e] = true;
                  } else {
                    const revert = item.options[this.revertSettings.tabIndex].value;
                    this.addItem(revert);
                  }
                  AlertBox.addMessage({
                    type: AlertBox.alertconfig.types.danger,
                    parent: item,
                    content: AlertBox.i18nmessages.exists
                  });

                }, 2000);
              } else users_list[e] = true;
            },
            onItemRemove: function(e) {
              if (users_list[e]) delete users_list[e];
              if (multiple || !this.revertSettings || (this.revertSettings.innerHTML === '' && this.revertSettings.tabIndex === 0) || this.revertSettings.tabIndex < 0) return;
              const revert = item.options[this.revertSettings.tabIndex].value;
              if (users_list[revert] !== undefined) delete users_list[revert];

            }
          }
        };
        break;
      case models.instr:
        option.url = "/search/instruments";
        option.settings = {
          valueField: 'id',
          labelField: 'text',
          searchField: 'id',
          maxItems: 1,
          preload: true
        };
        break;
      case models.taxo:
        TomSelect.define('no_close', () => {
          this.close = () => {};
        });

        option.url = "/search/taxo";
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            labelField: 'text',
            searchField: 'text',
            closeAfterSelect: true,
            onInitialize: () => {
              const wrapper = document.getElementById(id).nextElementSibling;
              if (!wrapper.classList.contains('ts-wrapper')) return;
              const tags = wrapper.querySelectorAll(domselectors.component.tomselect.tsdelet);
              tags.forEach(tag => {
                init_canceltag(tag);
              })
            }

          }
        }

        break;
    }
    const default_settings = {
      create: false,
      minOptions: 0,
      maxOptions: null,
      preload: false,
      hideSelected: true,
      duplicates: false,
      allowEmptyOption: true,
      closeAfterSelect: true,
      placeholder: (item.placeholder) ? item.placeholder : ((item.dataset.placeholder) ? item.dataset.placeholder : ''),
      onDropdownClose: function() {

      },
      shouldLoad: function(query) {
        return query.length > 2
      },
      onItemRemove: function() {
        return true;
      },
      load: function(query, callback) {
        query = DOMPurify.sanitize(query);

        const self = this;
        if (self.loading > 10) {

          callback();
          return;
        }
        let url = '';
        switch (type) {
          case models.user:
          case models.organisation:
            url = option.url + encodeURIComponent('%' + query + '%');
            break;
          case models.instr:
          case models.taxo:
            url = option.url;
            //

            if (query.indexOf('_') == 0 && option.settings.addoption && query == option.settings.addoption[0]) {
              url = null;
              return callback(Object.entries([{
                text: option.settings.addoption[0],
                id: option.settings.addoption[1]
              }]));
            }
            //
            if (query) url += '?q=' + encodeURIComponent(query);

            break;
          case models.project:
            url = option.url;

            if (query) url += '?filt_title=' + encodeURIComponent(query); //+ '&filt_instrum=' + encodeURIComponent(query);
            break;
        }
        if (url !== null) fetch(url, fetchSettings()).then(response => response.json()).then(json => {
          if (type === models.project) {

            if (json.data && json.data.length) json = json.data.map(row => {
              return {
                id: row[1],
                text: row[3][0],
                rights: row[0]
              }

            });
          } else if ([models.instr, models.organisation].indexOf(type) >= 0 && json.length) json = json.reduce((result, a, v) => {
            a = DOMPurify.sanitize(a);
            let obj = {
              id: a,
              text: a
            }
            result.push(obj);

            return result;
          }, []);

          if (json.length && typeof json == 'object') json = Object.entries(json);
          return callback(json);

        }).catch(err => {
          console.log('tomselect-err', err);
        });
      },

      render: {
        option: function(el, escape) {
          if (el === undefined || el === null) return ``;
          // add optgroup
          const optgroup = (el.hasOwnProperty('optgroup')) ? `data-optgroup=${el.optgroup}` : ``;
          const label = _get_label(el, option.settings.labelField);
          return `<div class="py-2 flex  ${ ((multiple)?'inline-flex':'') } " ${optgroup} data-value="${el[option.settings.valueField]}">${ escape(label) }</div>`;
        },
        item: function(el, escape) {
          if (el === undefined || el === null) return ``; // add optgroup
          const optgroup = (el.optgroup) ? `item-${el.optgroup}` : ``;
          const inlist = (users_list[el[this.settings.valueField]]) ? `data-inlist` : ``;
          // add cancel icon for multiple selections
          //  const cancel = ((multiple) ? `<i class="${domselectors.component.tomselect.tsdelet.substr(1)}"></i>` : ``);
          // use ts plugin remove_button
          const cancel = ``;
          const label = _get_label(el, option.settings.labelField, true);
          return DOMPurify.sanitize(`<div class="${((multiple) ? `flex inline-flex ` : ``) } ${optgroup}"  data-value="${el[this.settings.valueField]}"  ${inlist}>${ escape(label) } ${ cancel }</div>`);
        },
        no_results: function(data, escape) {
          return DOMPurify.sanitize('<div class="no-results">' + ((item.dataset.noresults) ? item.dataset.noresults : 'No result found for ') + escape(data.input) + '</div>');
        },

      }
    }
    if (item.getAttribute('readonly') === null) {
      option.settings.plugins = {
        'clear_button': {
          title: (item.dataset.clear) ? item.dataset.clear : 'Clear all',
          html: (data) => {
            return `<div class="${data.className}" id="clear-${id}" title="${data.title}"><i class="icon ${(multiple)?``:'p-[0.125rem]'} icon-x-circle-sm ${(multiple)?``:` opacity-50`}"></i></div>`;
          }
        }
      }
      option.settings.onClear = function() {
        item.tomselect.clear();
        return true;
      }
      if (multiple) {
        option.settings.plugins = { ...option.settings.plugins,
          ...{
            'remove_button': {}
          }

        };
        option.settings.plugins = { ...option.settings.plugins,
          ...{
            'caret_position': {}
          }

        };
      }
    }
    option.settings = Object.assign(default_settings, option.settings)
    if (id !== null) {
      const ts = new TomSelect('#' + id, option.settings);
      ts.wrapper.classList.remove(domselectors.component.tomselect.ident);
      ts.wrapper.classList.remove('js');
      // add
      ts.wrapper.setAttribute('data-component', 'tom-select');
      if (item.getAttribute('readonly') !== null) {
        ts.disable();
      }
      switch (type) {
        case models.taxo:
          ts.on('item_add', (v, el) => {
            if (el !== null) el.classList.add('new');
          });
          //
          break;
        case models.project:
          // add data-noaction just to select a project
          if (item.dataset.dest) {
            ts.on('item_add', (v, el) => {
              if (v != item.dataset.value && ts.options[v] && !el.querySelector('a')) {
                const links = {
                  "A": "/prj/",
                  "V": "/prj/",
                  "M": "/gui/prj/edit/"
                };
                const rights = ts.options[v].rights;
                const keys = Object.keys(rights);
                if (keys) {
                  if (keys.length > 1) {
                    Object.entries(rights).forEach(([k, r]) => {
                      el.insertAdjacentHTML('beforeend', ` <a data-k="${k}" class="small-caps font-normal ml-2">${r}</a>`);
                    });
                    el.querySelectorAll('a').forEach(lk => {
                      lk.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        window.open(links[e.target.dataset.k] + v, `_proj${v}`).focus();
                        ts.removeItem(v);
                      });
                    })
                  } else {
                    window.open(links[keys[0]] + v, `_proj${v}`).focus();
                    ts.removeItem(v);
                  }
                }
              }
            });
          }
          break;
      }
      return ts;
    } else console.log('noid');

  }

  function getUserList() {
    return users_list;
  }
  return {
    applyTo
  }
}
const JsTomSelect = createJsTomSelect();
export {
  JsTomSelect
}