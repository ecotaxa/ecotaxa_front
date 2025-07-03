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
  fetchSettings, create_box
} from '../modules/utils.js';
import {
  models,
  domselectors,
  css,
} from '../modules/modules-config.js';
import {
  AlertBox
} from '../modules/alert-box.js';
import {
  FormSubmit
} from '../modules/form-submit.js';
let users_list = null;
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
const funcselector='.js-autocomplete';
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
      case models.person:
        option.url = "/gui/search_persons?name=";
        const personurl="gui/persons/create";
        if (item.dataset.prefix) option.settings.itemprefix=item.dataset.prefix;
        const open_new_person= async function() {
        const response = await fetch(personurl,fetchSettings);
        return response;
        }
        const wait_for_input=async function(resp,newone,callback) {
               let response;
            const reply=(resp.ok) ?await resp.text():await Promise.reject(resp);
        const parent=item.form.parentElement;
        parent.classList.remove("relative");
        document.body.classList.add(css.hidevscroll);
        const popup =create_box("div", {class:["absolute","z-[100]","bg-white","w-96","h-48","p-8","rounded","drop-shadow","centered"],src:personurl},parent);
        parent.disabled=true;
        const close=create_box("div",{class:[domselectors.close.substr(1)],text:"x"},popup);
        const content=create_box("div",{class:["h-full","w-full"]},popup);
        close.addEventListener('click', (e)=> {popup.remove();delete parent.disabled;  document.body.classList.remove(css.hidevscroll); });
        content.insertAdjacentHTML('afterbegin',reply);
        popup.querySelectorAll('[data-href]').forEach(btn=> {
        popup.classList.remove('h-48');
        popup.classList.add('h-auto');
        popup.classList.add('overflow-y-auto');
        popup.classList.add('max-h-full');
        btn.addEventListener('click',async(e)=>{
        const url=btn.dataset.href + '?type=' + btn.dataset.type;
        response =await fetch(url,fetchSettings);
        const reply=(response.ok) ?await response.text():await Promise.reject(response);
        content.innerHTML=reply;
        content.querySelectorAll(funcselector).forEach(el=> {applyTo(el);});
        const form2submit=popup.querySelector('form');
        form2submit.dataset.fetch=true;
        const formSubmit = new FormSubmit(form2submit);
        let namefield=popup.querySelector("[id='name']");
        if (namefield !==null) namefield.value=newone;
        else {
            namefield=popup.querySelector("[id='lastname']");
            if (namefield !==null) namefield.value=newone;
        }
        content.querySelector("[type='submit']").addEventListener('click', async(e) => {
        e.preventDefault();
        response=await formSubmit.submitForm();
        if (response.success) {
        newone=response[btn.dataset.type];
        const newitem={id:newone.id, "name":newone.name};
        if (btn.dataset.type=="guest") newitem["name+email"]= newone.name+" "+newone.email;
        else if(option.settings.itemprefix) newitem.id=option.settings.itemprefix+newitem.id;
         if(callback) callback(newitem);
        popup.remove();
        document.body.classList.remove(css.hidevscroll);
        } else popup.insertAdjacentHTML('afterbegin',response.message);

         })
        })})
        }
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            searchField: 'name',
            labelField: 'name+email',
            onItemRemove: function(e) {
              if (multiple || !this.revertSettings || (this.revertSettings.innerHTML === '' && this.revertSettings.tabIndex === 0) || this.revertSettings.tabIndex < 0) return;
              const revert = item.options[this.revertSettings.tabIndex].value;
            }},
              onItemAdd: function(e) {
              }}
        if (item.dataset.create ) {
            option.settings.create=function(e,callback) {
              open_new_person(e).then(response => { wait_for_input(response,e,callback);
              });
            }
           }
        break;
      case models.user:
        option.url = "/api/users/search?by_name=";
        option.settings = { ...option.settings,
          ...{
            valueField: 'id',
            searchField: 'name',
            labelField: 'name+email',
            onInitialize: function() {
              if (item.currentlist) users_list = item.currentlist;
              else if(item.name.indexOf('[')>=0) { users_list = {}; item.tomselect.items.forEach(e => {
                if (e !== '' && parseInt(e) > 0) users_list[e] = true;
              });}
            },
            onItemAdd: function(e) {
              if (e === "") return;
              if (users_list!==null  && users_list[e] ) {
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
                 /* AlertBox.addMessage({
                    type: AlertBox.alertconfig.types.danger,
                    parent: item,
                    content: AlertBox.i18nmessages.exists
                  });*/
                }, 2000);
              } else if (users_list!==null) users_list[e] = true;
            },
            onItemRemove: function(e) {
              if (users_list!==null && users_list[e]) delete users_list[e];
              if (multiple || !this.revertSettings || (this.revertSettings.innerHTML === '' && this.revertSettings.tabIndex === 0) || this.revertSettings.tabIndex < 0) {console.log('this revet',this.revertSettings);return;}
              const revert = item.options[this.revertSettings.tabIndex].value;
              if (users_list!==null && users_list[revert] !== undefined) delete users_list[revert];
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
          case models.person:
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
          console.log('thisoptions', this.options)
          return this.options + (callback)?callback(json):json;

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
          const itemprefix =(this.settings.itemprefix  && el[this.settings.valueField].length>this.settings.itemprefix.length)?((el[this.settings.valueField].substr(0,this.settings.itemprefix.length)===this.settings.itemprefix)?this.settings.itemprefix.replace('_',''):""):"";
          return `<div class="py-2 flex  ${ ((multiple)?'inline-flex':'') } ${itemprefix} " ${optgroup} data-value="${el[option.settings.valueField]}">${ escape(label) }</div>`;
        },
        item: function(el, escape) {
          if (el === undefined || el === null) return ``; // add optgroup
          const optgroup = (el.optgroup) ? `item-${el.optgroup}` : ``;
          const inlist = (users_list!==null && users_list[el[this.settings.valueField]]) ? `data-inlist` : ``;
          const cancel = ``;
          const label = _get_label(el, option.settings.labelField, true);
          const itemprefix =(this.settings.itemprefix && el[this.settings.valueField].length>this.settings.itemprefix.length)?((el[this.settings.valueField].substr(0,this.settings.itemprefix.length)===this.settings.itemprefix)?this.settings.itemprefix.replace('_',''):""):"";
          return DOMPurify.sanitize(`<div class="${((multiple) ? `flex inline-flex ` : ``) } ${itemprefix} ${optgroup}"  data-value="${el[this.settings.valueField]}"  ${inlist}>${ escape(label) } ${ cancel }</div>`);
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
    if (id !== null ) {
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
            });} else if (item.dataset.refresh ) {
                 const refresh = function(e) {
        const el=document.getElementById(item.dataset.refresh);
        if (el===null) return;
        const href=el.dataset.href.split('?');
        if (href.length>1) {
            href[1]=href[1].split("=");
            if (href[1].length>1) {
            href[1][1]=item.tomselect.items.join(',');
            }
            href[1]=href[1].join('=');}
            el.dataset.href=href.join('?');
            el.click();
        } ;
        ts.on('item_add', (v,el)=> {
            if(refresh!==null) refresh(ts.items.join(','));
            });
            ts.on('item_remove', (v,el)=> {
            if(refresh!==null) refresh(ts.items.join(','));
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