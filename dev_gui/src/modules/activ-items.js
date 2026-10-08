import DOMPurify from 'dompurify';
import {
  AlertBox
} from '../modules/alert-box.js';
import {
  models,
  domselectors,
  css
} from '../modules/modules-config.js';
import {
  get_catcha_reponse,
  decode_HTMLEntities,fetchSettings
} from '../modules/utils.js';
import {
  export_html2word
} from '../modules/export-html2word.js';
const localcss = {
  trigger: {
    show: 'triggershow',
    hide: 'triggerhide'
  },
  icon: 'icon',
  iconeyeslash: 'icon-eye-dark-slash',
  iconeye: 'icon-eye-dark',
  wrap: 'password-wrapper'
};

function createActivItems() {
  /*  activate function */
  function applyTo(element = document) {
    element = (document || element instanceof HTMLElement) ? element : document.querySelector(element);
    if (!element) return;
    element.querySelectorAll('[data-action]').forEach(async (item) => {
      const ev = item.dataset.event || 'click';
      const action = item.dataset.action;
      switch (action) {
        case 'toggle':
          const targets = (item.dataset.target) ? document.querySelectorAll(item.dataset.target) : ((item.nextElementSibling) ? [item.nextElementSibling] : null);
          if (!targets) return;
          const what = item.dataset.what ? item.dataset.what : css.hide;
          const disabled = item.dataset.disabled ? item.dataset.disabled : null;
          const toggle_target = (t) => {
            t.classList.toggle(what);
            if (disabled) {
              t.querySelectorAll(disabled).forEach(el => {
                if (el.disabled) el.removeAttribute('disabled');
                else el.disabled = true;
              });
            };
          }
          item.addEventListener(ev, (e) => {
            targets.forEach(t => {
              toggle_target(t);
            });
            item.classList.toggle(localcss.trigger.show);
            item.classList.toggle(localcss.trigger.hide);
            item.querySelectorAll('i[data-toggle]').forEach(ico => {
              ico.dataset.toggle.split(',').forEach(cl => {
                cl = cl.trim();
                if (cl !== ``) ico.classList.toggle(cl);
              });

            })
          });
          targets.forEach(t => {
            toggle_target(t);
          });
          break;
        case 'gotop':
          item.addEventListener(ev, (e) => {
            e.preventDefault();
            let box = (item.dataset.target) ? document.getElementById(item.dataset.target) : window;
            if (box !== window && box.classList.contains(css.modal)) box = box.querySelector(domselectors.component.modal.modalcontent);
            if (box !== null) box.scrollTo({
              top: 0,
              behavior: 'smooth'
            });
          });
          break;
          case "normalize":
           const target = (item.dataset.target) ? document.getElementById(item.dataset.target) : item;
          if (target===null) return;
          const normalize_title= function(value) {
            // space replaced by _ , and only alfa-numeric lowercase
            value=value.replace(/[!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]/gu, '').toLowerCase();
            return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, "_");
          }
           if(target!==item ) {
           item.addEventListener("input",(e)=> {
           if (item.value!=="") target.value=normalize_title(item.value);
          });}
           target.addEventListener("input",(e)=> {
           if (target.value.trim()!=="") target.value=normalize_title(target.value); else target.value=target.value.trim();
          });
          if (item.value.trim()!=="") target.value=normalize_title(item.value);
          break;
          case "replace":
          const toreplace=(item.dataset.replace)?item.dataset.replace:null;
          const replaceby=(item.dataset.replaceby)?item.dataset.replaceby:"";
          if(toreplace===null) return;
           item.addEventListener("input",(e)=> {
           if (item.value!=="") item.value=item.value.replace(toreplace,replaceby,g);
          });
          break;
        case 'wrapeye':
          const wrap = document.createElement('div');
          wrap.classList.add(localcss.wrap);
          const view = document.createElement('i');
          view.classList.add(localcss.icon);
          view.classList.add(localcss.iconeyeslash);
          item.parentNode.insertBefore(wrap, item);
          wrap.append(item);
          wrap.append(view);
          view.addEventListener('click', () => {
            let icoadd, icorem;
            if (item.type === "password") {
              item.type = "text";
              icoadd = localcss.iconeye;
              icorem = localcss.iconeyeslash;
            } else {
              item.type = "password";
              icoadd = localcss.iconeyeslash;
              icorem = localcss.iconeye;
            }
            view.classList.remove(icorem);
            view.classList.add(icoadd);
          })
          break;
        case 'setvalue':
          if (!item.dataset.what || !item.dataset.target) return;
          const dest = (item.dataset.target) ? document.getElementById(item.dataset.target) : null;
          if (!dest) return;
          item.addEventListener(ev, (e) => {
            dest.value = item.dataset.what;
          });
          break;

        case 'add-filters':
          item.addEventListener(ev, async (e) => {
            let inputs = item.closest('.ghost-form');
            if (!inputs) return;
            inputs = inputs.querySelectorAll('input');
            let href = item.href;
            href = href.split('?');
            href[1] = [];
            inputs.forEach(input => {
              if (input.checked) href[1].push(input.name + '=' + input.value);
            });
            item.href = href[0] + '?' + href[1].join('&');
            return true;
          });
          break;
        case 'getfile':
          if (item.dataset.contentlength) return item.dataset.contentlength;
          const enable_link = () => {
            item.classList.remove(css.disabled);
          }
          item.addEventListener('click', (e) => {
            if (item.classList.contains(css.disabled)) {
              e.preventDefault();
              return;
            }
            item.classList.add(css.disabled);
            setTimeout(enable_link, 4000);
            /*response.headers.forEach(function(val, key) {
              console.log(key + ' -> ' + val);
            });
            console.log('resp', response.headers.get('Content-Length'));
            item.dataset.contentlength = response.headers.get('Content-Length');*/
          });
          break;

        case 'togglecheckall':
          if (!item.dataset.target) return;
          item.addEventListener(((item.dataset.event) ? item.dataset.event : 'change'), (e) => {
            document.querySelectorAll(item.dataset.target).forEach(el => {
              el.toggleAttribute('checked', item.checked);
            });
          });
          break;
        case 'disabled':
          item.addEventListener(((item.dataset.event) ? item.dataset.event : 'click'), (e) => {
            e.preventDefault();
          });
          item.classList.add(css.disabled);
          break;
        case 'discardone':
          const inputs = (item.dataset.target) ? item.dataset.target.split(',') : null;
          if (inputs === null) return;
          const triggers = (item.dataset.trigger) ? item.parentElement.querySelectorAll('[name="' + item.dataset.trigger + '"]') : null;
          if (triggers === null) return;
          triggers.forEach(trigger => trigger.addEventListener('change', (e) => {
            const targetvalue = parseInt(e.target.value);
            inputs.forEach(input => {
              input = input.split('|');
              const value = (input.length) ? input[1] : 0;
              input = input[0];
              item.closest('fieldset').querySelectorAll('[data-name="' + input + '"]').forEach(box => {
                const els = box.querySelectorAll('input[name="' + input + '"]');
                if (targetvalue === 1 && e.target.checked) {
                  box.dataset.keep = (box.querySelector('input[name="' + input + '"]:checked')) ? box.querySelector('input[name="' + input + '"]:checked').value : null;
                  box.classList.add(css.disabled);
                  els.forEach(el => {
                    if (el.value === value) el.checked = true;
                    else el.checked = false;
                  });
                } else if (box.classList.contains(css.disabled)) {
                  box.classList.remove(css.disabled);
                  els.forEach(el => {
                    if (box.dataset.keep === el.value) el.checked = true;
                    else if (box.dataset.keep) el.checked = false;
                  });
                }

              });
            });
          }));
          break;
        case 'reset_ts':
            // settings for autocomplete taxons reset to automatic worms values
            const resetaction = document.querySelector('[data-reset]');
            if (resetaction) {
                const target=(resetaction.dataset.hasOwnProperty('resettarget'))?resetaction.dataset.resettarget:'data-worms';
                resetaction.addEventListener('click', (e) => {
                e.preventDefault();
                const btntxt=e.target.textContent;
                e.target.innerHTML = (e.target.dataset.wait)?e.target.dataset.wait:'Please wait ...';
                    document.querySelectorAll(domselectors.component.tomselect.line).forEach(line=> {
                    const auto = line.querySelector('[data-'+resetaction.dataset.reset+']') ;
                    if (auto!==null && auto.dataset.auto!=='') {
                    const values = auto.dataset.auto.split('|'); // id, display_name, lineage, id_lineage
                    const obj= {id:values[0],display_name:values[1],lineage:values[2],id_lineage:values[3]};
                    line.querySelectorAll('['+target+']').forEach(el=> {
                    if (el.tomselect.items.length>0  && values[0]!=el.tomselect.items[0]) {
                       let opt =el.tomselect.getOption(values[0]);
                       if (!opt) el.tomselect.addOption(obj);
                       el.tomselect.addItem(values[0]);}
                    })
                    }
                });
                setTimeout( () => {e.target.innerHTML=btntxt;},1000)
                });
                }
          break;
        case "no_mapping":
        if (item.dataset.hasOwnProperty('backref')) {
            const tab=item.closest(domselectors.component.tabs.tabcontent)
            const backref=(tab!==null)? item.dataset.backref+'-'+tab.id:item.dataset.backref;
            const hrefbox = document.getElementById(backref);
            if (hrefbox!==null && hrefbox.dataset.hasOwnProperty('href')) {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                hrefbox.nextElementSibling.remove();hrefbox.classList.remove(css.hide);});}}
        break;
        case 'confirm':
          item.addEventListener((item.dataset.event) ? item.dataset.event : 'click', async (e) => {
            e.preventDefault();
            const message = (item.dataset.content) ? item.dataset.content : `Do you really want to ` + item.textContent + '?';
            const options = (item.href) ? {
              callback: function() {window.location.href=item.href;}
            } : { callback: function() {
            if (item.form) {
             if (item.form.formsubmit) {
                item.form.formsubmit.submitForm();
              } else item.form.submit();
            }}};
            await AlertBox.addConfirm(message, options);
          });
          break;
        case 'astext':
             item.addEventListener((item.dataset.event) ? item.dataset.event : 'click', (e) => {
                const article = (item.dataset.target) ? document.getElementById(item.dataset.target) : document.body.querySelector('article');
                if (article)  export_html2word(article, item.parentElement);
            });
          break;
        case 'not_empty':
           if(!item.dataset.target || !item.dataset.message) return;
           let targetinputs=document.getElementById(item.dataset.target).querySelectorAll('.line input');
           let form =(targetinputs.length>0) ?targetinputs[0].form:null;
           if (form===null ) return;
            const not_empty=async function() {
            const inputs=[...targetinputs].filter(input=> (!input.disabled) );
            if (inputs.length===0) return true;
           let empty=true;
           inputs.forEach(input => {
            empty=(empty && input.value.trim()==='');
           });
           if (empty) return await AlertBox.addConfirm(item.dataset.message);
           else return true;
           }
           if (form.formsubmit) { form.formsubmit.addHandler('submit',not_empty)} else {
           form.addEventListener('submit',async (e) => {e.preventDefault();
           return await not_empty();})}
        break;
        case "set-value":
              const trgt = (item.dataset.hasOwnProperty('target')) ? document.getElementById(item.dataset.target) : null;
              if (trgt === null) return;
              item.addEventListener((item.dataset.event) ? item.dataset.event : 'click', (e) => {
                  trgt.textContent = item.textContent;
              });
        break;
        case "suggest": {
          // regroup the options of a select: the ones matching the trigger value (in option data-<suggestby>, | separated) first
          // only a suggestion: when the trigger value changes, the selection is reset and the data-warning element shown
          const source = (item.dataset.trigger) ? document.getElementById(item.dataset.trigger) : null;
          if (source === null || !item.dataset.suggestby) return;
          const warning = (item.dataset.warning) ? document.getElementById(item.dataset.warning) : null;
          // order: by first data-<suggestby> value asc (none last), then by data-<sortby> desc (none last)
          const sortby = item.dataset.sortby;
          const first_key = (opt) => (opt.dataset[item.dataset.suggestby] || '').split('|').filter(k => k !== '').sort((a, b) => a.localeCompare(b, undefined, {sensitivity: 'base'}))[0] || null;
          const by_sort_desc = (a, b) => {
            const va = (sortby) ? (a.dataset[sortby] || '') : '';
            const vb = (sortby) ? (b.dataset[sortby] || '') : '';
            return (va < vb) ? 1 : ((va > vb) ? -1 : 0);
          };
          const by_key_then_sort = (a, b) => {
            const ka = first_key(a), kb = first_key(b);
            if (ka !== kb) {
              if (ka === null) return 1;
              if (kb === null) return -1;
              const cmp = ka.localeCompare(kb, undefined, {sensitivity: 'base'});
              if (cmp !== 0) return cmp;
            }
            return by_sort_desc(a, b) || a.value.localeCompare(b.value);
          };
          const options = [...item.querySelectorAll('option')].filter(opt => opt.value !== '').sort(by_key_then_sort);
          const suggest = () => {
            const selected = item.value;
            const key = source.value;
            item.querySelectorAll('optgroup').forEach(grp => grp.remove());
            const matching = options.filter(opt => key !== '' && (opt.dataset[item.dataset.suggestby] || '').split('|').indexOf(key) >= 0).sort(by_sort_desc);
            if (matching.length) {
              const suggested = document.createElement('optgroup');
              suggested.label = ((item.dataset.suggestedlabel) ? item.dataset.suggestedlabel + ' ' : '') + key;
              matching.forEach(opt => suggested.append(opt));
              const others = document.createElement('optgroup');
              others.label = (item.dataset.otherlabel) ? item.dataset.otherlabel : '';
              options.filter(opt => matching.indexOf(opt) < 0).forEach(opt => others.append(opt));
              item.append(suggested, others);
            } else options.forEach(opt => item.append(opt));
            item.value = selected;
          }
          source.addEventListener((item.dataset.event) ? item.dataset.event : 'change', () => {
            suggest();
            item.value = '';
            if (warning) warning.classList.remove(css.hide);
          });
          item.addEventListener('change', () => {
            if (warning && item.value !== '') warning.classList.add(css.hide);
          });
          suggest();
        }
        break;
          }

    });
  }
  return {
    applyTo
  }

}
const ActivItems = createActivItems();
export {
  ActivItems
}