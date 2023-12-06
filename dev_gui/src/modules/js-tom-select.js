import DOMPurify from 'dompurify';
import TomSelect from 'tom-select/dist/js/tom-select.base.min.js';
import TomSelect_remove_button from 'tom-select/dist/js/plugins/remove_button.js';
import TomSelect_clear_button from 'tom-select/dist/js/plugins/clear_button.js';
import TomSelect_caret_position from 'tom-select/dist/js/plugins/caret_position.js';
TomSelect.define('remove_button', TomSelect_remove_button);
TomSelect.define('clear_button', TomSelect_clear_button);
TomSelect.define('caret_position', TomSelect_caret_position);
import tomSelectcss from "../css/tom-select.css";
import {
  fetchSettings
} from '../modules/utils.js';
import {
  models,
  domselectors
} from '../modules/modules-config.js';
let users_list = {};

// settings for autocomplete select component - users , instruments , taxons
export class JsTomSelect {
  applyTo(item, settings = {}, siblings = null) {

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
      //    option.settings.createOnBlur = true;
      option.settings.create = true;
      option.settings.addPrecedence = true;

    }
    /*,
          on_clear = function() {

            if (item.tagName.toLowerCase() === 'select')
              item.querySelectorAll('option:checked').forEach(option => {
                option.removeAttribute('selected');
              });
            item.selectedIndex = -1;
            return true;
          }*/
    ;

    switch (type) {
      case models.project:
        option.url = "/gui/prjlist/";
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            searchField: 'text',
            labelField: 'text',
            openOnFocus: false,
            maxItems: 1,
            allowEmptyOption: false,
          }
        };
        if (!item.dataset.noaction) option.settings.onItemAdd = function(e) {
          if (e != item.dataset.value) {
            let href = window.location.href.split('?');
            if (href.length > 1) {
              href[1] = href[1].split("=");
              href[1][1] = e;
              href[1] = href[1].join("=");
              href = href.join("?");
            } else {
              href = window.location.href.split('/');
              href.pop();
              href = href.join('/') + '/' + e;
            }
            window.open(href, '_blank').focus();
          }
          this.removeItem(e);
          return;
        }

        break;

      case models.user:
        option.url = "/api/users/search?by_name=";
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            searchField: 'name',
            labelField: 'name',
            onInitialize: function() {
              item.tomselect.items.forEach(e => {
                users_list[e] = true;
              });
            },
            onItemAdd: function(e) {
              if (e === "") return;
              if (users_list[e]) {
                users_list[e] = false;
                if (multiple || !this.revertSettings || this.revertSettings.tabIndex < 0 || !item.options.length) return;
                const revert = item.options[this.revertSettings.tabIndex].value;
                this.removeOption(e);
                this.addItem(revert);
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
            closeAfterSelect: false,
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
            url = option.url + encodeURIComponent('%' + query + '%');
            break;
          case models.instr:
          case models.taxo:
            url = option.url;
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
                text: row[3][0]
              }

            });
          }
          if (type === models.instr && json.length) json = json.reduce((result, a, v) => {
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
          return `<div class="py-2 flex  ${ ((multiple)?'inline-flex':'') } " ${optgroup} data-value="${el[option.settings.valueField]}">${ escape(el[this.settings.labelField]) }</div>`;
        },
        item: function(el, escape) {
          if (el === undefined || el === null) return ``; // add optgroup
          const optgroup = (el.optgroup) ? `item-${el.optgroup}` : ``;
          const inlist = (users_list[el[this.settings.valueField]]) ? `data-inlist` : ``;
          // add cancel icon for multiple selections
          //  const cancel = ((multiple) ? `<i class="${domselectors.component.tomselect.tsdelet.substr(1)}"></i>` : ``);
          // use ts plugin remove_button
          const cancel = ``;
          return DOMPurify.sanitize(`<div class="${((multiple) ? `flex inline-flex ` : ``) } ${optgroup}"  data-value="${el[this.settings.valueField]}"  ${inlist}>${ escape(el[this.settings.labelField])} ${ cancel }</div>`);
        },
        no_results: function(data, escape) {
          return DOMPurify.sanitize('<div class="no-results">' + ((item.dataset.noresults) ? item.dataset.noresults : 'No result found for ') + escape(data.input) + '</div>');
        },

      }
    }

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
    option.settings = Object.assign(default_settings, option.settings)
    if (id !== null) {
      const ts = new TomSelect('#' + id, option.settings);

      ts.wrapper.classList.remove(domselectors.component.tomselect.ident);
      ts.wrapper.classList.remove('js');
      // add
      ts.wrapper.setAttribute('data-component', 'tom-select');
      switch (type) {
        case 'taxo':
          ts.on('item_add', (v, el) => {
            if (el !== null) el.classList.add('new');
            //  el = el.querySelector('.ts-delet');
            //  if (el !== null) init_canceltag(el);
          });
          break;
          /*  case 'user':
              if (item.dataset.priv) ts.on("item_add", function(v, el) {
                el = el.querySelector(domselectors.component.tomselect.tsdelet);
                if (el !== null) init_canceltag(el);
              });
              break;*/
      }
      return ts;
    } else console.log('noid');

  }
}