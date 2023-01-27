import TomSelect from 'tom-select/dist/js/tom-select.base.min.js';
import tomSelectcss from "../css/tom-select.css";
import DOMPurify from 'dompurify';
import {
  fetchSettings,
  escape_html
} from '../modules/utils.js';
import {
  models
} from '../modules/modules-config.js';
let users_list = {};

export class JsTomSelect {
  apply(item, siblings = null) {
    const id = item.getAttribute('id');
    const multiple = item.hasAttribute('multiple');
    const type = item.dataset.type;
    let option = {
        url: '',
        settings: {}
      },
      init_canceltag = (tag) => {

        tag.addEventListener('click', (e) => {
          const v = e.currentTarget.closest('.item').dataset.value;
          if (v) {
            e.stopImmediatePropagation();
            item.tomselect.removeItem(v);
          }
        })
      };

    switch (type) {
      case models.user:
        option.url = "/api/users/search?by_name=";
        option.settings.valueField = 'id';
        option.settings.searchField = 'name';
        option.settings.labelField = 'name';
        option.settings.onInitialize = function() {
          item.tomselect.items.forEach(e => {
            users_list[e] = true;
          });
        }
        option.settings.onItemAdd = function(e) {
          if (users_list[e]) {
            if (!this.revertSettings || this.revertSettings.tabIndex < 0 || !item.querySelectorAll('option')) return;
            const revert = item.querySelectorAll('option')[this.revertSettings.tabIndex].value;
            this.removeOption(e);
            this.addItem(revert);
            users_list[e] = false;
          } else users_list[e] = true;
        }
        option.settings.onItemRemove = function(e) {
          if (users_list[e]) delete users_list[e];
          if (!this.revertSettings || this.revertSettings.tabIndex < 0) return;
          const revert = item.querySelectorAll('option')[this.revertSettings.tabIndex].value;
          if (users_list[revert] !== undefined) delete users_list[revert];
        }
        break;
      case models.instr:
        option.url = "/search/instruments";
        option.settings.valueField = 'id';
        option.settings.labelField = 'text';
        option.settings.searchField = 'id';
        option.settings.preload = true;
        break;
      case models.taxo:
        TomSelect.define('no_close', () => {
          this.close = () => {};
        });
        //option.settings.plugins.push('no-close')
        option.url = "/search/taxo";
        option.settings.valueField = 'id';
        option.settings.labelField = 'text';
        option.settings.searchField = 'text';
        option.settings.onInitialize = () => {
          const wrapper = document.querySelector('#' + id).nextElementSibling;
          if (!wrapper.classList.contains('ts-wrapper')) return;
          const tags = wrapper.querySelectorAll('.item .ts-delet');
          tags.forEach(tag => {
            init_canceltag(tag);
          })

        }
        option.settings.shouldLoad = (query) => {
          return query.length > 2;
        }
        break;
    }
    const default_settings = {
      create: false,
      maxOptions: null,
      preload: false,
      hideSelected: true,
      duplicates: false,
      allowEmptyOption: true,

      onDropdownClose: function() {

      },
      shouldLoad: function(query) {
        return query.length > 2
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
            url = option.url;
            if (query) url += '?q=' + encodeURIComponent(query);

            break;
          case models.taxo:
            url = option.url;
            if (query) url += '?q=' + encodeURIComponent(query);
            break;
        }
        if (url !== null) fetch(url, fetchSettings()).then(response => response.json()).then(json => {
          if (type === 'instr' && json.length) json = json.reduce((result, a, v) => {
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
          console.log('tomselect', err);
        });
      },

      render: {
        option: function(el, escape) {
          if (el === undefined || el === null) return ``;
          // add optgroup

          const optgroup = (el.optgroup) ? `data-optgroup=${el.optgroup}` : ``;
          return `<div class="py-2 flex  ${ ((multiple)?'inline-flex':'') } " ${optgroup} data-value="${el[option.settings.valueField]}">${ escape(el[this.settings.labelField]) }</div>`;
        },
        item: function(el, escape) {
          if (el === undefined || el === null) return ``; // add optgroup

          const optgroup = (el.optgroup) ? `item-${el.optgroup}` : ``;
          // add cancel icon for multiple selections
          const cancel = ((multiple) ? `<i class="ts-delet"></i>` : ``);
          return DOMPurify.sanitize(`<div class="` + ((multiple) ? `flex inline-flex ` : ``) + ` ${optgroup}" data-value="${el[this.settings.valueField]}">${ escape(el[this.settings.labelField])} ${ cancel }</div>`);
        },
        no_results: function(data, escape) {
          return DOMPurify.sanitize('<div class="no-results">' + ((item.dataset.noresults) ? item.dataset.noresults : 'No result found for ') + escape(data.input) + '</div>');
        },
      }
    }

    option.settings = Object.assign(default_settings, option.settings)
    if (id !== null) {
      const ts = new TomSelect('#' + id, option.settings);

      ts.wrapper.classList.remove('js-autocomplete');
      ts.wrapper.classList.remove('js');
      // add
      ts.wrapper.setAttribute('data-component', 'tom-select');
      switch (type) {
        case 'taxo':
          ts.on('item_add', (v, el) => {
            if (el !== null) el.classList.add('new');
            el = el.querySelector('.ts-delet');
            if (el !== null) init_canceltag(el);
          });
          break;
        case 'user':
          if (item.dataset.priv) ts.on("item_add", function(v, el) {
            el = el.querySelector('.ts-delet');
            if (el !== null) init_canceltag(el);
          });
          break;
      }
      return ts;
    }

  }
}